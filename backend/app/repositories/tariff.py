import sqlite3

FIELDS = ("start_price", "start_include_km", "per_km", "per_slow_min", "night_factor")

def get_active(conn: sqlite3.Connection) -> dict:
    row = conn.execute("SELECT * FROM tariff ORDER BY id LIMIT 1").fetchone()
    return dict(row) if row else {}

def update_active(conn: sqlite3.Connection, values: dict) -> dict:
    vals = [float(values[f]) for f in FIELDS]
    row = conn.execute("SELECT id FROM tariff ORDER BY id LIMIT 1").fetchone()
    if row:
        conn.execute(
            "UPDATE tariff SET start_price=?, start_include_km=?, per_km=?, per_slow_min=?, night_factor=? WHERE id=?",
            (*vals, row["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO tariff(start_price,start_include_km,per_km,per_slow_min,night_factor) VALUES (?,?,?,?,?)",
            vals,
        )
    conn.commit()
    return get_active(conn)
