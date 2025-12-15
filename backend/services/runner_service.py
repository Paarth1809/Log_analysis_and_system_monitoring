# backend/services/runner_service.py
import threading
import uuid
import time
from typing import Dict, Any, Optional

# task states: queued, running, success, failed
_TASKS: Dict[str, Dict[str, Any]] = {}

def _init_task(name: str, payload: Optional[Dict[str, Any]] = None) -> str:
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
        "logs": [],
        "payload": payload or {}
    }
    return task_id

def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    return _TASKS.get(task_id)

def list_tasks() -> Dict[str, Dict[str, Any]]:
    return _TASKS

def get_tasks_by_name(name: str) -> list:
    """Return all tasks matching `name`, sorted by started_at descending."""
    tasks = [t for t in _TASKS.values() if t.get("name") == name]
    tasks.sort(key=lambda x: x.get("started_at") or 0, reverse=True)
    return tasks

def get_last_task_by_name(name: str) -> Optional[Dict[str, Any]]:
    tasks = get_tasks_by_name(name)
    return tasks[0] if tasks else None

def _set(task_id: str, **kwargs):
    task = _TASKS.get(task_id)
    if not task:
        return
    task.update(kwargs)

def log_message(task_id: str, message: str):
    task = _TASKS.get(task_id)
    if not task:
        return
    if "logs" not in task:
        task["logs"] = []
    task["logs"].append({"time": time.time(), "message": message})
    # Also update msg for backward compatibility
    task["msg"] = message

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
def create_and_start(name: str, func, *args, payload=None, pass_task_id=False, **kwargs) -> str:
    tid = _init_task(name, payload or {})
    if pass_task_id:
        kwargs['task_id'] = tid
    run_background(tid, func, *args, **kwargs)
    return tid
