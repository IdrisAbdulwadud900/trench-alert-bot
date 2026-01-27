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
from ui.coins import (
    show_coins_menu, 
    show_coin_list, 
    start_add_coin,
    show_configure_alerts,
    handle_remove_coin,
    confirm_remove_coin
)
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
    
    if choice == "coin_remove":
        await query.answer()
        await handle_remove_coin(update, context)
        return
    
    if choice.startswith("remove_coin_"):
        await query.answer()
        coin_index = int(choice.split("_")[-1])
        await confirm_remove_coin(update, context, coin_index)
        return
    
    # Alert configuration
    if choice.startswith("alert_config_"):
        await query.answer()
        await handle_alert_config(update, context, choice)
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
        awhandle_alert_config(update: Update, context: ContextTypes.DEFAULT_TYPE, choice: str):
    """Handle alert configuration selections."""
    query = update.callback_query
    user_id = query.from_user.id
    
    state = context.bot_data.get("user_states", {}).get(user_id, {})
    
    if choice == "alert_config_mc":
        state["configuring"] = "mc"
        await query.message.reply_text(
            "📉 MC Target Alert\n\n"
            "Send the market cap value to alert at.\n"
            "Example: 50000"
        )
    
    elif choice == "alert_config_pct":
        state["configuring"] = "pct"
        await query.message.reply_text(
            "📈 % Move Alert\n\n"
            "Send the percentage change to alert at.\n"
            "Example: 30 (for ±30%)"
        )
    
    elif choice == "alert_config_x":
        state["configuring"] = "x"
        await query.message.reply_text(
            "🚀 X Multiple Alert\n\n"
            "Send the X multiplier to alert at.\n"
            "Example: 5 (for 5x)"
        )
    
    elif choice == "alert_config_reclaim":
        # ATH reclaim is a toggle, just add it
        state.setdefault("alerts", {})
        state["alerts"]["reclaim"] = True
        await query.message.reply_text("✅ ATH Reclaim alert added")
    
    elif choice == "alert_config_done":
        # Save the coin
        ca = state.get("ca")
        mc = state.get("start_mc")
        alerts = state.get("alerts", {})
        
        if ca and mc:
            from core.tracker import Tracker
            coin_data = {
                "ca": ca,
                "start_mc": mc,
                "ath_mc": mc,
                "low_mc": mc,
                "alerts": alerts,
                "triggered": {}
            }
            
            Tracker.add_coin(user_id, coin_data)
            
            alert_count = len(alerts)
            await query.message.reply_text(
                f"✅ Coin Added\n\n"
                f"MC: ${int(mc):,}\n"
                f"Alerts: {alert_count} configured"
            )
        
        # Clear state
        context.bot_data["user_states"].pop(user_id, None)


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
    configuring = state.get("configuring")
    
    # Add coin flow - step 1: get CA
    if step == "awaiting_ca":
        from mc import get_market_cap
        
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
        
        # Store in state and show alert config
        state["ca"] = ca
        state["start_mc"] = mc
        state["alerts"] = {}
        state["step"] = "configuring_alerts"
        
        await show_configure_alerts(update, context, ca, mc)
        return
    
    # Alert configuration inputs
    if configuring == "mc":
        try:
            mc_value = float(text)
            state.setdefault("alerts", {})
            state["alerts"]["mc"] = mc_value
            state.pop("configuring", None)
            await update.message.reply_text(
                f"✅ MC alert set: ${int(mc_value):,}\n\n"
                f"Configure more alerts or tap Done."
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Try again.")
    
    elif configuring == "pct":
        try:
            pct_value = float(text)
            state.setdefault("alerts", {})
            state["alerts"]["pct"] = pct_value
            state.pop("configuring", None)
            await update.message.reply_text(
                f"✅ % alert set: ±{int(pct_value)}%\n\n"
                f"Configure more alerts or tap Done."
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Try again.")
    
    elif configuring == "x":
        try:
            x_value = float(text)
            state.setdefault("alerts", {})
            state["alerts"]["x"] = x_value
            state.pop("configuring", None)
            await update.message.reply_text(
                f"✅ X alert set: {x_value}x\n\n"
                f"Configure more alerts or tap Done."
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Try again."    "ca": ca,
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
