# Layer 3 — Wallet Buy Alert Engine (PRODUCTION)

## Overview

Production-grade on-chain wallet buy detection using 3-layer architecture:
- **Layer 1**: Transaction signature fetching (wallet_scanner.py)
- **Layer 2**: Transaction parsing (wallet_parser.py)
- **Layer 3**: Alert engine with deduplication (wallet_alert_engine.py)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    TELEGRAM BOT                          │
│                     (app.py)                             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              MONITOR LOOP (60s interval)                 │
│  • Loads tracked coins from data.json                    │
│  • For each coin with wallet alerts enabled:             │
│    - For each tracked wallet address:                    │
│      detect_wallet_buys(wallet, coin, min_usd)           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│          LAYER 3: ALERT ENGINE                           │
│         (wallet_alert_engine.py)                         │
│                                                           │
│  detect_wallet_buys(wallet, coin, min_usd)               │
│    ├─ Get last_signature from coin["wallet_state"]       │
│    ├─ Call Layer 1 to fetch recent signatures            │
│    ├─ For each new signature:                            │
│    │   ├─ Call Layer 2 to parse transaction              │
│    │   ├─ Check if token inflow for this mint            │
│    │   ├─ Calculate USD value                            │
│    │   └─ Check if >= min_usd                            │
│    └─ Return alert dict OR None                          │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
┌────────────────┐          ┌────────────────┐
│   LAYER 1      │          │   LAYER 2      │
│  Signatures    │          │  TX Parsing    │
│                │          │                │
│ getSignatures  │          │ getTransaction │
│ ForAddress     │          │ (jsonParsed)   │
│                │          │                │
│ Returns:       │          │ Returns:       │
│ [signatures]   │          │ token deltas   │
└────────────────┘          └────────────────┘
```

## Files

### wallet_scanner.py (Layer 1)
**Purpose**: Fetch recent transaction signatures for a wallet

**Key Function**:
```python
get_recent_signatures(wallet: str, limit: int = 5) -> List[Dict]
```

**Returns**:
```python
[
    {
        "signature": "5KAStV9CGVuv8rMF...",
        "blockTime": 1704123456,
        "slot": 123456789
    },
    ...
]
```

**RPC Call**: `getSignaturesForAddress`

### wallet_parser.py (Layer 2)
**Purpose**: Parse transactions to detect token balance changes

**Key Functions**:
```python
get_transaction(signature: str) -> Dict
parse_token_inflow(tx_result: Dict, wallet: str, mint: str) -> Optional[Dict]
```

**Returns**:
```python
{
    "wallet": "7xKXtg...",
    "mint": "EPjFWdd...",
    "delta_tokens": 1250.5,
    "usd": 1250.50,
    "signature": "5KAStV9...",
    "slot": 123456789,
    "blockTime": 1704123456
}
```

**RPC Call**: `getTransaction` with `jsonParsed` encoding and `maxSupportedTransactionVersion: 0`

**Logic**:
1. Reads `preTokenBalances` and `postTokenBalances`
2. Finds wallet's balance for the mint in both
3. Calculates delta (post - pre)
4. Converts to USD using price.py

### wallet_alert_engine.py (Layer 3)
**Purpose**: Production alert engine with deduplication

**Key Function**:
```python
detect_wallet_buys(wallet: str, coin: Dict, min_usd: float = 300) -> Optional[Dict]
```

**Returns**:
```python
{
    "signature": "5KAStV9...",
    "amount": 1250.5,
    "usd": 1250.50,
    "price": 1.00,
    "wallet": "7xKXtg...",
    "mint": "EPjFWdd...",
    "blockTime": 1704123456
}
# OR None if no buy detected
```

**Deduplication**:
- Manages `coin["wallet_state"]["last_signature"]`
- Only processes signatures newer than last_signature
- Updates last_signature when buy detected

**Conditions** (ALL must be true):
1. Tracked wallet (provided as parameter)
2. Tracked coin/mint (coin["ca"])
3. Token inflow detected (delta > 0)
4. Buy size >= min_usd
5. Transaction not alerted before (sig != last_signature)

## Integration

### app.py Monitor Loop

```python
# For each coin with wallet alerts enabled
wallet_alert = coin.get("alerts", {}).get("wallets", {})
if wallet_alert.get("enabled"):
    watched_addresses = wallet_alert.get("addresses", [])
    min_buy = wallet_alert.get("min_buy_usd", 300)
    
    # Check each watched wallet
    for wallet in watched_addresses:
        from wallet_alert_engine import detect_wallet_buys as engine_detect
        
        # Use production engine
        buy = engine_detect(wallet, coin, min_buy)
        
        if buy:
            # Send alert
            symbol = coin.get("symbol", "Token")
            alert_msg = format_wallet_buy_alert(buy, symbol)
            await bot.send_message(user_id, alert_msg)
```

### Alert Formatting (onchain.py)

```python
def format_wallet_buy_alert(buy_info: Dict, coin_symbol: str) -> str:
    """
    Format a clean, professional wallet buy alert message.
    
    Readable. Screenshot-worthy. Trust-building.
    """
    wallet = buy_info.get("wallet", "unknown")
    usd = buy_info.get("usd", 0)
    price = buy_info.get("price", 0)
    signature = buy_info.get("signature", "")
    
    wallet_short = wallet[:6] + "..."
    tx_link = f"https://solscan.io/tx/{signature}"
    
    return (
        f"🟢 WALLET BUY DETECTED\n\n"
        f"🪙 Token: {coin_symbol}\n"
        f"👛 Wallet: {wallet_short}\n"
        f"💰 Buy Size: ${int(usd):,}\n"
        f"📊 Price: ${price}\n"
        f"🔗 Tx: {tx_link}"
    )
```

## Data Structure

### Coin Object
```python
{
    "ca": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "symbol": "USDC",
    "start_mc": 1000000,
    "alerts": {
        "wallets": {
            "enabled": True,
            "addresses": [
                "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                "..."
            ],
            "min_buy_usd": 300
        }
    },
    "wallet_state": {
        "last_signature": "5KAStV9CGVuv8rMF..."  # Updated by engine
    }
}
```

## Testing

Run comprehensive pipeline test:
```bash
python3 test_wallet_detection.py
```

Tests:
- ✅ Layer 1: Signature fetching
- ✅ Layer 2: Transaction parsing (with version support)
- ✅ Layer 3: Alert engine with deduplication
- ✅ Integration: Full workflow with alert formatting

## Rate Limiting

**Public RPC**: ~100 requests/10 seconds
- Layer 1: 1 request per wallet
- Layer 2: 1 request per signature (up to 5)
- Total: ~6 requests per wallet per check

**Mitigation**:
- `time.sleep(0.2)` between wallets in monitor loop
- 60-second check interval
- Deduplication reduces redundant requests

**Production Recommendations**:
1. Use private RPC endpoint (higher limits)
2. Or implement request pooling/batching
3. Monitor rate limit errors and backoff

## Production Checklist

- ✅ Layer 1-3 implemented and tested
- ✅ Deduplication via last_signature
- ✅ Transaction version support (v0)
- ✅ Pro-level UX with Solscan links
- ✅ Error handling at each layer
- ✅ Integration with monitor loop
- ✅ Commit bd63691 pushed to GitHub
- ⏳ Deploy to Render with BOT_TOKEN
- ⏳ Test with controlled wallet

## Next Steps

1. **Controlled Testing**:
   - Pick a wallet you control
   - Track a small token
   - Set min_buy to $1
   - Buy the token
   - Wait for alert

2. **Deploy to Render**:
   - Set BOT_TOKEN environment variable
   - Code already on GitHub (bd63691)
   - Monitor logs for errors

3. **Future Enhancements** (User Roadmap):
   - **D**: UX Polish (dashboard cards, inline flows)
   - **B**: Group Monetization (pro tiers)
   - **A**: Meta-wide alerts (lists heating up)
   - **C**: Performance optimization (RPC batching, caching)

## Performance Notes

**Strengths**:
- True on-chain detection (not aggregated signals)
- Wallet-specific tracking
- Zero false positives with strict filtering
- Deduplication prevents spam

**Limitations**:
- Public RPC rate limits (~100 req/10s)
- Each wallet check = ~6 RPC requests
- 60-second delay between checks

**For High-Volume**:
- Use private RPC (Helius, QuickNode, etc.)
- Implement WebSocket subscriptions
- Consider RPC batching for multiple wallets
