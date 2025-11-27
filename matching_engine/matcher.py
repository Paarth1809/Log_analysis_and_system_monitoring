"""
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

# ----------------------------
# CONFIG
# ----------------------------
MONGO_URI = "mongodb://admin:admin123@localhost:27017/?authSource=admin"
DB = "vulnerability_logs"

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


# ----------------------------
# VERSION EXTRACTION
# ----------------------------
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
