import requests
import time
from pymongo import MongoClient
from datetime import datetime

# Config
MONGO_URI = "mongodb://admin:admin123@localhost:27017/?authSource=admin"
DB_NAME = "vulnerability_logs"
CVE_COL = "cve_database"
API_KEY = "f57b5441-e323-4ba2-a757-049b36010c21"
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
cves_col = db[CVE_COL]

def fetch_and_store(keyword):
    print(f"[+] Fetching CVEs for keyword: '{keyword}'...")
    headers = {"apiKey": API_KEY}
    params = {
        "keywordSearch": keyword,
        "resultsPerPage": 20,
        "pubStartDate": "2023-01-01T00:00:00.000",
        "pubEndDate": "2023-04-01T00:00:00.000" # Short window to get some data
    }
    
    try:
        response = requests.get(NVD_API_URL, headers=headers, params=params, timeout=10)
        if response.status_code != 200:
            print(f"[!] Failed: {response.status_code}")
            return

        data = response.json()
        vulnerabilities = data.get("vulnerabilities", [])
        
        count = 0
        for item in vulnerabilities:
            cve = item.get("cve", {})
            cve_id = cve.get("id")
            
            # Metrics
            metrics = cve.get("metrics", {})
            cvss = 0.0
            severity = "UNKNOWN"
            
            if "cvssMetricV31" in metrics:
                m = metrics["cvssMetricV31"][0]["cvssData"]
                cvss = m.get("baseScore", 0.0)
                severity = m.get("baseSeverity", "UNKNOWN")
            elif "cvssMetricV2" in metrics:
                m = metrics["cvssMetricV2"][0]["cvssData"]
                cvss = m.get("baseScore", 0.0)
                severity = m.get("baseSeverity", "UNKNOWN")

            doc = {
                "cve_id": cve_id,
                "description": cve.get("descriptions", [{}])[0].get("value", "No description"),
                "cvss_score": cvss,
                "severity": severity,
                "source": "NVD_SEED",
                "last_updated": datetime.utcnow()
            }
            
            cves_col.update_one(
                {"cve_id": cve_id},
                {"$set": doc},
                upsert=True
            )
            count += 1
            
        print(f"[✓] Stored {count} CVEs for '{keyword}'")
        
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    # Fetch some common software to populate the DB
    keywords = ["nginx", "apache", "linux kernel"]
    for k in keywords:
        fetch_and_store(k)
        time.sleep(1) # Be nice to API
