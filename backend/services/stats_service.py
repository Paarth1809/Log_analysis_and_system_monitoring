# backend/services/stats_service.py
from ..db import COL_MATCHES, COL_LOGS, COL_CVES, COL_ALERTS
from datetime import datetime
from pymongo.errors import ServerSelectionTimeoutError

def get_stats(limit_hosts=20, limit_cves=20):
    """Get statistics from database with error handling"""
    # severity counts from vuln_matches
    pipeline_sev = [
        {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
    ]
    try:
        sev_cursor = COL_MATCHES.aggregate(pipeline_sev)
        severity_counts = {doc["_id"] if doc["_id"] else "Unknown": doc["count"] for doc in sev_cursor}
    except (ServerSelectionTimeoutError, Exception):
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    # top hosts
    pipeline_hosts = [
        {"$group": {"_id": "$host", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit_hosts}
    ]
    try:
        hosts = [{"host": d["_id"], "count": d["count"]} for d in COL_MATCHES.aggregate(pipeline_hosts)]
    except (ServerSelectionTimeoutError, Exception):
        hosts = []

    # top CVEs
    pipeline_cves = [
        {"$group": {"_id": "$cve_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit_cves}
    ]
    try:
        top_cves = [{"cve_id": d["_id"], "count": d["count"]} for d in COL_MATCHES.aggregate(pipeline_cves)]
    except (ServerSelectionTimeoutError, Exception):
        top_cves = []

    # Get totals with error handling
    try:
        logs_count = COL_LOGS.estimated_document_count()
    except (ServerSelectionTimeoutError, Exception):
        logs_count = 0
        
    try:
        cves_count = COL_CVES.estimated_document_count()
    except (ServerSelectionTimeoutError, Exception):
        cves_count = 0
        
    try:
        matches_count = COL_MATCHES.estimated_document_count()
    except (ServerSelectionTimeoutError, Exception):
        matches_count = 0
        
    try:
        alerts_count = COL_ALERTS.estimated_document_count()
    except (ServerSelectionTimeoutError, Exception):
        alerts_count = 0

    totals = {
        "logs": logs_count,
        "cves": cves_count,
        "alerts": alerts_count,
        "matches": matches_count
    }

    # Activity Trend (Last 24 hours)
    try:
        pipeline_trend = [
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%H:00", "date": "$timestamp"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        # Logs trend
        logs_trend = {d["_id"]: d["count"] for d in COL_LOGS.aggregate(pipeline_trend)}
        
        # Alerts trend (use alert_generated_at instead of timestamp)
        pipeline_alerts_trend = [
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%H:00", "date": "$alert_generated_at"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        alerts_trend = {d["_id"]: d["count"] for d in COL_ALERTS.aggregate(pipeline_alerts_trend)}
        
        # Merge and format
        # Create a list of last 24 hours or just available hours
        all_hours = sorted(list(set(list(logs_trend.keys()) + list(alerts_trend.keys()))))
        activity_trend = []
        for h in all_hours:
            activity_trend.append({
                "time": h,
                "logs": logs_trend.get(h, 0),
                "alerts": alerts_trend.get(h, 0)
            })
            
        # If empty, provide some default empty data
        if not activity_trend:
            activity_trend = [{"time": "00:00", "logs": 0, "alerts": 0}]
            
    except (ServerSelectionTimeoutError, Exception):
        activity_trend = [{"time": "00:00", "logs": 0, "alerts": 0}]

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "totals": totals,
        "severity_counts": severity_counts,
        "top_hosts": hosts,
        "top_cves": top_cves,
        "activity_trend": activity_trend
    }
