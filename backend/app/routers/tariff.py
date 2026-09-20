from fastapi import APIRouter
from app.schemas.fare import TariffUpdate
from app.services.taxi_service import TaxiService
router = APIRouter()
@router.get("/tariff")
def get_tariff():
    with TaxiService() as s: return s.tariff()
@router.put("/tariff")
def put_tariff(body: TariffUpdate):
    with TaxiService() as s: return s.update_tariff(body.model_dump())
