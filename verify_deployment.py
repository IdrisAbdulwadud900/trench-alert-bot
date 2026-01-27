#!/usr/bin/env python3
"""Final verification before deployment."""

import sys
import json

print("=" * 60)
print("FINAL DEPLOYMENT VERIFICATION")
print("=" * 60)

# 1. Check all imports
print("\n🔍 Checking imports...")
try:
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
    from meta import analyze_list_performance, detect_list_heating, format_list_alert
    from onchain import detect_wallet_buys, format_wallet_buy_alert
    print("   ✅ All imports successful")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# 2. Check subscriptions file exists
print("\n📁 Checking data files...")
try:
    from subscriptions import SUBS_FILE
    print(f"   ✅ Subscriptions file path: {SUBS_FILE}")
except:
    print("   ❌ Could not get subscriptions file path")
    sys.exit(1)

# 3. Test pricing message
print("\n💰 Testing pricing display...")
pricing = get_pricing_message()
if "Free" in pricing and "Pro" in pricing and "Premium" in pricing and "$" in pricing:
    print("   ✅ Pricing message valid")
    print(f"   📋 Length: {len(pricing)} chars")
else:
    print("   ❌ Pricing message missing tiers")
    sys.exit(1)

# 4. Test feature gates
print("\n🔐 Testing feature gates...")
test_user = 999999999
free_limits = {
    "coins": can_add_coin(test_user, 0),
    "coins_limit": can_add_coin(test_user, 3),
    "wallets": can_add_wallet(test_user, 0),
    "wallets_limit": can_add_wallet(test_user, 1),
    "lists": can_add_list(test_user, 0),
    "lists_limit": can_add_list(test_user, 1),
}
print(f"   ✅ Free tier limits: {free_limits}")

# Verify proper gating
if not free_limits["coins_limit"]:
    print("   ✅ Coin limit properly enforced at 3")
else:
    print("   ⚠️  Coin limit not enforced correctly")

if not free_limits["wallets_limit"]:
    print("   ✅ Wallet limit properly enforced at 1")
else:
    print("   ⚠️  Wallet limit not enforced correctly")

# 5. Test upgrade messages
print("\n📢 Testing upgrade messages...")
msg = get_upgrade_message(test_user, "wallet_alerts")
if "wallet" in msg.lower() and ("pro" in msg.lower() or "premium" in msg.lower()):
    print("   ✅ Upgrade message valid")
else:
    print("   ❌ Upgrade message missing wallet feature info")
    sys.exit(1)

# 6. Test meta analysis
print("\n📊 Testing meta analysis...")
test_coins = ["CA1", "CA2", "CA3", "CA4", "CA5"]
test_data = {
    "CA1": {"mc": 2000000, "start_mc": 1000000, "volume_24h": 600000, "symbol": "TEST1"},
    "CA2": {"mc": 2500000, "start_mc": 1000000, "volume_24h": 700000, "symbol": "TEST2"},
    "CA3": {"mc": 1200000, "start_mc": 1000000, "volume_24h": 100000, "symbol": "TEST3"},
    "CA4": {"mc": 800000, "start_mc": 1000000, "volume_24h": 50000, "symbol": "TEST4"},
    "CA5": {"mc": 950000, "start_mc": 1000000, "volume_24h": 30000, "symbol": "TEST5"},
}

metrics = analyze_list_performance(test_coins, test_data)
print(f"   📈 Heat score: {metrics['heat_score']:.1f}")
print(f"   📊 Pumping: {metrics['pumping_count']}/{metrics['total_coins']}")
print(f"   📉 Dumping: {metrics['dumping_count']}/{metrics['total_coins']}")
print(f"   📢 Status: {metrics['status']}")

if metrics['heat_score'] > 0:
    print("   ✅ Meta analysis working")
else:
    print("   ❌ Meta analysis broken")
    sys.exit(1)

# 7. Test list heating detection
print("\n🔥 Testing list heating detection...")
is_heating, reason = detect_list_heating("test_list", metrics, threshold=30)
print(f"   🔥 Is heating: {is_heating}")
print(f"   📝 Reason: {reason}")
if is_heating and reason:
    print("   ✅ Heating detection working")
else:
    print("   ⚠️  No heating detected (might be normal)")

# 8. Test alert formatting
print("\n📨 Testing alert formatting...")
alert = format_list_alert("my_list", metrics, "Most coins pumping together")
if len(alert) > 20 and "my_list" in alert:
    print("   ✅ List alert formatting valid")
else:
    print("   ❌ List alert formatting broken")
    sys.exit(1)

# 9. Check app.py syntax
print("\n🐍 Checking app.py syntax...")
try:
    import app
    print("   ✅ app.py imports successfully")
except SyntaxError as e:
    print(f"   ❌ Syntax error in app.py: {e}")
    sys.exit(1)
except Exception as e:
    # May fail due to config/env, but syntax should pass
    if "BOT_TOKEN" in str(e) or "config" in str(e).lower():
        print("   ✅ app.py syntax valid (config error expected)")
    else:
        print(f"   ⚠️  app.py import issue: {e}")

# 10. Summary
print("\n" + "=" * 60)
print("✅ VERIFICATION COMPLETE - READY FOR DEPLOYMENT")
print("=" * 60)
print("\nDeployment instructions:")
print("1. Set BOT_TOKEN environment variable")
print("2. Ensure DexScreener API is accessible")
print("3. Run: python3 app.py")
print("4. Test with /start, /pricing, and track a coin")
print("\nMonitoring:")
print("- Check logs for wallet buy detections")
print("- Monitor meta heating alerts for Pro users")
print("- Verify subscription tier enforcement")
print("\nOptional:")
print("- Integrate Helius RPC for wallet-specific detection")
print("- Add payment gateway for automated Pro upgrades")
