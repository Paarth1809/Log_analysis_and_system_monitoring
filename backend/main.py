# backend/main.py
from fastapi import FastAPI
from backend.routes import run
from fastapi.middleware.cors import CORSMiddleware
from .config import API_HOST, API_PORT
from .routes import logs, cves, alerts, stats

app = FastAPI(title="Vuln Detection API", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(logs.router)
app.include_router(cves.router)
app.include_router(alerts.router)
app.include_router(stats.router)

@app.get("/health")
def health():
    return {"status": "ok"}
