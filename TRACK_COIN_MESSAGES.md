# Track Coin UX - Message Reference

## Exact Message Templates

### Step 1: Initial Prompt
```
Send token contract address:
```
Simple and direct.

---

### Step 2: Token Detection (NEW)
```
✅ 🪙 Token Detected
━━━━━━━━━━━━━━━━━━━━━━━━
💰 Market Cap: $82,300
💧 Liquidity: $120,000

What do you want to track?
(Select multiple)
```

**Format rules:**
- ✅ emoji + 🪙 emoji at start
- ASCII divider (━ × 24)
- 💰 with formatted market cap
- 💧 with formatted liquidity
- Blank line
- Question with helpful note

---

### Step 3: Alert Type Prompts

#### Market Cap Level Alert
```
📉 Market Cap Level
━━━━━━━━━━━━━━━━━━━━━━━━
Current: $82,300

Send the market cap to alert at (e.g., 50000)
```

#### % Movement Alert
```
📈 % Movement Alert
━━━━━━━━━━━━━━━━━━━━━━━━
Alert when price moves ±X%

Send percentage (e.g., 30 for ±30%)
```

#### X Multiple Alert
```
🚀 X Multiple Alert
━━━━━━━━━━━━━━━━━━━━━━━━
Alert when you reach X multiplier X

Send X value (e.g., 2 for 2x, 5 for 5x)
```

#### ATH Reclaim Alert
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

### Step 4: Threshold Confirmations

#### Market Cap Confirmed
```
✅ 📉 Market Cap Alert Set
━━━━━━━━━━━━━━━━━━━━━━━━
Threshold: $50,000

Active alerts:
• MC ≤ $50,000

Add more alerts or tap Done
```

#### % Movement Confirmed
```
✅ 📈 % Move Alert Set
━━━━━━━━━━━━━━━━━━━━━━━━
Threshold: ±30.0%

Active alerts:
• MC ≤ $50,000
• % ±30%

Add more alerts or tap Done
```

#### X Multiple Confirmed
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

### Step 5: Final Confirmation

#### First-Time User (With Tips)
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

#### Returning User (Simple)
```
✅ Coin added successfully

Active alerts:
• MC ≤ $50,000
• % ±30%
• X ≥ 3.0x
• ATH reclaim (95%)
```

---

## Error Messages

### Invalid Token
```
❌ Invalid token. Send CA again.
```

### Invalid Number
```
❌ Invalid number. Send a valid market cap:
```

```
❌ Invalid number. Send a valid percentage:
```

```
❌ Invalid number. Send a valid X multiple:
```

---

## Button Labels

### Main Alert Selection
```
[📉 Market Cap Levels]
[📈 % Moves]
[🚀 X Multiples]
[🔥 ATH Reclaim]
[✅ Done]
```

---

## Formatting Rules

### Currency Values
- Format: `$` + number with commas
- Examples:
  - `$50,000`
  - `$1,245,000`
  - `$82,300`
  - `$120,000`

### Percentages
- Format: `±X.X%`
- Examples:
  - `±30.0%`
  - `±25.5%`
  - `±50.0%`

### X Multiples
- Format: `X.Xx`
- Examples:
  - `2.0x`
  - `3.5x`
  - `10.0x`

### Alert Display
- Format: `• [Type] [Operator] [Value]`
- Examples:
  - `• MC ≤ $50,000`
  - `• % ±30%`
  - `• X ≥ 3.0x`
  - `• ATH reclaim (95%)`

---

## ASCII Art

### Divider
```
━━━━━━━━━━━━━━━━━━━━━━━━
```
(24 characters total)

### Checkmark
```
✅
```

---

## Emoji Legend

| Emoji | Meaning |
|-------|---------|
| ✅ | Success/Confirmation |
| 🪙 | Token |
| 💰 | Market Cap (Money) |
| 💧 | Liquidity (Fluid) |
| 📉 | Market Cap Level (Down chart) |
| 📈 | % Movement (Up chart) |
| 🚀 | X Multiple (Rocket/Growth) |
| 🔥 | ATH Reclaim (Hot/Peak) |
| ❌ | Error |
| 👋 | Tips (Wave/Hello) |

---

## Message Structure Pattern

All messages follow this structure:

```
[EMOJI(s)] [HEADER]
[ASCII DIVIDER]
[Content Line 1]
[Content Line 2]
...
[Blank Line]
[Action or Next Step]
```

Example:
```
✅ 📉 Market Cap Alert Set
━━━━━━━━━━━━━━━━━━━━━━━━
Threshold: $50,000

Active alerts:
• MC ≤ $50,000

Add more alerts or tap Done
```

---

## Copy-Paste Reference

For developers implementing similar features:

### Basic confirmation pattern:
```python
await message.reply_text(
    f"✅ [EMOJI] [Type] Set\n"
    f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
    f"Threshold: [formatted_value]\n\n"
    f"Active alerts:\n"
    f"{alerts_display}\n\n"
    f"Add more alerts or tap Done"
)
```

### Token detection pattern:
```python
await message.reply_text(
    f"✅ 🪙 Token Detected\n"
    f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
    f"💰 Market Cap: {formatted_mc}\n"
    f"💧 Liquidity: {formatted_liquidity}\n\n"
    f"What do you want to track?\n"
    f"(Select multiple)",
    reply_markup=InlineKeyboardMarkup(keyboard)
)
```

### Prompt pattern:
```python
await message.reply_text(
    f"[EMOJI] [Alert Type]\n"
    f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
    f"[Context about current or explanation]\n\n"
    f"[Action statement] (e.g., [example])"
)
```

---

## Number Formatting Examples

### Market Cap
- Input: `50000` → Display: `$50,000`
- Input: `1245000` → Display: `$1,245,000`
- Input: `82.50` → Display: `$82.50`

### Percentage
- Input: `30` → Display: `±30.0%`
- Input: `25.5` → Display: `±25.5%`

### X Multiple
- Input: `2` → Display: `2.0x`
- Input: `3.5` → Display: `3.5x`

---

## Testing Messages

Test each message type:

1. ✅ Token detection with formatted MC/liquidity
2. ✅ MC alert prompt with current value
3. ✅ % alert prompt with ± notation
4. ✅ X alert prompt with explanation
5. ✅ Reclaim alert auto-confirmation
6. ✅ Confirmation with formatted threshold
7. ✅ Alert list with proper bullets
8. ✅ First-time user tips
9. ✅ Error message with recovery
10. ✅ Final save confirmation

---

## Localization Notes

If translating to other languages:
- Emojis remain universal ✅
- ASCII dividers remain consistent ━
- Number formatting rules adapt to locale
- Examples should match local currency conventions

---

## Accessibility Notes

- Large emojis (easy to scan)
- Bold headers (important info)
- Clear hierarchy (structure)
- High contrast (light background)
- Simple language (easy to understand)

---

## Summary

The Track Coin UX uses:
- **Consistent emoji scheme** for visual scanning
- **ASCII dividers** for professional appearance
- **Formatted numbers** for clarity
- **Context-aware prompts** with examples
- **Confirmation pattern** showing exactly what was set
- **Multi-step guidance** without overwhelming

Result: **Professional, clear, modern UX** that guides users to success.
