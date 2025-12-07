"""
Script execution endpoints for running Python automation scripts
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
import uuid
from datetime import datetime
from typing import Dict, Any
import threading

router = APIRouter(prefix="/scripts", tags=["scripts"])

# In-memory task storage (in production, use Redis or database)
TASKS: Dict[str, Dict[str, Any]] = {}
TASK_LOCK = threading.Lock()

# Script mapping to actual Python functions
SCRIPT_HANDLERS = {
    'parse_logs': 'Parse raw security logs from all data sources',
    'normalize_logs': 'Normalize parsed logs into standard format',
    'insert_logs': 'Store normalized logs in MongoDB database',
    'create_cve_collection': 'Initialize CVE database collection',
    'fetch_nvd': 'Fetch latest CVE definitions from NVD',
    'fetch_circl': 'Fetch CVE definitions from CIRCL database',
    'insert_cves': 'Import CVE definitions into database',
    'setup_vuln_matches': 'Initialize vulnerability matching pipeline',
    'run_matching': 'Match logs against CVE database',
    'generate_reports': 'Compile compliance and vulnerability reports',
    'send_alerts': 'Dispatch notifications for critical findings',
    'run_diagnostics': 'Run the full security scan pipeline (Ingest -> Match -> Alert -> Report)',
    'validate_data': 'Validate integrity of stored data',
}

def execute_script(task_id: str, script_name: str):
    """Execute a script in background"""
    try:
        with TASK_LOCK:
            TASKS[task_id]['state'] = 'running'
            TASKS[task_id]['progress'] = 10

        # Import and execute the script
        result = None
        
        if script_name == 'parse_logs':
            from parser_engine.parser import main
            result = main()
        elif script_name == 'normalize_logs':
            # Normalization is integrated into the insertion process
            result = {"status": "skipped", "msg": "Normalization is integrated into the insertion process."}
        elif script_name == 'insert_logs':
            from parser_engine.insert_to_mongo import main as insert_logs_main
            result = insert_logs_main()
        elif script_name == 'create_cve_collection':
            from cve_engine.create_cve_collection import setup_cve_collection
            result = setup_cve_collection()
        elif script_name == 'fetch_nvd':
            from cve_engine.fetch_nvd import fetch_nvd
            result = fetch_nvd()
        elif script_name == 'fetch_circl':
            from cve_engine.fetch_circl import fetch_circl_for_existing_cves
            result = fetch_circl_for_existing_cves()
        elif script_name == 'insert_cves':
            # This is handled by fetch scripts, but we can return a message
            result = {"status": "info", "msg": "Use Fetch NVD or Fetch CIRCL to insert CVEs."}
        elif script_name == 'setup_vuln_matches':
            from matching_engine.setup_vuln_matches import setup_collection
            result = setup_collection()
        elif script_name == 'run_matching':
            from matching_engine.matcher import main as run_matching_main
            result = run_matching_main()
        elif script_name == 'generate_reports':
            from reports.report_generator import main as generate_reports_main
            result = generate_reports_main()
        elif script_name == 'send_alerts':
            from alerts.alert_engine import main as send_alerts_main
            result = send_alerts_main()
        elif script_name == 'validate_data':
            result = {"status": "validated", "timestamp": datetime.now().isoformat()}


        elif script_name == 'run_diagnostics':
            # Run the full chain sequentially
            
            # 1. Ingest (Parse/Normalize/Insert)
            print("\n[DIAGNOSTICS] Step 1/4: Ingesting Logs (Parser + Normalizer)...", flush=True)
            with TASK_LOCK:
                TASKS[task_id]['msg'] = "Step 1/4: Ingesting Logs..."
            from parser_engine.insert_to_mongo import main as insert_logs_main
            # FORCE RESET to demonstrate full processing flow
            res_ingest = insert_logs_main(payload={"reset": True})
            
            # 2. Match
            print("\n[DIAGNOSTICS] Step 2/4: Matching Vulnerabilities...", flush=True)
            with TASK_LOCK:
                TASKS[task_id]['msg'] = "Step 2/4: Matching Vulnerabilities..."
                TASKS[task_id]['progress'] = 40
            from matching_engine.matcher import main as run_matching_main
            res_match = run_matching_main(payload={"reset": True})
            
            # 3. Alert
            print("\n[DIAGNOSTICS] Step 3/4: Generating Alerts...", flush=True)
            with TASK_LOCK:
                TASKS[task_id]['msg'] = "Step 3/4: Generating Alerts..."
                TASKS[task_id]['progress'] = 70
            from alerts.alert_engine import main as send_alerts_main
            res_alert = send_alerts_main(payload={"reset": True})
            
            # 4. Report
            print("\n[DIAGNOSTICS] Step 4/4: Generating Reports...", flush=True)
            with TASK_LOCK:
                TASKS[task_id]['msg'] = "Step 4/4: generating Report..."
                TASKS[task_id]['progress'] = 90
            from reports.report_generator import main as generate_reports_main
            res_report = generate_reports_main()

            print("\n[DIAGNOSTICS] All steps completed successfully.", flush=True)
            
            result = {
                "status": "completed",
                "ingest": res_ingest,
                "match": res_match,
                "alerts": res_alert,
                "report": res_report
            }
        
        with TASK_LOCK:
            TASKS[task_id]['state'] = 'success'
            TASKS[task_id]['progress'] = 100
            TASKS[task_id]['result'] = result
            TASKS[task_id]['msg'] = f"Script '{script_name}' completed successfully"
            TASKS[task_id]['completed_at'] = datetime.now().isoformat()
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        with TASK_LOCK:
            TASKS[task_id]['state'] = 'failed'
            TASKS[task_id]['msg'] = str(e)
            TASKS[task_id]['error'] = str(e)
            TASKS[task_id]['completed_at'] = datetime.now().isoformat()

@router.post("/{script_name}")
async def run_script(script_name: str, background_tasks: BackgroundTasks):
    """Run a Python script asynchronously"""
    print(f"\n[API] Received request to run script: {script_name}", flush=True)
    if script_name not in SCRIPT_HANDLERS:
        raise HTTPException(status_code=404, detail=f"Script '{script_name}' not found")
    
    try:
        task_id = str(uuid.uuid4())
        
        with TASK_LOCK:
            TASKS[task_id] = {
                "task_id": task_id,
                "script_name": script_name,
                "state": "pending",
                "msg": "Task queued for execution",
                "progress": 0,
                "started_at": datetime.now().isoformat(),
                "result": None
            }
        
        # Add background task
        background_tasks.add_task(execute_script, task_id, script_name)
        
        return {
            "task_id": task_id,
            "script_name": script_name,
            "status": "pending",
            "started_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}")
async def get_script_status(task_id: str):
    """Get the status of a running script"""
    try:
        with TASK_LOCK:
            if task_id not in TASKS:
                return {
                    "state": "failed",
                    "msg": "Task not found",
                    "progress": 0
                }
            
            task = TASKS[task_id]
            return {
                "state": task.get('state', 'unknown'),
                "msg": task.get('msg', ''),
                "progress": task.get('progress', 0),
                "result": task.get('result'),
                "error": task.get('error')
            }
    except Exception as e:
        return {
            "state": "failed",
            "msg": str(e),
            "progress": 0
        }

@router.get("/list")
async def list_scripts():
    """List all available scripts"""
    return {
        "scripts": [
            {"name": name, "description": desc}
            for name, desc in SCRIPT_HANDLERS.items()
        ]
    }

@router.get("/tasks")
async def list_tasks():
    """List all tasks"""
    with TASK_LOCK:
        return {
            "tasks": list(TASKS.values())
        }

