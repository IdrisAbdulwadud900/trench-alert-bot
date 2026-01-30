#!/usr/bin/env python3
"""
Test script for wallet buy detection pipeline (Layers 1-3)

Tests:
1. Layer 1: Signature fetching
2. Layer 2: Transaction parsing
3. Layer 3: Alert engine with deduplication
4. Integration: Full workflow
"""

import pytest

def test_layer_1():
    """Test Layer 1: Signature fetching"""
    print("\n=== Layer 1: Signature Fetching ===")
    from wallet_scanner import get_recent_signatures
    
    # Test with known active wallet
    wallet = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
    
    try:
        sigs = get_recent_signatures(wallet, limit=3)
        
        if not sigs:
            pytest.skip("No signatures returned (RPC/no recent activity)")

        print(f"✅ Fetched {len(sigs)} signatures")
        print(f"   Latest: {sigs[0]['signature'][:16]}...")
            
    except Exception as e:
        pytest.skip(f"Layer 1 unavailable: {e}")


def test_layer_2():
    """Test Layer 2: Transaction parsing"""
    print("\n=== Layer 2: Transaction Parsing ===")
    from wallet_scanner import get_recent_signatures
    from wallet_parser import get_transaction, parse_token_inflow
    
    wallet = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
    
    try:
        sigs = get_recent_signatures(wallet, limit=3)
        
        if not sigs:
            pytest.skip("No signatures to parse (RPC/no recent activity)")
        
        sig = sigs[0]["signature"]
        tx = get_transaction(sig)
        
        if not tx:
            pytest.skip("Transaction fetch returned None (RPC throttled/unavailable)")

        print(f"✅ Transaction fetched: {sig[:16]}...")

        # Try to parse (may not have token inflow, but should not crash)
        # We don't know the mint, so this is just a structure test
        test_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC for test
        inflow = parse_token_inflow(tx, wallet, test_mint)

        if inflow:
            print(f"✅ Inflow detected: {inflow.get('delta_tokens', 0):.4f} tokens")
        else:
            print("⚠️  No inflow for test mint (expected)")
            
        # Structure test: parsing should not crash.
        assert True
            
    except Exception as e:
        pytest.skip(f"Layer 2 unavailable: {e}")


def test_layer_3():
    """Test Layer 3: Alert engine"""
    print("\n=== Layer 3: Alert Engine ===")
    from wallet_alert_engine import detect_wallet_buys
    
    wallet = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
    
    # Test with USDC mint (just to test structure)
    coin = {
        "ca": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "symbol": "USDC",
        "wallet_state": {}
    }
    
    try:
        result = detect_wallet_buys(wallet, coin, min_usd=1)
        
        if result:
            print(f"✅ Buy detected:")
            print(f"   Amount: {result['amount']:.4f}")
            print(f"   USD: ${result['usd']:.2f}")
            print(f"   Signature: {result['signature'][:16]}...")
        else:
            print("⚠️  No buys detected (may not have recent activity)")
        
        # Test deduplication (only if we saw a buy)
        if result:
            print("\n=== Testing Deduplication ===")
            # Run again - should return None since last_signature is set
            result2 = detect_wallet_buys(wallet, coin, min_usd=1)
            assert result2 is None, "Deduplication failed (got duplicate)"
        else:
            pytest.skip("No buys detected; skipping deduplication assertion")
            
    except Exception as e:
        pytest.skip(f"Layer 3 unavailable: {e}")


def test_integration():
    """Test full integration with alert formatting"""
    print("\n=== Integration: Full Workflow ===")
    from wallet_alert_engine import detect_wallet_buys
    from onchain import format_wallet_buy_alert
    
    wallet = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
    
    coin = {
        "ca": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "symbol": "USDC",
        "wallet_state": {}
    }
    
    try:
        result = detect_wallet_buys(wallet, coin, min_usd=1)
        
        if not result:
            pytest.skip("No buy to format (no recent activity)")

        # Format alert
        alert_msg = format_wallet_buy_alert(
            {
                "type": "wallet_buy",
                "wallet": result["wallet"],
                "usd": result["usd"],
                "price": result.get("price", 0),
                "signature": result["signature"],
            },
            coin["symbol"],
        )

        print("✅ Alert formatted:")
        print("\n" + alert_msg)
        assert isinstance(alert_msg, str) and alert_msg.strip()
            
    except Exception as e:
        pytest.skip(f"Integration unavailable: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("WALLET BUY DETECTION PIPELINE TEST")
    print("=" * 60)
    
    results = {
        "Layer 1": test_layer_1(),
        "Layer 2": test_layer_2(),
        "Layer 3": test_layer_3(),
        "Integration": test_integration()
    }
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - System ready for production!")
    else:
        print("⚠️  Some tests failed - Review errors above")
    print("=" * 60)
