#!/usr/bin/env python3
"""
Core Tracker - Pure data operations
No UI. No Telegram. Just data.
"""

from storage import load_data, save_data
from wallets import load_wallets, save_wallets
from lists import load_lists, save_lists


class Tracker:
    """Pure data tracker - no UI dependencies"""
    
    @staticmethod
    def add_coin(user_id: str, coin_data: dict) -> bool:
        """Add a coin to tracking. Returns True if successful."""
        data = load_data()
        user_id = str(user_id)
        
        if user_id not in data:
            data[user_id] = {"coins": [], "profile": {"mode": "aggressive"}}
        
        # Ensure coins list exists
        if "coins" not in data[user_id]:
            data[user_id]["coins"] = []
        
        # Initialize required fields
        coin_data.setdefault("low_mc", coin_data.get("start_mc", 0))
        coin_data.setdefault("ath_mc", coin_data.get("start_mc", 0))
        coin_data.setdefault("history", [])
        coin_data.setdefault("triggered", {})
        
        data[user_id]["coins"].append(coin_data)
        save_data(data)
        return True
    
    @staticmethod
    def get_user_coins(user_id: str) -> list:
        """Get all coins for a user."""
        data = load_data()
        user_id = str(user_id)
        
        if user_id not in data:
            return []
        
        user_data = data[user_id]
        if isinstance(user_data, list):
            return user_data
        elif isinstance(user_data, dict):
            return user_data.get("coins", [])
        
        return []
    
    @staticmethod
    def remove_coin(user_id: str, ca: str) -> bool:
        """Remove a coin by contract address."""
        data = load_data()
        user_id = str(user_id)
        
        if user_id not in data:
            return False
        
        user_data = data[user_id]
        
        if isinstance(user_data, list):
            before = len(user_data)
            data[user_id] = [c for c in user_data if c.get("ca") != ca]
            after = len(data[user_id])
        elif isinstance(user_data, dict):
            coins = user_data.get("coins", [])
            before = len(coins)
            user_data["coins"] = [c for c in coins if c.get("ca") != ca]
            after = len(user_data["coins"])
        else:
            return False
        
        if after < before:
            save_data(data)
            return True
        
        return False
    
    @staticmethod
    def add_wallet(user_id: str, address: str, label: str = None) -> bool:
        """Add a wallet to track."""
        from wallets import add_wallet as wallet_add
        return wallet_add(user_id, address, label)
    
    @staticmethod
    def get_wallets(user_id: str) -> list:
        """Get all wallets for a user."""
        from wallets import get_wallets as wallet_get
        return wallet_get(user_id)
    
    @staticmethod
    def remove_wallet(user_id: str, address: str) -> bool:
        """Remove a wallet."""
        from wallets import remove_wallet as wallet_remove
        return wallet_remove(user_id, address)
    
    @staticmethod
    def get_user_lists(user_id: str) -> list:
        """Get all lists for a user."""
        from lists import get_user_lists as lists_get_user
        return lists_get_user(user_id)
    
    @staticmethod
    def create_list(user_id: str, name: str) -> bool:
        """Create a new list."""
        from lists import create_list as list_create
        return list_create(user_id, name)
    
    @staticmethod
    def get_lists(user_id: str) -> dict:
        """Get all lists for a user."""
        from lists import get_lists as lists_get
        return lists_get(user_id)
    
    @staticmethod
    def add_coin_to_list(user_id: str, list_name: str, ca: str) -> bool:
        """Add a coin to a list."""
        from lists import add_coin_to_list as list_add_coin
        return list_add_coin(user_id, list_name, ca)
    
    @staticmethod
    def delete_list(user_id: str, list_index: int) -> bool:
        """Delete a list by index."""
        from lists import delete_list as list_delete
        return list_delete(user_id, list_index)
