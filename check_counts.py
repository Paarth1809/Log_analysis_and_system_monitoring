
from pymongo import MongoClient
import os

client = MongoClient("mongodb://admin:admin123@localhost:27017/?authSource=admin")
db = client["vulnerability_logs"]

print(f"Normalized Logs: {db.normalized_logs.count_documents({})}")
print(f"Vuln Matches: {db.vuln_matches.count_documents({})}")
print(f"Alerts: {db.alerts.count_documents({})}")

print("\n--- Vuln Matches Severity Breakdown ---")
pipeline = [{"$group": {"_id": "$severity", "count": {"$sum": 1}}}]
for doc in db.vuln_matches.aggregate(pipeline):
    print(f"{doc['_id']}: {doc['count']}")

print("\n--- Alerts Breakdown ---")
pipeline = [{"$group": {"_id": "$rule_type", "count": {"$sum": 1}}}]
for doc in db.alerts.aggregate(pipeline):
    print(f"{doc['_id']}: {doc['count']}")
