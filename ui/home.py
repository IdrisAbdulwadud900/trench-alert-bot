#!/usr/bin/env python3
"""
Home Screen - Clean & Professional
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


HOME_TEXT = """🚨 Trench Alert

Track coins. Watch wallets.
Catch narratives early.

What do you want to do?"""


async def show_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the main home screen."""
    
    keyboard = [
        [InlineKeyboardButton("📈 Track Coins", callback_data="menu_coins")],
        [InlineKeyboardButton("👛 Watch Wallets", callback_data="menu_wallets")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="menu_dashboard")],
        [InlineKeyboardButton("📋 Lists", callback_data="menu_lists")],
        [InlineKeyboardButton("📜 Alert History", callback_data="alert_history")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")]
    ]
    
    # Check if this is a callback query or message
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            HOME_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            HOME_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def handle_home_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, choice: str):
    """Route home menu selections."""
    query = update.callback_query
    await query.answer()
    
    if choice == "menu_coins":
        from ui.coins import show_coins_menu
        await show_coins_menu(update, context)
    
    elif choice == "menu_wallets":
        from ui.wallets import show_wallets_menu
        await show_wallets_menu(update, context)
    
    elif choice == "menu_lists":
        from ui.lists import show_lists_menu
        await show_lists_menu(update, context)
    
    elif choice == "menu_alerts":
        await query.message.reply_text("🔔 Alerts menu - Coming soon")
    
    elif choice == "menu_settings":
        from ui.settings import show_settings_menu
        await show_settings_menu(update, context)
    
    elif choice == "home":
        # Back to home
        await show_home(update, context)
