"""
PHASE 4 — STEP 1 (FINAL)
ALERT ENGINE V2 (Multi-Rule Support)

This module implements 3 types of alert rules:
1. Severity-Based: From NVD matches (Critical/High).
2. Behavior-Based: Suspicious patterns in logs (e.g. "failed password").
3. Threshold-Based: High frequency events (e.g. >5 failed logins in 1 min).
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import re

# ----------------------------
# CONFIG
# ----------------------------
MONGO_URI = "mongodb://admin:admin123@localhost:27017/?authSource=admin"
DB_NAME = "vulnerability_logs"

MATCH_COL = "vuln_matches"
LOGS_COL = "normalized_logs"
ALERT_COL = "alerts"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

matches = db[MATCH_COL]
logs = db[LOGS_COL]
alerts = db[ALERT_COL]

# ----------------------------
# RULES CONFIGURATION
# ----------------------------

# 2. Behavior Rules (Regex patterns)
BEHAVIOR_RULES = [
    {
        "name": "Suspicious Login Failure",
        "pattern": r"(failed password|authentication failure|invalid user)",
        "severity": "Medium",
        "description": "Multiple failed authentication attempts detected."
    },
    {
        "name": "Unauthorized Access",
        "pattern": r"(unauthorized|permission denied|access denied)",
        "severity": "High",
        "description": "Unauthorized access attempt detected."
    },
    {
        "name": "Root Login Attempt",
        "pattern": r"accepted password for root",
        "severity": "High",
        "description": "Direct root login detected."
    }
]

# 3. Threshold Rules (Aggregation)
THRESHOLD_RULES = [
    {
        "name": "Brute Force Detection",
        "event_type": "failed_login", # or matching pattern
        "threshold": 5,
        "window_minutes": 5,
        "severity": "Critical",
        "description": "High volume of failed logins detected (Brute Force)."
    }
]

# ----------------------------
# HELPER: Create Alert
# ----------------------------
def insert_alert(alert_id, rule_type, rule_name, severity, host, description, details):
    if alerts.find_one({"_id": alert_id}):
        return False

    alert_doc = {
        "_id": alert_id,
        "alert_generated_at": datetime.utcnow(),
        "rule_type": rule_type,     # Severity, Behavior, Threshold
        "rule_name": rule_name,     # e.g. "CVE-2023-1234", "Brute Force"
        "severity": severity,
        "host": host,
        "description": description,
        "details": details          # JSON object with extra info
    }

    alerts.insert_one(alert_doc)
    return True

# ----------------------------
# 1. SEVERITY ALERTS (from Matches)
# ----------------------------
def process_severity_alerts():
    print("[*] Processing Severity-Based Alerts...")
    count = 0
    
    # Only alert on High/Critical vulnerabilities
    cursor = matches.find({"severity": {"$in": ["High", "Critical", "HIGH", "CRITICAL"]}})
    
    for m in cursor:
        alert_id = f"sev_{m['_id']}"
        
        details = {
            "cve_id": m.get("cve_id"),
            "software": m.get("software"),
            "version": m.get("version"),
            "cvss": m.get("cvss_score")
        }
        
        if insert_alert(
            alert_id=alert_id,
            rule_type="Severity",
            rule_name=m.get("cve_id"),
            severity=m.get("severity"),
            host=m.get("host"),
            description=f"Vulnerability found in {m.get('software')} {m.get('version')}",
            details=details
        ):
            count += 1
            print(f"[ALERT] Severity: {m.get('cve_id')} on {m.get('host')}")
            
    return count

# ----------------------------
# 2. BEHAVIOR ALERTS (from Logs)
# ----------------------------
def process_behavior_alerts():
    print("[*] Processing Behavior-Based Alerts...")
    count = 0
    
    # Scan recent logs (e.g. last 1 hour to avoid re-scanning old history forever)
    # For demo, we scan all or limit to recent. Let's scan last 1000 logs for efficiency.
    cursor = logs.find().sort("timestamp", -1).limit(2000)
    
    for log in cursor:
        msg = log.get("message", "")
        if not msg: continue
        
        for rule in BEHAVIOR_RULES:
            if re.search(rule["pattern"], msg, re.IGNORECASE):
                alert_id = f"beh_{log['_id']}_{rule['name'].replace(' ', '_')}"
                
                if insert_alert(
                    alert_id=alert_id,
                    rule_type="Behavior",
                    rule_name=rule["name"],
                    severity=rule["severity"],
                    host=log.get("host"),
                    description=rule["description"],
                    details={"log_message": msg, "timestamp": log.get("timestamp")}
                ):
                    count += 1
                    print(f"[ALERT] Behavior: {rule['name']} on {log.get('host')}")
                    
    return count

# ----------------------------
# 3. THRESHOLD ALERTS (Aggregation)
# ----------------------------
def process_threshold_alerts():
    print("[*] Processing Threshold-Based Alerts...")
    count = 0
    
    # Example: Brute Force (Failed logins > 5 in last 5 mins)
    # Since we don't have real-time streaming, we simulate by aggregating recent logs.
    
    # 1. Find logs matching "failed"
    # In a real system, we'd filter by time window. 
    # Here we just group by host for all "failed" logs in the dataset to demonstrate.
    
    pipeline = [
        {
            "$match": {
                "message": {"$regex": "failed", "$options": "i"}
            }
        },
        {
            "$group": {
                "_id": "$host",
                "count": {"$sum": 1},
                "last_timestamp": {"$max": "$timestamp"}
            }
        },
        {
            "$match": {
                "count": {"$gte": 5}
            }
        }
    ]
    
    results = logs.aggregate(pipeline)
    
    for res in results:
        host = res["_id"]
        cnt = res["count"]
        
        # Stable ID per host for this rule (removed count from ID to prevent duplicates)
        alert_id = f"thresh_bruteforce_{host}"
        
        # Update existing or insert new
        result = alerts.update_one(
            {"_id": alert_id},
            {
                "$set": {
                    "alert_generated_at": datetime.utcnow(),
                    "rule_type": "Threshold",
                    "rule_name": "Brute Force Attack",
                    "severity": "Critical",
                    "host": host,
                    "description": f"Detected {cnt} failed login attempts (Threshold > 5)",
                    "details": {"count": cnt, "last_seen": res["last_timestamp"]}
                }
            },
            upsert=True
        )
        
        if result.upserted_id:
            count += 1
            print(f"[ALERT] New Threshold Alert: Brute Force on {host}")
        elif result.modified_count > 0:
            print(f"[ALERT] Updated Threshold Alert: Brute Force on {host} (Count: {cnt})")
            
    return count

# ----------------------------
# MAIN RUNNER
# ----------------------------
def main(payload=None):
    print("\n[+] Running Alert Engine V2 (Multi-Rule)...\n")
    
    c1 = process_severity_alerts()
    c2 = process_behavior_alerts()
    c3 = process_threshold_alerts()
    
    total = c1 + c2 + c3
    
    print("\n[✓] Alert Engine Complete")
    print(f"Severity Alerts  : {c1}")
    print(f"Behavior Alerts  : {c2}")
    print(f"Threshold Alerts : {c3}")
    print(f"Total New Alerts : {total}\n")
    
    return {"status": "completed", "new_alerts": total}

if __name__ == "__main__":
    main()
