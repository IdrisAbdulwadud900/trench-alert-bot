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
    
    keyboard = [
        [InlineKeyboardButton("🗑️ Remove Wallet", callback_data="wallet_remove")],
        [InlineKeyboardButton("◀ Back", callback_data="menu_wallets")]
    ]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def start_add_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the add wallet flow."""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Set state for this user
    if "user_states" not in context.bot_data:
        context.bot_data["user_states"] = {}
    
    context.bot_data["user_states"][user_id] = {"step": "awaiting_wallet_address"}
    
    await query.message.reply_text(
        "➕ Add Wallet\n\n"
        "Send the Solana wallet address to track:"
    )


async def handle_remove_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show wallets with remove option."""
    query = update.callback_query
    user_id = query.from_user.id
    
    wallets = Tracker.get_wallets(user_id)
    
    if not wallets:
        await query.message.reply_text("No wallets to remove.")
        return
    
    text = "🗑️ Remove Wallet\n\nSelect wallet to remove:"
    
    keyboard = []
    for i, wallet in enumerate(wallets):
        address = wallet.get("address", "")
        label = wallet.get("label", "Unnamed")
        keyboard.append([
            InlineKeyboardButton(
                f"{label} ({address[:6]}...{address[-4:]})",
                callback_data=f"remove_wallet_{i}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("◀ Back", callback_data="menu_wallets")])
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def confirm_remove_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE, wallet_index: int):
    """Remove a wallet by index."""
    query = update.callback_query
    user_id = query.from_user.id
    
    wallets = Tracker.get_wallets(user_id)
    
    if wallet_index >= len(wallets):
        await query.message.reply_text("❌ Invalid wallet selection.")
        return
    
    wallet = wallets[wallet_index]
    address = wallet.get("address")
    label = wallet.get("label", "Unnamed")
    
    if Tracker.remove_wallet(user_id, address):
        await query.message.reply_text(
            f"✅ Wallet Removed\n\n{label}\n{address[:10]}...{address[-8:]}"
        )
    else:
        await query.message.reply_text("❌ Error removing wallet.")
