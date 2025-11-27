# backend/services/log_service.py
from datetime import datetime
from bson import ObjectId
from ..db import COL_LOGS

def _to_output(doc):
    if not doc:
        return None
    out = dict(doc)
    # convert _id to string
    _id = out.get("_id")
    out["_id"] = str(_id) if _id is not None else None
    # convert datetime-like fields to ISO strings if present
    ts = out.get("timestamp")
    if hasattr(ts, "isoformat"):
        out["timestamp"] = ts.isoformat()
    return out

def build_query(host=None, software=None, event_type=None, q=None, start=None, end=None):
    query = {}
    if host:
        query["host"] = host
    if software:
        query["software"] = {"$regex": software, "$options": "i"}
    if event_type:
        query["event_type"] = event_type
    if q:
        query["$or"] = [
            {"message": {"$regex": q, "$options": "i"}},
            {"software": {"$regex": q, "$options": "i"}},
            {"host": {"$regex": q, "$options": "i"}}
        ]
    # timestamp range
    if start or end:
        ts_query = {}
        if start:
            ts_query["$gte"] = datetime.fromisoformat(start)
        if end:
            ts_query["$lte"] = datetime.fromisoformat(end)
        query["timestamp"] = ts_query
    return query

def find_logs(host=None, software=None, event_type=None, q=None, start=None, end=None, limit=50, skip=0, sort="-timestamp"):
    query = build_query(host, software, event_type, q, start, end)
    sort_field = "timestamp"
    sort_dir = -1
    if sort:
        if sort.startswith("-"):
            sort_field = sort[1:]
            sort_dir = -1
        else:
            sort_field = sort
            sort_dir = 1
    cursor = COL_LOGS.find(query).sort(sort_field, sort_dir).skip(skip).limit(limit)
    items = [_to_output(d) for d in cursor]
    total = COL_LOGS.count_documents(query)
    return {"total": total, "limit": limit, "skip": skip, "items": items}
