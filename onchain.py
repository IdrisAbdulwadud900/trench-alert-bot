#!/usr/bin/env python3
"""
On-chain detection module for wallet transaction monitoring

This module provides lightweight wallet buy detection using DexScreener's
transaction feed as a fallback (Helius integration can be added later).
"""

import requests
import time
from typing import List, Dict, Optional

# Cache for recent transactions to avoid duplicate alerts
_tx_cache = {}
CACHE_TTL = 300  # 5 minutes

def get_recent_transactions(token_ca: str, limit: int = 20) -> List[Dict]:
    """
    Get recent transactions for a token from DexScreener.
    
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
        
        # DexScreener doesn't expose transaction feed in public API
        # This is a placeholder for future Helius integration
        # For now, we'll track based on volume changes
        
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
    
    Note: This is a simplified version. For real on-chain detection,
    integrate with Helius or similar RPC provider.
    
    Returns list of detected buys with wallet info.
    """
    # For MVP, we use volume spikes as proxy signals
    # Real implementation would use Helius WebSocket for wallet monitoring
    
    txns = get_recent_transactions(token_ca, limit=50)
    detected_buys = []
    
    for txn in txns:
        if txn["type"] == "aggregated":
            # Check if there's significant buying activity
            if txn["buys_5m"] > txn["sells_5m"] and txn["volume_5m"] >= min_buy_usd:
                # Create aggregated signal (not wallet-specific without Helius)
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
                        "note": "Aggregated buy signal - integrate Helius for wallet-specific tracking"
                    })
    
    # Clean old cache entries
    current_time = time.time()
    _tx_cache.clear()  # Simple clear for now
    
    return detected_buys

def format_wallet_buy_alert(buy_info: Dict, coin_symbol: str = "Token") -> str:
    """Format a wallet buy alert message."""

    if buy_info.get("type") == "volume_spike":
        # UX-forward message, even for aggregated signals
        wallet_disp = buy_info.get("address") or "unknown"
        size_usd = int(buy_info.get("usd", 0))
        return (
            f"🟢 WALLET BUY DETECTED\n\n"
            f"Token: ${coin_symbol}\n"
            f"Wallet: {wallet_disp}\n"
            f"Buy Size: ${size_usd:,}\n"
            f"Tracked by: Wallet Alert\n\n"
            f"(Aggregated activity — add RPC for wallet-level)"
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
