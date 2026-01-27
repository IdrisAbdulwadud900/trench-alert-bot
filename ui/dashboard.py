#!/usr/bin/env python3
"""
Dashboard UI - Portfolio Overview
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.tracker import Tracker


async def show_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show portfolio dashboard."""
    query = update.callback_query
    user_id = query.from_user.id
    
    coins = Tracker.get_user_coins(user_id)
    
    if not coins:
        await query.message.reply_text(
            "📊 Dashboard\n\n"
            "No coins tracked yet.\n"
            "Add coins to see your portfolio."
        )
        return
    
    from mc import get_market_cap
    
    text = "📊 Portfolio Dashboard\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    total_invested = 0
    total_current = 0
    winners = 0
    losers = 0
    
    for coin in coins:
        ca = coin.get("ca", "")
        start_mc = coin.get("start_mc", 0)
        
        token = get_market_cap(ca)
        if not token or not token.get("mc"):
            continue
        
        current_mc = token["mc"]
        total_invested += start_mc
        total_current += current_mc
        
        if current_mc > start_mc:
            winners += 1
        else:
            losers += 1
    
    # Portfolio stats
    pnl = total_current - total_invested
    pnl_pct = ((total_current - total_invested) / total_invested * 100) if total_invested > 0 else 0
    
    pnl_emoji = "🟢" if pnl >= 0 else "🔴"
    
    text += f"💼 Total Coins: {len(coins)}\n"
    text += f"🟢 Winners: {winners}\n"
    text += f"🔴 Losers: {losers}\n\n"
    text += f"💰 Total Value: ${int(total_current):,}\n"
    text += f"{pnl_emoji} PnL: ${int(pnl):,} ({pnl_pct:+.1f}%)\n\n"
    
    # Top performers
    performance_list = []
    for coin in coins:
        ca = coin.get("ca", "")
        start_mc = coin.get("start_mc", 0)
        
        token = get_market_cap(ca)
        if not token or not token.get("mc"):
            continue
        
        current_mc = token["mc"]
        multiple = current_mc / start_mc if start_mc > 0 else 1
        
        performance_list.append({
            "ca": ca,
            "multiple": multiple,
            "current_mc": current_mc
        })
    
    # Sort by performance
    performance_list.sort(key=lambda x: x["multiple"], reverse=True)
    
    text += "🏆 Top Performers:\n"
    for i, perf in enumerate(performance_list[:3], 1):
        ca = perf["ca"]
        mult = perf["multiple"]
        emoji = "🟢" if mult >= 1 else "🔴"
        text += f"{i}. {emoji} {ca[:6]}...{ca[-4:]} - {mult:.2f}x\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data="menu_alerts")],
        [InlineKeyboardButton("◀ Back", callback_data="home")]
    ]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
