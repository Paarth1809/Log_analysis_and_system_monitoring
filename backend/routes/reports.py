from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from datetime import datetime

router = APIRouter(prefix="/reports", tags=["reports"])

REPORTS_DIR = "reports/output"

@router.get("/list")
def list_reports():
    """List all generated reports"""
    reports = []
    
    # Check hosts dir
    hosts_dir = os.path.join(REPORTS_DIR, "hosts")
    if os.path.exists(hosts_dir):
        for f in os.listdir(hosts_dir):
            path = os.path.join(hosts_dir, f)
            if os.path.isfile(path):
                stats = os.stat(path)
                reports.append({
                    "name": f,
                    "type": "host",
                    "format": f.split(".")[-1],
                    "size": stats.st_size,
                    "created_at": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                    "path": f"hosts/{f}"
                })

    # Check aggregate dir
    agg_dir = os.path.join(REPORTS_DIR, "aggregate")
    if os.path.exists(agg_dir):
        for f in os.listdir(agg_dir):
            path = os.path.join(agg_dir, f)
            if os.path.isfile(path):
                stats = os.stat(path)
                reports.append({
                    "name": f,
                    "type": "aggregate",
                    "format": f.split(".")[-1],
                    "size": stats.st_size,
                    "created_at": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                    "path": f"aggregate/{f}"
                })
                
    # Sort by date desc
    reports.sort(key=lambda x: x["created_at"], reverse=True)
    return reports

@router.get("/download/{category}/{filename}")
def download_report(category: str, filename: str):
    """Download a specific report"""
    if category not in ["hosts", "aggregate"]:
        raise HTTPException(400, "Invalid category")
        
    path = os.path.join(REPORTS_DIR, category, filename)
    if not os.path.exists(path):
        raise HTTPException(404, "Report not found")
        
    return FileResponse(path, filename=filename)
