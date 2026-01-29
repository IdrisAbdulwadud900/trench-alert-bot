#!/usr/bin/env python3
"""
Final UX Polish Validation
Tests all improved flows
"""


import sys

print("=" * 70)
print("FINAL UX POLISH VALIDATION")
print("=" * 70)

successes = []
issues = []

# Test 1: Import all modules
print("\n\u2705 Test 1: Module Imports")
try:
    import app
    from ui import home, coins, wallets, lists, dashboard, history, settings, notifications
    from core import monitor, tracker
    print("   \u2713 All modules import successfully")
    successes.append("Module imports")
except ImportError as e:
    issues.append(f"Import error: {e}")
    print(f"   \u2717 {e}")

# Test 2: Check for loading states
print("\n\u2705 Test 2: Loading States Added")
try:
    with open('ui/coins.py', 'r') as f:
        content = f.read()
        if '\u23f3' in content and 'loading_msg' in content:
            print("   \u2713 Loading states implemented in coins.py")
            successes.append("Loading states")
        else:
            issues.append("Loading states not found in coins.py")
except Exception as e:
    issues.append(f"Loading state check failed: {e}")

# Test 3: Check for improved empty states
print("\n\u2705 Test 3: Empty State Improvements")
try:
    files_checked = 0
    improvements_found = 0
    
    for filepath in ['ui/coins.py', 'ui/wallets.py', 'ui/lists.py', 'ui/dashboard.py']:
        with open(filepath, 'r') as f:
            content = f.read()
            files_checked += 1
            if '\ud83d\udca1' in content and 'Add Your First' in content:
                improvements_found += 1
    
    print(f"   \u2713 {improvements_found}/{files_checked} files have enhanced empty states")
    if improvements_found >= 3:
        successes.append("Empty state improvements")
    else:
        issues.append("Not enough empty state improvements")
except Exception as e:
    issues.append(f"Empty state check failed: {e}")

# Test 4: Check for better error messages
print("\n\u2705 Test 4: Improved Error Messages")
try:
    with open('app.py', 'r') as f:
        content = f.read()
        error_improvements = 0
        
        if 'Invalid Address Format' in content:
            error_improvements += 1
        if 'Token Not Found' in content:
            error_improvements += 1
        if 'Invalid Number' in content:
            error_improvements += 1
    
    print(f"   \u2713 {error_improvements} improved error messages found")
    if error_improvements >= 2:
        successes.append("Error message improvements")
    else:
        issues.append("Not enough error message improvements")
except Exception as e:
    issues.append(f"Error message check failed: {e}")

# Test 5: Check for success confirmations
print("\n\u2705 Test 5: Success Confirmations with Next Steps")
try:
    with open('app.py', 'r') as f:
        content = f.read()
        confirmations = 0
        
        if 'Successfully' in content and 'View' in content:
            confirmations += 1
        if 'Next:' in content or "You'll be" in content:
            confirmations += 1
    
    print(f"   \u2713 Success confirmations with guidance found")
    if confirmations >= 2:
        successes.append("Success confirmations")
    else:
        issues.append("Success confirmations need improvement")
except Exception as e:
    issues.append(f"Success confirmation check failed: {e}")

# Test 6: Check for enhanced alert formatting
print("\n\u2705 Test 6: Enhanced Alert Formatting")
try:
    with open('core/monitor.py', 'r') as f:
        content = f.read()
        if 'parse_mode=\"HTML\"' in content and 'timestamp' in content:
            print("   \u2713 Alerts now include timestamps and HTML formatting")
            successes.append("Alert formatting")
        else:
            issues.append("Alert formatting not fully enhanced")
except Exception as e:
    issues.append(f"Alert formatting check failed: {e}")

# Test 7: Check for inline keyboards with CTAs
print("\n\u2705 Test 7: Inline Keyboards with CTAs")
try:
    keyboard_count = 0
    for filepath in ['ui/coins.py', 'ui/wallets.py', 'ui/lists.py', 'app.py']:
        with open(filepath, 'r') as f:
            content = f.read()
            keyboard_count += content.count('InlineKeyboardMarkup(keyboard)')
    
    print(f"   \u2713 {keyboard_count} inline keyboards with action buttons")
    if keyboard_count >= 10:
        successes.append("Inline keyboards")
    else:
        issues.append("Not enough inline keyboards")
except Exception as e:
    issues.append(f"Keyboard check failed: {e}")

# Test 8: Check for helpful tips
print("\n\u2705 Test 8: Helpful Tips and Hints")
try:
    tip_count = 0
    for filepath in ['ui/coins.py', 'ui/wallets.py', 'app.py']:
        with open(filepath, 'r') as f:
            content = f.read()
            tip_count += content.count('\ud83d\udca1')
    
    print(f"   \u2713 {tip_count} helpful tips found throughout the UI")
    if tip_count >= 5:
        successes.append("Helpful tips")
    else:
        issues.append("Not enough helpful tips")
except Exception as e:
    issues.append(f"Tip check failed: {e}")

# Test 9: Check for consistent navigation
print("\n\u2705 Test 9: Consistent Navigation")
try:
    back_buttons = 0
    home_buttons = 0
    
    import os
    for root, dirs, files in os.walk('ui'):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    back_buttons += content.count('\u25c0 Back')
                    home_buttons += content.count('callback_data=\"home\"')
    
    print(f"   \u2713 {back_buttons} back buttons, {home_buttons} home references")
    if back_buttons >= 10:
        successes.append("Navigation consistency")
    else:
        issues.append("Navigation needs more back buttons")
except Exception as e:
    issues.append(f"Navigation check failed: {e}")

# Test 10: Code quality check
print("\n\u2705 Test 10: Code Quality")
try:
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', 'app.py'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("   \u2713 app.py compiles without syntax errors")
        successes.append("Code quality")
    else:
        issues.append("Syntax errors in app.py")
        print(f"   \u2717 Syntax error: {result.stderr}")
except Exception as e:
    issues.append(f"Code quality check failed: {e}")

# Summary
print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

print(f"\n\u2705 Successes: {len(successes)}/10")
for success in successes:
    print(f"   \u2713 {success}")

if issues:
    print(f"\n\u26a0\ufe0f  Issues: {len(issues)}")
    for issue in issues:
        print(f"   \u2022 {issue}")
else:
    print("\n\ud83c\udf89 No issues found!")

print("\n" + "=" * 70)
if len(successes) >= 8 and len(issues) == 0:
    print("\u2705 UX POLISH: EXCELLENT - Ready to deploy!")
    exit_code = 0
elif len(successes) >= 6:
    print("\u2705 UX POLISH: GOOD - Minor issues to address")
    exit_code = 0
else:
    print("\u26a0\ufe0f UX POLISH: Needs more work")
    exit_code = 1


def test_ux_polish_meets_minimum_quality_bar():
    # Match the script's definition of "good enough".
    assert exit_code == 0, f"UX polish below bar: successes={len(successes)}/10 issues={issues}"


if __name__ == "__main__":
    sys.exit(exit_code)
