import json
import os
import tempfile
import shutil
import fcntl
import time

LIST_FILE = "lists.json"

def load_lists():
    """Load all lists from file with retry logic."""
    if not os.path.exists(LIST_FILE):
        return {}
    
    for attempt in range(3):
        try:
            with open(LIST_FILE, "r") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                    return data
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except (json.JSONDecodeError, IOError) as e:
            if attempt < 2:
                time.sleep(0.1)
                continue
            print(f"Error loading lists: {e}")
            return {}
    return {}

def save_lists(data):
    """Save lists to file atomically."""
    try:
        fd, temp_path = tempfile.mkstemp(suffix=".json", dir=os.path.dirname(LIST_FILE) or ".")
        try:
            with os.fdopen(fd, "w") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            shutil.move(temp_path, LIST_FILE)
        except Exception as e:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
    except (IOError, OSError) as e:
        print(f"Error saving lists: {e}")

def create_list(user_id, name):
    """Create a new list. Returns True if successful, False if already exists."""
    data = load_lists()
    uid = str(user_id)

    if uid not in data:
        data[uid] = {}

    if name in data[uid]:
        return False  # List already exists

    data[uid][name] = []
    save_lists(data)
    return True

def add_coin_to_list(user_id, list_name, ca):
    """Add a coin (CA) to a list."""
    data = load_lists()
    uid = str(user_id)

    if uid not in data or list_name not in data[uid]:
        return False  # List doesn't exist

    if ca not in data[uid][list_name]:
        data[uid][list_name].append(ca)

    save_lists(data)
    return True

def get_lists(user_id):
    """Get all lists for a user."""
    data = load_lists()
    return data.get(str(user_id), {})

def remove_coin_from_list(user_id, list_name, ca):
    """Remove a coin from a list."""
    data = load_lists()
    uid = str(user_id)

    if uid in data and list_name in data[uid]:
        if ca in data[uid][list_name]:
            data[uid][list_name].remove(ca)
        save_lists(data)
        return True

    return False

def delete_list(user_id, list_name):
    """Delete an entire list."""
    data = load_lists()
    uid = str(user_id)

    if uid in data and list_name in data[uid]:
        del data[uid][list_name]
        save_lists(data)
        return True

    return False
