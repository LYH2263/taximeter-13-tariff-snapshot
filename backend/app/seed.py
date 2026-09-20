import json
from app.db import connect
from app.engines.tariff_breakdown import TARIFF_FIELDS, calc_fare, tariff_snapshot

TARIFF = {"start_price": 11, "start_include_km": 3, "per_km": 2.5, "per_slow_min": 0.8, "night_factor": 1.2}

_SNAPSHOT_COLS = {
    "start_price": "snap_start_price",
    "start_include_km": "snap_start_include_km",
    "per_km": "snap_per_km",
    "per_slow_min": "snap_per_slow_min",
    "night_factor": "snap_night_factor",
}


def init_db():
    conn = connect()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS tariff(id INTEGER PRIMARY KEY, start_price REAL, start_include_km REAL, per_km REAL, per_slow_min REAL, night_factor REAL);
    CREATE TABLE IF NOT EXISTS trips(id INTEGER PRIMARY KEY, label TEXT, distance_km REAL, slow_min REAL, night INTEGER);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
    CREATE TABLE IF NOT EXISTS calc_runs(id INTEGER PRIMARY KEY, kind TEXT, trip_id INTEGER, input_json TEXT, result_json TEXT,
        snap_start_price REAL, snap_start_include_km REAL, snap_per_km REAL, snap_per_slow_min REAL, snap_night_factor REAL,
        created_at TEXT);
    """)
    _migrate_runs(conn)
    if conn.execute("SELECT COUNT(*) c FROM tariff").fetchone()["c"] == 0:
        conn.execute("INSERT INTO tariff(start_price,start_include_km,per_km,per_slow_min,night_factor) VALUES (11,3,2.5,0.8,1.2)")
        conn.execute("INSERT INTO trips(label,distance_km,slow_min,night) VALUES ('白天短途',5.0,2,0)")
        conn.execute("INSERT INTO trips(label,distance_km,slow_min,night) VALUES ('夜间长途(种子)',18.0,12,1)")
        conn.execute("INSERT INTO settings(key,value) VALUES ('currency','CNY')")
        r = calc_fare(5, 2, False, TARIFF)
        snap = tariff_snapshot(TARIFF)
        cols = ",".join(_SNAPSHOT_COLS.values())
        conn.execute(
            f"INSERT INTO calc_runs(kind,trip_id,input_json,result_json,{cols},created_at) VALUES ('fare',1,?,?,{','.join('?'*5)},datetime('now'))",
            (json.dumps({"distance_km":5,"slow_min":2,"night":False}), json.dumps(r, ensure_ascii=False),
             *(snap[k] for k in TARIFF_FIELDS)),
        )
        conn.commit()
    conn.close()


def _migrate_runs(conn):
    """旧库 calc_runs 补五列；旧结果若 JSON 内已带快照则回填，否则留 NULL。"""
    existing = {r["name"] for r in conn.execute("PRAGMA table_info(calc_runs)").fetchall()}
    for key, col in _SNAPSHOT_COLS.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE calc_runs ADD COLUMN {col} REAL")
    conn.commit()
    rows = conn.execute(
        "SELECT id, result_json FROM calc_runs WHERE snap_start_price IS NULL OR snap_night_factor IS NULL"
    ).fetchall()
    for row in rows:
        try:
            result = json.loads(row["result_json"] or "{}")
        except json.JSONDecodeError:
            continue
        vals = [result.get(k) for k in TARIFF_FIELDS]
        if any(v is None for v in vals):
            continue
        conn.execute(
            "UPDATE calc_runs SET snap_start_price=?, snap_start_include_km=?, snap_per_km=?, snap_per_slow_min=?, snap_night_factor=? WHERE id=?",
            (*vals, row["id"]),
        )
    conn.commit()
