"""
MongoDB-based database module.
Drop-in replacement for the previous JSON file-based storage.
All functions maintain the same interface so app.py does NOT need changes.

Requires: pymongo, python-dotenv
Environment variable: MONGODB_URI (MongoDB Atlas connection string)
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

load_dotenv()

# ================== MONGODB CONNECTION ==================
MONGODB_URI = os.getenv("MONGODB_URI", "")
DB_NAME = os.getenv("MONGODB_DB_NAME", "khtnsonggu")

if not MONGODB_URI:
    raise RuntimeError(
        "[ERROR] MONGODB_URI is not set! "
        "Please add MONGODB_URI to your .env file.\n"
        "Example: MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority"
    )

_client = MongoClient(MONGODB_URI)
_db = _client[DB_NAME]
_users_col = _db["users"]

# Ensure unique index on username
_users_col.create_index("tendangnhap", unique=True)

# ================== HELPER ==================

def _next_id():
    """Auto-increment ID: find the max id and add 1."""
    last = _users_col.find_one(sort=[("id", -1)])
    if last:
        return last["id"] + 1
    return 1


def _default_user(user_id, tendangnhap, matkhau_hash, tenhocsinh=''):
    """Return a default user document (same schema as before)."""
    return {
        'id': user_id,
        'tendangnhap': tendangnhap,
        'matkhau': matkhau_hash,
        'tenhocsinh': tenhocsinh,
        'nangluc': 'TB', 'lichsu': '', 'lydo': '',
        'lichsutoan': '', 'lichsuly': '', 'lichsuhoa': '', 'lichsusinh': '',
        'nangluctoan': 'TB', 'nanglucly': 'TB', 'nangluchoa': 'TB', 'nanglucsinh': 'TB',
        'lydotoan': '', 'lydoly': '', 'lydohoa': '', 'lydosinh': '',
        'socautoan': 0, 'socauly': 0, 'socauhoa': 0, 'socausinh': 0
    }


def _doc_to_dict(doc):
    """Convert a MongoDB document to a plain dict (remove _id)."""
    if doc is None:
        return None
    d = dict(doc)
    d.pop('_id', None)
    return d


# ================== CRUD Operations ==================

def load_users():
    """Return all users as a list of dicts."""
    return [_doc_to_dict(doc) for doc in _users_col.find()]


def save_users(users):
    """Bulk replace all users (used for migration/seeding only)."""
    _users_col.delete_many({})
    if users:
        _users_col.insert_many(users)


def get_user_by_id(user_id):
    doc = _users_col.find_one({"id": user_id})
    return _doc_to_dict(doc)


def get_user_by_username(tendangnhap):
    doc = _users_col.find_one({"tendangnhap": tendangnhap})
    return _doc_to_dict(doc)


def create_user(tendangnhap, matkhau_hash, tenhocsinh=''):
    """Create a new user. Raises ValueError if username already exists."""
    new_id = _next_id()
    user = _default_user(new_id, tendangnhap, matkhau_hash, tenhocsinh)
    try:
        _users_col.insert_one(user)
    except DuplicateKeyError:
        raise ValueError(f"Username '{tendangnhap}' already exists")
    return _doc_to_dict(_users_col.find_one({"id": new_id}))


def update_user(user_id, updates: dict):
    """Update a user by id. Returns updated user dict or None."""
    result = _users_col.find_one_and_update(
        {"id": user_id},
        {"$set": updates},
        return_document=True  # return the updated document
    )
    return _doc_to_dict(result)


def delete_user(user_id):
    _users_col.delete_one({"id": user_id})


def get_all_users():
    return load_users()


def reset_user_data(user_id):
    return update_user(user_id, {
        'lichsutoan': '', 'lichsuly': '', 'lichsuhoa': '', 'lichsusinh': '',
        'nangluctoan': 'TB', 'nanglucly': 'TB', 'nangluchoa': 'TB', 'nanglucsinh': 'TB',
        'lydotoan': '', 'lydoly': '', 'lydohoa': '', 'lydosinh': '',
        'socautoan': 0, 'socauly': 0, 'socauhoa': 0, 'socausinh': 0,
        'nangluc': 'TB', 'lichsu': '', 'lydo': ''
    })


# ================== INITIALIZATION ==================
try:
    # Test connection
    _client.admin.command('ping')
    count = _users_col.count_documents({})
    print(f"[OK] MongoDB connected successfully! Database: {DB_NAME}, Users: {count}")
except Exception as e:
    print(f"[WARNING] MongoDB connection test failed: {e}")
    print("         The app will retry on first request.")
