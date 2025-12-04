from pymongo import MongoClient

# ------------------------------------------------------------
# CONNECT TO MONGODB
# ------------------------------------------------------------
client = MongoClient("mongodb://admin:admin123@localhost:27017/?authSource=admin")
db = client["vulnerability_logs"]
cve_collection = db["cve_database"]


# ------------------------------------------------------------
# CVE SCHEMA (TEAM STANDARD)
# ------------------------------------------------------------
CVE_SCHEMA_EXAMPLE = {
    "cve_id": "CVE-2023-34527",
    "vendor": "Microsoft",
    "product": "Print Spooler",
    "affected_versions": ["< 10.0.19044"],
    "cvss_score": 8.8,
    "severity": "High",
    "description": "Remote code execution vulnerability in Windows Print Spooler service.",
    "published_date": "2023-07-12",
    "last_modified": "2023-09-10",
    "cwe": "CWE-269",
    "references": [
        "https://nvd.nist.gov/vuln/detail/CVE-2023-34527"
    ]
}


# ------------------------------------------------------------
# CREATE COLLECTION + INSERT SAMPLE DATA
# ------------------------------------------------------------
def setup_cve_collection():
    print("\n[+] Creating CVE database collection...")

    # Create unique index on cve_id
    cve_collection.create_index("cve_id", unique=True)

    # Insert sample CVE (only if collection is empty)
    if cve_collection.count_documents({}) == 0:
        cve_collection.insert_one(CVE_SCHEMA_EXAMPLE)
        print("[✓] Inserted sample CVE entry.")
    else:
        print("[✓] Collection already has data. Skipping sample insert.")

    print("[✓] CVE collection setup complete.")


if __name__ == "__main__":
    setup_cve_collection()
