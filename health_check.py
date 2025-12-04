#!/usr/bin/env python3
"""
System Health Check Script
Validates all components of the vulnerability detection system
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")

def print_check(name, passed, message=""):
    """Print a check result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {name}")
    if message:
        print(f"       {message}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    required = (3, 8)
    passed = version >= required
    print_check(
        f"Python Version (required 3.8+)",
        passed,
        f"Current: {version.major}.{version.minor}.{version.micro}"
    )
    return passed

def check_project_structure():
    """Check if all required directories exist"""
    base_path = Path(__file__).parent
    required_dirs = [
        'backend',
        'frontend',
        'cve_engine',
        'parser_engine',
        'matching_engine',
        'alerts',
        'reports',
        'datasets',
        'logs'
    ]
    
    print("\nProject Structure:")
    all_exist = True
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        exists = dir_path.exists()
        all_exist = all_exist and exists
        status = "📁" if exists else "❌"
        print(f"  {status} {dir_name}/")
    
    return all_exist

def check_backend_files():
    """Check if all backend files exist"""
    base_path = Path(__file__).parent / 'backend'
    required_files = [
        'main.py',
        'config.py',
        'db.py',
        'requirements.txt',
        'routes/scripts.py',
        'routes/logs.py',
        'routes/cves.py',
        'routes/alerts.py',
        'routes/stats.py',
        'services/stats_service.py',
    ]
    
    print("\nBackend Files:")
    all_exist = True
    for file_name in required_files:
        file_path = base_path / file_name
        exists = file_path.exists()
        all_exist = all_exist and exists
        status = "✅" if exists else "❌"
        print(f"  {status} {file_name}")
    
    return all_exist

def check_frontend_files():
    """Check if all frontend files exist"""
    base_path = Path(__file__).parent / 'frontend/src'
    required_files = [
        'App.jsx',
        'api.js',
        'components/PythonScriptsSection.jsx',
        'components/ScriptRunner.jsx',
        'components/NormalizedLogsViewer.jsx',
        'components/ChartsSection.jsx',
        'components/VulnerabilitiesSection.jsx',
        'components/LogsSection.jsx',
        'glass-effects.css',
    ]
    
    print("\nFrontend Files:")
    all_exist = True
    for file_name in required_files:
        file_path = base_path / file_name
        exists = file_path.exists()
        all_exist = all_exist and exists
        status = "✅" if exists else "❌"
        print(f"  {status} {file_name}")
    
    return all_exist

def check_backend_imports():
    """Check if backend can import all required modules"""
    print("\nBackend Dependencies:")
    modules = {
        'fastapi': 'FastAPI web framework',
        'uvicorn': 'ASGI server',
        'pymongo': 'MongoDB driver',
        'pydantic': 'Data validation',
        'apscheduler': 'Task scheduling',
    }
    
    all_ok = True
    for module_name, description in modules.items():
        try:
            __import__(module_name)
            print_check(f"✅ {module_name}", True, description)
        except ImportError:
            print_check(f"❌ {module_name}", False, description)
            all_ok = False
    
    return all_ok

def check_no_celery():
    """Ensure Celery is NOT imported in scripts.py"""
    print("\nCritical Fixes:")
    base_path = Path(__file__).parent / 'backend/routes/scripts.py'
    
    if not base_path.exists():
        print_check("scripts.py exists", False, "File not found")
        return False
    
    with open(base_path, 'r') as f:
        content = f.read()
    
    # Check Celery is not imported
    has_celery = 'from celery import' in content or 'import celery' in content
    print_check("✅ No Celery dependency", not has_celery, 
                "Scripts use threading instead" if not has_celery else "⚠️ Celery still present!")
    
    # Check threading is imported
    has_threading = 'import threading' in content
    print_check("✅ Threading support", has_threading, 
                "BackgroundTasks with threading.Lock" if has_threading else "Missing!")
    
    return not has_celery and has_threading

def check_error_handling():
    """Check if stats_service has MongoDB error handling"""
    print("\nError Handling:")
    base_path = Path(__file__).parent / 'backend/services/stats_service.py'
    
    if not base_path.exists():
        print_check("stats_service.py exists", False, "File not found")
        return False
    
    with open(base_path, 'r') as f:
        content = f.read()
    
    # Check for error handling
    has_error_handling = 'ServerSelectionTimeoutError' in content
    has_try_catch = 'try:' in content and 'except' in content
    
    print_check("✅ ServerSelectionTimeoutError handling", has_error_handling)
    print_check("✅ Try-catch blocks", has_try_catch)
    
    return has_error_handling and has_try_catch

def check_api_functions():
    """Check if frontend API functions are present"""
    print("\nFrontend API Functions:")
    base_path = Path(__file__).parent / 'frontend/src/api.js'
    
    if not base_path.exists():
        print_check("api.js exists", False, "File not found")
        return False
    
    with open(base_path, 'r') as f:
        content = f.read()
    
    functions = {
        'executeScript': 'Script execution',
        'getScriptStatus': 'Status polling',
        'listScripts': 'List scripts',
        'getScriptTasks': 'Task listing',
    }
    
    all_present = True
    for func_name, description in functions.items():
        present = f'export const {func_name}' in content
        all_present = all_present and present
        print_check(f"✅ {func_name}()", present, description)
    
    return all_present

def check_main_imports():
    """Check if main.py imports scripts router"""
    print("\nBackend Router Integration:")
    base_path = Path(__file__).parent / 'backend/main.py'
    
    if not base_path.exists():
        print_check("main.py exists", False, "File not found")
        return False
    
    with open(base_path, 'r') as f:
        content = f.read()
    
    has_import = 'from backend.routes import' in content and 'scripts' in content
    has_router = 'app.include_router(scripts.router)' in content
    
    print_check("✅ Scripts router imported", has_import)
    print_check("✅ Scripts router included", has_router)
    
    return has_import and has_router

def check_docker_compose():
    """Check if docker-compose.yml is configured"""
    print("\nDocker Configuration:")
    base_path = Path(__file__).parent / 'docker-compose.yml'
    
    if not base_path.exists():
        print_check("docker-compose.yml exists", False, "File not found")
        return False
    
    with open(base_path, 'r') as f:
        content = f.read()
    
    has_mongo = 'mongo:' in content
    has_backend = 'backend:' in content
    has_frontend = 'frontend:' in content
    has_volumes = 'volumes:' in content
    
    print_check("✅ MongoDB service", has_mongo)
    print_check("✅ Backend service", has_backend)
    print_check("✅ Frontend service", has_frontend)
    print_check("✅ Data volumes", has_volumes)
    
    return has_mongo and has_backend and has_frontend

def check_test_files():
    """Check if test files exist"""
    print("\nTest & Documentation Files:")
    base_path = Path(__file__).parent
    test_files = {
        'test_mongo_connection.py': 'MongoDB connection test',
        'BACKEND_FIXES_SUMMARY.md': 'Detailed fix documentation',
        'QUICK_START.md': 'Quick start guide',
    }
    
    all_exist = True
    for file_name, description in test_files.items():
        file_path = base_path / file_name
        exists = file_path.exists()
        all_exist = all_exist and exists
        print_check(f"✅ {file_name}", exists, description)
    
    return all_exist

def main():
    """Run all health checks"""
    print_header("VULNERABILITY DETECTION SYSTEM - HEALTH CHECK")
    
    results = {
        'Python Version': check_python_version(),
        'Project Structure': check_project_structure(),
        'Backend Files': check_backend_files(),
        'Frontend Files': check_frontend_files(),
        'Backend Dependencies': check_backend_imports(),
        'Critical Fixes': check_no_celery(),
        'Error Handling': check_error_handling(),
        'API Functions': check_api_functions(),
        'Router Integration': check_main_imports(),
        'Docker Setup': check_docker_compose(),
        'Test Files': check_test_files(),
    }
    
    # Summary
    print_header("SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, passed_check in results.items():
        status = "✅" if passed_check else "❌"
        print(f"{status} {check_name}")
    
    print(f"\n{'=' * 60}")
    print(f"  Results: {passed}/{total} checks passed")
    print(f"{'=' * 60}\n")
    
    if passed == total:
        print("🎉 All systems operational! Ready to deploy.\n")
        print("Next steps:")
        print("  1. docker-compose up mongo")
        print("  2. cd backend && python -m uvicorn main:app --reload")
        print("  3. cd frontend && npm run dev")
        print("  4. Open http://localhost:5173\n")
        return 0
    else:
        print(f"⚠️  {total - passed} issue(s) found. Please fix before deployment.\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
