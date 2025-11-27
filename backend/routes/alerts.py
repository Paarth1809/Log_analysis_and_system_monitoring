# backend/routes/alerts.py
from fastapi import APIRouter, Query, Body
from typing import Optional
from ..services.alert_service import find_alerts, create_alert

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/", summary="Fetch alerts")
def api_get_alerts(
    host: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    return find_alerts(host=host, limit=limit, skip=skip)

@router.post("/", summary="Create an alert (manual/test)")
def api_create_alert(payload: dict = Body(...)):
    # basic manual creation endpoint for testing/dev
    inserted_id = create_alert(payload)
    return {"inserted_id": inserted_id}
