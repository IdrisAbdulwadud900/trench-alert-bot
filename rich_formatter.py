"""Rich message formatting utilities."""
from typing import Dict, Optional


def format_coin_alert_rich(
    ca: str,
    alert_type: str,
    current_mc: float,
    start_mc: float,
    details: Dict
) -> str:
    """
    Format coin alert with HTML markup.
    
    Args:
        ca: Contract address
        alert_type: Type of alert
        current_mc: Current market cap
        start_mc: Starting market cap
        details: Additional details
    
    Returns:
        HTML-formatted message
    """
    # Calculate metrics
    multiple = current_mc / start_mc if start_mc > 0 else 1
    change_pct = ((current_mc - start_mc) / start_mc * 100) if start_mc > 0 else 0
    
    # Build message with HTML
    msg = f"<b>🚨 ALERT - {alert_type.upper()}</b>\n\n"
    
    # Contract address
    msg += f"<code>{ca}</code>\n\n"
    
    # Metrics
    msg += f"<b>Current MC:</b> ${int(current_mc):,}\n"
    msg += f"<b>Start MC:</b> ${int(start_mc):,}\n"
    msg += f"<b>Multiple:</b> {multiple:.2f}x\n"
    
    # Color-coded change
    if change_pct > 0:
        msg += f"<b>Change:</b> <b>+{change_pct:.1f}%</b> 🟢\n"
    else:
        msg += f"<b>Change:</b> <b>{change_pct:.1f}%</b> 🔴\n"
    
    # Type-specific details
    if alert_type == "mc":
        target = details.get("target", 0)
        msg += f"\n<b>Target MC:</b> ${int(target):,} ✅\n"
    
    elif alert_type == "pct":
        threshold = details.get("threshold", 0)
        msg += f"\n<b>Threshold:</b> ±{threshold}% ✅\n"
    
    elif alert_type == "x":
        target_x = details.get("target", 0)
        msg += f"\n<b>Target:</b> {target_x}x ✅\n"
    
    elif alert_type == "reclaim":
        ath = details.get("ath", 0)
        msg += f"\n<b>ATH Reclaimed:</b> ${int(ath):,} 🔥\n"
    
    elif alert_type == "volume":
        spike = details.get("spike_multiplier", 0)
        msg += f"\n<b>Volume Spike:</b> {spike:.1f}x average 📊\n"
    
    elif alert_type == "liquidity":
        pct_drop = details.get("pct_drop", 0)
        msg += f"\n<b>Liquidity Drop:</b> {pct_drop:.1f}% ⚠️\n"
    
    return msg


def format_wallet_alert_rich(
    wallet_address: str,
    wallet_label: Optional[str],
    ca: str,
    amount_usd: float,
    signature: str
) -> str:
    """
    Format wallet buy alert with HTML markup.
    
    Returns:
        HTML-formatted message
    """
    msg = "<b>👛 WALLET BUY ALERT</b>\n\n"
    
    # Wallet info
    if wallet_label:
        msg += f"<b>Wallet:</b> {wallet_label}\n"
    msg += f"<code>{wallet_address[:8]}...{wallet_address[-6:]}</code>\n\n"
    
    # Buy info
    msg += f"<b>Token:</b> <code>{ca[:8]}...{ca[-6:]}</code>\n"
    msg += f"<b>Amount:</b> ${amount_usd:,.2f}\n\n"
    
    # Transaction link
    msg += f"<a href='https://solscan.io/tx/{signature}'>View on Solscan</a>\n"
    
    return msg


def format_meta_alert_rich(result: Dict) -> str:
    """
    Format meta alert with HTML markup.
    
    Returns:
        HTML-formatted message
    """
    alert_type = result.get("type")
    list_name = result.get("list_name", "Unknown")
    
    msg = f"<b>🚀 LIST ALERT</b>\n<b>{list_name}</b>\n\n"
    
    if alert_type == "n_pumping":
        count = result.get("count", 0)
        threshold = result.get("threshold", 0)
        coins = result.get("coins", [])
        
        msg += f"<b>🔥 {count}/{threshold} coins pumping!</b>\n\n"
        
        for coin_info in coins[:5]:
            ca = coin_info.get("ca", "")
            pct = coin_info.get("pct", 0)
            msg += f"• <code>{ca[:8]}...</code> <b>+{pct:.1f}%</b> 🟢\n"
        
        if len(coins) > 5:
            msg += f"\n...and {len(coins) - 5} more\n"
    
    elif alert_type == "total_mc":
        total = result.get("total", 0)
        threshold = result.get("threshold", 0)
        
        msg += f"<b>💰 Total MC:</b> ${int(total):,}\n"
        msg += f"<b>🎯 Target:</b> ${int(threshold):,} ✅\n"
    
    elif alert_type == "avg_pct":
        avg = result.get("average", 0)
        threshold = result.get("threshold", 0)
        
        msg += f"<b>📈 Average:</b> <b>+{avg:.1f}%</b> 🟢\n"
        msg += f"<b>🎯 Target:</b> +{threshold:.1f}% ✅\n"
    
    return msg


def format_combo_alert_rich(combo_type: str, details: Dict, ca: str) -> str:
    """
    Format combination alert with HTML markup.
    
    Returns:
        HTML-formatted message
    """
    msg = "<b>🔥🔥 COMBO ALERT</b>\n\n"
    msg += f"<code>{ca[:8]}...{ca[-6:]}</code>\n\n"
    
    if combo_type == "mc_volume":
        mc = details.get("mc", 0)
        mc_target = details.get("mc_target", 0)
        spike = details.get("spike_multiplier", 0)
        
        msg += f"<b>✅ MC:</b> ${int(mc):,}\n"
        msg += f"   <i>(target: ${int(mc_target):,})</i>\n"
        msg += f"<b>✅ Volume spike:</b> {spike:.1f}x average\n\n"
        msg += "<b>Both conditions met!</b> 🎯"
    
    elif combo_type == "pct_volume":
        pct = details.get("pct", 0)
        pct_target = details.get("pct_target", 0)
        volume = details.get("volume", 0)
        min_volume = details.get("min_volume", 0)
        
        msg += f"<b>✅ Change:</b> +{pct:.1f}%\n"
        msg += f"   <i>(target: {pct_target}%)</i>\n"
        msg += f"<b>✅ Volume:</b> ${int(volume):,}\n"
        msg += f"   <i>(min: ${int(min_volume):,})</i>\n\n"
        msg += "<b>Both conditions met!</b> 🎯"
    
    elif combo_type == "x_liquidity":
        x = details.get("x", 0)
        x_target = details.get("x_target", 0)
        liq = details.get("liquidity", 0)
        min_liq = details.get("min_liquidity", 0)
        
        msg += f"<b>✅ Multiple:</b> {x:.2f}x\n"
        msg += f"   <i>(target: {x_target}x)</i>\n"
        msg += f"<b>✅ Liquidity:</b> ${int(liq):,}\n"
        msg += f"   <i>(min: ${int(min_liq):,})</i>\n\n"
        msg += "<b>Both conditions met!</b> 🎯"
    
    elif combo_type == "triple":
        mc = details.get("mc", 0)
        mc_target = details.get("mc_target", 0)
        pct = details.get("pct", 0)
        pct_target = details.get("pct_target", 0)
        volume = details.get("volume", 0)
        min_volume = details.get("min_volume", 0)
        
        msg += f"<b>✅ MC:</b> ${int(mc):,}\n"
        msg += f"<b>✅ Change:</b> +{pct:.1f}%\n"
        msg += f"<b>✅ Volume:</b> ${int(volume):,}\n\n"
        msg += "<b>All 3 conditions met!</b> 🎯🎯🎯"
    
    return msg
