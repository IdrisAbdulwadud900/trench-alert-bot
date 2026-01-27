import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY", "PASTE_YOUR_BIRDEYE_KEY")
CHAIN = "solana"
