# backend/services/cve_service.py
from bson import ObjectId
from ..db import COL_CVES

def _to_output(doc):
    if not doc:
        return None
    out = dict(doc)
    out["_id"] = str(out.get("_id")) if out.get("_id") else None
    return out

def find_cves(q=None, vendor=None, product=None, limit=50, skip=0, sort_field="cvss_score", sort_dir=-1):
    query = {}
    if q:
        query["$or"] = [
            {"cve_id": {"$regex": q, "$options": "i"}},
            {"vendor": {"$regex": q, "$options": "i"}},
            {"product": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
        ]
    if vendor:
        query["vendor"] = {"$regex": vendor, "$options": "i"}
    if product:
        query["product"] = {"$regex": product, "$options": "i"}

    cursor = COL_CVES.find(query).sort(sort_field, sort_dir).skip(skip).limit(limit)
    items = [_to_output(d) for d in cursor]
    total = COL_CVES.count_documents(query)
    return {"total": total, "limit": limit, "skip": skip, "items": items}

def get_cve_by_id(cve_id):
    return _to_output(COL_CVES.find_one({"cve_id": cve_id}))
