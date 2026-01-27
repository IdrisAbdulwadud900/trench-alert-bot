#!/usr/bin/env python3
"""
Quick diagnostic to test if alert system is working
"""

import json
import os

def check_alert_setup():
    print("🔍 Alert System Diagnostic\n")
    
    # Check data.json
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            data = json.load(f)
        
        print("📊 TRACKED COINS:")
        coin_count = 0
        for user_id, user_data in data.items():
            if isinstance(user_data, dict):
                coins = user_data.get("coins", [])
            else:
                coins = user_data
            
            if coins:
                print(f"\n👤 User {user_id}: {len(coins)} coin(s)")
                for i, coin in enumerate(coins, 1):
                    ca = coin.get("ca", "Unknown")
                    alerts = coin.get("alerts", {})
                    triggered = coin.get("triggered", {})
                    
                    print(f"  {i}. {ca[:10]}...")
                    print(f"     Alerts: {list(alerts.keys())}")
                    print(f"     Triggered: {triggered}")
                    coin_count += 1
            else:
                print(f"\n👤 User {user_id}: No coins tracked")
        
        if coin_count == 0:
            print("\n⚠️  NO COINS BEING TRACKED")
            print("   → Add a coin using the bot to enable alerts")
    else:
        print("❌ data.json not found")
    
    # Check settings
    print("\n\n⚙️  SETTINGS:")
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as f:
            settings = json.load(f)
        print(json.dumps(settings, indent=2))
    else:
        print("No settings.json found")
    
    # Check wallets
    print("\n\n👛 WALLETS:")
    if os.path.exists("wallets.json"):
        with open("wallets.json", "r") as f:
            wallets = json.load(f)
        for user_id, user_wallets in wallets.items():
            print(f"User {user_id}: {len(user_wallets)} wallet(s)")
    else:
        print("No wallets.json found")
    
    # Check lists
    print("\n\n📂 LISTS:")
    if os.path.exists("lists.json"):
        with open("lists.json", "r") as f:
            lists = json.load(f)
        for user_id, user_lists in lists.items():
            print(f"User {user_id}: {len(user_lists)} list(s)")
    else:
        print("No lists.json found")
    
    print("\n\n" + "="*50)
    print("DIAGNOSIS:")
    print("="*50)
    
    if coin_count == 0:
        print("❌ No coins tracked - alerts won't trigger")
        print("   Fix: Use /start and add a coin with alerts")
    else:
        print(f"✅ {coin_count} coin(s) tracked")
        print("   Monitor loop should be checking them every 60 seconds")
        print("   Check Render logs to see if monitor is running")

if __name__ == "__main__":
    check_alert_setup()
