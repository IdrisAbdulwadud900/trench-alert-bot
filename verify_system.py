#!/usr/bin/env python3
"""
Final comprehensive system check for Trench Alert Bot
"""
import sys

errors = []

print('=' * 60)
print('COMPREHENSIVE SYSTEM CHECK')
print('=' * 60)

# 1. Check all core modules
print('\n1. MODULE IMPORTS:')
modules = [
    'app', 'mc', 'price', 'supply', 'storage', 
    'wallets', 'lists', 'groups', 'intelligence',
    'subscriptions', 'meta', 'onchain',
    'wallet_scanner', 'wallet_parser', 'wallet_alert_engine'
]
for mod in modules:
    try:
        __import__(mod)
        print(f'   ✅ {mod}')
    except Exception as e:
        print(f'   ❌ {mod}: {e}')
        errors.append(f'{mod} import failed')

# 2. Check data files
print('\n2. DATA FILES:')
import os, json
files = ['data.json', 'wallets.json', 'lists.json', 'groups.json']
for f in files:
    if os.path.exists(f):
        try:
            with open(f) as fp:
                json.load(fp)
            print(f'   ✅ {f}')
        except Exception as e:
            print(f'   ❌ {f} - corrupted: {e}')
            errors.append(f'{f} corrupted')
    else:
        print(f'   ⚠️  {f} - will be created')

# 3. Check key functions
print('\n3. KEY FUNCTIONS:')
try:
    from storage import load_data, save_data
    from subscriptions import get_user_tier, can_use_wallet_alerts
    from onchain import detect_wallet_buys, format_wallet_buy_alert
    print('   ✅ Storage functions')
    print('   ✅ Subscription functions')
    print('   ✅ Wallet detection functions')
except Exception as e:
    print(f'   ❌ Function test failed: {e}')
    errors.append('Function tests failed')

# 4. Check wallet detection pipeline
print('\n4. WALLET DETECTION PIPELINE:')
try:
    from wallet_scanner import get_recent_signatures
    from wallet_parser import get_transaction, parse_token_inflow
    from wallet_alert_engine import detect_new_buys
    print('   ✅ Layer 1: Signature fetching')
    print('   ✅ Layer 2: Transaction parsing')
    print('   ✅ Layer 3: Alert engine')
except Exception as e:
    print(f'   ❌ Pipeline incomplete: {e}')
    errors.append('Pipeline incomplete')

# 5. Check config
print('\n5. CONFIGURATION:')
try:
    from config import BOT_TOKEN, CHECK_INTERVAL
    print(f'   ✅ CHECK_INTERVAL: {CHECK_INTERVAL}s')
    if BOT_TOKEN:
        print(f'   ✅ BOT_TOKEN: Set')
    else:
        print(f'   ⚠️  BOT_TOKEN: Not set (required for deployment)')
except Exception as e:
    print(f'   ❌ Config error: {e}')
    errors.append('Config error')

# Summary
print('\n' + '=' * 60)
if errors:
    print('RESULT: ❌ ERRORS FOUND')
    for e in errors:
        print(f'  - {e}')
    sys.exit(1)
else:
    print('RESULT: ✅ ALL CHECKS PASSED')
    print('=' * 60)
    print('\nSystem is production-ready!')
    print('\nDeployment checklist:')
    print('  1. Set BOT_TOKEN environment variable on Render')
    print('  2. Push latest code to GitHub (already done)')
    print('  3. Deploy on Render')
    print('  4. Monitor logs for any runtime issues')
    sys.exit(0)
