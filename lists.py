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

def get_user_lists(user_id):
    """Get all lists for a user as a list of dicts."""
    data = load_lists()
    uid = str(user_id)
    
    if uid not in data:
        return []
    
    # Convert dict to list format for UI
    result = []
    for name, coins in data[uid].items():
        result.append({
            "name": name,
            "coins": coins
        })
    
    return result


def create_list(user_id, name, description="", meta_alerts=None):
    """
    Create a new list. Returns True if successful, False if already exists.
    
    Args:
        meta_alerts: Optional dict with {"n_pumping": N, "total_mc": threshold, "avg_pct": threshold}
    """
    data = load_lists()
    uid = str(user_id)

    if uid not in data:
        data[uid] = {}

    if name in data[uid]:
        return False  # List already exists

    data[uid][name] = {
        "coins": [],
        "description": description,
        "meta_alerts": meta_alerts or {},
        "meta_triggered": {}
    }
    save_lists(data)
    return True

def add_coin_to_list(user_id, list_name, ca):
    """Add a coin (CA) to a list."""
    data = load_lists()
    uid = str(user_id)

    if uid not in data or list_name not in data[uid]:
        return False  # List doesn't exist

    # Support both old format (list) and new format (dict with "coins")
    list_data = data[uid][list_name]
    if isinstance(list_data, dict):
        # New format
        if ca not in list_data.get("coins", []):
            list_data.setdefault("coins", []).append(ca)
    else:
        # Old format (list)
        if ca not in list_data:
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
        list_data = data[uid][list_name]
        # Support both old format (list) and new format (dict with "coins")
        if isinstance(list_data, dict):
            # New format
            if ca in list_data.get("coins", []):
                list_data["coins"].remove(ca)
        else:
            # Old format (list)
            if ca in list_data:
                data[uid][list_name].remove(ca)
        save_lists(data)
        return True

    return False

def delete_list(user_id, list_index):
    """Delete a list by index."""
    data = load_lists()
    uid = str(user_id)

    if uid not in data:
        return False
    
    # Convert to list to get by index
    list_names = list(data[uid].keys())
    
    if list_index >= len(list_names):
        return False
    
    list_name = list_names[list_index]
    data[uid].pop(list_name, None)  # Safe deletion - prevents KeyError
    save_lists(data)
    return True
