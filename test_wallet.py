#!/usr/bin/env python3
"""
Simple test harness for Layer 1 wallet signature fetching.

Run:
    python test_wallet.py <WALLET_ADDRESS> [limit]
Or:
    WALLET_ADDR=<address> python test_wallet.py

Outputs signature + blockTime for recent transactions.
"""

import os
import sys
import datetime as dt
from wallet_scanner import get_recent_signatures


def main():
    wallet = None
    if len(sys.argv) > 1:
        wallet = sys.argv[1]
    else:
        wallet = os.getenv("WALLET_ADDR")

    if not wallet:
        print("Provide wallet via argv or WALLET_ADDR env.")
        print("Usage: python test_wallet.py <WALLET_ADDRESS> [limit]")
        sys.exit(1)

    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    sigs = get_recent_signatures(wallet, limit=limit)
    for s in sigs:
        sig = s.get("signature")
        bt = s.get("blockTime")
        bt_iso = dt.datetime.utcfromtimestamp(bt).isoformat() + "Z" if isinstance(bt, int) else str(bt)
        print(f"{sig}  blockTime={bt_iso}  slot={s.get('slot')}")


if __name__ == "__main__":
    main()
