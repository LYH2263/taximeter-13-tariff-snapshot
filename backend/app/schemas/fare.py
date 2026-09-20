from pydantic import BaseModel, Field

class FareRequest(BaseModel):
    distance_km: float = Field(ge=0)
    slow_min: float = Field(ge=0)
    night: bool = False
    trip_id: int | None = None
    persist: bool = True

class CompareRequest(BaseModel):
    distance_km: float = Field(ge=0)
    slow_min: float = Field(ge=0)
    persist: bool = False

class TariffUpdate(BaseModel):
    start_price: float = Field(gt=0)
    start_include_km: float = Field(ge=0)
    per_km: float = Field(gt=0)
    per_slow_min: float = Field(gt=0)
    night_factor: float = Field(gt=0)
