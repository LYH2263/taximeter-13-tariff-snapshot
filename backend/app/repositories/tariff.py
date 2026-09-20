import sqlite3

from app.engines.tariff_breakdown import TARIFF_FIELDS


class TariffValidationError(ValueError):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("；".join(errors))


def get_active(conn: sqlite3.Connection) -> dict:
    row = conn.execute("SELECT * FROM tariff ORDER BY id LIMIT 1").fetchone()
    return dict(row) if row else {}


def validate(fields: dict) -> list[str]:
    """起步价、每公里、低速单价须为正；含公里不得为负；夜间系数须大于零。"""
    errors = []
    positive = (("start_price", "起步价"), ("per_km", "每公里"), ("per_slow_min", "低速单价"))
    for key, label in positive:
        if fields[key] <= 0:
            errors.append(f"{label}须为正数")
    if fields["start_include_km"] < 0:
        errors.append("含公里不得为负")
    if fields["night_factor"] <= 0:
        errors.append("夜间系数须大于零")
    return errors


def update(conn: sqlite3.Connection, fields: dict) -> dict:
    """校验通过才写库；失败抛 TariffValidationError，库中运价不变。"""
    errors = validate(fields)
    if errors:
        raise TariffValidationError(errors)
    conn.execute(
        "UPDATE tariff SET start_price=?, start_include_km=?, per_km=?, per_slow_min=?, night_factor=?"
        " WHERE id=(SELECT id FROM tariff ORDER BY id LIMIT 1)",
        tuple(fields[k] for k in TARIFF_FIELDS),
    )
    conn.commit()
    return get_active(conn)
