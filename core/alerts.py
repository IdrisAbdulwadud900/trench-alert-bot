#!/usr/bin/env python3
"""
Alert Evaluation Engine - Pure logic
No UI. No Telegram. Just "should we alert?"
"""

from typing import Optional, Tuple
from intelligence import (
    detect_dump_stabilize_bounce,
    format_smart_alert,
    should_suppress_alert,
    compute_range_position,
    get_range_description
)


class AlertEngine:
    """Evaluate if alerts should fire - pure logic"""
    
    @staticmethod
    def should_alert_mc(coin: dict, current_mc: float) -> Tuple[bool, Optional[str]]:
        """Check if MC alert should fire."""
        alerts = coin.get("alerts", {})
        triggered = coin.get("triggered", {})
        
        if "mc" not in alerts or triggered.get("mc"):
            return False, None
        
        if current_mc <= alerts["mc"]:
            msg = f"🚨 MC ALERT\n━━━━━━━━━━━━━━━━━━━━━━━━\nTarget: ${int(alerts['mc']):,}\nCurrent: ${int(current_mc):,}"
            return True, msg
        
        return False, None
    
    @staticmethod
    def should_alert_pct(coin: dict, current_mc: float) -> Tuple[bool, Optional[str]]:
        """Check if % change alert should fire."""
        alerts = coin.get("alerts", {})
        triggered = coin.get("triggered", {})
        
        if "pct" not in alerts or triggered.get("pct"):
            return False, None
        
        start_mc = coin.get("start_mc", current_mc)
        if start_mc <= 0:
            return False, None
        
        pct_change = ((current_mc - start_mc) / start_mc) * 100
        
        if abs(pct_change) >= alerts["pct"]:
            range_pos = compute_range_position(
                current_mc,
                coin.get("low_mc", current_mc),
                coin.get("ath_mc", current_mc)
            )
            msg = (
                f"📈 % CHANGE ALERT\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Move: {pct_change:.1f}%\n"
                f"Position: {get_range_description(range_pos)}\n"
                f"MC: ${int(current_mc):,}"
            )
            return True, msg
        
        return False, None
    
    @staticmethod
    def should_alert_x(coin: dict, current_mc: float) -> Tuple[bool, Optional[str]]:
        """Check if X multiple alert should fire."""
        alerts = coin.get("alerts", {})
        triggered = coin.get("triggered", {})
        
        if "x" not in alerts or triggered.get("x"):
            return False, None
        
        start_mc = coin.get("start_mc", current_mc)
        if start_mc <= 0:
            return False, None
        
        multiple = current_mc / start_mc
        
        if multiple >= alerts["x"]:
            msg = (
                f"🚀 X ALERT\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Reached {multiple:.2f}x\n"
                f"MC: ${int(current_mc):,}"
            )
            return True, msg
        
        return False, None
    
    @staticmethod
    def should_alert_reclaim(coin: dict, current_mc: float) -> Tuple[bool, Optional[str]]:
        """Check if ATH reclaim alert should fire."""
        alerts = coin.get("alerts", {})
        triggered = coin.get("triggered", {})
        
        if not alerts.get("reclaim") or triggered.get("reclaim"):
            return False, None
        
        ath_mc = coin.get("ath_mc", current_mc)
        reclaim_level = ath_mc * 0.95
        
        if current_mc >= reclaim_level:
            msg = (
                f"🔥 ATH RECLAIM\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"95% of ATH reached\n"
                f"MC: ${int(current_mc):,}"
            )
            return True, msg
        
        return False, None
    
    @staticmethod
    def should_alert_bounce(coin: dict, current_mc: float, volume_24h: float, user_mode: str) -> Tuple[bool, Optional[str]]:
        """Check if dump/stabilize/bounce pattern detected."""
        triggered = coin.get("triggered", {})
        
        if triggered.get("bounce"):
            return False, None
        
        bounce_detected, bounce_type = detect_dump_stabilize_bounce(coin, current_mc, volume_24h)
        
        if bounce_detected:
            msg = format_smart_alert(coin, current_mc, bounce_type, user_mode)
            return True, msg
        
        return False, None
    
    @staticmethod
    def evaluate_all(coin: dict, current_mc: float, volume_24h: float, user_mode: str = "aggressive") -> list:
        """
        Evaluate all alerts for a coin.
        Returns list of (alert_type, message) tuples that should fire.
        """
        alerts_to_fire = []
        
        # Check quality suppression first
        if should_suppress_alert(coin, "default", user_mode):
            return []
        
        # Bounce (highest priority - pattern detection)
        should_alert, msg = AlertEngine.should_alert_bounce(coin, current_mc, volume_24h, user_mode)
        if should_alert:
            alerts_to_fire.append(("bounce", msg))
        
        # MC target
        should_alert, msg = AlertEngine.should_alert_mc(coin, current_mc)
        if should_alert:
            alerts_to_fire.append(("mc", msg))
        
        # % change
        should_alert, msg = AlertEngine.should_alert_pct(coin, current_mc)
        if should_alert:
            alerts_to_fire.append(("pct", msg))
        
        # X multiple
        should_alert, msg = AlertEngine.should_alert_x(coin, current_mc)
        if should_alert:
            alerts_to_fire.append(("x", msg))
        
        # ATH reclaim
        should_alert, msg = AlertEngine.should_alert_reclaim(coin, current_mc)
        if should_alert:
            alerts_to_fire.append(("reclaim", msg))
        
        return alerts_to_fire
