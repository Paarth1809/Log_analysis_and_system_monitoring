from pymongo import MongoClient
import os

MONGO_URI = "mongodb://admin:admin123@localhost:27017/?authSource=admin"
client = MongoClient(MONGO_URI)
db = client["vulnerability_logs"]

print("--- DB STATUS ---")
print(f"normalized_logs: {db.normalized_logs.count_documents({})}")
print(f"vuln_matches: {db.vuln_matches.count_documents({})}")
print(f"alerts: {db.alerts.count_documents({})}")
print(f"cve_database: {db.cve_database.count_documents({})}")
