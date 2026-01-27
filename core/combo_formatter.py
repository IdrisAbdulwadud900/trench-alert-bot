"""Format combination alert messages."""


def format_combo_alert(combo_type: str, details: dict, ca: str) -> str:
    """
    Format a combination alert message.
    
    Args:
        combo_type: Type of combo alert
        details: Alert details dict
        ca: Contract address
    
    Returns:
        Formatted message string
    """
    if combo_type == "mc_volume":
        mc = details.get("mc", 0)
        mc_target = details.get("mc_target", 0)
        spike = details.get("spike_multiplier", 0)
        
        return (
            f"🔥🔥 COMBO ALERT\n\n"
            f"{ca[:8]}...\n\n"
            f"✅ MC: ${int(mc):,} (target: ${int(mc_target):,})\n"
            f"✅ Volume spike: {spike:.1f}x average\n\n"
            f"Both conditions met!"
        )
    
    elif combo_type == "pct_volume":
        pct = details.get("pct", 0)
        pct_target = details.get("pct_target", 0)
        volume = details.get("volume", 0)
        min_volume = details.get("min_volume", 0)
        
        return (
            f"🔥🔥 COMBO ALERT\n\n"
            f"{ca[:8]}...\n\n"
            f"✅ Change: +{pct:.1f}% (target: {pct_target}%)\n"
            f"✅ Volume: ${int(volume):,} (min: ${int(min_volume):,})\n\n"
            f"Both conditions met!"
        )
    
    elif combo_type == "x_liquidity":
        x = details.get("x", 0)
        x_target = details.get("x_target", 0)
        liq = details.get("liquidity", 0)
        min_liq = details.get("min_liquidity", 0)
        
        return (
            f"🔥🔥 COMBO ALERT\n\n"
            f"{ca[:8]}...\n\n"
            f"✅ Multiple: {x:.2f}x (target: {x_target}x)\n"
            f"✅ Liquidity: ${int(liq):,} (min: ${int(min_liq):,})\n\n"
            f"Both conditions met!"
        )
    
    elif combo_type == "triple":
        mc = details.get("mc", 0)
        mc_target = details.get("mc_target", 0)
        pct = details.get("pct", 0)
        pct_target = details.get("pct_target", 0)
        volume = details.get("volume", 0)
        min_volume = details.get("min_volume", 0)
        
        return (
            f"🔥🔥🔥 TRIPLE COMBO\n\n"
            f"{ca[:8]}...\n\n"
            f"✅ MC: ${int(mc):,} (target: ${int(mc_target):,})\n"
            f"✅ Change: +{pct:.1f}% (target: {pct_target}%)\n"
            f"✅ Volume: ${int(volume):,} (min: ${int(min_volume):,})\n\n"
            f"All 3 conditions met!"
        )
    
    else:
        return f"🔥 COMBO ALERT: {combo_type}\n\n{ca[:8]}...\n\n{details}"
