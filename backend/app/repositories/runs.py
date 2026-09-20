import json, sqlite3
from datetime import datetime, timezone

from app.engines.tariff_breakdown import TARIFF_FIELDS

_SNAPSHOT_COLS = ("snap_start_price", "snap_start_include_km", "snap_per_km", "snap_per_slow_min", "snap_night_factor")


def _snapshot_values(result: dict) -> tuple:
    return tuple(result.get(k) for k in TARIFF_FIELDS)


def insert(conn, kind, payload, result, trip_id=None):
    now = datetime.now(timezone.utc).isoformat()
    snap = _snapshot_values(result)
    cur = conn.execute(
        f"INSERT INTO calc_runs(kind,trip_id,input_json,result_json,{','.join(_SNAPSHOT_COLS)},created_at)"
        f" VALUES (?,?,?,?,{','.join('?' * 5)},?)",
        (kind, trip_id, json.dumps(payload, ensure_ascii=False), json.dumps(result, ensure_ascii=False), *snap, now),
    )
    conn.commit()
    return int(cur.lastrowid)


def list_recent(conn, limit=50):
    return [dict(r) for r in conn.execute("SELECT * FROM calc_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]


def get(conn, run_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM calc_runs WHERE id=?", (run_id,)).fetchone()
    return dict(row) if row else None


def snapshot_of(row: dict) -> dict | None:
    """从行上的快照列组装五项；旧记录缺列数据时返回 None。"""
    snap = {
        "start_price": row.get("snap_start_price"),
        "start_include_km": row.get("snap_start_include_km"),
        "per_km": row.get("snap_per_km"),
        "per_slow_min": row.get("snap_per_slow_min"),
        "night_factor": row.get("snap_night_factor"),
    }
    return snap if all(v is not None for v in snap.values()) else None
