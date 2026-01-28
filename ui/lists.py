#!/usr/bin/env python3
"""
Lists UI - Narrative Tracking
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.tracker import Tracker


async def show_lists_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show lists/narrative tracking menu."""
    query = update.callback_query
    user_id = query.from_user.id
    
    lists = Tracker.get_user_lists(user_id)
    list_count = len(lists)
    
    text = f"📋 Track Lists\n\nYou have {list_count} list(s)."
    
    keyboard = [
        [InlineKeyboardButton("➕ Create List", callback_data="list_create")],
        [InlineKeyboardButton("📋 View Lists", callback_data="list_view")],
        [InlineKeyboardButton("🔔 Meta Alerts", callback_data="list_meta")],
        [InlineKeyboardButton("◀ Back", callback_data="home")]
    ]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_lists_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all user lists."""
    query = update.callback_query
    user_id = query.from_user.id
    
    lists = Tracker.get_user_lists(user_id)
    
    if not lists:
        keyboard = [[InlineKeyboardButton("➕ Create Your First List", callback_data="list_create")],
                    [InlineKeyboardButton("◀ Back to Menu", callback_data="home")]]
        await query.message.reply_text(
            "📋 Lists\n\n"
            "No lists yet.\n\n"
            "💡 Create lists to group coins by narrative (AI, Gaming, DeFi, etc.)\n"
            "Get alerted when entire narratives start pumping!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    text = "📋 Your Lists\n\n"
    
    keyboard = []
    for i, lst in enumerate(lists):
        name = lst.get("name", "Unnamed")
        coins = lst.get("coins", [])
        
        text += f"{i+1}. {name} ({len(coins)} coins)\n"
        keyboard.append([
            InlineKeyboardButton(
                f"📂 {name}",
                callback_data=f"list_open_{i}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("◀ Back", callback_data="menu_lists")])
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def start_create_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start list creation flow."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if "user_states" not in context.bot_data:
        context.bot_data["user_states"] = {}
    
    context.bot_data["user_states"][user_id] = {"step": "awaiting_list_name"}
    
    await query.message.reply_text(
        "➕ Create List\n\n"
        "Send a name for your list:\n"
        "(e.g., 'AI Coins', 'Gaming', 'DeFi')"
    )


async def show_list_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, list_index: int):
    """Show detailed view of a list."""
    query = update.callback_query
    user_id = query.from_user.id
    
    lists = Tracker.get_user_lists(user_id)
    
    if list_index >= len(lists):
        await query.message.reply_text("❌ Invalid list selection.")
        return
    
    lst = lists[list_index]
    name = lst.get("name", "Unnamed")
    coins = lst.get("coins", [])
    
    text = f"📂 {name}\n\n"
    
    if not coins:
        text += "No coins in this list yet.\n"
    else:
        from mc import get_market_cap
        
        total_mc = 0
        pumping_count = 0
        
        for ca in coins:
            token = get_market_cap(ca)
            if token and token.get("mc"):
                mc = token["mc"]
                total_mc += mc
                text += f"• {ca[:6]}...{ca[-4:]} - ${int(mc):,}\n"
        
        text += f"\n💰 Total MC: ${int(total_mc):,}\n"
    
    keyboard = [
        [InlineKeyboardButton("➕ Add Coin", callback_data=f"list_add_coin_{list_index}")],
        [InlineKeyboardButton("🗑️ Delete List", callback_data=f"list_delete_{list_index}")],
        [InlineKeyboardButton("◀ Back", callback_data="list_view")]
    ]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_meta_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show meta alert configuration."""
    query = update.callback_query
    user_id = query.from_user.id
    
    from core.tracker import Tracker
    user_lists = Tracker.get_user_lists(user_id)
    
    if not user_lists:
        text = (
            "🔔 Meta Alerts\n\n"
            "Create lists first to set up meta alerts!\n\n"
            "Meta alerts notify you when:\n"
            "• N+ coins in a list are pumping\n"
            "• List total MC hits threshold\n"
            "• Volume surge across the list\n\n"
            "💡 Create a list and add coins to get started!"
        )
    else:
        text = (
            "🔔 Meta Alerts\n\n"
            f"You have {len(user_lists)} list(s) set up.\n\n"
            "Meta alerts track list-wide behavior:\n"
            "• When multiple coins pump together\n"
            "• Total list market cap changes\n"
            "• Coordinated volume activity\n\n"
            "💡 Meta alerts are automatically enabled for all lists!\n"
            "You'll be notified when narratives start moving."
        )
    
    keyboard = [[InlineKeyboardButton("◀ Back", callback_data="menu_lists")]]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
