from pydantic import BaseModel

from app.engines.tariff_breakdown import TARIFF_FIELDS


class TariffUpdate(BaseModel):
    start_price: float
    start_include_km: float
    per_km: float
    per_slow_min: float
    night_factor: float

    def fields(self) -> dict:
        return {k: getattr(self, k) for k in TARIFF_FIELDS}
