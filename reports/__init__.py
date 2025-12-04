def run_reports(payload=None):
    from reports.report_generator import main as reports_main
    return reports_main(payload)
