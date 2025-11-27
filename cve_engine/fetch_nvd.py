import requests
import gzip
import json
from datetime import datetime
from pymongo import MongoClient

# ------------------------------------------------------------
# CONNECT TO MONGO
# ------------------------------------------------------------
client = MongoClient("mongodb://admin:admin123@localhost:27017/?authSource=admin")
db = client["vulnerability_logs"]
cve_collection = db["cve_database"]

# ------------------------------------------------------------
# NVD PUBLIC FEED (No API Key Required)
# Full database (last 20 years)
# ------------------------------------------------------------
NVD_FEED_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0/?resultsPerPage=2000"

# If feed size becomes huge, we will extend with pagination:
# https://services.nvd.nist.gov/rest/json/cves/2.0/?resultsPerPage=2000&startIndex=2000


# ------------------------------------------------------------
# EXTRACT REQUIRED FIELDS
# ------------------------------------------------------------
def extract_fields(cve_item):
    """
    Takes a single NVD CVE item and extracts ONLY fields we need.
    Returns a normalized Python dict.
    """

    cve_id = cve_item.get("id", "UNKNOWN-CVE")

    descriptions = cve_item.get("descriptions", [])
    description = descriptions[0].get("value", "") if descriptions else ""

    # Vendors, products, versions
    vendor = "Unknown"
    product = "Unknown"
    versions = []

    for vendor_item in cve_item.get("vendors", []):
        vendor = vendor_item.get("vendorName", "Unknown")
        for product_item in vendor_item.get("products", []):
            product = product_item.get("productName", "Unknown")
            for version_item in product_item.get("versions", []):
                versions.append(version_item.get("versionValue", "Unknown"))

    # CVSS Score & Severity
    metrics = cve_item.get("metrics", {})
    cvss = 0.0
    severity = "Unknown"

    if "cvssMetricV31" in metrics:
        cvss = metrics["cvssMetricV31"][0]["cvssData"]["baseScore"]
        severity = metrics["cvssMetricV31"][0]["cvssData"]["baseSeverity"]

    elif "cvssMetricV30" in metrics:
        cvss = metrics["cvssMetricV30"][0]["cvssData"]["baseScore"]
        severity = metrics["cvssMetricV30"][0]["cvssData"]["baseSeverity"]

    elif "cvssMetricV2" in metrics:
        cvss = metrics["cvssMetricV2"][0]["cvssData"]["baseScore"]
        severity = metrics["cvssMetricV2"][0]["baseSeverity"]

    # Dates
    published = cve_item.get("published", "2020-01-01")
    modified = cve_item.get("lastModified", "2020-01-01")

    # CWE
    cwe_list = cve_item.get("weaknesses", [])
    cwe = cwe_list[0]["description"][0]["value"] if cwe_list else "Unknown"

    return {
        "_id": cve_id,
        "cve_id": cve_id,
        "vendor": vendor,
        "product": product,
        "affected_versions": versions,
        "cvss_score": cvss,
        "severity": severity,
        "description": description,
        "published_date": published,
        "last_modified": modified,
        "cwe": cwe,
        "references": [],
    }


# ------------------------------------------------------------
# INSERT / UPDATE CVE
# ------------------------------------------------------------
def insert_or_update_cve(cve):
    existing = cve_collection.find_one({"_id": cve["_id"]})

    if existing:
        # Update if modified date is newer
        if cve["last_modified"] > existing["last_modified"]:
            cve_collection.update_one({"_id": cve["_id"]}, {"$set": cve})
            print(f"[UPDATED] {cve['_id']}")
        else:
            print(f"[SKIP] {cve['_id']} (Already up to date)")
    else:
        cve_collection.insert_one(cve)
        print(f"[NEW] {cve['_id']}")


# ------------------------------------------------------------
# DOWNLOAD + PARSE NVD FEED
# ------------------------------------------------------------
def fetch_nvd():
    print("\n[+] Fetching NVD CVE data (no API key required)...\n")

    page_index = 0
    total_processed = 0

    while True:
        url = f"{NVD_FEED_URL}&startIndex={page_index}"
        print(f"[+] Downloading: {url}")

        r = requests.get(url)

        if r.status_code != 200:
            print(f"[ERROR] Failed to download page {page_index}")
            break

        data = r.json()

        cve_items = data.get("vulnerabilities", [])
        print(f"[+] CVEs on this page: {len(cve_items)}")

        if len(cve_items) == 0:
            print("\n[✓] No more pages. Completed full NVD import.")
            break

        for item in cve_items:
            cve = extract_fields(item["cve"])
            insert_or_update_cve(cve)
            total_processed += 1

        page_index += 2000  # Next page

    print(f"\n[✓] Total CVEs processed: {total_processed}")


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
if __name__ == "__main__":
    fetch_nvd()
