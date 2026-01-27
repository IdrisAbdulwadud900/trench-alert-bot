# WALLET TRACKING — UX FLOWS (IMPLEMENTED)

## Flow 1: Add Wallet

```
Home Screen
    ↓
User taps: 👀 Watch Wallets
    ↓
Watch Wallets Menu
    ├─ [➕ Add Wallet]  ← User taps here
    ├─ [📋 My Wallets]
    └─ [◀ Back]
    ↓
Bot: "📥 Add Wallet - Send wallet address"
    ↓
User sends: 9B5XlmKz2mP8jK4L9nOpQrStUvWxYzAbCdEfGhIjKl
    ↓
handle_message() → state: wallet_address
    └─ Validates length (30-50 chars)
    └─ Stores in state["wallet_address"]
    └─ Sets state → wallet_label
    ↓
Bot: "✅ Address saved - Give this wallet a name (optional)"
    ↓
User sends: Smart Money (or 'skip')
    ↓
handle_message() → state: wallet_label
    └─ Calls add_wallet(user_id, address, label)
    └─ wallets.py saves to wallets.json
    └─ Prevents duplicates
    ↓
Bot: "✅ Wallet Added - Name: Smart Money - Address: 9B5X...KjKl"
    ↓
State cleared. Ready for next action.
```

---

## Flow 2: View Wallets

```
Watch Wallets Menu
    ↓
User taps: [📋 My Wallets]
    ↓
alert_choice() → action: wallet_list
    └─ Calls get_wallets(user_id)
    ↓
Bot displays:
    📋 Your Wallets
    
    1. Smart Money
       9B5X...KjKl
    
    2. Dev Team
       4xY7...UvWx
```

---

## Flow 3: Return to Home

```
Watch Wallets Menu
    ↓
User taps: [◀ Back]
    ↓
alert_choice() → action: wallet_back
    └─ Shows home menu buttons
    ↓
Home Screen
    ├─ [➕ Track Coin]
    ├─ [👀 Watch Wallets]
    ├─ [📂 Lists / Meta]
    ├─ [📊 Dashboard]
    └─ [ℹ️ Help]
```

---

## Current State Machine (handle_message)

```
wallet_address state:
├─ Waits for wallet address (30-50 chars)
├─ Validates basic format
├─ Stores to state["wallet_address"]
└─ → wallet_label state

wallet_label state:
├─ Waits for label (optional)
├─ User can send label or 'skip'
├─ Calls add_wallet()
├─ Saves to wallets.json
├─ Shows confirmation
└─ → Clears state
```

---

## Data Saved (wallets.json)

```json
{
  "123456789": [
    {
      "address": "9B5XlmKz2mP8jK4L9nOpQrStUvWxYzAbCdEfGhIjKl",
      "label": "Smart Money"
    },
    {
      "address": "4xY7QpRs9TuV1WxYzAbCdEfGhIjKlMnOpQrStUvWx",
      "label": "Dev Team"
    }
  ],
  "987654321": [
    {
      "address": "9B5XlmKz2mP8jK4L9nOpQrStUvWxYzAbCdEfGhIjKl",
      "label": "My Wallet"
    }
  ]
}
```

---

## Integration Points

### In alert_choice() — Button handlers:
```python
elif choice == "action_wallets":
    # Show Watch Wallets menu
    
elif choice == "wallet_add":
    # Start wallet_address state
    
elif choice == "wallet_list":
    # Fetch & display wallets
    
elif choice == "wallet_back":
    # Return to home
```

### In handle_message() — Text input handlers:
```python
if step == "wallet_address":
    # Validate & store address
    
elif step == "wallet_label":
    # Save wallet via add_wallet()
```

### In app.py — Handler registration:
```python
app.add_handler(CallbackQueryHandler(alert_choice))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
```

---

## Next Phase: Linking Wallets to Coins

When Track Coin flow reaches alert selection:

```
Track Coin Flow
    ↓
User selects alerts for coin
    ├─ [📉 Market Cap Levels]
    ├─ [📈 % Moves]
    ├─ [🚀 X Multiples]
    ├─ [👀 Wallet Buys]  ← Next to implement
    ├─ [🔥 ATH Reclaim]
    └─ [✅ Done]
    ↓
User taps: [👀 Wallet Buys]
    ↓
alert_choice() → action: alert_wallet
    └─ Fetch get_wallets(user_id)
    └─ Show checkboxes for each wallet
    └─ User selects (multi-select)
    └─ Save selected addresses to coin["alerts"]["wallets"]
    ↓
Confirmation shows selected wallets
```

---

## Files & Functions

### wallets.py (Storage Layer)
- `load_wallets()` — Load from wallets.json
- `save_wallets(data)` — Save to wallets.json
- `add_wallet(user_id, address, label)` — Add wallet
- `get_wallets(user_id)` — Get user's wallets
- `remove_wallet(user_id, address)` — Remove wallet

### app.py (UX Layer)
- `alert_choice()` — Handle button clicks
  - `action_wallets` — Show menu
  - `wallet_add` — Start add flow
  - `wallet_list` — Show wallets
  - `wallet_back` — Return to home
  
- `handle_message()` — Handle text input
  - `wallet_address` state — Validate & store address
  - `wallet_label` state — Save wallet

### test_wallets.py (Tests)
- Test add, view, remove, duplicates, multi-user

---

## Status Summary

✅ Storage layer working  
✅ UX flows implemented  
✅ Add wallet working  
✅ View wallets working  
✅ Duplicate prevention working  
✅ Multi-user support working  
✅ All tests passing  

🔄 Next: Link wallets to coins (Phase 2c)
