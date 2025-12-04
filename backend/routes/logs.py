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
<<<<<<< HEAD
    severity: Optional[str] = Query(None),
=======
>>>>>>> cd260ba9258ba3c2c7ffb1588424565f3f1c9eae
    q: Optional[str] = Query(None),
    start: Optional[str] = Query(None, description="ISO date string e.g. 2025-11-01T00:00:00"),
    end: Optional[str] = Query(None, description="ISO date string"),
    limit: int = Query(50, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    sort: str = Query("-timestamp")
):
<<<<<<< HEAD
    return find_logs(host=host, software=software, event_type=event_type, severity=severity, q=q, start=start, end=end, limit=limit, skip=skip, sort=sort)
=======
    return find_logs(host=host, software=software, event_type=event_type, q=q, start=start, end=end, limit=limit, skip=skip, sort=sort)
>>>>>>> cd260ba9258ba3c2c7ffb1588424565f3f1c9eae
