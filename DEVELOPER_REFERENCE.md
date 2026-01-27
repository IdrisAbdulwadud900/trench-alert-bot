# 📖 Developer Reference - Intelligence API

Quick reference for working with the intelligence system.

---

## Core Functions (intelligence.py)

### Range Analysis

```python
from intelligence import compute_range_position, get_range_description

# Get position in range (0.0 = bottom, 1.0 = top)
position = compute_range_position(
    mc=75000,        # current MC
    low_mc=40000,    # lowest seen
    ath_mc=150000    # highest seen
)
# Result: 0.467 (between low and high)

# Get human-readable description
desc = get_range_description(0.467)
# Result: "middle range ➡️"
```

### Quality Scoring

```python
from intelligence import compute_quality_score, should_alert_based_quality

# Score signal quality 0-3
score = compute_quality_score(
    liquidity=45000,
    volume_24h=150000,
    mc=100000
)
# Result: 3 (high quality)

# Check if meets user threshold
should_alert = should_alert_based_quality(
    quality_score=3,
    user_mode="conservative"
)
# Result: True (meets conservative 2+ requirement)
```

### Pattern Detection

```python
from intelligence import detect_dump_stabilize_bounce

# Detect bounce pattern
detected, pattern_type = detect_dump_stabilize_bounce(
    coin={
        "ath_mc": 200000,
        "history": [...]
    },
    mc=75000,
    current_volume=50000
)

if detected:
    print(f"Pattern detected: {pattern_type}")
    # Output: "Pattern detected: dump_stabilize_bounce"
```

### Momentum Analysis

```python
from intelligence import analyze_momentum

direction, strength = analyze_momentum(
    history=[
        {"mc": 100000, "ts": 1234567890},
        {"mc": 95000, "ts": 1234567900},
        # ... more history
    ]
)
# Result: ("down", 0.67) - Down trend, strong
```

### History Management

```python
from intelligence import update_coin_history

# Update coin tracking
coin = update_coin_history(
    coin=coin_data,
    mc=75000,
    volume_24h=150000,
    liquidity=45000
)

# Coin now has:
# - coin["history"] updated
# - coin["ath_mc"] updated
# - coin["low_mc"] updated
```

### Smart Formatting

```python
from intelligence import format_smart_alert

# Generate rich alert message
message = format_smart_alert(
    coin=coin_data,
    mc=75000,
    alert_type="dump_stabilize_bounce",
    user_mode="aggressive"
)

# Result:
# "🚀 BOUNCE PATTERN DETECTED\n..."
```

---

## User Profiles

```python
from intelligence import USER_MODES

# Access profile thresholds
conservative = USER_MODES["conservative"]
# {
#   "min_liquidity": 50000,
#   "min_volume_ratio": 0.5,
#   "min_quality_score": 2,
#   "max_dd_percent": 30
# }

aggressive = USER_MODES["aggressive"]
sniper = USER_MODES["sniper"]
```

---

## Storage Integration

### Getting User Profile

```python
from storage import get_user_profile

profile = get_user_profile(user_id=123456)
# Result: {"mode": "aggressive"}
```

### Setting User Profile

```python
from storage import set_user_profile

set_user_profile(
    user_id=123456,
    profile={"mode": "sniper"}
)
# User's mode is now "sniper"
```

### Updating Coin History

```python
from intelligence import update_coin_history
from storage import load_data, save_data

data = load_data()
coin = data[user_id]["coins"][0]

# Update tracking
coin = update_coin_history(coin, mc, volume, liquidity)

# Save back
data[user_id]["coins"][0] = coin
save_data(data)
```

---

## In Monitor Loop

```python
from intelligence import (
    update_coin_history,
    detect_dump_stabilize_bounce,
    should_suppress_alert,
    format_smart_alert,
    compute_range_position
)

# Standard pattern
for coin in coins:
    # 1. Update history/range
    coin = update_coin_history(coin, mc, volume, liquidity)
    
    # 2. Check if should suppress (quality)
    if should_suppress_alert(coin, "default", user_mode):
        continue
    
    # 3. Detect patterns
    detected, pattern = detect_dump_stabilize_bounce(coin, mc, volume)
    if detected:
        msg = format_smart_alert(coin, mc, pattern, user_mode)
        await bot.send_message(user_id, msg)
    
    # 4. Check other alerts
    # ... existing alert logic ...
```

---

## Enum: Alert Types

```python
# Valid alert_type values for format_smart_alert()

"dump_stabilize_bounce"  # Pattern alert
"mc_break"               # MC target hit
"range_bottom"           # Hit lowest point
"default"                # Generic alert
```

---

## Enum: User Modes

```python
# Valid modes for get_user_profile(), should_alert_based_quality()

"conservative"  # Strict filtering
"aggressive"    # Balanced (default)
"sniper"        # Permissive
```

---

## Key Constants

```python
# From intelligence.py

HISTORY_WINDOW = 600  # 10 minutes (seconds)

USER_MODES = {
    "conservative": {...},
    "aggressive": {...},
    "sniper": {...}
}
```

---

## Error Handling

All functions handle edge cases:

```python
# Safe handling of missing fields
range_pos = compute_range_position(
    mc=100,
    low_mc=50,
    ath_mc=50  # Edge case: ath == low
)
# Returns: 0.5 (default safe value)

# Safe handling of empty history
direction, strength = analyze_momentum(
    history=[]  # Empty
)
# Returns: ("stable", 0.0)
```

---

## Testing Patterns

### Test Quality Filtering

```python
coin = {
    "liquidity": 500,      # Low
    "volume_24h": 1000,    # Low
    "mc": 5000             # Low
}

score = compute_quality_score(500, 1000, 5000)
# Result: 0 (all checks failed)

should_alert = should_alert_based_quality(0, "conservative")
# Result: False (conservative requires 2+)
```

### Test Pattern Detection

```python
coin = {
    "ath_mc": 200000,
    "low_mc": 50000,
    "history": [
        {"mc": 50000, "ts": time.time() - 300, "volume": 10000},
        {"mc": 50500, "ts": time.time() - 200, "volume": 15000},
        {"mc": 50400, "ts": time.time(), "volume": 20000}
    ]
}

detected, pattern = detect_dump_stabilize_bounce(
    coin=coin,
    mc=50400,
    current_volume=20000
)

# Coin dumped 75% ✓
# Stabilized ✓
# Volume increasing ✓
# Bounced 10%? (Not yet, so returns False)
```

---

## Performance Notes

- **History trimming:** Automatic, keeps 20 minutes
- **Quality calculation:** O(1), instant
- **Pattern detection:** O(n) where n=history entries (small)
- **Memory:** ~500 bytes per coin per 10 minutes

Safe for 100+ coins being tracked.

---

## Backwards Compatibility

Old data format:
```json
{"user_id": [{"ca": "..."}]}
```

Is auto-upgraded to:
```json
{"user_id": {"coins": [...], "profile": {...}}}
```

No migration code needed.

---

**This is the intelligence engine. Use it in all new features.** 🧠
