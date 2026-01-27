#!/usr/bin/env python3
"""
Layer 3 — Alert Engine (Business Rules)

Combines Layer 1 (signature fetching) and Layer 2 (transaction parsing)
to detect wallet buys with:
- Minimum buy size filter
- Per-coin + per-wallet filters
- Deduplication (last_signature tracking)

This module does NOT send alerts. It returns buy events for the bot to act on.
"""

import time
from typing import List, Dict, Optional
from wallet_scanner import get_recent_signatures
from wallet_parser import get_transaction, parse_token_inflow


def detect_new_buys(
    wallet: str,
    mint: str,
    min_buy_usd: float = 300,
    last_signature: Optional[str] = None,
    limit: int = 10
) -> List[Dict]:
    """
    Detect new token buys for a wallet.
    
    Args:
        wallet: Wallet address to monitor
        mint: Token mint address to watch
        min_buy_usd: Minimum buy size in USD
        last_signature: Last processed signature (for dedup)
        limit: Max signatures to fetch
    
    Returns:
        List of buy events with keys: wallet, mint, delta_tokens, usd, signature, blockTime
    """
    try:
        # Layer 1: Fetch recent signatures
        sigs = get_recent_signatures(wallet, limit=limit)
        
        # Filter out already-processed signatures
        new_sigs = []
        for sig in sigs:
            sig_str = sig.get("signature")
            if not sig_str:
                continue
            # Stop when we hit the last seen signature
            if last_signature and sig_str == last_signature:
                break
            new_sigs.append(sig_str)
        
        if not new_sigs:
            return []
        
        buys = []
        for sig in new_sigs:
            try:
                # Layer 2: Parse transaction for token inflow
                tx = get_transaction(sig)
                if not tx:
                    continue
                
                inflow = parse_token_inflow(tx, wallet, mint)
                if not inflow:
                    continue
                
                # Check minimum buy size
                usd = inflow.get("usd")
                if usd is None or usd < min_buy_usd:
                    continue
                
                buys.append(inflow)
                
                # Rate limit to avoid RPC throttle
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error parsing tx {sig[:16]}...: {e}")
                continue
        
        return buys
        
    except Exception as e:
        print(f"Error detecting buys for wallet {wallet[:8]}...: {e}")
        return []


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python wallet_alert_engine.py <WALLET> <MINT> [min_usd] [last_sig]")
        sys.exit(1)
    
    wallet = sys.argv[1]
    mint = sys.argv[2]
    min_usd = float(sys.argv[3]) if len(sys.argv) > 3 else 300.0
    last_sig = sys.argv[4] if len(sys.argv) > 4 else None
    
    buys = detect_new_buys(wallet, mint, min_buy_usd=min_usd, last_signature=last_sig)
    
    if buys:
        print(f"Found {len(buys)} new buy(s):")
        for b in buys:
            print(f"  {b['delta_tokens']:.4f} tokens @ ${b['usd']:.2f} USD — sig: {b['signature'][:16]}...")
    else:
        print("No new buys detected.")
