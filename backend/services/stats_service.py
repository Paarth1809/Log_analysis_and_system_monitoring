# backend/services/stats_service.py
from ..db import COL_MATCHES, COL_LOGS, COL_CVES, COL_ALERTS
from datetime import datetime

def get_stats(limit_hosts=20, limit_cves=20):
    # severity counts from vuln_matches
    pipeline_sev = [
        {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
    ]
    sev_cursor = COL_MATCHES.aggregate(pipeline_sev)
    severity_counts = {doc["_id"] if doc["_id"] else "Unknown": doc["count"] for doc in sev_cursor}

    # top hosts
    pipeline_hosts = [
        {"$group": {"_id": "$host", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit_hosts}
    ]
    hosts = [{"host": d["_id"], "count": d["count"]} for d in COL_MATCHES.aggregate(pipeline_hosts)]

    # top CVEs
    pipeline_cves = [
        {"$group": {"_id": "$cve_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit_cves}
    ]
    top_cves = [{"cve_id": d["_id"], "count": d["count"]} for d in COL_MATCHES.aggregate(pipeline_cves)]

    totals = {
        "logs": COL_LOGS.estimated_document_count(),
        "cves": COL_CVES.estimated_document_count(),
        "alerts": COL_ALERTS.estimated_document_count(),
        "matches": COL_MATCHES.estimated_document_count()
    }

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "totals": totals,
        "severity_counts": severity_counts,
        "top_hosts": hosts,
        "top_cves": top_cves
    }
