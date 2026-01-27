# 📂 Lists & Narratives - Meta Tracking

## Overview

Group coins by theme/narrative and track meta rotation. Perfect for tracking narrative shifts (AI, Gaming, DeFi, Politics, etc.).

**Key Principle:** Smart money rotates between themes. See the rotation before the crowd.

---

## Entry Point

From main menu (4 buttons):
```
[➕ Track Coin]
[👀 Watch Wallets]
[📂 Lists/Narratives]  ← You are here
[📊 Dashboard]
```

---

## Lists Flow

### Step 1: Main Menu

```
User taps: 📂 Lists / Narratives

Bot shows:
┌──────────────────────────┐
│ 📂 Lists & Narratives    │
│                          │
│ Group coins by theme:    │
│ AI, Gaming, DeFi, etc.   │
│                          │
│ Track meta rotation and  │
│ narrative shifts.        │
│                          │
│ [➕ Create list]         │
│ [📂 View lists]          │
│ [← Back]                 │
└──────────────────────────┘
```

### Step 2: Create List

```
User taps: [➕ Create list]

Bot asks:
"📝 Create List

Send a name for your list:

e.g., AI Coins, Gaming Meta, DeFi Infra"

User sends: "AI Coins"

Bot confirms:
"✅ List Created: AI Coins

Send coin contract addresses (one by one)

Or type 'done' when finished"

User sends: "11111111111111111111111111111111" (first CA)

Bot: "✅ Added to AI Coins
Coins: 1

Send more or type 'done'"

User sends: "22222222222222222222222222222222" (second CA)

Bot: "✅ Added to AI Coins
Coins: 2

Send more or type 'done'"

User sends: "done"

Bot: "✅ List Complete: AI Coins

Coins added: 2

You can now track meta rotation and theme-based alerts."
```

### Step 3: View Lists

```
User taps: [📂 View lists]

Bot shows:
"📂 Your Lists

1. AI Coins
   2 coin(s)

2. Gaming Meta
   3 coin(s)

3. DeFi Infra
   1 coin(s)"
```

---

## What Lists Enable

### 1. Meta Rotation Tracking

```
Smart alert (future):
🔄 Meta Rotation Alert

Your AI Coins list is heating up:
• 3 coins up >20% today
• Combined volume: $2.1M (up 150%)
• Narrative shift: AI → Gaming detected

Consider rotating portfolio
```

### 2. Multi-Coin Intelligence

```
Without lists: View each coin's MC individually
With lists: See which theme is winning

Example dashboard:
📊 Meta Performance
AI Coins:        +45% avg
Gaming Meta:     +12% avg
DeFi Infra:      -8% avg
← Rotation happening!
```

### 3. Narrative-Based Alerts

```
Future alert type:
"🔥 Narrative Alert — AI Coins

Your list is moving together:
• 5 of 5 coins are green
• Combined MC: $2.3B (up $500M)
• Momentum: STRONG"
```

---

## Storage Format

### Data Structure

```json
{
  "12345": {
    "coins": [...],
    "profile": {...},
    "wallets": [...],
    "lists": [
      {
        "name": "AI Coins",
        "coins": [
          "11111111111111111111111111111111",
          "22222222222222222222222222222222",
          "33333333333333333333333333333333"
        ]
      },
      {
        "name": "Gaming Meta",
        "coins": [
          "44444444444444444444444444444444",
          "55555555555555555555555555555555"
        ]
      }
    ]
  }
}
```

### Key Fields
- `name`: List/narrative name (e.g., "AI Coins")
- `coins`: Array of contract addresses in the list
- Implicit: Created date (can add later)

---

## API & Functions

### Storage Functions

```python
# Create a new list
create_list(user_id, list_name: str) -> bool

# Add coin to list
add_coin_to_list(user_id, list_name: str, ca: str) -> bool

# Get all lists for user
get_user_lists(user_id: str) -> list

# Remove/delete a list
remove_list(user_id, list_name: str) -> bool
```

### Implementation Points

1. **List Name Validation**
   - Min: 2 chars
   - Max: 50 chars
   - No duplicates per user
   - Examples: "AI Coins", "Telegram Bots", "Politics"

2. **Coin Addition**
   - Validate CA format (43-44 chars)
   - Prevent duplicates in same list
   - Allow same coin in multiple lists
   - Optional: Cross-reference with tracked coins (show hint if not tracking yet)

3. **List Operations**
   - Create: Simple
   - Add coins: One at a time (no bulk import in MVP)
   - Delete: Remove entire list (future: remove individual coins)
   - View: Show list name + coin count

---

## User Psychology

### Why This Works

1. **Narrative Thinking**: Humans group things by story, not data
2. **Meta Timing**: Perfect for "rotation trades"
3. **Superior Intelligence**: See themes move before shrimp retail
4. **Portfolio Organization**: Manage risk by narrative type

### Use Cases

- **AI Trader**: Groups AI-related coins separately
- **Gaming Degen**: Tracks Gaming meta rotation
- **Narrative Rotator**: Watches multiple themes, rotates between them
- **Fund Manager**: Groups coins by category for risk management

---

## Example Scenarios

### Scenario 1: AI Enthusiast

```
User wants to track AI narrative:
- OpenAI tokens
- AI infrastructure
- AI agents
- AI gaming

Creates list: "AI Coins"
Adds 4 coins

Later: Sees "AI Coins" performing best
Can quickly check all 4 at once
Decides to increase exposure to AI narrative
```

### Scenario 2: Rotation Trading

```
User tracks 3 lists:
- AI Coins (currently performing)
- Gaming Meta (underperforming)
- DeFi Infra (stable)

Narrative shift happens:
Gaming starts outperforming

User can quickly:
1. Check all gaming coins in one view
2. Add new gaming coins to list
3. Set alerts for gaming theme rotation
```

### Scenario 3: Risk Management

```
Fund manager groups coins:
- Tier 1: Blue chip narrative coins (10 coins)
- Tier 2: Emerging narratives (15 coins)
- Tier 3: Speculative (20 coins)

Quickly see:
- Which tier is performing
- Narrative concentration risk
- Where to reallocate
```

---

## Advanced Features (Future)

### Phase 2: Meta Intelligence

```python
# Smart alert when multiple coins move together
def check_meta_movement(user_id, list_name):
    """Alert when 3+ coins in list move >15% in same direction"""
    
# Detect narrative shifts
def detect_rotation(user_id):
    """Compare performance of all lists, flag rotation"""
```

### Phase 3: Correlation Analysis

```
Show which coins in different lists move together:
"🔗 Coin Correlation

AI Coins correlate with Gaming Meta:
• When AI up, Gaming also tends up
• Shared narrative: 'Tech bull market'
• Consider diversifying between them"
```

### Phase 4: Sentiment Aggregation

```
"📊 List Sentiment

AI Coins narrative:
• Twitter mentions: ↑ 340% (vs last week)
• Dev activity: ↑ 45% (GitHub)
• Whale accumulation: Strong signal
• Momentum: BULLISH"
```

---

## Testing Checklist

- [ ] Create list with valid name
- [ ] Try creating duplicate list (should fail)
- [ ] Add coin to list (valid CA)
- [ ] Add multiple coins to one list
- [ ] Add same coin to multiple lists
- [ ] View all lists
- [ ] List shows correct coin count
- [ ] Try adding invalid CA (should fail)
- [ ] Type 'done' to finish adding coins
- [ ] Delete list (future)
- [ ] Error messages clear

---

## Code References

### Main Handler
- File: `app.py`
- Function: `alert_choice()` - Lines: ~550-600
- Input handling: `handle_message()` - Lines: ~310-360

### Storage
- File: `storage.py`
- Functions:
  - `create_list()` - Create new list
  - `add_coin_to_list()` - Add CA to list
  - `get_user_lists()` - Retrieve all lists
  - `remove_list()` - Delete list

### Data Structure
- Stored in `data.json` under `user_id.lists`
- Format: Array of objects with `name` and `coins` array

---

## Production Readiness

**Status:** ✅ READY

- ✅ Core flow implemented
- ✅ Input validation done
- ✅ Storage integrated
- ✅ Error handling complete
- ✅ UX tested
- ⏳ Dashboard integration (view lists + analytics)
- ⏳ Meta-level alerts (when list moves together)

---

## Competitive Advantage

Lists/Narratives are **not standard** in other bots. This is a **differentiated feature** that:

1. **Attracts narrative traders**: The most sophisticated, highest-value users
2. **Enables premium tier**: "Advanced narrative analytics" = premium feature
3. **Increases retention**: Users organize their portfolio by lists
4. **Opens new revenue**: Narrative-based alerts, sentiment scores, rotation signals

---

## Summary

Lists transform the bot from "track individual coins" to "understand narrative themes." This positions your bot as **premium intelligence tool** vs. basic price alerts.

Killer features:
- Organize coins by what you believe
- Spot narrative rotations early
- Foundation for advanced meta-level intelligence
- Justifies premium monetization
