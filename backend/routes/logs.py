# backend/routes/logs.py
from fastapi import APIRouter, Query
from typing import Optional
from ..services.log_service import find_logs

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("/", summary="Fetch normalized logs (advanced filters)")
def api_get_logs(
    host: Optional[str] = Query(None),
    software: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    start: Optional[str] = Query(None, description="ISO date string e.g. 2025-11-01T00:00:00"),
    end: Optional[str] = Query(None, description="ISO date string"),
    limit: int = Query(50, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    sort: str = Query("-timestamp")
):
    return find_logs(host=host, software=software, event_type=event_type, q=q, start=start, end=end, limit=limit, skip=skip, sort=sort)
