# WALLET TRACKING — IMPLEMENTATION ROADMAP

**Status:** ✅ UX DESIGN COMPLETE  
**Next Phase:** Implementation (Phase 2)

---

## WHAT'S LOCKED IN (Design Phase Complete)

✅ Wallet data structure (address + label)  
✅ Watch Wallets flow (Add > View > Back)  
✅ Wallet selection in Track Coin flow (checkboxes, no address input)  
✅ Alert trigger rules (smart filtering, no spam)  
✅ Alert message format (exact layout)  
✅ Storage requirements (global per user, max 20 wallets)  

---

## WHAT NEEDS TO BE CODED

### Phase 2a: Storage Layer

**File:** `storage.py`

Need these functions:
- `add_wallet(user_id, address, label)` → returns True/False
- `get_user_wallets(user_id)` → returns list of wallets
- `remove_wallet(user_id, address)` → returns True/False

Validation:
- Check for duplicates (same user can't add same address twice)
- Basic format check on address (should be Solana address length)
- Enforce max 20 wallets per user

---

### Phase 2b: UX Layer

**File:** `app.py`

Need these handlers:

#### 1. **Home Screen Button**
```python
# In home_router():
elif callback_query.data == 'action_wallets':
    # Show Watch Wallets menu
    # [➕ Add Wallet] [📋 My Wallets] [◀ Back]
```

#### 2. **Add Wallet Flow**
```python
# States to add to STATE_MACHINE:
'wallet_address'     # Waiting for address input
'wallet_label'       # Waiting for label input (optional)
'wallet_confirm'     # Showing confirmation

# Handlers:
wallet_address()     # Get address from user
wallet_label()       # Get label from user
wallet_confirm()     # Show what was saved
```

#### 3. **My Wallets View**
```python
# Callback:
action_view_wallets()  # Show read-only list
```

#### 4. **Wallet Selection in Track Coin**
```python
# In alert type selection (when user taps 👀 Wallet Buys):
action_wallet_buys()   # Show user's wallets as checkboxes
toggle_wallet()        # Handle checkbox toggle
```

---

## DATA FLOW (Reference)

### When User Adds Wallet

```
User taps [➕ Add Wallet]
    ↓
Bot: "Send wallet address"
    ↓
User sends: "9B5XlmKz2mP8jK4L"
    ↓
Bot: "Give it a label (optional)"
    ↓
User sends: "Smart Money" (or "skip")
    ↓
storage.add_wallet(user_id, "9B5X...", "Smart Money")
    ↓
Bot: "✅ Wallet Added"
    ↓
Back to Watch Wallets menu
```

### When User Selects Wallet for Coin Alert

```
User taps [👀 Wallet Buys]
    ↓
storage.get_user_wallets(user_id)
    ↓
Display checkboxes with wallet labels
    ↓
User taps checkboxes to select
    ↓
User taps [✅ Done]
    ↓
Save selected wallets to coin's alert config
    ↓
Show confirmation with selected wallets listed
```

---

## ALERT TRIGGER LOGIC (Phase 2c — LATER)

**NOT in Phase 2a/2b. This is Phase 2c.**

When you receive wallet transaction data:

```python
def should_alert_wallet(wallet_address, transaction):
    """Check if this wallet transaction warrants an alert"""
    
    # Rule 1: Must be a BUY (not sell)
    if transaction.type != 'buy':
        return False
    
    # Rule 2: Must be significant size (>= $300)
    if transaction.amount_usd < 300:
        return False
    
    # Rule 3: User must be tracking this coin
    if coin_not_in_user_tracked_coins(user_id, transaction.coin):
        return False
    
    # Rule 4: Must be first buy OR significant buy (prevent spam)
    if not is_first_or_significant_buy(wallet_address, transaction.coin):
        return False
    
    return True
```

**Implementation delay:** On-chain data fetching is Phase 2c. Start with Phase 2a/2b storage + UX.

---

## CHECKLIST FOR PHASE 2 IMPLEMENTATION

### Phase 2a: Storage

- [ ] Add `add_wallet()` to storage.py
- [ ] Add `get_user_wallets()` to storage.py
- [ ] Add `remove_wallet()` to storage.py
- [ ] Add validation (no duplicates, max 20)
- [ ] Test storage functions work
- [ ] Verify data persists to data.json

### Phase 2b: UX

- [ ] Add `wallet_address` state handler
- [ ] Add `wallet_label` state handler
- [ ] Add `wallet_confirm` state handler
- [ ] Add `action_view_wallets()` callback
- [ ] Add `action_wallet_buys()` callback (shows checkboxes)
- [ ] Add `toggle_wallet()` for checkbox handling
- [ ] Wire up home_router to show wallet menu
- [ ] Test all flows end-to-end

### Phase 2c: Alert Triggering (LATER)

- [ ] Integrate Helius/RPC for wallet monitoring
- [ ] Parse buy/sell transactions
- [ ] Calculate buy sizes
- [ ] Implement `should_alert_wallet()` logic
- [ ] Send alert messages

---

## CURRENT CODE STATE

### What Already Exists

From earlier Parts 3-5 implementation in `app.py`:
- `wallet_add()` — handler started, needs refactoring
- `wallet_list()` — handler started, needs refactoring
- `wallet_back()` — handler started

From `storage.py`:
- `add_wallet()` — function exists
- `get_user_wallets()` — function exists
- `remove_wallet()` — function exists

**Note:** These functions exist but may need refinement for Phase 2 exact specs.

---

## KEY DESIGN CONSTRAINTS (Don't violate)

1. ✅ **Wallets are global per user** (not per coin)
2. ✅ **Selected PER COIN** (when setting up alert)
3. ✅ **No address input in Track Coin** (reuse existing wallets only)
4. ✅ **Read-only view** in My Wallets (no edit/delete yet)
5. ✅ **Max 20 wallets** per user (prevent abuse)
6. ✅ **No duplicates** (same address twice = error)
7. ✅ **Label is optional** (address is required)
8. ✅ **Smart alert filtering** (no spam trades <$100 or duplicates)

---

## SUCCESS CRITERIA

**Phase 2a/2b complete when:**

- [ ] User can add wallet with address + optional label
- [ ] User can view all their wallets (read-only)
- [ ] User can select wallets when tracking a coin
- [ ] Confirmation shows which wallets are selected
- [ ] Data persists across sessions (saves to data.json)
- [ ] No errors, clean UX, all flows work

**NOT required yet:**
- ❌ On-chain transaction detection
- ❌ Alert sending
- ❌ Edit/delete wallets
- ❌ Wallet transaction history

---

## NEXT STEPS

1. **User Review:** Confirm this design matches your intent
2. **Phase 2 Implementation:** Code the storage + UX flows
3. **Testing:** Test end-to-end before Phase 2c
4. **Phase 2c:** Later, add on-chain detection and alerting

**Questions before coding?**
