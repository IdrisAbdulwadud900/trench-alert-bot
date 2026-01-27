# 🚀 How to Run Your Bot

## Quick Start (3 steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

Or with Python 3 explicitly:
```bash
pip3 install -r requirements.txt
```

### Step 2: Set Your Bot Token
Get your bot token from [@BotFather](https://t.me/botfather) on Telegram.

Then set it as an environment variable:

**On Mac/Linux:**
```bash
export BOT_TOKEN="your_bot_token_here"
export CHECK_INTERVAL="60"
```

**Verify it's set:**
```bash
echo $BOT_TOKEN
```

### Step 3: Run the Bot
```bash
python3 app.py
```

You should see:
```
🚀 Trench Alert Bot running...
📡 Monitor loop started in background thread
```

---

## Full Example (Step by Step)

```bash
# Navigate to bot folder
cd /Users/mac/Downloads/mc_alert_bot

# Install packages
pip3 install -r requirements.txt

# Set your token (replace with real token)
export BOT_TOKEN="123456789:ABCDefGHIjklMNOpqrstUVWxyz"
export CHECK_INTERVAL="60"

# Run the bot
python3 app.py
```

---

## Verify It's Working

Once running, in Telegram:
1. Send `/start` to your bot
2. You should get a welcome message
3. Try `/help` to see all commands

---

## Common Issues & Fixes

**"python3: command not found"**
- Try: `python --version`
- If that works, use `python` instead of `python3`

**"No module named 'telegram'"**
- Run: `pip3 install python-telegram-bot`

**"BOT_TOKEN is not set!"**
- Make sure you ran: `export BOT_TOKEN="your_token"`
- Verify with: `echo $BOT_TOKEN`

**"ModuleNotFoundError: No module named..."**
- Run: `pip3 install -r requirements.txt`

---

## Environment Variables Explained

| Variable | Value | Example |
|----------|-------|---------|
| `BOT_TOKEN` | Your Telegram bot token | `123456:ABC...` |
| `CHECK_INTERVAL` | Seconds between checks | `60` (1 minute) |

**To make them permanent** (auto-load on terminal start):

Add to `~/.zshrc` or `~/.bash_profile`:
```bash
export BOT_TOKEN="your_token"
export CHECK_INTERVAL="60"
```

Then restart terminal or run:
```bash
source ~/.zshrc
```

---

## Bot Features

### Private Chat Mode
- ➕ Track coins with custom alerts
- 👀 Watch wallets for buys
- 📂 Create lists/narratives
- 📊 View detailed dashboard
- Full control over all features

### Group Mode (NEW in Phase 5)
- 🚨 Shared coin tracking for groups
- 👥 Members can view status
- 👨‍💼 **Only admins can configure**
- Clean, non-noisy alerts
- Separate data from private chats

**To use in a group:**
1. Add bot to your Telegram group
2. Type `/start` in the group
3. Admins can tap "➕ Track Coin" button
4. All members can tap "📊 Status"

---

## Stopping the Bot

Press `Ctrl+C` in the terminal running the bot.

---

## Running in Background (Optional)

To keep bot running even if terminal closes:

```bash
nohup python3 app.py > bot.log 2>&1 &
```

Check logs:
```bash
tail -f bot.log
```

---

## For Production (Render/AWS/etc)

See **DEPLOYMENT_CHECKLIST.md** for cloud deployment steps.

---

**That's it! Your bot is ready to go.** 🚀
