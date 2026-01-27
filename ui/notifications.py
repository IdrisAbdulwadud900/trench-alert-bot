"""UI for notification settings."""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from notification_settings import get_user_notification_settings, update_notification_setting


async def show_notification_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show notification settings menu."""
    query = update.callback_query
    user_id = query.from_user.id
    
    settings = get_user_notification_settings(user_id)
    
    text = "🔔 Notification Settings\n\nToggle sound for each alert type:\n\n"
    
    alert_names = {
        "mc": "📉 MC Target",
        "pct": "📈 % Move",
        "x": "🚀 X Multiple",
        "reclaim": "🔥 ATH Reclaim",
        "volume": "📊 Volume Spike",
        "liquidity": "💧 Liquidity Drop",
        "wallet": "👛 Wallet Buy",
        "meta": "📋 Meta Alerts",
        "timebased": "⏰ Time-based",
        "combo": "🔥 Combo Alerts"
    }
    
    keyboard = []
    
    for alert_type, name in alert_names.items():
        enabled = settings.get(alert_type, True)
        status = "🔔" if enabled else "🔕"
        keyboard.append([
            InlineKeyboardButton(
                f"{status} {name}",
                callback_data=f"notif_toggle_{alert_type}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("◀ Back", callback_data="menu_settings")])
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def toggle_notification(update: Update, context: ContextTypes.DEFAULT_TYPE, alert_type: str):
    """Toggle notification for specific alert type."""
    query = update.callback_query
    user_id = query.from_user.id
    
    settings = get_user_notification_settings(user_id)
    current = settings.get(alert_type, True)
    new_value = not current
    
    update_notification_setting(user_id, alert_type, new_value)
    
    status = "enabled" if new_value else "disabled"
    await query.answer(f"Notifications {status}")
    
    # Refresh the menu
    await show_notification_settings(update, context)
