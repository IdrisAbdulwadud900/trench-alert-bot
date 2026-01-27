# PHASE 2c — LINK WALLETS TO COINS (READY TO BUILD)

## What Phase 2c Does

When user is tracking a coin and selecting alert types:

**Current flow:**
```
[📉 Market Cap Levels]
[📈 % Moves]
[🚀 X Multiples]
[🔥 ATH Reclaim]
[✅ Done]
```

**After Phase 2c:**
```
[📉 Market Cap Levels]
[📈 % Moves]
[👀 Wallet Buys]  ← NEW
[🚀 X Multiples]
[🔥 ATH Reclaim]
[✅ Done]
```

---

## Implementation Steps

### Step 1: Add button to alert selection

In `handle_message()` where token info is displayed:

```python
keyboard = [
    [InlineKeyboardButton("📉 Market Cap Levels", callback_data="alert_mc")],
    [InlineKeyboardButton("📈 % Moves", callback_data="alert_pct")],
    [InlineKeyboardButton("👀 Wallet Buys", callback_data="alert_wallet")],  # ← ADD THIS
    [InlineKeyboardButton("🚀 X Multiples", callback_data="alert_x")],
    [InlineKeyboardButton("🔥 ATH Reclaim", callback_data="alert_reclaim")],
    [InlineKeyboardButton("✅ Done", callback_data="alert_done")]
]
```

### Step 2: Add handler for alert_wallet choice

In `alert_choice()` function, add after other alert handlers:

```python
elif choice == "alert_wallet":
    wallets = get_wallets(user_id)
    
    if not wallets:
        # User has no wallets yet
        await query.message.reply_text(
            "⚠️ No Wallets Added\n\n"
            "Add wallets first to use this feature.\n\n"
            "Go to 👀 Watch Wallets to add wallets.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀ Back", callback_data="alert_back")]
            ])
        )
        return
    
    # Show wallet checkboxes
    keyboard = []
    for wallet in wallets:
        label = wallet.get('label', 'Unnamed Wallet')
        # Using ☑ for visual checkbox effect
        keyboard.append([
            InlineKeyboardButton(
                f"☑ {label}",
                callback_data=f"wallet_select_{wallet['address']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("✅ Done", callback_data="wallet_select_done")
    ])
    
    await query.message.reply_text(
        "👀 Select Wallets\n\n"
        "Which wallets to watch for buys on this coin?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    # Initialize selected wallets in state
    state = user_state.get(user_id)
    if state:
        state["selected_wallets"] = []
```

### Step 3: Handle wallet selection toggles

Add in `alert_choice()`:

```python
elif choice.startswith("wallet_select_"):
    user_id = query.from_user.id
    state = user_state.get(user_id)
    
    if not state:
        return
    
    if choice == "wallet_select_done":
        # Done selecting wallets
        wallets_list = state.get("selected_wallets", [])
        
        if wallets_list:
            state["alerts"]["wallets"] = wallets_list
            
            # Show confirmation
            selected_wallets = get_wallets(user_id)
            wallet_names = [w['label'] for w in selected_wallets if w['address'] in wallets_list]
            
            msg = "✅ Wallets Selected\n\n"
            msg += "Monitoring wallets:\n"
            for name in wallet_names:
                msg += f"• {name}\n"
            
            await query.message.reply_text(msg)
        
        # Return to alert selection
        state["step"] = "choose_alert"
        # Show alert menu again
        # (reuse existing alert selection keyboard)
        return
    
    # Handle individual wallet toggle
    wallet_address = choice.replace("wallet_select_", "")
    
    if wallet_address in state.get("selected_wallets", []):
        # Toggle OFF
        state["selected_wallets"].remove(wallet_address)
        toggle_state = "☐"  # unchecked
    else:
        # Toggle ON
        if "selected_wallets" not in state:
            state["selected_wallets"] = []
        state["selected_wallets"].append(wallet_address)
        toggle_state = "☑"  # checked
    
    # Show updated list
    wallets = get_wallets(user_id)
    keyboard = []
    
    for wallet in wallets:
        label = wallet.get('label', 'Unnamed Wallet')
        is_selected = wallet['address'] in state.get("selected_wallets", [])
        check = "☑" if is_selected else "☐"
        
        keyboard.append([
            InlineKeyboardButton(
                f"{check} {label}",
                callback_data=f"wallet_select_{wallet['address']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("✅ Done", callback_data="wallet_select_done")
    ])
    
    await query.message.edit_text(
        "👀 Select Wallets\n\n"
        "Which wallets to watch for buys on this coin?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
```

### Step 4: Show confirmation in final alert summary

When displaying final alert configuration before saving coin:

```python
# In the confirmation message:
if "wallets" in alerts and alerts["wallets"]:
    wallet_list = get_wallets(user_id)
    wallet_names = [w['label'] for w in wallet_list if w['address'] in alerts["wallets"]]
    
    for name in wallet_names:
        msg += f"• 👀 {name}\n"
```

---

## Data Structure After Phase 2c

```python
coin = {
    "ca": "...",
    "start_mc": 50000,
    "alerts": {
        "mc": 30000,
        "pct": 30,
        "x": 2.5,
        "reclaim": True,
        "wallets": [  # ← NEW
            "9B5XlmKz2mP8jK4L9nOpQrStUvWxYzAbCdEfGhIjKl",
            "4xY7QpRs9TuV1WxYzAbCdEfGhIjKlMnOpQrStUvWx"
        ]
    },
    "triggered": {...}
}
```

---

## Alert Confirmation Example

After Phase 2c, confirmation shows:

```
✅ Coin Added

Active alerts:
• MC ≤ $30,000
• % ±30%
• 👀 Smart Money
• 👀 Dev Team
• ATH reclaim
```

---

## UX Flow Diagram

```
Track Coin Flow
    ↓
User sends CA
    ↓
Token detected, alerts menu shown
    ↓
User taps [👀 Wallet Buys]
    ↓
Bot shows: "Select Wallets"
    ├─ [☑ Smart Money]
    ├─ [☐ Dev Team]
    ├─ [☐ Insider #1]
    └─ [✅ Done]
    ↓
User taps wallets to toggle
    ↓
User taps [✅ Done]
    ↓
Confirmation: "Wallets Selected - Smart Money, Dev Team"
    ↓
Back to alert selection menu
    ↓
User taps [✅ Done] (for final coin confirmation)
    ↓
Coin saved with wallet alerts configured
```

---

## Testing Phase 2c

After implementation, test:

1. ✅ Add coin, select no wallets (should error)
2. ✅ Add coin, select one wallet
3. ✅ Add coin, select multiple wallets
4. ✅ Toggle wallets on/off
5. ✅ Confirmation shows correct wallets
6. ✅ Data saves to storage
7. ✅ Can view coin and see wallet alerts

---

## Phase 3: Alert Triggering

Phase 2c just **links wallets to coins**.

Phase 3 will **detect wallet transactions** and trigger alerts:

```python
# Phase 3 logic (not yet):
def should_alert_wallet_buy(coin, wallet_address, tx):
    """
    Check if wallet buy matches alert criteria.
    
    Rules:
    - Must be a BUY (not sell)
    - Buy size ≥ $300
    - First buy or significant buy (no spam)
    - Wallet is in coin's alert list
    """
    if wallet_address not in coin["alerts"]["wallets"]:
        return False  # This wallet not being tracked for this coin
    
    if tx["type"] != "buy":
        return False  # Only buys, not sells
    
    if tx["amount_usd"] < 300:
        return False  # Ignore dust
    
    # Check for first or significant buy
    # (prevent spam, only alert on important buys)
    
    return True  # Alert this buy
```

---

## Ready to Build?

Phase 2c is straightforward:
- Add button to alert menu
- Add handlers for wallet selection
- Save selected wallets to coin data
- Show confirmation

**No new dependencies needed.** Uses existing wallets.py functions.

Build when ready!
