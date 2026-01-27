#!/usr/bin/env python3
"""
Plans & Pricing Logic

LOCKED PLAN STRUCTURE:
- free: $0 - Basic coin alerts only
- basic: $10/mo - Wallet alerts (private only) + loud alerts
- pro: $50/mo - Full access (wallets, lists, meta, groups)
- owner: $0 - You only, full access, no limits

Owner bypasses ALL gates. Zero friction.
"""

from settings import get_chat_settings

# 👑 OWNER IDS - Full access, no limits, no checks
OWNER_IDS = [7483359361]  # Your Telegram user ID


def is_owner(user_id: int) -> bool:
    """Check if user is owner (bypasses all gates)."""
    return int(user_id) in OWNER_IDS


def get_plan(chat: dict, user_id: int) -> str:
    """
    Get user's subscription plan.
    
    Args:
        chat: Chat settings dict from get_chat_settings()
        user_id: Telegram user ID
        
    Returns:
        Plan name: "owner", "pro", "basic", or "free"
    """
    if is_owner(user_id):
        return "owner"
    
    return chat.get("plan", "free")


def can_wallet_alerts(chat: dict, user_id: int, is_group: bool = False) -> bool:
    """
    Check if user can use wallet buy alerts.
    
    Rules:
    - Owner: Always yes
    - Pro: Always yes
    - Basic: Yes if private chat (no in groups)
    - Free: No
    """
    if is_owner(user_id):
        return True

    plan = get_plan(chat, user_id)

    if plan == "pro":
        return True

    if plan == "basic" and not is_group:
        return True

    return False


def can_meta_alerts(chat: dict, user_id: int) -> bool:
    """
    Check if user can use meta/list-wide alerts.
    
    Rules:
    - Owner: Always yes
    - Pro: Yes
    - Basic/Free: No
    """
    if is_owner(user_id):
        return True
    
    return get_plan(chat, user_id) == "pro"


def can_loud_alerts(chat: dict, user_id: int) -> bool:
    """
    Check if user can receive loud (sound) alerts.
    
    Rules:
    - Owner: Always yes
    - Pro: Yes
    - Basic: Yes
    - Free: No (silent only)
    """
    if is_owner(user_id):
        return True
    
    return get_plan(chat, user_id) in ["basic", "pro"]


def get_max_coins(user_id: int) -> int:
    """
    Get max number of coins user can track.
    
    Limits:
    - Owner: Unlimited (999999)
    - Pro: 100
    - Basic: 20
    - Free: 3
    """
    if is_owner(user_id):
        return 999999
    
    # Get plan from settings (need user_id as chat key for individual users)
    chat = get_chat_settings(user_id)
    plan = get_plan(chat, user_id)
    
    limits = {
        "pro": 100,
        "basic": 20,
        "free": 3
    }
    
    return limits.get(plan, 3)


def get_max_wallets(user_id: int) -> int:
    """
    Get max number of wallets user can track.
    
    Limits:
    - Owner: Unlimited (999999)
    - Pro: 25
    - Basic: 5
    - Free: 0
    """
    if is_owner(user_id):
        return 999999
    
    chat = get_chat_settings(user_id)
    plan = get_plan(chat, user_id)
    
    limits = {
        "pro": 25,
        "basic": 5,
        "free": 0
    }
    
    return limits.get(plan, 0)


def get_max_lists(user_id: int) -> int:
    """
    Get max number of lists user can create.
    
    Limits:
    - Owner: Unlimited (999999)
    - Pro: 10
    - Basic: 0
    - Free: 0
    """
    if is_owner(user_id):
        return 999999
    
    chat = get_chat_settings(user_id)
    plan = get_plan(chat, user_id)
    
    limits = {
        "pro": 10,
        "basic": 0,
        "free": 0
    }
    
    return limits.get(plan, 0)


def get_upgrade_prompt(user_id: int, feature: str) -> str:
    """
    Get upgrade prompt for locked feature.
    
    Args:
        user_id: Telegram user ID
        feature: Feature name (e.g., "Wallet Buy Alerts")
        
    Returns:
        Formatted upgrade message (empty if owner)
    """
    if is_owner(user_id):
        return ""  # Owner never sees upgrade prompts
    
    chat = get_chat_settings(user_id)
    plan = get_plan(chat, user_id)
    
    msg = (
        f"🔒 Premium Feature\n\n"
        f"{feature} is not available on your plan.\n\n"
        f"💵 BASIC — $10/month\n"
        f"• 20 coins\n"
        f"• Wallet alerts (private only)\n"
        f"• Loud alerts\n\n"
        f"💎 PRO — $50/month\n"
        f"• 100 coins\n"
        f"• Wallet alerts (25 wallets)\n"
        f"• Lists & Meta alerts (10 lists)\n"
        f"• Group features\n\n"
        f"Current plan: {plan.upper()}"
    )
    
    return msg


def set_user_plan(user_id: int, plan: str) -> bool:
    """
    Set user's plan (admin/owner only).
    
    Args:
        user_id: Telegram user ID
        plan: Plan name ("free", "basic", "pro", "owner")
        
    Returns:
        True if successful, False if invalid plan
    """
    valid_plans = ["free", "basic", "pro", "owner"]
    
    if plan not in valid_plans:
        return False
    
    from settings import set_chat_setting
    set_chat_setting(user_id, "plan", plan)
    return True
