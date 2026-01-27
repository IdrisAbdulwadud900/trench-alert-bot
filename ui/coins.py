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
        [InlineKeyboardButton("🗑️ Remove Coin", callback_data="coin_remove")],
        [InlineKeyboardButton("◀ Back", callback_data="home")]
    ]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_coin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of tracked coins with live data."""
    query = update.callback_query
    user_id = query.from_user.id
    
    coins = Tracker.get_user_coins(user_id)
    
    if not coins:
        await query.message.reply_text(
            "No coins tracked yet.\n\nUse ➕ Add Coin to start."
        )
        return
    
    text = "📋 Your Coins\n\n"
    
    from mc import get_market_cap
    
    for i, coin in enumerate(coins, 1):
        ca = coin.get("ca", "Unknown")
        start_mc = coin.get("start_mc", 0)
        alerts = coin.get("alerts", {})
        
        # Try to get live data
        token = get_market_cap(ca)
        
        if token and token.get("mc"):
            current_mc = token["mc"]
            multiple = current_mc / start_mc if start_mc > 0 else 1
            change_pct = ((current_mc - start_mc) / start_mc * 100) if start_mc > 0 else 0
            
            text += f"{i}. {ca[:6]}...{ca[-4:]}\n"
            text += f"   MC: ${int(current_mc):,}\n"
            text += f"   {multiple:.2f}x | {change_pct:+.1f}%\n"
        else:
            text += f"{i}. {ca[:6]}...{ca[-4:]}\n"
            text += f"   (Unable to fetch data)\n"
        
        # Show configured alerts
        alert_types = []
        if "mc" in alerts:
            alert_types.append(f"MC≤${int(alerts['mc']):,}")
        if "pct" in alerts:
            alert_types.append(f"±{int(alerts['pct'])}%")
        if "x" in alerts:
            alert_types.append(f"{alerts['x']}x")
        if alerts.get("reclaim"):
            alert_types.append("ATH")
        
        if alert_types:
            text += f"   🔔 {', '.join(alert_types)}\n"
        else:
            text += f"   🔕 No alerts\n"
        
        text += "\n"
    
    keyboard = [
        [InlineKeyboardButton("🔍 Search", callback_data="coin_search")],
        [InlineKeyboardButton("✏️ Edit Alerts", callback_data="coin_edit_alerts")],
        [InlineKeyboardButton("⏸️ Pause All", callback_data="coin_pause_all"),
         InlineKeyboardButton("▶️ Resume All", callback_data="coin_resume_all")],
        [InlineKeyboardButton("🗑️ Delete All", callback_data="coin_delete_all")],
        [InlineKeyboardButton("◀ Back", callback_data="menu_coins")]
    ]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
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


async def show_configure_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE, ca: str, mc: float):
    """Show alert configuration options."""
    text = (
        f"✅ Token Detected\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Market Cap: ${int(mc):,}\n\n"
        f"Configure alerts:\n"
        f"(Select multiple or skip)"
    )
    
    keyboard = [
        [InlineKeyboardButton("📉 MC Target", callback_data=f"alert_config_mc")],
        [InlineKeyboardButton("📈 % Move", callback_data=f"alert_config_pct")],
        [InlineKeyboardButton("🚀 X Multiple", callback_data=f"alert_config_x")],
        [InlineKeyboardButton("🔥 ATH Reclaim", callback_data=f"alert_config_reclaim")],
        [InlineKeyboardButton("✅ Done (No Alerts)", callback_data=f"alert_config_done")],
    ]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_remove_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show coins with remove option."""
    query = update.callback_query
    user_id = query.from_user.id
    
    coins = Tracker.get_user_coins(user_id)
    
    if not coins:
        await query.message.reply_text("No coins to remove.")
        return
    
    text = "🗑️ Remove Coin\n\nSelect coin to remove:"
    
    keyboard = []
    for i, coin in enumerate(coins):
        ca = coin.get("ca", "Unknown")
        keyboard.append([
            InlineKeyboardButton(
                f"{ca[:8]}...{ca[-6:]}",
                callback_data=f"remove_coin_{i}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("◀ Back", callback_data="menu_coins")])
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def confirm_remove_coin(update: Update, context: ContextTypes.DEFAULT_TYPE, coin_index: int):
    """Remove a coin by index."""
    query = update.callback_query
    user_id = query.from_user.id
    
    coins = Tracker.get_user_coins(user_id)
    
    if coin_index >= len(coins):
        await query.message.reply_text("❌ Invalid coin selection.")
        return
    
    coin = coins[coin_index]
    ca = coin.get("ca")
    
    if Tracker.remove_coin(user_id, ca):
        await query.message.reply_text(
            f"✅ Coin Removed\n\n{ca[:8]}...{ca[-6:]}"
        )
    else:
        await query.message.reply_text("❌ Error removing coin.")


async def handle_pause_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show coins with pause/resume option."""
    query = update.callback_query
    user_id = query.from_user.id
    
    coins = Tracker.get_user_coins(user_id)
    
    if not coins:
        await query.message.reply_text("No coins to pause.")
        return
    
    text = "⏸️ Pause/Resume Coins\n\nSelect coin:"
    
    keyboard = []
    for i, coin in enumerate(coins):
        ca = coin.get("ca", "")
        paused = coin.get("paused", False)
        status = "⏸️" if paused else "▶️"
        
        keyboard.append([
            InlineKeyboardButton(
                f"{status} {ca[:8]}...{ca[-6:]}",
                callback_data=f"toggle_pause_{i}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("◀ Back", callback_data="coin_list")])
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def toggle_pause_coin(update: Update, context: ContextTypes.DEFAULT_TYPE, coin_index: int):
    """Toggle pause state of a coin."""
    query = update.callback_query
    user_id = query.from_user.id
    
    from storage import load_data, save_data
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in data:
        await query.message.reply_text("❌ Error toggling pause state.")
        return
    
    user_data = data[user_id_str]
    if isinstance(user_data, dict):
        coins = user_data.get("coins", [])
    else:
        coins = user_data
    
    if coin_index >= len(coins):
        await query.message.reply_text("❌ Invalid coin selection.")
        return
    
    coin = coins[coin_index]
    current_state = coin.get("paused", False)
    coin["paused"] = not current_state
    
    save_data(data)
    
    status = "Paused" if coin["paused"] else "Resumed"
    await query.message.reply_text(f"✅ {status}: {coin.get('ca', '')[:8]}...")


async def handle_edit_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show coins to select for editing alerts."""
    query = update.callback_query
    user_id = query.from_user.id
    
    coins = Tracker.get_user_coins(user_id)
    
    if not coins:
        await query.message.reply_text("No coins to edit.")
        return
    
    text = "✏️ Edit Alerts\n\nSelect coin to modify:"
    
    keyboard = []
    for i, coin in enumerate(coins):
        ca = coin.get("ca", "")
        keyboard.append([
            InlineKeyboardButton(
                f"{ca[:8]}...{ca[-6:]}",
                callback_data=f"edit_alerts_{i}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("◀ Back", callback_data="coin_list")])
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_edit_alert_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, coin_index: int):
    """Show alert editing menu for a specific coin."""
    query = update.callback_query
    user_id = query.from_user.id
    
    coins = Tracker.get_user_coins(user_id)
    
    if coin_index >= len(coins):
        await query.message.reply_text("❌ Invalid coin selection.")
        return
    
    coin = coins[coin_index]
    ca = coin.get("ca", "")
    alerts = coin.get("alerts", {})
    
    text = f"✏️ Edit Alerts\n{ca[:8]}...{ca[-6:]}\n\n"
    text += "Current alerts:\n"
    
    if "mc" in alerts:
        text += f"📉 MC: ${int(alerts['mc']):,}\n"
    if "pct" in alerts:
        text += f"📈 %: ±{int(alerts['pct'])}%\n"
    if "x" in alerts:
        text += f"🚀 X: {alerts['x']}x\n"
    if alerts.get("reclaim"):
        text += f"🔥 ATH Reclaim: ON\n"
    
    if not alerts:
        text += "(No alerts configured)\n"
    
    text += "\nSelect alert to modify:"
    
    keyboard = [
        [InlineKeyboardButton("📉 MC Target", callback_data=f"edit_mc_{coin_index}")],
        [InlineKeyboardButton("📈 % Move", callback_data=f"edit_pct_{coin_index}")],
        [InlineKeyboardButton("🚀 X Multiple", callback_data=f"edit_x_{coin_index}")],
        [InlineKeyboardButton("🔥 Toggle ATH Reclaim", callback_data=f"edit_reclaim_{coin_index}")],
        [InlineKeyboardButton("🗑️ Clear All Alerts", callback_data=f"clear_alerts_{coin_index}")],
        [InlineKeyboardButton("◀ Back", callback_data="coin_edit_alerts")]
    ]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


