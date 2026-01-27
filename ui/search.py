"""Search and filter functionality for coins."""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.tracker import Tracker
from mc import get_market_cap


async def start_coin_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start coin search flow."""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Set state
    if "user_states" not in context.bot_data:
        context.bot_data["user_states"] = {}
    
    context.bot_data["user_states"][user_id] = {"step": "searching_coin"}
    
    text = "🔍 Search Coins\n\nSend part of the contract address to search:"
    
    await query.message.reply_text(text)


async def handle_coin_search(update: Update, context: ContextTypes.DEFAULT_TYPE, search_term: str, user_id: int):
    """Handle coin search query."""
    coins = Tracker.get_user_coins(user_id)
    
    if not coins:
        await update.message.reply_text("No coins to search.")
        return
    
    # Search by CA (partial match)
    search_lower = search_term.lower()
    matches = []
    
    for i, coin in enumerate(coins):
        ca = coin.get("ca", "")
        if search_lower in ca.lower():
            matches.append((i, coin))
    
    if not matches:
        await update.message.reply_text(f"No coins found matching: {search_term}")
        return
    
    text = f"🔍 Found {len(matches)} match(es):\n\n"
    
    for i, (original_index, coin) in enumerate(matches):
        ca = coin.get("ca", "")
        start_mc = coin.get("start_mc", 0)
        alerts = coin.get("alerts", {})
        paused = coin.get("paused", False)
        
        # Try to get current data
        token = get_market_cap(ca)
        
        text += f"{i+1}. {ca[:8]}...{ca[-6:]}\n"
        
        if token and token.get("mc"):
            current_mc = token["mc"]
            multiple = current_mc / start_mc if start_mc > 0 else 1
            change_pct = ((current_mc - start_mc) / start_mc * 100) if start_mc > 0 else 0
            
            text += f"   MC: ${int(current_mc):,}\n"
            text += f"   {multiple:.2f}x ({change_pct:+.1f}%)\n"
        else:
            text += f"   Start MC: ${int(start_mc):,}\n"
        
        status = "⏸️ Paused" if paused else "▶️ Active"
        text += f"   {status}\n"
        
        # Show configured alerts
        alert_types = []
        if "mc" in alerts:
            alert_types.append(f"${int(alerts['mc']):,}")
        if "pct" in alerts:
            alert_types.append(f"±{int(alerts['pct'])}%")
        if "x" in alerts:
            alert_types.append(f"{alerts['x']}x")
        if alerts.get("reclaim"):
            alert_types.append("ATH")
        
        if alert_types:
            text += f"   🔔 {', '.join(alert_types)}\n"
        
        text += "\n"
    
    keyboard = [[InlineKeyboardButton("◀ Back", callback_data="coin_list")]]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def pause_all_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pause all coins for user."""
    query = update.callback_query
    user_id = query.from_user.id
    
    from storage import load_data, save_data
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in data:
        await query.message.reply_text("No coins to pause.")
        return
    
    user_data = data[user_id_str]
    coins = user_data.get("coins", []) if isinstance(user_data, dict) else user_data
    
    count = 0
    for coin in coins:
        if not coin.get("paused", False):
            coin["paused"] = True
            count += 1
    
    save_data(data)
    
    await query.message.reply_text(f"✅ Paused {count} coin(s)")


async def resume_all_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Resume all coins for user."""
    query = update.callback_query
    user_id = query.from_user.id
    
    from storage import load_data, save_data
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in data:
        await query.message.reply_text("No coins to resume.")
        return
    
    user_data = data[user_id_str]
    coins = user_data.get("coins", []) if isinstance(user_data, dict) else user_data
    
    count = 0
    for coin in coins:
        if coin.get("paused", False):
            coin["paused"] = False
            count += 1
    
    save_data(data)
    
    await query.message.reply_text(f"✅ Resumed {count} coin(s)")


async def delete_all_coins_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm deleting all coins."""
    query = update.callback_query
    
    text = "⚠️ Delete All Coins\n\nThis will remove ALL tracked coins and their alerts. Continue?"
    
    keyboard = [
        [InlineKeyboardButton("✅ Yes, Delete All", callback_data="coin_delete_all_confirmed")],
        [InlineKeyboardButton("❌ Cancel", callback_data="coin_list")]
    ]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def delete_all_coins_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Actually delete all coins."""
    query = update.callback_query
    user_id = query.from_user.id
    
    from storage import load_data, save_data
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in data:
        await query.message.reply_text("No coins to delete.")
        return
    
    user_data = data[user_id_str]
    
    if isinstance(user_data, dict):
        count = len(user_data.get("coins", []))
        user_data["coins"] = []
    else:
        count = len(user_data)
        data[user_id_str] = []
    
    save_data(data)
    
    await query.message.reply_text(f"✅ Deleted {count} coin(s)")
