from fastapi import APIRouter, Query
from typing import Optional
from ..db import COL_MATCHES
from pymongo import DESCENDING

router = APIRouter(prefix="/matches", tags=["matches"])

@router.get("/", summary="Fetch vulnerability matches")
def get_matches(
    host: Optional[str] = Query(None),
    cve_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    query = {}
    if host:
        query["host"] = {"$regex": host, "$options": "i"}
    if cve_id:
        query["cve_id"] = {"$regex": cve_id, "$options": "i"}
    if severity:
        query["severity"] = {"$regex": severity, "$options": "i"}

    cursor = COL_MATCHES.find(query).sort("matched_at", DESCENDING).skip(skip).limit(limit)
    items = list(cursor)
    total = COL_MATCHES.count_documents(query)

    return {"total": total, "limit": limit, "skip": skip, "items": items}
