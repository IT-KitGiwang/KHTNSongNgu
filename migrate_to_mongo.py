"""
Migration script: Import data from data/users.json into MongoDB Atlas.

Usage:
    1. Set MONGODB_URI in .env
    2. Run: python migrate_to_mongo.py

This script will:
    - Read all users from data/users.json
    - Insert them into MongoDB Atlas (collection: users, database: khtnsonggu)
    - Skip users that already exist (by tendangnhap)
"""
import json
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

load_dotenv()

# Config
MONGODB_URI = os.getenv("MONGODB_URI", "")
DB_NAME = os.getenv("MONGODB_DB_NAME", "khtnsonggu")
USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'users.json')

if not MONGODB_URI:
    print("[ERROR] MONGODB_URI is not set in .env file!")
    print("Example: MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority")
    exit(1)

# Connect to MongoDB
print(f"[INFO] Connecting to MongoDB Atlas...")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
users_col = db["users"]

# Test connection
try:
    client.admin.command('ping')
    print(f"[OK] Connected to MongoDB Atlas successfully!")
except Exception as e:
    print(f"[ERROR] Cannot connect to MongoDB: {e}")
    exit(1)

# Ensure unique index
users_col.create_index("tendangnhap", unique=True)

# Read JSON data
if not os.path.exists(USERS_FILE):
    print(f"[ERROR] File not found: {USERS_FILE}")
    exit(1)

with open(USERS_FILE, 'r', encoding='utf-8') as f:
    users = json.load(f)

print(f"[INFO] Found {len(users)} users in {USERS_FILE}")

# Check existing data in MongoDB
existing_count = users_col.count_documents({})
if existing_count > 0:
    print(f"[WARNING] MongoDB already has {existing_count} users.")
    answer = input("Do you want to DELETE all existing data and re-import? (yes/no): ").strip().lower()
    if answer == 'yes':
        users_col.delete_many({})
        print(f"[INFO] Deleted all existing users from MongoDB.")
    else:
        print(f"[INFO] Will skip users that already exist (by tendangnhap).")

# Insert users
inserted = 0
skipped = 0
errors = 0

for user in users:
    try:
        # Remove any _id field if present (let MongoDB generate it)
        user.pop('_id', None)
        users_col.insert_one(user)
        inserted += 1
    except DuplicateKeyError:
        skipped += 1
    except Exception as e:
        errors += 1
        print(f"  [ERROR] Failed to insert user '{user.get('tendangnhap', '?')}': {e}")

print(f"\n{'='*50}")
print(f"Migration complete!")
print(f"  Inserted: {inserted}")
print(f"  Skipped (duplicate): {skipped}")
print(f"  Errors: {errors}")
print(f"  Total in MongoDB: {users_col.count_documents({})}")
print(f"{'='*50}")
