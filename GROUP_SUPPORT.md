# 🎯 Group Support - Community Alerts

## Overview

Bot works in groups, but with **read-only by default** + **admin-only configuration**.

Group alerts are brief, actionable, and no-nonsense.

**Key Principle:** Groups need brevity. No essays. Just signal.

---

## How Groups Work

### Access Rules

✅ **Any user can:**
- View group coins (`/status`)
- View active alerts (`/alerts`)
- Read incoming alerts

❌ **Only admins can:**
- Add coins to group (`/track`)
- Configure group alerts (future)
- Remove coins (future)

❌ **Not allowed in groups:**
- Wallet tracking (too noisy for group)
- Personal alerts (private feature)
- Dashboard (use `/status` instead)

---

## Group Commands

### /track <CA>

**Purpose:** Add a coin for the group to monitor

**Requirements:**
- User must be group admin
- Valid contract address
- Coin not already tracked

**Flow:**
```
Admin sends: /track 11111111111111111111111111111111

Bot checks: Is user admin? ✓
Bot fetches: Token data
Bot stores: Coin in group tracking

Bot responds:
"✅ Coin added to group

CA: 11111111111111111111111111111111
MC: $82,300

Alert at 30% drop"
```

**Error Cases:**
```
Non-admin sends: /track ...
Bot: "❌ Only admins can add coins in groups."

Invalid CA: /track invalid123
Bot: "❌ Invalid token address."

Duplicate: /track 11111... (already tracked)
Bot: "Coin already in group tracking."
```

### /status

**Purpose:** Show all coins tracked in the group

**Available to:** All group members

**Flow:**
```
Any user sends: /status

Bot shows:
"📊 Group Tracked Coins (3)

🪙 11111...
💰 $82,300
📈 1.05x | 📉 2.3% DD

🪙 22222...
💰 $156,200
📈 2.10x | 📉 15.8% DD

🪙 33333...
💰 $2.1M
📈 0.95x | 📉 5.0% DD"
```

**Key Info:**
- Short CA (first 6 chars)
- Current market cap
- Current multiple (X)
- Current drawdown (%)

### /alerts

**Purpose:** Show all active alerts for the group

**Available to:** All group members

**Flow:**
```
Any user sends: /alerts

Bot shows:
"🔔 Active Alerts

• 11111... MC ≤ $57,610
• 22222... MC ≤ $109,340
• 33333... MC ≤ $1.47M"
```

**Info:**
- Coin identifier (short)
- Alert type + threshold
- Clean, scannable format

---

## Group Alert Format

### When Alerts Trigger

```
🚨 Group Alert — BONK

MC hit $50k
Wallet: Smart Money
Buy: $4,100
```

**vs Private Alert:**
```
📊 Smart Alert — BONK

Market cap down 30%
Current: $50,200
Range: Low ═════════ High

Quality Score: 85/100
Pattern: Stabilizing after dump
```

### Design Rules

✅ **Group alerts should be:**
- 2-3 lines maximum
- One action item
- Clear numbers
- No fluff

❌ **Never in groups:**
- Multi-paragraph explanations
- Historical context
- Sentiment analysis
- Technical analysis

### Example Alerts

#### Market Cap Break

```
🚨 Group Alert — SHIB

MC ≤ $100k (alert triggered)
```

#### Wallet Buy

```
👀 Whale Buy — BONK

Wallet bought $8,500 BONK
(Wallet: Smart Money)
```

#### Mass Movement

```
🔥 List Movement — DeFi Coins

3 of 5 DeFi coins up >15% today
```

---

## Storage Format

### Group Data Structure

```json
{
  "group_-123456789": {
    "is_group": true,
    "coins": [
      {
        "ca": "11111111111111111111111111111111",
        "start_mc": 82300,
        "ath_mc": 82300,
        "low_mc": 82300,
        "alerts": {
          "mc": 57610  // 30% drop alert
        },
        "triggered": {
          "mc": false
        }
      }
    ]
  }
}
```

### Key Differences from Private

- Key: `group_<chat_id>` (vs just user_id)
- Flag: `"is_group": true`
- No wallets, lists, or profiles
- Minimal alert config (just MC level)

---

## Admin Verification

### How Bot Checks Admin Status

```python
# Get group member info
member = await bot.get_chat_member(chat_id, user_id)

# Check status
if member.status in ["creator", "administrator"]:
    # Allow admin actions
else:
    # Deny, show error
```

### Admin Roles

✅ **Creator:** Full permissions
✅ **Administrator:** Full permissions
❌ **Member:** Read-only

---

## User Psychology in Groups

### Why Groups Matter

1. **Community Validation**: "My group is watching this"
2. **Social Proof**: "Multiple people tracking this"
3. **Accountability**: Public alerts = people pay attention
4. **FOMO Reducer**: Group sees alert first = don't FOMO alone

### Perfect Use Cases

- **DAO Communities**: Track DAO-related coins
- **Trader Groups**: Coordinate on coins to watch
- **Discord Communities**: Send alerts to main channel
- **Project Communities**: Watch competitive/related projects

---

## Workflow Examples

### Example 1: New Group Setup

```
Admin creates group: "AI Coins Community"

Day 1 - Setup:
Admin: /track <GPTI>
Bot: ✅ GPTI added
Admin: /track <OPEN>
Bot: ✅ OPEN added
Admin: /track <GOAT>
Bot: ✅ GOAT added

Day 2 - Monitoring:
Member: /status
Bot: Shows all 3 coins + current price

Member: /alerts
Bot: Shows MC alert levels

GPTI MC hits $50k alert:
Bot (in group): "🚨 Group Alert — GPTI - MC ≤ $50k"
All members: See alert instantly
Members: Can discuss in thread
```

### Example 2: Trader Group

```
Trader group: "Degen Stackers"
Members: 15 traders

Setup:
Admin adds 5 coins group wants to track
Admin configures: 20% drop alert on each

Activity:
Coin #2 drops 20%
Bot: 🚨 Group Alert — COIN2 - 20% drop
Members: React in group, discuss strategy
Someone: "This is accumulation, buying more"
Others: Follow analysis
```

### Example 3: DAO Community

```
DAO group: "Solana Ecosystem"
Members: 200+ community members

Setup:
DAO team adds ecosystem coins:
- Related projects
- Competitors
- Infrastructure plays

Daily usage:
Members: Check /status for ecosystem health
Members: Get alerted on major price moves
DAO team: Monitor which coins community cares about
Community: Feels connected to broader ecosystem
```

---

## Technical Implementation

### Group Identification

```python
# In handlers, check chat type
if update.message.chat.type == "private":
    # Private chat - use full feature set
elif update.message.chat.type in ["group", "supergroup"]:
    # Group chat - use limited feature set
```

### Storing Group Data

```python
# Group key = "group_" + chat_id
chat_id = update.message.chat_id
group_key = f"group_{chat_id}"

# Add coin to group
data[group_key] = {
    "is_group": True,
    "coins": [...]
}
```

### Sending Group Alerts

```python
# Alert to all group members
await bot.send_message(
    chat_id=chat_id,
    text=alert_message,
    parse_mode="HTML"
)
```

### Admin Check

```python
member = await context.bot.get_chat_member(chat_id, user_id)
is_admin = member.status in ["creator", "administrator"]
```

---

## Testing Checklist

- [ ] Bot can be added to group
- [ ] Admin can add coin (`/track`)
- [ ] Non-admin cannot add coin (shows error)
- [ ] `/status` shows all group coins
- [ ] `/status` shows correct MC and X values
- [ ] `/alerts` shows all configured alerts
- [ ] Group receives alert when MC drops 30%
- [ ] Alert format is brief and scannable
- [ ] Multiple groups tracked independently
- [ ] Private and group features don't interfere
- [ ] Admin verification works correctly

---

## Code References

### Group Command Handlers
- File: `app.py`
- Functions:
  - `group_track()` - Add coin (admin only)
  - `group_status()` - Show coins
  - `group_alerts()` - Show alerts

### Group Data Check
```python
# In handle_message, identify group
if update.message.chat.type in ["group", "supergroup"]:
    # Handle as group
```

### Handler Registration
```python
# In main()
app.add_handler(CommandHandler("track", group_track))
app.add_handler(CommandHandler("status", group_status))
app.add_handler(CommandHandler("alerts", group_alerts))
```

---

## Production Readiness

**Status:** ✅ READY FOR GROUPS

- ✅ Admin verification implemented
- ✅ Group storage separate from private
- ✅ Commands functional
- ✅ Alert delivery working
- ✅ Error handling complete
- ✅ No feature pollution (wallets/lists not in groups)

---

## Monetization Opportunities

### Private: Premium Features
- Unlimited wallets
- Advanced lists analytics
- Custom alert thresholds
- Portfolio risk scoring

### Groups: Freemium Model
- Free: Basic /track, /status, /alerts
- Premium (group): "Pro group" with custom alerts, webhooks, API

### Cross-Sell

User: "Our trading group wants premium alerts"
Product: "Pro Group tier" ($10-50/month)
Perfect upsell opportunity

---

## Future Enhancements

### Phase 2: Group Settings

```python
# Admin can configure per group
group_settings = {
    "alert_threshold_mc": 0.30,  # 30% drop
    "alert_threshold_x": 2.0,    # 2x
    "min_buy_size": 100,         # $100
    "quiet_hours": "22:00-08:00" # No alerts at night
}
```

### Phase 3: Group Dashboard

```
Web dashboard showing:
- Group performance across all coins
- Historical prices
- Member activity
- Most traded coins
```

### Phase 4: Webhooks

```
Group admins can:
- Send alerts to Discord
- Send alerts to Telegram channel
- POST to custom webhook URL
- Trigger automated actions
```

---

## Summary

Group support makes the bot **social and community-driven**. Groups are where:
- Real traders organize
- Communities form
- Monetization happens
- Word-of-mouth spreads

By keeping group features **simple and powerful**, the bot becomes the de-facto alert tool for every crypto trading community.

Core principle: **Groups = signal. No noise. No fluff. Just action.**
