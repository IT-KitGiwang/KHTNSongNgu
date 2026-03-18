"""
JSON-based database replacement for SQLAlchemy.
Stores all user data in data/users.json
Fixed: atomic read-modify-write operations to prevent JSON corruption.
"""
import json
import os
import threading
from werkzeug.security import generate_password_hash, check_password_hash

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
_lock = threading.Lock()

def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def _read_users_unsafe():
    """Read users WITHOUT acquiring lock (caller must hold lock)."""
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def _write_users_unsafe(users):
    """Write users WITHOUT acquiring lock (caller must hold lock)."""
    # Write to temp file first, then rename for atomicity
    tmp_file = USERS_FILE + '.tmp'
    with open(tmp_file, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    os.replace(tmp_file, USERS_FILE)

def load_users():
    _ensure_data_dir()
    with _lock:
        return _read_users_unsafe()

def save_users(users):
    _ensure_data_dir()
    with _lock:
        _write_users_unsafe(users)

def _next_id(users):
    if not users:
        return 1
    return max(u['id'] for u in users) + 1

def _default_user(id, tendangnhap, matkhau_hash, tenhocsinh=''):
    return {
        'id': id,
        'tendangnhap': tendangnhap,
        'matkhau': matkhau_hash,
        'tenhocsinh': tenhocsinh,
        'nangluc': 'TB', 'lichsu': '', 'lydo': '',
        'lichsutoan': '', 'lichsuly': '', 'lichsuhoa': '', 'lichsusinh': '',
        'nangluctoan': 'TB', 'nanglucly': 'TB', 'nangluchoa': 'TB', 'nanglucsinh': 'TB',
        'lydotoan': '', 'lydoly': '', 'lydohoa': '', 'lydosinh': '',
        'socautoan': 0, 'socauly': 0, 'socauhoa': 0, 'socausinh': 0
    }

# --- CRUD Operations (all atomic) ---

def get_user_by_id(user_id):
    users = load_users()
    for u in users:
        if u['id'] == user_id:
            return u
    return None

def get_user_by_username(tendangnhap):
    users = load_users()
    for u in users:
        if u['tendangnhap'] == tendangnhap:
            return u
    return None

def create_user(tendangnhap, matkhau_hash, tenhocsinh=''):
    """Atomic create: read + append + write in single lock."""
    _ensure_data_dir()
    with _lock:
        users = _read_users_unsafe()
        # Check for duplicate username
        for u in users:
            if u['tendangnhap'] == tendangnhap:
                raise ValueError(f"Username '{tendangnhap}' already exists")
        new_id = _next_id(users)
        user = _default_user(new_id, tendangnhap, matkhau_hash, tenhocsinh)
        users.append(user)
        _write_users_unsafe(users)
        return user

def update_user(user_id, updates: dict):
    """Atomic update: read + modify + write in single lock."""
    _ensure_data_dir()
    with _lock:
        users = _read_users_unsafe()
        for u in users:
            if u['id'] == user_id:
                u.update(updates)
                _write_users_unsafe(users)
                return u
    return None

def delete_user(user_id):
    _ensure_data_dir()
    with _lock:
        users = _read_users_unsafe()
        users = [u for u in users if u['id'] != user_id]
        _write_users_unsafe(users)

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

# Initialize on import
_ensure_data_dir()
try:
    print("[OK] JSON Database initialized at:", USERS_FILE)
except UnicodeEncodeError:
    print("[OK] JSON Database initialized.")
