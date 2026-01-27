import requests
import time

SUPPLY_CACHE = {}
RPC_URL = "https://api.mainnet-beta.solana.com"
MAX_RETRIES = 3

def get_token_supply_and_decimals(mint):
    if mint in SUPPLY_CACHE:
        return SUPPLY_CACHE[mint]

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenSupply",
        "params": [mint]
    }

    for attempt in range(MAX_RETRIES):
        try:
            r = requests.post(RPC_URL, json=payload, timeout=10)
            if r.status_code != 200:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(0.5 * (attempt + 1))
                continue

            result = r.json().get("result")
            if not result:
                return None

            value = result["value"]
            amount = int(value["amount"])
            decimals = int(value["decimals"])
            supply = amount / (10 ** decimals)

            SUPPLY_CACHE[mint] = (supply, decimals)
            return supply, decimals
        except (requests.RequestException, ValueError, KeyError) as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(0.5 * (attempt + 1))
            continue
    
    return None
