#!/usr/bin/env python3
"""
Layer 2 — Transaction Parsing (Logic)

Decode token balance changes for a wallet in a given transaction.
We call `getTransaction` with `jsonParsed` and read `preTokenBalances`/
`postTokenBalances` to detect mint inflow and compute USD size.

This module is standalone and does not touch the bot loop.
"""

import os
import requests
from typing import Dict, Any, Optional, Tuple
from price import get_token_price_usd

RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")


def get_transaction(signature: str) -> Dict[str, Any]:
    """Fetch a transaction by signature using jsonParsed encoding."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {"encoding": "jsonParsed"}
        ]
    }
    resp = requests.post(RPC_URL, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"RPC error: {data['error']}")
    return data.get("result")


def _find_balance(balances: list, wallet: str, mint: str) -> Optional[Tuple[float, int]]:
    """Find (amount, decimals) for a wallet+mint in balances array."""
    for b in balances or []:
        try:
            owner = b.get("owner")
            bmint = b.get("mint")
            if owner == wallet and bmint == mint:
                ui = b.get("uiTokenAmount", {})
                amt = float(ui.get("amount", 0))
                dec = int(ui.get("decimals", 0))
                # amount is raw units; convert to tokens
                tokens = amt / (10 ** dec) if dec else amt
                return tokens, dec
        except Exception:
            continue
    return None


def parse_token_inflow(tx_result: Dict[str, Any], wallet: str, mint: str) -> Optional[Dict[str, Any]]:
    """Return inflow info if wallet's balance of `mint` increased in the tx."""
    if not tx_result:
        return None
    meta = tx_result.get("meta") or {}
    pre = meta.get("preTokenBalances") or []
    post = meta.get("postTokenBalances") or []

    pre_amt = _find_balance(pre, wallet, mint)
    post_amt = _find_balance(post, wallet, mint)

    pre_tokens = pre_amt[0] if pre_amt else 0.0
    post_tokens = post_amt[0] if post_amt else 0.0
    delta_tokens = post_tokens - pre_tokens

    if delta_tokens <= 0:
        return None

    # price lookup
    price_data = get_token_price_usd(mint)
    usd_price = price_data.get("price") if price_data else None
    usd_size = (delta_tokens * usd_price) if (usd_price and usd_price > 0) else None

    info = {
        "wallet": wallet,
        "mint": mint,
        "delta_tokens": delta_tokens,
        "usd": usd_size,
        "signature": tx_result.get("transaction", {}).get("signatures", [None])[0],
        "slot": meta.get("slot"),
        "blockTime": tx_result.get("blockTime")
    }
    return info


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python wallet_parser.py <WALLET> <MINT> <SIGNATURE>")
        sys.exit(1)
    wallet, mint, sig = sys.argv[1], sys.argv[2], sys.argv[3]
    try:
        tx = get_transaction(sig)
        info = parse_token_inflow(tx, wallet, mint)
        print(info or "No inflow detected.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(2)
