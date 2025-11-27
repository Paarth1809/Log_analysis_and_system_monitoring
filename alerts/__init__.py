def run_alerts(payload=None):
    from alerts.alert_engine import main as alerts_main
    return alerts_main(payload)
