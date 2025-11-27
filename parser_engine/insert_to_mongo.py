import json
from datetime import datetime
from pymongo import MongoClient
from hashlib import md5

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
