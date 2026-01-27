"""Format meta alert messages."""


def format_meta_alert(result: dict) -> str:
    """
    Format a meta alert result into a Telegram message.
    
    Args:
        result: Meta alert result from evaluate_meta_alerts
    
    Returns:
        Formatted message string
    """
    alert_type = result.get("type")
    list_name = result.get("list_name", "Unknown")
    
    if alert_type == "n_pumping":
        count = result.get("count", 0)
        threshold = result.get("threshold", 0)
        coins = result.get("coins", [])
        
        msg = f"🚀 LIST ALERT: {list_name}\n\n"
        msg += f"🔥 {count}/{threshold} coins pumping!\n\n"
        
        for coin_info in coins[:5]:  # Show top 5
            ca = coin_info.get("ca", "")
            pct = coin_info.get("pct", 0)
            msg += f"• {ca[:8]}... +{pct:.1f}%\n"
        
        if len(coins) > 5:
            msg += f"\n...and {len(coins) - 5} more"
        
        return msg
    
    elif alert_type == "total_mc":
        total = result.get("total", 0)
        threshold = result.get("threshold", 0)
        
        msg = f"📊 LIST ALERT: {list_name}\n\n"
        msg += f"💰 Total MC: ${int(total):,}\n"
        msg += f"🎯 Target: ${int(threshold):,}\n"
        
        return msg
    
    elif alert_type == "avg_pct":
        avg = result.get("average", 0)
        threshold = result.get("threshold", 0)
        
        msg = f"📈 LIST ALERT: {list_name}\n\n"
        msg += f"🔥 Average: +{avg:.1f}%\n"
        msg += f"🎯 Target: +{threshold:.1f}%\n"
        
        return msg
    
    else:
        return f"🔔 META ALERT: {list_name}\n\n{result}"
