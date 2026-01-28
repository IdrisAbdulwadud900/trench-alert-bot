"""Alert history tracking system."""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import fcntl
import tempfile
import shutil

HISTORY_FILE = "alert_history.json"


def load_history() -> Dict:
    """Load alert history from JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return {}
    
    try:
        with open(HISTORY_FILE, 'r') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return data
    except Exception as e:
        print(f"⚠️ Error loading history: {e}")
        return {}


def save_history(history: Dict):
    """Save alert history to JSON file."""
    try:
        fd, temp_path = tempfile.mkstemp(suffix=".json", dir=os.path.dirname(HISTORY_FILE) or ".")
        try:
            with os.fdopen(fd, "w") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(history, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            shutil.move(temp_path, HISTORY_FILE)
        except Exception as e:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
    except (IOError, OSError) as e:
        print(f"⚠️ Error saving history: {e}")


def log_alert(user_id: int, alert_type: str, coin_ca: str, details: Dict):
    """
    Log a fired alert to history.
    
    Args:
        user_id: Telegram user ID
        alert_type: Type of alert (mc, pct, x, reclaim, volume, liquidity, etc.)
        coin_ca: Contract address of the coin
        details: Additional information about the alert (value, threshold, etc.)
    """
    history = load_history()
    
    user_id_str = str(user_id)
    if user_id_str not in history:
        history[user_id_str] = []
    
    alert_record = {
        "timestamp": datetime.now().isoformat(),
        "type": alert_type,
        "ca": coin_ca,
        "details": details
    }
    
    history[user_id_str].append(alert_record)
    
    # Keep only last 1000 alerts per user to prevent bloat
    if len(history[user_id_str]) > 1000:
        history[user_id_str] = history[user_id_str][-1000:]
    
    save_history(history)


def get_user_history(user_id: int, limit: Optional[int] = None) -> List[Dict]:
    """
    Get alert history for a user.
    
    Args:
        user_id: Telegram user ID
        limit: Maximum number of alerts to return (most recent first)
    
    Returns:
        List of alert records
    """
    history = load_history()
    user_id_str = str(user_id)
    
    if user_id_str not in history:
        return []
    
    alerts = history[user_id_str]
    
    # Return most recent first
    alerts_sorted = sorted(alerts, key=lambda x: x["timestamp"], reverse=True)
    
    if limit:
        return alerts_sorted[:limit]
    
    return alerts_sorted


def get_history_stats(user_id: int) -> Dict:
    """
    Get statistics about user's alert history.
    
    Returns:
        Dict with total_alerts, alerts_by_type, most_alerted_coin
    """
    alerts = get_user_history(user_id)
    
    if not alerts:
        return {
            "total_alerts": 0,
            "alerts_by_type": {},
            "most_alerted_coin": None
        }
    
    alerts_by_type = {}
    coin_counts = {}
    
    for alert in alerts:
        alert_type = alert["type"]
        coin_ca = alert["ca"]
        
        alerts_by_type[alert_type] = alerts_by_type.get(alert_type, 0) + 1
        coin_counts[coin_ca] = coin_counts.get(coin_ca, 0) + 1
    
    most_alerted_coin = max(coin_counts.items(), key=lambda x: x[1])[0] if coin_counts else None
    
    return {
        "total_alerts": len(alerts),
        "alerts_by_type": alerts_by_type,
        "most_alerted_coin": most_alerted_coin
    }


def clear_user_history(user_id: int):
    """Clear all alert history for a user."""
    history = load_history()
    user_id_str = str(user_id)
    
    # Use pop to safely remove - won't error if key doesn't exist
    if history.pop(user_id_str, None) is not None:
        save_history(history)
        return True
    return False
