# 🎯 Code Standards & Best Practices

Follow these patterns for all future development:

---

## ✅ Input Validation Pattern

```python
# ❌ WRONG - No validation
value = float(user_input)

# ✅ RIGHT - Validated with feedback
try:
    value = float(user_input)
except ValueError:
    await update.message.reply_text("❌ Invalid number. Please try again:")
    return
```

---

## ✅ Safe Dictionary Access Pattern

```python
# ❌ WRONG - Crashes if key missing
price = token["price"]

# ✅ RIGHT - Safe fallback
price = token.get("price")
# or with default
price = token.get("price", 0)
```

---

## ✅ Type Safety Pattern

```python
# ❌ WRONG - Type uncertainty
return_value = some_api_call()

# ✅ RIGHT - Guaranteed type
return {
    "price": float(api_response["price"]),
    "volume": float(api_response.get("volume", 0))
}
```

---

## ✅ API Call Pattern with Retry

```python
MAX_RETRIES = 3

def api_call(url, data=None):
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(0.5 * (attempt + 1))
                continue
            
            return response.json()
            
        except (requests.RequestException, ValueError) as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(0.5 * (attempt + 1))
            continue
    
    return None
```

---

## ✅ Monitor Loop Pattern

```python
async def monitor():
    while True:
        try:
            data = load_data()
            
            for user_id, items in data.items():
                # Validate types
                if not isinstance(items, list):
                    continue
                
                for item in items:
                    try:
                        # Isolated error handling per item
                        result = process_item(item)
                        if result:
                            await send_alert(user_id, result)
                        
                        await asyncio.sleep(2)  # Throttle
                        
                    except Exception as e:
                        print(f"Item error: {e}")
                        continue
            
            save_data(data)
            
        except Exception as e:
            print(f"Monitor error: {e}")
        
        await asyncio.sleep(INTERVAL)
```

---

## ✅ Logging Pattern

```python
# ✅ Startup logging
print("🚀 Bot starting up...")
print("📡 Monitor loop started")

# ✅ Error logging
print(f"❌ Error: {e}")
print(f"Token lookup error: {e}")

# ✅ State logging (debug mode)
if DEBUG:
    print(f"Processing user {user_id}: {num_coins} coins")
```

---

## ✅ Command Handler Pattern

```python
async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    # Validate user state
    if user_id not in user_data:
        await update.message.reply_text("No data found.")
        return
    
    # Validate data
    data = user_data[user_id]
    if not data:
        await update.message.reply_text("Empty data.")
        return
    
    # Process with error handling
    try:
        result = process(data)
        await update.message.reply_text(f"Result: {result}")
    except Exception as e:
        print(f"Command error: {e}")
        await update.message.reply_text("Error processing request.")
```

---

## ❌ Anti-Patterns to Avoid

| Pattern | Problem | Solution |
|---------|---------|----------|
| `float(user_input)` | ValueError crash | Use try-except |
| `dict["key"]` | KeyError crash | Use `dict.get("key")` |
| Single API call | Network hiccup = fail | Add retry logic |
| Bare `except Exception` | Catches too much | Catch specific exceptions |
| No type validation | Downstream errors | Assert types early |
| Async sleep in sync context | Doesn't actually sleep | Use `time.sleep()` |

---

## 🎯 Before Deploying Code

Checklist:
- [ ] All inputs validated
- [ ] All API calls have try-except
- [ ] All dict access uses `.get()`
- [ ] Types are guaranteed (use `float()`, `int()`, `str()`)
- [ ] Retry logic on network calls
- [ ] Startup logs show initialization
- [ ] Error messages are user-friendly
- [ ] No bare `except:` statements
- [ ] Monitor loops have inner + outer error handling
- [ ] Rate limiting implemented (asyncio.sleep or time.sleep)

---

**Apply these patterns to all new code.**
