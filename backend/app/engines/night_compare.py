from app.engines.tariff_breakdown import calc_fare, tariff_snapshot


def compare_day_night(distance_km: float, slow_min: float, tariff: dict) -> dict:
    snap = tariff_snapshot(tariff)
    day = calc_fare(distance_km, slow_min, False, tariff)
    night = calc_fare(distance_km, slow_min, True, tariff)
    return {
        "distance_km": day["distance_km"],
        "slow_min": day["slow_min"],
        # 运价五项快照：对比时适用的运价，夜间系数为运价表当时配置值
        "start_price": round(snap["start_price"], 2),
        "start_include_km": round(snap["start_include_km"], 2),
        "per_km": round(snap["per_km"], 2),
        "per_slow_min": round(snap["per_slow_min"], 2),
        "night_factor": round(snap["night_factor"], 2),
        "day_total": day["total"],
        "night_total": night["total"],
        "delta": round(night["total"] - day["total"], 2),
        "day": day,
        "night": night,
    }
