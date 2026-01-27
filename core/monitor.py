#!/usr/bin/env python3
"""
Core Monitor - Background alert checking
Pure background task - No UI logic
"""

import asyncio
from telegram import Bot
from config import CHECK_INTERVAL
from storage import load_data, save_data
from wallets import load_wallets
from mc import get_market_cap
from intelligence import update_coin_history
from core.alerts import AlertEngine
from settings import get_chat_settings
from plans import can_loud_alerts, can_wallet_alerts


async def start_monitor(bot: Bot):
    """Main monitoring loop - runs forever."""
    print("📡 Monitor loop running...")
    
    while True:
        try:
            data = load_data()
            wallets_data = load_wallets()
            
            # Monitor coins
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
            
            # Monitor wallets for buys
            for user_id, wallets in wallets_data.items():
                try:
                    # Convert user_id to int safely
                    try:
                        user_id_int = int(user_id)
                    except (ValueError, TypeError):
                        # Skip invalid user IDs (like test_999 from tests)
                        continue
                    
                    chat = get_chat_settings(user_id)
                    
                    # Check if user has wallet alert permission
                    if not can_wallet_alerts(chat, user_id_int):
                        continue
                    
                    for wallet in wallets:
                        try:
                            address = wallet.get("address")
                            if not address:
                                continue
                            
                            # Check for new buys (using existing wallet_alert_engine)
                            from wallet_alert_engine import detect_wallet_buys
                            from onchain import format_wallet_buy_alert
                            
                            # Get user's tracked coins for context
                            user_data = data.get(str(user_id), {})
                            if isinstance(user_data, dict):
                                tracked_coins = user_data.get("coins", [])
                            else:
                                tracked_coins = user_data if isinstance(user_data, list) else []
                            
                            # Check each tracked coin for wallet buys
                            for coin in tracked_coins:
                                ca = coin.get("ca")
                                if not ca:
                                    continue
                                
                                buy_info = detect_wallet_buys(address, coin, min_usd=100)
                                
                                if buy_info:
                                    alert_msg = format_wallet_buy_alert(
                                        {
                                            "type": "wallet_buy",
                                            "wallet": address,
                                            "amount_usd": buy_info.get("amount_usd", 0),
                                            "signature": buy_info.get("signature", "")
                                        },
                                        coin_symbol=ca[:8]
                                    )
                                    
                                    disable_notification = not can_loud_alerts(chat, user_id)
                                    
                                    await bot.send_message(
                                        chat_id=user_id,
                                        text=alert_msg,
                                        disable_notification=disable_notification
                                    )
                                
                                await asyncio.sleep(0.5)  # Throttle
                        
                        except Exception as e:
                            print(f"Wallet monitoring error: {e}")
                            continue
                
                except Exception as e:
                    print(f"User wallet error: {e}")
                    continue
            
            save_data(data)
            
        except Exception as e:
            print(f"Monitor error: {e}")
        
        await asyncio.sleep(CHECK_INTERVAL)
