#!/usr/bin/env python3
"""
Layer 3 — Wallet Buy Alert Engine (Production Logic)

Production-grade wallet buy detection with:
- Tracked wallet + tracked coin (mint) matching
- Token inflow detection via RPC
- USD size calculation
- Deduplication via last_signature tracking
- Zero spam, zero duplicates, zero guessing

Returns alert dict ONLY when ALL conditions met:
1. Tracked wallet
2. Tracked coin (mint)
3. Token inflow detected
4. Buy size >= min USD
5. Transaction not alerted before
"""

import time
from typing import Dict, Optional
from wallet_scanner import get_recent_signatures
from wallet_parser import get_transaction, parse_token_inflow
from price import get_token_price_usd


def detect_wallet_buys(wallet: str, coin: Dict, min_usd: float = 300) -> Optional[Dict]:
    """
    Detect if tracked wallet bought tracked coin.
    
    Args:
        wallet: Wallet address to monitor
        coin: Coin dict with 'ca' (mint), 'wallet_state', etc.
        min_usd: Minimum buy size in USD
    
    Returns:
        Alert dict with signature, amount, usd, price OR None
    """
    try:
        # Get last seen signature for deduplication
        wallet_state = coin.setdefault("wallet_state", {})
        last_sig = wallet_state.get("last_signature")
        
        mint = coin.get("ca")
        if not mint:
            return None
        
        # Layer 1: Fetch recent signatures
        sigs = get_recent_signatures(wallet, limit=5)
        
        for s in sigs:
            sig = s.get("signature")
            if not sig:
                continue
            
            # Stop when we hit the last seen signature (already processed)
            if sig == last_sig:
                break
            
            # Layer 2: Parse transaction for token inflow
            tx = get_transaction(sig)
            if not tx:
                continue
            
            inflow = parse_token_inflow(tx, wallet, mint)
            if not inflow:
                continue
            
            # Calculate USD value
            amount = inflow.get("delta_tokens", 0)
            usd_value = inflow.get("usd")
            
            # If USD not available from parser, try to calculate
            if usd_value is None and amount > 0:
                price = get_token_price_usd(mint)
                if price and price > 0:
                    usd_value = amount * price
            
            # Check minimum buy size
            if usd_value is None or usd_value < min_usd:
                continue
            
            # SUCCESS - Update last seen signature
            wallet_state["last_signature"] = sig
            
            return {
                "signature": sig,
                "amount": amount,
                "usd": usd_value,
                "price": usd_value / amount if amount > 0 else 0,
                "wallet": wallet,
                "mint": mint,
                "blockTime": inflow.get("blockTime")
            }
        
        return None
        
    except Exception as e:
        print(f"Error detecting buy for wallet {wallet[:8]}...: {e}")
        return None


# Legacy compatibility wrapper
def detect_new_buys(
    wallet: str,
    mint: str,
    min_buy_usd: float = 300,
    last_signature: Optional[str] = None,
    limit: int = 10
) -> list:
    """Legacy function for backward compatibility."""
    coin = {
        "ca": mint,
        "wallet_state": {"last_signature": last_signature}
    }
    result = detect_wallet_buys(wallet, coin, min_buy_usd)
    return [result] if result else []


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python wallet_alert_engine.py <WALLET> <MINT> [min_usd]")
        sys.exit(1)
    
    wallet = sys.argv[1]
    mint = sys.argv[2]
    min_usd = float(sys.argv[3]) if len(sys.argv) > 3 else 300.0
    
    # Test with mock coin structure
    coin = {
        "ca": mint,
        "symbol": "TEST",
        "wallet_state": {}
    }
    
    result = detect_wallet_buys(wallet, coin, min_usd)
    
    if result:
        print(f"✅ Buy detected:")
        print(f"  Amount: {result['amount']:.4f} tokens")
        print(f"  USD: ${result['usd']:.2f}")
        print(f"  Signature: {result['signature'][:16]}...")
    else:
        print("No buys detected above minimum.")

