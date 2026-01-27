# PHASE 1 — UX DESIGN (Skeleton)

**Status:** 🎨 DESIGN PHASE (NO CODE YET)  
**Goal:** Answer: "What are the first 3 things a user sees and taps?"  
**Scope:** Home screen → Button purposes → One complete flow (Track Coin)

---

## THE HOME SCREEN (Everything Starts Here)

This is the most important screen. Don't overthink it.

```
┌─────────────────────────────┐
│                             │
│   🚨 Trench Alert Bot       │
│                             │
│  Track coins. Track wallets.│
│  Get smart alerts.          │
│                             │
│  What do you want to do?    │
│                             │
│ ┌─────────────────────────┐ │
│ │  ➕ Track Coin          │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │  👀 Watch Wallets       │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │  📂 Lists / Meta        │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │  📊 Dashboard           │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │  ℹ️ Help                │ │
│ └─────────────────────────┘ │
│                             │
└─────────────────────────────┘
```

**Design Principles:**
- ✅ One job per button
- ✅ Clear emoji (visual scanning)
- ✅ Friendly tone ("What do you want to do?")
- ❌ No commands (`/start`, `/add`, etc.)
- ❌ No walls of text
- ❌ No hidden features

---

## BUTTON PURPOSES (No Implementation Details)

### ➕ Track Coin

**What it does:**
1. User pastes contract address
2. Bot detects token info (MC, liquidity)
3. User chooses alert types (MC, %, X, Wallet, ATH)
4. Bot saves coin with alerts

**User psychology:**
- "I found an interesting coin, let me track it"
- Primary feature
- Most frequently used

**Entry point:** User has a CA they want to monitor

---

### 👀 Watch Wallets

**What it does:**
1. User adds wallet addresses (with optional labels)
2. Bot watches those wallets
3. Alerts user when they buy coins user is tracking

**User psychology:**
- "I want to follow smart money"
- "When [Wallet X] buys, I want to know"
- Insider feeling

**Entry point:** User found a smart wallet they want to follow

**Note:** Wallets are ADD-ON to coins, not separate system

---

### 📂 Lists / Meta

**What it does:**
1. User creates lists (narratives): "AI Coins", "Gaming", "DeFi"
2. User adds coins to lists
3. User sees list health, meta movement

**User psychology:**
- "I think AI is next, let me group these coins"
- "Is Gaming narrative heating up?"
- Sophisticated trader feels

**Entry point:** User wants to organize coins by theme

---

### 📊 Dashboard

**What it does:**
- Shows all coins
- Shows all wallets
- Shows all lists
- Shows health/status of everything
- READ-ONLY (no config here)

**User psychology:**
- "What's my overall exposure?"
- "What needs attention?"
- Check-in point

**Entry point:** User wants quick overview

---

### ℹ️ Help

**What it does:**
- Explains what bot does
- Explains each feature
- Answers common questions
- Builds trust

**User psychology:**
- "I'm new, help me understand"
- "I'm confused about [feature]"
- Safety valve

**Entry point:** User is lost or wants to learn

---

## FLOW: TRACK COIN (COMPLETE)

This is the **most important flow**. Design it perfectly.

### Step 1️⃣ — Entry

```
User taps: ➕ Track Coin

Bot asks:
┌─────────────────────────────┐
│                             │
│  ➕ Track Coin              │
│                             │
│  Paste token contract       │
│  address                    │
│                             │
│  (user sends: CA)           │
│                             │
└─────────────────────────────┘
```

**What happens:**
- User types/pastes contract address
- Bot validates it's a valid Solana token
- Bot fetches token data (MC, liquidity, volume)
- Continue to Step 2

**Error case:**
```
Bot: ❌ Invalid token. Send CA again.
(user tries again)
```

---

### Step 2️⃣ — Token Detected

```
Bot shows:
┌─────────────────────────────┐
│                             │
│  ✅ 🪙 Token Detected       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ │
│                             │
│  💰 Market Cap: $82,300     │
│  💧 Liquidity: $120,000     │
│                             │
│  What do you want to track? │
│  (Select multiple)          │
│                             │
│ ┌─────────────────────────┐ │
│ │ 📉 Market Cap Levels    │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │ 📈 % Moves              │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │ 🚀 X Multiples          │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │ 👀 Wallet Buys          │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │ 🔥 ATH Reclaim          │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │ ✅ Done                 │ │
│ └─────────────────────────┘ │
│                             │
└─────────────────────────────┘
```

**Design notes:**
- Shows auto-detected data (proves bot is "smart")
- User sees current MC and liquidity (context)
- User chooses alert types by tapping buttons
- **Can select multiple** (hint: "Select multiple")
- User taps "Done" when finished configuring

**Flow is:** Tap button → Configure that alert type → Shown confirmation → Back to this screen (or can add more)

---

### Step 3️⃣ — User Configures Alert Types

**If user taps: 📉 Market Cap Levels**

```
Bot asks:
┌─────────────────────────────┐
│                             │
│  📉 Market Cap Level        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ │
│                             │
│  Current: $82,300           │
│                             │
│  Send market cap to alert:  │
│  (e.g., 50000)              │
│                             │
│  (user sends number)        │
│                             │
└─────────────────────────────┘
```

**Design notes:**
- Shows current MC (reference point)
- Example provided (50000)
- User sends number
- Confirm and return to alert selection

---

**If user taps: 📈 % Moves**

```
Bot asks:
┌─────────────────────────────┐
│                             │
│  📈 % Movement Alert        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ │
│                             │
│  Alert when price moves     │
│  up or down by X%           │
│                             │
│  Send % value:              │
│  (e.g., 30 for ±30%)        │
│                             │
│  (user sends number)        │
│                             │
└─────────────────────────────┘
```

**Design notes:**
- Explains what % means
- Example provided
- Simple and clear

---

**If user taps: 🚀 X Multiples**

```
Bot asks:
┌─────────────────────────────┐
│                             │
│  🚀 X Multiple Alert        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ │
│                             │
│  Alert when token reaches   │
│  X multiplier from start    │
│                             │
│  Send X value:              │
│  (e.g., 2 for 2x, 5 for 5x) │
│                             │
│  (user sends number)        │
│                             │
└─────────────────────────────┘
```

**Design notes:**
- Explains what X means
- Examples provided (2x, 5x)
- Clear and helpful

---

**If user taps: 👀 Wallet Buys**

```
Bot asks:
┌─────────────────────────────┐
│                             │
│  👀 Wallet Buys             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ │
│                             │
│  Alert when specific        │
│  wallets buy this coin      │
│                             │
│  Your wallets:              │
│  • Smart Money (1)          │
│  • Dev Wallet (2)           │
│                             │
│ ┌─────────────────────────┐ │
│ │ Select wallet...        │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │ ➕ Add new wallet       │ │
│ └─────────────────────────┘ │
│                             │
└─────────────────────────────┘
```

**Design notes:**
- Shows existing wallets (user can choose)
- Option to add new wallet
- Wallet selection happens here
- Then back to alert selection

---

**If user taps: 🔥 ATH Reclaim**

```
Bot shows:
┌─────────────────────────────┐
│                             │
│  ✅ 🔥 ATH Reclaim Added    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ │
│                             │
│  You'll be alerted when     │
│  token reaches 95% of ATH   │
│                             │
│  (no additional config)     │
│                             │
│  Back to alerts selection   │
│                             │
└─────────────────────────────┘
```

**Design notes:**
- No input needed (automatic at 95%)
- Instant confirmation
- Back to alert selection

---

### Step 4️⃣ — Confirmation & Done

**After user taps ✅ Done**

```
Bot shows:
┌─────────────────────────────┐
│                             │
│  ✅ Coin Added              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ │
│                             │
│  Active alerts:             │
│  • MC ≤ $50,000             │
│  • % ±30%                   │
│  • Wallet: Smart Money      │
│  • ATH reclaim              │
│                             │
│  Use Dashboard to monitor   │
│                             │
└─────────────────────────────┘
```

**Design notes:**
- Lists ALL active alerts
- Shows exactly what will trigger
- Professional confirmation
- User feels confident

**Next:** User goes back to home screen or can track another coin

---

## WATCH WALLETS FLOW (Complete Design)

**Wallet tracking lets users follow smart wallets across ALL their tracked coins.**

Wallets are global per user. Once added, they can be selected when setting up "Wallet Buy" alerts on any coin.

---

### Entry — Main Wallet Menu

```
User taps: 👀 Watch Wallets

Bot shows:
┌─────────────────────────────┐
│                             │
│  👀 Wallet Tracking         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ │
│                             │
│  Track smart wallets and    │
│  get alerts when they buy   │
│  coins you're monitoring.   │
│                             │
│ ┌─────────────────────────┐ │
│ │ ➕ Add Wallet           │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │ 📋 My Wallets (2)       │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │ ◀ Back                  │ │
│ └─────────────────────────┘ │
│                             │
└─────────────────────────────┘
```

**Design notes:**
- Clean, simple menu
- Two main actions: Add or view
- Shows count of existing wallets

---

### Add Wallet — Step-by-Step

#### Step 1️⃣ — Get Address

```
User taps: ➕ Add Wallet

Bot asks:
┌─────────────────────────────┐
│                             │
│  📥 Add Wallet              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ │
│                             │
│  Send a Solana wallet       │
│  address (paste full CA)    │
│                             │
│  (user sends: 9B5XlmKz2...) │
│                             │
└─────────────────────────────┘
```

**Design notes:**
- Simple, one-line prompt
- Example hint (paste full CA)
- User sends address

---

#### Step 2️⃣ — Get Optional Label

```
Bot asks:
┌─────────────────────────────┐
│                             │
│  📝 Name this wallet        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ │
│                             │
│  Give it a label (optional) │
│                             │
│  e.g. Smart Money, Dev,     │
│      Insider #1             │
│                             │
│  Or type 'skip' for default │
│                             │
│  (user sends: Smart Money)  │
│                             │
└─────────────────────────────┘
```

**Design notes:**
- Optional, not required
- Examples provided
- 'skip' option available
- User sends name or skips

---

#### Step 3️⃣ — Confirmation

```
Bot shows:
┌─────────────────────────────┐
│                             │
│  ✅ Wallet Added            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ │
│                             │
│  Name: Smart Money          │
│  Address: 9B5X...Kz2        │
│                             │
│  You can now select this    │
│  wallet when setting up     │
│  coin alerts.               │
│                             │
└─────────────────────────────┘
```

**Design notes:**
- Shows what was saved
- Truncates address for display
- Explains next step (using wallet in alerts)
- Back to main menu

---

### My Wallets — View List

```
User taps: 📋 My Wallets

Bot shows:
┌─────────────────────────────┐
│                             │
│  📋 Your Wallets (2)        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ │
│                             │
│  1. Smart Money             │
│     9B5XlmKz2mP8jK4L        │
│                             │
│  2. Dev Wallet              │
│     4xY7QpRs9TuV1WxYz       │
│                             │
│  (Read-only view)           │
│                             │
└─────────────────────────────┘
```

**Design notes:**
- Read-only list
- Shows full address (truncated display)
- Shows count
- Simple, clean
- Can add remove/edit later

---

### Integration — Selecting Wallets in Track Coin

**When user is tracking a coin and taps: 👀 Wallet Buys**

```
User taps: 👀 Wallet Buys

Bot shows:
┌─────────────────────────────┐
│                             │
│  👀 Wallet Buy Alerts       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ │
│                             │
│  Select wallets to watch    │
│  for buys on this coin:     │
│                             │
│ ┌─────────────────────────┐ │
│ │ ☑ Smart Money           │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │ ☐ Dev Wallet            │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │ ◀ Back                  │ │
│ └─────────────────────────┘ │
│                             │
└─────────────────────────────┘
```

**Design notes:**
- Shows all user wallets
- User can select multiple
- Buttons toggle on/off
- Back button returns to alert selection

---

### Edge Case — No Wallets Yet

```
User taps: 👀 Wallet Buys
(but has not added any wallets)

Bot shows:
┌─────────────────────────────┐
│                             │
│  ⚠️ No Wallets Added        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ │
│                             │
│  You haven't added any      │
│  wallets yet.               │
│                             │
│  Add wallets first to use   │
│  this feature.              │
│                             │
│ ┌─────────────────────────┐ │
│ │ ➕ Add Wallet           │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │ ◀ Back                  │ │
│ └─────────────────────────┘ │
│                             │
└─────────────────────────────┘
```

**Design notes:**
- User-friendly error
- Provides action (add wallet)
- Back to alerts if they change mind

---

### Data Structure (Lock This In)

**Each user's wallets (stored in data.json):**

```json
{
  "user_id": {
    "coins": [...],
    "profile": {...},
    "wallets": [
      {
        "address": "9B5XlmKz2mP8jK4L9nOpQ",
        "label": "Smart Money"
      },
      {
        "address": "4xY7QpRs9TuV1WxYzAbCd",
        "label": "Dev Wallet"
      }
    ]
  }
}
```

**Storage rules:**
- Wallets are global per user
- Each coin's alerts reference wallet addresses
- No duplicates (check before adding)
- Addresses should be validated (basic format check)

---

### Alert Confirmation (When wallet alert is selected)

```
User selects: Smart Money and Dev Wallet
User taps: ✅ Done

Bot shows:
┌─────────────────────────────┐
│                             │
│  ✅ Coin Added              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ │
│                             │
│  Active alerts:             │
│  • MC ≤ $50,000             │
│  • % ±30%                   │
│  • 👀 Wallets:              │
│    - Smart Money            │
│    - Dev Wallet             │
│  • ATH reclaim              │
│                             │
│  Use Dashboard to monitor   │
│                             │
└─────────────────────────────┘
```

**Design notes:**
- Shows all alerts including selected wallets
- Clear list of which wallets are being tracked
- User feels confident

---

## WALLET ALERTS (When they trigger)

### Good Alert Message (Smart & Clean)

```
When wallet buys > $300:

👀 Wallet Buy Detected
━━━━━━━━━━━━━━━━━━━━━

Wallet: Smart Money
Coin: BONK
Buy Size: $3,200
MC: $74k

First buy by this wallet.
```

### Alert Rules (CRITICAL — prevents spam)

Alert ONLY when ALL are true:

1. ✅ Wallet makes a transaction
2. ✅ Transaction is a BUY (not sell)
3. ✅ Buy size ≥ $300 (configurable)
4. ✅ Coin is already tracked by user
5. ✅ First buy OR significant buy

### Non-Alerts (SILENT — avoids spam)

❌ Wallet sells → No alert  
❌ Wallet swaps dust (<$100) → No alert  
❌ Wallet buys untracked coin → No alert  
❌ Same wallet buys same coin again (within day) → No alert  

**Philosophy:** Signal, not noise.

---

## IMPLEMENTATION TIMELINE

### Phase A (NOW) — Design & Storage

- [x] Define wallet data structure
- [x] Design Watch Wallets flow
- [x] Design wallet selection in Track Coin
- [ ] Implement storage (add_wallet, get_wallets, etc.)
- [ ] Implement UX (buttons, menus)

### Phase B (NEXT) — Tx Detection

- [ ] Integrate Helius/RPC for wallet monitoring
- [ ] Parse buy/sell transactions
- [ ] Calculate buy sizes
- [ ] Trigger alerts

### Phase C (LATER) — Enhancements

- [ ] Edit wallet labels
- [ ] Remove wallets
- [ ] Configure minimum buy size
- [ ] View wallet transaction history


---

## LISTS / META FLOW (High-level sketch only)

**Do NOT implement yet. Just map it out.**

### Entry

```
User taps: 📂 Lists / Meta

Bot shows:
┌─────────────────────────────┐
│                             │
│  📂 Lists & Narratives      │
│                             │
│  Group coins by theme,      │
│  track meta movement        │
│                             │
│ ┌─────────────────────────┐ │
│ │ ➕ Create list          │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │ 📂 My Lists (2)         │ │
│ └─────────────────────────┘ │
│                             │
└─────────────────────────────┘
```

### Create List

```
User taps: ➕ Create list

1. Bot: "Name your list"
   (user: "AI Coins")

2. Bot: "Add coins (paste CAs)"
   (user: CA1, CA2, CA3)

3. Bot: "✅ List created with 3 coins"
   Back to Lists
```

### My Lists

```
User taps: 📂 My Lists

Shows:
• AI Coins (3 coins)
• Gaming (5 coins)
• DeFi (2 coins)

(Read-only view)
```

---

## DASHBOARD FLOW (High-level sketch only)

**Do NOT implement yet. Just map it out.**

```
User taps: 📊 Dashboard

Bot shows overview:
┌─────────────────────────────┐
│  📊 Dashboard               │
│                             │
│  Coins tracked: 5           │
│  Wallets watched: 2         │
│  Lists created: 3           │
│                             │
│  Recent alerts:             │
│  • BONK MC down 20%         │
│  • SHIB 2x reached          │
│                             │
│  Use buttons to drill down  │
│                             │
└─────────────────────────────┘
```

(Read-only, informational)

---

## HELP FLOW (High-level sketch only)

**Do NOT implement yet. Just map it out.**

```
User taps: ℹ️ Help

Bot shows:
┌─────────────────────────────┐
│  ℹ️ Help                    │
│                             │
│  Track Coins                │
│  Paste CA → Choose alerts   │
│  → Get smart alerts         │
│                             │
│  Watch Wallets              │
│  Add wallets → Get alerts   │
│  when they buy your coins   │
│                             │
│  Lists / Meta               │
│  Group coins by theme       │
│  → Track meta movement      │
│                             │
│  Dashboard                  │
│  See all your positions     │
│                             │
└─────────────────────────────┘
```

---

## DESIGN RULES (Non-negotiable)

### ✅ Do This

- Clean buttons (1 action per button)
- Show data (auto-detected MC, current price)
- Provide examples (e.g., "50000")
- Confirmations are clear ("✅ Alert Set")
- Multi-step flows are short (2-4 steps max)
- Navigation is obvious (Back, Done, etc.)

### ❌ Don't Do This

- No hidden commands (`/track`, `/add`, etc.)
- No walls of text
- No configuration outside the flow
- No features users don't explicitly tap
- No confusing abbreviations
- No assumes knowledge of blockchain

---

## FIRST USER EXPERIENCE (The Journey)

This is what a brand new user sees:

```
1. User discovers bot, taps /start
   → Sees Home Screen (5 buttons)
   → Feels: "Oh, this is simple and clear"

2. User wants to track BONK
   → Taps ➕ Track Coin
   → Pastes CA
   → Bot detects BONK, shows MC & liquidity
   → User feels: "Wow, this is smart"

3. User chooses alert types
   → Taps buttons, fills in thresholds
   → Sees confirmation
   → Feeling: "I'm in control, clear alerts"

4. User goes to Dashboard
   → Sees BONK with alerts
   → Simple, organized
   → Feeling: "This works"

5. User recommends to friend
   → Thought: "Simple, smart, useful"
```

---

## WHAT'S NOT INCLUDED (YET)

🚫 Group support (Phase 5)  
🚫 Advanced monitoring loop (Phase 2)  
🚫 Wallet buy alerts (Phase 3)  
🚫 List movement detection (Phase 4)  
🚫 Storage implementation (Phase 2)  
🚫 Any code (Phase 2+)

---

## NEXT STEP

**DO NOT CHANGE THIS YET.**

Validate this UX design:

1. Does this feel natural?
2. Are the flows clear?
3. Is the home screen obvious?
4. Would a new user understand this?
5. Is anything missing?

Once we confirm this UX skeleton is right, we move to Phase 2 (code implementation).

---

## SUMMARY

**Home Screen:** 5 buttons, clear purpose  
**Track Coin:** 4 steps, complete flow  
**Watch Wallets:** Sketch (implementation phase)  
**Lists / Meta:** Sketch (implementation phase)  
**Dashboard:** Sketch (implementation phase)  
**Help:** Sketch (implementation phase)  

**Status:** ✅ UX DESIGN COMPLETE (no code)  
**Next:** Phase 2 — Code Implementation (buttons, navigation, logic)
