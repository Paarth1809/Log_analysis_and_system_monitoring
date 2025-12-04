@echo off
echo Starting Vulnerability Detection System...

echo Starting Backend...
start "Backend" cmd /k "python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

echo Starting Frontend...
start "Frontend" cmd /k "cd react-frontend && npm start"

echo System started!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000/docs
echo.
echo Note: Ensure MongoDB is running locally on port 27017.
