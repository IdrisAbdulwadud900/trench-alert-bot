"""Redis caching layer for API calls."""
import json
from typing import Optional, Dict
import time

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis not available - using in-memory cache")


class CacheLayer:
    """Cache layer with Redis fallback to in-memory dict."""
    
    def __init__(self):
        """Initialize cache layer."""
        self.redis_client = None
        self.memory_cache = {}
        self.cache_ttl = {}
        
        if REDIS_AVAILABLE:
            try:
                # Try to connect to Redis
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=0,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                # Test connection
                self.redis_client.ping()
                print("✅ Redis cache connected")
            except Exception as e:
                print(f"⚠️ Redis connection failed: {e}")
                print("   Using in-memory cache instead")
                self.redis_client = None
    
    def get(self, key: str) -> Optional[Dict]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                print(f"Cache get error: {e}")
        
        # Fallback to memory cache
        if key in self.memory_cache:
            # Check TTL
            if key in self.cache_ttl:
                if time.time() > self.cache_ttl[key]:
                    # Expired
                    del self.memory_cache[key]
                    del self.cache_ttl[key]
                    return None
            
            return self.memory_cache[key]
        
        return None
    
    def set(self, key: str, value: Dict, ttl: int = 30):
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl: Time to live in seconds (default 30)
        """
        if self.redis_client:
            try:
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value)
                )
                return
            except Exception as e:
                print(f"Cache set error: {e}")
        
        # Fallback to memory cache
        self.memory_cache[key] = value
        self.cache_ttl[key] = time.time() + ttl
    
    def delete(self, key: str):
        """Delete key from cache."""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                print(f"Cache delete error: {e}")
        
        # Also delete from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
        if key in self.cache_ttl:
            del self.cache_ttl[key]
    
    def clear(self):
        """Clear entire cache."""
        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception as e:
                print(f"Cache clear error: {e}")
        
        self.memory_cache.clear()
        self.cache_ttl.clear()
    
    def cleanup_expired(self):
        """Clean up expired entries from memory cache."""
        now = time.time()
        expired_keys = [
            key for key, expiry in self.cache_ttl.items()
            if now > expiry
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
            del self.cache_ttl[key]


# Global cache instance
cache = CacheLayer()


def get_cached_market_data(ca: str) -> Optional[Dict]:
    """Get cached market data for contract address."""
    return cache.get(f"market:{ca}")


def cache_market_data(ca: str, data: Dict, ttl: int = 30):
    """Cache market data for contract address."""
    cache.set(f"market:{ca}", data, ttl)


def invalidate_market_cache(ca: str):
    """Invalidate cached market data for contract address."""
    cache.delete(f"market:{ca}")
