# backend/routes/stats.py
from fastapi import APIRouter, Query
from ..services.stats_service import get_stats

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/", summary="Aggregate stats")
def api_stats(limit_hosts: int = Query(20), limit_cves: int = Query(20)):
    return get_stats(limit_hosts=limit_hosts, limit_cves=limit_cves)
