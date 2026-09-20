from fastapi import APIRouter, HTTPException
from app.services.taxi_service import TaxiService
router = APIRouter()
@router.get("/history")
def history(limit: int = 50):
    with TaxiService() as s: return {"items": s.history(limit)}
@router.get("/history/{run_id}")
def history_detail(run_id: int):
    with TaxiService() as s:
        row = s.run(run_id)
        if not row: raise HTTPException(404)
        return row
