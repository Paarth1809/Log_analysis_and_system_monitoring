# backend/config.py
from os import environ
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = environ.get("MONGO_URI", "mongodb://localhost:27017/vulnerability_logs") # Default to localhost without auth if not provided
DB_NAME = environ.get("VULN_DB", "vulnerability_logs")
API_HOST = environ.get("API_HOST", "0.0.0.0")
API_PORT = int(environ.get("API_PORT", 8000))
