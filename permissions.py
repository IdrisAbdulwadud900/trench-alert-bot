#!/usr/bin/env python3
"""
Feature Permissions & Monetization Logic

This module handles access control for premium features.
Monetization = permissions, NOT new features.

Tiers:
- Free: Basic coin tracking, silent alerts only
- Basic ($10/month): Wallet alerts (limited), loud alerts
- Pro ($50/month): Everything - wallets, lists, meta, groups
- Owner: Full access, no limits (YOU)
"""

from settings import get_chat_settings

# 👑 OWNER IDS - Full access, no limits, no checks
OWNER_IDS = [7483359361]  # Add your Telegram user ID here


def is_owner(user_id):
    """Check if user is owner (bypasses all gates)."""
    return int(user_id) in OWNER_IDS


def get_user_plan(user_id):
    """
    Get user's subscription plan.
    
    Returns:
        "owner", "free", "basic", or "pro"
    """
    if is_owner(user_id):
        return "owner"
    
    settings = get_chat_settings(user_id)
    return settings.get("plan", "free")


def can_use_wallet_alerts(user_id, is_group=False):
    """
    Check if user/group can use wallet buy alerts.
    
    Free: NO
    Basic: YES (private only)
    Pro: YES (private + groups)
    Owner: YES (always)
    """
    if is_owner(user_id):
        return True
    
    plan = get_user_plan(user_id)
    
    if plan == "pro":
        return True
    
    if plan == "basic" and not is_group:
        return True
    
    return False


def can_use_meta_alerts(user_id, is_group=False):
    """
    Check if user/group can use meta/list alerts.
    
    Free: NO
    Basic: NO
    Pro: YES
    Owner: YES (always)
    """
    if is_owner(user_id):
        return True
    
    plan = get_user_plan(user_id)
    return plan == "pro"


def can_use_loud_alerts(user_id):
    """
    Check if user can use loud (sound) alerts.
    
    Free: NO (silent only)
    Basic: YES
    Pro: YES
    Owner: YES (always)
    """
    if is_owner(user_id):
        return True
    
    plan = get_user_plan(user_id)
    return plan in ["basic", "pro"]


def get_max_coins(user_id):
    """Get maximum number of coins user can track."""
    if is_owner(user_id):
        return 999999  # Unlimited
    
    plan = get_user_plan(user_id)
    
    limits = {
        "free": 3,
        "basic": 20,
        "pro": 100
    }
    
    return limits.get(plan, 3)


def get_max_wallets(user_id):
    """Get maximum number of wallets user can watch."""
    if is_owner(user_id):
        return 999999  # Unlimited
    
    plan = get_user_plan(user_id)
    
    limits = {
        "free": 0,
        "basic": 5,
        "pro": 25
    }
    
    return limits.get(plan, 0)


def get_max_lists(user_id):
    """Get maximum number of lists user can create."""
    if is_owner(user_id):
        return 999999  # Unlimited
    
    plan = get_user_plan(user_id)
    
    limits = {
        "free": 0,
        "basic": 0,
        "pro": 10
    }
    
    return limits.get(plan, 0)


def get_upgrade_prompt(user_id, feature):
    """
    Get upgrade message when user hits a premium feature.
    
    Args:
        user_id: User ID
        feature: Feature name (wallet_alerts, meta_alerts, loud_alerts)
    
    Returns:
        Professional upgrade message
    """
    if is_owner(user_id):
        return ""  # Owner never sees upgrade prompts
    
    plan = get_user_plan(user_id)
    
    messages = {
        "wallet_alerts": (
            "🔒 Premium Feature\n\n"
            "Wallet buy alerts track smart money on-chain.\n\n"
            "Available on:\n"
            "• Basic ($10/mo) - Private chats only\n"
            "• Pro ($50/mo) - Private + Groups\n\n"
            f"Your plan: {plan.upper()}"
        ),
        "meta_alerts": (
            "🔒 Pro Feature\n\n"
            "Meta alerts detect narrative rotation.\n\n"
            "Available on:\n"
            "• Pro ($50/mo) - Multi-coin analysis\n\n"
            f"Your plan: {plan.upper()}"
        ),
        "loud_alerts": (
            "🔒 Premium Feature\n\n"
            "Loud alerts ensure you never miss a move.\n\n"
            "Available on:\n"
            "• Basic ($10/mo)\n"
            "• Pro ($50/mo)\n\n"
            f"Your plan: {plan.upper()}"
        ),
        "max_coins": (
            f"🔒 Coin Limit Reached\n\n"
            f"Free: 3 coins\n"
            f"Basic: 20 coins\n"
            f"Pro: 100 coins\n\n"
            f"Your plan: {plan.upper()}"
        ),
        "max_wallets": (
            f"🔒 Wallet Limit Reached\n\n"
            f"Free: 0 wallets\n"
            f"Basic: 5 wallets\n"
            f"Pro: 25 wallets\n\n"
            f"Your plan: {plan.upper()}"
        ),
        "max_lists": (
            f"🔒 List Limit Reached\n\n"
            f"Free: 0 lists\n"
            f"Basic: 0 lists\n"
            f"Pro: 10 lists\n\n"
            f"Your plan: {plan.upper()}"
        )
    }
    
    return messages.get(feature, "🔒 Premium Feature\n\nUpgrade to unlock.")


def check_permission(user_id, feature, is_group=False):
    """
    Generic permission check.
    
    Args:
        user_id: User/group ID
        feature: Feature name
        is_group: Whether this is a group chat
    
    Returns:
        (allowed: bool, message: str)
    """
    checks = {
        "wallet_alerts": can_use_wallet_alerts,
        "meta_alerts": can_use_meta_alerts,
        "loud_alerts": can_use_loud_alerts
    }
    
    check_fn = checks.get(feature)
    
    if check_fn is None:
        return False, "Unknown feature"
    
    # Call appropriate check
    if feature in ["wallet_alerts", "meta_alerts"]:
        allowed = check_fn(user_id, is_group)
    else:
        allowed = check_fn(user_id)
    
    if allowed:
        return True, ""
    else:
        return False, get_upgrade_prompt(user_id, feature)


# Admin function to upgrade users (for manual upgrades, future payment integration)
def set_user_plan(user_id, plan):
    """
    Set user's subscription plan.
    
    Args:
        user_id: User ID
        plan: "free", "basic", "pro", or "owner"
    """
    from settings import set_chat_setting
    
    if plan not in ["free", "basic", "pro", "owner"]:
        raise ValueError(f"Invalid plan: {plan}")
    
    set_chat_setting(user_id, "plan", plan)


if __name__ == "__main__":
    # Test permission system
    print("=== Permission System Test ===\n")
    
    # Free user
    test_user = "123456789"
    print(f"User plan: {get_user_plan(test_user)}")
    print(f"Can use wallet alerts: {can_use_wallet_alerts(test_user)}")
    print(f"Can use meta alerts: {can_use_meta_alerts(test_user)}")
    print(f"Can use loud alerts: {can_use_loud_alerts(test_user)}")
    print(f"Max coins: {get_max_coins(test_user)}")
    print(f"Max wallets: {get_max_wallets(test_user)}")
    print(f"Max lists: {get_max_lists(test_user)}")
    
    print("\n" + "="*50 + "\n")
    
    # Upgrade to pro
    set_user_plan(test_user, "pro")
    print(f"Upgraded to: {get_user_plan(test_user)}")
    print(f"Can use wallet alerts: {can_use_wallet_alerts(test_user)}")
    print(f"Can use meta alerts: {can_use_meta_alerts(test_user)}")
    print(f"Max coins: {get_max_coins(test_user)}")
    print(f"Max wallets: {get_max_wallets(test_user)}")
    
    print("\n" + "="*50 + "\n")
    
    # Test upgrade prompts
    set_user_plan(test_user, "free")
    allowed, msg = check_permission(test_user, "wallet_alerts")
    if not allowed:
        print("Wallet alerts prompt:")
        print(msg)
