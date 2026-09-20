import json
import sqlite3

import pytest

from app.db import DB_PATH, connect
from app.repositories.tariff import TariffValidationError
from app.services.taxi_service import TaxiService


def test_fare_persisted_with_snapshot():
    with TaxiService() as s:
        out = s.fare(5, 2, False, None, True)
        rid = out["run_id"]
        assert rid is not None
        row = s.run(rid)
    snap = row["tariff_snapshot"]
    assert snap == {"start_price": 11.0, "start_include_km": 3.0, "per_km": 2.5,
                    "per_slow_min": 0.8, "night_factor": 1.2}
    assert row["result"]["total"] == out["total"]
    # 快照列与拆解同时落库
    conn = connect()
    db = conn.execute("SELECT snap_start_price, snap_night_factor, result_json FROM calc_runs WHERE id=?", (rid,)).fetchone()
    conn.close()
    assert db["snap_start_price"] == 11.0
    assert db["snap_night_factor"] == 1.2
    assert json.loads(db["result_json"])["start"] == row["result"]["start"]


def test_old_record_still_reads_written_values():
    with TaxiService() as s:
        out = s.fare(18, 12, True, None, True)
        rid = out["run_id"]
        original_total = out["total"]
        # 之后运价被改动
        s.update_tariff({"start_price": 20, "start_include_km": 0, "per_km": 3,
                         "per_slow_min": 1, "night_factor": 1.5})
        row = s.run(rid)
    assert row["tariff_snapshot"] == {"start_price": 11.0, "start_include_km": 3.0, "per_km": 2.5,
                                      "per_slow_min": 0.8, "night_factor": 1.2}
    assert row["result"]["total"] == original_total == 69.72


def test_preview_after_save_does_not_write_record():
    with TaxiService() as s:
        before = len(s.history(1000))
        s.update_tariff({"start_price": 13, "start_include_km": 3, "per_km": 2.6,
                         "per_slow_min": 0.9, "night_factor": 1.3})
        preview = s.preview_fare(8, 3, False)
        after = len(s.history(1000))
    assert after == before
    assert preview["start_price"] == 13
    assert preview["per_km"] == 2.6


@pytest.mark.parametrize("bad", [
    {"start_price": 0, "start_include_km": 3, "per_km": 2.5, "per_slow_min": 0.8, "night_factor": 1.2},
    {"start_price": 11, "start_include_km": 3, "per_km": -1, "per_slow_min": 0.8, "night_factor": 1.2},
    {"start_price": 11, "start_include_km": 3, "per_km": 2.5, "per_slow_min": 0, "night_factor": 1.2},
    {"start_price": 11, "start_include_km": -0.1, "per_km": 2.5, "per_slow_min": 0.8, "night_factor": 1.2},
    {"start_price": 11, "start_include_km": 3, "per_km": 2.5, "per_slow_min": 0.8, "night_factor": 0},
])
def test_invalid_tariff_leaves_db_untouched(bad):
    with TaxiService() as s:
        good = s.tariff()
        with pytest.raises(TariffValidationError):
            s.update_tariff(bad)
        assert s.tariff() == good


def test_compare_persisted_with_night_factor():
    with TaxiService() as s:
        out = s.compare(18, 12, True)
        row = s.run(out["run_id"])
    assert row["tariff_snapshot"]["night_factor"] == 1.2
    assert row["result"]["night_factor"] == 1.2
    assert row["result"]["day"]["night_factor"] == 1.2


def test_legacy_db_migration_backfills_snapshot():
    # 构造旧库：calc_runs 无快照列，但结果 JSON 内含五项
    import shutil
    shutil.rmtree(DB_PATH.parent, ignore_errors=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    old = sqlite3.connect(DB_PATH)
    old.executescript("""
    CREATE TABLE tariff(id INTEGER PRIMARY KEY, start_price REAL, start_include_km REAL, per_km REAL, per_slow_min REAL, night_factor REAL);
    INSERT INTO tariff VALUES (1, 11, 3, 2.5, 0.8, 1.2);
    CREATE TABLE calc_runs(id INTEGER PRIMARY KEY, kind TEXT, trip_id INTEGER, input_json TEXT, result_json TEXT, created_at TEXT);
    """)
    legacy_result = {"total": 17.6, "start": 11, "mileage": 5.0, "slow_fee": 1.6,
                     "start_price": 11, "start_include_km": 3, "per_km": 2.5,
                     "per_slow_min": 0.8, "night_factor": 1.2}
    old.execute("INSERT INTO calc_runs(kind,input_json,result_json,created_at) VALUES ('fare','{}',?,datetime('now'))",
                (json.dumps(legacy_result),))
    old.commit()
    old.close()

    from app import seed
    seed.init_db()

    with TaxiService() as s:
        row = s.run(1)
    assert row["tariff_snapshot"]["night_factor"] == 1.2
    assert row["result"]["total"] == 17.6
