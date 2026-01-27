"""Admin dashboard for monitoring and management."""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from storage import load_data
from wallets import load_wallets
from lists import load_lists
from alert_history import load_history
from rate_limiter import api_limiter
from cache_layer import cache
import os


async def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    admin_ids = os.getenv("ADMIN_IDS", "").split(",")
    return str(user_id) in admin_ids


async def show_admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin dashboard with system stats."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not await is_admin(user_id):
        await query.message.reply_text("❌ Admin access required")
        return
    
    # Gather stats
    data = load_data()
    wallets_data = load_wallets()
    lists_data = load_lists()
    history_data = load_history()
    
    # User stats
    total_users = len(data)
    total_coins = sum(
        len(user_data.get("coins", []) if isinstance(user_data, dict) else user_data)
        for user_data in data.values()
    )
    total_wallets = sum(len(wallets) for wallets in wallets_data.values())
    total_lists = sum(len(lists) for lists in lists_data.values())
    total_alerts = sum(len(alerts) for alerts in history_data.values())
    
    # API stats
    dex_stats = api_limiter.get_stats("dexscreener")
    rpc_stats = api_limiter.get_stats("solana_rpc")
    
    text = (
        "<b>🔧 ADMIN DASHBOARD</b>\n\n"
        f"<b>📊 System Stats:</b>\n"
        f"  • Users: {total_users}\n"
        f"  • Tracked Coins: {total_coins}\n"
        f"  • Watched Wallets: {total_wallets}\n"
        f"  • Lists: {total_lists}\n"
        f"  • Alerts Fired: {total_alerts}\n\n"
        f"<b>🌐 API Usage (last hour):</b>\n"
        f"  • DexScreener: {dex_stats['requests_last_hour']} req\n"
        f"  • Solana RPC: {rpc_stats['requests_last_hour']} req\n\n"
        f"<b>💾 Cache:</b>\n"
        f"  • Memory entries: {len(cache.memory_cache)}\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("👥 User List", callback_data="admin_users")],
        [InlineKeyboardButton("📈 Detailed Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("🗑️ Clear Cache", callback_data="admin_clear_cache")],
        [InlineKeyboardButton("◀ Back", callback_data="menu_settings")]
    ]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def show_admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of all users."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not await is_admin(user_id):
        await query.message.reply_text("❌ Admin access required")
        return
    
    data = load_data()
    
    text = "<b>👥 USER LIST</b>\n\n"
    
    for user_id_str, user_data in list(data.items())[:20]:  # Show first 20
        if isinstance(user_data, dict):
            coins_count = len(user_data.get("coins", []))
        else:
            coins_count = len(user_data)
        
        text += f"• <code>{user_id_str}</code> - {coins_count} coins\n"
    
    if len(data) > 20:
        text += f"\n...and {len(data) - 20} more users"
    
    keyboard = [[InlineKeyboardButton("◀ Back", callback_data="admin_dashboard")]]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def admin_clear_cache(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear API cache."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not await is_admin(user_id):
        await query.message.reply_text("❌ Admin access required")
        return
    
    cache.clear()
    
    await query.answer("✅ Cache cleared")
    await show_admin_dashboard(update, context)


async def show_admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed stats."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not await is_admin(user_id):
        await query.message.reply_text("❌ Admin access required")
        return
    
    # Get detailed API stats
    endpoints = ["dexscreener", "solana_rpc", "wallet_alerts"]
    
    text = "<b>📈 DETAILED STATS</b>\n\n"
    
    for endpoint in endpoints:
        stats = api_limiter.get_stats(endpoint)
        text += f"<b>{endpoint}:</b>\n"
        text += f"  • Last minute: {stats['requests_last_minute']} req\n"
        text += f"  • Last hour: {stats['requests_last_hour']} req\n"
        text += f"  • Total: {stats['total_requests']} req\n\n"
    
    keyboard = [[InlineKeyboardButton("◀ Back", callback_data="admin_dashboard")]]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
