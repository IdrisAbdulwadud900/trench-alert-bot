# PHASE 1 VALIDATION CHECKLIST

**Purpose:** Confirm all UX is locked before Phase 2 implementation

---

## HOME SCREEN ✅

- [x] 5 buttons total
- [x] Exact labels and emoji: [🔔 Track Coin] [👀 Watch Wallets] [📊 Dashboard] [ℹ️ Help] [⚙️ Settings]
- [x] One job per button
- [x] Clear emoji for visual scanning
- [x] Friendly tone ("What do you want to do?")
- [x] No commands
- [x] No walls of text
- [x] Professional appearance

**Status:** ✅ LOCKED — Do not move, add, or remove buttons

---

## TRACK COIN FLOW ✅

### Step 1: Entry
- [x] User taps 🔔 Track Coin
- [x] Bot asks for contract address
- [x] Simple, one-line prompt
- [x] Error handling for invalid CA

**Status:** ✅ LOCKED

### Step 2: Token Detection
- [x] Auto-fetches MC and liquidity
- [x] Shows formatted data ($82,300, not 82300)
- [x] Shows 5 alert type buttons (including 👀 Wallet Buys)
- [x] Hint: "Select multiple"
- [x] Clean, professional layout

**Status:** ✅ LOCKED

### Step 3: Configuration (Per Alert Type)
- [x] Market Cap Levels (sends number)
- [x] % Moves (sends percentage)
- [x] Wallet Buys (select from list — no address input)
- [x] ATH Reclaim (auto at 95%, no input)
- [x] Each has context and examples

**Status:** ✅ LOCKED

### Step 4: Confirmation
- [x] Shows all active alerts
- [x] Lists exactly what triggers
- [x] Professional "✅ Coin Added" message
- [x] User feels confident

**Status:** ✅ LOCKED

---

## WATCH WALLETS FLOW (Sketch) ✅

### High-level Design
- [x] Entry: Two options (Add wallet, My Wallets)
- [x] Add: Address → Optional name → Confirmation
- [x] View: List of wallets with addresses
- [x] Simple, mirrors Track Coin flow

**Status:** ✅ SKETCH APPROVED

**Note:** Will refine in Phase 2

---

## LISTS / META FLOW (Sketch) ✅

### High-level Design
- [x] Entry: Two options (Create list, My Lists)
- [x] Create: Name → Add CAs → Confirmation
- [x] View: List of lists with coin counts
- [x] Simple, mirrors Track Coin flow

**Status:** ✅ SKETCH APPROVED

**Note:** Will refine in Phase 2

---

## DASHBOARD FLOW (Sketch) ✅

### High-level Design
- [x] Read-only overview
- [x] Shows counts (coins, wallets, lists)
- [x] Shows recent alerts
- [x] No configuration
- [x] Simple drill-down capability

**Status:** ✅ SKETCH APPROVED

**Note:** Will refine in Phase 2

---

## HELP FLOW (Sketch) ✅

### High-level Design
- [x] Explains each feature
- [x] Plain English (no jargon)
- [x] Builds trust
- [x] Answers basic questions

**Status:** ✅ SKETCH APPROVED

**Note:** Will refine in Phase 2

---

## DESIGN PRINCIPLES ✅

- [x] Clean buttons (1 action per)
- [x] Show data (auto-detected, formatted)
- [x] Provide examples ("e.g., 50000")
- [x] Clear confirmations ("✅ Alert Set")
- [x] Short flows (2-4 steps max)
- [x] Obvious navigation

**Status:** ✅ ALL PRINCIPLES MET

---

## UX QUALITY CHECKS ✅

### Clarity
- [x] New user understands first flow (Track Coin)
- [x] Each button's job is obvious
- [x] No hidden features or commands
- [x] Error messages are helpful

**Status:** ✅ CLEAR

### Simplicity
- [x] Home screen is not overwhelming
- [x] Track Coin is 4 steps, not 10
- [x] No unnecessary configuration
- [x] Users only see what they tap

**Status:** ✅ SIMPLE

### Confidence
- [x] Confirmations show exactly what will happen
- [x] Formatted data (not raw numbers)
- [x] Examples provided in prompts
- [x] Professional tone

**Status:** ✅ CONFIDENT

### Completeness
- [x] All main flows mapped
- [x] All edge cases considered (invalid CA, errors)
- [x] Multi-select working (Track Coin)
- [x] Read-only sections clear (Dashboard)

**Status:** ✅ COMPLETE

---

## WHAT WE'RE LOCKING IN

```
HOME SCREEN:
  ➕ Track Coin (fully designed)
  👀 Watch Wallets (sketched)
  📂 Lists / Meta (sketched)
  📊 Dashboard (sketched)
  ℹ️ Help (sketched)

COMPLETE FLOWS:
  ✅ Track Coin (4 steps, all alert types)

SKETCHED FLOWS:
- [x] 👀 Wallet Buys (select from user's wallets — no address input)
- [x] ❌ Custom (power-users, free text)
- [x] Each has context and examples

**Status:** ✅ LOCKED

### Step 4: Confirmation
- [x] Shows all selected alerts
- [x] Lists which wallets are selected
- [x] Shows "Use Dashboard to monitor" hint

**Status:** ✅ LOCKED

---

## WATCH WALLETS FLOW ✅

### Entry Screen
- [x] 👀 Watch Wallets button on home
- [x] Two actions: [➕ Add Wallet] [📋 My Wallets]
- [x] Simple, clear menu
- [x] [◀ Back] option

**Status:** ✅ LOCKED

### Add Wallet (3-step flow)
- [x] Step 1: User sends wallet address
- [x] Step 2: User sends optional label (or skip)
- [x] Step 3: Confirmation shows saved wallet
- [x] Back to main wallet menu

**Status:** ✅ LOCKED

### My Wallets (Read-only view)
- [x] Shows all user's wallets with labels
- [x] Shows truncated addresses
- [x] Shows count
- [x] Read-only (no edit/delete yet)

**Status:** ✅ LOCKED

### Wallet Selection in Track Coin
- [x] When user taps 👀 Wallet Buys, shows checkboxes
- [x] Lists all user's wallets (with labels)
- [x] User can select multiple
- [x] No address input (reuse existing wallets)
- [x] If no wallets exist: Show helpful error + option to add

**Status:** ✅ LOCKED

### Wallet Alert Confirmation
- [x] Shows which wallets are selected
- [x] Explains: "Alerts only on significant buys"
- [x] Confirms thresholds and rules

**Status:** ✅ LOCKED

---

## WALLET ALERT RULES ✅

Alert ONLY when ALL are true:
- [x] Wallet makes a BUY transaction (not sell)
- [x] Buy size ≥ $300 (configurable threshold)
- [x] Coin is already tracked by user
- [x] First buy OR significant buy (prevents spam)

Silent (no alerts) when:
- [x] Wallet sells
- [x] Wallet buys untracked coin
- [x] Dust trades (<$100)
- [x] Same wallet buys same coin again same day

**Philosophy:** Signal, not noise. Premium quality alerts.

**Status:** ✅ LOCKED

---

## WALLET ALERT MESSAGE FORMAT ✅

```
👀 Wallet Buy Detected
━━━━━━━━━━━━━━━━━━━━━

Wallet: Smart Money
Coin: BONK
Buy Size: $3,200
MC: $74k

First buy by this wallet.
```

- [x] Exact format (no variations)
- [x] Shows wallet label
- [x] Shows coin name
- [x] Shows buy size and MC
- [x] Shows context (first buy / significant)

**Status:** ✅ LOCKED

---

## WALLET TRACKING DATA STRUCTURE ✅

Storage in data.json:
```json
{
  "user_id": {
    "wallets": [
      {"address": "9B5XlmKz2mP8jK4L", "label": "Smart Money"},
      {"address": "4xY7QpRs9TuV1WxYz", "label": "Dev Team"}
    ]
  }
}
```

- [x] Wallets are global per user
- [x] Each wallet has address + optional label
- [x] No duplicates allowed
- [x] Max 20 wallets per user

**Status:** ✅ LOCKED

---

## DASHBOARD ✅

- [x] 📊 Dashboard button on home
- [x] Four sections: [Active Alerts] [Top Gainers] [Recent Txs] [Settings]
- [x] Read-only view (no interaction yet)
- [x] Professional layout

**Status:** ✅ LOCKED (basic version, can enhance later)

---

## HELP ✅

- [x] ℹ️ Help button on home
- [x] Four sections: [Track Coins] [Watch Wallets] [Dashboard] [Settings]
- [x] Simple descriptions
- [x] No commands

**Status:** ✅ LOCKED

---

## SETTINGS ✅

- [x] ⚙️ Settings button on home
- [x] Two toggles: [Alert Style] [Quiet Hours]
- [x] Clean, simple interface

**Status:** ✅ LOCKED

---

## DESIGN RULES (ALL FLOWS) ✅

- [x] ✅ One job per button
- [x] ✅ No hidden commands
- [x] ✅ No overwhelming text
- [x] ✅ Short flows (2-4 steps max)
- [x] ✅ Clear confirmations
- [x] ✅ Examples provided
- [x] ✅ Helpful errors (no crashes)
- [x] ✅ Read-only when safe
- [x] ✅ Signal > Noise (smart filtering)
```

---

## SIGN-OFF

**Question:** "If I were a user, what are the first 3 things I see and tap?"

**Answer:**

1. **First:** Home screen with 5 buttons
2. **Second:** I tap ➕ Track Coin (most common action)
3. **Third:** I paste a CA and choose alert types

**Status:** ✅ FULLY ANSWERED

---

## PHASE 1 STATUS

🎨 **UX DESIGN:** COMPLETE  
📋 **VALIDATION:** APPROVED  
🔒 **LOCKED IN:** YES

---

## PHASE 2 BEGINS WHEN

- [x] This UX is locked
- [x] All flows are mapped
- [x] No design changes planned
- [x] Code implementation is clear

**Ready to code:** ✅ YES

**Note:** We will NOT change this UX unless there's a critical issue.

Phase 2 is about implementing this design, not rethinking it.
