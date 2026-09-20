from fastapi import APIRouter, HTTPException
from app.repositories.tariff import TariffValidationError
from app.schemas.tariff import TariffUpdate
from app.services.taxi_service import TaxiService
router = APIRouter()
@router.get("/tariff")
def get_tariff():
    with TaxiService() as s: return s.tariff()
@router.post("/tariff")
def post_tariff(body: TariffUpdate):
    with TaxiService() as s:
        try:
            return s.update_tariff(body.fields())
        except TariffValidationError as e:
            raise HTTPException(status_code=400, detail={"errors": e.errors})
