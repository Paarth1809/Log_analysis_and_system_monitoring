# backend/app.py
"""
Backend API for Vulnerability Detection System (Phase 5 Step 1)
Framework: Flask (single-file app)

APIs:
  GET /health          -> service health
  GET /logs            -> fetch normalized logs (supports host, limit, skip)
  GET /cves            -> fetch CVEs (supports q, limit, skip)
  GET /alerts          -> fetch alerts (supports host, limit, skip)
  GET /stats           -> aggregated stats: severity counts, top hosts, top CVEs

Run:
  python backend/app.py
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.json_util import dumps
from collections import Counter
from datetime import datetime

# ---------- CONFIG ----------
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://admin:admin123@localhost:27017/?authSource=admin"
)

DB_NAME = os.environ.get("VULN_DB", "vulnerability_logs")

# optional: change host/port here or via env
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8000))

# ---------- APP ----------
app = Flask(__name__)
CORS(app)

# ---------- DB ----------
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# collection handles
COL_LOGS = db.get_collection("normalized_logs")
COL_CVES = db.get_collection("cve_database")
COL_ALERTS = db.get_collection("alerts")
COL_MATCHES = db.get_collection("vuln_matches")


# ---------- HELPERS ----------
def parse_int(qs_value, default):
    try:
        return int(qs_value)
    except Exception:
        return default


def to_jsonable(cursor_or_doc):
    """
    Convert pymongo cursor or document to JSON serializable form (string).
    We'll return via flask jsonify after loading.
    """
    # dumps returns a JSON string; jsonify will double-encode if we pass string
    # so return parsed python object: use bson.json_util.loads by indirect approach
    # but simplest: return JSON string directly and set response mimetype application/json.
    return dumps(cursor_or_doc)


# ---------- ROUTES ----------
@app.route("/health", methods=["GET"])
def health():
    try:
        # quick ping
        client.admin.command("ping")
        return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()}), 200
    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "Vulnerability Detection System API", 
        "endpoints": ["/health", "/logs", "/cves", "/alerts", "/stats"]
    }), 200


@app.route("/logs", methods=["GET"])
def get_logs():
    """
    GET /logs
    Query params:
      host  -> filter by host
      limit -> integer
      skip  -> integer
    """
    host = request.args.get("host")
    limit = parse_int(request.args.get("limit"), 50)
    skip = parse_int(request.args.get("skip"), 0)

    query = {}
    if host:
        query["host"] = host

    cursor = COL_LOGS.find(query).skip(skip).limit(limit)
    total = COL_LOGS.count_documents(query)

    return app.response_class(
        response=to_jsonable({"total": total, "limit": limit, "skip": skip, "items": list(cursor)}),
        status=200,
        mimetype="application/json"
    )


@app.route("/cves", methods=["GET"])
def get_cves():
    """
    GET /cves
    Query params:
      q     -> search term for cve_id or product or vendor
      limit -> integer
      skip  -> integer
    """
    q = request.args.get("q", "").strip()
    limit = parse_int(request.args.get("limit"), 50)
    skip = parse_int(request.args.get("skip"), 0)

    query = {}
    if q:
        # simple text match across few fields (case-insensitive)
        query["$or"] = [
            {"cve_id": {"$regex": q, "$options": "i"}},
            {"vendor": {"$regex": q, "$options": "i"}},
            {"product": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}}
        ]

    cursor = COL_CVES.find(query).skip(skip).limit(limit)
    total = COL_CVES.count_documents(query)

    return app.response_class(
        response=to_jsonable({"total": total, "limit": limit, "skip": skip, "items": list(cursor)}),
        status=200,
        mimetype="application/json"
    )


@app.route("/alerts", methods=["GET"])
def get_alerts():
    """
    GET /alerts
    Query params:
      host  -> filter by host
      limit -> integer
      skip  -> integer
    """
    host = request.args.get("host")
    limit = parse_int(request.args.get("limit"), 50)
    skip = parse_int(request.args.get("skip"), 0)

    query = {}
    if host:
        query["host"] = host

    cursor = COL_ALERTS.find(query).sort("alert_generated_at", -1).skip(skip).limit(limit)
    total = COL_ALERTS.count_documents(query)

    return app.response_class(
        response=to_jsonable({"total": total, "limit": limit, "skip": skip, "items": list(cursor)}),
        status=200,
        mimetype="application/json"
    )


@app.route("/stats", methods=["GET"])
def get_stats():
    """
    GET /stats
    Returns:
      - severity_counts (aggregated from vuln_matches)
      - top_hosts (by number of matches)
      - top_cves (by frequency)
      - totals
    """
    # severity counts
    pipeline_sev = [
        {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
    ]
    sev_cursor = COL_MATCHES.aggregate(pipeline_sev)
    severity_counts = {doc["_id"] if doc["_id"] else "Unknown": doc["count"] for doc in sev_cursor}

    # top hosts
    pipeline_hosts = [
        {"$group": {"_id": "$host", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    hosts_cursor = COL_MATCHES.aggregate(pipeline_hosts)
    top_hosts = [{"host": doc["_id"], "count": doc["count"]} for doc in hosts_cursor]

    # top CVEs
    pipeline_cves = [
        {"$group": {"_id": "$cve_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    cves_cursor = COL_MATCHES.aggregate(pipeline_cves)
    top_cves = [{"cve_id": doc["_id"], "count": doc["count"]} for doc in cves_cursor]

    # totals
    total_logs = COL_LOGS.estimated_document_count()
    total_cves = COL_CVES.estimated_document_count()
    total_alerts = COL_ALERTS.estimated_document_count()
    total_matches = COL_MATCHES.estimated_document_count()

    out = {
        "generated_at": datetime.utcnow().isoformat(),
        "totals": {
            "logs": total_logs,
            "cves": total_cves,
            "alerts": total_alerts,
            "matches": total_matches
        },
        "severity_counts": severity_counts,
        "top_hosts": top_hosts,
        "top_cves": top_cves
    }
    return jsonify(out), 200


# ---------- ERROR HANDLING ----------
@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "internal_server_error", "message": str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "not_found", "message": "endpoint not found"}), 404


# ---------- SCHEDULER ----------
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import sys

# Import engines (ensure they are in python path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from matching_engine.matcher import process_logs as run_matcher
from alerts.alert_engine import main as run_alert_engine

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Run matcher every 5 minutes
    scheduler.add_job(func=run_matcher, trigger="interval", minutes=5, id="matcher_job")
    
    # Run alert engine every 1 minute
    scheduler.add_job(func=run_alert_engine, trigger="interval", minutes=1, id="alert_job")
    
    scheduler.start()
    print("[+] Scheduler started: Matcher (5m), Alerts (1m)")
    
    # Shut down scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

# ---------- MAIN ----------
if __name__ == "__main__":
    print("Starting Backend API (Flask) on {}:{} ...".format(HOST, PORT))
    
    # Start Scheduler
    # Only run scheduler if not in reloader mode (to avoid duplicate jobs during dev)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_scheduler()
        
    app.run(host=HOST, port=PORT, debug=True)
