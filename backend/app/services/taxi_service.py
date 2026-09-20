import json
from app.db import connect
from app.engines.night_compare import compare_day_night
from app.engines.tariff_breakdown import calc_fare
from app.repositories import runs, settings, tariff, trips

SNAPSHOT_FIELDS = ("start_price", "start_include_km", "per_km", "per_slow_min", "night_factor")

def _snapshot(t: dict) -> dict:
    return {k: float(t[k]) for k in SNAPSHOT_FIELDS}

def _parse_run(r: dict) -> dict:
    return {
        "id": r["id"], "kind": r["kind"], "trip_id": r["trip_id"], "created_at": r["created_at"],
        "input": json.loads(r["input_json"]), "result": json.loads(r["result_json"]),
    }

class TaxiService:
    def __init__(self, conn=None): self._c = conn if conn is not None else connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_trips(self): return trips.list_all(self._c)
    def trip(self, tid): return trips.get(self._c, tid)
    def tariff(self): return tariff.get_active(self._c)
    def update_tariff(self, values): return tariff.update_active(self._c, values)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50): return [_parse_run(r) for r in runs.list_recent(self._c, limit)]
    def run(self, run_id):
        row = runs.get(self._c, run_id)
        return _parse_run(row) if row else None
    def fare(self, distance_km, slow_min, night, trip_id, persist):
        t = tariff.get_active(self._c)
        r = calc_fare(distance_km, slow_min, night, t)
        r["tariff"] = _snapshot(t)
        rid = runs.insert(self._c, "fare", {"distance_km": distance_km, "slow_min": slow_min, "night": night}, r, trip_id) if persist else None
        return {"run_id": rid, **r}
    def compare(self, distance_km, slow_min, persist):
        t = tariff.get_active(self._c)
        r = compare_day_night(distance_km, slow_min, t)
        r["tariff"] = _snapshot(t)
        rid = runs.insert(self._c, "compare", {"distance_km": distance_km, "slow_min": slow_min}, r, None) if persist else None
        return {"run_id": rid, **r}
    def dashboard(self):
        items = trips.list_all(self._c)
        clean = [x for x in items if "种子" not in x["label"]]
        dirty = [x for x in items if "种子" in x["label"]]
        return {"trip_count": len(items), "clean": len(clean), "dirty": len(dirty)}
