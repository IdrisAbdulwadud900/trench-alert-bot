#!/usr/bin/env python3
"""
Settings UI - Clean & Focused
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from settings import get_alert_mode, set_alert_mode
from plans import get_plan, is_owner
from settings import get_chat_settings


async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings menu."""
    query = update.callback_query
    user_id = query.from_user.id
    
    chat = get_chat_settings(user_id)
    plan = get_plan(chat, user_id)
    alert_mode = get_alert_mode(user_id)
    
    plan_names = {
        "free": "FREE",
        "basic": "BASIC ($10/mo)",
        "pro": "PRO ($50/mo)",
        "owner": "OWNER"
    }
    
    text = (
        f"⚙️ Settings\n\n"
        f"Plan: {plan_names.get(plan, plan.upper())}\n"
        f"Alert Mode: {alert_mode.upper()}\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔔 Alert Mode", callback_data="setting_alert_mode")],
        [InlineKeyboardButton("💳 View Plans", callback_data="setting_plans")],
        [InlineKeyboardButton("◀ Back", callback_data="home")]
    ]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_alert_mode_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show alert mode selection."""
    query = update.callback_query
    user_id = query.from_user.id
    
    current_mode = get_alert_mode(user_id)
    
    text = (
        f"🔔 Alert Mode\n\n"
        f"Current: {current_mode.upper()}\n\n"
        f"• LOUD - Alerts with sound\n"
        f"• SILENT - Quiet notifications"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔊 Loud", callback_data="set_mode_loud")],
        [InlineKeyboardButton("🔕 Silent", callback_data="set_mode_silent")],
        [InlineKeyboardButton("◀ Back", callback_data="menu_settings")]
    ]
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
