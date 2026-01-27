#!/usr/bin/env python3
"""
Coin Tracking UI - Clean & Focused
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.tracker import Tracker


async def show_coins_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show coin tracking menu."""
    query = update.callback_query
    user_id = query.from_user.id
    
    coins = Tracker.get_user_coins(user_id)
    coin_count = len(coins)
    
    text = f"📈 Track Coins\n\nYou are tracking {coin_count} coin(s)."
    
    keyboard = [
        [InlineKeyboardButton("➕ Add Coin", callback_data="coin_add")],
        [InlineKeyboardButton("📋 View Coins", callback_data="coin_list")],
        [InlineKeyboardButton("◀ Back", callback_data="home")]
    ]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_coin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of tracked coins."""
    query = update.callback_query
    user_id = query.from_user.id
    
    coins = Tracker.get_user_coins(user_id)
    
    if not coins:
        await query.message.reply_text(
            "No coins tracked yet.\n\nUse ➕ Add Coin to start."
        )
        return
    
    text = "📋 Your Coins\n\n"
    
    for i, coin in enumerate(coins, 1):
        ca = coin.get("ca", "Unknown")
        alerts = coin.get("alerts", {})
        alert_types = list(alerts.keys())
        
        text += f"{i}. {ca[:8]}...{ca[-6:]}\n"
        text += f"   Alerts: {', '.join(alert_types) if alert_types else 'None'}\n\n"
    
    keyboard = [[InlineKeyboardButton("◀ Back", callback_data="menu_coins")]]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def start_add_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the add coin flow."""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Set state for this user
    if "user_states" not in context.bot_data:
        context.bot_data["user_states"] = {}
    
    context.bot_data["user_states"][user_id] = {"step": "awaiting_ca"}
    
    await query.message.reply_text(
        "➕ Add Coin\n\n"
        "Send the Solana contract address:"
    )
