TARIFF_FIELDS = ("start_price", "start_include_km", "per_km", "per_slow_min", "night_factor")


def tariff_snapshot(tariff: dict) -> dict:
    """运价五项在计算时点的值，用于随结果落库，后续不受改价影响。"""
    return {
        "start_price": float(tariff["start_price"]),
        "start_include_km": float(tariff["start_include_km"]),
        "per_km": float(tariff["per_km"]),
        "per_slow_min": float(tariff["per_slow_min"]),
        "night_factor": float(tariff["night_factor"]),
    }


def calc_fare(distance_km: float, slow_min: float, night: bool, tariff: dict) -> dict:
    snap = tariff_snapshot(tariff)
    base = snap["start_price"]
    include = snap["start_include_km"]
    per_km = snap["per_km"]
    per_slow = snap["per_slow_min"]
    factor = snap["night_factor"]
    night_f = factor if night else 1.0
    dist = max(0.0, float(distance_km) - include)
    mile = dist * per_km
    slow = float(slow_min) * per_slow
    sub = base + mile + slow
    return {
        "distance_km": round(float(distance_km), 2),
        "slow_min": round(float(slow_min), 1),
        "night": night,
        # 运价五项快照：本次打表实际使用的值
        "start_price": round(base, 2),
        "start_include_km": round(include, 2),
        "per_km": round(per_km, 2),
        "per_slow_min": round(per_slow, 2),
        "night_factor": round(factor, 2),
        "start": round(base * night_f, 2),
        "mileage": round(mile * night_f, 2),
        "slow_fee": round(slow * night_f, 2),
        "total": round(sub * night_f, 2),
    }
