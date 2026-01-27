"""
Intelligence Layer for Trench Alert Bot

Provides context-aware analysis:
- ATH + Range positioning
- Behavior pattern detection
- Signal quality filtering
- User profile adaptation
- Smart alert formatting
"""

import time
from typing import Dict, List, Tuple

# User modes and their thresholds
USER_MODES = {
    "conservative": {
        "min_liquidity": 50_000,
        "min_volume_ratio": 0.5,  # volume_24h / mc
        "min_quality_score": 2,
        "max_dd_percent": 30,  # max drawdown before alert
    },
    "aggressive": {
        "min_liquidity": 10_000,
        "min_volume_ratio": 0.2,
        "min_quality_score": 1,
        "max_dd_percent": 60,
    },
    "sniper": {
        "min_liquidity": 2_000,
        "min_volume_ratio": 0.1,
        "min_quality_score": 0,
        "max_dd_percent": 80,
    }
}

HISTORY_WINDOW = 600  # 10 minutes in seconds


def compute_range_position(mc: float, low_mc: float, ath_mc: float) -> float:
    """
    Compute where price is in historical range (0-1).
    
    0.0 = at low
    1.0 = at high
    0.5 = middle
    """
    if ath_mc == low_mc or ath_mc <= 0 or low_mc <= 0:
        return 0.5  # Edge case: no range yet or invalid data
    
    # Clamp mc between low and ath
    mc = max(min(mc, ath_mc * 2), low_mc * 0.5)  # Allow some overflow
    
    position = (mc - low_mc) / (ath_mc - low_mc)
    return max(0.0, min(1.0, position))  # Clamp to 0-1


def compute_quality_score(liquidity: float, volume_24h: float, mc: float) -> int:
    """
    Score signal quality 0-3.
    
    Higher score = more reliable signal
    """
    score = 0
    
    # Ensure no negative values
    liquidity = max(0, liquidity)
    volume_24h = max(0, volume_24h)
    mc = max(0, mc)
    
    # Liquidity check
    if liquidity > 20_000:
        score += 1
    
    # Volume relative to MC (prevent division by zero)
    if mc > 0 and volume_24h > mc * 0.3:
        score += 1
    
    # MC not too low (avoid scams)
    if mc > 50_000:
        score += 1
    
    return min(score, 3)


def should_alert_based_quality(quality_score: int, user_mode: str) -> bool:
    """Check if quality meets user's threshold."""
    min_required = USER_MODES.get(user_mode, USER_MODES["aggressive"])["min_quality_score"]
    return quality_score >= min_required


def get_range_description(position: float) -> str:
    """Describe where price is in range."""
    if position < 0.15:
        return "near bottom 15% 🔴"
    elif position < 0.35:
        return "lower 35% 📉"
    elif position < 0.65:
        return "middle range ➡️"
    elif position < 0.85:
        return "upper 35% 📈"
    else:
        return "near top 15% 🟢"


def detect_dump_stabilize_bounce(
    coin: Dict, 
    mc: float, 
    current_volume: float
) -> Tuple[bool, str]:
    """
    Detect dump → stabilize → bounce pattern.
    
    Returns: (pattern_detected, pattern_type)
    """
    history = coin.get("history", [])
    ath_mc = coin.get("ath_mc", mc)
    
    if len(history) < 3 or ath_mc <= 0 or mc <= 0:
        return False, ""
    
    current_time = time.time()
    recent_history = [
        h for h in history 
        if current_time - h["ts"] < HISTORY_WINDOW
    ]
    
    if len(recent_history) < 3:
        return False, ""
    
    # Check: Has coin dumped significantly from ATH?
    dump_percent = (ath_mc - mc) / ath_mc * 100 if ath_mc > 0 else 0
    if dump_percent < 30:
        return False, ""
    
    # Check: Is price stabilizing? (small range in last 10 mins)
    recent_prices = [h["mc"] for h in recent_history if h.get("mc", 0) > 0]
    if not recent_prices:
        return False, ""
        
    min_price = min(recent_prices)
    max_price = max(recent_prices)
    
    if min_price <= 0:
        return False, ""
        
    price_range = (max_price - min_price) / min_price * 100
    
    if price_range > 10:  # Too volatile, not stabilizing
        return False, ""
    
    # Check: Is volume increasing?
    if len(recent_history) >= 2:
        recent_vol = recent_history[-1].get("volume", 0)
        older_vol = recent_history[-3].get("volume", 0) if len(recent_history) >= 3 else 0
        
        if older_vol > 0 and recent_vol <= older_vol:
            return False, ""
    
    # Check: Has there been a small bounce?
    recent_low = min(recent_prices)
    if recent_low > 0 and mc > recent_low * 1.10:  # Bounced 10%+
        return True, "dump_stabilize_bounce"
    
    return False, ""


def analyze_momentum(history: List[Dict]) -> Tuple[str, float]:
    """
    Analyze price momentum from history.
    
    Returns: (direction, strength)
    direction: "up", "down", "stable"
    strength: 0-1 (how strong the move is)
    """
    if len(history) < 2:
        return "stable", 0.0
    
    prices = [h["mc"] for h in history[-5:] if h.get("mc", 0) > 0]  # Last 5 valid entries
    
    if not prices or len(prices) < 2:
        return "stable", 0.0
    
    first_price = prices[0]
    if first_price <= 0:
        return "stable", 0.0
        
    pct_change = (prices[-1] - first_price) / first_price * 100
    strength = min(abs(pct_change) / 20, 1.0)  # Normalize to 0-1
    
    if pct_change > 5:
        return "up", strength
    elif pct_change < -5:
        return "down", strength
    else:
        return "stable", strength


def format_smart_alert(
    coin: Dict,
    mc: float,
    alert_type: str,
    user_mode: str = "aggressive"
) -> str:
    """
    Format alert with context + intelligence.
    
    Much more informative than raw numbers.
    """
    ath_mc = coin.get("ath_mc", mc)
    low_mc = coin.get("low_mc", mc)
    history = coin.get("history", [])
    quality = compute_quality_score(
        coin.get("liquidity", 0),
        coin.get("volume_24h", 0),
        mc
    )
    
    # Compute metrics (with safe division)
    dd_from_ath = ((ath_mc - mc) / ath_mc) * 100 if ath_mc > 0 else 0
    range_pos = compute_range_position(mc, low_mc, ath_mc)
    range_desc = get_range_description(range_pos)
    momentum, momentum_strength = analyze_momentum(history)
    quality_label = "🟢" if quality >= 2 else "🟡" if quality == 1 else "🔴"
    
    # Build smart message
    if alert_type == "dump_stabilize_bounce":
        return (
            f"🚀 BOUNCE PATTERN DETECTED\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 MC: ${int(mc):,}\n"
            f"📉 Down {dd_from_ath:.1f}% from ATH\n"
            f"📊 Position: {range_desc}\n"
            f"⚡ Momentum: {momentum.upper()} ({momentum_strength*100:.0f}%)\n"
            f"📈 Volume increasing\n"
            f"✅ Price stabilizing\n"
            f"{quality_label} Quality: {quality}/3\n\n"
            f"⚠️ Second leg potential HIGH"
        )
    
    elif alert_type == "mc_break":
        return (
            f"🎯 MARKET CAP ALERT\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Target MC reached: ${int(mc):,}\n"
            f"📊 Position in range: {range_desc}\n"
            f"📉 Drawdown from ATH: {dd_from_ath:.1f}%\n"
            f"⚡ Momentum: {momentum.upper()}\n"
            f"{quality_label} Signal Quality: {quality}/3"
        )
    
    elif alert_type == "range_bottom":
        return (
            f"🔴 EXTREME BOTTOM DETECTED\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 MC: ${int(mc):,}\n"
            f"📊 Lowest position in {HISTORY_WINDOW//60} minutes\n"
            f"📉 Drawdown from ATH: {dd_from_ath:.1f}%\n"
            f"{quality_label} Signal Quality: {quality}/3\n\n"
            f"💡 Watch for reversal signals"
        )
    
    else:  # Default format
        return (
            f"📊 ALERT: {alert_type.upper()}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 MC: ${int(mc):,}\n"
            f"📊 Range position: {range_desc}\n"
            f"{quality_label} Quality: {quality}/3"
        )


def should_suppress_alert(
    coin: Dict,
    alert_type: str,
    user_mode: str = "aggressive"
) -> bool:
    """
    Determine if alert should be suppressed based on quality.
    
    Prevents low-quality noise from triggering alerts.
    """
    quality = compute_quality_score(
        coin.get("liquidity", 0),
        coin.get("volume_24h", 0),
        coin.get("mc", 0)
    )
    
    min_score = USER_MODES[user_mode]["min_quality_score"]
    
    return quality < min_score


def update_coin_history(coin: Dict, mc: float, volume_24h: float, liquidity: float) -> Dict:
    """
    Update coin history and range tracking.
    """
    current_time = time.time()
    
    # Initialize if needed
    if "history" not in coin:
        coin["history"] = []
    if "low_mc" not in coin:
        coin["low_mc"] = mc
    if "ath_mc" not in coin:
        coin["ath_mc"] = mc
    
    # Update ATH and low
    coin["ath_mc"] = max(coin.get("ath_mc", mc), mc)
    coin["low_mc"] = min(coin.get("low_mc", mc), mc)
    
    # Add to history
    coin["history"].append({
        "mc": mc,
        "ts": current_time,
        "volume": volume_24h,
        "liquidity": liquidity
    })
    
    # Trim old history (keep only last 10 minutes)
    coin["history"] = [
        h for h in coin["history"]
        if current_time - h["ts"] < HISTORY_WINDOW * 2  # Keep 20 min for safety
    ]
    
    return coin
