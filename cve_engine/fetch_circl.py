import requests
from pymongo import MongoClient
from datetime import datetime
import time
import re

# ------------------------------------------------------------
# CONNECT TO MONGO
# ------------------------------------------------------------
client = MongoClient("mongodb://admin:admin123@localhost:27017/?authSource=admin")
db = client["vulnerability_logs"]
cve_collection = db["cve_database"]

# ------------------------------------------------------------
# CIRCL API
# ------------------------------------------------------------
CIRCL_URL = "https://cve.circl.lu/api/cve/"

# Valid CVE ID: CVE-YYYY-NNNN
CVE_PATTERN = re.compile(r"^CVE-\d{4}-\d+$")

# ------------------------------------------------------------
# Normalize CIRCL → unified CVE schema
# ------------------------------------------------------------
def normalize_circl(circl_data):
    if not circl_data:
        return None

    cve_id = circl_data.get("id", "UNKNOWN-CVE")

    vendor = "Unknown"
    product = "Unknown"
    versions = []

    # Extract vendor/product/version from CPEs
    for cpe in circl_data.get("vulnerable_configuration", []):
        # Example: "cpe:/a:microsoft:edge_chromium:113.0.1774.35"
        parts = cpe.split(":")
        if len(parts) >= 5:
            vendor = parts[3] or vendor
            product = parts[4] or product
        if len(parts) >= 6:
            versions.append(parts[5])

    cvss_score = circl_data.get("cvss", 0.0)

    if cvss_score >= 9.0:
        severity = "Critical"
    elif cvss_score >= 7.0:
        severity = "High"
    elif cvss_score >= 4.0:
        severity = "Medium"
    else:
        severity = "Low"

    return {
        "_id": cve_id,
        "cve_id": cve_id,
        "vendor": vendor,
        "product": product,
        "affected_versions": versions,
        "cvss_score": cvss_score,
        "severity": severity,
        "description": circl_data.get("summary", ""),
        "published_date": circl_data.get("Published", ""),
        "last_modified": circl_data.get("Modified", ""),
        "cwe": circl_data.get("cwe", "Unknown"),
        "references": circl_data.get("references", []),
        "source": "circl"
    }

# ------------------------------------------------------------
# Insert or update CVEs in MongoDB
# ------------------------------------------------------------
def insert_or_update(cve):
    existing = cve_collection.find_one({"_id": cve["_id"]})

    if existing:
        if cve["last_modified"] > existing["last_modified"]:
            cve_collection.update_one({"_id": cve["_id"]}, {"$set": cve})
            print(f"[UPDATED] {cve['_id']}")
        else:
            print(f"[SKIP] {cve['_id']} (Up-to-date)")
    else:
        cve_collection.insert_one(cve)
        print(f"[NEW] {cve['_id']}")

# ------------------------------------------------------------
# Get valid CVE IDs from our DB
# ------------------------------------------------------------
def get_valid_cve_ids(limit=500):
    """
    Fetch only modern CVEs that CIRCL actually supports.
    We filter for CVE IDs starting with 'CVE-202'
    (covers 2020–2029).
    """
    cursor = cve_collection.find(
        {"_id": {"$regex": "^CVE-202"}},    # Only modern CVEs
        {"_id": 1}
    ).sort("_id", -1).limit(limit)

    return [c["_id"] for c in cursor]


# ------------------------------------------------------------
# Fetch CIRCL data for each CVE
# ------------------------------------------------------------
def fetch_circl_for_existing_cves(limit=200):
    print("\n[+] Fetching CIRCL CVE data...\n")

    cve_ids = get_valid_cve_ids(limit)
    print(f"[+] Valid CVE IDs found: {len(cve_ids)}")

    total = 0

    for cve_id in cve_ids:
        try:
            url = CIRCL_URL + cve_id
            r = requests.get(url, timeout=10)

            # CIRCL returns null when CVE is missing
            if r.status_code != 200 or r.text.strip() in ("null", ""):
                print(f"[NO_DATA] {cve_id} (CIRCL has no info)")
                continue

            data = r.json()

            normalized = normalize_circl(data)

            if not normalized or normalized["cve_id"] == "UNKNOWN-CVE":
                print(f"[SKIP] {cve_id} (Unsupported by CIRCL)")
                continue

            insert_or_update(normalized)

            total += 1
            time.sleep(0.5)

        except Exception as e:
            print(f"[ERROR] {cve_id}: {e}")

    print(f"\n[✓] Processed {total} CIRCL CVEs\n")

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
if __name__ == "__main__":
    fetch_circl_for_existing_cves(limit=200)
