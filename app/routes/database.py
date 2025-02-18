from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
users_collection = db["users"]

# Sample users to insert
users = [
    {"username": "Alice", "role": "admin", "reservations": []},
    {"username": "Bob", "role": "user", "reservations": []},
    {"username": "Charlie", "role": "user", "reservations": []},
    {"username": "David", "role": "moderator", "reservations": []},
    {"username": "Eve", "role": "user", "reservations": []}
]

# Insert users only if they don't exist
for user in users:
    if not users_collection.find_one({"username": user["username"]}):  # Check if user exists
        users_collection.insert_one(user)
        print(f"✅ Inserted: {user['username']}")
    else:
        print(f"⚠️ Skipped (Already Exists): {user['username']}")

print("🎉 Database seeding completed!")
