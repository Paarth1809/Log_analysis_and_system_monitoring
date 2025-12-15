
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
