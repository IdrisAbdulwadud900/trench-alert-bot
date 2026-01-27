import json
import os
import tempfile
import shutil
import fcntl
import time

DATA_FILE = "data.json"

def load_data():
    """Load data with retry logic for concurrent access."""
    if not os.path.exists(DATA_FILE):
        return {}
    
    for attempt in range(3):
        try:
            with open(DATA_FILE, "r") as f:
                # Acquire shared lock for reading
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                    return data
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except (json.JSONDecodeError, IOError) as e:
            if attempt < 2:
                time.sleep(0.1)  # Brief retry delay
                continue
            print(f"Error loading data after retries: {e}")
            return {}
    return {}

def save_data(data):
    """Save data atomically with temp file to prevent corruption."""
    try:
        # Write to temp file first
        fd, temp_path = tempfile.mkstemp(suffix=".json", dir=os.path.dirname(DATA_FILE) or ".")
        try:
            with os.fdopen(fd, "w") as f:
                # Acquire exclusive lock
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())  # Ensure written to disk
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            
            # Atomic rename
            shutil.move(temp_path, DATA_FILE)
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
    except (IOError, OSError) as e:
        print(f"Error saving data: {e}")

def get_user_profile(user_id: str) -> dict:
    """Get user profile settings."""
    data = load_data()
    user_id = str(user_id)
    
    if user_id not in data:
        return {"mode": "aggressive"}  # Default mode
    
    return data.get(user_id, {}).get("profile", {"mode": "aggressive"})

def set_user_profile(user_id: str, profile: dict) -> None:
    """Update user profile settings."""
    data = load_data()
    user_id = str(user_id)
    
    if user_id not in data:
        data[user_id] = {}
    
    data[user_id]["profile"] = profile
    save_data(data)

def add_coin(user_id, coin_data):
    data = load_data()
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {"coins": [], "profile": {"mode": "aggressive"}}

    # Ensure coins list exists
    if "coins" not in data[user_id]:
        data[user_id]["coins"] = []
    
    # Initialize intelligence fields
    if "low_mc" not in coin_data:
        coin_data["low_mc"] = coin_data.get("start_mc", 0)
    if "ath_mc" not in coin_data:
        coin_data["ath_mc"] = coin_data.get("start_mc", 0)
    if "history" not in coin_data:
        coin_data["history"] = []

    data[user_id]["coins"].append(coin_data)
    save_data(data)

def get_all_coins():
    """Get all coins organized by user."""
    data = load_data()
    
    # Legacy support: if data has coins at root level, restructure it
    restructured = {}
    for key, value in data.items():
        if isinstance(value, list):  # Old format (list of coins)
            restructured[key] = {"coins": value, "profile": {"mode": "aggressive"}}
        elif isinstance(value, dict):  # New format
            if "coins" not in value:
                value["coins"] = []
            if "profile" not in value:
                value["profile"] = {"mode": "aggressive"}
            restructured[key] = value
    
    return restructured

def get_user_coins(user_id: str) -> list:
    """Get coins for a specific user."""
    data = load_data()
    user_id = str(user_id)
    
    if user_id not in data:
        return []
    
    user_data = data[user_id]
    
    # Handle both old and new format
    if isinstance(user_data, list):
        return user_data
    elif isinstance(user_data, dict):
        return user_data.get("coins", [])
    
    return []

def remove_coin(user_id, ca):
    data = load_data()
    user_id = str(user_id)

    if user_id not in data:
        return False

    user_data = data[user_id]
    
    # Handle both formats
    if isinstance(user_data, list):
        before = len(user_data)
        data[user_id] = [c for c in user_data if c.get("ca") != ca]
        if len(data[user_id]) == 0:
            data.pop(user_id)
        save_data(data)
        return len(data.get(user_id, [])) < before
    
    elif isinstance(user_data, dict):
        coins = user_data.get("coins", [])
        before = len(coins)
        user_data["coins"] = [c for c in coins if c.get("ca") != ca]
        
        if len(user_data["coins"]) == 0:
            data.pop(user_id)
        
        save_data(data)
        return len(data.get(user_id, {}).get("coins", [])) < before
    
    return False

# ========================
# WALLET TRACKING
# ========================

def add_wallet(user_id, wallet_address: str, label: str = None) -> bool:
    """Add a wallet to track."""
    data = load_data()
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {"coins": [], "profile": {"mode": "aggressive"}}
    
    if "wallets" not in data[user_id]:
        data[user_id]["wallets"] = []
    
    # Check if wallet already exists
    for wallet in data[user_id]["wallets"]:
        if wallet["address"].lower() == wallet_address.lower():
            return False  # Already exists
    
    data[user_id]["wallets"].append({
        "address": wallet_address,
        "label": label or f"Wallet {len(data[user_id]['wallets']) + 1}",
        "added_at": None
    })
    save_data(data)
    return True

def get_user_wallets(user_id: str) -> list:
    """Get all wallets for a user."""
    data = load_data()
    user_id = str(user_id)
    
    if user_id not in data:
        return []
    
    return data[user_id].get("wallets", [])

def remove_wallet(user_id, wallet_address: str) -> bool:
    """Remove a wallet."""
    data = load_data()
    user_id = str(user_id)

    if user_id not in data:
        return False
    
    wallets = data[user_id].get("wallets", [])
    before = len(wallets)
    data[user_id]["wallets"] = [w for w in wallets if w["address"].lower() != wallet_address.lower()]
    save_data(data)
    return len(data[user_id]["wallets"]) < before

# ========================
# LISTS & NARRATIVES
# ========================

def create_list(user_id, list_name: str) -> bool:
    """Create a new list."""
    data = load_data()
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {"coins": [], "profile": {"mode": "aggressive"}}
    
    if "lists" not in data[user_id]:
        data[user_id]["lists"] = []
    
    # Check if list already exists
    for lst in data[user_id]["lists"]:
        if lst["name"].lower() == list_name.lower():
            return False  # Already exists
    
    data[user_id]["lists"].append({
        "name": list_name,
        "coins": []
    })
    save_data(data)
    return True

def add_coin_to_list(user_id, list_name: str, ca: str) -> bool:
    """Add a coin to a list."""
    data = load_data()
    user_id = str(user_id)

    if user_id not in data:
        return False
    
    lists = data[user_id].get("lists", [])
    for lst in lists:
        if lst["name"].lower() == list_name.lower():
            if ca not in lst["coins"]:
                lst["coins"].append(ca)
                save_data(data)
                return True
    
    return False

def get_user_lists(user_id: str) -> list:
    """Get all lists for a user."""
    data = load_data()
    user_id = str(user_id)
    
    if user_id not in data:
        return []
    
    return data[user_id].get("lists", [])

def remove_list(user_id, list_name: str) -> bool:
    """Delete a list."""
    data = load_data()
    user_id = str(user_id)

    if user_id not in data:
        return False
    
    lists = data[user_id].get("lists", [])
    before = len(lists)
    data[user_id]["lists"] = [l for l in lists if l["name"].lower() != list_name.lower()]
    save_data(data)
    return len(data[user_id]["lists"]) < before
