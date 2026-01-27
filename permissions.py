#!/usr/bin/env python3
"""
Feature Permissions & Monetization Logic

This module handles access control for premium features.
Monetization = permissions, NOT new features.

Tiers:
- Free: Basic coin tracking, silent alerts only
- Pro: Wallet alerts, lists/meta, loud alerts  
- Group Pro: Group wallet alerts, meta alerts, priority delivery
"""

from settings import get_chat_settings


def get_user_plan(user_id):
    """
    Get user's subscription plan.
    
    Returns:
        "free", "pro", or "group_pro"
    """
    settings = get_chat_settings(user_id)
    return settings.get("plan", "free")


def can_use_wallet_alerts(user_id, is_group=False):
    """
    Check if user/group can use wallet buy alerts.
    
    Free tier: NO wallet alerts
    Pro tier: YES (private only)
    Group Pro: YES (groups)
    """
    plan = get_user_plan(user_id)
    
    if is_group:
        return plan == "group_pro"
    
    return plan in ["pro", "group_pro"]


def can_use_meta_alerts(user_id, is_group=False):
    """
    Check if user/group can use meta/list alerts.
    
    Free tier: NO
    Pro tier: YES (private)
    Group Pro: YES (groups)
    """
    plan = get_user_plan(user_id)
    
    if is_group:
        return plan == "group_pro"
    
    return plan in ["pro", "group_pro"]


def can_use_loud_alerts(user_id):
    """
    Check if user can use loud (sound) alerts.
    
    Free tier: Silent only
    Pro tier: YES
    Group Pro: YES
    """
    plan = get_user_plan(user_id)
    return plan in ["pro", "group_pro"]


def get_max_coins(user_id):
    """Get maximum number of coins user can track."""
    plan = get_user_plan(user_id)
    
    limits = {
        "free": 3,
        "pro": 50,
        "group_pro": 100
    }
    
    return limits.get(plan, 3)


def get_max_wallets(user_id):
    """Get maximum number of wallets user can watch."""
    plan = get_user_plan(user_id)
    
    limits = {
        "free": 0,  # No wallet alerts on free
        "pro": 10,
        "group_pro": 25
    }
    
    return limits.get(plan, 0)


def get_max_lists(user_id):
    """Get maximum number of lists user can create."""
    plan = get_user_plan(user_id)
    
    limits = {
        "free": 0,  # No lists on free
        "pro": 5,
        "group_pro": 10
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
    plan = get_user_plan(user_id)
    
    messages = {
        "wallet_alerts": (
            "🔒 Pro Feature\n\n"
            "Wallet buy alerts track smart money on-chain.\n\n"
            "Upgrade to Pro to unlock:\n"
            "• Real-time wallet tracking\n"
            "• Custom buy size filters\n"
            "• Up to 10 wallets\n\n"
            "Your plan: FREE"
        ),
        "meta_alerts": (
            "🔒 Pro Feature\n\n"
            "Meta alerts detect narrative rotation.\n\n"
            "Upgrade to Pro to unlock:\n"
            "• List-wide analysis\n"
            "• Multi-coin pumps\n"
            "• Sector heating signals\n\n"
            "Your plan: FREE"
        ),
        "loud_alerts": (
            "🔒 Pro Feature\n\n"
            "Loud alerts ensure you never miss a move.\n\n"
            "Upgrade to Pro to unlock:\n"
            "• Sound notifications\n"
            "• Priority delivery\n"
            "• Real-time pings\n\n"
            "Your plan: FREE"
        ),
        "max_coins": (
            f"🔒 Coin Limit Reached\n\n"
            f"Free plan: 3 coins\n"
            f"Pro plan: 50 coins\n\n"
            f"Upgrade to track more."
        ),
        "max_wallets": (
            f"🔒 Wallet Limit Reached\n\n"
            f"Free plan: 0 wallets\n"
            f"Pro plan: 10 wallets\n\n"
            f"Upgrade to track wallets."
        ),
        "max_lists": (
            f"🔒 List Limit Reached\n\n"
            f"Free plan: 0 lists\n"
            f"Pro plan: 5 lists\n\n"
            f"Upgrade to create lists."
        )
    }
    
    return messages.get(feature, "🔒 Pro Feature\n\nUpgrade to unlock.")


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
        plan: "free", "pro", or "group_pro"
    """
    from settings import set_chat_setting
    
    if plan not in ["free", "pro", "group_pro"]:
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
