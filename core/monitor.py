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
from alert_history import log_alert
from meta_alerts import evaluate_meta_alerts
from lists import load_lists
from core.meta_formatter import format_meta_alert
from timebased_alerts import should_alert_timeased
from combination_alerts import CombinationAlerts
from core.combo_formatter import format_combo_alert


async def start_monitor(bot: Bot):
    """Main monitoring loop - runs forever."""
    print("📡 Monitor loop running...")
    
    while True:
        try:
            data = load_data()
            wallets_data = load_wallets()
            lists_data = load_lists()
            
            # Monitor meta alerts for lists
            for user_id_str, user_lists in lists_data.items():
                try:
                    # Skip non-numeric user IDs (test/verification users)
                    try:
                        user_id_int = int(user_id_str)
                    except (ValueError, TypeError):
                        continue
                    
                    # Build coin_data dict from user's tracked coins
                    user_data = data.get(user_id_str, {})
                    if isinstance(user_data, list):
                        coins = user_data
                    else:
                        coins = user_data.get("coins", [])
                    
                    coin_data = {coin.get("ca"): coin for coin in coins if coin.get("ca")}
                    
                    # Check each list
                    for list_name, list_info in user_lists.items():
                        if isinstance(list_info, dict):
                            list_coins = list_info.get("coins", [])
                            meta_alerts = list_info.get("meta_alerts", {})
                            meta_triggered = list_info.get("meta_triggered", {})
                            
                            if meta_alerts and list_coins:
                                result = evaluate_meta_alerts(
                                    list_name,
                                    list_coins,
                                    coin_data,
                                    meta_alerts,
                                    meta_triggered
                                )
                                
                                if result:
                                    # Format alert message
                                    msg = format_meta_alert(result)
                                    
                                    # Send alert
                                    chat = get_chat_settings(user_id_str)
                                    disable_notification = not can_loud_alerts(chat, user_id_str)
                                    
                                    await bot.send_message(
                                        chat_id=user_id_int,
                                        text=msg,
                                        disable_notification=disable_notification
                                    )
                                    
                                    # Log alert
                                    log_alert(user_id_int, f"meta_{result['type']}", list_name, result)
                                    
                                    # Mark as triggered
                                    list_info["meta_triggered"][result["type"]] = True
                
                except Exception as e:
                    print(f"Meta alert error for user {user_id_str}: {e}")
                    continue
            
            # Save updated list states
            from lists import save_lists
            save_lists(lists_data)
            
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
                            
                            # Skip paused coins
                            if coin.get("paused", False):
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
                            
                            # Evaluate standard alerts
                            alerts_to_fire = AlertEngine.evaluate_all(
                                coin, mc, volume_24h, user_mode, liquidity
                            )
                            
                            # Evaluate time-based alerts
                            start_mc = coin.get("start_mc", 0)
                            try:
                                user_id_int = int(user_id)
                                timebased_result = should_alert_timeased(
                                    user_id_int, ca, mc, start_mc
                                )
                            except (ValueError, TypeError):
                                timebased_result = None
                            if timebased_result:
                                alerts_to_fire.append((
                                    timebased_result["type"],
                                    timebased_result["message"]
                                ))
                            
                            # Evaluate combination alerts
                            combo_alerts = coin.get("combo_alerts", {})
                            combo_triggered = coin.get("combo_triggered", {})
                            avg_volume = coin.get("avg_volume", 0)
                            
                            if combo_alerts:
                                combo_results = CombinationAlerts.evaluate_all_combos(
                                    mc, start_mc, volume_24h, liquidity,
                                    avg_volume, combo_alerts, combo_triggered
                                )
                                
                                for combo_type, details in combo_results:
                                    msg = format_combo_alert(combo_type, details, ca)
                                    alerts_to_fire.append((f"combo_{combo_type}", msg))
                                    coin.setdefault("combo_triggered", {})
                                    coin["combo_triggered"][combo_type] = True
                            
                            # Send alerts
                            for alert_type, message in alerts_to_fire:
                                chat = get_chat_settings(user_id)
                                disable_notification = not can_loud_alerts(chat, user_id)
                                
                                # Add timestamp and quick action buttons
                                from datetime import datetime
                                timestamp = datetime.now().strftime("%H:%M")
                                enhanced_message = f"[⏰ {timestamp}] {message}"
                                
                                await bot.send_message(
                                    chat_id=user_id,
                                    text=enhanced_message,
                                    disable_notification=disable_notification,
                                    parse_mode="HTML"
                                )
                                
                                # Log alert to history
                                try:
                                    user_id_int = int(user_id)
                                    log_alert(user_id_int, alert_type, ca, {"message": message, "mc": mc})
                                except (ValueError, TypeError):
                                    pass  # Skip logging for invalid user IDs
                                
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
