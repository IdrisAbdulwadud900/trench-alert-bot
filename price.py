import requests
import time
from rate_limiter import with_rate_limit

MAX_RETRIES = 3

@with_rate_limit("dexscreener")
def get_token_price_usd(ca):
    """Fetch token price with retry logic and timeout protection."""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
    
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, timeout=10)

            if r.status_code != 200:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(0.5 * (attempt + 1))
                continue

            data = r.json()
            pairs = data.get("pairs")
            if not pairs:
                return None

            pair = max(
                pairs,
                key=lambda p: p.get("liquidity", {}).get("usd", 0)
            )

            price = pair.get("priceUsd")
            if not price:
                return None

            liquidity = pair.get("liquidity", {}).get("usd", 0)
            if liquidity < 1000:
                return None

            return {
                "price": float(price),
                "liquidity": liquidity,
                "volume_24h": float(pair.get("volume", {}).get("h24", 0))
            }
        except (requests.RequestException, ValueError, KeyError, AttributeError) as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(0.5 * (attempt + 1))
            continue
    
    return None
