from parser_engine.insert_to_mongo import main as ingest_main

def main(payload=None):
    print("[INFO] Starting Raw Log Parser & Ingestion...")
    return ingest_main(payload)

if __name__ == "__main__":
    main()
