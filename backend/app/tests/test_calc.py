from app.engines.night_compare import compare_day_night
from app.engines.tariff_breakdown import calc_fare

T = {"start_price": 11, "start_include_km": 3, "per_km": 2.5, "per_slow_min": 0.8, "night_factor": 1.2}

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

def test_fare_carries_tariff_snapshot():
    r = calc_fare(5, 2, False, T)
    # 白天行程也须记下运价表配置的夜间系数，而不是生效倍率 1.0
    assert (r["start_price"], r["start_include_km"], r["per_km"], r["per_slow_min"], r["night_factor"]) == (11, 3, 2.5, 0.8, 1.2)
    n = calc_fare(5, 2, True, T)
    assert n["night_factor"] == 1.2

def test_compare_carries_night_factor():
    c = compare_day_night(18, 12, T)
    assert c["night_factor"] == 1.2
    assert c["night"]["night_factor"] == 1.2
