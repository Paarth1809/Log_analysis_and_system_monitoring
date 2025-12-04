from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend import scheduler
from backend.services import runner_service
from typing import Optional

router = APIRouter(prefix="/jobs", tags=["jobs"])

class SchedulePayload(BaseModel):
    name: str
    minutes: int
    enabled: Optional[bool] = True

@router.post("/schedule")
def schedule(payload: SchedulePayload):
    try:
        if not payload.enabled:
            scheduler.unschedule_job(payload.name)
            return {"status": "unscheduled", "name": payload.name}
        info = scheduler.schedule_job(payload.name, payload.minutes)
        return {"status": "scheduled", "name": payload.name, "info": info}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/unschedule/{name}")
def unschedule(name: str):
    scheduler.unschedule_job(name)
    return {"status": "unscheduled", "name": name}

@router.get("/list")
def list_schedules():
    return scheduler.list_schedules()

@router.post("/run/{name}")
def run_now(name: str):
    try:
        tid = scheduler.run_now(name)
        return {"task_id": tid, "status": "started"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/last-run/{name}")
def last_run(name: str):
    task = runner_service.get_last_task_by_name(name)
    if not task:
        return {"name": name, "last_run": None}
    return {"name": name, "last_run": task}
