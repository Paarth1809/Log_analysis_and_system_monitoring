# backend/main.py
from fastapi import FastAPI
from backend.routes import run, scripts
from fastapi.middleware.cors import CORSMiddleware
from .config import API_HOST, API_PORT
from .routes import logs, cves, alerts, stats
from backend.routes import jobs
from backend import scheduler as _scheduler

app = FastAPI(title="Vuln Detection API", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(logs.router)
app.include_router(cves.router)
app.include_router(alerts.router)
app.include_router(stats.router)
app.include_router(run.router)
app.include_router(jobs.router)
app.include_router(scripts.router)
from backend.routes import reports, matches
app.include_router(reports.router)
app.include_router(matches.router)

@app.on_event("startup")
def _startup():
    # start the background scheduler
    try:
        _scheduler.start()
    except Exception:
        pass

    # Run diagnostics on startup in a separate thread
    # DISABLED to prevent data wiping/re-ingestion loop on every reload
    import threading
    import time
    from parser_engine.insert_to_mongo import main as insert_logs
    from matching_engine.matcher import main as run_matching
    from alerts.alert_engine import main as send_alerts
    from reports.report_generator import main as generate_reports

    def run_diagnostics():
        # Delay slightly to let server come up
        time.sleep(2)
        print("\n[STARTUP] Running full diagnostic chain...")
        try:
            # 1. Parse/Insert Logs
            print("[STARTUP] Step 1: Ingesting Logs (Resetting DB)...")
            insert_logs(payload={"reset": True})
            
            # 2. Run Matching
            print("[STARTUP] Step 2: Running Matching Engine...")
            run_matching(payload={"reset": True})
            
            # 3. Send Alerts
            print("[STARTUP] Step 3: Generating Alerts...")
            send_alerts(payload={"reset": True})
            
            # 4. Generate Reports
            print("[STARTUP] Step 4: Generating Reports...")
            generate_reports()
            
            print("[STARTUP] Diagnostic chain completed successfully.\n")
        except Exception as e:
            print(f"[STARTUP] Diagnostic chain failed: {e}\n")

    threading.Thread(target=run_diagnostics, daemon=True).start()

@app.on_event("shutdown")
def _shutdown():
    try:
        _scheduler.shutdown()
    except Exception:
        pass

@app.get("/health")
def health():
    return {"status": "ok"}
