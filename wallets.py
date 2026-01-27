import json
import os
import tempfile
import shutil
import fcntl
import time

WALLET_FILE = "wallets.json"

def load_wallets():
    """Load all wallets from file with retry logic."""
    if not os.path.exists(WALLET_FILE):
        return {}
    
    for attempt in range(3):
        try:
            with open(WALLET_FILE, "r") as f:
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
            print(f"Error loading wallets: {e}")
            return {}
    return {}

def save_wallets(data):
    """Save wallets to file atomically."""
    try:
        fd, temp_path = tempfile.mkstemp(suffix=".json", dir=os.path.dirname(WALLET_FILE) or ".")
        try:
            with os.fdopen(fd, "w") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            shutil.move(temp_path, WALLET_FILE)
        except Exception as e:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
    except (IOError, OSError) as e:
        print(f"Error saving wallets: {e}")

def add_wallet(user_id, address, label):
    """Add a wallet for a user. Returns True if successful, False if duplicate."""
    data = load_wallets()
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = []

    # Prevent duplicates
    for w in data[user_id]:
        if w["address"] == address:
            return False

    data[user_id].append({
        "address": address,
        "label": label
    })

    save_wallets(data)
    return True

def get_wallets(user_id):
    """Get all wallets for a user."""
    data = load_wallets()
    return data.get(str(user_id), [])

def remove_wallet(user_id, address):
    """Remove a wallet for a user."""
    data = load_wallets()
    user_id = str(user_id)

    if user_id in data:
        data[user_id] = [w for w in data[user_id] if w["address"] != address]
        save_wallets(data)
        return True

    return False
