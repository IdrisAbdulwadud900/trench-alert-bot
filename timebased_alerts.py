"""Time-based alert system."""
from datetime import datetime, timedelta
from typing import Dict, Optional
import json
import os
import fcntl
import tempfile
import shutil

TIMEBASED_FILE = "timebased_alerts.json"


def load_timebased() -> Dict:
    """Load time-based alerts from JSON file."""
    if not os.path.exists(TIMEBASED_FILE):
        return {}
    
    try:
        with open(TIMEBASED_FILE, 'r') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return data
    except Exception as e:
        print(f"⚠️ Error loading timebased alerts: {e}")
        return {}


def save_timebased(data: Dict):
    """Save time-based alerts to JSON file."""
    try:
        fd, temp_path = tempfile.mkstemp(suffix=".json", dir=os.path.dirname(TIMEBASED_FILE) or ".")
        try:
            with os.fdopen(fd, "w") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            shutil.move(temp_path, TIMEBASED_FILE)
        except Exception as e:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
    except (IOError, OSError) as e:
        print(f"⚠️ Error saving timebased alerts: {e}")


def add_timebaased_alert(
    user_id: int,
    ca: str,
    alert_type: str,
    target_value: float,
    expiry_hours: int
):
    """
    Add a time-based alert.
    
    Args:
        user_id: Telegram user ID
        ca: Contract address
        alert_type: Type of alert (e.g., "2x", "mc", "pct")
        target_value: Target value for the alert
        expiry_hours: Hours until alert expires
    """
    data = load_timebased()
    
    user_id_str = str(user_id)
    if user_id_str not in data:
        data[user_id_str] = []
    
    expiry_time = (datetime.now() + timedelta(hours=expiry_hours)).isoformat()
    
    alert = {
        "ca": ca,
        "type": alert_type,
        "target": target_value,
        "expires_at": expiry_time,
        "created_at": datetime.now().isoformat(),
        "triggered": False
    }
    
    data[user_id_str].append(alert)
    save_timebased(data)


def should_alert_timeased(
    user_id: int,
    ca: str,
    current_mc: float,
    start_mc: float
) -> Optional[Dict]:
    """
    Check if any time-based alerts should fire or expire.
    
    Returns:
        Alert details if should fire/expire, None otherwise
    """
    data = load_timebased()
    user_id_str = str(user_id)
    
    if user_id_str not in data:
        return None
    
    alerts = data[user_id_str]
    now = datetime.now()
    
    for alert in alerts:
        if alert["ca"] != ca or alert["triggered"]:
            continue
        
        expiry_time = datetime.fromisoformat(alert["expires_at"])
        
        # Check if expired
        if now >= expiry_time:
            alert_type = alert["type"]
            
            # Check if target was NOT met
            if alert_type == "2x":
                current_x = current_mc / start_mc if start_mc > 0 else 1
                if current_x < alert["target"]:
                    # Target not met
                    alert["triggered"] = True
                    save_timebased(data)
                    
                    return {
                        "type": "time_expired",
                        "subtype": alert_type,
                        "target": alert["target"],
                        "actual": current_x,
                        "message": f"⏰ TIME EXPIRED\n\n{ca[:8]}... did not {alert['target']}x in time\n\nCurrent: {current_x:.2f}x"
                    }
            
            elif alert_type == "mc":
                if current_mc < alert["target"]:
                    alert["triggered"] = True
                    save_timebased(data)
                    
                    return {
                        "type": "time_expired",
                        "subtype": alert_type,
                        "target": alert["target"],
                        "actual": current_mc,
                        "message": f"⏰ TIME EXPIRED\n\n{ca[:8]}... did not reach ${int(alert['target']):,} MC\n\nCurrent: ${int(current_mc):,}"
                    }
        
        else:
            # Not expired yet - check if target met
            if alert_type == "2x":
                current_x = current_mc / start_mc if start_mc > 0 else 1
                if current_x >= alert["target"]:
                    alert["triggered"] = True
                    save_timebased(data)
                    
                    return {
                        "type": "time_target_met",
                        "subtype": alert_type,
                        "target": alert["target"],
                        "actual": current_x,
                        "message": f"🎯 TARGET MET\n\n{ca[:8]}... hit {current_x:.2f}x!\n\nTarget: {alert['target']}x"
                    }
            
            elif alert_type == "mc":
                if current_mc >= alert["target"]:
                    alert["triggered"] = True
                    save_timebased(data)
                    
                    return {
                        "type": "time_target_met",
                        "subtype": alert_type,
                        "target": alert["target"],
                        "actual": current_mc,
                        "message": f"🎯 TARGET MET\n\n{ca[:8]}... hit ${int(current_mc):,} MC!\n\nTarget: ${int(alert['target']):,}"
                    }
    
    return None


def get_active_timebased(user_id: int) -> list:
    """Get all active (non-triggered, non-expired) time-based alerts for a user."""
    data = load_timebased()
    user_id_str = str(user_id)
    
    if user_id_str not in data:
        return []
    
    now = datetime.now()
    active = []
    
    for alert in data[user_id_str]:
        if alert["triggered"]:
            continue
        
        expiry_time = datetime.fromisoformat(alert["expires_at"])
        if now < expiry_time:
            active.append(alert)
    
    return active


def clear_timebased_for_coin(user_id: int, ca: str):
    """Clear all time-based alerts for a specific coin."""
    data = load_timebased()
    user_id_str = str(user_id)
    
    if user_id_str not in data:
        return
    
    data[user_id_str] = [
        alert for alert in data[user_id_str]
        if alert["ca"] != ca
    ]
    
    save_timebased(data)
