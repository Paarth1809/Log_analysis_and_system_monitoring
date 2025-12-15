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
COLLECTION = "alerts"

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
        return []     # No fallback, only real hosts
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
        # Get severity and normalize it (handle case-insensitive matching)
        raw_sev = r.get("severity", "Unknown")
        
        # Normalize severity: convert to title case for matching
        if isinstance(raw_sev, str):
            sev = raw_sev.strip().capitalize()
        else:
            sev = "Unknown"
        
        # Count in distribution
        if sev in sev_dist:
            sev_dist[sev] += 1
        else:
            sev_dist["Unknown"] += 1
            sev = "Unknown"

        # Alerts schema handling:
        details = r.get("details", {})
        
        # ID is typically rule_name (e.g. CVE-X or 'Brute Force')
        # Fallback to cve_id inside details if present
        item_id = r.get("rule_name") or details.get("cve_id") or r.get("cve_id") or "Unknown-ID"
        
        software = details.get("software") or r.get("software") or r.get("rule_type") or "N/A"
        version = details.get("version") or r.get("version") or "N/A"
        cvss = details.get("cvss") or details.get("cvss_score") or r.get("cvss") or "N/A"
        summary = r.get("description") or details.get("description") or "N/A"

        vulnerabilities.append({
            "cve_id": item_id,
            "software": software,
            "version": version,
            "severity": sev,
            "cvss_score": cvss,
            "summary": summary,
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
# QUICK STATS HELPER
# -----------------------------
def get_quick_stats():
    """
    Fetch counts for dashboard-like Quick Stats:
    - Total Hosts Monitored (normalized_logs.distinct("host"))
    - Processed Logs (normalized_logs.count_documents({}))
    - CVE Definitions (cve_database.count_documents({}))
    - Active Threats (vuln_matches.count_documents({}))
    - Critical Alerts (alerts.count_documents({"severity": "Critical"}))
    """
    col_logs = db["normalized_logs"]
    col_cves = db["cve_database"]
    col_matches = db["vuln_matches"]
    col_alerts = db["alerts"]

    stats = {
        "total_hosts": len(col_logs.distinct("host")),
        "processed_logs": col_logs.count_documents({}),
        "cve_definitions": col_cves.count_documents({}),
        "active_threats": col_matches.count_documents({}),
        "critical_alerts": col_alerts.count_documents({"severity": {"$regex": "^Critical$", "$options": "i"}})
    }
    return stats

# -----------------------------
# EXPORT PDF (supports host + aggregate)
# -----------------------------
def export_pdf(report, path):
    if not PDF_ENABLED:
        return None

    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    # Standard margins
    margin = inch
    content_width = width - 2*margin
    y = height - margin

    # --- HEADER ---
    c.setFont("Helvetica-Bold", 18)
    title = f"Security Vulnerability Report"
    c.drawString(margin, y, title)
    y -= 25
    
    c.setFont("Helvetica", 12)
    subtitle = f"Host: {report.get('host', 'All Hosts (Aggregate)')}"
    c.drawString(margin, y, subtitle)
    y -= 18

    # Timestamp
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.4, 0.4, 0.4) # Grey
    c.drawString(margin, y, f"Generated: {report['generated_at']}")
    c.setFillColorRGB(0, 0, 0) # Black
    y -= 40 # Space before next section

    # --- QUICK STATS (Aggregate Only) ---
    # Only show full stats if available in report (aggregate)
    if "quick_stats" in report:
        qs = report["quick_stats"]
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y, "Quick Stats")
        y -= 20
        
        # Draw a box for stats
        box_height = 80
        c.setStrokeColorRGB(0.2, 0.2, 0.2)
        c.rect(margin, y - box_height, content_width, box_height, stroke=1, fill=0)
        
        # Stats Layout (2 rows, 3 cols)
        # Row 1
        row1_y = y - 30
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin + 20, row1_y, "Total Hosts Monitored")
        c.drawString(margin + 200, row1_y, "Processed Logs")
        c.drawString(margin + 380, row1_y, "CVE Definitions")
        
        c.setFont("Helvetica", 12)
        c.setFillColorRGB(0, 0.4, 0.8) # Blueish
        c.drawString(margin + 20, row1_y - 15, f"{qs['total_hosts']}")
        c.setFillColorRGB(0.6, 0, 0.6) # Purpleish
        c.drawString(margin + 200, row1_y - 15, f"{qs['processed_logs']:,}")
        c.setFillColorRGB(1, 0.5, 0)   # Orange
        c.drawString(margin + 380, row1_y - 15, f"{qs['cve_definitions']}")
        
        # Row 2
        row2_y = y - 65
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin + 20, row2_y, "Active Threats")
        c.drawString(margin + 200, row2_y, "Critical Alerts")
        
        c.setFont("Helvetica", 12)
        c.setFillColorRGB(0.8, 0, 0) # Red
        c.drawString(margin + 20, row2_y - 15, f"{qs['active_threats']:,}")
        c.drawString(margin + 200, row2_y - 15, f"{qs['critical_alerts']:,}")
        
        c.setFillColorRGB(0, 0, 0)
        y -= (box_height + 30)

    # --- EXECUTIVE SUMMARY ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Executive Summary")
    y -= 20
    
    c.setFont("Helvetica", 10)
    total_vulns = report.get('total_vulnerabilities', 0)
    c.drawString(margin + 15, y, f"Total Alerts Generated: {total_vulns}")
    y -= 30

    # --- SEVERITY BREAKDOWN (BARS) ---
    if "severity_distribution" in report:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Severity Breakdown")
        y -= 25

        sev_dist = report["severity_distribution"]
        severity_order = ["Critical", "High", "Medium", "Low"]
        
        # Max value for scaling bars
        max_val = max(sev_dist.values()) if sev_dist else 1
        if max_val == 0: max_val = 1
        
        bar_x = margin + 80
        bar_max_width = 300
        
        c.setFont("Helvetica", 10)
        
        for sev in severity_order:
            count = sev_dist.get(sev, 0)
            
            # Label
            c.setFillColorRGB(0, 0, 0)
            c.drawString(margin + 15, y, sev.upper())
            
            # Bar
            bar_width = (count / max_val) * bar_max_width
            
            # Color coding
            if sev == "Critical": c.setFillColorRGB(0.8, 0.2, 0.2)
            elif sev == "High": c.setFillColorRGB(1.0, 0.6, 0.2)
            elif sev == "Medium": c.setFillColorRGB(1.0, 0.8, 0.2)
            else: c.setFillColorRGB(0.2, 0.6, 1.0)
                
            if bar_width > 0:
                c.rect(bar_x, y - 2, bar_width, 10, fill=1, stroke=0)
            
            # Value Label
            c.setFillColorRGB(0, 0, 0)
            c.drawString(bar_x + bar_width + 10, y, str(count))
            
            y -= 20
        
        # Add Unknown if any
        unknown = sev_dist.get("Unknown", 0)
        if unknown > 0:
            c.drawString(margin + 15, y, "UNKNOWN")
            c.setFillColorRGB(0.5, 0.5, 0.5)
            bar_width = (unknown / max_val) * bar_max_width
            c.rect(bar_x, y-2, bar_width, 10, fill=1, stroke=0)
            c.setFillColorRGB(0, 0, 0)
            c.drawString(bar_x + bar_width + 10, y, str(unknown))
            y -= 20
            
        y -= 20

    # --- RECOMMENDATIONS ---
    if "recommendations" in report:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Recommendations:")
        y -= 18

        c.setFont("Helvetica", 10)
        for r in report["recommendations"]:
            # Word wrap for long recommendations
            if len(r) > 80:
                words = r.split()
                line = ""
                for word in words:
                    if len(line + word) < 80:
                        line += word + " "
                    else:
                        c.drawString(margin + 15, y, f"• {line.strip()}")
                        y -= 14
                        line = word + " "
                if line:
                    c.drawString(margin + 15, y, f"• {line.strip()}")
                    y -= 14
            else:
                c.drawString(margin + 15, y, f"• {r}")
                y -= 14
        y -= 20

    # --- VULNERABILITY LIST ---
    if "vulnerabilities" in report and len(report["vulnerabilities"]) > 0:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, f"Detailed Alert/Vulnerability List ({report['total_vulnerabilities']} items):")
        y -= 20

        c.setFont("Helvetica", 8)
        for i, v in enumerate(report["vulnerabilities"], 1):
            # Check page break
            if y < margin + 40:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", 8)

            # Header line
            c.setFont("Helvetica-Bold", 9)
            header = f"{i}. {v['cve_id']} - {v['severity']}"
            if v.get('cvss_score') and v.get('cvss_score') != 'N/A':
                header += f" (CVSS: {v['cvss_score']})"
            c.drawString(margin, y, header)
            y -= 12

            # Details
            c.setFont("Helvetica", 8)
            c.drawString(margin + 15, y, f"Software: {v['software']} {v['version']}")
            y -= 10
            
            # Summary
            summary = v.get('summary', 'N/A')
            if len(summary) > 95:
                # Basic truncate
                summary = summary[:95] + "..."
            c.drawString(margin + 15, y, f"Description: {summary}")
            y -= 15

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(margin, 0.5 * inch, f"Generated by Cyart Vulnerability Detection System")
    c.drawRightString(width - margin, 0.5 * inch, f"Page {c.getPageNumber()}")

    c.save()
    return path



# -----------------------------
# EXPORT HOST REPORT
# -----------------------------
def generate_host_report(host):
    recs = get_records_for(host)
    report = build_report(host, recs)

    # Format: report_DD_MM_YYYY_HH-MM-SS
    ts_str = datetime.now().strftime("%d_%m_%Y_%H-%M-%S")
    
    json_path = os.path.join(HOST_DIR, f"report_{host}_{ts_str}.json")
    pdf_path = os.path.join(HOST_DIR, f"report_{host}_{ts_str}.pdf")

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

    # Get Quick Stats (System-wide)
    quick_stats = get_quick_stats()
    
    agg = {
        "generated_at": iso_now(),
        "total_hosts": len(reports),
        "total_vulnerabilities": total_vulns,
        "severity_distribution": dict(sev_total),
        "quick_stats": quick_stats, # Added for PDF
        "recommendations": (
            ["Review overall patching strategy."]
            if total_vulns > 0
            else ["All hosts clean — no vulnerabilities detected."]
        )
    }

    # Format: aggregate_report_DD_MM_YYYY_HH-MM-SS
    ts_str = datetime.now().strftime("%d_%m_%Y_%H-%M-%S")

    json_path = os.path.join(AGG_DIR, f"aggregate_report_{ts_str}.json")
    pdf_path = os.path.join(AGG_DIR, f"aggregate_report_{ts_str}.pdf")

    export_json(agg, json_path)
    export_pdf(agg, pdf_path)

    return agg


# -----------------------------
# MAIN RUNNER
# -----------------------------
def main(payload=None):
    print("\n[+] Generating reports for all hosts...")
    print(f"[+] Database: {DB_NAME}")
    print(f"[+] Collection: {COLLECTION}")
    
    # Check total matches first
    total_matches = matches.count_documents({})
    print(f"[+] Total alerts in database: {total_matches}")
    
    if total_matches == 0:
        print("\n[!] WARNING: No alerts found in database!")
        print("[!] Please run the alert engine first.")
        print("[!] Command: python matching_engine/matcher.py")
        return {"status": "no_data", "total_vulnerabilities": 0}

    hosts = get_hosts()
    print(f"[+] Found {len(hosts)} unique hosts")
    
    if len(hosts) == 0:
        print("\n[!] WARNING: No hosts found in vulnerability matches!")
        print("[!] This might indicate a data structure issue.")
        # Try to generate a single aggregate report anyway
        print("[!] Generating aggregate report for all matches...")
        all_records = list(matches.find())
        agg_report = build_report("All Hosts (Aggregate)", all_records)
        
        # Save aggregate report
        ts_str = datetime.now().strftime("%d_%m_%Y_%H-%M-%S")
        json_path = os.path.join(AGG_DIR, f"aggregate_report_{ts_str}.json")
        pdf_path = os.path.join(AGG_DIR, f"aggregate_report_{ts_str}.pdf")
        
        export_json(agg_report, json_path)
        export_pdf(agg_report, pdf_path)
        
        print(f"\n[✓] Aggregate report generated")
        print(f"Total vulnerabilities: {agg_report['total_vulnerabilities']}")
        print(f"Severity distribution: {agg_report['severity_distribution']}")
        print(f"[✓] Reports saved in reports/output/aggregate/")
        
        return agg_report
    
    all_reports = []

    for h in hosts:
        print(f" - Generating report for {h}")
        r = generate_host_report(h)
        all_reports.append(r)
        print(f"   → {r['report']['total_vulnerabilities']} vulnerabilities found")

    agg = generate_aggregate(all_reports)

    print("\n[✓] Report Generation Completed.")
    print(f"Hosts processed: {len(all_reports)}")
    print(f"Total vulnerabilities: {agg['total_vulnerabilities']}")
    print(f"Severity distribution: {agg['severity_distribution']}")
    print("[✓] Reports saved in reports/output/")

    if not PDF_ENABLED:
        print("[i] reportlab not installed — PDF generation skipped.")

    return agg


if __name__ == "__main__":
    main()
