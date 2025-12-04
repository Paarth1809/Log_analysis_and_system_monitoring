# backend/services/alert_service.py
from datetime import datetime
from bson import ObjectId
from ..db import COL_ALERTS

def _to_output(doc):
    if not doc:
        return None
    out = dict(doc)
    out["_id"] = str(out.get("_id")) if out.get("_id") else None
    if "alert_generated_at" in out and hasattr(out["alert_generated_at"], "isoformat"):
        out["alert_generated_at"] = out["alert_generated_at"].isoformat()
    return out

def find_alerts(host=None, limit=50, skip=0, sort_field="alert_generated_at", sort_dir=-1):
    query = {}
    if host:
        query["host"] = host
    cursor = COL_ALERTS.find(query).sort(sort_field, sort_dir).skip(skip).limit(limit)
    items = [_to_output(d) for d in cursor]
    total = COL_ALERTS.count_documents(query)
    return {"total": total, "limit": limit, "skip": skip, "items": items}

def create_alert(alert_obj):
    alert_obj.setdefault("alert_generated_at", datetime.utcnow())
    res = COL_ALERTS.insert_one(alert_obj)
    return str(res.inserted_id)
