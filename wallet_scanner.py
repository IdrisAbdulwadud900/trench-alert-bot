#!/usr/bin/env python3
"""
Layer 1 — Wallet Transaction Fetching

Fetch recent transaction signatures for a wallet using Solana JSON-RPC
(getSignaturesForAddress). This is infrastructure-only: no parsing.

Usage (module):
    from wallet_scanner import get_recent_signatures
    sigs = get_recent_signatures(wallet_address, limit=5)

Env:
    SOLANA_RPC_URL — optional override for RPC endpoint
"""

import os
import requests
import time
from typing import List, Dict, Any

RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

# Rate limiting
LAST_REQUEST_TIME = 0
MIN_REQUEST_INTERVAL = 0.5  # 500ms between requests

def get_recent_signatures(wallet: str, limit: int = 5, max_retries: int = 3) -> List[Dict[str, Any]]:
    """Return a list of recent signatures for the given wallet.
    Each item contains keys like 'signature', 'slot', 'blockTime'.
    Includes retry logic for rate limiting.
    """
    global LAST_REQUEST_TIME
    
    if not wallet or not isinstance(wallet, str):
        raise ValueError("wallet address is required")
    if limit <= 0:
        limit = 5

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            wallet,
            {"limit": limit}
        ]
    }
    
    for attempt in range(max_retries):
        try:
            # Rate limiting - ensure minimum interval between requests
            now = time.time()
            time_since_last = now - LAST_REQUEST_TIME
            if time_since_last < MIN_REQUEST_INTERVAL:
                time.sleep(MIN_REQUEST_INTERVAL - time_since_last)
            
            LAST_REQUEST_TIME = time.time()
            
            resp = requests.post(RPC_URL, json=payload, timeout=10)
            
            # Handle rate limiting with exponential backoff
            if resp.status_code == 429:
                if attempt < max_retries - 1:
                    backoff = (2 ** attempt) * 2  # 2s, 4s, 8s
                    print(f"⚠️ Rate limited, retrying in {backoff}s...")
                    time.sleep(backoff)
                    continue
                else:
                    print(f"❌ Rate limit exceeded after {max_retries} retries")
                    return []  # Return empty instead of crashing
            
            resp.raise_for_status()
            data = resp.json()

            if "error" in data:
                err = data["error"]
                print(f"RPC error for wallet {wallet[:8]}...: {err}")
                return []  # Return empty on RPC errors

            result = data.get("result", [])
            if not isinstance(result, list):
                return []
            return result
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                backoff = (2 ** attempt) * 1  # 1s, 2s, 4s
                print(f"⚠️ Request failed, retrying in {backoff}s...")
                time.sleep(backoff)
                continue
            else:
                print(f"❌ Request failed after {max_retries} retries: {e}")
                return []  # Return empty instead of crashing
    
    return []

if __name__ == "__main__":
    import sys
    import datetime as dt

    if len(sys.argv) < 2:
        print("Usage: python wallet_scanner.py <WALLET_ADDRESS> [limit]")
        sys.exit(1)

    wallet = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    try:
        sigs = get_recent_signatures(wallet, limit=limit)
        for s in sigs:
            sig = s.get("signature")
            bt = s.get("blockTime")
            bt_iso = dt.datetime.utcfromtimestamp(bt).isoformat() + "Z" if isinstance(bt, int) else str(bt)
            print(f"{sig}  blockTime={bt_iso}  slot={s.get('slot')}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(2)
