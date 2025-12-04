"""
PHASE 3 — STEP 3 (FINAL)
Create vuln_matches collection schema + indexes.

This script:
 - Creates the collection if it does not exist
 - Ensures important indexes (performance)
 - Confirms structure
"""

from pymongo import MongoClient

MONGO_URI = "mongodb://admin:admin123@localhost:27017/?authSource=admin"
DB_NAME = "vulnerability_logs"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

COL_NAME = "vuln_matches"

def setup_collection():
    print("[+] Setting up vuln_matches collection...")

    # Create collection only if missing
    if COL_NAME not in db.list_collection_names():
        db.create_collection(COL_NAME)
        print("[✓] Created collection: vuln_matches")
    else:
        print("[i] Collection already exists.")

    # Create indexes for speed
    db[COL_NAME].create_index("log_id")
    db[COL_NAME].create_index("cve_id")
    db[COL_NAME].create_index("severity")
    db[COL_NAME].create_index("host")
    db[COL_NAME].create_index("matched_at")

    print("[✓] Indexes created.")
    print("[✓] vuln_matches collection ready.")


if __name__ == "__main__":
    setup_collection()
