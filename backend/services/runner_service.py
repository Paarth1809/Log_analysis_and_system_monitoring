# backend/services/runner_service.py
import threading
import uuid
import time
from typing import Dict, Any

# task states: queued, running, success, failed
_TASKS: Dict[str, Dict[str, Any]] = {}

def _init_task(name: str, payload: Dict[str, Any] | None = None) -> str:
    task_id = str(uuid.uuid4())[:8]
    _TASKS[task_id] = {
        "id": task_id,
        "name": name,
        "state": "queued",
        "progress": 0,
        "msg": "",
        "started_at": None,
        "finished_at": None,
        "result": None,
        "payload": payload or {}
    }
    return task_id

def get_task(task_id: str) -> Dict[str, Any] | None:
    return _TASKS.get(task_id)

def list_tasks() -> Dict[str, Dict[str, Any]]:
    return _TASKS

def _set(task_id: str, **kwargs):
    task = _TASKS.get(task_id)
    if not task:
        return
    task.update(kwargs)

def run_background(task_id: str, target, *args, **kwargs):
    def _wrapper():
        try:
            _set(task_id, state="running", started_at=time.time(), progress=1, msg="started")
            result = target(*args, **kwargs)
            _set(task_id, state="success", finished_at=time.time(), progress=100, msg="finished", result=result)
        except Exception as e:
            _set(task_id, state="failed", finished_at=time.time(), msg=str(e))
    t = threading.Thread(target=_wrapper, daemon=True)
    t.start()

# Convenience API used by routes
def create_and_start(name: str, func, *args, payload=None, **kwargs) -> str:
    tid = _init_task(name, payload or {})
    run_background(tid, func, *args, **kwargs)
    return tid
