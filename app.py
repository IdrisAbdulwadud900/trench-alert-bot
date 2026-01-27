#!/usr/bin/env python3
"""
Trench Alert Bot - Clean Architecture
Main entry point - Minimal wiring only
"""

import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN, CHECK_INTERVAL
from ui.home import show_home, handle_home_callback
from ui.coins import show_coins_menu, show_coin_list, start_add_coin
from ui.wallets import show_wallets_menu, show_wallet_list
from ui.settings import show_settings_menu, show_alert_mode_setting
from core.monitor import start_monitor


# Validate BOT_TOKEN
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is not set!")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await show_home(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    text = (
        "ℹ️ Help\n\n"
        "/start - Open home menu\n"
        "/help - Show this help\n"
    )
    await update.message.reply_text(text)


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route all callback queries to appropriate handlers."""
    query = update.callback_query
    choice = query.data
    
    # Home menu
    if choice.startswith("menu_") or choice == "home":
        await handle_home_callback(update, context, choice)
        return
    
    # Coins
    if choice == "coin_list":
        await query.answer()
        await show_coin_list(update, context)
        return
    
    if choice == "coin_add":
        await query.answer()
        await start_add_coin(update, context)
        return
    
    # Wallets
    if choice == "wallet_list":
        await query.answer()
        await show_wallet_list(update, context)
        return
    
    # Settings
    if choice == "setting_alert_mode":
        await query.answer()
        await show_alert_mode_setting(update, context)
        return
    
    if choice == "setting_plans":
        await query.answer()
        await query.message.reply_text("💳 Plans - Coming soon")
        return
    
    if choice == "set_mode_loud":
        from settings import set_alert_mode
        await query.answer()
        set_alert_mode(query.message.chat_id, "loud")
        await query.message.reply_text("✅ Alert mode set to LOUD")
        return
    
    if choice == "set_mode_silent":
        from settings import set_alert_mode
        await query.answer()
        set_alert_mode(query.message.chat_id, "silent")
        await query.message.reply_text("✅ Alert mode set to SILENT")
        return
    
    # Default
    await query.answer()
    await query.message.reply_text(f"Handler for '{choice}' not yet implemented")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages (for flows like adding coins)."""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Check if user is in a flow
    if "user_states" not in context.bot_data:
        context.bot_data["user_states"] = {}
    
    state = context.bot_data["user_states"].get(user_id, {})
    
    if not state:
        # No active flow - ignore
        return
    
    step = state.get("step")
    
    # Add coin flow
    if step == "awaiting_ca":
        from mc import get_market_cap
        from core.tracker import Tracker
        
        ca = text
        
        # Validate and fetch token info
        token = get_market_cap(ca)
        
        if not token or not token.get("mc"):
            await update.message.reply_text(
                "❌ Invalid token or API error.\n\n"
                "Please send a valid Solana contract address."
            )
            return
        
        mc = token["mc"]
        
        # Add coin with default config (can enhance later)
        coin_data = {
            "ca": ca,
            "start_mc": mc,
            "ath_mc": mc,
            "low_mc": mc,
            "alerts": {},  # Empty - user can configure later
            "triggered": {}
        }
        
        Tracker.add_coin(user_id, coin_data)
        
        # Clear state
        context.bot_data["user_states"].pop(user_id, None)
        
        await update.message.reply_text(
            f"✅ Coin Added\n\n"
            f"MC: ${int(mc):,}\n\n"
            f"Use 🔔 Alerts menu to configure alerts."
        )


def main():
    """Main entry point."""
    print("🚀 Trench Alert Bot - Clean Architecture")
    print("=" * 50)
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Post-init hook
    async def post_init(application):
        await application.bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhooks cleared")
        
        await application.bot.set_my_commands([
            ("start", "Open home menu"),
            ("help", "Show help")
        ])
        print("✅ Commands registered")
        
        # Start monitor loop
        asyncio.create_task(start_monitor(application.bot))
        print("✅ Monitor loop started")
    
    app.post_init = post_init
    
    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("✅ All handlers registered")
    print("=" * 50)
    print("🟢 Bot starting...\n")
    
    # Run
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        close_loop=False
    )


if __name__ == "__main__":
    main()
