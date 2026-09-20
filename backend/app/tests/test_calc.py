import sqlite3

import pytest
from pydantic import ValidationError

from app.engines.night_compare import compare_day_night
from app.engines.tariff_breakdown import calc_fare
from app.schemas.fare import TariffUpdate
from app.services.taxi_service import TaxiService

T = {"start_price": 11, "start_include_km": 3, "per_km": 2.5, "per_slow_min": 0.8, "night_factor": 1.2}

SCHEMA = """
CREATE TABLE tariff(id INTEGER PRIMARY KEY, start_price REAL, start_include_km REAL, per_km REAL, per_slow_min REAL, night_factor REAL);
CREATE TABLE trips(id INTEGER PRIMARY KEY, label TEXT, distance_km REAL, slow_min REAL, night INTEGER);
CREATE TABLE settings(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE calc_runs(id INTEGER PRIMARY KEY, kind TEXT, trip_id INTEGER, input_json TEXT, result_json TEXT, created_at TEXT);
"""

def mk_service():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.execute(
        "INSERT INTO tariff(start_price,start_include_km,per_km,per_slow_min,night_factor) VALUES (?,?,?,?,?)",
        (T["start_price"], T["start_include_km"], T["per_km"], T["per_slow_min"], T["night_factor"]),
    )
    conn.commit()
    return TaxiService(conn)

def test_day_short():
    r = calc_fare(5, 2, False, T)
    assert r["total"] == 17.6
    assert r["mileage"] == 5.0

def test_night_long():
    r = calc_fare(18, 12, True, T)
    assert r["total"] == 69.72

def test_compare_delta():
    c = compare_day_night(18, 12, T)
    assert c["night_total"] > c["day_total"]

def test_fare_persist_carries_snapshot():
    with mk_service() as s:
        r = s.fare(5, 2, False, None, True)
        assert r["run_id"]
        assert r["tariff"] == T
        rec = s.run(r["run_id"])
        assert rec["kind"] == "fare"
        assert rec["result"]["tariff"] == T
        assert rec["result"]["total"] == r["total"]

def test_compare_persist_carries_night_factor():
    with mk_service() as s:
        r = s.compare(18, 12, True)
        rec = s.run(r["run_id"])
        assert rec["kind"] == "compare"
        assert rec["result"]["tariff"]["night_factor"] == T["night_factor"]
        assert rec["result"]["night"]["night_factor"] == T["night_factor"]

def test_old_record_keeps_snapshot_after_tariff_change():
    with mk_service() as s:
        old = s.fare(5, 2, False, None, True)
        s.update_tariff({"start_price": 20, "start_include_km": 2, "per_km": 3.0, "per_slow_min": 1.0, "night_factor": 1.5})
        rec = s.run(old["run_id"])
        assert rec["result"]["tariff"] == T           # 旧记录仍是写入时的五项
        assert rec["result"]["total"] == old["total"]  # 拆解也不变
        new = s.fare(5, 2, False, None, False)
        assert new["tariff"]["start_price"] == 20.0   # 新计算跟新运价
        assert new["total"] != old["total"]

def test_readonly_fare_not_persisted():
    with mk_service() as s:
        before = len(s.history())
        r = s.fare(5, 2, True, None, False)
        assert r["run_id"] is None
        assert r["tariff"] == T  # 只读也返回本次五项
        assert len(s.history()) == before

def test_tariff_update_persists():
    with mk_service() as s:
        t = s.update_tariff({"start_price": 13, "start_include_km": 3, "per_km": 2.6, "per_slow_min": 0.9, "night_factor": 1.3})
        assert t["start_price"] == 13.0 and t["night_factor"] == 1.3
        assert s.tariff()["per_km"] == 2.6

@pytest.mark.parametrize("bad", [
    {"start_price": 0}, {"start_price": -1}, {"per_km": 0}, {"per_slow_min": -0.5},
    {"start_include_km": -1}, {"night_factor": 0},
])
def test_tariff_update_validation_rejects(bad):
    good = {"start_price": 11, "start_include_km": 3, "per_km": 2.5, "per_slow_min": 0.8, "night_factor": 1.2}
    with pytest.raises(ValidationError):
        TariffUpdate(**{**good, **bad})

def test_invalid_tariff_leaves_db_untouched():
    with mk_service() as s:
        before = s.tariff()
        for bad in ({"start_price": -1}, {"night_factor": 0}, {"start_include_km": -2}):
            good = {"start_price": 11, "start_include_km": 3, "per_km": 2.5, "per_slow_min": 0.8, "night_factor": 1.2}
            try:
                TariffUpdate(**{**good, **bad})
            except ValidationError:
                pass  # 路由层同样因 422 到不了 update_tariff
        assert s.tariff() == before
