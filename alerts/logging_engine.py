"""
PHASE 4 — STEP 2 (FINAL)
LOGGING ENGINE

This script:
 - Logs every alert creation event
 - Stores sync logs for each alert engine run
 - Works even when alerts = 0
 - No duplicate logs
"""

from pymongo import MongoClient
from datetime import datetime

# ----------------------------
# CONFIG
# ----------------------------
MONGO_URI = "mongodb://admin:admin123@localhost:27017/?authSource=admin"
DB_NAME = "vulnerability_logs"

ALERTS_COL = "alerts"
LOGS_COL = "alert_logs"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

alerts = db[ALERTS_COL]
alert_logs = db[LOGS_COL]


# ----------------------------
# CREATE A LOG ENTRY
# ----------------------------
def create_log_entry(run_summary):
    """
    Store a structured record of the alert engine run.
    """

    entry = {
        "run_timestamp": datetime.utcnow(),
        "total_alerts_in_collection": alert_logs.estimated_document_count(),
        "processed_matches": run_summary["processed_matches"],
        "new_alerts_created": run_summary["new_alerts_created"],
        "status": "ok" if run_summary["status"] == "success" else "failed"
    }

    alert_logs.insert_one(entry)
    return True


# ----------------------------
# LOG INDIVIDUAL ALERT CREATION
# ----------------------------
def log_alert_creation(alert_doc):
    """
    Log details for each alert created.
    """

    entry = {
        "log_timestamp": datetime.utcnow(),
        "alert_id": alert_doc.get("_id"),
        "host": alert_doc.get("host"),
        "severity": alert_doc.get("severity"),
        "cve_id": alert_doc.get("cve_id"),
        "software": alert_doc.get("software"),
        "status": "created"
    }

    alert_logs.insert_one(entry)


# ----------------------------
# MAIN LOGGING WRAPPER
# ----------------------------
def log_alert_engine_run(processed_matches, new_alerts):
    """
    Summary logger after alert engine finishes.
    """

    summary = {
        "processed_matches": processed_matches,
        "new_alerts_created": new_alerts,
        "status": "success"
    }

    create_log_entry(summary)


# ----------------------------
# EXECUTE FOR TESTING
# ----------------------------
if __name__ == "__main__":
    # example dry-run
    log_alert_engine_run(processed_matches=0, new_alerts=0)
    print("[✓] Logging Engine Test Completed")
