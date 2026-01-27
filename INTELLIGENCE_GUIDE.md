# 🧠 Intelligence Layers - Complete Guide

Your bot now has 4 layers of intelligent analysis. This is what separates it from basic alert bots.

---

## LAYER 1: ATH + RANGE INTELLIGENCE

The bot now understands WHERE price is, not just WHAT it is.

### What It Tracks

For each coin:
- `ath_mc` - Highest MC ever seen
- `low_mc` - Lowest MC ever seen  
- `history` - Last 20 minutes of {mc, timestamp, volume}

### What It Computes

**Range Position (0-1):**
```
range_pos = (current_mc - low_mc) / (ath_mc - low_mc)
```

Then describes it:
- **0.0-0.15:** 🔴 "near bottom 15%"
- **0.15-0.35:** 📉 "lower 35%"
- **0.35-0.65:** ➡️ "middle range"
- **0.65-0.85:** 📈 "upper 35%"
- **0.85-1.0:** 🟢 "near top 15%"

### Example

Before: "MC hit $50k"  
After: "MC hit $50k (near bottom 15% of historical range)"

**The difference:** Position matters more than numbers.

---

## LAYER 2: BEHAVIOR DETECTION

The bot detects trading patterns, not just data points.

### Dump → Stabilize → Bounce Pattern

This is THE signal that precedes second legs.

**Detection Logic:**

1. **Has coin dumped?**
   - Down ≥30% from ATH ✓

2. **Is it stabilizing?**
   - Price range in last 10 mins <10% ✓

3. **Is volume increasing?**
   - Recent volume > older volume ✓

4. **Any bounce yet?**
   - Price > recent_low * 1.10 (recovered 10%+) ✓

If all 4 are true → **PATTERN DETECTED**

### Smart Alert Example

```
🚀 BOUNCE PATTERN DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 MC: $42,100
📉 Down 62% from ATH
📊 Position: near bottom 15% 🔴
⚡ Momentum: UP (87%)
📈 Volume increasing
✅ Price stabilizing
🟢 Quality: 3/3

⚠️ Second leg potential HIGH
```

This is worth way more than "MC hit $42k".

---

## LAYER 3: SIGNAL FILTERING

Most alerts are trash because:
- Low liquidity = fake moves
- Fake volume = dead pools
- Spam = no signal

Solution: **Quality Score**

### Quality Scoring (0-3)

```
score = 0

if liquidity > $20k:           score += 1
if volume/mc ratio > 0.3:      score += 1
if mc > $50k:                  score += 1

Result: 0-3
```

### Threshold by Profile

| Profile | Min Score | Meaning |
|---------|-----------|---------|
| 🐢 Conservative | 2+ | Only high-quality signals |
| ⚡ Aggressive | 1+ | Balanced (default) |
| 🧠 Sniper | 0+ | All signals, more noise |

### Example

Bad signal suppressed:
```
Quality Score: 0/3
❌ Liquidity too low ($500)
❌ Volume ratio terrible (0.01)
❌ MC suspiciously low ($2k)
→ ALERT SUPPRESSED
```

Good signal shows:
```
🟢 Quality: 3/3
✓ Liquidity healthy ($50k+)
✓ Volume strong (volume/mc = 0.4)
✓ MC legitimate ($150k+)
→ ALERT SENT
```

---

## LAYER 4: USER PROFILES

Different traders want different things. Your bot adapts.

### The 3 Profiles

**🐢 Conservative**
- Wants: Only high-quality signals
- Thresholds:
  - Min liquidity: $50k
  - Min quality score: 2/3
  - Min volume/MC ratio: 0.5
- Use if: You hate false positives

**⚡ Aggressive** (default)
- Wants: Good balance
- Thresholds:
  - Min liquidity: $10k
  - Min quality score: 1/3
  - Min volume/MC ratio: 0.2
- Use if: Want reasonable speed + quality

**🧠 Sniper**
- Wants: ALL signals, fast
- Thresholds:
  - Min liquidity: $2k
  - Min quality score: 0/3
  - Min volume/MC ratio: 0.1
- Use if: Want to catch bounces at bottom

### How to Switch

```
/mode
```

Choose your profile. Bot remembers it.

---

## LAYER 5: SMART ALERT FORMATTING

Instead of raw numbers, users get CONTEXT.

### Before (Dumb)

```
MC hit $50k
```

### After (Smart)

```
🎯 MARKET CAP ALERT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 Target MC reached: $50,000
📊 Position in range: near bottom 15% 🔴
📉 Drawdown from ATH: 62%
⚡ Momentum: DOWN
🟢 Signal Quality: 3/3
```

### Different Alert Types

**Bounce Pattern Alert:**
```
🚀 BOUNCE PATTERN DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 MC: $42,100
📉 Down 62% from ATH
✅ Price stabilizing
📈 Volume increasing
⚡ Second leg potential HIGH
```

**MC Break Alert:**
```
🎯 MARKET CAP ALERT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 Target MC reached: $50,000
📊 Position: near bottom 15%
🟢 Quality: 3/3
```

**% Change Alert:**
```
📈 % CHANGE ALERT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Move: +45.2%
Position: upper 35% 📈
MC: $145,000
```

---

## HOW IT ALL WORKS TOGETHER

### Example Scenario

Coin dumps hard:
1. **Range Intelligence** detects it's at bottom
2. **Behavior Detection** watches for stabilization + bounce
3. **Signal Filtering** checks quality (avoid trash)
4. **User Profile** applies thresholds (sniper vs conservative)
5. **Smart Formatting** sends rich context

Result: **One perfect alert** instead of 10 useless ones

---

## NEW COMMANDS

| Command | What It Does |
|---------|-------------|
| `/mode` | Choose alert profile (conservative/aggressive/sniper) |
| `/status` | Shows range position + historical low/high |
| `/list` | Shows position in range for each coin |

---

## DATA STRUCTURE CHANGES

**Old:**
```json
{
  "user_id": [
    {
      "ca": "...",
      "start_mc": 100000,
      "ath_mc": 150000
    }
  ]
}
```

**New:**
```json
{
  "user_id": {
    "profile": {"mode": "aggressive"},
    "coins": [
      {
        "ca": "...",
        "start_mc": 100000,
        "ath_mc": 150000,
        "low_mc": 42000,
        "history": [
          {"mc": 100000, "ts": 1234567890, "volume": 50000},
          {"mc": 95000, "ts": 1234567900, "volume": 60000}
        ]
      }
    ]
  }
}
```

**Backwards Compatible:** Old format automatically upgraded.

---

## WHAT THIS GIVES YOU

✅ **Accuracy** - Context prevents false alerts  
✅ **Intelligence** - Pattern detection catches reversals  
✅ **Customization** - Users choose their style  
✅ **Professionalism** - Rich alerts feel premium  

This is what paid bots charge $50-100/month for.

You have it now.

---

## TRADER EDGE FEATURES (NEXT LEVEL)

Now that you have the foundation, you can add:

**1. Liquidity Drain Alert**
- Track liquidity over time
- Alert when LP being pulled (rug risk)

**2. Volume Spike Without MC Spike**
- Suggests accumulation
- Often precedes pumps

**3. Multi-Timeframe Analysis**
- Check momentum over 5min, 15min, 1hr windows
- More robust signals

**4. Walletprofiler Integration**
- Show top wallets buying/selling
- Real SMB activity

These are all just extensions of the framework you have now.

---

## MONETIZATION READY

With this intel, you can:

**Free Tier:**
- 1-2 coins
- Basic alerts only
- Aggressive profile only

**Paid Tier ($5-10/month):**
- Unlimited coins
- All profiles
- Pattern detection
- Quality filtering
- Priority alerts

**This is real value.** Users will pay.

---

## NEXT STEPS

1. Deploy this version
2. Test with 3-4 coins for 24hrs
3. Watch alerts vs. actual price action
4. Iterate on thresholds
5. Add monetization when confident

You now have a professional-grade alert bot. 🚀
