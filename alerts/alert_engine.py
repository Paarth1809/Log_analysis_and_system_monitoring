"""
PHASE 4 — STEP 1 (FINAL)
ALERT ENGINE

This module:
 - Reads all entries from vuln_matches
 - Creates alerts for each match
 - Stores alerts into alerts collection
 - Avoids duplicates
 - Adds timestamp, host, severity, cve_id
 - Works even if there are 0 vulnerability matches
"""

from pymongo import MongoClient
from datetime import datetime

# ----------------------------
# CONFIG
# ----------------------------
MONGO_URI = "mongodb://admin:admin123@localhost:27017/?authSource=admin"
DB_NAME = "vulnerability_logs"

MATCH_COL = "vuln_matches"
ALERT_COL = "alerts"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

matches = db[MATCH_COL]
alerts = db[ALERT_COL]

# ----------------------------
# CREATE ALERT DOCUMENT
# ----------------------------
def create_alert(match_doc):
    """
    Convert a match entry into an alert document
    """
    alert_id = f"{match_doc['_id']}__alert"

    # prevent duplicate alerts
    if alerts.find_one({"_id": alert_id}):
        return False

    alert_doc = {
        "_id": alert_id,
        "alert_generated_at": datetime.utcnow(),

        # host metadata
        "host": match_doc.get("host", "unknown"),

        # vulnerability info
        "cve_id": match_doc.get("cve_id"),
        "severity": match_doc.get("severity", "Unknown"),
        "cvss_score": match_doc.get("cvss_score", 0),
        "affected_versions": match_doc.get("affected_versions", []),

        # log info
        "software": match_doc.get("software"),
        "log_version": match_doc.get("log_version"),
        "log_message": match_doc.get("log_message"),
        "log_timestamp": match_doc.get("log_timestamp"),
    }

    alerts.insert_one(alert_doc)
    return True


# ----------------------------
# RUN ALERT ENGINE
# ----------------------------
def run_alert_engine():
    print("\n[+] Running Alert Engine...\n")

    count = 0
    new_alerts = 0

    for match in matches.find():
        count += 1
        ok = create_alert(match)
        if ok:
            new_alerts += 1
            print(f"[ALERT] {match.get('host')} -> {match.get('cve_id')} ({match.get('severity')})")

    print("\n[✓] Alert Engine Complete")
    print(f"Processed Matches : {count}")
    print(f"New Alerts       : {new_alerts}\n")


# ----------------------------
# EXECUTE
# ----------------------------
if __name__ == "__main__":
    run_alert_engine()
