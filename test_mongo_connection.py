from pymongo import MongoClient

try:
    client = MongoClient("mongodb://admin:admin123@localhost:27017/?authSource=admin")
    db = client["demo_test_db"]
    collection = db["demo_collection"]

    result = collection.insert_one({"message": "MongoDB connection successful"})
    print("Connected successfully!")
    print("Inserted document ID:", result.inserted_id)

except Exception as e:
    print("Connection error:", e)
