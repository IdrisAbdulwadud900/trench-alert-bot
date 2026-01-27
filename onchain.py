#!/usr/bin/env python3
"""
On-chain detection module for wallet transaction monitoring

V2: Uses raw Solana RPC (Layer 1-3) for true wallet-level buy detection.
Falls back to aggregated signals when wallet list is empty.
"""

import requests
import time
from typing import List, Dict, Optional

# V1 fallback: aggregated DexScreener signals
_tx_cache = {}
CACHE_TTL = 300  # 5 minutes

def get_recent_transactions(token_ca: str, limit: int = 20) -> List[Dict]:
    """
    Get recent transactions for a token from DexScreener (V1 fallback).
    
    Returns list of transactions with wallet addresses and amounts.
    """
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_ca}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        pairs = data.get("pairs", [])
        
        if not pairs:
            return []
        
        # Get the pair with highest liquidity
        main_pair = max(pairs, key=lambda p: p.get("liquidity", {}).get("usd", 0))
        
        txns = main_pair.get("txns", {})
        
        # Extract buy/sell counts from last intervals
        buys_5m = txns.get("m5", {}).get("buys", 0)
        sells_5m = txns.get("m5", {}).get("sells", 0)
        
        volume_usd = main_pair.get("volume", {}).get("m5", 0)
        
        return [{
            "type": "aggregated",
            "buys_5m": buys_5m,
            "sells_5m": sells_5m,
            "volume_5m": volume_usd,
            "timestamp": time.time()
        }]
        
    except Exception as e:
        print(f"Error fetching transactions for {token_ca}: {e}")
        return []

def detect_wallet_buys(
    token_ca: str,
    tracked_wallets: List[str],
    min_buy_usd: float = 300
) -> List[Dict]:
    """
    Detect if any tracked wallets bought the token.
    
    V2: Uses wallet_alert_engine (Layer 1-3) for true RPC-based detection.
    V1 fallback: aggregated volume signals when no wallets tracked.
    
    Returns list of detected buys with wallet info.
    """
    from wallet_alert_engine import detect_wallet_buys as engine_detect
    
    detected_buys = []
    
    # V2: Real wallet-level detection
    if tracked_wallets:
        for wallet in tracked_wallets:
            try:
                # Create coin dict structure expected by engine
                coin = {
                    "ca": token_ca,
                    "wallet_state": {}  # Engine will manage last_signature
                }
                
                # Use production engine
                buy = engine_detect(wallet, coin, min_buy_usd)
                
                if buy:
                    detected_buys.append({
                        "type": "wallet_buy",
                        "wallet": buy["wallet"],
                        "mint": buy["mint"],
                        "delta_tokens": buy["amount"],
                        "usd": buy["usd"],
                        "signature": buy["signature"],
                        "blockTime": buy.get("blockTime"),
                        "address": buy["wallet"],  # for compatibility
                        "tx_id": buy["signature"],
                        "price": buy.get("price", 0)
                    })
                    
                time.sleep(0.2)  # Rate limit between wallets
                
            except Exception as e:
                print(f"Error checking wallet {wallet[:8]}...: {e}")
                continue
    
    # V1 fallback: aggregated signals (when no wallets specified)
    else:
        txns = get_recent_transactions(token_ca, limit=50)
        
        for txn in txns:
            if txn["type"] == "aggregated":
                if txn["buys_5m"] > txn["sells_5m"] and txn["volume_5m"] >= min_buy_usd:
                    bucket_min = int(txn['timestamp'] / 60)
                    cache_key = f"{token_ca}_{bucket_min}"
                    
                    if cache_key not in _tx_cache:
                        _tx_cache[cache_key] = True
                        
                        detected_buys.append({
                            "type": "volume_spike",
                            "token_ca": token_ca,
                            "buys": txn["buys_5m"],
                            "sells": txn["sells_5m"],
                            "usd": txn["volume_5m"],
                            "timestamp": txn["timestamp"],
                            "tx_id": f"agg_{bucket_min}",
                            "side": "buy",
                            "address": "aggregated",
                            "note": "Aggregated buy signal"
                        })
        
        _tx_cache.clear()
    
    return detected_buys

def format_wallet_buy_alert(buy_info: Dict, coin_symbol: str = "Token") -> str:
    """Format a wallet buy alert message with pro-level UX."""

    buy_type = buy_info.get("type", "unknown")
    
    if buy_type == "wallet_buy":
        # V2: True wallet-level detection - production UX
        wallet = buy_info.get("wallet", "unknown")
        wallet_short = wallet[:6] + "..." if len(wallet) > 6 else wallet
        usd = buy_info.get("usd", 0)
        price = buy_info.get("price", 0)
        signature = buy_info.get("signature", "")
        
        # Build Solscan link
        tx_link = f"https://solscan.io/tx/{signature}" if signature else "N/A"
        
        return (
            f"🟢 WALLET BUY DETECTED\n\n"
            f"🪙 Token: {coin_symbol}\n"
            f"👛 Wallet: {wallet_short}\n"
            f"💰 Buy Size: ${int(usd):,}\n"
            f"📊 Price: ${price}\n"
            f"🔗 Tx: {tx_link}"
        )
    
    elif buy_type == "volume_spike":
        # V1 fallback: Aggregated activity
        wallet_disp = buy_info.get("address") or "aggregated"
        size_usd = int(buy_info.get("usd", 0))
        return (
            f"🟢 WALLET BUY DETECTED\n\n"
            f"Token: ${coin_symbol}\n"
            f"Wallet: {wallet_disp}\n"
            f"Buy Size: ${size_usd:,}\n"
            f"Tracked by: Wallet Alert\n\n"
            f"(Aggregated activity — add wallets for specific tracking)"
        )

    return (
        f"🟢 WALLET BUY DETECTED\n\n"
        f"Token: ${coin_symbol}\n"
        f"Tracked by: Wallet Alert"
    )

def clean_transaction_cache():
    """Clean up old transaction cache entries."""
    global _tx_cache
    _tx_cache.clear()

# Helius Integration Placeholder
# ================================
# For production, integrate Helius Enhanced WebSockets:
# 
# from helius import HeliusClient
# 
# client = HeliusClient(api_key=HELIUS_KEY)
# 
# async def monitor_wallet(wallet_address: str):
#     async for txn in client.stream_wallet_transactions(wallet_address):
#         if txn.type == "SWAP" and txn.token_in == "SOL":
#             # Wallet bought a token
#             yield {
#                 "wallet": wallet_address,
#                 "token": txn.token_out,
#                 "amount_usd": txn.amount_usd,
#                 "timestamp": txn.timestamp
#             }
