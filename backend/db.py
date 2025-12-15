# backend/db.py
from pymongo import MongoClient
from .config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
try:
    client.admin.command("ping")
    print("MongoDB connected successfully")
except Exception as e:
    print(f"Warning: Could not connect to MongoDB: {e}")
db = client[DB_NAME]

# collection handles (reuse across services)
COL_LOGS = db["normalized_logs"]
COL_CVES = db["cve_database"]
COL_ALERTS = db["alerts"]
COL_MATCHES = db["vuln_matches"]
COL_SYNC_LOGS = db.get_collection("sync_logs")
