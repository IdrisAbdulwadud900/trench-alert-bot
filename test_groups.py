#!/usr/bin/env python3
"""
Test groups functionality
"""

import os
from groups import (
    create_group,
    add_group_admin,
    get_group_admins,
    add_coin_to_group,
    get_group_coins,
    remove_coin_from_group,
    update_group_coin_alerts,
    update_group_coin_history,
    delete_group,
    get_all_group_ids
)

def test_groups():
    """Test basic group operations."""
    
    # Clean up any existing test file
    if os.path.exists("groups.json"):
        os.remove("groups.json")
    
    print("🧪 Testing Groups Operations...\n")
    
    group_id = "-100123456789"
    admin_1 = 12345678
    admin_2 = 87654321
    test_ca_1 = "EPjFWaLb3odcccccccccccccccccccccccccccccccc"
    test_ca_2 = "So11111111111111111111111111111111111111112"
    
    # Test 1: Create group with admin
    print("✅ Test 1: Create group with admin")
    success = create_group(group_id, admin_1)
    assert success, "Failed to create group"
    admins = get_group_admins(group_id)
    assert admin_1 in admins, f"Expected admin {admin_1} in group"
    print("   ✓ Group created with admin\n")
    
    # Test 2: Prevent duplicate group creation
    print("✅ Test 2: Prevent duplicate group creation")
    success = create_group(group_id, admin_1)
    assert not success, "Should reject duplicate group creation"
    print("   ✓ Duplicate creation prevented\n")
    
    # Test 3: Add second admin
    print("✅ Test 3: Add second admin")
    success = add_group_admin(group_id, admin_2)
    assert success, "Failed to add second admin"
    admins = get_group_admins(group_id)
    assert len(admins) == 2, f"Expected 2 admins, got {len(admins)}"
    assert admin_2 in admins, f"Expected admin {admin_2} in group"
    print("   ✓ Second admin added\n")
    
    # Test 4: Prevent duplicate admin
    print("✅ Test 4: Prevent duplicate admin")
    success = add_group_admin(group_id, admin_1)
    assert not success, "Should reject duplicate admin"
    admins = get_group_admins(group_id)
    assert len(admins) == 2, f"Expected still 2 admins, got {len(admins)}"
    print("   ✓ Duplicate admin prevented\n")
    
    # Test 5: Add coin to group
    print("✅ Test 5: Add coin to group")
    alerts = {"mc": 50000}
    success = add_coin_to_group(group_id, test_ca_1, alerts, 100000)
    assert success, "Failed to add coin to group"
    coins = get_group_coins(group_id)
    assert len(coins) == 1, f"Expected 1 coin, got {len(coins)}"
    assert coins[0]["ca"] == test_ca_1, "Coin CA mismatch"
    print("   ✓ Coin added to group\n")
    
    # Test 6: Prevent duplicate coin in group
    print("✅ Test 6: Prevent duplicate coin in group")
    success = add_coin_to_group(group_id, test_ca_1, alerts, 100000)
    assert not success, "Should reject duplicate coin"
    coins = get_group_coins(group_id)
    assert len(coins) == 1, f"Expected still 1 coin, got {len(coins)}"
    print("   ✓ Duplicate coin prevented\n")
    
    # Test 7: Add second coin
    print("✅ Test 7: Add second coin to group")
    success = add_coin_to_group(group_id, test_ca_2, {"ath": "reclaim"}, 80000)
    assert success, "Failed to add second coin"
    coins = get_group_coins(group_id)
    assert len(coins) == 2, f"Expected 2 coins, got {len(coins)}"
    print("   ✓ Second coin added\n")
    
    # Test 8: Update coin alerts
    print("✅ Test 8: Update coin alerts")
    new_alerts = {"mc": 45000, "ath": "reclaim"}
    success = update_group_coin_alerts(group_id, test_ca_1, new_alerts)
    assert success, "Failed to update alerts"
    coins = get_group_coins(group_id)
    matching_coin = [c for c in coins if c["ca"] == test_ca_1][0]
    assert matching_coin["alerts"] == new_alerts, "Alerts not updated"
    print("   ✓ Alerts updated successfully\n")
    
    # Test 9: Update coin history
    print("✅ Test 9: Update coin history")
    update_group_coin_history(group_id, test_ca_1, 75000, 105000, 70000)
    coins = get_group_coins(group_id)
    matching_coin = [c for c in coins if c["ca"] == test_ca_1][0]
    assert matching_coin["ath_mc"] == 105000, "ATH not updated"
    assert matching_coin["low_mc"] == 70000, "Low not updated"
    print("   ✓ History updated successfully\n")
    
    # Test 10: Remove coin from group
    print("✅ Test 10: Remove coin from group")
    success = remove_coin_from_group(group_id, test_ca_1)
    assert success, "Failed to remove coin"
    coins = get_group_coins(group_id)
    assert len(coins) == 1, f"Expected 1 coin after removal, got {len(coins)}"
    assert coins[0]["ca"] == test_ca_2, "Wrong coin removed"
    print("   ✓ Coin removed successfully\n")
    
    # Test 11: Get all group IDs
    print("✅ Test 11: Get all group IDs")
    group_2 = "-100987654321"
    create_group(group_2, admin_1)
    all_groups = get_all_group_ids()
    assert len(all_groups) == 2, f"Expected 2 groups, got {len(all_groups)}"
    assert group_id in all_groups, f"Expected {group_id} in groups"
    assert group_2 in all_groups, f"Expected {group_2} in groups"
    print("   ✓ All group IDs retrieved\n")
    
    # Test 12: Delete group
    print("✅ Test 12: Delete group")
    success = delete_group(group_id)
    assert success, "Failed to delete group"
    all_groups = get_all_group_ids()
    assert len(all_groups) == 1, f"Expected 1 group after deletion, got {len(all_groups)}"
    assert group_id not in all_groups, f"Group {group_id} should be deleted"
    print("   ✓ Group deleted successfully\n")
    
    # Test 13: Multiple groups with separate data
    print("✅ Test 13: Multiple groups maintain separate data")
    group_3 = "-100555666777"
    create_group(group_id, admin_1)  # Recreate group 1
    create_group(group_3, admin_2)
    add_coin_to_group(group_id, test_ca_1, {"mc": 50000}, 100000)
    add_coin_to_group(group_3, test_ca_2, {"ath": "reclaim"}, 80000)
    
    coins_g1 = get_group_coins(group_id)
    coins_g3 = get_group_coins(group_3)
    
    assert len(coins_g1) == 1, f"Group 1 should have 1 coin"
    assert len(coins_g3) == 1, f"Group 3 should have 1 coin"
    assert coins_g1[0]["ca"] == test_ca_1, "Group 1 has wrong coin"
    assert coins_g3[0]["ca"] == test_ca_2, "Group 3 has wrong coin"
    print("   ✓ Multiple groups maintain separate data\n")
    
    print("=" * 50)
    print("✅ ALL TESTS PASSED")
    print("=" * 50)

if __name__ == "__main__":
    test_groups()
