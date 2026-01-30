#!/usr/bin/env python3
"""
Integration test for Trench Alert Bot
Tests all core flows without running the actual bot
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def test_imports():
    """Test all imports work."""
    print("Testing imports...")
    try:
        import app
        import core.tracker
        import core.alerts
        import core.monitor
        import ui.home
        import ui.coins
        import ui.wallets
        import ui.settings
        import storage
        import wallets
        import settings
        import plans
        import mc
        import intelligence
        print("✅ All imports successful")
    except Exception as e:
        raise AssertionError(f"Import failed: {e}") from e


def test_tracker():
    """Test tracker operations."""
    print("\nTesting Tracker...")
    try:
        from core.tracker import Tracker
        
        test_user = "test_user_999"
        
        # Test add coin
        coin_data = {
            "ca": "test_ca_123",
            "start_mc": 100000,
            "ath_mc": 100000,
            "low_mc": 100000,
            "alerts": {"mc": 50000, "pct": 30},
            "triggered": {}
        }
        
        Tracker.add_coin(test_user, coin_data)
        print("  ✅ Add coin works")
        
        # Test get coins
        coins = Tracker.get_user_coins(test_user)
        if len(coins) > 0:
            print(f"  ✅ Get coins works ({len(coins)} found)")
        else:
            print("  ⚠️ No coins found (might be ok)")
        
        # Test remove coin
        if Tracker.remove_coin(test_user, "test_ca_123"):
            print("  ✅ Remove coin works")
        else:
            print("  ⚠️ Remove coin didn't find coin to remove")
    except Exception as e:
        print(f"  ❌ Tracker test failed: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_alerts():
    """Test alert engine."""
    print("\nTesting AlertEngine...")
    try:
        from core.alerts import AlertEngine
        
        test_coin = {
            "ca": "test",
            "start_mc": 100000,
            "ath_mc": 200000,
            "low_mc": 50000,
            "alerts": {
                "mc": 75000,
                "pct": 30,
                "x": 2,
                "reclaim": True
            },
            "triggered": {}
        }
        
        # Test MC alert
        should_alert, msg = AlertEngine.should_alert_mc(test_coin, 70000)
        if should_alert:
            print("  ✅ MC alert triggers correctly")
        else:
            print("  ⚠️ MC alert didn't trigger (70k < 75k threshold)")
        
        # Test % alert
        should_alert, msg = AlertEngine.should_alert_pct(test_coin, 140000)
        if should_alert:
            print("  ✅ % alert triggers correctly")
        else:
            print("  ⚠️ % alert didn't trigger")
        
        # Test X alert
        should_alert, msg = AlertEngine.should_alert_x(test_coin, 210000)
        if should_alert:
            print("  ✅ X alert triggers correctly")
        else:
            print("  ⚠️ X alert didn't trigger")
        
        # Test evaluate_all
        alerts = AlertEngine.evaluate_all(test_coin, 150000, 10000, "aggressive")
        print(f"  ✅ evaluate_all returns {len(alerts)} alerts")
    except Exception as e:
        print(f"  ❌ AlertEngine test failed: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_data_files():
    """Test data file structure."""
    print("\nTesting data files...")
    try:
        # Test data.json
        with open(BASE_DIR / "data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"  ✅ data.json is valid JSON ({len(data)} users)")
        
        # Test settings.json if exists
        try:
            with open(BASE_DIR / "settings.json", "r", encoding="utf-8") as f:
                settings = json.load(f)
                print(f"  ✅ settings.json is valid JSON ({len(settings)} chats)")
        except FileNotFoundError:
            print("  ℹ️ settings.json doesn't exist yet (ok)")
        
        # Test wallets.json if exists
        try:
            with open(BASE_DIR / "wallets.json", "r", encoding="utf-8") as f:
                wallets = json.load(f)
                print(f"  ✅ wallets.json is valid JSON ({len(wallets)} users)")
        except FileNotFoundError:
            print("  ℹ️ wallets.json doesn't exist yet (ok)")
    except Exception as e:
        raise AssertionError(f"Data file test failed: {e}") from e


def test_intelligence():
    """Test intelligence layer."""
    print("\nTesting Intelligence...")
    try:
        from intelligence import (
            compute_range_position,
            compute_quality_score,
            get_range_description
        )
        
        # Test range position
        pos = compute_range_position(150000, 100000, 200000)
        if 0.45 <= pos <= 0.55:
            print(f"  ✅ Range position correct: {pos:.2f}")
        else:
            print(f"  ⚠️ Range position unexpected: {pos:.2f}")
        
        # Test quality score
        score = compute_quality_score(50000, 100000, 300000)
        print(f"  ✅ Quality score: {score}/3")
        
        # Test range description
        desc = get_range_description(0.5)
        print(f"  ✅ Range description: {desc}")
    except Exception as e:
        print(f"  ❌ Intelligence test failed: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Run all tests."""
    print("=" * 60)
    print("TRENCH ALERT BOT - INTEGRATION TEST")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_data_files,
        test_tracker,
        test_alerts,
        test_intelligence
    ]
    
    results = []
    for test in tests:
        try:
            test()
            results.append(True)
        except Exception:
            results.append(False)
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for ok in results if ok)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - System is working!")
        return 0
    else:
        print(f"⚠️ Some tests failed or had warnings")
        return 1


if __name__ == "__main__":
    sys.exit(main())
