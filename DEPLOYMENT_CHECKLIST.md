# ✅ Pre-Deployment Checklist

## System Verification

```bash
# 1. Check Python syntax (no errors)
python3 -m py_compile app.py price.py supply.py monitor.py bot.py

# 2. Check all imports resolve
python3 -c "import app; import mc; import price; import supply; print('✅ All imports OK')"

# 3. Verify requirements installed
pip show python-telegram-bot requests solana

# 4. Check data.json is reset
cat data.json
# Should output: {}
```

## Environment Variables

```bash
# Set these before running:
export BOT_TOKEN="your_token_here"
export CHECK_INTERVAL="60"

# Verify they're set:
echo $BOT_TOKEN
echo $CHECK_INTERVAL
```

## Startup Test

```bash
# Run with timeout to verify startup works
timeout 5 python3 app.py || true

# Expected output:
# 🚀 Trench Alert Bot running...
# 📡 Monitor loop started in background thread
```

## Code Quality Verification

✅ **All checks passed:**
- [x] No syntax errors (verified)
- [x] All float() calls are validated
- [x] All dict access uses .get()
- [x] All API calls have error handling
- [x] Retry logic implemented in price.py
- [x] Monitor loops have inner error handling
- [x] Startup logs present
- [x] Type safety improved
- [x] User feedback messages improved
- [x] data.json is empty (fresh state)

## Deployment Steps

### **Option 1: Render (Recommended)**

1. Push to GitHub:
```bash
git add .
git commit -m "Fix: Complete code audit and safety improvements"
git push
```

2. Create Render service:
   - Service type: **Background Worker**
   - Runtime: **Python 3.11**
   - Start command: `python app.py`

3. Set environment variables in Render:
   - `BOT_TOKEN`: your_token
   - `CHECK_INTERVAL`: 60

4. Click "Create Web Service"

5. Check logs (should see):
```
🚀 Trench Alert Bot running...
📡 Monitor loop started in background thread
```

### **Option 2: Local Testing**

```bash
# Install dependencies
pip install -r requirements.txt

# Export token
export BOT_TOKEN="your_test_token"
export CHECK_INTERVAL="60"

# Run
python app.py
```

### **Option 3: Docker Deployment**

```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t mc-alert-bot .
docker run -e BOT_TOKEN="your_token" mc-alert-bot
```

## Post-Deployment Verification

1. ✅ Bot is running (check logs for startup messages)
2. ✅ Send `/start` command to bot - should respond
3. ✅ Send `/list` - should say "You are not monitoring any coins"
4. ✅ Add a coin and verify no crashes
5. ✅ Check logs for any error messages

## Troubleshooting

**Bot doesn't respond:**
- Check BOT_TOKEN is correct
- Check logs for "Token lookup error"
- Verify internet connection

**Monitor crashes:**
- Check logs for "Monitor error"
- Verify DexScreener API is accessible
- Check data.json isn't corrupted

**High CPU/Memory:**
- Check asyncio.sleep(2) is in place (it is)
- Check time.sleep() is used in sync context (it is)
- Monitor should use ~1-2% CPU

## Files Changed

| File | Changes | Status |
|------|---------|--------|
| app.py | Input validation, error handling, startup log | ✅ Production Ready |
| price.py | Retry logic, exception handling | ✅ Enhanced |
| monitor.py | Marked deprecated | ⚠️ Reference Only |
| bot.py | Marked deprecated | ⚠️ Reference Only |
| data.json | Reset to {} | ✅ Clean |

## Ready to Deploy! 🚀

All issues fixed. Code is safe and production-ready.

**Next Steps:**
1. Push to GitHub
2. Deploy to Render
3. Monitor logs for first 24 hours
4. Add users once confirmed stable
