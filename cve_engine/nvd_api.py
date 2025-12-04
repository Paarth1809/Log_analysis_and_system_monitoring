import requests
import time
import logging

# NVD API Configuration
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
API_KEY = "f57b5441-e323-4ba2-a757-049b36010c21"

logger = logging.getLogger("nvd_api")

def query_nvd_cves(keyword, limit=50):
    """
    Search NVD for CVEs related to a specific keyword (e.g., "linux kernel 5.4").
    """
    headers = {
        "apiKey": API_KEY
    }
    params = {
        "keywordSearch": keyword,
        "resultsPerPage": limit
    }
    
    try:
        print(f"[API] Querying NVD for: {keyword}")
        response = requests.get(NVD_API_URL, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            vulnerabilities = data.get("vulnerabilities", [])
            return [parse_nvd_item(item) for item in vulnerabilities]
        else:
            print(f"[ERR] NVD API failed: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"[ERR] Exception querying NVD: {e}")
        return []

def parse_nvd_item(item):
    """
    Extract relevant fields from NVD response item.
    """
    cve = item.get("cve", {})
    cve_id = cve.get("id")
    
    # Description
    descriptions = cve.get("descriptions", [])
    desc = descriptions[0].get("value", "No description") if descriptions else "No description"
    
    # Metrics (CVSS)
    metrics = cve.get("metrics", {})
    cvss_score = 0.0
    severity = "UNKNOWN"
    
    # Try V3.1, then V3.0, then V2
    if "cvssMetricV31" in metrics:
        data = metrics["cvssMetricV31"][0]["cvssData"]
        cvss_score = data.get("baseScore", 0.0)
        severity = data.get("baseSeverity", "UNKNOWN")
    elif "cvssMetricV30" in metrics:
        data = metrics["cvssMetricV30"][0]["cvssData"]
        cvss_score = data.get("baseScore", 0.0)
        severity = data.get("baseSeverity", "UNKNOWN")
    elif "cvssMetricV2" in metrics:
        data = metrics["cvssMetricV2"][0]["cvssData"]
        cvss_score = data.get("baseScore", 0.0)
        severity = data.get("baseSeverity", "UNKNOWN")

    return {
        "cve_id": cve_id,
        "description": desc,
        "cvss_score": cvss_score,
        "severity": severity,
        "affected_versions": [] # NVD API structure for versions is complex, we might skip precise version matching for now or implement it if needed.
                                # For "keyword search", we rely on the search result being relevant.
    }
