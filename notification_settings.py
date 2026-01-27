"""Notification settings per alert type."""
import json
import os
from typing import Dict
import fcntl
import tempfile
import shutil

NOTIF_SETTINGS_FILE = "notification_settings.json"


def load_notification_settings() -> Dict:
    """Load notification settings from JSON file."""
    if not os.path.exists(NOTIF_SETTINGS_FILE):
        return {}
    
    try:
        with open(NOTIF_SETTINGS_FILE, 'r') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return data
    except Exception as e:
        print(f"⚠️ Error loading notification settings: {e}")
        return {}


def save_notification_settings(data: Dict):
    """Save notification settings to JSON file."""
    try:
        fd, temp_path = tempfile.mkstemp(suffix=".json", dir=os.path.dirname(NOTIF_SETTINGS_FILE) or ".")
        try:
            with os.fdopen(fd, "w") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            shutil.move(temp_path, NOTIF_SETTINGS_FILE)
        except Exception as e:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
    except (IOError, OSError) as e:
        print(f"⚠️ Error saving notification settings: {e}")


def get_user_notification_settings(user_id: int) -> Dict:
    """
    Get notification settings for a user.
    
    Returns dict with alert types as keys and sound preference as values.
    Default: all alerts have sound enabled.
    """
    settings = load_notification_settings()
    user_id_str = str(user_id)
    
    if user_id_str not in settings:
        # Default settings - all enabled
        return {
            "mc": True,
            "pct": True,
            "x": True,
            "reclaim": True,
            "volume": True,
            "liquidity": True,
            "wallet": True,
            "meta": True,
            "timebased": True,
            "combo": True
        }
    
    return settings[user_id_str]


def update_notification_setting(user_id: int, alert_type: str, enabled: bool):
    """Update notification setting for specific alert type."""
    settings = load_notification_settings()
    user_id_str = str(user_id)
    
    if user_id_str not in settings:
        settings[user_id_str] = get_user_notification_settings(user_id)
    
    settings[user_id_str][alert_type] = enabled
    save_notification_settings(settings)


def should_notify(user_id: int, alert_type: str) -> bool:
    """Check if notification should be sent for this alert type."""
    user_settings = get_user_notification_settings(user_id)
    return user_settings.get(alert_type, True)
