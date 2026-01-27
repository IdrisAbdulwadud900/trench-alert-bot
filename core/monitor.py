#!/usr/bin/env python3
"""
Core Monitor - Background alert checking
Pure background task - No UI logic
"""

import asyncio
from telegram import Bot
from config import CHECK_INTERVAL
from storage import load_data, save_data
from mc import get_market_cap
from intelligence import update_coin_history
from core.alerts import AlertEngine
from settings import get_chat_settings
from plans import can_loud_alerts


async def start_monitor(bot: Bot):
    """Main monitoring loop - runs forever."""
    print("📡 Monitor loop running...")
    
    while True:
        try:
            data = load_data()
            
            for user_id, user_data in data.items():
                try:
                    # Handle both data formats
                    if isinstance(user_data, list):
                        coins = user_data
                        user_mode = "aggressive"
                    else:
                        coins = user_data.get("coins", [])
                        user_mode = user_data.get("profile", {}).get("mode", "aggressive")
                    
                    for coin in coins:
                        try:
                            ca = coin.get("ca")
                            if not ca:
                                continue
                            
                            # Fetch current market data
                            token = get_market_cap(ca)
                            if not token:
                                continue
                            
                            mc = token["mc"]
                            volume_24h = token.get("volume_24h", 0)
                            liquidity = token.get("liquidity", 0)
                            
                            # Update coin history
                            coin = update_coin_history(coin, mc, volume_24h, liquidity)
                            
                            # Evaluate all alerts
                            alerts_to_fire = AlertEngine.evaluate_all(
                                coin, mc, volume_24h, user_mode
                            )
                            
                            # Send alerts
                            for alert_type, message in alerts_to_fire:
                                chat = get_chat_settings(user_id)
                                disable_notification = not can_loud_alerts(chat, user_id)
                                
                                await bot.send_message(
                                    chat_id=user_id,
                                    text=message,
                                    disable_notification=disable_notification
                                )
                                
                                # Mark as triggered
                                coin.setdefault("triggered", {})
                                coin["triggered"][alert_type] = True
                            
                            await asyncio.sleep(1)  # Throttle
                        
                        except Exception as e:
                            print(f"Coin error: {e}")
                            continue
                    
                    # Save updated data
                    if isinstance(user_data, dict):
                        data[user_id] = user_data
                    
                except Exception as e:
                    print(f"User error: {e}")
                    continue
            
            save_data(data)
            
        except Exception as e:
            print(f"Monitor error: {e}")
        
        await asyncio.sleep(CHECK_INTERVAL)
