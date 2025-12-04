"""
<<<<<<< HEAD
PHASE 3 — STEP 1 (API-BASED MATCHING)

This matcher:
 1. Scans normalized logs.
 2. Identifies software/version info.
 3. Queries NVD API directly for vulnerabilities (using caching to avoid rate limits).
 4. Stores matches in 'vuln_matches'.
"""

import re
import time
from pymongo import MongoClient
from datetime import datetime
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cve_engine.nvd_api import query_nvd_cves
=======
PHASE 3 — STEP 1 (FINAL & OPTIMIZED FOR AUTH.LOG + ELASTIC LOGS)

This matcher handles:
 - Linux Kernel CVEs (version extracted from kernel log lines)
 - log.software mapping → linux_kernel
 - version extraction from system messages
 - fast CVE lookup with indexing
 - stores matches in vuln_matches

Other logs (auth, sshd, audit, cron) contain NO version → skipped safely.
"""

import re
from pymongo import MongoClient
from datetime import datetime
from cve_engine.version_compare import satisfies
>>>>>>> cd260ba9258ba3c2c7ffb1588424565f3f1c9eae

# ----------------------------
# CONFIG
# ----------------------------
MONGO_URI = "mongodb://admin:admin123@localhost:27017/?authSource=admin"
DB = "vulnerability_logs"
<<<<<<< HEAD
LOGS_COL = "normalized_logs"
MATCH_COL = "vuln_matches"
CVE_COL = "cve_database"

# Limit logs to process to avoid API spamming during testing
LOG_LIMIT = 1000 

client = MongoClient(MONGO_URI)
db = client[DB]
logs = db[LOGS_COL]
matches = db[MATCH_COL]
cves_col = db[CVE_COL]

# Cache: "software version" -> [cve_list]
CVE_CACHE = {}
=======

LOGS_COL = "normalized_logs"
CVE_COL = "cve_database"
MATCH_COL = "vuln_matches"

# Limit logs per run (safe)
LOG_LIMIT = 10000

client = MongoClient(MONGO_URI)
db = client[DB]

logs = db[LOGS_COL]
cves = db[CVE_COL]
matches = db[MATCH_COL]

# ----------------------------
# SOFTWARE NORMALIZATION
# ----------------------------
def normalize_software(name: str):
    if not name:
        return None

    s = name.lower()

    if "kernel" in s:
        return "linux_kernel"

    return None  # other logs not matchable

>>>>>>> cd260ba9258ba3c2c7ffb1588424565f3f1c9eae

# ----------------------------
# VERSION EXTRACTION
# ----------------------------
<<<<<<< HEAD
KERNEL_REGEX = re.compile(r"Linux version\s+([0-9]+\.[0-9]+\.[0-9]+)", re.IGNORECASE)

def extract_software_version(log):
    """
    Returns a tuple (software, version) or (None, None)
    """
    # 1. Try explicit fields
    sw = log.get("software")
    ver = log.get("version")
    
    # 2. Try Kernel Regex in message
    msg = log.get("message", "")
    m = KERNEL_REGEX.search(msg)
    if m:
        return "linux_kernel", m.group(1)

    # 3. Return explicit if valid
    if sw and ver and sw.lower() != "unknown" and ver.lower() != "unknown":
        return sw, ver
        
    return None, None

# ----------------------------
# MATCHING LOGIC
# ----------------------------
# ----------------------------
# MATCHING LOGIC
# ----------------------------
def main(payload=None):
    print("\n[+] Starting API-based Vulnerability Matching...")
    print(f"[+] Log Limit: {LOG_LIMIT}")
    
    cursor = logs.find().limit(LOG_LIMIT)
    processed = 0
    new_matches = 0
    new_cves_stored = 0
    
    for log in cursor:
        processed += 1
        sw, ver = extract_software_version(log)
        
        if not sw or not ver:
            continue
            
        # Construct query key
        query_key = f"{sw} {ver}"
        
        # Check Cache
        if query_key in CVE_CACHE:
            cve_list = CVE_CACHE[query_key]
        else:
            # Query API
            # Sleep slightly to be nice to API if not cached
            time.sleep(0.5) 
            cve_list = query_nvd_cves(query_key, limit=5) # Limit 5 matches per software to save space/time
            CVE_CACHE[query_key] = cve_list
            
            # Store fetched CVEs in database for frontend visibility
            for cve in cve_list:
                # Upsert to avoid duplicates
                res = cves_col.update_one(
                    {"cve_id": cve["cve_id"]},
                    {"$set": {
                        "cve_id": cve["cve_id"],
                        "description": cve["description"],
                        "cvss_score": cve["cvss_score"],
                        "severity": cve["severity"],
                        "last_updated": datetime.utcnow(),
                        "source": "NVD_API"
                    }},
                    upsert=True
                )
                if res.upserted_id:
                    new_cves_stored += 1

        # Record Matches
        for cve in cve_list:
            match_id = f"{log['_id']}__{cve['cve_id']}"
            
            # Check if match already exists
            if matches.find_one({"_id": match_id}):
                continue
                
            match_doc = {
                "_id": match_id,
                "matched_at": datetime.utcnow(),
                "log_id": str(log["_id"]),
                "host": log.get("host"),
                "timestamp": log.get("timestamp"),
                "software": sw,
                "version": ver,
                "cve_id": cve["cve_id"],
                "severity": cve["severity"],
                "cvss_score": cve["cvss_score"],
                "description": cve["description"],
                "message": log.get("message")
            }
            
            matches.insert_one(match_doc)
            new_matches += 1
            print(f"[MATCH] {sw} {ver} -> {cve['cve_id']} ({cve['severity']})")

    print(f"\n[✓] Matching Completed")
    print(f"Processed: {processed}")
    print(f"New Matches: {new_matches}")
    print(f"New CVEs Stored: {new_cves_stored}")
    print(f"Unique Software/Versions Queried: {len(CVE_CACHE)}")
    
    return {"status": "completed", "matches": new_matches}

if __name__ == "__main__":
    main()

=======
KERNEL_REGEX = re.compile(
    r"Linux version\s+([0-9]+\.[0-9]+\.[0-9]+)", re.IGNORECASE
)

def extract_version(log_doc):
    msg = log_doc.get("message", "")

    # extract kernel version
    m = KERNEL_REGEX.search(msg)
    if m:
        return m.group(1)

    # fallback if version exists
    version = log_doc.get("version")
    if version and version != "N/A":
        return version

    return None


# ----------------------------
# GET CVEs FOR PRODUCT
# ----------------------------
def get_kernel_cves():
    return list(cves.find(
        {"product": {"$regex": "linux", "$options": "i"}},
        {"cve_id": 1, "affected_versions": 1, "severity": 1}
    ))


# ----------------------------
# MATCH ONE LOG
# ----------------------------
def match_log(log):
    sw = log.get("software")
    normalized = normalize_software(sw)

    if normalized != "linux_kernel":
        return []  # skip non-kernel logs

    version = extract_version(log)
    if not version:
        return []  # no version → can't match

    results = []
    kernel_cves = get_kernel_cves()

    for cve in kernel_cves:
        for vr in cve.get("affected_versions", []):
            try:
                if satisfies(version, vr):
                    results.append((cve, vr))
            except:
                pass

    return results


# ----------------------------
# STORE MATCH
# ----------------------------
def store_match(log, cve, vr):
    mid = f"{log['_id']}__{cve['cve_id']}"

    if matches.find_one({"_id": mid}):
        return False

    matches.insert_one({
        "_id": mid,
        "matched_at": datetime.utcnow(),
        "log_id": str(log["_id"]),
        "software": log.get("software"),
        "kernel_version": extract_version(log),
        "cve_id": cve["cve_id"],
        "severity": cve.get("severity"),
        "affected_version_range": vr,
        "message": log.get("message")
    })

    return True


# ----------------------------
# MAIN RUNNER
# ----------------------------
def run():
    print("\n[+] Running Kernel Vulnerability Matching Engine...\n")

    processed = 0
    new_matches = 0

    cursor = logs.find().limit(LOG_LIMIT)

    for log in cursor:
        processed += 1

        matches_found = match_log(log)

        for cve, vr in matches_found:
            if store_match(log, cve, vr):
                new_matches += 1
                print(f"[MATCH] linux_kernel {extract_version(log)} -> {cve['cve_id']} [{vr}]")

    print("\n[✓] Matching Completed")
    print(f"Processed Logs : {processed}")
    print(f"New Matches    : {new_matches}")


# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    run()
>>>>>>> cd260ba9258ba3c2c7ffb1588424565f3f1c9eae
