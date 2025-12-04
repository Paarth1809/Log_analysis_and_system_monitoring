# backend/routes/cves.py
from fastapi import APIRouter, Query
from typing import Optional
from ..services.cve_service import find_cves, get_cve_by_id

router = APIRouter(prefix="/cves", tags=["cves"])

@router.get("/", summary="Search CVE entries")
def api_get_cves(
    q: Optional[str] = Query(None),
    vendor: Optional[str] = Query(None),
    product: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    return find_cves(q=q, vendor=vendor, product=product, limit=limit, skip=skip)

@router.get("/{cve_id}", summary="Get CVE by ID")
def api_get_cve_by_id(cve_id: str):
    c = get_cve_by_id(cve_id)
    if not c:
        return {"error": "not_found", "cve_id": cve_id}
    return c
