import asyncio
import threading
from mc import get_market_cap
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, CHECK_INTERVAL
from storage import (
    add_coin, 
    get_user_coins, 
    save_data, 
    remove_coin,
    load_data,
    get_user_profile,
    get_all_coins,
    get_user_wallets,
    get_user_lists
)
from wallets import (
    add_wallet,
    get_wallets,
    remove_wallet
)
from lists import (
    create_list,
    add_coin_to_list,
    get_lists
)
from groups import (
    create_group,
    add_group_admin,
    get_group_admins,
    add_coin_to_group,
    get_group_coins,
    remove_coin_from_group,
    update_group_coin_alerts,
    update_group_coin_triggered,
    update_group_coin_history,
    get_all_group_ids
)
from intelligence import (
    update_coin_history,
    compute_range_position,
    detect_dump_stabilize_bounce,
    format_smart_alert,
    should_suppress_alert,
    get_range_description
)
from subscriptions import (
    get_user_tier,
    get_user_limits,
    can_add_coin,
    can_add_wallet,
    can_add_list,
    can_use_meta_alerts,
    can_use_wallet_alerts,
    get_upgrade_message,
    get_pricing_message
)
from meta import (
    analyze_list_performance,
    detect_list_heating,
    format_list_alert,
    get_top_performers_in_list
)
from onchain import (
    detect_wallet_buys,
    format_wallet_buy_alert
)

# Validate BOT_TOKEN
if not BOT_TOKEN:
    raise ValueError(
        "❌ BOT_TOKEN is not set!\n"
        "Please run: export BOT_TOKEN=your_token_here\n"
        "Then: python app.py"
    )
# -------------------------
# In-memory user state
# -------------------------
user_state = {}

# -------------------------
# Telegram commands
# -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main home screen - detects group vs private chat."""
    chat = update.effective_chat
    is_group = chat.type in ["group", "supergroup"]
    
    if is_group:
        # GROUP MODE
        group_id = str(chat.id)
        admin_id = update.effective_user.id
        
        # Initialize group if new
        create_group(group_id, admin_id)
        
        keyboard = [
            [InlineKeyboardButton("➕ Track Coin", callback_data="group_track_coin")],
            [InlineKeyboardButton("📊 Status", callback_data="group_status")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="group_help")]
        ]
        
        await update.message.reply_text(
            "🚨 Trench Alert Bot — Group Mode\n\n"
            "I monitor coins for this group\n"
            "and send alerts here.\n\n"
            "Only group admins can configure.\n"
            "Members can view status.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        # PRIVATE MODE (unchanged)
        keyboard = [
            [InlineKeyboardButton("➕ Track Coin", callback_data="home_track_coin")],
            [InlineKeyboardButton("👀 Watch Wallets", callback_data="home_wallets")],
            [InlineKeyboardButton("📂 Lists / Meta", callback_data="home_lists")],
            [InlineKeyboardButton("📊 Dashboard", callback_data="home_dashboard")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="home_help")]
        ]
        
        await update.message.reply_text(
            "🚨 Trench Alert Bot\n\n"
            "Track coins. Track wallets.\n"
            "Get smart alerts.\n\n"
            "What do you want to do?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Legacy /add command - redirect to home screen."""
    await start(update, context)

async def list_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    
    user_data = data.get(user_id)
    if not user_data:
        await update.message.reply_text("You are not monitoring any coins.")
        return
    
    # Handle both formats
    if isinstance(user_data, list):
        coins = user_data
    else:
        coins = user_data.get("coins", [])

    if not coins:
        await update.message.reply_text("You are not monitoring any coins.")
        return

    msg = "📊 Monitored coins:\n\n"

    for i, coin in enumerate(coins, start=1):
        alerts = coin.get("alerts", {})
        ath = coin.get("ath_mc", coin.get("start_mc", 0))
        low = coin.get("low_mc", coin.get("start_mc", 0))
        mc = coin.get("start_mc", 0)
        
        range_pos = compute_range_position(mc, low, ath)
        range_desc = get_range_description(range_pos)
        
        alerts_str = format_active_alerts(alerts)
        msg += (
            f"{i}. {coin['ca']}\n"
            f"Start MC: ${int(coin['start_mc']):,}\n"
            f"Range: {range_desc}\n"
            f"Alerts: {alerts_str}\n\n"
        )

    await update.message.reply_text(msg)

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /remove <contract_address>")
        return

    ca = context.args[0]
    user_id = update.effective_user.id

    if remove_coin(user_id, ca):
        await update.message.reply_text("Coin removed.")
    else:
        await update.message.reply_text("Coin not found.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    is_group = chat.type in ["group", "supergroup"]
    
    if is_group:
        # GROUP STATUS
        group_id = str(chat.id)
        coins = get_group_coins(group_id)
        
        if not coins:
            await update.message.reply_text("No coins tracked for this group yet.")
            return
        
        msg = "📊 Group Status\n\n"
        
        for coin in coins:
            try:
                token = get_market_cap(coin["ca"])
                if not token:
                    continue
                
                mc = token["mc"]
                alerts = coin.get("alerts", {})
                
                msg += f"🪙 {coin['ca'][:6]}...\n"
                msg += f"MC: ${int(mc):,}\n"
                
                alerts_str = format_active_alerts(alerts)
                msg += f"Alerts: {alerts_str}\n\n"
            
            except Exception as e:
                print(f"Status error: {e}")
                continue
        
        await update.message.reply_text(msg)
    
    else:
        # PRIVATE STATUS (unchanged)
        user_id = str(update.effective_user.id)
        data = load_data()
        
        user_data = data.get(user_id)
        if not user_data:
            await update.message.reply_text("No active coins.")
            return
        
        # Handle both formats
        if isinstance(user_data, list):
            coins = user_data
        else:
            coins = user_data.get("coins", [])

        if not coins:
            await update.message.reply_text("No active coins.")
            return

        msg = "📊 Live Status\n\n"

        for coin in coins:
            try:
                token = get_market_cap(coin["ca"])
                if not token:
                    continue

                mc = token["mc"]
                start = coin["start_mc"]
                ath = coin.get("ath_mc", start)
                low = coin.get("low_mc", start)
                
                dd = ((start - mc) / start) * 100
                x = mc / start
                
                # Compute range position
                range_pos = compute_range_position(mc, low, ath)
                range_desc = get_range_description(range_pos)
                
                alerts = coin.get("alerts", {})

                msg += (
                    f"🪙 {coin['ca'][:6]}...\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"💰 MC: ${int(mc):,}\n"
                    f"📉 DD: {dd:.1f}%\n"
                    f"🚀 X: {x:.2f}x\n"
                    f"🔥 ATH: ${int(ath):,}\n"
                    f"📊 Position: {range_desc}\n"
                    f"🟢 Range: {low:.0f} → {ath:.0f}\n\n"
                    f"🔔 Alerts:\n"
                )

                for k, v in alerts.items():
                    msg += f"• {k.upper()}: {v}\n"

                msg += "\n"
            
            except Exception as e:
                print(f"Status fetch error: {e}")
                continue

        await update.message.reply_text(msg)


async def pricing_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pricing and subscription tiers."""
    await update.message.reply_text(get_pricing_message())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Trench Alert — Help\n\n"
        "➕ /add\n"
        "Add a new coin to monitor\n\n"
        "📊 /status\n"
        "View live market cap, drawdown & X\n\n"
        "📋 /list\n"
        "See all monitored coins\n\n"
        "⚙️ /mode\n"
        "Choose alert profile (conservative/aggressive/sniper)\n\n"
        "❌ /remove <CA>\n"
        "Stop monitoring a coin\n\n"
        "Alert types:\n"
        "• Market Cap → alert at a target MC\n"
        "• % Change → alert on up/down move\n"
        "• X Multiple → alert on X gain\n"
        "• ATH Reclaim → alert on recovery\n\n"
        "Profiles:\n"
        "🐢 Conservative: High quality only\n"
        "⚡ Aggressive: Balanced (default)\n"
        "🧠 Sniper: All signals, noisy\n\n"
        "Tip:\n"
        "Smart alerts show context, not just numbers"
    )

async def mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Let user choose alert profile."""
    keyboard = [
        [InlineKeyboardButton("🐢 Conservative", callback_data="mode_conservative")],
        [InlineKeyboardButton("⚡ Aggressive", callback_data="mode_aggressive")],
        [InlineKeyboardButton("🧠 Sniper", callback_data="mode_sniper")]
    ]
    
    await update.message.reply_text(
        "Choose your alert profile:\n\n"
        "🐢 Conservative: Higher quality, fewer alerts\n"
        "⚡ Aggressive: Balanced (default)\n"
        "🧠 Sniper: All signals, more noise",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# -------------------------
# Helper functions
# -------------------------
def get_token_data(ca):
    """Get token data (market cap) for a contract address."""
    return get_market_cap(ca)

def format_active_alerts(alerts):
    """Format active alerts for display."""
    if not alerts:
        return "No alerts set"
    
    lines = []
    if "mc" in alerts:
        lines.append(f"• MC ≤ ${int(alerts['mc']):,}")
    if "pct" in alerts:
        lines.append(f"• % ±{int(alerts['pct'])}%")
    if "x" in alerts:
        lines.append(f"• X ≥ {alerts['x']:.1f}x")
    if alerts.get("reclaim"):
        lines.append("• ATH reclaim (95%)")
    
    return "\n".join(lines) if lines else "No alerts set"

# -------------------------
# Text input handler
# -------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in user_state:
        return

    state = user_state[user_id]
    step = state.get("step")

    # ========================
    # WALLET TRACKING INPUT
    # ========================
    if step == "wallet_address":
        from storage import add_wallet
        # Validate address format (Solana addresses are 32-44 chars, base58)
        text = text.strip()
        
        if len(text) < 32 or len(text) > 44:
            await update.message.reply_text("❌ Invalid address length. Solana addresses are 32-44 characters.")
            return
        
        # Basic base58 validation (no 0, O, I, l)
        if any(char in text for char in ['0', 'O', 'I', 'l']):
            await update.message.reply_text("❌ Invalid address format. Solana addresses use base58 (no 0, O, I, l).")
            return
        
        state["wallet_address"] = text
        state["step"] = "wallet_label"
        await update.message.reply_text(
            "✅ Address saved\n\n"
            "Give this wallet a name (optional):\n\n"
            "e.g., Smart Money, Dev Wallet, Insider #1\n\n"
            "Or type 'skip' to use default"
        )
        return
    
    elif step == "wallet_label":
        from storage import add_wallet
        text = text.strip()
        
        # Validate label length
        if text.lower() != "skip" and len(text) > 50:
            await update.message.reply_text("❌ Label too long. Max 50 characters.")
            return
            
        label = None if text.lower() == "skip" else text
        wallet_addr = state.get("wallet_address")
        
        if add_wallet(user_id, wallet_addr, label):
            label = label or f"Wallet {len(get_user_wallets(user_id))}"
            await update.message.reply_text(
                f"✅ Wallet Added\n\n"
                f"Name: {label}\n"
                f"Address: {wallet_addr[:10]}...{wallet_addr[-8:]}\n\n"
                f"Will alert on buys into your tracked coins."
            )
        else:
            await update.message.reply_text("❌ Wallet already added.")
        
        user_state.pop(user_id)
        return
    
    # ========================
    # WALLET MINIMUM BUY SIZE
    # ========================
    elif step == "wallet_min_buy":
        text = text.strip()
        
        if text.lower() == "skip":
            state["alerts"]["wallets"]["min_buy_usd"] = 300
        else:
            try:
                min_buy = float(text)
                if min_buy < 0:
                    await update.message.reply_text("❌ Amount must be positive. Try again or type 'skip'.")
                    return
                if min_buy > 1_000_000:
                    await update.message.reply_text("❌ Amount too large. Max $1,000,000. Try again.")
                    return
                state["alerts"]["wallets"]["min_buy_usd"] = min_buy
            except ValueError:
                await update.message.reply_text(
                    "❌ Invalid amount. Send a number (e.g., 500) or 'skip'."
                )
                return
        
        # Return to alert selection
        state["step"] = "choose_alert"
        min_buy_amount = state["alerts"]["wallets"]["min_buy_usd"]
        await update.message.reply_text(
            f"✅ Wallet Alerts Configured\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Wallets: {len(state['alerts']['wallets']['addresses'])} selected\n"
            f"Minimum buy: ${int(min_buy_amount):,}\n\n"
            f"Add more alerts or tap Done"
        )
        return
    
    # ========================
    # LISTS & NARRATIVES INPUT
    # ========================
    elif step == "list_name":
        text = text.strip()
        
        # Validate list name
        if len(text) < 1:
            await update.message.reply_text("❌ List name cannot be empty.")
            return
        if len(text) > 30:
            await update.message.reply_text("❌ List name too long. Max 30 characters.")
            return
        
        # Prevent special characters that could cause issues
        if any(char in text for char in ['"', "'", "\\", "/", "<", ">"]):
            await update.message.reply_text("❌ List name contains invalid characters.")
            return
            
        list_name = text
        
        if create_list(user_id, list_name):
            state["list_name"] = list_name
            state["step"] = "list_add_coins"
            await update.message.reply_text(
                f"✅ List Created: {list_name}\n\n"
                f"Send coin contract addresses (one by one)\n\n"
                f"Or type 'done' when finished"
            )
        else:
            await update.message.reply_text(f"❌ List '{list_name}' already exists.")
            user_state.pop(user_id)
        return
    
    elif step == "list_add_coins":
        text = text.strip()
        
        if text.lower() == "done":
            list_name = state.get("list_name")
            user_lists = get_lists(user_id)
            coin_count = len(user_lists.get(list_name, []))
            
            await update.message.reply_text(
                f"✅ List Complete: {list_name}\n\n"
                f"Coins added: {coin_count}\n\n"
                f"You can now track meta rotation and narrative themes."
            )
            user_state.pop(user_id)
            return
        
        # Validate CA format (Solana address)
        if len(text) < 32 or len(text) > 44:
            await update.message.reply_text("❌ Invalid address length. Send a valid CA or type 'done'")
            return
        
        if any(char in text for char in ['0', 'O', 'I', 'l']):
            await update.message.reply_text("❌ Invalid address format (base58). Send a valid CA or type 'done'")
            return
        
        list_name = state.get("list_name")
        if add_coin_to_list(user_id, list_name, text):
            user_lists = get_lists(user_id)
            coin_count = len(user_lists.get(list_name, []))
            await update.message.reply_text(
                f"✅ Added to {list_name}\n"
                f"Coins: {coin_count}\n\n"
                f"Send more or type 'done'"
            )
        else:
            await update.message.reply_text("❌ Failed to add coin or already in list.")
        return
    
    # ========================
    # GROUP COIN TRACKING
    # ========================
    elif step == "group_ca":
        # Validate CA format (basic)
        if len(text) < 30 or len(text) > 50:
            await update.message.reply_text("❌ Invalid address. Paste a full contract address.")
            return
        
        group_id = state.get("group_id")
        state["ca"] = text
        state["step"] = "group_alerts"
        
        # Get token info to confirm
        try:
            token = get_market_cap(text)
            if token:
                mc = token["mc"]
                state["start_mc"] = mc
                await update.message.reply_text(
                    f"✅ Token found!\n\n"
                    f"MC: ${int(mc):,}\n\n"
                    f"Now set alerts (or skip).\n"
                    f"Send: mc:50000 for MC alert, or 'none'"
                )
            else:
                await update.message.reply_text("❌ Token not found. Check CA and try again.")
                user_state.pop(user_id)
        except Exception as e:
            print(f"Token lookup error: {e}")
            await update.message.reply_text("❌ Error looking up token.")
            user_state.pop(user_id)
        return
    
    elif step == "group_alerts":
        group_id = state.get("group_id")
        ca = state.get("ca")
        start_mc = state.get("start_mc", 0)
        
        if text.lower() == "none":
            alerts = {}
        else:
            # Parse alert format: "mc:50000" or "ath:reclaim"
            try:
                parts = text.split(":")
                if parts[0] == "mc":
                    alerts = {"mc": float(parts[1])}
                elif parts[0] == "ath":
                    alerts = {"reclaim": True}
                else:
                    alerts = {}
            except:
                alerts = {}
        
        # Add coin to group
        if add_coin_to_group(group_id, ca, alerts, start_mc):
            await update.message.reply_text(
                f"✅ Coin added to group tracking\n\n"
                f"CA: {ca[:10]}...\n"
                f"Alerts: {format_active_alerts(alerts) if alerts else 'None'}"
            )
        else:
            await update.message.reply_text("❌ Coin already tracked in this group.")
        
        user_state.pop(user_id)
        return

    # Handle step-specific input

    if step == "set_alert_mc":
        try:
            mc_alert = float(text)
            state["alerts"]["mc"] = mc_alert
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Send a valid market cap:")
            return
        alerts_display = format_active_alerts(state["alerts"])
        mc_str = f"${int(mc_alert):,}" if mc_alert >= 1 else f"${mc_alert:.2f}"
        await update.message.reply_text(
            f"✅ 📉 Market Cap Alert Set\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Threshold: {mc_str}\n\n"
            f"Active alerts:\n"
            f"{alerts_display}\n\n"
            f"Add more alerts or tap Done"
        )
        state["step"] = "choose_alert"
        return

    elif step == "set_alert_pct":
        try:
            pct_alert = float(text)
            state["alerts"]["pct"] = pct_alert
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Send a valid percentage:")
            return
        alerts_display = format_active_alerts(state["alerts"])
        await update.message.reply_text(
            f"✅ 📈 % Move Alert Set\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Threshold: ±{pct_alert:.1f}%\n\n"
            f"Active alerts:\n"
            f"{alerts_display}\n\n"
            f"Add more alerts or tap Done"
        )
        state["step"] = "choose_alert"
        return

    elif step == "set_alert_x":
        try:
            x_alert = float(text)
            state["alerts"]["x"] = x_alert
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Send a valid X multiple:")
            return
        alerts_display = format_active_alerts(state["alerts"])
        await update.message.reply_text(
            f"✅ 🚀 X Multiple Alert Set\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Threshold: {x_alert:.1f}x\n\n"
            f"Active alerts:\n"
            f"{alerts_display}\n\n"
            f"Add more alerts or tap Done"
        )
        state["step"] = "choose_alert"
        return

    if "ca" not in state:
        # Step 1: User sends contract address
        try:
            token = get_token_data(text)
            if not token or not token.get("mc"):
                await update.message.reply_text("❌ Invalid token. Send CA again.")
                return
        except Exception as e:
            print(f"Token lookup error: {e}")
            await update.message.reply_text("❌ Error fetching token. Try again.")
            return

        # Step 2: Auto-detect and display token info
        state["ca"] = text
        state["start_mc"] = token["mc"]
        state["alerts"] = {}
        
        mc = token.get("mc", 0)
        liquidity = token.get("liquidity", 0)
        
        # Format numbers
        mc_str = f"${int(mc):,}" if mc >= 1 else f"${mc:.2f}"
        liq_str = f"${int(liquidity):,}" if liquidity >= 1 else f"${liquidity:.2f}"
        
        # Show detected info
        info_msg = (
            f"✅ 🪙 Token Detected\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Market Cap: {mc_str}\n"
            f"💧 Liquidity: {liq_str}\n\n"
            f"What do you want to track?\n"
            f"(Select multiple)"
        )
        
        keyboard = [
            [InlineKeyboardButton("📉 Market Cap Levels", callback_data="alert_mc")],
            [InlineKeyboardButton("📈 % Moves", callback_data="alert_pct")],
            [InlineKeyboardButton("� Wallet Buys", callback_data="alert_wallet")],
            [InlineKeyboardButton("�🚀 X Multiples", callback_data="alert_x")],
            [InlineKeyboardButton("🔥 ATH Reclaim", callback_data="alert_reclaim")],
            [InlineKeyboardButton("✅ Done", callback_data="alert_done")]
        ]

        await update.message.reply_text(
            info_msg,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        state["step"] = "choose_alert"

    elif "alert_mc" not in state:
        try:
            state["alert_mc"] = float(text)
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Send market cap:")
            return
        await update.message.reply_text("Send drawdown %:")

    elif "alert_dd" not in state:
        try:
            state["alert_dd"] = float(text)
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Send percentage:")
            return
        await update.message.reply_text("Send X multiple:")

    elif "alert_x" not in state:
        try:
            state["alert_x"] = float(text)
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Send X multiple:")
            return

        coin_data = {
            "ca": state["ca"],
            "start_mc": state["start_mc"],
            "ath_mc": state["start_mc"],
            "alert_mc": state["alert_mc"],
            "alert_dd": state["alert_dd"],
            "alert_x": state["alert_x"],
            "alert_reclaim_pct": 80,
            "triggered": {
                "mc": False,
                "dd": False,
                "x": False,
                "reclaim": False
            }
        }

        add_coin(user_id, coin_data)
        user_state.pop(user_id)

        await update.message.reply_text("✅ Coin added. Monitoring started.")


# ========================
# GROUP HANDLERS
# ========================

async def handle_group_track_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle group track coin button."""
    query = update.callback_query
    await query.answer()
    
    # Admin check
    if not await is_admin(update, context):
        await query.message.reply_text(
            "⚠️ Only group admins can configure alerts."
        )
        return
    
    group_id = str(update.effective_chat.id)
    user_id = query.from_user.id
    
    user_state[user_id] = {
        "step": "group_ca",
        "group_id": group_id
    }
    
    await query.message.reply_text(
        "Send token contract address:"
    )

async def handle_group_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle group status button."""
    query = update.callback_query
    await query.answer()
    
    group_id = str(update.effective_chat.id)
    coins = get_group_coins(group_id)
    
    if not coins:
        await query.message.reply_text("No coins tracked yet.")
        return
    
    msg = "📊 Group Status\n\n"
    
    for coin in coins:
        try:
            token = get_market_cap(coin["ca"])
            if not token:
                continue
            
            mc = token["mc"]
            alerts = coin.get("alerts", {})
            
            msg += f"🪙 {coin['ca'][:6]}...\n"
            msg += f"MC: ${int(mc):,}\n"
            
            alerts_str = format_active_alerts(alerts)
            msg += f"Alerts: {alerts_str}\n\n"
        
        except Exception as e:
            print(f"Group status error: {e}")
            continue
    
    await query.message.reply_text(msg)

async def handle_group_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle group help button."""
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(
        "ℹ️ Group Alert Bot\n\n"
        "This bot tracks coins and sends alerts "
        "to the group.\n\n"
        "👥 Members can:\n"
        "• View status (/status)\n"
        "• See active alerts\n\n"
        "👨‍💼 Admins can:\n"
        "• Add coins to track\n"
        "• Configure alerts\n"
        "• Set alert rules\n\n"
        "Alert Types:\n"
        "• Market Cap → alert at target MC\n"
        "• % Change → alert on ±move\n"
        "• ATH Reclaim → recovery signal\n\n"
        "Alerts are sent to the group only."
    )


# -------------------------
# Button callback handler
# -------------------------
async def alert_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    choice = query.data
    
    # GROUP CALLBACKS
    if choice == "group_track_coin":
        await handle_group_track_coin(update, context)
        return
    elif choice == "group_status":
        await handle_group_status(update, context)
        return
    elif choice == "group_help":
        await handle_group_help(update, context)
        return
    
    # HOME SCREEN CALLBACKS
    if choice == "home_track_coin":
        # Check tier limits first
        user_coins = get_user_coins(user_id)
        if not can_add_coin(user_id, len(user_coins)):
            await query.message.reply_text(get_upgrade_message(user_id, "max_coins"))
            return
        user_state[user_id] = {}
        await query.message.reply_text("Send token contract address:")
        return
    
    elif choice == "home_wallets":
        # Check wallet limits
        wallets = get_wallets(user_id)
        if not can_add_wallet(user_id, len(wallets)) and len(wallets) >= 1:
            await query.message.reply_text(get_upgrade_message(user_id, "max_wallets"))
            return
        
        if not wallets:
            msg = "👀 Watch Wallets\n\nNo wallets tracked yet.\nAdd a wallet to get started."
            keyboard = [
                [InlineKeyboardButton("➕ Add Wallet", callback_data="wallet_add")],
                [InlineKeyboardButton("◀ Back", callback_data="home_back")]
            ]
        else:
            msg = f"👀 Watch Wallets\n\nYou have {len(wallets)} wallet(s):\n\n"
            for w in wallets:
                msg += f"• {w.get('label', 'Unnamed')} ({w['address'][:8]}...)\n"
            keyboard = [
                [InlineKeyboardButton("➕ Add Wallet", callback_data="wallet_add")],
                [InlineKeyboardButton("🗑️ Remove Wallet", callback_data="wallet_remove")],
                [InlineKeyboardButton("◀ Back", callback_data="home_back")]
            ]
        
        await query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    elif choice == "home_dashboard":
        # Show dashboard with user stats
        coins = get_user_coins(user_id)
        wallets = get_wallets(user_id)
        user_lists = get_lists(user_id)
        tier = get_user_tier(user_id)
        
        msg = (
            f"📊 Dashboard\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Tier: {tier.title()}\n\n"
            f"📈 Tracking: {len(coins)} coins\n"
            f"👀 Wallets: {len(wallets)}\n"
            f"📂 Lists: {len(user_lists)}\n\n"
            f"Use /pricing to see tier limits."
        )
        keyboard = [[InlineKeyboardButton("◀ Back", callback_data="home_back")]]
        await query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    elif choice == "home_help":
        msg = (
            "ℹ️ Help\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "➕ Track Coin — Monitor MC, price, ATH\n"
            "👀 Watch Wallets — Get buy alerts\n"
            "📂 Lists/Meta — Group by narrative\n"
            "📊 Dashboard — View your stats\n\n"
            "Commands:\n"
            "/start — Home menu\n"
            "/pricing — View tiers\n"
            "/list — List tracked coins\n"
            "/help — Show this help\n"
        )
        keyboard = [[InlineKeyboardButton("◀ Back", callback_data="home_back")]]
        await query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    elif choice == "home_back":
        # Go back to home screen
        keyboard = [
            [InlineKeyboardButton("➕ Track Coin", callback_data="home_track_coin")],
            [InlineKeyboardButton("👀 Watch Wallets", callback_data="home_wallets")],
            [InlineKeyboardButton("📂 Lists / Meta", callback_data="home_lists")],
            [InlineKeyboardButton("📊 Dashboard", callback_data="home_dashboard")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="home_help")]
        ]
        await query.message.reply_text(
            "🚨 Trench Alert Bot\n\n"
            "Track coins. Track wallets.\n"
            "Get smart alerts.\n\n"
            "What do you want to do?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # MAIN ACTIONS
    if choice == "action_track":
        # Check tier limits
        user_coins = get_user_coins(user_id)
        if not can_add_coin(user_id, len(user_coins)):
            await query.message.reply_text(get_upgrade_message(user_id, "max_coins"))
            return
        
        user_state[user_id] = {}
        await query.message.reply_text("Send token contract address:")
        return
    
    elif choice == "action_wallets":
        # Check if user has wallet alert access
        if not can_use_wallet_alerts(user_id):
            wallets_count = len(get_wallets(user_id))
            if wallets_count >= 1:  # Free tier has 1 wallet
                await query.message.reply_text(get_upgrade_message(user_id, "wallet_alerts"))
                return
        
        wallets = get_wallets(user_id)
        
        keyboard = [
            [InlineKeyboardButton("➕ Add Wallet", callback_data="wallet_add")],
            [InlineKeyboardButton("📋 My Wallets", callback_data="wallet_list")],
            [InlineKeyboardButton("◀ Back", callback_data="wallet_back")]
        ]
        
        if wallets:
            msg = f"👀 Wallet Tracking\n\n"
            msg += f"You're tracking {len(wallets)} wallet(s):\n\n"
            for w in wallets:
                label = w.get('label', 'Unnamed Wallet')
                msg += f"• {label}\n  {w['address'][:10]}...{w['address'][-8:]}\n\n"
        else:
            msg = "👀 Wallet Tracking\n\n"
            msg += "Track smart wallets for buys into your tracked coins.\n\n"
            msg += "Only alerts on meaningful buys (not dust).\n\n"
            msg += "What would you like to do?"
        
        await query.message.reply_text(
            msg,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    elif choice == "home_lists":
        user_lists = get_lists(user_id)
        
        keyboard = [
            [InlineKeyboardButton("➕ Create List", callback_data="list_create")],
            [InlineKeyboardButton("📂 View Lists", callback_data="list_view")],
            [InlineKeyboardButton("◀ Back", callback_data="home_back")]
        ]
        
        if user_lists:
            msg = f"📂 Lists / Meta\n\n"
            msg += f"Group coins by narrative and\ntrack meta movements.\n\n"
            msg += f"You have {len(user_lists)} list(s):\n\n"
            for list_name, coins in user_lists.items():
                msg += f"• {list_name} ({len(coins)} coins)\n"
        else:
            msg = "📂 Lists / Meta\n\n"
            msg += "Group coins by narrative and\n"
            msg += "track meta movements.\n\n"
            msg += "Choose an option:"
        
        await query.message.reply_text(
            msg,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    elif choice == "action_lists":
        user_lists = get_lists(user_id)
        
        keyboard = [
            [InlineKeyboardButton("➕ Create List", callback_data="list_create")],
            [InlineKeyboardButton("📂 View Lists", callback_data="list_view")],
            [InlineKeyboardButton("◀ Back", callback_data="home_back")]
        ]
        
        if user_lists:
            msg = f"📂 Lists / Meta\n\n"
            msg += f"Group coins by narrative and\ntrack meta movements.\n\n"
            msg += f"You have {len(user_lists)} list(s):\n\n"
            for list_name, coins in user_lists.items():
                msg += f"• {list_name} ({len(coins)} coins)\n"
        else:
            msg = "📂 Lists / Meta\n\n"
            msg += "Group coins by narrative and\n"
            msg += "track meta movements.\n\n"
            msg += "Choose an option:"
        
        await query.message.reply_text(
            msg,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    elif choice == "action_dashboard":
        from storage import load_data
        data = load_data()
        user_data = data.get(str(user_id))
        
        if isinstance(user_data, list):
            coins = user_data
        else:
            coins = user_data.get("coins", []) if user_data else []
        
        if not coins:
            await query.message.reply_text(
                "📊 Dashboard\n\n"
                "You don't have any coins tracked yet.\n\n"
                "Use ➕ Track Coin to start monitoring."
            )
            return
        
        msg = "📊 Dashboard\n\n"
        
        for coin in coins:
            try:
                token = get_market_cap(coin["ca"])
                if not token:
                    continue

                mc = token["mc"]
                start = coin["start_mc"]
                ath = coin.get("ath_mc", start)
                low = coin.get("low_mc", start)
                
                dd = ((start - mc) / start) * 100
                x = mc / start
                
                range_pos = compute_range_position(mc, low, ath)
                range_desc = get_range_description(range_pos)
                
                alerts = coin.get("alerts", {})

                msg += (
                    f"🪙 {coin['ca'][:6]}...\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"💰 ${int(mc):,}\n"
                    f"📈 {x:.2f}x | 📉 {dd:.1f}%\n"
                    f"📊 {range_desc}\n\n"
                )
            
            except Exception as e:
                print(f"Dashboard error: {e}")
                continue
        
        await query.message.reply_text(msg)
        return
    
    # ALERT CONFIGURATION (inside track coin flow)
    state = user_state.get(user_id)

    if not state:
        return

    if choice == "alert_mc":
        state["step"] = "set_alert_mc"
        start_mc = state.get("start_mc", 0)
        mc_str = f"${int(start_mc):,}" if start_mc >= 1 else f"${start_mc:.2f}"
        await query.message.reply_text(
            f"📉 Market Cap Level\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Current: {mc_str}\n\n"
            f"Send the market cap to alert at (e.g., 50000)"
        )

    elif choice == "alert_pct":
        state["step"] = "set_alert_pct"
        await query.message.reply_text(
            f"📈 % Movement Alert\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Alert when price moves ±X%\n\n"
            f"Send percentage (e.g., 30 for ±30%)"
        )

    elif choice == "alert_x":
        state["step"] = "set_alert_x"
        await query.message.reply_text(
            f"🚀 X Multiple Alert\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Alert when you reach X multiplier\n\n"
            f"Send X value (e.g., 2 for 2x, 5 for 5x)"
        )

    elif choice == "alert_wallet":
        # Check if user has wallet alert access (Pro/Premium only)
        if not can_use_wallet_alerts(user_id):
            await query.message.reply_text(get_upgrade_message(user_id, "wallet_alerts"))
            return
        
        # Initialize wallet alerts with defaults
        state["alerts"]["wallets"] = {
            "addresses": [],
            "min_buy_usd": 300  # default
        }
        state["step"] = "select_wallets"
        
        wallets = get_wallets(user_id)
        
        if not wallets:
            await query.message.reply_text(
                "⚠️ No Wallets Added\n\n"
                "Add wallets first to use this feature.\n\n"
                "Go to 👀 Watch Wallets to add wallets."
            )
            state["alerts"].pop("wallets", None)
            return
        
        # Show wallet checkboxes
        keyboard = []
        for wallet in wallets:
            label = wallet.get('label', 'Unnamed Wallet')
            keyboard.append([
                InlineKeyboardButton(
                    f"☐ {label}",
                    callback_data=f"wallet_select_{wallet['address']}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("✅ Done", callback_data="wallet_select_done")
        ])
        
        await query.message.reply_text(
            "👀 Select Wallets\n\n"
            "Which wallets to watch for buys on this coin?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif choice.startswith("wallet_select_"):
        if choice == "wallet_select_done":
            # Move to minimum buy size configuration
            if not state["alerts"]["wallets"]["addresses"]:
                await query.message.reply_text(
                    "Please select at least one wallet."
                )
                return
            
            state["step"] = "wallet_min_buy"
            await query.message.reply_text(
                "💰 Minimum Buy Size\n\n"
                "Alert only if a wallet buys at least this amount (USD).\n\n"
                "Example: 500\n"
                "Type 'skip' to use default ($300)."
            )
        else:
            # Toggle wallet selection
            wallet_address = choice.replace("wallet_select_", "")
            wallets = get_wallets(user_id)
            selected = state["alerts"]["wallets"]["addresses"]
            
            if wallet_address in selected:
                selected.remove(wallet_address)
            else:
                selected.append(wallet_address)
            
            # Rebuild keyboard with updated checkmarks
            keyboard = []
            for wallet in wallets:
                label = wallet.get('label', 'Unnamed Wallet')
                check = "☑" if wallet["address"] in selected else "☐"
                keyboard.append([
                    InlineKeyboardButton(
                        f"{check} {label}",
                        callback_data=f"wallet_select_{wallet['address']}"
                    )
                ])
            
            keyboard.append([
                InlineKeyboardButton("✅ Done", callback_data="wallet_select_done")
            ])
            
            await query.edit_message_text(
                "👀 Select Wallets\n\n"
                "Which wallets to watch for buys on this coin?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    elif choice == "alert_reclaim":
        state["alerts"]["reclaim"] = True
        alerts_display = format_active_alerts(state["alerts"])
        await query.message.reply_text(
            f"✅ 🔥 ATH Reclaim Alert Added\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"You'll be alerted at 95% of ATH\n\n"
            f"Active alerts:\n"
            f"{alerts_display}"
        )

    elif choice == "alert_done":
        # Check if this is first coin
        from storage import load_data
        data = load_data()
        user_data = data.get(str(user_id))
        is_first_coin = (
            user_data is None or 
            (isinstance(user_data, dict) and len(user_data.get("coins", [])) == 0) or
            (isinstance(user_data, list) and len(user_data) == 0)
        )
        
        # save coin
        add_coin(user_id, {
            "ca": state["ca"],
            "start_mc": state["start_mc"],
            "ath_mc": state["start_mc"],
            "low_mc": state["start_mc"],
            "alerts": state["alerts"],
            "history": [],
            "triggered": {
                "mc": False,
                "pct": False,
                "x": False,
                "reclaim": False,
                "bounce": False
            }
        })
        user_state.pop(user_id)
        alerts_display = format_active_alerts(state["alerts"])
        
        # Send first-time tip if applicable
        if is_first_coin:
            await query.message.reply_text(
                f"✅ Coin added successfully\n\n"
                f"Active alerts:\n"
                f"{alerts_display}\n\n"
                f"👋 First coin tips:\n"
                f"• Use Dashboard to monitor\n"
                f"• Smart alerts trigger when conditions align\n"
                f"• Use /mode to choose your alert profile\n"
                f"• Add more coins with ➕ Track Coin"
            )
        else:
            await query.message.reply_text(
                f"✅ Coin added successfully\n\n"
                f"Active alerts:\n"
                f"{alerts_display}"
            )
    
    elif choice.startswith("mode_"):
        from storage import set_user_profile
        mode = choice.replace("mode_", "")
        set_user_profile(user_id, {"mode": mode})
        mode_names = {
            "conservative": "🐢 Conservative",
            "aggressive": "⚡ Aggressive",
            "sniper": "🧠 Sniper"
        }
        await query.message.reply_text(
            f"✅ Profile set to {mode_names.get(mode, mode)}\n\n"
            f"Your alerts will now match your preferences."
        )
    
    # ========================
    # WALLET TRACKING HANDLERS
    # ========================
    
    elif choice == "wallet_add":
        # Check tier limits
        wallets = get_wallets(user_id)
        if not can_add_wallet(user_id, len(wallets)):
            await query.message.reply_text(get_upgrade_message(user_id, "max_wallets"))
            return
        
        user_state[user_id] = {"step": "wallet_address"}
        await query.message.reply_text(
            "👛 Add Wallet\n\n"
            "Send a Solana wallet address to track:\n\n"
            "Paste the full address"
        )
    
    elif choice == "wallet_list":
        wallets = get_wallets(user_id)
        
        if not wallets:
            await query.message.reply_text("You don't have any wallets yet.")
            return
        
        msg = "📋 Your Wallets\n\n"
        for i, w in enumerate(wallets, start=1):
            label = w.get('label', 'Unnamed Wallet')
            msg += f"{i}. {label}\n"
            msg += f"   {w['address'][:10]}...{w['address'][-8:]}\n\n"
        
        await query.message.reply_text(msg)
    
    elif choice == "wallet_back":
        await query.message.reply_text(
            "Choose what you want to do:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Track Coin", callback_data="action_track")],
                [InlineKeyboardButton("👀 Watch Wallets", callback_data="action_wallets")],
                [InlineKeyboardButton("📂 Lists / Narratives", callback_data="action_lists")],
                [InlineKeyboardButton("📊 Dashboard", callback_data="action_dashboard")]
            ])
        )
    
    # ========================
    # LISTS & NARRATIVES HANDLERS
    # ========================
    
    elif choice == "list_create":
        # Check tier limits
        user_lists = get_lists(user_id)
        if not can_add_list(user_id, len(user_lists)):
            await query.message.reply_text(get_upgrade_message(user_id, "max_lists"))
            return
        
        user_state[user_id] = {"step": "list_name"}
        await query.message.reply_text(
            "📝 Create List\n\n"
            "Send a name for your list:\n\n"
            "e.g., AI, Bots, Gaming, DeFi"
        )
    
    elif choice == "list_view":
        user_lists = get_lists(user_id)
        
        if not user_lists:
            await query.message.reply_text("You don't have any lists yet.")
            return
        
        msg = "📂 Your Lists\n\n"
        for list_name, coins in user_lists.items():
            msg += f"• {list_name}\n"
            msg += f"  {len(coins)} coin(s)\n\n"
        
        await query.message.reply_text(msg)
    
    elif choice == "list_back":
        await query.message.reply_text(
            "Choose what you want to do:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Track Coin", callback_data="action_track")],
                [InlineKeyboardButton("👀 Watch Wallets", callback_data="action_wallets")],
                [InlineKeyboardButton("📂 Lists / Meta", callback_data="action_lists")],
                [InlineKeyboardButton("📊 Dashboard", callback_data="action_dashboard")]
            ])
        )

# -------------------------
# Monitoring loop (runs in separate thread)
# -------------------------

def monitor_loop_sync(bot_arg):
    """Synchronous monitor loop that runs in a separate thread."""
    import time
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = Bot(token=BOT_TOKEN)
    print("📡 Monitor loop started in background thread")
    
    async def monitor():
        while True:
            try:
                raw_data = load_data()
                
                for user_id, user_data in raw_data.items():
                    try:
                        if isinstance(user_data, list):
                            coins = user_data
                            user_mode = "aggressive"
                        else:
                            coins = user_data.get("coins", [])
                            user_mode = user_data.get("profile", {}).get("mode", "aggressive")
                        
                        for coin in coins:
                            try:
                                if not isinstance(coin, dict):
                                    continue

                                ca = coin.get("ca")
                                if not ca:
                                    continue

                                token = get_market_cap(ca)
                                if not token:
                                    continue

                                mc = token["mc"]
                                liquidity = token.get("liquidity", 0)
                                volume_24h = token.get("volume_24h", 0)
                                start = coin["start_mc"]

                                coin = update_coin_history(coin, mc, volume_24h, liquidity)
                                
                                if should_suppress_alert(coin, "default", user_mode):
                                    continue

                                dd = ((start - mc) / start) * 100
                                alerts = coin.get("alerts", {})
                                triggered = coin.get("triggered", {})

                                bounce_detected, bounce_type = detect_dump_stabilize_bounce(coin, mc, volume_24h)
                                
                                if bounce_detected and not triggered.get("bounce"):
                                    msg = format_smart_alert(coin, mc, bounce_type, user_mode)
                                    loop.run_until_complete(bot.send_message(user_id, msg))
                                    triggered["bounce"] = True

                                if "mc" in alerts and not triggered.get("mc"):
                                    if mc <= alerts["mc"]:
                                        msg = format_smart_alert(coin, mc, "mc_break", user_mode)
                                        loop.run_until_complete(bot.send_message(user_id, msg))
                                        triggered["mc"] = True

                                if "pct" in alerts and not triggered.get("pct"):
                                    pct_change = ((mc - start) / start) * 100
                                    if abs(pct_change) >= alerts["pct"]:
                                        range_pos = compute_range_position(
                                            mc, 
                                            coin.get("low_mc", mc), 
                                            coin.get("ath_mc", mc)
                                        )
                                        msg = (
                                            f"📈 % CHANGE ALERT\n"
                                            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                            f"Move: {pct_change:.1f}%\n"
                                            f"Position: {get_range_description(range_pos)}\n"
                                            f"MC: ${int(mc):,}"
                                        )
                                        loop.run_until_complete(bot.send_message(user_id, msg))
                                        triggered["pct"] = True

                                if "x" in alerts and not triggered.get("x"):
                                    multiple = mc / start
                                    if multiple >= alerts["x"]:
                                        loop.run_until_complete(bot.send_message(
                                            user_id,
                                            f"🚀 X ALERT\n"
                                            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                            f"Reached {multiple:.2f}x\n"
                                            f"MC: ${int(mc):,}"
                                        ))
                                        triggered["x"] = True

                                if alerts.get("reclaim") and not triggered.get("reclaim"):
                                    reclaim_level = coin["ath_mc"] * 0.95
                                    if mc >= reclaim_level:
                                        loop.run_until_complete(bot.send_message(
                                            user_id,
                                            f"🔥 ATH RECLAIM\n"
                                            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                            f"95% of ATH reached\n"
                                            f"MC: ${int(mc):,}"
                                        ))
                                        triggered["reclaim"] = True

                                # SAVE TRIGGERED STATE BACK TO COIN
                                coin["triggered"] = triggered

                                await asyncio.sleep(2)

                            except Exception as e:
                                print(f"Coin error: {e}")
                                continue

                        raw_data[user_id] = user_data
                        
                    except Exception as e:
                        print(f"User error: {e}")
                        continue
                
                save_data(raw_data)
                
            except Exception as e:
                print(f"Monitor loop error: {e}")
                continue

            time.sleep(CHECK_INTERVAL)
    
    try:
        loop.run_until_complete(monitor())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

async def monitor_loop(app):
    bot: Bot = app.bot
    while True:
        try:
            raw_data = load_data()
            
            # Restructure data for processing
            for user_id, user_data in raw_data.items():
                try:
                    # Handle both old and new data formats
                    if isinstance(user_data, list):
                        coins = user_data
                        user_mode = "aggressive"
                    else:
                        coins = user_data.get("coins", [])
                        user_mode = user_data.get("profile", {}).get("mode", "aggressive")
                    
                    for coin in coins:
                        try:
                            if not isinstance(coin, dict):
                                continue

                            ca = coin.get("ca")
                            if not ca:
                                continue

                            token = get_market_cap(ca)
                            if not token:
                                continue

                            mc = token["mc"]
                            liquidity = token.get("liquidity", 0)
                            volume_24h = token.get("volume_24h", 0)
                            start = coin["start_mc"]

                            # UPDATE INTELLIGENCE LAYER
                            coin = update_coin_history(coin, mc, volume_24h, liquidity)
                            
                            dd = ((start - mc) / start) * 100
                            x = mc / start
                            
                            # Suppress low-quality alerts
                            if should_suppress_alert(coin, "default", user_mode):
                                continue

                            alerts = coin.get("alerts", {})
                            triggered = coin.get("triggered", {})

                            # DETECT PATTERNS FIRST (highest priority)
                            bounce_detected, bounce_type = detect_dump_stabilize_bounce(coin, mc, volume_24h)
                            
                            if bounce_detected and not triggered.get("bounce"):
                                msg = format_smart_alert(coin, mc, bounce_type, user_mode)
                                await bot.send_message(user_id, msg)
                                triggered["bounce"] = True

                            # MC alert (with smart formatting)
                            if "mc" in alerts and not triggered.get("mc"):
                                if mc <= alerts["mc"]:
                                    msg = format_smart_alert(coin, mc, "mc_break", user_mode)
                                    await bot.send_message(user_id, msg)
                                    triggered["mc"] = True

                            # % change alert (up OR down)
                            if "pct" in alerts and not triggered.get("pct"):
                                pct_change = ((mc - start) / start) * 100
                                if abs(pct_change) >= alerts["pct"]:
                                    range_pos = compute_range_position(
                                        mc, 
                                        coin.get("low_mc", mc), 
                                        coin.get("ath_mc", mc)
                                    )
                                    msg = (
                                        f"📈 % CHANGE ALERT\n"
                                        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                        f"Move: {pct_change:.1f}%\n"
                                        f"Position: {get_range_description(range_pos)}\n"
                                        f"MC: ${int(mc):,}"
                                    )
                                    await bot.send_message(user_id, msg)
                                    triggered["pct"] = True

                            # X multiple alert
                            if "x" in alerts and not triggered.get("x"):
                                multiple = mc / start
                                if multiple >= alerts["x"]:
                                    await bot.send_message(
                                        user_id,
                                        f"🚀 X ALERT\n"
                                        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                        f"Reached {multiple:.2f}x\n"
                                        f"MC: ${int(mc):,}"
                                    )
                                    triggered["x"] = True

                            # ATH reclaim alert
                            if alerts.get("reclaim") and not triggered.get("reclaim"):
                                reclaim_level = coin["ath_mc"] * 0.95
                                if mc >= reclaim_level:
                                    await bot.send_message(
                                        user_id,
                                        f"🔥 ATH RECLAIM\n"
                                        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                        f"95% of ATH reached\n"
                                        f"MC: ${int(mc):,}"
                                    )
                                    triggered["reclaim"] = True

                            # SAVE TRIGGERED STATE BACK TO COIN
                            coin["triggered"] = triggered

                            # Throttle API calls
                            await asyncio.sleep(2)

                        except Exception as e:
                            print(f"Coin error: {e}")
                            continue
                    
                    # ======================
                    # WALLET BUY DETECTION (Phase 6)
                    # ======================
                    try:
                        if can_use_wallet_alerts(user_id):
                            user_wallets = get_wallets(user_id)
                            if user_wallets:
                                # Check each tracked coin for wallet buys
                                for coin in coins:
                                    if not isinstance(coin, dict):
                                        continue
                                    
                                    ca = coin.get("ca")
                                    if not ca:
                                        continue
                                    
                                    # Get wallet buy settings from coin alerts
                                    wallet_alert = coin.get("alerts", {}).get("wallets", {})
                                    if not wallet_alert.get("enabled"):
                                        continue
                                    
                                    min_buy = wallet_alert.get("min_buy_usd", 300)
                                    watched_addresses = wallet_alert.get("addresses", [])
                                    
                                    # Detect wallet buys
                                    buys = detect_wallet_buys(ca, user_wallets, min_buy)
                                    
                                    for buy in buys:
                                        # Filter to only watched wallets
                                        if watched_addresses and buy["address"] not in watched_addresses:
                                            continue
                                        
                                        # Send alert
                                        symbol = coin.get("symbol", "Token")
                                        alert_msg = format_wallet_buy_alert(buy, symbol)
                                        await bot.send_message(user_id, alert_msg)
                                        await asyncio.sleep(1)
                    
                    except Exception as e:
                        print(f"Wallet buy detection error: {e}")
                    
                    # ======================
                    # META ANALYSIS (Phase 7)
                    # ======================
                    try:
                        if can_use_meta_alerts(user_id):
                            user_lists = get_lists(user_id)
                            
                            # Build coin data dict for meta analysis
                            coin_data = {}
                            for coin in coins:
                                if isinstance(coin, dict) and coin.get("ca"):
                                    coin_data[coin["ca"]] = {
                                        "mc": coin.get("history", {}).get("mc", [])[-1] if coin.get("history", {}).get("mc") else coin.get("start_mc", 0),
                                        "volume_24h": coin.get("history", {}).get("volume_24h", [])[-1] if coin.get("history", {}).get("volume_24h") else 0,
                                        "start_mc": coin.get("start_mc", 0),
                                        "symbol": coin.get("symbol", ""),
                                    }
                            
                            # Check each list for heating
                            for list_name, list_coins in user_lists.items():
                                if not list_coins:
                                    continue
                                
                                # Analyze list performance
                                metrics = analyze_list_performance(list_coins, coin_data)
                                
                                # Check if list is heating up
                                is_heating, reason = detect_list_heating(list_name, metrics, threshold=40)
                                
                                if is_heating:
                                    # Check if we already alerted (simple cooldown)
                                    list_state_key = f"list_alert_{list_name}"
                                    if not triggered.get(list_state_key):
                                        alert_msg = format_list_alert(list_name, metrics, reason)
                                        await bot.send_message(user_id, alert_msg)
                                        triggered[list_state_key] = True
                                        await asyncio.sleep(1)
                    
                    except Exception as e:
                        print(f"Meta analysis error: {e}")

                    # Save updated data
                    raw_data[user_id] = user_data
                    
                except Exception as e:
                    print(f"User error: {e}")
                    continue
            
            # Save all updates at once
            save_data(raw_data)
            
            # MONITOR GROUPS
            try:
                group_ids = get_all_group_ids()
                for group_id in group_ids:
                    try:
                        coins = get_group_coins(group_id)
                        
                        for coin in coins:
                            try:
                                ca = coin.get("ca")
                                if not ca:
                                    continue
                                
                                token = get_market_cap(ca)
                                if not token:
                                    continue
                                
                                mc = token["mc"]
                                start = coin["start_mc"]
                                
                                # Update group coin history
                                ath = coin.get("ath_mc", start)
                                low = coin.get("low_mc", start)
                                
                                ath = max(ath, mc)
                                low = min(low, mc)
                                
                                update_group_coin_history(group_id, ca, mc, ath, low)
                                
                                alerts = coin.get("alerts", {})
                                triggered = coin.get("triggered", {})
                                
                                # MC alert (simple for groups)
                                if "mc" in alerts and not triggered.get("mc"):
                                    if mc <= alerts["mc"]:
                                        msg = (
                                            f"🚨 Group Alert — {ca[:6]}...\n\n"
                                            f"MC hit ${int(alerts['mc']):,}\n"
                                            f"Current: ${int(mc):,}"
                                        )
                                        await bot.send_message(group_id, msg)
                                        triggered["mc"] = True
                                
                                # ATH reclaim alert
                                if alerts.get("reclaim") and not triggered.get("reclaim"):
                                    reclaim_level = ath * 0.95
                                    if mc >= reclaim_level:
                                        msg = (
                                            f"🔥 Group Alert — {ca[:6]}...\n\n"
                                            f"ATH reclaim underway\n"
                                            f"Current: ${int(mc):,}"
                                        )
                                        await bot.send_message(group_id, msg)
                                        triggered["reclaim"] = True
                                
                                # Persist triggered state to storage
                                if triggered:
                                    update_group_coin_triggered(group_id, ca, triggered)
                                
                                await asyncio.sleep(1)
                            
                            except Exception as e:
                                print(f"Group coin error: {e}")
                                continue
                    
                    except Exception as e:
                        print(f"Group monitor error: {e}")
                        continue
            
            except Exception as e:
                print(f"Group monitoring error: {e}")
            
        except Exception as e:
            print(f"Monitor loop error: {e}")
            continue

        await asyncio.sleep(CHECK_INTERVAL)

# ========================
# APP ENTRY & SETUP
# ========================

# Create monitor thread
monitor_thread = threading.Thread(target=monitor_loop_sync, args=(None,), daemon=True)

def main():
    print("🚀 Trench Alert Bot running...")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands (work in both private and groups)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_coins))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("mode", mode))
    app.add_handler(CommandHandler("pricing", pricing_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    
    # Callbacks and message handlers
    app.add_handler(CallbackQueryHandler(alert_choice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    monitor_thread.start()

    # Drop any pending updates from previous runs to avoid getUpdates conflicts
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
