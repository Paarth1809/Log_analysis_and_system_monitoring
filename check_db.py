from pymongo import MongoClient
import json

client = MongoClient('mongodb://admin:admin123@localhost:27017/?authSource=admin')
db = client['vulnerability_logs']
matches = db['vuln_matches']

# Get one record to see all fields
sample = matches.find_one()
if sample:
    print("Sample record fields:")
    for key, value in sample.items():
        if isinstance(value, str) and len(value) > 100:
            value = value[:100] + "..."
        print(f"  {key}: {value}")
    
    # Try to find host field variations
    print("\n\nChecking for host-related fields:")
    for key in sample.keys():
        if 'host' in key.lower():
            print(f"  Found: {key} = {sample[key]}")
else:
    print("No records found in vuln_matches collection")

# Check what distinct values exist for common host field names
print("\n\nTrying different field names:")
for field_name in ['host', 'hostname', 'Host', 'detected_on', 'source_host']:
    try:
        values = matches.distinct(field_name)
        if values:
            print(f"  {field_name}: {values[:5]}")  # Show first 5
    except Exception as e:
        pass
