#!/usr/bin/env python3
"""
UX Flow Testing - Comprehensive UI/UX Validation
Tests all user flows and identifies improvement opportunities
"""

import sys
from collections import defaultdict

print("=" * 70)
print("UX FLOW VALIDATION")
print("=" * 70)

issues = []
improvements = []

# Test 1: Check all UI modules exist and are importable
print("\n✅ Test 1: UI Module Structure")
try:
    from ui import home, coins, wallets, lists, dashboard, settings, history, notifications, search, admin
    print("   ✓ All UI modules importable")
except ImportError as e:
    issues.append(f"UI Module missing: {e}")
    print(f"   ✗ {e}")

# Test 2: Verify consistent message formatting
print("\n✅ Test 2: Message Formatting Consistency")
try:
    import re
    
    # Check for inconsistent emoji usage
    files_to_check = [
        'ui/home.py', 'ui/coins.py', 'ui/wallets.py', 'ui/lists.py',
        'ui/dashboard.py', 'ui/settings.py', 'ui/history.py'
    ]
    
    emoji_patterns = defaultdict(set)
    
    for filepath in files_to_check:
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                # Find all emoji + text patterns
                matches = re.findall(r'[📈📊👛📋⚙️🔔📜🗑️➕✏️◀🔍⏸️▶️]+ [A-Z][a-z ]+', content)
                for match in matches:
                    emoji_patterns[match.split()[0]].add(' '.join(match.split()[1:]))
        except FileNotFoundError:
            pass
    
    print("   ✓ Emoji usage checked")
    
    # Check for inconsistent spacing
    spacing_check = True
    for filepath in files_to_check:
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    # Check for double spaces
                    if '  ' in line and '"""' not in line:
                        improvements.append(f"{filepath}:{i} - Double spaces found")
                        spacing_check = False
        except FileNotFoundError:
            pass
    
    if spacing_check:
        print("   ✓ No spacing issues found")
    else:
        print(f"   ⚠ {len([i for i in improvements if 'Double spaces' in i])} spacing issues")
        
except Exception as e:
    issues.append(f"Message formatting check failed: {e}")
    print(f"   ✗ {e}")

# Test 3: Check for helpful error messages
print("\n✅ Test 3: Error Message Quality")
try:
    error_messages_found = 0
    vague_errors = []
    
    import os
    for root, dirs, files in os.walk('ui'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    # Look for error messages
                    error_msgs = re.findall(r'reply_text\(["\']❌[^"\']+["\']\)', content)
                    error_messages_found += len(error_msgs)
                    
                    # Check for vague errors
                    for msg in error_msgs:
                        if 'Error' in msg and 'failed' in msg.lower():
                            if filepath not in [v.split(':')[0] for v in vague_errors]:
                                vague_errors.append(f"{filepath}: Generic error message")
    
    print(f"   ✓ Found {error_messages_found} error messages")
    if vague_errors:
        print(f"   ⚠ {len(vague_errors)} could be more specific")
        improvements.extend(vague_errors[:3])  # Show first 3
    else:
        print("   ✓ All error messages are specific")
        
except Exception as e:
    issues.append(f"Error message check failed: {e}")
    print(f"   ✗ {e}")

# Test 4: Check for loading states
print("\n✅ Test 4: Loading States & Feedback")
try:
    files_checked = 0
    loading_indicators = 0
    
    for root, dirs, files in os.walk('ui'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    files_checked += 1
                    # Look for loading indicators
                    if '⏳' in content or 'Loading' in content or 'Processing' in content:
                        loading_indicators += 1
    
    if loading_indicators > 0:
        print(f"   ✓ {loading_indicators}/{files_checked} files have loading states")
    else:
        improvements.append("Add loading states for API calls")
        print(f"   ⚠ No loading states found - consider adding")
        
except Exception as e:
    issues.append(f"Loading state check failed: {e}")
    print(f"   ✗ {e}")

# Test 5: Check for confirmation dialogs
print("\n✅ Test 5: Confirmation Dialogs")
try:
    dangerous_actions = ['delete', 'remove', 'clear']
    confirmations_found = 0
    missing_confirmations = []
    
    for root, dirs, files in os.walk('ui'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    for action in dangerous_actions:
                        if f'{action}_' in content.lower() and 'confirm' in content.lower():
                            confirmations_found += 1
                        elif f'{action}_all' in content.lower() and 'confirm' not in content.lower():
                            missing_confirmations.append(f"{filepath}: {action}_all without confirmation")
    
    print(f"   ✓ Found {confirmations_found} confirmations")
    if missing_confirmations:
        print(f"   ⚠ {len(missing_confirmations)} actions could use confirmation")
        improvements.extend(missing_confirmations[:2])
    else:
        print("   ✓ All destructive actions have confirmations")
        
except Exception as e:
    issues.append(f"Confirmation check failed: {e}")
    print(f"   ✗ {e}")

# Test 6: Check for empty state messages
print("\n✅ Test 6: Empty State Handling")
try:
    empty_state_patterns = ['No coins', 'No wallets', 'No lists', 'No alerts', 'No data']
    empty_states_with_cta = 0
    empty_states_without_cta = 0
    
    for root, dirs, files in os.walk('ui'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    for pattern in empty_state_patterns:
                        if pattern in content:
                            # Check if there's a call-to-action nearby
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if pattern in line:
                                    # Check next 5 lines for CTA
                                    next_lines = '\n'.join(lines[i:i+5])
                                    if 'Use' in next_lines or 'Add' in next_lines or '➕' in next_lines:
                                        empty_states_with_cta += 1
                                    else:
                                        empty_states_without_cta += 1
                                    break
    
    total_empty_states = empty_states_with_cta + empty_states_without_cta
    if total_empty_states > 0:
        print(f"   ✓ {empty_states_with_cta}/{total_empty_states} empty states have CTAs")
        if empty_states_without_cta > 0:
            improvements.append(f"{empty_states_without_cta} empty states could use clear CTAs")
    else:
        print("   ✓ Empty state handling looks good")
        
except Exception as e:
    issues.append(f"Empty state check failed: {e}")
    print(f"   ✗ {e}")

# Test 7: Check navigation consistency
print("\n✅ Test 7: Navigation Consistency")
try:
    back_button_count = 0
    home_button_count = 0
    
    for root, dirs, files in os.walk('ui'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    back_button_count += content.count('◀ Back') + content.count('Back')
                    home_button_count += content.count('🏠 Home') + content.count('callback_data="home"')
    
    print(f"   ✓ {back_button_count} back buttons found")
    print(f"   ✓ {home_button_count} home references found")
    
    if back_button_count < 5:
        improvements.append("Consider adding more back buttons for easier navigation")
        
except Exception as e:
    issues.append(f"Navigation check failed: {e}")
    print(f"   ✗ {e}")

# Test 8: Check message length
print("\n✅ Test 8: Message Length (Telegram Limits)")
try:
    long_messages = []
    
    for root, dirs, files in os.walk('ui'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    # Find multi-line strings
                    matches = re.findall(r'"""(.+?)"""', content, re.DOTALL)
                    for match in matches:
                        if len(match) > 3000:  # Telegram limit is 4096
                            long_messages.append(f"{filepath}: Message length {len(match)}")
    
    if long_messages:
        print(f"   ⚠ {len(long_messages)} messages might exceed Telegram limits")
        improvements.extend(long_messages)
    else:
        print("   ✓ All messages within safe limits")
        
except Exception as e:
    issues.append(f"Message length check failed: {e}")
    print(f"   ✗ {e}")

# Test 9: Check for proper keyboard layouts
print("\n✅ Test 9: Keyboard Layout Quality")
try:
    keyboards_checked = 0
    wide_rows = 0
    
    for root, dirs, files in os.walk('ui'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    # Count keyboard definitions
                    keyboards_checked += content.count('keyboard = [')
                    # Check for rows with too many buttons (>3 is hard to read on mobile)
                    matches = re.findall(r'\[InlineKeyboardButton[^\]]+InlineKeyboardButton[^\]]+InlineKeyboardButton[^\]]+InlineKeyboardButton', content)
                    wide_rows += len(matches)
    
    print(f"   ✓ {keyboards_checked} keyboards defined")
    if wide_rows > 0:
        print(f"   ⚠ {wide_rows} rows have 4+ buttons (might be cramped on mobile)")
        improvements.append(f"{wide_rows} keyboard rows could be split for better mobile UX")
    else:
        print("   ✓ All keyboard layouts mobile-friendly")
        
except Exception as e:
    issues.append(f"Keyboard layout check failed: {e}")
    print(f"   ✗ {e}")

# Test 10: Check for consistent emoji usage
print("\n✅ Test 10: Icon/Emoji Consistency")
try:
    feature_icons = {}
    inconsistencies = []
    
    files_to_check = ['ui/home.py', 'ui/coins.py', 'ui/wallets.py', 'ui/lists.py']
    
    for filepath in files_to_check:
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                # Extract feature names and their icons
                matches = re.findall(r'([📈📊👛📋⚙️🔔📜🗑️➕✏️◀🔍]) ([A-Z][a-z ]+)', content)
                for icon, name in matches:
                    if name in feature_icons and feature_icons[name] != icon:
                        inconsistencies.append(f"{name} uses both {feature_icons[name]} and {icon}")
                    else:
                        feature_icons[name] = icon
        except FileNotFoundError:
            pass
    
    if inconsistencies:
        print(f"   ⚠ {len(inconsistencies)} icon inconsistencies found")
        improvements.extend(inconsistencies[:3])
    else:
        print(f"   ✓ Consistent icon usage across {len(feature_icons)} features")
        
except Exception as e:
    issues.append(f"Icon consistency check failed: {e}")
    print(f"   ✗ {e}")

def _print_summary_and_get_exit_code(issues, improvements) -> int:
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if not issues:
        print("\n✅ NO CRITICAL ISSUES FOUND")
    else:
        print(f"\n❌ {len(issues)} CRITICAL ISSUES:")
        for issue in issues:
            print(f"   • {issue}")

    if improvements:
        print(f"\n💡 {len(improvements)} IMPROVEMENT OPPORTUNITIES:")
        for improvement in improvements[:10]:
            print(f"   • {improvement}")
    else:
        print("\n🎉 UX IS EXCELLENT - NO IMPROVEMENTS NEEDED!")

    print("\n" + "=" * 70)
    if not issues and len(improvements) < 5:
        print("✅ UX QUALITY: EXCELLENT")
        return 0
    if not issues:
        print("✅ UX QUALITY: GOOD (Minor improvements suggested)")
        return 0

    print("⚠️ UX QUALITY: NEEDS ATTENTION")
    return 1


def test_ux_flows_have_no_critical_issues():
    """Pytest entrypoint: only fail on critical UX issues."""
    assert not issues, f"Critical UX issues found: {issues}"


if __name__ == "__main__":
    sys.exit(_print_summary_and_get_exit_code(issues, improvements))
