"""UI for viewing alert history."""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from alert_history import get_user_history, get_history_stats
from datetime import datetime


async def show_alert_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show alert history dashboard."""
    query = update.callback_query
    user_id = query.from_user.id
    
    stats = get_history_stats(user_id)
    recent = get_user_history(user_id, limit=10)
    
    text = "📊 Alert History\n\n"
    
    # Stats
    text += f"Total Alerts: {stats['total_alerts']}\n\n"
    
    if stats['alerts_by_type']:
        text += "By Type:\n"
        for alert_type, count in sorted(stats['alerts_by_type'].items(), key=lambda x: x[1], reverse=True):
            text += f"  • {alert_type}: {count}\n"
        text += "\n"
    
    if stats['most_alerted_coin']:
        ca = stats['most_alerted_coin']
        text += f"Most Alerted: {ca[:8]}...{ca[-6:]}\n\n"
    
    # Recent alerts
    if recent:
        text += "Recent Alerts (10 max):\n\n"
        for alert in recent:
            timestamp = datetime.fromisoformat(alert['timestamp'])
            time_str = timestamp.strftime("%m/%d %H:%M")
            alert_type = alert['type']
            ca = alert['ca']
            
            text += f"{time_str} - {alert_type}\n"
            text += f"  {ca[:8]}...{ca[-4:]}\n"
            
            # Show key details
            details = alert.get('details', {})
            if 'mc' in details:
                text += f"  MC: ${int(details['mc']):,}\n"
            if 'pct' in details:
                text += f"  Change: {details['pct']:.1f}%\n"
            
            text += "\n"
    else:
        text += "No alerts yet.\n"
    
    keyboard = [
        [InlineKeyboardButton("🗑️ Clear History", callback_data="history_clear")],
        [InlineKeyboardButton("◀ Back", callback_data="menu_home")]
    ]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def clear_history_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm clearing alert history."""
    query = update.callback_query
    
    text = "⚠️ Clear Alert History\n\nThis will delete all your alert records. Continue?"
    
    keyboard = [
        [InlineKeyboardButton("✅ Yes, Clear", callback_data="history_clear_confirmed")],
        [InlineKeyboardButton("❌ Cancel", callback_data="alert_history")]
    ]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def clear_history_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Actually clear the history."""
    query = update.callback_query
    user_id = query.from_user.id
    
    from alert_history import clear_user_history
    clear_user_history(user_id)
    
    await query.message.reply_text("✅ Alert history cleared")
