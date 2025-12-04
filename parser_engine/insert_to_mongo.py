import json
<<<<<<< HEAD
import os
=======
>>>>>>> cd260ba9258ba3c2c7ffb1588424565f3f1c9eae
from datetime import datetime
from pymongo import MongoClient
from hashlib import md5

<<<<<<< HEAD
# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:admin123@localhost:27017/?authSource=admin")
DB_NAME = os.environ.get("VULN_DB", "vulnerability_logs")
DATA_FILE = r"c:\Users\parth\OneDrive - MSFT\Desktop\vuln-detection-system\vuln-detection-system\data\soc_logs.events.json"

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
def normalize_soc_log(item):
    """
    Normalize the complex nested SOC log structure to a flat format expected by the system.
    """
    try:
        # Timestamp
        ts_str = item.get("@timestamp", {}).get("$date", "")
        try:
            # Handle 2025-11-27T08:11:38.003Z
            ts = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            ts_formatted = ts.strftime("%Y-%m-%d %H:%M:%S")
        except:
            ts_formatted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Host
        host = item.get("host", {}).get("name") or item.get("host_custom") or "unknown"
        
        # OS
        os_info = item.get("host", {}).get("os", {})
        os_name = os_info.get("name") or os_info.get("family") or "Unknown"
        
        # Software / Agent
        software = item.get("agent", {}).get("type") or item.get("service", {}).get("type") or "unknown"
        version = item.get("agent", {}).get("version") or ""

        # Event
        event = item.get("event", {})
        event_type = event.get("action") or event.get("kind") or "unknown"
        source_type = event.get("dataset") or "soc_logs"

        # Message construction
        # Since 'message' field is often missing, we construct one.
        msg = item.get("message")
        if not msg:
            src_ip = item.get("source", {}).get("ip", "")
            dst_ip = item.get("destination", {}).get("ip", "")
            dst_port = item.get("destination", {}).get("port", "")
            if src_ip and dst_ip:
                msg = f"{event_type} from {src_ip} to {dst_ip}:{dst_port}"
            else:
                msg = f"{event_type} on {host}"

        # Generate ID
        # Use existing _id if possible, but we need a string for our system consistency if it relies on it.
        # The new data has {"_id": {"$oid": "..."}}. We can use the OID string.
        oid = item.get("_id", {}).get("$oid")
        if not oid:
            # Fallback
            key = f"{host}_{ts_formatted}_{software}_{event_type}"
            oid = md5(key.encode()).hexdigest()

        return {
            "_id": oid,
            "timestamp": ts_formatted, # Keep as string for consistency with old schema, or datetime object? 
                                       # Old schema used string in normalized dict but inserted as datetime object in DB?
                                       # Let's check old insert_to_mongo.py: 
                                       # normalized["timestamp"] = datetime.strptime(normalized["timestamp"], "%Y-%m-%d %H:%M:%S")
                                       # So it inserts datetime object.
            "host": host,
            "os": os_name,
            "software": software,
            "version": version,
            "event_type": event_type,
            "message": msg,
            "source": source_type
        }
    except Exception as e:
        print(f"[WARN] Normalization error: {e}")
        return None

# ------------------------------------------------------------
# STREAMING PARSER
# ------------------------------------------------------------
def stream_json_array(filepath):
    """
    Generator that yields JSON objects from a large JSON array file.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        # Skip until '['
        while True:
            char = f.read(1)
            if not char: return
            if char == '[': break
        
        decoder = json.JSONDecoder()
        buffer = ""
        
        while True:
            chunk = f.read(4096)
            if not chunk:
                # Process remaining buffer
                if buffer.strip():
                    try:
                        obj, idx = decoder.raw_decode(buffer.strip())
                        yield obj
                    except:
                        pass
                break
            
            buffer += chunk
            
            # Try to decode objects from buffer
            while True:
                try:
                    # Skip whitespace/commas
                    buffer = buffer.lstrip()
                    if buffer.startswith(','):
                        buffer = buffer[1:].lstrip()
                    if buffer.startswith(']'):
                        return # End of array
                    
                    obj, idx = decoder.raw_decode(buffer)
                    yield obj
                    buffer = buffer[idx:]
                except json.JSONDecodeError:
                    # Need more data
                    break

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main(payload=None):
    print(f"[+] Starting ingestion from {DATA_FILE}")
    
    if not os.path.exists(DATA_FILE):
        print(f"[ERR] File not found: {DATA_FILE}")
        return {"status": "error", "message": "file_not_found"}

    # Clear existing data
    print("[+] Clearing existing logs and matches...")
    collection.delete_many({})
    matches_collection.delete_many({})
    db["alerts"].delete_many({})

    count = 0
    inserted = 0
    batch = []
    BATCH_SIZE = 1000

    try:
        for item in stream_json_array(DATA_FILE):
            count += 1
            norm = normalize_soc_log(item)
            if norm:
                # Convert timestamp to datetime object for MongoDB
                try:
                    norm["timestamp"] = datetime.strptime(norm["timestamp"], "%Y-%m-%d %H:%M:%S")
                except:
                    pass # Keep as string if conversion fails (shouldn't happen due to normalize logic)
                
                batch.append(norm)

            if len(batch) >= BATCH_SIZE:
                try:
                    collection.insert_many(batch, ordered=False)
                    inserted += len(batch)
                    print(f"[+] Inserted {inserted} logs...", end='\r')
                except Exception as e:
                    print(f"[WARN] Batch insert error: {e}")
                batch = []

        # Insert remaining
        if batch:
            try:
                collection.insert_many(batch, ordered=False)
                inserted += len(batch)
            except Exception as e:
                print(f"[WARN] Final batch insert error: {e}")

        print(f"\n[✓] Ingestion complete. Processed: {count}, Inserted: {inserted}")
        return {"status": "completed", "processed": count, "inserted": inserted}

    except Exception as e:
        print(f"\n[ERR] Ingestion failed: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    main()
=======
from normalize import normalize_log
from validate import validate_log

# ------------------------------------------------------------
# 1. CONNECT TO MONGO DB (Your credentials)
# ------------------------------------------------------------

client = MongoClient("mongodb://admin:admin123@localhost:27017/?authSource=admin")
db = client["vulnerability_logs"]
collection = db["normalized_logs"]

# ------------------------------------------------------------
# 2. UNIQUE ID GENERATOR (Duplicate Checker)
# ------------------------------------------------------------

def generate_log_id(log):
    """
    Unique key = host + timestamp + software
    Ensures same log is never inserted twice.
    """
    key = f"{log.get('host','')}_{log.get('timestamp','')}_{log.get('software','')}"
    return md5(key.encode()).hexdigest()


# ------------------------------------------------------------
# 3. INSERT FUNCTION
# ------------------------------------------------------------

def insert_log(normalized):
    try:
        # Validate log
        validate_log(normalized)

        # Unique ID for duplicate prevention
        log_id = generate_log_id(normalized)

        # Skip if duplicate exists
        if collection.find_one({"_id": log_id}):
            print(f"[SKIP] Duplicate log for host={normalized['host']} at {normalized['timestamp']}")
            return

        # Convert timestamp string → datetime object
        normalized["timestamp"] = datetime.strptime(normalized["timestamp"], "%Y-%m-%d %H:%M:%S")

        # Add _id field
        normalized["_id"] = log_id

        # Insert
        collection.insert_one(normalized)
        print(f"[OK] Inserted log: {log_id}")

    except Exception as e:
        with open("error_log.txt", "a", encoding="utf-8") as err:
            err.write(f"{datetime.now()} | {str(e)} | {json.dumps(normalized)}\n")
        print(f"[ERR] {e}")


# ------------------------------------------------------------
# 4. PROCESS PARSED JSONL FILE
# ------------------------------------------------------------

def insert_from_parsed_file(input_jsonl):
    print(f"\n[+] Inserting logs from: {input_jsonl}")

    count = 0
    inserted = 0
    skipped = 0

    with open(input_jsonl, "r", encoding="utf-8") as infile:
        for line in infile:
            count += 1

            try:
                parsed = json.loads(line.strip())
                normalized = normalize_log(parsed)
                result = insert_log(normalized)

                if result is None:
                    skipped += 1
                else:
                    inserted += 1
            except Exception as e:
                with open("error_log.txt", "a", encoding="utf-8") as err:
                    err.write(f"{datetime.now()} | Parse Error: {str(e)} | {line}\n")
                print(f"[ERR] {e}")

    print(f"\n[✓] Total parsed lines: {count}")
    print(f"[✓] Inserted: {inserted}")
    print(f"[✓] Skipped: {skipped}")
    print("[✓] Errors logged to error_log.txt")


# ------------------------------------------------------------
# 5. MAIN — INSERT ALL PARSED OUTPUT FILES
# ------------------------------------------------------------

if __name__ == "__main__":
    files = [
        "parser_engine/out_syslog.jsonl",
        "parser_engine/out_auth.jsonl",
        "parser_engine/out_sysmon.jsonl",
        "parser_engine/out_security.jsonl",
        "parser_engine/out_http.jsonl",
        "parser_engine/out_dns.jsonl",
        "parser_engine/out_elastic.jsonl",
    ]

    for f in files:
        try:
            insert_from_parsed_file(f)
        except FileNotFoundError:
            print(f"[WARN] File not found: {f}")
>>>>>>> cd260ba9258ba3c2c7ffb1588424565f3f1c9eae
