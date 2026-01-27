#!/usr/bin/env python3
"""
Test harness for Layer 2 — transaction parsing.

Run:
    python test_parse.py <WALLET> <MINT> <SIGNATURE>

Prints the parsed inflow and USD size (if price is available).
"""

import sys
from wallet_parser import get_transaction, parse_token_inflow


def main():
    if len(sys.argv) < 4:
        print("Usage: python test_parse.py <WALLET> <MINT> <SIGNATURE>")
        sys.exit(1)

    wallet, mint, sig = sys.argv[1], sys.argv[2], sys.argv[3]
    tx = get_transaction(sig)
    info = parse_token_inflow(tx, wallet, mint)
    print(info or "No inflow detected.")


if __name__ == "__main__":
    main()
