"""
PHASE 3 — STEP 2 (FINAL)
Severity Mapping for CVE Records and Vulnerability Matches

This script:
 - Reads CVSS numeric score from cve_database
 - Maps score → Critical / High / Medium / Low / None
 - Updates all CVE entries with a 'severity' field
 - Updates all vuln_matches entries (whenever vuln_matches exists)
"""

from pymongo import MongoClient

# ----------------------------
# CONFIG
# ----------------------------
MONGO_URI = "mongodb://admin:admin123@localhost:27017/?authSource=admin"
DB_NAME = "vulnerability_logs"

CVE_COL = "cve_database"
MATCH_COL = "vuln_matches"  # may not exist yet — safe

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

cves = db[CVE_COL]
matches = db[MATCH_COL]


# ----------------------------
# SEVERITY MAPPING
# ----------------------------
def cvss_to_severity(score):
    """Convert CVSS score → Severity label"""

    if score is None:
        return "Unknown"

    try:
        score = float(score)
    except:
        return "Unknown"

    if score == 0.0:
        return "None"
    if score >= 9.0:
        return "Critical"
    if score >= 7.0:
        return "High"
    if score >= 4.0:
        return "Medium"
    if score > 0.0:
        return "Low"

    return "Unknown"


# ----------------------------
# UPDATE ALL CVEs
# ----------------------------
def update_cve_severities():
    print("[+] Updating severity for all CVEs...")

    count = 0
    for cve in cves.find({}):
        score = cve.get("cvss_score")
        severity = cvss_to_severity(score)

        cves.update_one(
            {"_id": cve["_id"]},
            {"$set": {"severity": severity}}
        )
        count += 1

    print(f"[✓] Updated severity for {count} CVEs.")


# ----------------------------
# UPDATE vuln_matches (when created later)
# ----------------------------
def update_match_severities():
    try:
        print("[+] Updating severity for vuln_matches...")

        count = 0
        for doc in matches.find({}):
            cvss = doc.get("cvss_score")
            severity = cvss_to_severity(cvss)

            matches.update_one(
                {"_id": doc["_id"]},
                {"$set": {"severity": severity}}
            )
            count += 1

        print(f"[✓] Updated severity for {count} vulnerability matches.")

    except Exception:
        print("[INFO] No vul_nmatches collection yet — skipping (this is normal).")


# ----------------------------
# RUN MAIN
# ----------------------------
if __name__ == "__main__":
    update_cve_severities()
    update_match_severities()
    print("\n[✓] Severity Mapping Completed.\n")
