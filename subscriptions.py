#!/usr/bin/env python3
"""
Subscription and tier system for monetization

Defines feature gates and user tier management.
"""

import json
import os
import time
from typing import Dict, Optional

SUBS_FILE = "subscriptions.json"

# Tier definitions
TIERS = {
    "free": {
        "name": "Free",
        "price": 0,
        "limits": {
            "max_coins": 3,
            "max_wallets": 1,
            "max_lists": 1,
            "group_coins": 2,
            "meta_alerts": False,
            "wallet_alerts": False,
            "advanced_intelligence": False,
        }
    },
    "pro": {
        "name": "Pro",
        "price": 25,  # USD per month
        "limits": {
            "max_coins": 10,
            "max_wallets": 5,
            "max_lists": 5,
            "group_coins": 5,
            "meta_alerts": True,
            "wallet_alerts": True,
            "advanced_intelligence": True,
        }
    },
    "premium": {
        "name": "Premium",
        "price": 50,  # USD per month
        "limits": {
            "max_coins": 25,
            "max_wallets": 15,
            "max_lists": 15,
            "group_coins": 10,
            "meta_alerts": True,
            "wallet_alerts": True,
            "advanced_intelligence": True,
        }
    }
}

def load_subscriptions():
    """Load subscription data."""
    if not os.path.exists(SUBS_FILE):
        return {}
    
    try:
        with open(SUBS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_subscriptions(data):
    """Save subscription data."""
    try:
        with open(SUBS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Error saving subscriptions: {e}")

def get_user_tier(user_id: str) -> str:
    """Get user's subscription tier."""
    data = load_subscriptions()
    user_id = str(user_id)
    
    if user_id not in data:
        return "free"
    
    sub = data[user_id]
    
    # Check if subscription is active
    if sub.get("expires_at", 0) < time.time():
        return "free"  # Expired
    
    return sub.get("tier", "free")

def set_user_tier(user_id: str, tier: str, duration_days: int = 30) -> bool:
    """Set user's subscription tier."""
    if tier not in TIERS:
        return False
    
    data = load_subscriptions()
    user_id = str(user_id)
    
    data[user_id] = {
        "tier": tier,
        "started_at": time.time(),
        "expires_at": time.time() + (duration_days * 24 * 60 * 60),
        "auto_renew": False
    }
    
    save_subscriptions(data)
    return True

def get_user_limits(user_id: str) -> Dict:
    """Get user's feature limits based on tier."""
    tier = get_user_tier(user_id)
    return TIERS[tier]["limits"].copy()

def check_limit(user_id: str, feature: str, current_count: int) -> bool:
    """
    Check if user can add more of a feature.
    
    Returns True if under limit, False if at/over limit.
    """
    limits = get_user_limits(user_id)
    
    if feature not in limits:
        return True  # No limit defined
    
    limit = limits[feature]
    
    # Boolean features
    if isinstance(limit, bool):
        return limit
    
    # Count-based features
    return current_count < limit

def can_add_coin(user_id: str, current_count: int) -> bool:
    """Check if user can add another coin."""
    return check_limit(user_id, "max_coins", current_count)

def can_add_wallet(user_id: str, current_count: int) -> bool:
    """Check if user can add another wallet."""
    return check_limit(user_id, "max_wallets", current_count)

def can_add_list(user_id: str, current_count: int) -> bool:
    """Check if user can add another list."""
    return check_limit(user_id, "max_lists", current_count)

def can_use_meta_alerts(user_id: str) -> bool:
    """Check if user has access to meta alerts."""
    limits = get_user_limits(user_id)
    return limits.get("meta_alerts", False)

def can_use_wallet_alerts(user_id: str) -> bool:
    """Check if user has access to wallet buy alerts."""
    limits = get_user_limits(user_id)
    return limits.get("wallet_alerts", False)

def get_upgrade_message(user_id: str, feature: str) -> str:
    """Get upgrade message for a feature."""
    tier = get_user_tier(user_id)
    
    messages = {
        "max_coins": (
            "🔒 Coin Limit Reached\n\n"
            f"Free: 3 coins\n"
            f"Pro: 10 coins ($25/mo)\n"
            f"Premium: 25 coins ($50/mo)\n\n"
            f"Upgrade to track more coins!"
        ),
        "max_wallets": (
            "🔒 Wallet Limit Reached\n\n"
            f"Free: 1 wallet\n"
            f"Pro: 5 wallets ($25/mo)\n"
            f"Premium: 15 wallets ($50/mo)\n\n"
            f"Upgrade to track more wallets!"
        ),
        "max_lists": (
            "🔒 List Limit Reached\n\n"
            f"Free: 1 list\n"
            f"Pro: 5 lists ($25/mo)\n"
            f"Premium: 15 lists ($50/mo)\n\n"
            f"Upgrade to create more lists!"
        ),
        "meta_alerts": (
            "🔒 Premium Feature\n\n"
            f"Meta alerts are only available for Pro+ users.\n\n"
            f"Pro: $25/mo\n"
            f"Premium: $50/mo\n\n"
            f"Upgrade to get narrative rotation alerts!"
        ),
        "wallet_alerts": (
            "🔒 Premium Feature\n\n"
            f"Wallet buy alerts are only available for Pro+ users.\n\n"
            f"Pro: $25/mo\n"
            f"Premium: $50/mo\n\n"
            f"Upgrade to track wallet activity!"
        )
    }
    
    return messages.get(feature, "🔒 Upgrade required for this feature")

def format_tier_info(tier: str) -> str:
    """Format tier information message."""
    if tier not in TIERS:
        return "Invalid tier"
    
    info = TIERS[tier]
    limits = info["limits"]
    
    return (
        f"💎 {info['name']} Tier\n\n"
        f"Price: ${info['price']}/month\n\n"
        f"Features:\n"
        f"• Coins: {limits['max_coins']}\n"
        f"• Wallets: {limits['max_wallets']}\n"
        f"• Lists: {limits['max_lists']}\n"
        f"• Group coins: {limits['group_coins']}\n"
        f"• Meta alerts: {'✅' if limits['meta_alerts'] else '❌'}\n"
        f"• Wallet alerts: {'✅' if limits['wallet_alerts'] else '❌'}\n"
        f"• Advanced intel: {'✅' if limits['advanced_intelligence'] else '❌'}"
    )

def get_pricing_message() -> str:
    """Get full pricing comparison."""
    return (
        "💎 Trench Alert — Pricing\n\n"
        "🆓 Free\n"
        "• 3 coins\n"
        "• 1 wallet\n"
        "• 1 list\n"
        "• Basic alerts\n\n"
        
        "⚡ Pro — $25/month\n"
        "• 10 coins\n"
        "• 5 wallets\n"
        "• 5 lists\n"
        "• Meta alerts ✅\n"
        "• Wallet buy alerts ✅\n"
        "• Advanced intelligence ✅\n\n"
        
        "🔥 Premium — $50/month\n"
        "• 25 coins\n"
        "• 15 wallets\n"
        "• 15 lists\n"
        "• All Pro features ✅\n"
        "• Priority support ✅\n\n"
        
        "Contact @YourHandle to upgrade"
    )
