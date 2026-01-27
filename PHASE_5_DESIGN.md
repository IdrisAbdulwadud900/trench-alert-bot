# PHASE 5: GROUP SUPPORT — UX DESIGN (LOCKED)

## CORE PRINCIPLES

1. **Separate Private & Group Modes**: Different UX, different data, different rules
2. **Admin-Only Configuration**: Only group admins can add/remove coins or change alerts
3. **Shared Signal Feed**: Groups see alerts for coins being tracked by the group
4. **Clean Alerts**: No noise, no spam, signal only
5. **Read-Only Wallets**: Members can view, admins configure

## DATA MODEL (LOCKED)

```python
# Group storage (groups.json)
{
  "-100123456789": {  # Telegram group ID (negative)
    "coins": [
      {
        "ca": "...",
        "alerts": { "mc": 50000, "ath": "reclaim" },
        "start_mc": 100000
      }
    ],
    "admins": [12345678, 87654321]  # User IDs of group admins
  }
}
```

## FLOWS (LOCKED)

### Flow 1: Group /start (Private Chat Detection)

**Trigger**: User types /start in a group

**Detection**:
```
chat_type = update.effective_chat.type  # "group" or "supergroup"
chat_id = str(update.effective_chat.id)  # Negative number

if chat_type in ["group", "supergroup"]:
    → GROUP MODE
else:
    → PRIVATE MODE (existing behavior)
```

**Response** (Group Mode):
```
🚨 Trench Alert Bot — Group Mode

I monitor coins for this group
and send alerts here.

Only group admins can configure.
Members can view status.
```

**Buttons** (GROUP):
- ➕ Track Coin (admin only)
- 📊 Status (all members)
- ℹ️ Help (all members)

**Buttons** (PRIVATE - unchanged):
- ➕ Track Coin
- 👀 Watch Wallets
- 📂 Lists / Meta
- 📊 Dashboard
- ℹ️ Help

---

### Flow 2: Admin Check (Before Any Config)

**Function** (in app.py):
```python
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if user is group admin."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Not in a group → treat as admin (private chat)
    if update.effective_chat.type not in ["group", "supergroup"]:
        return True
    
    # Get admins from Telegram
    admins = await context.bot.get_chat_administrators(chat_id)
    admin_ids = [admin.user.id for admin in admins]
    
    return user_id in admin_ids
```

**Usage**: Before any action that modifies group config:
- When user taps ➕ Track Coin
- When user removes a coin
- When user changes alerts

**Response if NOT admin**:
```
⚠️ Only group admins can configure alerts.
```

---

### Flow 3: Track Coin in Group

**Entry**: Admin taps ➕ Track Coin in group

**Reuse**: 90% of existing private chat logic
- Same CA input
- Same alert configuration  
- Same state machine

**Change**: 
```python
# Instead of storing under user_id
# Store under group_id

target_id = chat_id  # "-100123456789"
```

**Data Stored**:
```python
groups[target_id]["coins"].append({
    "ca": contract_address,
    "alerts": { ... },
    "start_mc": mc_at_tracking
})
```

**Confirmation**:
```
✅ Tracking [CA]...

This group will get alerts for:
• MC drops
• ATH reclaim
• etc.
```

---

### Flow 4: Group Status

**Entry**: Any member types `/status` in group

**Response**:
```
📊 Group Status

🪙 BONK
MC: $82,000
Alerts: MC ≤ $50k, ATH reclaim

🪙 CAT
MC: $41,000
Alerts: ±30% move, ATH $65k

🪙 WIF
MC: $125,000
No alerts configured
```

**Rules**:
- Short. Scannable.
- Show CA (truncated)
- Show current MC
- List active alerts (max 2 lines)
- NO price history, NO essays

---

### Flow 5: Group Alert Format

**Private Alert** (user sees):
```
🚨 BONK

MC: $82,000 ↓ 15%
ATH reclaim: 93% (was $95k)

Buy signal detected.
Wallet: 0x123... bought 4.2 SOL
```

**Group Alert** (group sees):
```
🚨 Group Alert — BONK

MC hit $50,000
ATH reclaim underway
```

**Rules**:
- One sentence per alert type
- NO wallet details (read-only)
- NO meta-analysis
- Signal only
- Clean line breaks

---

## PERMISSIONS MATRIX (LOCKED)

| Action | Private User | Group Member | Group Admin |
|--------|:------------:|:------------:|:----------:|
| /start | ✅ | ✅ | ✅ |
| /status | ✅ | ✅ | ✅ |
| ➕ Track Coin | ✅ | ❌ | ✅ |
| Remove coin | ✅ | ❌ | ✅ |
| Edit alerts | ✅ | ❌ | ✅ |
| View wallets | ✅ | ❌ | ❌ |
| Create lists | ✅ | ❌ | ❌ |

---

## WHAT GROUPS DO NOT HAVE (FOR NOW)

❌ Wallet tracking (read-only in v2)
❌ Lists / meta creation
❌ Per-user configuration
❌ Private alerts to specific members

These become **premium features** later.

---

## IMPLEMENTATION ORDER (LOCKED)

1. Create `groups.py` (storage module)
2. Create `is_admin()` helper in app.py
3. Update `/start` to detect group vs private
4. Create group `/status` handler
5. Create group ➕ Track Coin flow
6. Create group alert formatter
7. Integrate alerts into monitoring loop
8. Create tests (test_groups.py)

---

## DATA MIGRATION (FUTURE)

When a user adds group bot to existing group:
- Start with empty group coins list
- Admin must re-add any coins they want tracked
- No migration from private → group

This keeps data clean and explicit.

---

## NEXT AFTER PHASE 5

- **Phase 5 Extended**: Wallet wallet read-only view in groups
- **Phase 6**: On-chain wallet detection (DexScreener + Helius)
- **Phase 7**: Group meta-wide alerts
- **Phase 8**: Paid tiers (private alerts, advanced features)
