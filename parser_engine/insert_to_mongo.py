import json
import os
from datetime import datetime
from pymongo import MongoClient
from hashlib import md5

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:admin123@localhost:27017/?authSource=admin")
DB_NAME = os.environ.get("VULN_DB", "vulnerability_logs")
# Using Sysmon logs for now as the soc_logs.events.json is missing
DATA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "datasets", "windows", "sysmon.jsonl"))

# ------------------------------------------------------------
# DB CONNECTION
# ------------------------------------------------------------
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["normalized_logs"]
matches_collection = db["vuln_matches"]

# ------------------------------------------------------------
# NORMALIZATION
# ------------------------------------------------------------
import random

def normalize_soc_log(item):
    """
    Normalize the complex nested SOC log structure to a flat format expected by the system.
    Supports both standard SOC structure and Sysmon structure.
    Enriches with dummy versions if missing, for demonstration purposes.
    """
    try:
        # --- ALREADY NORMALIZED HANDLER ---
        # Checks if key fields exist corresponding to OUT_*.jsonl format
        if "timestamp" in item and "host" in item and "source" in item and "message" in item:
            # Enforce datetime
            ts_str = item["timestamp"]
            try:
                # Try parsing if string
                if isinstance(ts_str, str):
                    if "T" in ts_str:
                         ts = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    else:
                         ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    ts_formatted = ts.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    ts_formatted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            except:
                ts_formatted = ts_str # Assume correct if parsing fails or keep string

            software = item.get("software", "unknown")
            version = item.get("version", "N/A")

            # DEMO: Enrich version for matching if missing
            if version == "N/A" or not version:
                if "ssh" in software.lower(): version = "OpenSSH 7.2p2"
                elif "nginx" in software.lower(): version = "1.14.0"
                elif "apache" in software.lower(): version = "2.4.29"
                elif "sudo" in software.lower(): version = "1.8.21"
                elif "kernel" in software.lower(): version = "4.4.0"
                elif "python" in software.lower(): version = "2.7.12"
                elif "chrome" in software.lower(): version = "100.0.4896.60"
                elif "firefox" in software.lower(): version = "98.0.1"
                elif "explorer" in software.lower(): version = "10.0.19041"
                else: version = "N/A"
            
            # Ensure format
            return {
                "_id": item.get("_id") or md5(json.dumps(item, sort_keys=True).encode()).hexdigest(),
                "timestamp": ts_formatted,
                "host": item["host"],
                "os": item.get("os", "Unknown"),
                "software": software,
                "version": version,
                "event_type": item.get("event_type", "log"),
                "message": item["message"],
                "source": item["source"],
                "severity": item.get("severity", "info")
            }

        # --- SYSMON FORMAT HANDLER ---
        if "EventID" in item and "Computer" in item:
            # Timestamp: "2025-11-01 00:00:00"
            ts_str = item.get("TimeCreated", "")
            try:
                # Ensure we have a parseable timestamp
                ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                ts_formatted = ts.strftime("%Y-%m-%d %H:%M:%S")
            except:
                ts_formatted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            software = item.get("ProcessName", "unknown")
            version = "N/A"
            
            # DEMO: Enrich version for matching
            if "notepad" in software.lower(): version = "10.0.19041"
            if "explorer" in software.lower(): version = "10.0.19041"
            if "chrome" in software.lower(): version = "100.0.4896.60"
            if "firefox" in software.lower(): version = "98.0.1"

            return {
                "_id": md5(json.dumps(item, sort_keys=True).encode()).hexdigest(),
                "timestamp": ts_formatted,
                "host": item.get("Computer", "unknown"),
                "os": "Windows",
                "software": software,
                "version": version,
                "event_type": f"EventID {item.get('EventID')}",
                "message": f"Process: {item.get('ProcessName')} User: {item.get('User')} Cmd: {item.get('CommandLine')}",
                "source": "sysmon"
            }

        # --- RAW LOG HANDLER (New Heuristics) ---
        if "raw_message" in item:
            msg = item["raw_message"]
            source = item.get("source", "unknown_log")
            
            # Defaults
            software = "unknown"
            version = "N/A"
            event_type = "log"
            host = "unknown"
            
            # 1. Apache/Web Logs
            if "GET " in msg or "POST " in msg or "http" in source.lower():
                software = "apache"
                version = "2.4.49" # Vulnerable to Path Traversal (recent example)
                event_type = "web_access"
                host = "web_server_01"
                
            # 2. SSH/Auth Logs
            elif "ssh" in msg.lower() or "auth" in source.lower():
                software = "sshd"
                version = "OpenSSH 7.2p2" # Vulnerable to Username Enumeration
                event_type = "auth"
                host = "ssh_gateway"

            # 3. DNS Logs
            elif "dns" in msg.lower() or "query" in msg.lower() or "dns" in source.lower():
                software = "bind"
                version = "9.11.4" # Vulnerable version
                event_type = "dns_query"
                host = "dns_server"
                
            # 4. FTP Logs
            elif "ftp" in msg.lower() or "file" in msg.lower():
                software = "vsftpd"
                version = "2.3.4" # Backdoor vulnerability version
                event_type = "file_transfer"
                host = "ftp_server"

            return {
                "_id": md5(msg.encode()).hexdigest(),
                "timestamp": item.get("timestamp"),
                "host": host,
                "os": "Linux",
                "software": software,
                "version": version,
                "event_type": event_type,
                "message": msg,
                "source": source,
                "severity": "info"
            }
    except Exception as e:
        # print(f"[WARN] Normalization error: {e}")
        return None

# ------------------------------------------------------------
# STREAMING PARSER
# ------------------------------------------------------------
def stream_logs(filepath):
    """
    Streaming parser handling JSON Lines, JSON Array, or Raw Text Logs.
    """
    filename = os.path.basename(filepath)
    is_json = filepath.endswith(".json") or filepath.endswith(".jsonl")

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        # If explicitly known as JSON, try JSON parsing
        if is_json:
            for line in f:
                if line.strip():
                    try:
                         if line.startswith("<<<<") or line.startswith("====") or line.startswith(">>>>"): continue
                         yield json.loads(line)
                    except: pass
        else:
            # RAW TEXT LOGS (Bro/Zeek, Syslog, etc)
            # Yield each line as a generic log structure
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue # Skip comments
                yield {
                    "raw_message": line, 
                    "source": filename,
                    "timestamp": datetime.now().isoformat() # Placeholder for raw logs
                }

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
import glob

def main(payload=None):
    # Find all log files in datasets/
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, ".."))
    datasets_dir = os.path.join(project_root, "datasets")
    
    # Get all .log files from datasets
    files = glob.glob(os.path.join(datasets_dir, "*.log"))
    
    if not files:
        print(f"[ERR] No .log files found in {datasets_dir}")
        return {"status": "error", "message": "no_files_found"}

    # Clear existing data ONLY if requested
    reset = payload.get("reset", False) if payload else False
    if reset:
        print("[+] Clearing existing logs and matches...")
        collection.delete_many({})
        matches_collection.delete_many({})
        db["alerts"].delete_many({})
    else:
        print("[+] 'reset' flag not set. Appending new logs (skipping duplicates).")


    total_processed = 0
    total_inserted = 0
    BATCH_SIZE = 1000

    for data_file in files:
        print(f"[+] Processing file: {data_file}")
        count = 0
        inserted = 0
        batch = []

        try:
            for item in stream_logs(data_file):
                count += 1
                norm = normalize_soc_log(item)
                if norm:
                    # Convert timestamp to datetime object for MongoDB
                    try:
                        norm["timestamp"] = datetime.strptime(norm["timestamp"], "%Y-%m-%d %H:%M:%S")
                    except:
                        pass 
                    
                    batch.append(norm)

                if len(batch) >= BATCH_SIZE:
                    try:
                        collection.insert_many(batch, ordered=False)
                        inserted += len(batch)
                        if inserted % 10000 == 0:
                            print(f"[STATUS] Ingested {inserted} logs...")
                    except Exception as e:
                        # Duplicate key errors are common if we re-run, ignore them
                        if "E11000" not in str(e):
                            print(f"[WARN] Batch insert error: {e}")
                    batch = []

            # Insert remaining
            if batch:
                try:
                    collection.insert_many(batch, ordered=False)
                    inserted += len(batch)
                except Exception as e:
                    if "E11000" not in str(e):
                        print(f"[WARN] Final batch insert error: {e}")

            print(f"    [✓] File complete. Processed: {count}, Inserted: {inserted}")
            total_processed += count
            total_inserted += inserted

        except Exception as e:
            print(f"\n[ERR] Ingestion failed for {data_file}: {e}")

    print(f"\n[✓] Total Ingestion complete. Processed: {total_processed}, Inserted: {total_inserted}")
    return {"status": "completed", "processed": total_processed, "inserted": total_inserted}

if __name__ == "__main__":
    main()
