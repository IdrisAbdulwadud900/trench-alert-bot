from price import get_token_price_usd
from supply import get_token_supply_and_decimals
from cache_layer import get_cached_market_data, cache_market_data

def get_market_cap(ca):
    """Get market cap with comprehensive error handling and caching."""
    # Check cache first
    cached = get_cached_market_data(ca)
    if cached:
        return cached
    
    # Cache miss - fetch from API
    try:
        price_data = get_token_price_usd(ca)
        if not price_data:
            return None

        price = price_data.get("price")
        if not price or price <= 0:
            return None
            
        liquidity = price_data.get("liquidity", 0)
        volume_24h = price_data.get("volume_24h", 0)

        supply_data = get_token_supply_and_decimals(ca)
        if not supply_data:
            return None

        supply, decimals = supply_data
        
        if not supply or supply <= 0:
            return None
            
        mc = price * supply

        result = {
            "price": price,
            "liquidity": liquidity,
            "volume_24h": volume_24h,
            "supply": supply,
            "mc": mc
        }
        
        # Cache the result for 30 seconds
        cache_market_data(ca, result, ttl=30)
        
        return result
    except Exception as e:
        print(f"Error getting market cap for {ca}: {e}")
        return None
