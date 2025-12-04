# Developer Cheat Sheet

## 🚀 Common Commands

### Starting the Stack
```powershell
# Full stack (all services)
docker-compose up

# Individual services
docker-compose up mongo          # Just database
docker-compose up backend        # Database + backend
docker-compose up -d mongo       # MongoDB in background

# With new builds
docker-compose up --build mongo
docker-compose up --build
```

### Backend Development
```powershell
cd backend

# Installation
pip install -r requirements.txt

# Development server (with auto-reload)
python -m uvicorn main:app --reload

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000

# Check specific module
python -c "import backend.routes.scripts; print('OK')"

# Run tests
pytest
```

### Frontend Development
```powershell
cd frontend

# Installation
npm install

# Development server
npm run dev

# Production build
npm run build

# Run tests
npm test

# Linting
npm run lint
```

### Database Operations
```powershell
# Test connection
python test_mongo_connection.py

# Interactive shell
python
>>> from pymongo import MongoClient
>>> client = MongoClient("mongodb://admin:admin123@localhost:27017/?authSource=admin")
>>> db = client["vulnerability_logs"]
>>> db.list_collection_names()

# Clear collection
python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://admin:admin123@localhost:27017/?authSource=admin')
db = client['vulnerability_logs']
db.normalized_logs.delete_many({})
print('Cleared normalized_logs')
"

# Count documents
python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://admin:admin123@localhost:27017/?authSource=admin')
db = client['vulnerability_logs']
print(f'Logs: {db.normalized_logs.count_documents({})}')
print(f'CVEs: {db.cve_database.count_documents({})}')
print(f'Matches: {db.vuln_matches.count_documents({})}')
"
```

---

## 🐛 Debugging

### Backend Debugging
```powershell
# Verbose logging
python -m uvicorn main:app --reload --log-level debug

# Check imports
python -c "from backend.routes import scripts; print('✓ scripts')"
python -c "from backend.services import stats_service; print('✓ stats')"

# Check database connection
python -c "
from backend.db import COL_LOGS
try:
    count = COL_LOGS.estimated_document_count()
    print(f'✓ Database connected: {count} logs')
except Exception as e:
    print(f'✗ Database error: {e}')
"

# Check running processes
netstat -ano | findstr :8000    # Backend
netstat -ano | findstr :5173    # Frontend
netstat -ano | findstr :27017   # MongoDB
```

### Frontend Debugging
```powershell
# Check browser console (F12 → Console)
# Check network tab (F12 → Network)
# Check React components (F12 → Components)

# Clear cache
rm -r node_modules .next
npm install

# Check build errors
npm run build 2>&1 | head -50
```

### API Testing
```powershell
# List scripts
curl http://localhost:8000/scripts/list

# Execute script
$response = Invoke-RestMethod -Uri "http://localhost:8000/scripts/parse_logs" -Method Post
$taskId = $response.task_id
Write-Host "Task ID: $taskId"

# Check status
Invoke-RestMethod -Uri "http://localhost:8000/scripts/status/$taskId" -Method Get

# List tasks
Invoke-RestMethod -Uri "http://localhost:8000/scripts/tasks" -Method Get

# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get

# Get stats
Invoke-RestMethod -Uri "http://localhost:8000/stats" -Method Get
```

---

## 📝 Code Navigation

### Find Files
```powershell
# Backend script endpoints
code backend/routes/scripts.py

# Frontend script runner component
code frontend/src/components/ScriptRunner.jsx

# API client
code frontend/src/api.js

# Database configuration
code backend/db.py

# Main app
code backend/main.py
```

### Search Across Project
```powershell
# Find all endpoints
grep -r "@router" backend/routes/

# Find all API calls
grep -r "api.get\|api.post" frontend/src/

# Find imports of specific module
grep -r "from backend.routes import" backend/

# Find all error handling
grep -r "except" backend/ | grep -v __pycache__
```

---

## 🔍 Monitoring

### Real-time Logs
```powershell
# Backend logs
docker logs -f backend

# MongoDB logs
docker logs -f mongo

# All services
docker-compose logs -f

# Follow specific service
docker-compose logs -f backend --tail=50
```

### Container Status
```powershell
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Container resource usage
docker stats

# Detailed container info
docker inspect [container_id]

# View environment variables
docker inspect [container_id] | findstr -A 20 Env
```

### Performance Metrics
```powershell
# MongoDB performance
python -c "
from pymongo import MongoClient
import time
client = MongoClient('mongodb://admin:admin123@localhost:27017/?authSource=admin')
db = client['vulnerability_logs']

start = time.time()
count = db.normalized_logs.count_documents({})
elapsed = (time.time() - start) * 1000
print(f'Query time: {elapsed:.2f}ms for {count} documents')
"

# API response time
$start = Get-Date
$response = Invoke-RestMethod -Uri "http://localhost:8000/stats" -Method Get
$elapsed = (Get-Date) - $start
Write-Host "API response time: $($elapsed.TotalMilliseconds)ms"
```

---

## 🔧 Troubleshooting Guide

### Issue: Backend Won't Start
```powershell
# Check error message
python -m uvicorn main:app --reload 2>&1

# Verify imports
python -c "import fastapi; import pymongo; import apscheduler"

# Check port is free
netstat -ano | findstr :8000
# If port used: lsof -i :8000 (Mac/Linux) or powershell: Get-NetTCPConnection -LocalPort 8000

# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Frontend Can't Connect to Backend
```powershell
# Verify backend is running
Invoke-RestMethod -Uri http://localhost:8000/health

# Check CORS headers
Invoke-WebRequest -Uri http://localhost:8000/health -Verbose

# Check frontend API URL
code frontend/src/api.js  # Should have baseURL: 'http://localhost:8000'

# Test direct API call from browser console
# fetch('http://localhost:8000/stats').then(r => r.json()).then(d => console.log(d))
```

### Issue: MongoDB Connection Failed
```powershell
# Check container is running
docker ps | findstr mongo

# Check connection
python test_mongo_connection.py

# View logs
docker logs mongo

# Start container
docker-compose up -d mongo

# Reset MongoDB
docker-compose down
docker volume rm vuln-detection-system_mongo_data  # Clear data
docker-compose up -d mongo
```

### Issue: Script Execution Fails
```powershell
# Check script status
$task = Invoke-RestMethod -Uri "http://localhost:8000/scripts/status/[task-id]" -Method Get
Write-Host $task.error

# Check if Python modules exist
python -c "import parser_engine.parser; print('✓')"

# Common causes:
# 1. Missing module imports
# 2. File not found (datasets/...)
# 3. MongoDB unavailable
# 4. Syntax error in script
```

---

## 📊 Useful Queries

### MongoDB Queries
```javascript
// Count by severity
db.vuln_matches.aggregate([
  { $group: { _id: "$severity", count: { $sum: 1 } } }
])

// Top 10 hosts
db.vuln_matches.aggregate([
  { $group: { _id: "$host", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
])

// Logs in last 24h
db.normalized_logs.find({
  timestamp: { $gt: new Date(Date.now() - 24*60*60*1000) }
}).count()

// Export to JSON
db.normalized_logs.find().limit(100).toArray()
```

### API Queries with PowerShell
```powershell
# Get all stats
$stats = Invoke-RestMethod -Uri http://localhost:8000/stats -Method Get
$stats | ConvertTo-Json

# Get logs with filter
$logs = Invoke-RestMethod -Uri "http://localhost:8000/logs?source=sysmon&limit=10" -Method Get
$logs | ConvertTo-Json

# Get CVEs with severity
$cves = Invoke-RestMethod -Uri "http://localhost:8000/cves?severity=high" -Method Get
$cves | ConvertTo-Json

# List all tasks
$tasks = Invoke-RestMethod -Uri http://localhost:8000/scripts/tasks -Method Get
$tasks.tasks | Select-Object task_id, script_name, state, progress
```

---

## 🎯 Development Workflow

### Adding a New Component
```powershell
# 1. Create component file
code frontend/src/components/MyComponent.jsx

# 2. Import in App.jsx
code frontend/src/App.jsx

# 3. Test in browser
npm run dev
# Check http://localhost:5173 in browser

# 4. Check for errors
# F12 → Console (browser developer tools)
```

### Adding a New API Endpoint
```powershell
# 1. Create route file or add to existing
code backend/routes/my_route.py

# 2. Import in main.py
code backend/main.py
# Add: from backend.routes import my_route
# Add: app.include_router(my_route.router)

# 3. Add API function in frontend
code frontend/src/api.js
# Add: export const getMyData = () => api.get('/my-endpoint')

# 4. Use in component
# import { getMyData } from '../api'
# const response = await getMyData()

# 5. Test
curl http://localhost:8000/my-endpoint
```

### Debugging a Component
```powershell
# Add console logs
console.log('Component mounted', data)

# Check React DevTools
# F12 → Components tab

# Check props
console.log('Props received:', props)

# Check state
useState hook → Add console.log in useEffect

# Network tab
# F12 → Network → See API calls
```

---

## 🚀 Performance Optimization

### Backend Optimization
```python
# Add caching
from functools import lru_cache

@lru_cache(maxsize=100)
def get_stats():
    # Cached for repeated calls
    pass

# Add indexing (MongoDB)
db.normalized_logs.create_index([('timestamp', -1)])
db.vuln_matches.create_index([('host', 1), ('severity', 1)])

# Use pagination
def get_logs(limit=100, skip=0):
    return list(db.normalized_logs.find().skip(skip).limit(limit))
```

### Frontend Optimization
```javascript
// Memoize components
const MyComponent = React.memo(({ data }) => {
  // Only re-renders when data changes
  return <div>{data}</div>
})

// Use useCallback for event handlers
const handleClick = useCallback(() => {
  // Stable function reference
  executeScript()
}, [])

// Use lazy loading for heavy components
const HeavyComponent = React.lazy(() => import('./HeavyComponent'))
```

---

## 📚 Quick Reference

### API Status Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Server Error |

### Task States
| State | Meaning |
|-------|---------|
| pending | Queued, not started |
| running | Currently executing |
| success | Completed successfully |
| failed | Error during execution |

### Severity Levels
| Level | Score |
|-------|-------|
| critical | 9.0-10.0 |
| high | 7.0-8.9 |
| medium | 4.0-6.9 |
| low | 0.1-3.9 |

---

## 🆘 Emergency Commands

### Restart Everything
```powershell
docker-compose down
docker-compose up
```

### Clear All Data
```powershell
docker-compose down -v
docker-compose up -d mongo
# Data cleared!
```

### View All Logs
```powershell
docker-compose logs --follow
```

### Kill Hung Process
```powershell
# Find process on port
netstat -ano | findstr :8000

# Kill it
taskkill /PID [pid] /F
```

### Reset Docker
```powershell
docker system prune -a
docker volume prune
# Removes all unused images and volumes
```

---

**Last Updated:** 2024
**Version:** 1.0
**Status:** Ready for Development ✅
