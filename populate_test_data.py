"""
Test script to populate sample vulnerability matches and generate a report
"""
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb://admin:admin123@localhost:27017/?authSource=admin"
DB_NAME = "vulnerability_logs"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
matches = db['vuln_matches']

# Clear existing data
print("[+] Clearing existing matches...")
matches.delete_many({})

# Insert sample data with proper structure
print("[+] Inserting sample vulnerability matches...")

sample_data = [
    {
        "_id": "test1__CVE-2016-3115",
        "matched_at": datetime.utcnow(),
        "log_id": "test_log_1",
        "host": "ssh_gateway",
        "timestamp": datetime.utcnow(),
        "software": "sshd",
        "version": "OpenSSH 7.2p2",
        "cve_id": "CVE-2016-3115",
        "severity": "HIGH",  # Note: uppercase as per matcher.py
        "cvss_score": "6.4",
        "description": "The do_setup_env function in session.c in sshd in OpenSSH before 7.2p2 allows remote authenticated users to bypass intended environment restrictions.",
        "message": "Sample SSH log message"
    },
    {
        "_id": "test2__CVE-2016-3115",
        "matched_at": datetime.utcnow(),
        "log_id": "test_log_2",
        "host": "ssh_gateway",
        "timestamp": datetime.utcnow(),
        "software": "sshd",
        "version": "OpenSSH 7.2p2",
        "cve_id": "CVE-2016-3115",
        "severity": "HIGH",
        "cvss_score": "6.4",
        "description": "The do_setup_env function in session.c in sshd in OpenSSH before 7.2p2 allows remote authenticated users to bypass intended environment restrictions.",
        "message": "Sample SSH log message"
    },
    {
        "_id": "test3__CVE-2022-3488",
        "matched_at": datetime.utcnow(),
        "log_id": "test_log_3",
        "host": "web_server",
        "timestamp": datetime.utcnow(),
        "software": "nginx",
        "version": "1.18.0",
        "cve_id": "CVE-2022-3488",
        "severity": "MEDIUM",
        "cvss_score": "5.3",
        "description": "Processing of repeated responses to the same query, where both responses contain ECS pseudo-options, can cause BIND 9 to exit with an assertion failure.",
        "message": "Sample nginx log message"
    },
    {
        "_id": "test4__CVE-2021-1234",
        "matched_at": datetime.utcnow(),
        "log_id": "test_log_4",
        "host": "db_server",
        "timestamp": datetime.utcnow(),
        "software": "mysql",
        "version": "5.7.0",
        "cve_id": "CVE-2021-1234",
        "severity": "CRITICAL",
        "cvss_score": "9.8",
        "description": "Critical vulnerability in MySQL server",
        "message": "Sample MySQL log message"
    },
    {
        "_id": "test5__CVE-2020-5678",
        "matched_at": datetime.utcnow(),
        "log_id": "test_log_5",
        "host": "web_server",
        "timestamp": datetime.utcnow(),
        "software": "apache",
        "version": "2.4.29",
        "cve_id": "CVE-2020-5678",
        "severity": "LOW",
        "cvss_score": "3.1",
        "description": "Low severity vulnerability in Apache",
        "message": "Sample Apache log message"
    }
]

matches.insert_many(sample_data)
print(f"[✓] Inserted {len(sample_data)} sample matches")

# Verify the data
print("\n[+] Verifying data...")
total = matches.count_documents({})
print(f"Total matches in database: {total}")

# Check hosts
hosts = matches.distinct("host")
print(f"Hosts: {hosts}")

# Check severity distribution
from collections import Counter
severities = Counter()
for record in matches.find():
    severities[record.get("severity", "Unknown")] += 1

print("\nSeverity distribution:")
for sev, count in severities.items():
    print(f"  {sev}: {count}")

print("\n[✓] Sample data ready for report generation!")
print("\nNow run: python reports/report_generator.py")
