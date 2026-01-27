# ⚠️ NOTE: This file is deprecated.
# All monitor logic has been consolidated into app.py
# Use app.py instead - it includes error handling, throttling, and async protection.

import asyncio
from storage import get_all_coins, save_data
from config import CHECK_INTERVAL
from telegram import Bot
from mc import get_market_cap

async def monitor(bot: Bot):
    """DEPRECATED: Use monitor_loop() in app.py instead."""
    while True:
        try:
            data = get_all_coins()
            for user_id, coins in data.items():
                if not isinstance(coins, list):
                    continue
                    
                for coin in coins:
                    if not isinstance(coin, dict):
                        continue
                        
                    token = get_market_cap(coin.get("ca"))
                    if not token or not token.get("mc"):
                        continue

                    mc = token["mc"]
                    start = coin["start_mc"]
                    dd = ((start - mc) / start) * 100
                    x = mc / start

                    triggered = coin.get("triggered", {})
                    if not triggered.get("mc") and mc <= coin.get("alert_mc"):
                        await bot.send_message(user_id, f"🚨 MC alert hit: {int(mc)}")
                        triggered["mc"] = True
                        
                    await asyncio.sleep(2)  # Throttle API

            save_data(data)
        except Exception as e:
            print(f"Monitor error: {e}")
            
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    print("⚠️ Use app.py instead")
    asyncio.run(monitor(None))
