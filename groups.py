#!/usr/bin/env python3
"""
Groups storage module

Groups are separate from users.
Each group has:
- coins: list of tracked coins
- admins: list of admin user IDs
"""

import json
import os
import tempfile
import shutil
import fcntl
import time

GROUPS_FILE = "groups.json"

def load_groups():
    """Load groups data from file with retry logic."""
    if not os.path.exists(GROUPS_FILE):
        return {}
    
    for attempt in range(3):
        try:
            with open(GROUPS_FILE, "r") as f:
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
            print(f"Error loading groups: {e}")
            return {}
    return {}

def save_groups(data):
    """Save groups data atomically."""
    try:
        fd, temp_path = tempfile.mkstemp(suffix=".json", dir=os.path.dirname(GROUPS_FILE) or ".")
        try:
            with os.fdopen(fd, "w") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            shutil.move(temp_path, GROUPS_FILE)
        except Exception as e:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
    except (IOError, OSError) as e:
        print(f"Error saving groups: {e}")

def create_group(group_id, admin_id):
    """Initialize a new group with admin."""
    data = load_groups()
    group_id = str(group_id)
    
    if group_id not in data:
        data[group_id] = {
            "coins": [],
            "admins": [admin_id]
        }
        save_groups(data)
        return True
    
    return False

def add_group_admin(group_id, admin_id):
    """Add admin to group."""
    data = load_groups()
    group_id = str(group_id)
    
    if group_id not in data:
        data[group_id] = {"coins": [], "admins": []}
    
    if admin_id not in data[group_id]["admins"]:
        data[group_id]["admins"].append(admin_id)
        save_groups(data)
        return True
    
    return False

def get_group_admins(group_id):
    """Get list of admin IDs for a group."""
    data = load_groups()
    group_id = str(group_id)
    
    if group_id not in data:
        return []
    
    return data[group_id].get("admins", [])

def add_coin_to_group(group_id, ca, alerts, start_mc):
    """Add a coin to group tracking."""
    data = load_groups()
    group_id = str(group_id)
    
    if group_id not in data:
        data[group_id] = {"coins": [], "admins": []}
    
    # Check if coin already tracked
    for coin in data[group_id]["coins"]:
        if coin["ca"] == ca:
            return False  # Already tracking
    
    data[group_id]["coins"].append({
        "ca": ca,
        "alerts": alerts,
        "start_mc": start_mc,
        "ath_mc": start_mc,
        "low_mc": start_mc,
        "triggered": {}  # Initialize triggered state
    })
    
    save_groups(data)
    return True

def get_group_coins(group_id):
    """Get all tracked coins for a group."""
    data = load_groups()
    group_id = str(group_id)
    
    if group_id not in data:
        return []
    
    return data[group_id].get("coins", [])

def remove_coin_from_group(group_id, ca):
    """Remove a coin from group tracking."""
    data = load_groups()
    group_id = str(group_id)
    
    if group_id not in data:
        return False
    
    original_count = len(data[group_id]["coins"])
    data[group_id]["coins"] = [
        coin for coin in data[group_id]["coins"]
        if coin["ca"] != ca
    ]
    
    if len(data[group_id]["coins"]) < original_count:
        save_groups(data)
        return True
    
    return False

def update_group_coin_alerts(group_id, ca, alerts):
    """Update alerts for a coin in a group."""
    data = load_groups()
    group_id = str(group_id)
    
    if group_id not in data:
        return False
    
    for coin in data[group_id]["coins"]:
        if coin["ca"] == ca:
            coin["alerts"] = alerts
            save_groups(data)
            return True
    
    return False

def update_group_coin_triggered(group_id, ca, triggered):
    """Update triggered state for a coin in a group."""
    data = load_groups()
    group_id = str(group_id)
    
    if group_id not in data:
        return False
    
    for coin in data[group_id]["coins"]:
        if coin["ca"] == ca:
            coin["triggered"] = triggered
            save_groups(data)
            return True
    
    return False

def update_group_coin_history(group_id, ca, mc, ath, low):
    """Update price history for a coin in a group."""
    data = load_groups()
    group_id = str(group_id)
    
    if group_id not in data:
        return
    
    for coin in data[group_id]["coins"]:
        if coin["ca"] == ca:
            coin["ath_mc"] = max(coin.get("ath_mc", mc), ath)
            coin["low_mc"] = min(coin.get("low_mc", mc), low)
            save_groups(data)
            return

def get_all_group_ids():
    """Get all active group IDs."""
    data = load_groups()
    return list(data.keys())

def delete_group(group_id):
    """Delete a group (when bot is removed)."""
    data = load_groups()
    group_id = str(group_id)
    
    if group_id in data:
        del data[group_id]
        save_groups(data)
        return True
    
    return False
