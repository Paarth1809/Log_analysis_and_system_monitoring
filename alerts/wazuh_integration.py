"""
alerts/wazuh_integration.py
Phase 4 Step 4 — Wazuh Integration (FINAL)

Features:
 - Reads unexported alerts from MongoDB `alerts` collection
 - Exports them to a JSONL file (Wazuh-friendly lines)
 - Optionally POSTs each alert to a Wazuh Manager API endpoint
 - Marks alerts as exported with timestamp + method
 - Works when there are 0 alerts (prints a friendly message)
 - Uses timezone-aware datetimes

Usage:
  - Edit CONFIG below (MONGO_URI and optional WAZUH_API_URL + API_KEY)
  - Run: python -m alerts.wazuh_integration
  - Or: python alerts/wazuh_integration.py

Optional:
  pip install requests
"""

import os
import json
from datetime import datetime, timezone
from pymongo import MongoClient

# Optional (only needed if you're pushing to Wazuh API)
try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    REQUESTS_AVAILABLE = False

# -----------------------
# CONFIG - modify if needed
# -----------------------
MONGO_URI = "mongodb://admin:admin123@localhost:27017/?authSource=admin"
DB_NAME = "vulnerability_logs"

ALERTS_COL = "alerts"
EXPORT_DIR = "alerts/wazuh_exports"
EXPORT_FILE = os.path.join(EXPORT_DIR, "alerts_export.jsonl")

# If you want to push to a Wazuh Manager REST endpoint, set these:
# Example: WAZUH_API_URL = "https://wazuh-manager.example:55000/alerts"
WAZUH_API_URL = None       # <-- set to your Wazuh API endpoint (optional)
WAZUH_API_KEY = None       # <-- set to API key/token if required (optional)
# -----------------------

os.makedirs(EXPORT_DIR, exist_ok=True)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
alerts_col = db[ALERTS_COL]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def fetch_unexported_alerts(limit=1000):
    """
    Fetch alerts that haven't been exported yet.
    We mark exported alerts by setting field 'exported': True, 'exported_at', 'export_method'
    """
    query = {"exported": {"$ne": True}}
    # limit to avoid huge batches — adjust as needed
    return list(alerts_col.find(query).limit(limit))


def transform_for_wazuh(alert_doc):
    """
    Convert your alert document to a Wazuh-friendly alert shape.
    We keep original fields and add a small 'wazuh' envelope.
    """
    # Keep original alert fields safe for JSON
    safe = {k: (v if not isinstance(v, (bytes,)) else str(v)) for k, v in alert_doc.items() if k != "_id"}
    envelope = {
        "timestamp": safe.get("alert_generated_at") or now_iso(),
        "rule": {
            "id": "vuln_detect_001",
            "description": f"Matched CVE {safe.get('cve_id')}",
            "level": severity_to_level(safe.get("severity"))
        },
        "agent": {
            "id": safe.get("host", "unknown"),
            "name": safe.get("host", "unknown")
        },
        "id": str(alert_doc.get("_id")) + "__wazuh",
        "full_log": safe
    }
    return envelope


def severity_to_level(sev):
    """
    Map severity label to a numeric Wazuh/OSSEC level (1-15).
    Use conservative mapping:
     - Critical -> 12
     - High -> 10
     - Medium -> 6
     - Low -> 3
     - Unknown -> 1
    """
    if not sev:
        return 1
    s = str(sev).lower()
    if "critical" in s:
        return 12
    if "high" in s:
        return 10
    if "medium" in s:
        return 6
    if "low" in s:
        return 3
    return 1


def export_to_file(alerts, path=EXPORT_FILE):
    """
    Export a list of transformed alerts to a JSONL file (append mode).
    Each line is a JSON object (Wazuh-friendly).
    """
    written = 0
    with open(path, "a", encoding="utf-8") as fh:
        for a in alerts:
            json_line = json.dumps(a, ensure_ascii=False)
            fh.write(json_line + "\n")
            written += 1
    return written


def push_to_wazuh_api(alerts, api_url, api_key=None, timeout=10):
    """
    POST each alert to Wazuh API endpoint.
    Returns count pushed and list of errors.
    If `requests` is not installed or api_url is None, this becomes a no-op.
    """
    if not REQUESTS_AVAILABLE:
        return 0, ["requests library not installed"]
    if not api_url:
        return 0, ["no_api_url_configured"]

    pushed = 0
    errors = []

    headers = {"Content-Type": "application/json"}
    if api_key:
        # conservative header usage — change to your API auth scheme (Bearer, Token) if needed
        headers["Authorization"] = f"Bearer {api_key}"

    for alert in alerts:
        try:
            resp = requests.post(api_url, json=alert, headers=headers, timeout=timeout, verify=False)
            if 200 <= resp.status_code < 300:
                pushed += 1
            else:
                errors.append(f"status:{resp.status_code} body:{resp.text}")
        except Exception as e:
            errors.append(str(e))

    return pushed, errors


def mark_alerts_exported(original_alert_docs, method="file"):
    """
    Mark alerts in MongoDB as exported. Use original docs to find by _id.
    """
    now = now_iso()
    updated = 0
    for doc in original_alert_docs:
        res = alerts_col.update_one(
            {"_id": doc["_id"]},
            {"$set": {"exported": True, "exported_at": now, "export_method": method}}
        )
        updated += res.modified_count
    return updated


def run_export(limit=1000):
    """
    Main flow:
      - fetch unexported alerts
      - transform -> wazuh shape
      - export to file
      - optionally push to wazuh manager
      - mark exported
    """
    raw_alerts = fetch_unexported_alerts(limit=limit)
    total = len(raw_alerts)
    print(f"\n[+] Found {total} unexported alerts")

    if total == 0:
        print("[i] Nothing to export. Exiting cleanly.")
        return {"found": 0, "exported_file_count": 0, "pushed": 0, "errors": []}

    transformed = [transform_for_wazuh(a) for a in raw_alerts]

    # 1) Export to file
    written = export_to_file(transformed, EXPORT_FILE)
    print(f"[+] Exported {written} alerts to file: {EXPORT_FILE}")

    # 2) Optionally push to API
    pushed = 0
    push_errors = []
    if WAZUH_API_URL:
        pushed, push_errors = push_to_wazuh_api(transformed, WAZUH_API_URL, WAZUH_API_KEY)
        print(f"[+] Pushed {pushed} alerts to Wazuh API: {WAZUH_API_URL}")
        if push_errors:
            print(f"[!] Some push errors: {len(push_errors)} (see logs)")

    # 3) Mark exported in DB
    updated = mark_alerts_exported(raw_alerts, method=("api" if pushed else "file"))
    print(f"[+] Marked {updated} alerts as exported in MongoDB")

    return {"found": total, "exported_file_count": written, "pushed": pushed, "errors": push_errors}


# -----------------------
# CLI run
# -----------------------
if __name__ == "__main__":
    print("\n[+] Running Wazuh Integration Exporter")
    summary = run_export(limit=2000)
    print("\n[✓] Done. Summary:")
    print(json.dumps(summary, indent=2))
