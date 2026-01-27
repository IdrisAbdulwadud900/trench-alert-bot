# Track Coin Flow - Visual Guide

## Complete User Journey

```
┌─────────────────────────────────────────┐
│ User taps ➕ Track Coin                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Bot: "Send token contract address:"     │
└──────────────┬──────────────────────────┘
               │
               ▼
        ┌──────────────┐
        │ User sends:  │
        │ abc123...    │
        └──────┬───────┘
               │
               ▼
    ┌────────────────────────┐
    │ Fetch token data from  │
    │ DexScreener API        │
    │ (MC, Liquidity)        │
    └────────────┬───────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │ ✅ 🪙 Token Detected              │
    │ ━━━━━━━━━━━━━━━━━━━━━━━━        │
    │ 💰 Market Cap: $82,300            │
    │ 💧 Liquidity: $120,000            │
    │                                    │
    │ What do you want to track?        │
    │ (Select multiple)                  │
    │                                    │
    │ [📉 Market Cap Levels]            │
    │ [📈 % Moves]                      │
    │ [🚀 X Multiples]                  │
    │ [🔥 ATH Reclaim]                  │
    │ [✅ Done]                         │
    └────────┬───────────────┬──────────┘
             │               │
    ┌────────▼─┐    ┌────────▼──────────────────┐
    │ User     │    │ User can tap buttons in   │
    │ chooses  │    │ ANY order to add multiple │
    │ alerts   │    │ alert types               │
    └────────┬─┘    └─────────────────────────────┘
             │
   ┌─────────┴──────────────────────────┐
   │                                    │
   ▼                                    ▼
```

---

## Alert Selection Paths

```
User taps [📉 Market Cap Levels]
              ▼
Bot: "📉 Market Cap Level
      ━━━━━━━━━━━━━━━━━━━━━━
      Current: $82,300
      
      Send the market cap to alert at (e.g., 50000)"
              ▼
User sends: "50000"
              ▼
Bot: "✅ 📉 Market Cap Alert Set
      ━━━━━━━━━━━━━━━━━━━━━━━━
      Threshold: $50,000
      
      Active alerts:
      • MC ≤ $50,000
      
      Add more alerts or tap Done"
              │
              └─→ User can tap another alert type
                  or tap Done


User taps [📈 % Moves]
              ▼
Bot: "📈 % Movement Alert
      ━━━━━━━━━━━━━━━━━━━━━━
      Alert when price moves ±X%
      
      Send percentage (e.g., 30 for ±30%)"
              ▼
User sends: "30"
              ▼
Bot: "✅ 📈 % Move Alert Set
      ━━━━━━━━━━━━━━━━━━━━━━━━
      Threshold: ±30.0%
      
      Active alerts:
      • MC ≤ $50,000
      • % ±30%
      
      Add more alerts or tap Done"


User taps [🚀 X Multiples]
              ▼
Bot: "🚀 X Multiple Alert
      ━━━━━━━━━━━━━━━━━━━━━━
      Alert when you reach X multiplier X
      
      Send X value (e.g., 2 for 2x, 5 for 5x)"
              ▼
User sends: "3"
              ▼
Bot: "✅ 🚀 X Multiple Alert Set
      ━━━━━━━━━━━━━━━━━━━━━━━━
      Threshold: 3.0x
      
      Active alerts:
      • MC ≤ $50,000
      • % ±30%
      • X ≥ 3.0x
      
      Add more alerts or tap Done"


User taps [🔥 ATH Reclaim]
              ▼
Bot: "✅ 🔥 ATH Reclaim Alert Added
      ━━━━━━━━━━━━━━━━━━━━━━━━
      You'll be alerted at 95% of ATH
      
      Active alerts:
      • MC ≤ $50,000
      • % ±30%
      • X ≥ 3.0x
      • ATH reclaim (95%)
      
      Add more alerts or tap Done"
```

---

## Completion Path

```
User taps [✅ Done]
              ▼
        ┌─────────────────┐
        │ Save coin with  │
        │ all alerts      │
        └────────┬────────┘
                 │
                 ▼
   ┌─────────────────────────────┐
   │ Is this first coin?         │
   └────────┬────────────────┬───┘
            │                │
       YES  │                │  NO
            ▼                ▼
   ┌──────────────────┐  ┌──────────────┐
   │ Show first-time  │  │ Show simple  │
   │ user tips        │  │ confirmation │
   └──────────────────┘  └──────────────┘
            │                     │
            ▼                     ▼
   "✅ Coin added               "✅ Coin added
    
    Active alerts:              Active alerts:
    • MC ≤ $50,000              • MC ≤ $50,000
    • % ±30%                    • % ±30%
    • X ≥ 3.0x                  • X ≥ 3.0x
    • ATH reclaim               • ATH reclaim
    
    👋 First coin tips:
    • Use Dashboard to monitor
    • Smart alerts trigger...
    • Use /mode to choose...
    • Add more coins with..."
```

---

## State Management

```
User starts: user_state = {}

After sending CA:
user_state = {
  "ca": "abc123def456...",
  "start_mc": 82300,
  "alerts": {},
  "step": "choose_alert"
}

After adding MC alert:
user_state = {
  "ca": "abc123def456...",
  "start_mc": 82300,
  "alerts": {"mc": 50000},
  "step": "choose_alert"
}

After adding % alert:
user_state = {
  "ca": "abc123def456...",
  "start_mc": 82300,
  "alerts": {"mc": 50000, "pct": 30},
  "step": "choose_alert"
}

After adding X alert:
user_state = {
  "ca": "abc123def456...",
  "start_mc": 82300,
  "alerts": {"mc": 50000, "pct": 30, "x": 3},
  "step": "choose_alert"
}

After adding Reclaim alert:
user_state = {
  "ca": "abc123def456...",
  "start_mc": 82300,
  "alerts": {"mc": 50000, "pct": 30, "x": 3, "reclaim": true},
  "step": "choose_alert"
}

After clicking Done:
user_state.pop(user_id)  # Clear state
Coin saved to storage
```

---

## Input Validation Flow

```
User sends threshold value
              ▼
        try: float(text)
         /          \
    Success         Fail
       │              │
       ▼              ▼
   Save value    Show error:
   in alerts     "❌ Invalid number.
                 Send a valid [type]:"
       │              │
       │          Wait for
       │          new input
       └──────┬──────┘
              │
       Continue with
       confirmation

Example error paths:
- User sends "abc" for MC → "Invalid number. Send valid market cap:"
- User sends "xyz" for % → "Invalid number. Send valid percentage:"
- User sends "text" for X → "Invalid number. Send valid X multiple:"
- User sends "invalid_ca" → "Invalid token. Send CA again."
```

---

## Alert Type Selection Matrix

```
                   Useful For:
Type             Buyers    Traders   Holders
────────────────────────────────────────────
📉 MC Level      ✅        ✅        ✅
                 Catch      Range     Support
                 dumps      trade     breaks
                 
📈 % Moves       ✅        ✅✅       ✅
                 Volatility Scalping  Big moves
                 
🚀 X Multiple    ✅        ✅        ✅✅
                 Verify     Partial   Profit
                 growth     profit    targets
                 
🔥 ATH Reclaim   ✅        ✅        ✅✅
                 Recovery   Pattern   Rebound
                 plays      trading   plays


Recommended combinations:
─────────────────────────
For conservative users:
  • MC level + ATH Reclaim

For aggressive traders:
  • All 4 alerts

For new coins:
  • % Moves + X Multiple
  (Watch behavior first)

For established coins:
  • MC Level + ATH Reclaim
  (Support/resistance levels)
```

---

## Message Template Structure

### All prompts follow this pattern:

```
[EMOJI] [Alert Type Name]
━━━━━━━━━━━━━━━━━━━━━━━━
[Context about what it does]
[Optional: Current value or explanation]

[Action instruction] (e.g., [example_value])
```

### All confirmations follow this pattern:

```
✅ [EMOJI] [Alert Type] Set
━━━━━━━━━━━━━━━━━━━━━━━━
Threshold: [formatted_value]

Active alerts:
[list of all alerts]

[Next step instruction]
```

---

## Error Recovery Flow

```
User makes error:
- Invalid number format
- Token not found
- API failure

              ▼
Bot shows friendly error:
"❌ [Clear message]"

              ▼
User sees example:
"(e.g., 50000)"

              ▼
User resends valid value

              ▼
Process continues normally
```

**Key principle:** All errors are 100% recoverable.
Users just resend the value, no restart needed.

---

## Mobile UI Considerations

```
┌─────────────────────────────────────┐
│          Telegram Mobile UI         │
├─────────────────────────────────────┤
│                                     │
│  ✅ 🪙 Token Detected              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━        │
│  💰 Market Cap: $82,300            │
│  💧 Liquidity: $120k               │
│                                     │
│  What do you want to track?        │
│  (Select multiple)                  │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  📉 Market Cap Levels       │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │  📈 % Moves                 │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │  🚀 X Multiples             │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │  🔥 ATH Reclaim             │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │  ✅ Done                    │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘

Design notes:
• Buttons at least 50px tall = easy tapping
• One button per line = no confusion
• Emojis provide visual scanning
• Text color consistent
• Keyboard hidden when viewing buttons
```

---

## Comparison: Old vs New Flow

### OLD FLOW (3 screens)
```
Screen 1:
Bot: "Send token address:"

Screen 2:
Bot: "🪙 Token detected
      Start MC: $82,300
      How do you want to be alerted?"

Screen 3:
Bot: "✅ Alert added
      Active alerts: MC, %"
```

**Problem:** Generic, no context, unclear what to send

---

### NEW FLOW (4 screens, better UX)
```
Screen 1:
Bot: "Send token address:"

Screen 2:
Bot: "✅ 🪙 Token Detected
      💰 Market Cap: $82,300
      💧 Liquidity: $120,000
      
      What do you want to track?
      (Select multiple)"

Screen 3a (one of several):
Bot: "📉 Market Cap Level
      Send market cap (e.g., 50000)"

Screen 3b:
User sends: 50000

Screen 4a:
Bot: "✅ 📉 Market Cap Alert Set
      Threshold: $50,000
      
      Active alerts:
      • MC ≤ $50,000
      
      Add more or tap Done"

Screen 4b (optional):
Bot: "✅ Coin added
      Active alerts: [all]"
```

**Improvement:** Context, clarity, flexibility, professional

---

## Summary

The Track Coin UX now follows a **5-step smart flow**:

1. **Input** - User sends CA
2. **Detect** - System fetches data
3. **Show** - Display token info
4. **Select** - User chooses alerts
5. **Confirm** - System saves

Each step is **clear**, **guided**, and **error-resilient**.

Users go from uncertainty to confidence in one smooth flow.

🎯 **Result:** Professional, modern, user-friendly coin tracking experience
