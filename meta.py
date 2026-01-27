#!/usr/bin/env python3
"""
Meta Analysis Module - Track narrative rotation and list performance

Detects when multiple coins in a list are pumping (meta heating up).
"""

from typing import Dict, List, Tuple
import time

def analyze_list_performance(
    list_coins: List[str],
    coin_data: Dict[str, Dict]
) -> Dict:
    """
    Analyze performance of all coins in a list.
    
    Args:
        list_coins: List of contract addresses
        coin_data: Dict mapping CA -> {mc, start_mc, ath_mc, volume_24h}
    
    Returns:
        Performance metrics for the list
    """
    if not list_coins:
        return {
            "total_coins": 0,
            "pumping_count": 0,
            "dumping_count": 0,
            "avg_performance": 0,
            "heat_score": 0,
            "status": "empty"
        }
    
    pumping = 0
    dumping = 0
    total_performance = 0
    high_volume_count = 0
    
    valid_coins = 0
    
    for ca in list_coins:
        data = coin_data.get(ca)
        if not data:
            continue
            
        valid_coins += 1
        mc = data.get("mc", 0)
        start_mc = data.get("start_mc", mc)
        volume_24h = data.get("volume_24h", 0)
        
        if start_mc <= 0:
            continue
        
        # Calculate performance
        performance = ((mc - start_mc) / start_mc) * 100
        total_performance += performance
        
        # Track pumping/dumping
        if performance > 20:  # Up 20%+
            pumping += 1
        elif performance < -20:  # Down 20%+
            dumping += 1
        
        # Track high volume (suggests activity)
        if mc > 0 and volume_24h > mc * 0.5:  # Volume > 50% of MC
            high_volume_count += 1
    
    if valid_coins == 0:
        return {
            "total_coins": len(list_coins),
            "pumping_count": 0,
            "dumping_count": 0,
            "avg_performance": 0,
            "heat_score": 0,
            "status": "no_data"
        }
    
    avg_performance = total_performance / valid_coins
    
    # Heat score: combination of pumping coins and volume
    heat_score = (
        (pumping / valid_coins) * 50 +  # 50% weight on pumping coins
        (high_volume_count / valid_coins) * 30 +  # 30% weight on volume
        (max(0, avg_performance) / 100) * 20  # 20% weight on avg performance
    )
    
    # Determine status
    if heat_score > 60:
        status = "🔥 HOT"
    elif heat_score > 40:
        status = "📈 HEATING"
    elif heat_score > 20:
        status = "➡️ WARM"
    else:
        status = "❄️ COLD"
    
    return {
        "total_coins": len(list_coins),
        "valid_coins": valid_coins,
        "pumping_count": pumping,
        "dumping_count": dumping,
        "high_volume_count": high_volume_count,
        "avg_performance": avg_performance,
        "heat_score": heat_score,
        "status": status
    }

def detect_list_heating(
    list_name: str,
    current_metrics: Dict,
    previous_metrics: Dict = None,
    threshold: float = 40
) -> Tuple[bool, str]:
    """
    Detect if a list is heating up (narrative rotation).
    
    Returns: (is_heating, reason)
    """
    heat_score = current_metrics.get("heat_score", 0)
    
    # Simple threshold check
    if heat_score > threshold:
        pumping = current_metrics.get("pumping_count", 0)
        total = current_metrics.get("valid_coins", 1)
        
        if pumping >= 2:  # At least 2 coins pumping
            pct = (pumping / total) * 100 if total > 0 else 0
            return True, f"{pumping}/{total} coins ({pct:.0f}%) pumping"
    
    # Trend detection (if previous data available)
    if previous_metrics:
        prev_score = previous_metrics.get("heat_score", 0)
        score_change = heat_score - prev_score
        
        if score_change > 20:  # Rapid heating
            return True, f"Heat score jumped {score_change:.0f} points"
    
    return False, ""

def format_list_alert(
    list_name: str,
    metrics: Dict,
    reason: str
) -> str:
    """Format a list heating alert."""
    
    status = metrics.get("status", "")
    pumping = metrics.get("pumping_count", 0)
    total = metrics.get("valid_coins", 0)
    avg_perf = metrics.get("avg_performance", 0)
    heat = metrics.get("heat_score", 0)
    
    return (
        f"🔥 META ALERT — {list_name}\n\n"
        f"{status}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Pumping: {pumping}/{total} coins\n"
        f"Avg Performance: {avg_perf:+.1f}%\n"
        f"Heat Score: {heat:.0f}/100\n\n"
        f"Reason: {reason}\n\n"
        f"💡 Narrative rotation detected"
    )

def get_top_performers_in_list(
    list_coins: List[str],
    coin_data: Dict[str, Dict],
    top_n: int = 3
) -> List[Tuple[str, float]]:
    """Get top N performing coins in a list."""
    
    performances = []
    
    for ca in list_coins:
        data = coin_data.get(ca)
        if not data:
            continue
        
        mc = data.get("mc", 0)
        start_mc = data.get("start_mc", mc)
        
        if start_mc <= 0:
            continue
        
        performance = ((mc - start_mc) / start_mc) * 100
        performances.append((ca, performance))
    
    # Sort by performance descending
    performances.sort(key=lambda x: x[1], reverse=True)
    
    return performances[:top_n]

def format_list_status(
    list_name: str,
    metrics: Dict,
    top_performers: List[Tuple[str, float]] = None
) -> str:
    """Format a detailed list status message."""
    
    status = metrics.get("status", "")
    total = metrics.get("total_coins", 0)
    valid = metrics.get("valid_coins", 0)
    pumping = metrics.get("pumping_count", 0)
    avg_perf = metrics.get("avg_performance", 0)
    heat = metrics.get("heat_score", 0)
    
    msg = (
        f"📊 {list_name} — Status\n\n"
        f"{status} (Heat: {heat:.0f})\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Coins: {valid}/{total} tracked\n"
        f"Pumping: {pumping} coins\n"
        f"Avg: {avg_perf:+.1f}%\n"
    )
    
    if top_performers:
        msg += "\n🏆 Top Performers:\n"
        for ca, perf in top_performers:
            msg += f"• {ca[:6]}... {perf:+.1f}%\n"
    
    return msg
