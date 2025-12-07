# backend/config.py
from os import environ
from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
print(f"[DEBUG-BACKEND] Loading env from: {os.path.abspath(env_path)}")
load_dotenv(env_path, override=True)

DEFAULT_URI = "mongodb://admin:admin123@localhost:27017/?authSource=admin"
MONGO_URI = environ.get("MONGO_URI", DEFAULT_URI) 
DB_NAME = environ.get("VULN_DB", "vulnerability_logs")
API_HOST = environ.get("API_HOST", "0.0.0.0")
API_PORT = int(environ.get("API_PORT", 8000))

print(f"[DEBUG-BACKEND] MONGO_URI: {MONGO_URI.split('@')[-1] if '@' in MONGO_URI else 'NO_AUTH'}")
