# ⚠️ NOTE: This file is deprecated.
# All bot logic has been consolidated into app.py
# Use app.py instead - it's the main entry point.

from storage import get_all_coins, remove_coin
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config import BOT_TOKEN
from storage import add_coin
from mc import get_market_cap

user_state = {}

def get_token_data(ca):
    """Get token data (market cap) for a contract address."""
    return get_market_cap(ca)

async def list_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = get_all_coins()

    if user_id not in data or not data[user_id]:
        await update.message.reply_text("You are not monitoring any coins.")
        return

    msg = "📊 Monitored coins:\n\n"

    for i, coin in enumerate(data[user_id], start=1):
        msg += (
            f"{i}. {coin['ca']}\n"
            f"Start MC: {int(coin['start_mc'])}\n"
            f"Alert MC: {int(coin['alert_mc'])}\n"
            f"Alert DD: {coin['alert_dd']}%\n"
            f"Alert X: {coin['alert_x']}x\n\n"
        )

    await update.message.reply_text(msg)
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /remove <contract_address>")
        return

    ca = context.args[0]
    user_id = update.effective_user.id

    success = remove_coin(user_id, ca)

    if success:
        await update.message.reply_text("Coin removed from monitoring.")
    else:
        await update.message.reply_text("Coin not found.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome.\nSend /add to monitor a coin."
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_state[update.effective_user.id] = {}
    await update.message.reply_text("Send token contract address:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    state = user_state.get(user_id, {})

    if "ca" not in state:
        state["ca"] = text
        token = get_token_data(text)
        if not token or not token["mc"]:
            await update.message.reply_text("Invalid token. Try again.")
            return
        state["start_mc"] = token["mc"]
        await update.message.reply_text(
            f"Start MC detected: {int(token['mc'])}\nSend alert MC:"
        )

    elif "alert_mc" not in state:
        state["alert_mc"] = float(text)
        await update.message.reply_text("Send drawdown % (e.g. 80):")

    elif "alert_dd" not in state:
        state["alert_dd"] = float(text)
        await update.message.reply_text("Send X multiple (e.g. 5):")

    elif "alert_x" not in state:
        state["alert_x"] = float(text)

        coin_data = {
            "ca": state["ca"],
            "start_mc": state["start_mc"],
            "alert_mc": state["alert_mc"],
            "alert_dd": state["alert_dd"],
            "alert_x": state["alert_x"],
            "triggered": {"mc": False, "dd": False, "x": False}
        }

        add_coin(user_id, coin_data)
        user_state.pop(user_id)

        await update.message.reply_text("Coin added. Monitoring started.")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("list", list_coins))
    app.add_handler(CommandHandler("remove", remove))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
