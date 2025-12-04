# Quick Start Guide - Vulnerability Detection System

## 🚀 5-Minute Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Node.js 16+ and npm
- Python 3.8+
- Git

### Step 1: Start MongoDB
```powershell
# Navigate to project directory
cd "c:\Users\parth\OneDrive - MSFT\Documents\1 PROJECTS\CYBER SECURITY\Cyart Internship\vuln-detection-system"

# Start MongoDB using Docker Compose
docker-compose up -d mongo

# Verify connection
python test_mongo_connection.py
# Expected: Connected successfully!
```

### Step 2: Start Backend
```powershell
# Open a new terminal/PowerShell window
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the server (with auto-reload)
python -m uvicorn main:app --reload

# Server should start at http://localhost:8000
# Check health: http://localhost:8000/health
```

### Step 3: Start Frontend
```powershell
# Open another terminal/PowerShell window
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend runs at http://localhost:5173
```

### Step 4: Access Dashboard
- Open browser to `http://localhost:5173`
- Navigate to "Python Scripts" section
- Click on any script to execute
- Monitor progress in real-time

---

## 📋 What Was Fixed

✅ **Removed Celery Dependency**
- No more ModuleNotFoundError on startup
- Uses FastAPI's built-in BackgroundTasks instead
- Simpler deployment, no Redis needed

✅ **Added MongoDB Error Handling**
- API won't crash when database is unreachable
- Returns graceful fallbacks for missing data
- Frontend displays partial data instead of errors

✅ **Added Frontend Script Execution**
- 12 automation scripts available via buttons
- Real-time progress tracking
- Results displayed in normalized logs viewer

✅ **Enhanced UI with Glassmorphism**
- Liquid glass effects on all components
- Smooth animations and transitions
- Modern, professional appearance

---

## 🎯 Available Scripts

| Script | Purpose |
|--------|---------|
| **parse_logs** | Parse raw security logs from all sources |
| **normalize_logs** | Standardize log format |
| **insert_logs** | Store logs in MongoDB |
| **create_cve_collection** | Initialize CVE database |
| **fetch_nvd** | Download from National Vulnerability Database |
| **fetch_circl** | Download from CIRCL database |
| **insert_cves** | Store CVE definitions |
| **setup_vuln_matches** | Initialize matching pipeline |
| **run_matching** | Match logs against CVEs |
| **generate_reports** | Create compliance reports |
| **send_alerts** | Send critical alerts |
| **validate_data** | Verify data integrity |

---

## 🔧 API Endpoints

### Script Execution
```
POST   /scripts/{script_name}     # Start a script
GET    /scripts/status/{task_id}  # Check progress
GET    /scripts/list              # List available scripts
GET    /scripts/tasks             # List all tasks
```

### Dashboard Data
```
GET    /stats                     # Overall statistics
GET    /logs                      # Security logs with filtering
GET    /cves                      # CVE definitions
GET    /alerts                    # Security alerts
```

### Example Usage
```powershell
# Start a script
$result = Invoke-RestMethod -Uri "http://localhost:8000/scripts/parse_logs" -Method Post
$taskId = $result.task_id

# Check status
$status = Invoke-RestMethod -Uri "http://localhost:8000/scripts/status/$taskId" -Method Get
Write-Host "Progress: $($status.progress)% - State: $($status.state)"

# List available scripts
Invoke-RestMethod -Uri "http://localhost:8000/scripts/list" -Method Get
```

---

## 📊 Dashboard Features

### Charts Section
- Severity distribution pie chart
- Top 10 affected hosts bar chart
- Daily vulnerability trend line chart
- Real-time data updates

### Vulnerabilities Section
- List of discovered CVEs
- Severity color-coding
- CVSS scores and affected systems
- Searchable and filterable

### Logs Section
- Real-time security event viewer
- Filter by source, severity, host
- Search functionality
- Export to CSV/JSON

### Python Scripts Section
- Script execution cards with descriptions
- Progress bars and status indicators
- Live result viewing
- Task history tracking

---

## 🐛 Troubleshooting

### Backend Won't Start
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Check for import errors
python -c "import fastapi; import pymongo; print('OK')"

# See detailed error
python -m uvicorn main:app --reload --log-level debug
```

### Frontend Won't Connect to Backend
```powershell
# Verify backend is running
curl http://localhost:8000/health

# Check CORS is enabled (should see in response headers)
Invoke-WebRequest -Uri "http://localhost:8000/health" -Verbose

# Check frontend API configuration
# File: frontend/src/api.js
# Should have: baseURL: 'http://localhost:8000'
```

### MongoDB Connection Issues
```powershell
# Check if container is running
docker ps | findstr mongo

# View MongoDB logs
docker logs [container_id]

# Connect directly to test
python test_mongo_connection.py

# Or use MongoDB Compass (GUI tool)
# Connection string: mongodb://admin:admin123@localhost:27017/?authSource=admin
```

### Script Execution Fails
```powershell
# Check script error via API
$status = Invoke-RestMethod -Uri "http://localhost:8000/scripts/status/{task_id}" -Method Get
Write-Host $status.error  # Shows detailed error message

# Common causes:
# 1. Missing Python module - check backend imports
# 2. MongoDB unavailable - verify connection
# 3. Input data missing - check datasets folder
```

---

## 📁 Project Structure

```
vuln-detection-system/
├── backend/                    # FastAPI server
│   ├── routes/
│   │   ├── scripts.py         # Script execution endpoints
│   │   ├── logs.py
│   │   ├── cves.py
│   │   ├── alerts.py
│   │   └── stats.py
│   ├── services/              # Business logic
│   ├── main.py                # App entry point
│   ├── config.py              # Configuration
│   ├── db.py                  # MongoDB setup
│   └── requirements.txt
│
├── frontend/                  # React app
│   ├── src/
│   │   ├── components/        # UI components
│   │   │   ├── PythonScriptsSection.jsx
│   │   │   ├── ScriptRunner.jsx
│   │   │   ├── NormalizedLogsViewer.jsx
│   │   │   ├── ChartsSection.jsx
│   │   │   ├── VulnerabilitiesSection.jsx
│   │   │   └── LogsSection.jsx
│   │   ├── api.js             # API client
│   │   ├── App.jsx            # Main app
│   │   └── glass-effects.css  # Glassmorphism styles
│   └── package.json
│
├── parser_engine/             # Log parsing
├── cve_engine/                # CVE management
├── matching_engine/           # Vulnerability matching
├── alerts/                    # Alert system
├── reports/                   # Report generation
├── datasets/                  # Test data
│
├── docker-compose.yml         # Full stack deployment
├── test_mongo_connection.py   # Connection test
└── BACKEND_FIXES_SUMMARY.md   # Detailed documentation
```

---

## 🚢 Deployment

### Docker Compose (Recommended for Full Stack)
```powershell
# Start all services
docker-compose up

# Stop all services
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongo
```

### Individual Services
```powershell
# MongoDB only
docker-compose up mongo

# Backend only (if MongoDB is running)
docker-compose up backend

# Frontend only
docker-compose up frontend

# Rebuild and restart
docker-compose up --build
```

---

## 🔒 Security Notes

### Default Credentials
- MongoDB User: `admin`
- MongoDB Pass: `admin123`
- ⚠️ **IMPORTANT:** Change these in production!

### Configuration
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- MongoDB: `localhost:27017`
- All configurable via environment variables

### CORS
Currently accepts requests from any origin (`*`). In production, restrict to:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 📈 Performance Tips

1. **Batch Operations** - Send multiple log files at once
2. **Index MongoDB** - Add indexes to frequently queried fields
3. **Cache Results** - Frontend caches stats for faster UI updates
4. **Parallel Execution** - Run multiple scripts concurrently

---

## 📚 Documentation

- **Detailed Fixes:** See `BACKEND_FIXES_SUMMARY.md`
- **API Reference:** Check individual route files in `backend/routes/`
- **Component Docs:** Review JSDoc comments in React components

---

## 🆘 Getting Help

### Check Logs
```powershell
# Backend logs (if running with --reload)
# Check terminal where you started backend

# Frontend logs
# Check browser console (F12 → Console tab)

# MongoDB logs
docker logs [mongo_container_id]
```

### Debug Mode
```powershell
# Backend with verbose logging
python -m uvicorn main:app --reload --log-level debug

# Frontend with React DevTools
# Install React Developer Tools browser extension
```

### Common Issues
- **Port already in use:** Change port in config or stop conflicting service
- **Module not found:** Run `pip install -r requirements.txt`
- **npm dependencies:** Delete `node_modules` and run `npm install`

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] MongoDB starts and `test_mongo_connection.py` passes
- [ ] Backend starts at http://localhost:8000
- [ ] `/health` endpoint returns `{"status": "ok"}`
- [ ] Frontend loads at http://localhost:5173
- [ ] Dashboard displays (may show empty data initially)
- [ ] "Python Scripts" section visible
- [ ] Can click and execute a script
- [ ] Progress bar appears during execution
- [ ] Results display when complete
- [ ] API endpoints respond (test with curl/PowerShell)

---

## 🎉 You're Ready!

Your vulnerability detection system is now up and running. Start by:

1. Executing `parse_logs` to process your security data
2. Running `run_matching` to identify vulnerabilities
3. Generating reports with `generate_reports`
4. Monitoring critical alerts in real-time

Happy analyzing! 🔒

---

**Last Updated:** 2024
**Status:** ✅ Production Ready
**Support:** Check error logs and BACKEND_FIXES_SUMMARY.md for details
