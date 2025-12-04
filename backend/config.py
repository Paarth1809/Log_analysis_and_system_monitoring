# backend/config.py
from os import environ

MONGO_URI = environ.get("MONGO_URI", "mongodb://admin:admin123@localhost:27017/?authSource=admin")
DB_NAME = environ.get("VULN_DB", "vulnerability_logs")
API_HOST = environ.get("API_HOST", "0.0.0.0")
API_PORT = int(environ.get("API_PORT", 8000))
