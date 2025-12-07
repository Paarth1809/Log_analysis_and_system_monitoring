# backend/routes/run.py
from fastapi import APIRouter, HTTPException
from backend.services.runner_service import create_and_start, get_task, list_tasks
from typing import Dict

router = APIRouter(prefix="/run", tags=["run"])

# Import the functions you exposed in your modules
# These should be present after adding the small wrappers explained below
try:
    from parser_engine import run_parser
except Exception:
    run_parser = None
try:
    from matching_engine import run_matching
except Exception:
    run_matching = None
try:
    from alerts import run_alerts
except Exception:
    run_alerts = None
try:
    from reports import run_reports
except Exception:
    run_reports = None

@router.post("/parser")
def start_parser(payload: Dict = None):
    if not run_parser:
        raise HTTPException(500, "Parser function not available")
    tid = create_and_start("parser", run_parser, payload or {}, pass_task_id=True)
    return {"task_id": tid, "status": "started"}

@router.post("/matching")
def start_matching(payload: Dict = None):
    if not run_matching:
        raise HTTPException(500, "Matching function not available")
    tid = create_and_start("matching", run_matching, payload or {})
    return {"task_id": tid, "status": "started"}

@router.post("/alerts")
def start_alerts(payload: Dict = None):
    if not run_alerts:
        raise HTTPException(500, "Alerts function not available")
    tid = create_and_start("alerts", run_alerts, payload or {})
    return {"task_id": tid, "status": "started"}

@router.post("/reports")
def start_reports(payload: Dict = None):
    if not run_reports:
        raise HTTPException(500, "Reports function not available")
    tid = create_and_start("reports", run_reports, payload or {})
    return {"task_id": tid, "status": "started"}

@router.get("/status/{task_id}")
def task_status(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task

@router.get("/list")
def task_list():
    return list_tasks()
