"""
FINAL REPORT GENERATOR (Phase 4 Step 3)
- Generate per-host reports (JSON + PDF)
- Generate aggregate report (JSON + PDF)
- Works even if there are 0 vulnerability matches
- Fully compatible with reportlab or JSON-only mode
"""

import os
import json
from pymongo import MongoClient
from datetime import datetime, timezone
from collections import Counter

# -----------------------------
# OPTIONAL PDF SUPPORT
# -----------------------------
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    PDF_ENABLED = True
except:
    PDF_ENABLED = False


# -----------------------------
# CONFIG
# -----------------------------
MONGO_URI = "mongodb://admin:admin123@localhost:27017/?authSource=admin"
DB_NAME = "vulnerability_logs"
COLLECTION = "vuln_matches"

OUTPUT_DIR = "reports/output/"
HOST_DIR = os.path.join(OUTPUT_DIR, "hosts")
AGG_DIR = os.path.join(OUTPUT_DIR, "aggregate")

os.makedirs(HOST_DIR, exist_ok=True)
os.makedirs(AGG_DIR, exist_ok=True)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
matches = db[COLLECTION]


# -----------------------------
# HELPERS
# -----------------------------
def iso_now():
    return datetime.now(timezone.utc).isoformat()


def get_hosts():
    hosts = matches.distinct("host")
    if not hosts:
<<<<<<< HEAD
        return []     # No fallback, only real hosts
=======
        return ["server1"]     # fallback for empty DB
>>>>>>> cd260ba9258ba3c2c7ffb1588424565f3f1c9eae
    return hosts


def get_records_for(host):
    return list(matches.find({"host": host}))


# -----------------------------
# BUILD REPORT DICT
# -----------------------------
def build_report(host, records):

    sev_dist = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Unknown": 0}
    vulnerabilities = []

    for r in records:
        sev = r.get("severity", "Unknown")
        if sev not in sev_dist:
            sev_dist["Unknown"] += 1
        else:
            sev_dist[sev] += 1

        vulnerabilities.append({
            "cve_id": r.get("cve_id"),
            "software": r.get("software"),
            "version": r.get("version") or r.get("kernel_version") or "N/A",
            "severity": sev,
            "cvss_score": r.get("cvss") or r.get("cvss_score"),
            "summary": r.get("summary") or r.get("description") or "N/A",
        })

    # Recommendations
    rec = []
    if sev_dist["Critical"] > 0:
        rec.append("Patch all critical vulnerabilities immediately.")
    if sev_dist["High"] > 0:
        rec.append("Apply high severity patches for internet-facing systems.")
    if sev_dist["Medium"] > 0:
        rec.append("Schedule medium fixes and review hardening guides.")
    if sev_dist["Low"] > 0:
        rec.append("Address low severity issues during maintenance windows.")
    if sum(sev_dist.values()) == 0:
        rec.append("No vulnerabilities detected for this host.")

    return {
        "host": host,
        "generated_at": iso_now(),
        "total_vulnerabilities": len(vulnerabilities),
        "severity_distribution": sev_dist,
        "vulnerabilities": vulnerabilities,
        "recommendations": rec
    }


# -----------------------------
# EXPORT JSON
# -----------------------------
def export_json(report, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    return path


# -----------------------------
# EXPORT PDF (supports host + aggregate)
# -----------------------------
def export_pdf(report, path):
    if not PDF_ENABLED:
        return None

    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - inch

    # Title
    c.setFont("Helvetica-Bold", 16)
    title = f"Report: {report.get('host', 'All Hosts (Aggregate)')}"
    c.drawString(inch, y, title)
    y -= 30

    # Timestamp
    c.setFont("Helvetica", 10)
    c.drawString(inch, y, f"Generated: {report['generated_at']}")
    y -= 20

    # Severity distribution
    if "severity_distribution" in report:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y, "Severity Distribution:")
        y -= 20

        c.setFont("Helvetica", 10)
        for k, v in report["severity_distribution"].items():
            c.drawString(inch + 15, y, f"{k}: {v}")
            y -= 14

    # Recommendations
    if "recommendations" in report:
        y -= 14
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y, "Recommendations:")
        y -= 20

        c.setFont("Helvetica", 10)
        for r in report["recommendations"]:
            c.drawString(inch + 15, y, f"- {r}")
            y -= 14

    # Vulnerabilities list (only for host reports)
    if "vulnerabilities" in report:
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y, f"Vulnerabilities ({report['total_vulnerabilities']}):")
        y -= 20

        c.setFont("Helvetica", 9)
        for v in report["vulnerabilities"]:
            if y < inch:
                c.showPage()
                y = height - inch
                c.setFont("Helvetica", 9)

            line = f"{v['cve_id']} | {v['software']} | {v['version']} | {v['severity']}"
            c.drawString(inch, y, line)
            y -= 12

    c.save()
    return path


# -----------------------------
# EXPORT HOST REPORT
# -----------------------------
def generate_host_report(host):
    recs = get_records_for(host)
    report = build_report(host, recs)

<<<<<<< HEAD
    # Format: report_DD_MM_YYYY_HH-MM-SS
    ts_str = datetime.now().strftime("%d_%m_%Y_%H-%M-%S")
    
    json_path = os.path.join(HOST_DIR, f"report_{host}_{ts_str}.json")
    pdf_path = os.path.join(HOST_DIR, f"report_{host}_{ts_str}.pdf")
=======
    json_path = os.path.join(HOST_DIR, f"report_{host}.json")
    pdf_path = os.path.join(HOST_DIR, f"report_{host}.pdf")
>>>>>>> cd260ba9258ba3c2c7ffb1588424565f3f1c9eae

    export_json(report, json_path)
    export_pdf(report, pdf_path)

    return {"host": host, "report": report}


# -----------------------------
# AGGREGATE REPORT
# -----------------------------
def generate_aggregate(reports):
    sev_total = Counter()
    total_vulns = 0

    for r in reports:
        total_vulns += r["report"]["total_vulnerabilities"]
        for k, v in r["report"]["severity_distribution"].items():
            sev_total[k] += v

    agg = {
        "generated_at": iso_now(),
        "total_hosts": len(reports),
        "total_vulnerabilities": total_vulns,
        "severity_distribution": dict(sev_total),
        "recommendations": (
            ["Review overall patching strategy."]
            if total_vulns > 0
            else ["All hosts clean — no vulnerabilities detected."]
        )
    }

<<<<<<< HEAD
    # Format: aggregate_report_DD_MM_YYYY_HH-MM-SS
    ts_str = datetime.now().strftime("%d_%m_%Y_%H-%M-%S")

    json_path = os.path.join(AGG_DIR, f"aggregate_report_{ts_str}.json")
    pdf_path = os.path.join(AGG_DIR, f"aggregate_report_{ts_str}.pdf")
=======
    json_path = os.path.join(AGG_DIR, "aggregate_report.json")
    pdf_path = os.path.join(AGG_DIR, "aggregate_report.pdf")
>>>>>>> cd260ba9258ba3c2c7ffb1588424565f3f1c9eae

    export_json(agg, json_path)
    export_pdf(agg, pdf_path)

    return agg


# -----------------------------
# MAIN RUNNER
# -----------------------------
<<<<<<< HEAD
def main(payload=None):
=======
def run_reports():
>>>>>>> cd260ba9258ba3c2c7ffb1588424565f3f1c9eae
    print("\n[+] Generating reports for all hosts...")

    hosts = get_hosts()
    all_reports = []

    for h in hosts:
        print(f" - Generating report for {h}")
        r = generate_host_report(h)
        all_reports.append(r)

    agg = generate_aggregate(all_reports)

    print("\n[✓] Report Generation Completed.")
    print(f"Hosts processed: {len(all_reports)}")
    print(f"Total vulnerabilities: {agg['total_vulnerabilities']}")
    print("[✓] Reports saved in reports/output/")

    if not PDF_ENABLED:
        print("[i] reportlab not installed — PDF generation skipped.")

    return agg


if __name__ == "__main__":
<<<<<<< HEAD
    main()
=======
    run_reports()
>>>>>>> cd260ba9258ba3c2c7ffb1588424565f3f1c9eae
