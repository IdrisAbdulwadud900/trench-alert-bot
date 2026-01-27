#!/usr/bin/env python3
"""
Test wallet tracking functionality
"""

import json
import os
import tempfile
from wallets import add_wallet, get_wallets, remove_wallet, load_wallets, save_wallets

def test_wallet_operations():
    """Test basic wallet CRUD operations."""
    
    # Clean up any existing test file
    if os.path.exists("wallets.json"):
        os.remove("wallets.json")
    
    print("🧪 Testing Wallet Operations...\n")
    
    # Setup
    user_id = 12345
    test_address_1 = "9B5XlmKz2mP8jK4L9nOpQrStUvWxYzAbCdEfGhIjKl"
    test_address_2 = "4xY7QpRs9TuV1WxYzAbCdEfGhIjKlMnOpQrStUvWx"
    
    # Test 1: Add wallet
    print("✅ Test 1: Add first wallet")
    success = add_wallet(user_id, test_address_1, "Smart Money")
    assert success, "Failed to add first wallet"
    wallets = get_wallets(user_id)
    assert len(wallets) == 1, f"Expected 1 wallet, got {len(wallets)}"
    assert wallets[0]["address"] == test_address_1
    assert wallets[0]["label"] == "Smart Money"
    print("   ✓ First wallet added successfully\n")
    
    # Test 2: Add second wallet
    print("✅ Test 2: Add second wallet")
    success = add_wallet(user_id, test_address_2, "Dev Team")
    assert success, "Failed to add second wallet"
    wallets = get_wallets(user_id)
    assert len(wallets) == 2, f"Expected 2 wallets, got {len(wallets)}"
    print("   ✓ Second wallet added successfully\n")
    
    # Test 3: Prevent duplicates
    print("✅ Test 3: Prevent duplicate wallets")
    success = add_wallet(user_id, test_address_1, "Duplicate")
    assert not success, "Should reject duplicate wallet"
    wallets = get_wallets(user_id)
    assert len(wallets) == 2, f"Expected 2 wallets, got {len(wallets)}"
    print("   ✓ Duplicates correctly rejected\n")
    
    # Test 4: Get wallets
    print("✅ Test 4: Retrieve all wallets")
    wallets = get_wallets(user_id)
    assert len(wallets) == 2
    assert wallets[0]["label"] == "Smart Money"
    assert wallets[1]["label"] == "Dev Team"
    print("   ✓ All wallets retrieved correctly\n")
    
    # Test 5: Remove wallet
    print("✅ Test 5: Remove wallet")
    success = remove_wallet(user_id, test_address_1)
    assert success, "Failed to remove wallet"
    wallets = get_wallets(user_id)
    assert len(wallets) == 1, f"Expected 1 wallet, got {len(wallets)}"
    assert wallets[0]["address"] == test_address_2
    print("   ✓ Wallet removed successfully\n")
    
    # Test 6: Empty user
    print("✅ Test 6: Get wallets for user with no wallets")
    wallets = get_wallets(99999)
    assert wallets == [], f"Expected empty list, got {wallets}"
    print("   ✓ Empty user returns empty list\n")
    
    # Test 7: Multiple users
    print("✅ Test 7: Multiple users have separate wallets")
    user_2 = 54321
    add_wallet(user_2, test_address_1, "User 2 Wallet")
    
    wallets_user1 = get_wallets(user_id)
    wallets_user2 = get_wallets(user_2)
    
    assert len(wallets_user1) == 1, "User 1 should have 1 wallet"
    assert len(wallets_user2) == 1, "User 2 should have 1 wallet"
    assert wallets_user1[0]["label"] == "Dev Team"
    assert wallets_user2[0]["label"] == "User 2 Wallet"
    print("   ✓ Multiple users maintain separate wallets\n")
    
    print("=" * 50)
    print("✅ ALL TESTS PASSED")
    print("=" * 50)

if __name__ == "__main__":
    test_wallet_operations()
