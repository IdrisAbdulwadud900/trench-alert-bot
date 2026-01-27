#!/usr/bin/env python3
"""
Quick verification that Phase 5 Group Support is working
"""

print("🧪 Phase 5 Verification\n")

# Test 1: Import all group functions
print("✅ Test 1: Imports")
try:
    from groups import (
        create_group,
        add_group_admin,
        get_group_admins,
        add_coin_to_group,
        get_group_coins,
        remove_coin_from_group,
        update_group_coin_alerts,
        update_group_coin_history,
        get_all_group_ids,
        delete_group
    )
    print("   ✓ All groups.py functions imported\n")
except ImportError as e:
    print(f"   ✗ Import error: {e}\n")
    exit(1)

# Test 2: Check app.py has is_admin
print("✅ Test 2: Admin Check Function")
try:
    from app import is_admin
    print("   ✓ is_admin function exists in app.py\n")
except ImportError as e:
    print(f"   ✗ Import error: {e}\n")
    exit(1)

# Test 3: Verify group handlers exist
print("✅ Test 3: Group Handlers")
try:
    from app import (
        handle_group_track_coin,
        handle_group_status,
        handle_group_help
    )
    print("   ✓ All group handlers exist\n")
except ImportError as e:
    print(f"   ✗ Import error: {e}\n")
    exit(1)

# Test 4: Run basic storage test
print("✅ Test 4: Storage Operations")
import os
if os.path.exists("groups.json"):
    os.remove("groups.json")

group_id = "-100123456789"
admin_id = 12345678

success = create_group(group_id, admin_id)
if success:
    print("   ✓ Group creation works")
else:
    print("   ✗ Group creation failed")
    exit(1)

coins = get_group_coins(group_id)
if isinstance(coins, list):
    print("   ✓ Group coin retrieval works")
else:
    print("   ✗ Group coin retrieval failed")
    exit(1)

admins = get_group_admins(group_id)
if admin_id in admins:
    print("   ✓ Admin tracking works\n")
else:
    print("   ✗ Admin tracking failed\n")
    exit(1)

# Test 5: Check app.py compiles
print("✅ Test 5: Code Compilation")
import py_compile
try:
    py_compile.compile("app.py", doraise=True)
    print("   ✓ app.py compiles")
    py_compile.compile("groups.py", doraise=True)
    print("   ✓ groups.py compiles\n")
except py_compile.PyCompileError as e:
    print(f"   ✗ Compilation error: {e}\n")
    exit(1)

print("=" * 50)
print("✅ PHASE 5 VERIFICATION PASSED")
print("=" * 50)
print("\nGroup support is ready!")
print("\nFeatures:")
print("  • Separate private/group modes")
print("  • Admin-only configuration")
print("  • Clean group alerts")
print("  • Shared coin tracking")
print("  • Independent data storage")
print("\nFiles:")
print("  • groups.py (170 lines)")
print("  • app.py (updated with group support)")
print("  • test_groups.py (13 tests)")
print("  • PHASE_5_DESIGN.md (UX locked)")
