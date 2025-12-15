from pymongo import MongoClient

# Test both URIs
uris = [
    "mongodb://admin:admin123@localhost:27017/?authSource=admin",
    "mongodb://localhost:27017/"
]

for uri in uris:
    print(f"\n[+] Testing URI: {uri}")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Force connection
        client.admin.command('ping')
        print("  ✓ Connection successful")
        
        # List databases
        dbs = client.list_database_names()
        print(f"  Databases: {dbs}")
        
        # Check vulnerability_logs
        if 'vulnerability_logs' in dbs:
            db = client['vulnerability_logs']
            collections = db.list_collection_names()
            print(f"  Collections in vulnerability_logs: {collections}")
            
            for col_name in ['vuln_matches', 'alerts', 'normalized_logs']:
                if col_name in collections:
                    count = db[col_name].count_documents({})
                    print(f"    {col_name}: {count} documents")
                    
    except Exception as e:
        print(f"  ✗ Error: {e}")
