from apscheduler.schedulers.background import BackgroundScheduler
from typing import Dict, Any
from backend.services.runner_service import create_and_start
import logging

logger = logging.getLogger("scheduler")

# Map job name -> APScheduler job id
_SCHEDULES: Dict[str, Dict[str, Any]] = {}

scheduler = BackgroundScheduler()

# Try to import run functions from engines; they might be optional
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

_AVAILABLE = {
    "parser": run_parser,
    "matching": run_matching,
    "alerts": run_alerts,
    "reports": run_reports,
}


def start():
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def shutdown():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def schedule_job(name: str, minutes: int):
    """Schedule a job to run every `minutes` minutes. Replaces existing schedule for the name."""
    fn = _AVAILABLE.get(name)
    if not fn:
        raise ValueError(f"Job {name} not available")

    # remove existing
    unschedule_job(name)

    job = scheduler.add_job(lambda: create_and_start(name, fn), 'interval', minutes=max(1, int(minutes)))
    _SCHEDULES[name] = {"job_id": job.id, "minutes": int(minutes)}
    logger.info(f"Scheduled {name} every {minutes} minutes")
    return _SCHEDULES[name]


def unschedule_job(name: str):
    info = _SCHEDULES.get(name)
    if info:
        try:
            scheduler.remove_job(info["job_id"])
        except Exception:
            pass
        del _SCHEDULES[name]
        logger.info(f"Unscheduled {name}")
    return True


def list_schedules() -> Dict[str, Any]:
    return _SCHEDULES.copy()


def run_now(name: str):
    fn = _AVAILABLE.get(name)
    if not fn:
        raise ValueError(f"Job {name} not available")
    tid = create_and_start(name, fn)
    return tid
