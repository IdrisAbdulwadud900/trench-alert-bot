# 4-Button UI Redesign

## Overview
The Trench Alert Bot now features a clean, button-driven interface with just 4 main actions, replacing the complex command-based system. This makes the bot more intuitive for new users while maintaining full functionality.

## Main Menu (When you tap /start)

```
🚨 Trench Alert Bot

Choose what you want to do:

[➕ Track Coin]
[👀 Watch Wallets]
[📂 Lists / Narratives]
[📊 Dashboard]
```

## The 4 Main Actions

### 1. ➕ Track Coin
**Purpose:** Add a new coin to monitor

**Flow:**
- Tap button
- Send token contract address
- Select alert types (MC, %, X, Reclaim)
- Set thresholds for each alert
- Coin added and monitoring begins

**Behind the scenes:** Routes to the `/add` flow
**Status:** ✅ Fully functional
**Features:**
- Smart alert setup with inline buttons
- Alert threshold validation
- First-time user tips on first coin add
- Integration with intelligence layer (ATH tracking, range position, quality scoring)

---

### 2. 👀 Watch Wallets
**Purpose:** Monitor specific wallet addresses

**Current Status:** 🔜 Coming Soon feature
**Placeholder message:** 
```
👀 Wallet Tracking

Track specific wallet addresses for smart money activity.

Coming soon: Monitor whale wallets, insider trades, and LP movements.
```

**Future Implementation:**
- Add wallet address
- Get alerts on transfers from tracked wallets
- Track LP additions/removals
- Monitor insider/team wallet movements
- Whale activity tracking

---

### 3. 📂 Lists / Narratives
**Purpose:** View your tracked coins and narratives

**Flow:**
- Shows all coins you're monitoring
- Displays range position (ATH%, Cold, etc.) for each
- Shows active alerts
- Provides management options

**Current functionality:**
```
📂 Your Tracked Coins:

1. abc123...
   Range: ATH%
   Alerts: MC, %

2. def456...
   Range: Cold
   Alerts: X
```

**Status:** ✅ Working
**Features:**
- Range position for context
- Active alert summary
- Organized coin list

---

### 4. 📊 Dashboard
**Purpose:** Live monitoring of all tracked coins

**Flow:**
- Shows real-time data for each coin
- Market cap in USD
- Drawdown percentage from start
- X multiple (current price / start price)
- Range position
- Updates on-demand when tapped

**Current display:**
```
📊 Dashboard

🪙 abc123...
━━━━━━━━━━━━━━━━━━
💰 $1,245,000
📈 2.50x | 📉 -15.2%
📊 ATH%

🪙 def456...
━━━━━━━━━━━━━━━━━━
💰 $892,000
📈 1.80x | 📉 -8.5%
📊 Cold
```

**Status:** ✅ Working
**Features:**
- Real-time market cap fetching
- Percentage change calculation
- Range position showing
- Multi-coin support

---

## Secondary Commands (Still Available)

While the main UI is button-driven, these commands still work if users prefer typing:

| Command | What it does |
|---------|------------|
| `/start` | Show the 4-button main menu |
| `/add` | Directly start adding a coin (skips main menu) |
| `/list` | Show all monitored coins |
| `/status` | Show live dashboard data |
| `/mode` | Choose alert profile (Conservative/Aggressive/Sniper) |
| `/remove` | Stop monitoring a coin |
| `/help` | Show command reference |

---

## Alert Profiles

After adding a coin, users can set their alert profile using `/mode`:

```
Choose your alert profile:

[🐢 Conservative] - Only high-quality signals
[⚡ Aggressive] - Balanced (default)
[🧠 Sniper] - All signals, may be noisy
```

**What each does:**
- **Conservative:** Only triggers alerts when quality score is 3 (most reliable)
- **Aggressive:** Triggers on quality score 2+ (default, balanced)
- **Sniper:** Triggers on any signal (quality score 1+, may be noisy)

---

## First-Time User Experience

When users add their **first coin**, they get special tips:

```
✅ Coin added successfully

Active alerts:
MC, %, Reclaim

👋 First coin tips:
• Use Dashboard to monitor
• Smart alerts trigger when conditions align
• Use /mode to choose your alert profile
• Add more coins with ➕ Track Coin
```

---

## Intelligent Features Integrated

All 4 buttons use the intelligence layer:

1. **ATH/Range Tracking** - Displays range position (ATH%, Recovering, Cold, etc.)
2. **Quality Scoring** - Filters low-quality signals (0-3 scale)
3. **Pattern Detection** - Alerts on dump→stabilize→bounce patterns
4. **User Profiles** - Respects chosen alert profile (Conservative/Aggressive/Sniper)

---

## Button Interaction Map

```
/start
  ↓
[4 Inline Keyboard Buttons]
  ├─→ ➕ Track Coin → callback_data: "action_track"
  │   ↓
  │   Send token address → Full add flow
  │
  ├─→ 👀 Watch Wallets → callback_data: "action_wallets"
  │   ↓
  │   "Coming soon" message
  │
  ├─→ 📂 Lists / Narratives → callback_data: "action_lists"
  │   ↓
  │   Display all coins with range positions
  │
  └─→ 📊 Dashboard → callback_data: "action_dashboard"
      ↓
      Fetch and display live data for all coins
```

---

## Code Implementation

### In `app.py`:

**Modified `/start` command:**
```python
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Track Coin", callback_data="action_track")],
        [InlineKeyboardButton("👀 Watch Wallets", callback_data="action_wallets")],
        [InlineKeyboardButton("📂 Lists / Narratives", callback_data="action_lists")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="action_dashboard")]
    ]
    
    await update.message.reply_text(
        "🚨 Trench Alert Bot\n\n"
        "Choose what you want to do:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
```

**Enhanced `alert_choice()` handler:**
- Routes `action_track` → Initialize add flow
- Routes `action_wallets` → Show placeholder message
- Routes `action_lists` → Query and display coins
- Routes `action_dashboard` → Fetch and display live data
- Maintains existing alert setup flow (MC, %, X, Reclaim, Done)

---

## User Journey Examples

### New User
1. Tap /start → sees 4 buttons
2. Taps ➕ Track Coin → sends contract address
3. Sets up alerts (MC, %, Reclaim)
4. Sees first-time tips
5. Gets alerts on tracking page or returns to main menu

### Regular Monitoring
1. Tap /start → sees 4 buttons
2. Taps 📊 Dashboard → sees live data
3. Taps ➕ Track Coin → adds another coin
4. Taps 📂 Lists → reviews portfolio

### Profile Customization
1. Type `/mode` (secondary command)
2. Choose profile (Conservative/Aggressive/Sniper)
3. Future alerts now use that profile

---

## Future Features

The 4-button UI is designed to scale:

- **Watch Wallets:** Will track whale/insider activity
- **Lists/Narratives:** Will support custom tags and narratives
- **Dashboard:** Will support pagination for 50+ coins, advanced filtering
- **Settings:** Could add 5th button for preferences if needed

---

## Status Check

✅ **Implemented:**
- 4-button main menu UI
- Button callback routing
- Track Coin flow integration
- Dashboard display
- Lists/Narratives display
- Profile selection
- First-time tips

🔜 **Coming Soon:**
- Wallet tracking implementation
- Advanced dashboard (pagination, charts)
- Custom lists and narratives
- Settings/preferences panel

---

## Testing the New UI

To test locally:
```bash
export BOT_TOKEN=your_token
python3 app.py
```

Then in Telegram:
1. Send `/start` → should see 4 buttons
2. Tap ➕ Track Coin → should ask for contract address
3. Tap 📊 Dashboard → should show live data
4. Tap 📂 Lists → should show tracked coins
5. Tap 👀 Watch Wallets → should show coming soon message

All existing `/add`, `/list`, `/status`, `/mode` commands still work as fallbacks.
