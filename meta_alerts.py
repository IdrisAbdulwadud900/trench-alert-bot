"""Meta alert evaluation logic for lists/narratives."""
from typing import Dict, List, Optional
from mc import get_market_cap


def should_alert_n_pumping(
    list_coins: List[str],
    coin_data: Dict,  # user's coins with start_mc
    n_threshold: int,
    pct_threshold: float = 10.0
) -> Optional[Dict]:
    """
    Check if N+ coins in list are pumping.
    
    Args:
        list_coins: List of contract addresses in the list
        coin_data: Dict mapping CA to coin data (with start_mc)
        n_threshold: Minimum number of coins that must be pumping
        pct_threshold: Percentage change threshold (default 10%)
    
    Returns:
        Alert details if triggered, None otherwise
    """
    pumping_count = 0
    pumping_coins = []
    
    for ca in list_coins:
        # Get current price
        token = get_market_cap(ca)
        if not token or not token.get("mc"):
            continue
        
        current_mc = token["mc"]
        
        # Find start MC from user's coin data
        coin_info = coin_data.get(ca)
        if not coin_info:
            continue
        
        start_mc = coin_info.get("start_mc", 0)
        if start_mc == 0:
            continue
        
        # Calculate % change
        pct_change = ((current_mc - start_mc) / start_mc) * 100
        
        if pct_change >= pct_threshold:
            pumping_count += 1
            pumping_coins.append({
                "ca": ca,
                "pct": pct_change,
                "mc": current_mc
            })
    
    if pumping_count >= n_threshold:
        return {
            "type": "n_pumping",
            "count": pumping_count,
            "threshold": n_threshold,
            "coins": pumping_coins
        }
    
    return None


def should_alert_total_mc(
    list_coins: List[str],
    mc_threshold: float
) -> Optional[Dict]:
    """
    Check if total market cap of list exceeds threshold.
    
    Args:
        list_coins: List of contract addresses
        mc_threshold: Total MC threshold
    
    Returns:
        Alert details if triggered, None otherwise
    """
    total_mc = 0
    coin_mcs = []
    
    for ca in list_coins:
        token = get_market_cap(ca)
        if token and token.get("mc"):
            mc = token["mc"]
            total_mc += mc
            coin_mcs.append({"ca": ca, "mc": mc})
    
    if total_mc >= mc_threshold:
        return {
            "type": "total_mc",
            "total": total_mc,
            "threshold": mc_threshold,
            "coins": coin_mcs
        }
    
    return None


def should_alert_avg_pct(
    list_coins: List[str],
    coin_data: Dict,
    pct_threshold: float
) -> Optional[Dict]:
    """
    Check if average % change across list exceeds threshold.
    
    Args:
        list_coins: List of contract addresses
        coin_data: Dict mapping CA to coin data (with start_mc)
        pct_threshold: Average % change threshold
    
    Returns:
        Alert details if triggered, None otherwise
    """
    total_pct = 0
    count = 0
    coin_pcts = []
    
    for ca in list_coins:
        token = get_market_cap(ca)
        if not token or not token.get("mc"):
            continue
        
        current_mc = token["mc"]
        
        coin_info = coin_data.get(ca)
        if not coin_info:
            continue
        
        start_mc = coin_info.get("start_mc", 0)
        if start_mc == 0:
            continue
        
        pct_change = ((current_mc - start_mc) / start_mc) * 100
        total_pct += pct_change
        count += 1
        coin_pcts.append({"ca": ca, "pct": pct_change})
    
    if count == 0:
        return None
    
    avg_pct = total_pct / count
    
    if avg_pct >= pct_threshold:
        return {
            "type": "avg_pct",
            "average": avg_pct,
            "threshold": pct_threshold,
            "coins": coin_pcts
        }
    
    return None


def evaluate_meta_alerts(
    list_name: str,
    list_coins: List[str],
    coin_data: Dict,
    meta_alerts: Dict,
    meta_triggered: Dict
) -> Optional[Dict]:
    """
    Evaluate all meta alerts for a list.
    
    Args:
        list_name: Name of the list
        list_coins: List of CAs in the list
        coin_data: User's coin data
        meta_alerts: Meta alert configuration
        meta_triggered: Dict tracking which alerts have fired
    
    Returns:
        Alert details if any triggered, None otherwise
    """
    # Check N+ pumping
    if "n_pumping" in meta_alerts and not meta_triggered.get("n_pumping"):
        result = should_alert_n_pumping(
            list_coins,
            coin_data,
            meta_alerts["n_pumping"]
        )
        if result:
            result["list_name"] = list_name
            return result
    
    # Check total MC
    if "total_mc" in meta_alerts and not meta_triggered.get("total_mc"):
        result = should_alert_total_mc(
            list_coins,
            meta_alerts["total_mc"]
        )
        if result:
            result["list_name"] = list_name
            return result
    
    # Check average %
    if "avg_pct" in meta_alerts and not meta_triggered.get("avg_pct"):
        result = should_alert_avg_pct(
            list_coins,
            coin_data,
            meta_alerts["avg_pct"]
        )
        if result:
            result["list_name"] = list_name
            return result
    
    return None
