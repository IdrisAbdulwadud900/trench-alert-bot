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
from typing import List, Dict, Any

RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

def get_recent_signatures(wallet: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Return a list of recent signatures for the given wallet.
    Each item contains keys like 'signature', 'slot', 'blockTime'.
    Raises on HTTP or RPC error.
    """
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

    resp = requests.post(RPC_URL, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        # Raise a readable error for upstream handling
        err = data["error"]
        raise RuntimeError(f"RPC error: {err}")

    result = data.get("result", [])
    if not isinstance(result, list):
        return []
    return result

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
