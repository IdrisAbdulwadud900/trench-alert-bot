#!/usr/bin/env python3
"""
Test lists functionality
"""

import os
from lists import (
    create_list,
    add_coin_to_list,
    get_lists,
    delete_list,
    remove_coin_from_list
)

def test_lists():
    """Test basic list operations."""
    
    # Clean up any existing test file
    if os.path.exists("lists.json"):
        os.remove("lists.json")
    
    print("🧪 Testing Lists Operations...\n")
    
    user_id = 12345
    test_ca_1 = "EPjFWaLb3odcccccccccccccccccccccccccccccccc"
    test_ca_2 = "So11111111111111111111111111111111111111112"
    
    # Test 1: Create list
    print("✅ Test 1: Create list")
    success = create_list(user_id, "AI")
    assert success, "Failed to create list"
    lists = get_lists(user_id)
    assert "AI" in lists, f"Expected 'AI' in lists, got {lists.keys()}"
    print("   ✓ List created successfully\n")
    
    # Test 2: Prevent duplicate list names
    print("✅ Test 2: Prevent duplicate list names")
    success = create_list(user_id, "AI")
    assert not success, "Should reject duplicate list name"
    lists = get_lists(user_id)
    assert len(lists) == 1, f"Expected 1 list, got {len(lists)}"
    print("   ✓ Duplicates correctly rejected\n")
    
    # Test 3: Add coin to list
    print("✅ Test 3: Add coin to list")
    success = add_coin_to_list(user_id, "AI", test_ca_1)
    assert success, "Failed to add coin to list"
    lists = get_lists(user_id)
    assert test_ca_1 in lists["AI"]["coins"], f"Expected CA in list"
    assert len(lists["AI"]["coins"]) == 1, f"Expected 1 coin, got {len(lists['AI']['coins'])}"
    print("   ✓ Coin added successfully\n")
    
    # Test 4: Add second coin
    print("✅ Test 4: Add second coin to list")
    success = add_coin_to_list(user_id, "AI", test_ca_2)
    assert success, "Failed to add second coin"
    lists = get_lists(user_id)
    assert len(lists["AI"]["coins"]) == 2, f"Expected 2 coins, got {len(lists['AI']['coins'])}"
    print("   ✓ Second coin added successfully\n")
    
    # Test 5: Prevent duplicate coins in list
    print("✅ Test 5: Prevent duplicate coins in list")
    success = add_coin_to_list(user_id, "AI", test_ca_1)
    assert success, "Should add coin even if exists (idempotent)"
    lists = get_lists(user_id)
    assert len(lists["AI"]["coins"]) == 2, f"Expected 2 coins (no duplicates), got {len(lists['AI']['coins'])}"
    print("   ✓ Duplicate coins prevented\n")
    
    # Test 6: Create multiple lists
    print("✅ Test 6: Create multiple lists")
    create_list(user_id, "Gaming")
    create_list(user_id, "DeFi")
    lists = get_lists(user_id)
    assert len(lists) == 3, f"Expected 3 lists, got {len(lists)}"
    print("   ✓ Multiple lists created successfully\n")
    
    # Test 7: Add coins to different lists
    print("✅ Test 7: Add coins to different lists")
    add_coin_to_list(user_id, "Gaming", test_ca_1)
    add_coin_to_list(user_id, "DeFi", test_ca_2)
    lists = get_lists(user_id)
    assert len(lists["AI"]["coins"]) == 2, "AI list should have 2 coins"
    assert len(lists["Gaming"]["coins"]) == 1, "Gaming list should have 1 coin"
    assert len(lists["DeFi"]["coins"]) == 1, "DeFi list should have 1 coin"
    print("   ✓ Coins added to different lists correctly\n")
    
    # Test 8: Remove coin from list
    print("✅ Test 8: Remove coin from list")
    success = remove_coin_from_list(user_id, "AI", test_ca_1)
    assert success, "Failed to remove coin"
    lists = get_lists(user_id)
    assert len(lists["AI"]["coins"]) == 1, f"Expected 1 coin after removal, got {len(lists['AI']['coins'])}"
    assert test_ca_1 not in lists["AI"]["coins"], "Coin should be removed"
    assert test_ca_2 in lists["AI"]["coins"], "Other coin should remain"
    print("   ✓ Coin removed successfully\n")
    
    # Test 9: Delete list
    print("✅ Test 9: Delete list")
    success = delete_list(user_id, "Gaming")
    assert success, "Failed to delete list"
    lists = get_lists(user_id)
    assert "Gaming" not in lists, "Gaming list should be deleted"
    assert len(lists) == 2, f"Expected 2 lists, got {len(lists)}"
    print("   ✓ List deleted successfully\n")
    
    # Test 10: Multiple users
    print("✅ Test 10: Multiple users have separate lists")
    user_2 = 54321
    create_list(user_2, "AI")
    add_coin_to_list(user_2, "AI", test_ca_1)
    
    lists_user1 = get_lists(user_id)
    lists_user2 = get_lists(user_2)
    
    assert "AI" in lists_user1, "User 1 should have AI list"
    assert "AI" in lists_user2, "User 2 should have AI list"
    assert len(lists_user1["AI"]["coins"]) == 1, "User 1 AI list has 1 coin"
    assert len(lists_user2["AI"]["coins"]) == 1, "User 2 AI list has 1 coin"
    print("   ✓ Multiple users maintain separate lists\n")
    
    print("=" * 50)
    print("✅ ALL TESTS PASSED")
    print("=" * 50)

if __name__ == "__main__":
    test_lists()
