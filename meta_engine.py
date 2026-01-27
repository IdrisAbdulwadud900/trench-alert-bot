#!/usr/bin/env python3
"""
Meta Alert Engine v1

Detects when multiple coins in a list are pumping together (narrative rotation).

TRIGGER CONDITIONS:
- Same list
- ≥ 3 coins
- Each ≥ +20% (1h)
- Within last 60 minutes
- Cooldown: 3 hours per list
"""

import time
from typing import Dict, List, Optional, Tuple
from storage import get_all_coins


# Track last alert time per list to enforce cooldown
_last_alert_time: Dict[str, float] = {}

# Cooldown duration (3 hours)
COOLDOWN_SECONDS = 3 * 60 * 60


def detect_meta_movement(
    list_name: str,
    list_coins: List[str],
    all_coins_data: Dict
) -> Optional[List[Tuple[str, str, float]]]:
    """
    Detect if a list has meta movement (3+ coins pumping 20%+).
    
    Args:
        list_name: Name of the list
        list_coins: List of contract addresses in the list
        all_coins_data: Dict mapping CA -> coin data with pct_1h
        
    Returns:
        List of (symbol, ca, pct_1h) for movers, or None if no movement
    """
    movers = []
    
    for ca in list_coins:
        # Find coin data across all users
        coin_found = False
        
        for user_id, coins in all_coins_data.items():
            for coin in coins:
                if coin.get("ca") == ca:
                    symbol = coin.get("symbol", "???")
                    pct_1h = coin.get("pct_1h", 0)
                    
                    # Check if pumping 20%+
                    if pct_1h >= 20:
                        movers.append((symbol, ca, pct_1h))
                    
                    coin_found = True
                    break
            
            if coin_found:
                break
    
    # Need at least 3 movers
    if len(movers) >= 3:
        # Sort by performance (highest first)
        movers.sort(key=lambda x: x[2], reverse=True)
        return movers
    
    return None


def should_send_meta_alert(list_name: str) -> bool:
    """
    Check if enough time has passed since last alert for this list.
    Enforces 3-hour cooldown.
    
    Args:
        list_name: Name of the list
        
    Returns:
        True if alert can be sent (cooldown expired or first alert)
    """
    now = time.time()
    last_alert = _last_alert_time.get(list_name, 0)
    
    time_since_last = now - last_alert
    
    return time_since_last >= COOLDOWN_SECONDS


def mark_meta_alert_sent(list_name: str):
    """Mark that a meta alert was just sent for this list."""
    _last_alert_time[list_name] = time.time()


def format_meta_alert(list_name: str, movers: List[Tuple[str, str, float]]) -> str:
    """
    Format meta alert message.
    
    Args:
        list_name: Name of the list
        movers: List of (symbol, ca, pct_1h) tuples
        
    Returns:
        Formatted alert message
    """
    # Take top 3-5 movers
    top_movers = movers[:5]
    
    msg = f"🔥 META HEATING UP — {list_name}\n\n"
    
    msg += f"{len(movers)} coins moving together:\n"
    
    for symbol, ca, pct_1h in top_movers:
        msg += f"• {symbol} {pct_1h:+.0f}%\n"
    
    msg += "\nNarrative rotation likely."
    
    return msg


def get_cooldown_remaining(list_name: str) -> int:
    """
    Get seconds remaining until next alert can be sent.
    
    Args:
        list_name: Name of the list
        
    Returns:
        Seconds remaining (0 if can send now)
    """
    now = time.time()
    last_alert = _last_alert_time.get(list_name, 0)
    
    time_since_last = now - last_alert
    remaining = max(0, COOLDOWN_SECONDS - time_since_last)
    
    return int(remaining)


def reset_cooldowns():
    """Reset all cooldowns (for testing/admin)."""
    _last_alert_time.clear()
