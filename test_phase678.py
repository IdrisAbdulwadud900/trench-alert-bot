#!/usr/bin/env python3
"""Test Phase 6, 7, 8 integration."""

import sys
from subscriptions import (
    get_user_tier,
    can_add_coin,
    can_add_wallet,
    can_add_list,
    can_use_wallet_alerts,
    can_use_meta_alerts,
    get_upgrade_message,
    get_pricing_message
)
from meta import analyze_list_performance, detect_list_heating
from onchain import detect_wallet_buys
from wallets import get_wallets
from lists import get_lists
from storage import get_user_coins

print("=" * 50)
print("PHASE 6-8 INTEGRATION TEST")
print("=" * 50)

# Test 1: Subscription tiers
print("\n✅ Test 1: Subscription Functions")
test_user = 123456789
tier = get_user_tier(test_user)
print(f"  User tier: {tier}")
print(f"  Can add coin: {can_add_coin(test_user, 0)}")
print(f"  Can use wallet alerts: {can_use_wallet_alerts(test_user)}")
print(f"  Can use meta alerts: {can_use_meta_alerts(test_user)}")

# Test 2: Upgrade messaging
print("\n✅ Test 2: Upgrade Messages")
msg = get_upgrade_message(test_user, "wallet_alerts")
print(f"  Message length: {len(msg)} chars")
print(f"  Contains 'Pro': {'Pro' in msg}")

# Test 3: Pricing display
print("\n✅ Test 3: Pricing Display")
pricing = get_pricing_message()
print(f"  Pricing length: {len(pricing)} chars")
print(f"  Contains tiers: {'Free' in pricing and 'Pro' in pricing and 'Premium' in pricing}")

# Test 4: Meta analysis
print("\n✅ Test 4: Meta Analysis")
test_coins = ["addr1", "addr2", "addr3"]
test_data = {
    "addr1": {"mc": 1500000, "start_mc": 1000000, "volume_24h": 50000, "symbol": "TEST1"},
    "addr2": {"mc": 2000000, "start_mc": 1000000, "volume_24h": 100000, "symbol": "TEST2"},
    "addr3": {"mc": 800000, "start_mc": 1000000, "volume_24h": 20000, "symbol": "TEST3"},
}
metrics = analyze_list_performance(test_coins, test_data)
print(f"  Heat score: {metrics['heat_score']:.1f}")
print(f"  Pumping coins: {metrics['pumping_count']}")
print(f"  Total coins: {metrics['total_coins']}")

is_heating, reason = detect_list_heating("test_list", metrics, threshold=30)
print(f"  Is heating: {is_heating}")
print(f"  Reason: {reason if reason else 'N/A'}")

# Test 5: On-chain detection (mock)
print("\n✅ Test 5: On-chain Detection")
# Note: This will make API calls - just check the function exists
try:
    # Test with empty wallets to avoid API spam
    buys = detect_wallet_buys("test_ca", [], min_buy_usd=100)
    print(f"  Function callable: True")
    print(f"  Returns list: {isinstance(buys, list)}")
except Exception as e:
    print(f"  Error: {e}")

# Test 6: Feature gating logic
print("\n✅ Test 6: Feature Gate Logic")
# Test free tier limits
for i in range(5):
    can_add = can_add_coin(test_user, i)
    print(f"  Coin count {i}: Can add = {can_add}")

print("\n" + "=" * 50)
print("ALL TESTS COMPLETED")
print("=" * 50)
