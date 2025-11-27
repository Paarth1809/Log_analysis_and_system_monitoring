"""
PHASE 3 — STEP 4 (FINAL)
Generate Stats from vuln_matches

Outputs:
 - Severity counts
 - Top vulnerable hosts
 - Top CVEs
"""

from pymongo import MongoClient
from collections import Counter

# ----------------------------
# CONFIG
# ----------------------------
MONGO_URI = "mongodb://admin:admin123@localhost:27017/?authSource=admin"
DB_NAME = "vulnerability_logs"
MATCH_COL = "vuln_matches"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
matches = db[MATCH_COL]


# ----------------------------
# SEVERITY COUNTS
# ----------------------------
def get_severity_counts():
    counts = Counter()
    for m in matches.find():
        sev = m.get("severity", "Unknown")
        counts[sev] += 1
    return dict(counts)


# ----------------------------
# TOP VULNERABLE HOSTS
# ----------------------------
def get_top_hosts(limit=10):
    counts = Counter()
    for m in matches.find():
        host = m.get("host", "unknown")
        counts[host] += 1
    return counts.most_common(limit)


# ----------------------------
# TOP CVEs
# ----------------------------
def get_top_cves(limit=10):
    counts = Counter()
    for m in matches.find():
        cve = m.get("cve_id", "unknown")
        counts[cve] += 1
    return counts.most_common(limit)


# ----------------------------
# MAIN
# ----------------------------
def run():
    print("\n[+] Generating Vulnerability Stats...\n")

    sev = get_severity_counts()
    hosts = get_top_hosts()
    cves = get_top_cves()

    print("=== Severity Counts ===")
    if sev:
        for s, c in sev.items():
            print(f"{s}: {c}")
    else:
        print("No severity data (no matches yet).")

    print("\n=== Top Vulnerable Hosts ===")
    if hosts:
        for h, c in hosts:
            print(f"{h}: {c}")
    else:
        print("No vulnerable hosts found.")

    print("\n=== Top CVEs ===")
    if cves:
        for cv, ct in cves:
            print(f"{cv}: {ct}")
    else:
        print("No CVE matches found.")

    print("\n[✓] Stats Generated.\n")


if __name__ == "__main__":
    run()
