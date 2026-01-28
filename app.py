#!/usr/bin/env python3
"""
Trench Alert Bot - Clean Architecture
Main entry point - Minimal wiring only
"""

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
    confirm_remove_coin,
    handle_pause_coin,
    toggle_pause_coin,
    handle_edit_alerts,
    show_edit_alert_menu
)
from ui.wallets import (
    show_wallets_menu,
    show_wallet_list,
    start_add_wallet,
    handle_remove_wallet,
    confirm_remove_wallet
)
from ui.settings import show_settings_menu, show_alert_mode_setting
from ui.lists import (
    show_lists_menu,
    show_lists_view,
    start_create_list,
    show_list_detail,
    show_meta_alerts
)
from ui.dashboard import show_dashboard
from ui.history import show_alert_history, clear_history_confirm, clear_history_confirmed
from ui.search import start_coin_search, handle_coin_search, pause_all_coins, resume_all_coins, delete_all_coins_confirm, delete_all_coins_confirmed
from ui.notifications import show_notification_settings, toggle_notification
from ui.admin import show_admin_dashboard, show_admin_users, admin_clear_cache, show_admin_stats
from core.monitor import start_monitor
from webhook_config import should_use_webhook, get_webhook_config, setup_webhook


# Validate BOT_TOKEN
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is not set!")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    # Detect if this is a group
    is_group = update.effective_chat.type in ["group", "supergroup"]
    
    if is_group:
        await update.message.reply_text(
            "👋 Trench Alert Bot\n\n"
            "Add me to your group to track coins together!\n"
            "Use /start in private chat to configure."
        )
    else:
        await show_home(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    text = (
        "ℹ️ Help\n\n"
        "/start - Open home menu\n"
        "/help - Show this help\n"
    )
    await update.message.reply_text(text)


async def handle_alert_config(update: Update, context: ContextTypes.DEFAULT_TYPE, choice: str):
    """Handle alert configuration selections."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if "user_states" not in context.bot_data:
        context.bot_data["user_states"] = {}
    
    state = context.bot_data["user_states"].get(user_id, {})
    
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
        try:
            coin_index = int(choice.split("_")[-1])
            await confirm_remove_coin(update, context, coin_index)
        except (ValueError, IndexError):
            await query.message.edit_text("⚠️ Invalid selection")
        return
    
    if choice == "coin_pause":
        await query.answer()
        await handle_pause_coin(update, context)
        return
    
    if choice.startswith("toggle_pause_"):
        await query.answer()
        try:
            coin_index = int(choice.split("_")[-1])
            await toggle_pause_coin(update, context, coin_index)
        except (ValueError, IndexError):
            await query.message.edit_text("⚠️ Invalid selection")
        return
    
    if choice == "coin_edit_alerts":
        await query.answer()
        await handle_edit_alerts(update, context)
        return
    
    if choice.startswith("edit_alerts_"):
        await query.answer()
        try:
            coin_index = int(choice.split("_")[-1])
            await show_edit_alert_menu(update, context, coin_index)
        except (ValueError, IndexError):
            await query.message.edit_text("⚠️ Invalid selection")
        return
    
    if choice.startswith("edit_mc_") or choice.startswith("edit_pct_") or choice.startswith("edit_x_"):
        await query.answer()
        try:
            parts = choice.split("_")
            alert_type = parts[1]
            coin_index = int(parts[2])
        except (ValueError, IndexError):
            await query.message.edit_text("⚠️ Invalid selection")
            return
        
        # Store in user state for message handler
        if "user_states" not in context.bot_data:
            context.bot_data["user_states"] = {}
        
        context.bot_data["user_states"][query.from_user.id] = {
            "step": "editing_alert",
            "alert_type": alert_type,
            "coin_index": coin_index
        }
        
        alert_names = {"mc": "MC Target", "pct": "% Move", "x": "X Multiple"}
        await query.message.reply_text(
            f"✏️ Edit {alert_names[alert_type]}\n\n"
            f"Send the new value:"
        )
        return
    
    if choice.startswith("edit_reclaim_"):
        await query.answer()
        try:
            coin_index = int(choice.split("_")[-1])
        except (ValueError, IndexError):
            await query.message.edit_text("⚠️ Invalid selection")
            return
        
        from storage import load_data, save_data
        data = load_data()
        user_id_str = str(query.from_user.id)
        
        if user_id_str in data:
            user_data = data[user_id_str]
            coins = user_data.get("coins", []) if isinstance(user_data, dict) else user_data
            
            if coin_index < len(coins):
                coin = coins[coin_index]
                alerts = coin.setdefault("alerts", {})
                current = alerts.get("reclaim", False)
                alerts["reclaim"] = not current
                save_data(data)
                
                status = "ON" if alerts["reclaim"] else "OFF"
                await query.message.reply_text(f"✅ ATH Reclaim: {status}")
        return
    
    if choice.startswith("clear_alerts_"):
        await query.answer()
        try:
            coin_index = int(choice.split("_")[-1])
        except (ValueError, IndexError):
            await query.message.edit_text("⚠️ Invalid selection")
            return
        
        from storage import load_data, save_data
        data = load_data()
        user_id_str = str(query.from_user.id)
        
        if user_id_str in data:
            user_data = data[user_id_str]
            coins = user_data.get("coins", []) if isinstance(user_data, dict) else user_data
            
            if coin_index < len(coins):
                coin = coins[coin_index]
                coin["alerts"] = {}
                coin["triggered"] = {}
                save_data(data)
                await query.message.reply_text("✅ All alerts cleared")
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
    
    if choice == "wallet_add":
        await query.answer()
        await start_add_wallet(update, context)
        return
    
    if choice == "wallet_remove":
        await query.answer()
        await handle_remove_wallet(update, context)
        return
    
    if choice.startswith("remove_wallet_"):
        await query.answer()
        try:
            wallet_index = int(choice.split("_")[-1])
            await confirm_remove_wallet(update, context, wallet_index)
        except (ValueError, IndexError):
            await query.message.edit_text("⚠️ Invalid selection")
        return
    
    # Dashboard
    if choice == "menu_dashboard":
        await query.answer()
        await show_dashboard(update, context)
        return
    
    # Alert History
    if choice == "alert_history":
        await query.answer()
        await show_alert_history(update, context)
        return
    
    if choice == "history_clear":
        await query.answer()
        await clear_history_confirm(update, context)
        return
    
    if choice == "history_clear_confirmed":
        await query.answer()
        await clear_history_confirmed(update, context)
        return
    
    # Search & Bulk Operations
    if choice == "coin_search":
        await query.answer()
        await start_coin_search(update, context)
        return
    
    if choice == "coin_pause_all":
        await query.answer()
        await pause_all_coins(update, context)
        return
    
    if choice == "coin_resume_all":
        await query.answer()
        await resume_all_coins(update, context)
        return
    
    if choice == "coin_delete_all":
        await query.answer()
        await delete_all_coins_confirm(update, context)
        return
    
    if choice == "coin_delete_all_confirmed":
        await query.answer()
        await delete_all_coins_confirmed(update, context)
        return
    
    # Notification Settings
    if choice == "notif_settings":
        await query.answer()
        await show_notification_settings(update, context)
        return
    
    if choice.startswith("notif_toggle_"):
        await query.answer()
        alert_type = choice.replace("notif_toggle_", "")
        await toggle_notification(update, context, alert_type)
        return
    
    # Admin Dashboard
    if choice == "admin_dashboard":
        await query.answer()
        await show_admin_dashboard(update, context)
        return
    
    if choice == "admin_users":
        await query.answer()
        await show_admin_users(update, context)
        return
    
    if choice == "admin_clear_cache":
        await query.answer()
        await admin_clear_cache(update, context)
        return
    
    if choice == "admin_stats":
        await query.answer()
        await show_admin_stats(update, context)
        return
    
    # Lists
    if choice == "menu_lists" or choice == "list_view":
        await query.answer()
        await show_lists_view(update, context)
        return
    
    if choice == "list_create":
        await query.answer()
        await start_create_list(update, context)
        return
    
    if choice.startswith("list_open_"):
        await query.answer()
        try:
            list_index = int(choice.split("_")[-1])
            await show_list_detail(update, context, list_index)
        except (ValueError, IndexError):
            await query.message.edit_text("⚠️ Invalid selection")
        return
    
    if choice.startswith("list_delete_"):
        await query.answer()
        try:
            list_index = int(choice.split("_")[-1])
            from core.tracker import Tracker
            if Tracker.delete_list(query.from_user.id, list_index):
                await query.message.reply_text("✅ List deleted")
            else:
                await query.message.reply_text("❌ Error deleting list")
        except (ValueError, IndexError):
            await query.message.edit_text("⚠️ Invalid selection")
        return
    
    if choice == "list_meta":
        await query.answer()
        await show_meta_alerts(update, context)
        return
    
    # Dashboard/Alerts
    if choice == "menu_alerts":
        await query.answer()
        await show_dashboard(update, context)
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
    configuring = state.get("configuring")
    
    # Coin search flow
    if step == "searching_coin":
        from ui.search import handle_coin_search
        
        await handle_coin_search(update, context, text, user_id)
        
        # Clear state
        context.bot_data["user_states"].pop(user_id, None)
        return
    
    # Edit alert flow
    if step == "editing_alert":
        from storage import load_data, save_data
        
        alert_type = state["alert_type"]
        coin_index = state["coin_index"]
        
        try:
            if alert_type == "mc":
                value = float(text.replace(",", ""))
            elif alert_type == "pct":
                value = int(text)
            elif alert_type == "x":
                value = float(text)
            else:
                await update.message.reply_text("❌ Invalid alert type")
                context.bot_data["user_states"].pop(user_id, None)
                return
            
            # Update the alert
            data = load_data()
            user_id_str = str(user_id)
            
            if user_id_str in data:
                user_data = data[user_id_str]
                coins = user_data.get("coins", []) if isinstance(user_data, dict) else user_data
                
                if coin_index < len(coins):
                    coin = coins[coin_index]
                    if "alerts" not in coin:
                        coin["alerts"] = {}
                    
                    coin["alerts"][alert_type] = value
                    save_data(data)
                    
                    alert_names = {"mc": "MC Target", "pct": "% Move", "x": "X Multiple"}
                    keyboard = [
                        [InlineKeyboardButton("📋 View Coins", callback_data="coin_list")],
                        [InlineKeyboardButton("🏠 Home", callback_data="home")]
                    ]
                    await update.message.reply_text(
                        f"✅ Alert Updated\n\n"
                        f"{alert_names[alert_type]}: {value}\n\n"
                        f"You'll be notified when this target is hit!",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
            
            # Clear state
            context.bot_data["user_states"].pop(user_id, None)
            return
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid Number\n\n"
                "Please enter a valid number.\n\n"
                "💡 Examples:\n"
                "MC Target: 100000\n"
                "% Move: 50\n"
                "X Multiple: 5"
            )
            context.bot_data["user_states"].pop(user_id, None)
            return
    
    # Add coin flow - step 1: get CA
    if step == "awaiting_ca":
        from mc import get_market_cap
        from ui.coins import show_configure_alerts
        
        ca = text.strip()
        
        # Basic validation
        if len(ca) < 32 or len(ca) > 44:
            keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="menu_coins")]]
            await update.message.reply_text(
                "⚠️ Invalid Address Format\n\n"
                "Solana addresses are 32-44 characters long.\n\n"
                "💡 Tip: Copy the full contract address from DexScreener",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        
        # Show loading indicator
        loading_msg = await update.message.reply_text("⏳ Validating token...")
        
        # Validate and fetch token info
        token = get_market_cap(ca)
        
        # Delete loading message
        try:
            await loading_msg.delete()
        except:
            pass
        
        if not token or not token.get("mc"):
            keyboard = [
                [InlineKeyboardButton("➡️ Try Again", callback_data="coin_add")],
                [InlineKeyboardButton("❌ Cancel", callback_data="menu_coins")]
            ]
            await update.message.reply_text(
                "❌ Token Not Found\n\n"
                "Unable to fetch token data. This could mean:\n"
                "• Invalid contract address\n"
                "• Token not listed on DexScreener\n"
                "• Very new token (not indexed yet)\n\n"
                "Please verify the address and try again.",
                reply_markup=InlineKeyboardMarkup(keyboard)
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
    
    # Add wallet flow - step 1: get address
    if step == "awaiting_wallet_address":
        address = text.strip()
        
        # Basic Solana address validation (32-44 chars, base58)
        if len(address) < 32 or len(address) > 44:
            keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="menu_wallets")]]
            await update.message.reply_text(
                "⚠️ Invalid Wallet Address\n\n"
                "Solana wallet addresses are 32-44 characters long.\n\n"
                "💡 Example: DYw8j...8cTD",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        
        # Store address and ask for label
        state["wallet_address"] = address
        state["step"] = "awaiting_wallet_label"
        
        await update.message.reply_text(
            "✅ Address Received\n\n"
            "Now send a label/name for this wallet\n\n"
            "💡 Examples: 'Smart Money', 'Ansem', 'Dev Team'\n\n"
            "Or type 'skip' to leave unnamed:"
        )
        return
    
    # Add wallet flow - step 2: get label
    if step == "awaiting_wallet_label":
        label = text if text.lower() != "skip" else "Unnamed Wallet"
        address = state.get("wallet_address")
        
        if address:
            from core.tracker import Tracker
            
            if Tracker.add_wallet(user_id, address, label):
                # Clear state
                context.bot_data["user_states"].pop(user_id, None)
                
                keyboard = [
                    [InlineKeyboardButton("👛 View Wallets", callback_data="wallet_list")],
                    [InlineKeyboardButton("🏠 Home", callback_data="home")]
                ]
                await update.message.reply_text(
                    f"✅ Wallet Added Successfully\n\n"
                    f"🏷️ Label: {label}\n"
                    f"📍 Address: {address[:10]}...{address[-8:]}\n\n"
                    f"🔔 You'll be alerted when this wallet buys into your tracked coins!",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                keyboard = [[InlineKeyboardButton("◀ Back", callback_data="menu_wallets")]]
                await update.message.reply_text(
                    "❌ Unable to Add Wallet\n\n"
                    "This wallet may already be tracked.\n\n"
                    "Check your wallet list or try a different address.",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                context.bot_data["user_states"].pop(user_id, None)
        return
    
    # Create list flow
    if step == "awaiting_list_name":
        list_name = text
        
        from core.tracker import Tracker
        
        if Tracker.create_list(user_id, list_name):
            context.bot_data["user_states"].pop(user_id, None)
            
            keyboard = [
                [InlineKeyboardButton("📋 View Lists", callback_data="list_view")],
                [InlineKeyboardButton("🏠 Home", callback_data="home")]
            ]
            await update.message.reply_text(
                f"✅ List Created\n\n"
                f"🏷️ Name: {list_name}\n\n"
                f"💡 Next: Add coins to your list to track narratives!\n"
                f"You'll get meta alerts when the whole list starts pumping.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            keyboard = [[InlineKeyboardButton("➡️ Try Different Name", callback_data="list_create")]]
            await update.message.reply_text(
                "❌ Name Already Used\n\n"
                f"You already have a list named '{list_name}'.\n\n"
                "Choose a different name.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            context.bot_data["user_states"].pop(user_id, None)
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
            await update.message.reply_text("❌ Invalid number. Try again.")


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
    
    # Check if webhook mode
    webhook_config = get_webhook_config()
    
    if webhook_config:
        print(f"🌐 Starting in WEBHOOK mode")
        print(f"   URL: {webhook_config['webhook_url']}")
        print(f"   Port: {webhook_config['port']}")
        print("=" * 50)
        
        setup_webhook(
            app,
            webhook_config["webhook_url"],
            webhook_config["port"]
        )
    else:
        print("🔄 Starting in POLLING mode")
        print("=" * 50)
        print("🟢 Bot starting...\n")
        
        # Run polling
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )


if __name__ == "__main__":
    main()
