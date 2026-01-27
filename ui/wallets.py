#!/usr/bin/env python3
"""
Wallet Tracking UI - Clean & Focused
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.tracker import Tracker


async def show_wallets_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show wallet tracking menu."""
    query = update.callback_query
    user_id = query.from_user.id
    
    wallets = Tracker.get_wallets(user_id)
    wallet_count = len(wallets)
    
    text = f"👛 Watch Wallets\n\nYou are watching {wallet_count} wallet(s)."
    
    keyboard = [
        [InlineKeyboardButton("➕ Add Wallet", callback_data="wallet_add")],
        [InlineKeyboardButton("📋 View Wallets", callback_data="wallet_list")],
        [InlineKeyboardButton("◀ Back", callback_data="home")]
    ]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_wallet_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of tracked wallets."""
    query = update.callback_query
    user_id = query.from_user.id
    
    wallets = Tracker.get_wallets(user_id)
    
    if not wallets:
        await query.message.reply_text(
            "No wallets tracked yet.\n\nUse ➕ Add Wallet to start."
        )
        return
    
    text = "📋 Your Wallets\n\n"
    
    for i, wallet in enumerate(wallets, 1):
        address = wallet.get("address", "")
        label = wallet.get("label", "Unnamed")
        
        text += f"{i}. {label}\n"
        text += f"   {address[:10]}...{address[-8:]}\n\n"
    
    keyboard = [[InlineKeyboardButton("◀ Back", callback_data="menu_wallets")]]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
