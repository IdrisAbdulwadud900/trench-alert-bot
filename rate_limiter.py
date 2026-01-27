"""Rate limiting system for API calls."""
import time
from typing import Dict, Optional
from collections import defaultdict, deque


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, requests_per_second: float = 10.0):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_second: Max requests allowed per second
        """
        self.rate = requests_per_second
        self.capacity = requests_per_second * 2  # Burst capacity
        self.tokens = self.capacity
        self.last_update = time.time()
        self.lock = False
    
    def _refill(self):
        """Refill tokens based on time elapsed."""
        now = time.time()
        elapsed = now - self.last_update
        
        # Add tokens based on elapsed time
        self.tokens = min(
            self.capacity,
            self.tokens + (elapsed * self.rate)
        )
        
        self.last_update = now
    
    def acquire(self, tokens: float = 1.0) -> bool:
        """
        Try to acquire tokens.
        
        Args:
            tokens: Number of tokens to acquire
        
        Returns:
            True if tokens acquired, False if rate limit exceeded
        """
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        return False
    
    def wait_and_acquire(self, tokens: float = 1.0, timeout: float = 5.0):
        """
        Wait until tokens are available or timeout.
        
        Args:
            tokens: Number of tokens to acquire
            timeout: Max seconds to wait
        
        Returns:
            True if acquired, False if timeout
        """
        start = time.time()
        
        while time.time() - start < timeout:
            if self.acquire(tokens):
                return True
            
            # Sleep for a fraction of expected wait time
            time.sleep(0.1)
        
        return False


class APIRateLimiter:
    """Rate limiter for different API endpoints."""
    
    def __init__(self):
        """Initialize API rate limiter with different limits per endpoint."""
        self.limiters = {
            "dexscreener": RateLimiter(requests_per_second=5.0),  # 5 req/s
            "solana_rpc": RateLimiter(requests_per_second=10.0),  # 10 req/s
            "wallet_alerts": RateLimiter(requests_per_second=2.0),  # 2 req/s
            "default": RateLimiter(requests_per_second=10.0)
        }
        
        # Per-user rate limits
        self.user_limits = defaultdict(lambda: RateLimiter(requests_per_second=2.0))
        
        # Request history for monitoring
        self.request_history = defaultdict(lambda: deque(maxlen=100))
    
    def can_request(self, endpoint: str, user_id: Optional[int] = None) -> bool:
        """
        Check if request is allowed.
        
        Args:
            endpoint: API endpoint name
            user_id: Optional user ID for per-user limiting
        
        Returns:
            True if request allowed
        """
        # Check endpoint limit
        limiter = self.limiters.get(endpoint, self.limiters["default"])
        if not limiter.acquire():
            return False
        
        # Check user limit if provided
        if user_id:
            user_limiter = self.user_limits[user_id]
            if not user_limiter.acquire():
                return False
        
        # Log request
        self.request_history[endpoint].append(time.time())
        
        return True
    
    def wait_for_request(
        self,
        endpoint: str,
        user_id: Optional[int] = None,
        timeout: float = 5.0
    ) -> bool:
        """
        Wait until request is allowed or timeout.
        
        Returns:
            True if allowed, False if timeout
        """
        limiter = self.limiters.get(endpoint, self.limiters["default"])
        
        if not limiter.wait_and_acquire(timeout=timeout):
            return False
        
        if user_id:
            user_limiter = self.user_limits[user_id]
            if not user_limiter.wait_and_acquire(timeout=timeout):
                return False
        
        self.request_history[endpoint].append(time.time())
        return True
    
    def get_stats(self, endpoint: str) -> Dict:
        """Get rate limiting stats for endpoint."""
        history = self.request_history[endpoint]
        
        if not history:
            return {
                "total_requests": 0,
                "requests_last_minute": 0,
                "requests_last_hour": 0
            }
        
        now = time.time()
        last_minute = sum(1 for t in history if now - t < 60)
        last_hour = sum(1 for t in history if now - t < 3600)
        
        return {
            "total_requests": len(history),
            "requests_last_minute": last_minute,
            "requests_last_hour": last_hour
        }


# Global rate limiter instance
api_limiter = APIRateLimiter()


def with_rate_limit(endpoint: str):
    """Decorator for rate-limited API calls."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if api_limiter.wait_for_request(endpoint):
                return func(*args, **kwargs)
            else:
                print(f"⚠️ Rate limit exceeded for {endpoint}")
                return None
        return wrapper
    return decorator
