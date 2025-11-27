from pymongo import MongoClient, InsertOne
import datetime
import json
import traceback

# ------------------------------------------------------------
# DB CONNECTION
# ------------------------------------------------------------
client = MongoClient("mongodb://admin:admin123@localhost:27017/?authSource=admin")
db = client["vulnerability_logs"]
cve_collection = db["cve_database"]

# ------------------------------------------------------------
# VALIDATION HELPERS
# ------------------------------------------------------------
REQUIRED_FIELDS = [
    "cve_id",
    "vendor",
    "product",
    "affected_versions",
    "cvss_score",
    "severity",
    "description",
    "published_date",
    "last_modified",
]


def validate_cve(cve):
    """Ensure CVE dict has the required fields"""
    missing = [f for f in REQUIRED_FIELDS if f not in cve]
    if missing:
        raise ValueError(f"Missing fields: {missing}")

    return True


# ------------------------------------------------------------
# BATCH INSERT FUNCTION
# ------------------------------------------------------------
def batch_insert_cves(cve_list):
    """
    Insert many CVEs (NVD or CIRCL) in batch.
    Duplicate skip is automatic due to unique _id field.
    """

    if not isinstance(cve_list, list):
        raise ValueError("Input must be a list of CVE dictionaries")

    operations = []
    skipped = 0
    inserted = 0
    invalid = 0

    for cve in cve_list:
        try:
            validate_cve(cve)

            # Use CVE ID as MongoDB ID (prevents duplicates)
            cve["_id"] = cve["cve_id"]

            operations.append(InsertOne(cve))

        except Exception as e:
            invalid += 1
            with open("error_log_cve.txt", "a") as f:
                f.write(
                    f"{datetime.datetime.now()} | {str(e)} | CVE: {json.dumps(cve, indent=2)}\n"
                )

    # Execute batch insert
    try:
        if operations:
            result = cve_collection.bulk_write(operations, ordered=False)
            inserted = result.inserted_count
    except Exception as e:
        # “duplicate key” errors will be skipped
        if "duplicate key" in str(e):
            skipped += 1
        else:
            print("[ERROR] Bulk insert failed:")
            print(e)
            print(traceback.format_exc())

    print("\n====== CVE Import Summary ======")
    print(f"Inserted : {inserted}")
    print(f"Skipped  : {skipped}")
    print(f"Invalid  : {invalid}")
    print("================================\n")


# ------------------------------------------------------------
# TEST MODE – Insert a sample list when script is run directly
# ------------------------------------------------------------
if __name__ == "__main__":
    sample_cves = [
        {
            "cve_id": "CVE-2023-55555",
            "vendor": "TestVendor",
            "product": "TestProduct",
            "affected_versions": ["< 1.0"],
            "cvss_score": 7.5,
            "severity": "High",
            "description": "Test vulnerability.",
            "published_date": "2023-10-10",
            "last_modified": "2023-11-10",
            "references": [],
            "source": "test",
        }
    ]

    batch_insert_cves(sample_cves)
