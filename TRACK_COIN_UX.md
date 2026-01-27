# 🎯 Track Coin UX - Clean & Modern Flow

## Overview
The Track Coin feature now has a streamlined, modern UX that auto-detects token information and guides users through alert selection with clear, contextual prompts.

---

## The Flow

### Step 1: User Sends Token Contract Address

```
User:  /start or taps ➕ Track Coin
Bot:   "Send token contract address:"
User:  abc123def456...
```

**Behind the scenes:**
- Validates the contract address
- Calls DexScreener API to fetch token data
- Extracts Market Cap and Liquidity info

---

### Step 2: Auto-Detected Token Info

Bot responds with:

```
✅ 🪙 Token Detected
━━━━━━━━━━━━━━━━━━━━━━━━
💰 Market Cap: $82,300
💧 Liquidity: $120,000

What do you want to track?
(Select multiple)

[📉 Market Cap Levels]
[📈 % Moves]
[🚀 X Multiples]
[🔥 ATH Reclaim]
[✅ Done]
```

**Why this is better:**
- Shows actual token data (not just an echo of the CA)
- Market Cap shown in formatted USD
- Liquidity shown for context
- Clear button labels that match user intent
- "Select multiple" hint tells users they can add more alerts

---

### Step 3: Multi-Select Alert Types

User can tap buttons in any order to add multiple alerts.

#### Option A: Market Cap Level Alert

User taps: `[📉 Market Cap Levels]`

Bot responds:

```
📉 Market Cap Level
━━━━━━━━━━━━━━━━━━━━━━━━
Current: $82,300

Send the market cap to alert at (e.g., 50000)
```

User sends: `50000`

Bot responds:

```
✅ 📉 Market Cap Alert Set
━━━━━━━━━━━━━━━━━━━━━━━━
Threshold: $50,000

Active alerts:
• MC ≤ $50,000

Add more alerts or tap Done
```

---

#### Option B: % Movement Alert

User taps: `[📈 % Moves]`

Bot responds:

```
📈 % Movement Alert
━━━━━━━━━━━━━━━━━━━━━━━━
Alert when price moves ±X%

Send percentage (e.g., 30 for ±30%)
```

User sends: `30`

Bot responds:

```
✅ 📈 % Move Alert Set
━━━━━━━━━━━━━━━━━━━━━━━━
Threshold: ±30.0%

Active alerts:
• MC ≤ $50,000
• % ±30%

Add more alerts or tap Done
```

---

#### Option C: X Multiple Alert

User taps: `[🚀 X Multiples]`

Bot responds:

```
🚀 X Multiple Alert
━━━━━━━━━━━━━━━━━━━━━━━━
Alert when you reach X multiplier X

Send X value (e.g., 2 for 2x, 5 for 5x)
```

User sends: `3`

Bot responds:

```
✅ 🚀 X Multiple Alert Set
━━━━━━━━━━━━━━━━━━━━━━━━
Threshold: 3.0x

Active alerts:
• MC ≤ $50,000
• % ±30%
• X ≥ 3.0x

Add more alerts or tap Done
```

---

#### Option D: ATH Reclaim Alert

User taps: `[🔥 ATH Reclaim]`

Bot responds:

```
✅ 🔥 ATH Reclaim Alert Added
━━━━━━━━━━━━━━━━━━━━━━━━
You'll be alerted at 95% of ATH

Active alerts:
• MC ≤ $50,000
• % ±30%
• X ≥ 3.0x
• ATH reclaim (95%)

Add more alerts or tap Done
```

---

### Step 4: Confirmation & Save

User taps: `[✅ Done]`

Bot responds:

```
✅ Coin added successfully

Active alerts:
• MC ≤ $50,000
• % ±30%
• X ≥ 3.0x
• ATH reclaim (95%)

👋 First coin tips:
• Use Dashboard to monitor
• Smart alerts trigger when conditions align
• Use /mode to choose your alert profile
• Add more coins with ➕ Track Coin
```

(First-time users get tips; returning users get a simpler confirmation)

---

## Design Principles

### 1. **Clarity**
- Each step has ONE clear purpose
- Button labels describe outcomes, not actions
- Examples provided in prompts

### 2. **Context**
- Auto-detected token info shown upfront
- Current market cap displayed when setting thresholds
- Active alerts shown after each addition

### 3. **Flexibility**
- Multi-select (add alerts in any order)
- Can go back and add more
- "Done" button always visible

### 4. **Feedback**
- Every action gets immediate confirmation
- Shows what was set with emojis
- Lists all active alerts

### 5. **Guidance**
- Prompts show examples ("e.g., 50000")
- First-time users get tips
- Hints like "(Select multiple)" encourage exploration

---

## Message Templates

### Token Detection
```
✅ 🪙 Token Detected
━━━━━━━━━━━━━━━━━━━━━━━━
💰 Market Cap: [formatted number]
💧 Liquidity: [formatted number]

What do you want to track?
(Select multiple)
```

### Threshold Prompts
```
[EMOJI] [Alert Type]
━━━━━━━━━━━━━━━━━━━━━━━━
[Context about current value or explanation]

Send [what to send] (e.g., [example])
```

### Confirmation
```
✅ [EMOJI] [Alert Type] Set
━━━━━━━━━━━━━━━━━━━━━━━━
Threshold: [user's value]

Active alerts:
[list of all alerts]

Add more alerts or tap Done
```

---

## Alert Type Details

### 📉 Market Cap Level
- **What it does:** Triggers when MC drops to your target
- **Use case:** Buy the dip, catch major dumps
- **Example:** Set to $50k, alert at $50k
- **Typical range:** 10-50% of starting MC

### 📈 % Movement
- **What it does:** Triggers when price moves ±X% from entry
- **Use case:** Catch pumps and dumps
- **Example:** Set to ±30%, alerts at -30% and +30%
- **Typical range:** 20-100%

### 🚀 X Multiple
- **What it does:** Triggers when you reach X times entry price
- **Use case:** Hit profit targets
- **Example:** Set to 2x, alerts when you 2x
- **Typical range:** 2x to 10x

### 🔥 ATH Reclaim
- **What it does:** Triggers when coin recovers to 95% of ATH
- **Use case:** Bounce detection, recovery plays
- **No threshold:** Automatic at 95% of ATH
- **Always useful:** Yes, for every coin

---

## Error Handling

### Invalid Input Examples

**Invalid Market Cap:**
```
User:  sends "abc"
Bot:   ❌ Invalid number. Send a valid market cap:
```

**Invalid Percentage:**
```
User:  sends "xyz"
Bot:   ❌ Invalid number. Send a valid percentage:
```

**Invalid X Multiple:**
```
User:  sends "text"
Bot:   ❌ Invalid number. Send a valid X multiple:
```

**Invalid Token:**
```
User:  sends "invalid_address"
Bot:   ❌ Invalid token. Send CA again.
```

All errors are **recoverable** - user just resends the value.

---

## First-Time User Tips

When user adds their **first coin**, they see:

```
👋 First coin tips:
• Use Dashboard to monitor
• Smart alerts trigger when conditions align
• Use /mode to choose your alert profile
• Add more coins with ➕ Track Coin
```

This educates without overwhelming.

---

## Mobile Optimization

✅ **Big tappable buttons** - 50px+ tall for easy tapping
✅ **Short messages** - Fit in one screen
✅ **Clear emoji icons** - Visual scanning
✅ **Numbered steps** - Progress indication
✅ **Confirmation feedback** - Know it worked

---

## Comparison: Before vs After

### BEFORE
```
🪙 Token detected

💰 Start MC: $82,300

How do you want to be alerted?

[📉 Market Cap Alert]
[📈 % Change Alert]
[🚀 X Multiple Alert]
[🔥 ATH Reclaim Alert]
[🟢 Done]
```

**Issues:**
- No token data context
- Generic button labels
- No example prompts
- Unclear what to send

### AFTER
```
✅ 🪙 Token Detected
━━━━━━━━━━━━━━━━━━━━━━━━
💰 Market Cap: $82,300
💧 Liquidity: $120,000

What do you want to track?
(Select multiple)

[📉 Market Cap Levels]
[📈 % Moves]
[🚀 X Multiples]
[🔥 ATH Reclaim]
[✅ Done]
```

**Improvements:**
- ✅ Shows actual token data
- ✅ Action-oriented button labels
- ✅ Hints user can multi-select
- ✅ Clear visual hierarchy
- ✅ Emoji consistency

**When user sets threshold:**

BEFORE:
```
✅ Alert added

Active alerts:
MC, %
```

AFTER:
```
✅ 📉 Market Cap Alert Set
━━━━━━━━━━━━━━━━━━━━━━━━
Threshold: $50,000

Active alerts:
• MC ≤ $50,000

Add more alerts or tap Done
```

**Improvements:**
- ✅ Shows what type was set
- ✅ Shows the exact threshold
- ✅ Formatted currency values
- ✅ Reminds user of next steps
- ✅ Professional appearance

---

## Testing Checklist

✅ User sends valid CA
✅ Token data displays correctly
✅ Market cap formatted with commas
✅ Liquidity formatted with commas
✅ Each alert type can be selected
✅ Thresholds are properly validated
✅ Multiple alerts can be added
✅ Confirmation shows all alerts
✅ First-time users get tips
✅ Invalid input shows errors
✅ Done button saves coin
✅ Coin appears in Dashboard

---

## Code Implementation

**Key files modified:**
- `app.py` - handle_message() & alert_choice() callbacks
- No changes to storage, intelligence, or other modules

**Key functions used:**
- `get_token_data()` - Fetches market cap and liquidity
- `format_active_alerts()` - Displays alert list
- State management tracks user progress through flow

---

## UX Metrics

**Goal:** Users should understand each step without reading help text

**Success indicators:**
- Button labels self-explanatory ✓
- Prompt examples make sense ✓
- Emojis match alert types ✓
- Confirmations show clear thresholds ✓
- Error messages help recovery ✓

---

## Summary

The Track Coin flow is now:
- **Modern** - Clean, professional appearance
- **Clear** - Each step has one purpose
- **Helpful** - Auto-detected info and examples
- **Flexible** - Multi-select alerts in any order
- **Forgiving** - Easy error recovery
- **Guided** - Tips for first-time users

Users go from confusion ("What do I send?") to confidence ("I've got my alerts set up") in 5 steps.

🚀 **Result:** Higher conversion, happier users, professional bot experience
