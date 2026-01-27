#!/usr/bin/env python3
"""
User/Group Settings Management

Handles per-chat preferences:
- Alert mode (loud/silent)
- Future: notification preferences, display settings, etc.
"""

import json
import os
import fcntl

SETTINGS_FILE = "settings.json"


def load_settings():
    """Load settings from JSON file."""
    if not os.path.exists(SETTINGS_FILE):
        return {}
    
    with open(SETTINGS_FILE, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        try:
            return json.load(f)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def save_settings(data):
    """Save settings to JSON file with atomic write."""
    temp_file = SETTINGS_FILE + ".tmp"
    
    with open(temp_file, "w") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            json.dump(data, f, indent=2)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    os.replace(temp_file, SETTINGS_FILE)


def get_alert_mode(chat_id):
    """
    Get alert mode for a chat.
    
    Returns:
        "loud" - Alerts play sound (default)
        "silent" - Alerts delivered quietly
    """
    data = load_settings()
    chat_id = str(chat_id)
    
    # Default = loud (professional behavior)
    return data.get(chat_id, {}).get("alert_mode", "loud")


def set_alert_mode(chat_id, mode):
    """
    Set alert mode for a chat.
    
    Args:
        chat_id: User or group chat ID
        mode: "loud" or "silent"
    """
    if mode not in ["loud", "silent"]:
        raise ValueError(f"Invalid mode: {mode}")
    
    data = load_settings()
    chat_id = str(chat_id)
    
    if chat_id not in data:
        data[chat_id] = {}
    
    data[chat_id]["alert_mode"] = mode
    save_settings(data)


def get_chat_settings(chat_id):
    """Get all settings for a chat."""
    data = load_settings()
    chat_id = str(chat_id)
    
    return data.get(chat_id, {
        "alert_mode": "loud",
        "plan": "free"  # For future monetization
    })


def set_chat_setting(chat_id, key, value):
    """Set a specific setting for a chat."""
    data = load_settings()
    chat_id = str(chat_id)
    
    if chat_id not in data:
        data[chat_id] = {}
    
    data[chat_id][key] = value
    save_settings(data)
