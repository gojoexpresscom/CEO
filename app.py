import os
import logging
import requests
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ceo-exchange-bot")

app = Flask(__name__)

# ---- required environment variables ----
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
ADMIN_CHAT_ID = os.environ["ADMIN_CHAT_ID"]
BOT_USERNAME = os.environ.get("BOT_USERNAME", "")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "")

# ---- Supabase ----
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

# ---- Telegram topic used for official announcements ----
# Put the Announcement topic ID here.
# Example: 123
ANNOUNCEMENT_TOPIC_ID = os.environ.get("ANNOUNCEMENT_TOPIC_ID", "")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


SYSTEM_PROMPT = """You are the official support assistant for CEO Exchange, a real P2P crypto trading platform and Telegram community.

Your job is to professionally support CEO Exchange members and help them understand CEO Exchange, P2P crypto trading, merchants, exchange rates, orders, escrow, payments, security, disputes, announcements, support information, and general trading concepts.

CEO Exchange is a real P2P trading project designed for real trading activity, not a demo or educational-only platform.

Always speak respectfully and professionally.
Be friendly, natural, confident, and helpful.
Do not sound like a robot or a bank hotline.

==================================================
CEO EXCHANGE
==================================================

CEO Exchange is a real P2P crypto trading platform where users can buy and sell crypto with other users and merchants.

CEO Exchange focuses on:

- P2P crypto trading
- Buying and selling crypto
- Merchant offers
- Local payment methods
- Order management
- Escrow-style protection
- Payment verification
- Dispute handling
- User security
- Merchant trading
- Community support
- Exchange-rate information

CEO Exchange is NOT Binance.
CEO Exchange is NOT officially affiliated with Binance.

You may explain Binance P2P concepts when useful for educational comparison, but never claim Binance operates, owns, guarantees, or controls CEO Exchange.

==================================================
TELEGRAM SUPPORT
==================================================

The current AI assistant is designed specifically for support inside the official CEO Exchange Telegram community.

It can help members with:

- CEO Exchange information
- P2P trading
- Merchant information
- Exchange rates
- Buy and sell prices
- P2P procedures
- Escrow
- Payment verification
- Security
- Scam prevention
- Disputes
- Official announcements
- Official support information
- General crypto/P2P education

The CEO Exchange website and future website AI features are separate future projects.

Do not claim that this Telegram AI currently controls or operates the CEO Exchange website.

==================================================
ANNOUNCEMENTS
==================================================

Official CEO Exchange announcements may contain:

- Platform updates
- New features
- P2P updates
- Exchange-rate updates
- Maintenance notices
- Security alerts
- Merchant updates
- Support information
- Promotions
- Important community information

Use official announcement information when it is provided.

Do not invent announcements.

Do not claim to have automatically read the entire historical Telegram group.

==================================================
CEO EXCHANGE RATES
==================================================

Current CEO Exchange reference rates:

BUY:
$1 USD = 190 ETB

SELL:
$1 USD = 180 ETB

BUY examples:

$1 = 190 ETB
$5 = 950 ETB
$10 = 1,900 ETB
$50 = 9,500 ETB
$100 = 19,000 ETB

SELL examples:

$1 = 180 ETB
$5 = 900 ETB
$10 = 1,800 ETB
$50 = 9,000 ETB
$100 = 18,000 ETB

If the user asks for a dollar conversion and the direction is unclear, ask whether they are buying or selling.

Do not describe these as an official government exchange rate.

Do not claim they are the universal Ethiopian market rate.

==================================================
P2P TRADING
==================================================

P2P means Peer-to-Peer.

P2P allows users to buy and sell crypto directly with other users or merchants using supported payment methods.

Typical process:

1. Find an available offer.
2. Check price and amount.
3. Check payment method.
4. Check order limits and conditions.
5. Open the order.
6. Complete the required payment.
7. Provide proof when required.
8. Seller verifies the actual payment.
9. Crypto is released.
10. Order is completed.

Never tell a seller to release crypto only because the buyer says they paid.

Never treat a screenshot as guaranteed proof of payment.

==================================================
ESCROW
==================================================

Escrow-style protection can secure crypto during an active P2P order while the buyer and seller complete the payment process.

Example:

Seller creates an offer.
Buyer accepts.
Crypto is secured.
Buyer pays.
Seller verifies payment.
Crypto is released.
Order is completed.

Disputes should be reviewed by the appropriate CEO Exchange admin/support team.

==================================================
BINANCE P2P
==================================================

You understand general Binance-style P2P concepts including:

- P2P advertisements
- Merchants
- Buy orders
- Sell orders
- Payment methods
- Escrow
- Order timers
- Payment confirmation
- Proof of payment
- Disputes
- Merchant reputation
- Completed orders
- Trading limits
- Crypto release
- Order cancellation

If asked whether CEO Exchange is Binance:

"CEO Exchange is a separate P2P platform. It can use similar P2P concepts such as merchants, escrow, payment verification, and order management, but CEO Exchange is not Binance and is not officially affiliated with Binance."

Never invent Binance fees, limits, policies, or current rules.

==================================================
MERCHANTS
==================================================

Merchants provide P2P offers.

Merchant offers can include:

- Price
- Available amount
- Payment method
- Order limits
- Trading conditions

Users should carefully review an offer before opening an order.

Never guarantee that a specific merchant is safe or legitimate.

==================================================
BLACK MARKET / PARALLEL MARKET
==================================================

Understand:

- Black market
- Black-market rate
- Parallel market
- Parallel exchange rate
- Unofficial exchange rate
- Street exchange rate
- Unofficial dollar rate

These terms generally refer to currency exchange outside official or authorized financial channels.

You can explain differences between:

- Bank rates
- Platform rates
- P2P rates
- Merchant rates
- Unofficial/parallel market rates

Rates can differ because of:

- Supply and demand
- Liquidity
- Foreign-currency availability
- Payment methods
- Transaction risk
- Market conditions
- Fees
- Trading volume

Do not present an unofficial market rate as an official CEO Exchange rate.

Do not provide instructions for hiding transactions, money laundering, falsifying information, avoiding authorities, or bypassing financial controls.

==================================================
PAYMENT SECURITY
==================================================

Never tell users to share:

- Passwords
- Private keys
- Seed phrases
- OTP codes
- Authentication codes

Never tell users to release crypto outside the order.

Common scams include:

- Fake payment screenshots
- Fake receipts
- Fake bank notifications
- Fake admins
- Fake support accounts
- Phishing links
- Edited transaction screenshots
- Social engineering
- Fake crypto release messages
- Chargeback attempts

If something looks suspicious, tell the user to stop and contact an admin.

==================================================
PROOF OF PAYMENT
==================================================

A screenshot, SMS, or receipt does not automatically prove that funds were received.

Sellers should check their actual payment account before releasing crypto.

==================================================
DISPUTES
==================================================

Escalate issues involving:

- Scam
- Fraud
- Missing payment
- Payment not received
- Fake proof
- Wrong payment amount
- Buyer did not pay
- Seller did not release crypto
- Stuck order
- Refund problem
- Suspicious transaction
- Account problem

Do not decide who is right or wrong.

Do not promise refunds.

Do not promise that funds will definitely be recovered.

Tell users to keep relevant evidence and allow an admin to review the situation.

==================================================
PRIVACY
==================================================

The AI is a Telegram support assistant.

It does NOT have access to:

- Passwords
- Private keys
- Seed phrases
- OTP codes
- Private account information
- KYC information
- Wallet balances
- Transaction history

Never pretend to see private user information.

Do not behave as a personal memory assistant.

==================================================
TELEGRAM HISTORY
==================================================

Use official CEO Exchange announcements and approved support information when available.

Do not claim to have automatically read the entire past Telegram group.

Do not claim to see private Telegram conversations.

==================================================
STICKERS AND EMOJIS
==================================================

You can understand emojis and the meaning of stickers when enough context is provided.

You may naturally use emojis when appropriate.

Do not spam emojis.

Do not claim you can send Telegram stickers unless the bot is specifically programmed to send them.

==================================================
REAL TRADING
==================================================

CEO Exchange is intended for real P2P trading activity.

Do not describe CEO Exchange as:

- A demo
- A simulation
- An educational-only platform

Treat real-money trading questions seriously.

Prioritize accurate information, payment verification, security, and proper support escalation.

==================================================
ACCOUNT INFORMATION
==================================================

You do NOT have live access to:

- User balances
- Wallet balances
- Active orders
- Transaction history
- Deposits
- Withdrawals
- KYC information
- Merchant status
- Payment accounts
- Private account information

Never pretend to see these things.

==================================================
PLATFORM RULES
==================================================

If you are not certain about an exact CEO Exchange rule, do not invent it.

This includes:

- Fees
- Limits
- Processing times
- Withdrawal rules
- Deposit rules
- KYC requirements
- Merchant requirements
- Account restrictions
- Payment methods

Tell the user that an admin should confirm the current rule.

==================================================
FUTURE PROJECTS
==================================================

CEO Exchange is an actively developing project.

Future projects may include:

- Website improvements
- AI features
- New trading features
- New payment methods
- Merchant features
- Community features
- Additional platform services

Do not claim a future feature is already available unless officially announced.

==================================================
COMMUNICATION STYLE
==================================================

Always be respectful.

Be natural and professional.

Use phrases such as:

"Absolutely."
"I understand."
"Sure, let me explain."
"Here's how it works."
"For your security..."
"Please check the order details carefully."

Do not insult users.
Do not argue.
Do not make fun of users.

Simple question = simple answer.

Detailed question = detailed answer.

==================================================
IMPORTANT
==================================================

You represent CEO Exchange professionally.

Understand:

CEO Exchange
P2P trading
Binance-style P2P mechanics
Escrow
Merchants
Buy and sell orders
Payment verification
Proof of payment
Disputes
Trading limits
Exchange rates
Buy/sell spreads
P2P rates
Unofficial/parallel markets
Black-market terminology
Crypto security
P2P scams
Official announcements
Telegram community support
Real P2P trading

Never make up information.

Never claim access to private user data.

Never guarantee a trade is safe.

Never claim to have read Telegram history that has not actually been provided.

Current CEO Exchange reference rates:

BUY:
$1 = 190 ETB

SELL:
$1 = 180 ETB
"""


ESCALATE_KEYWORDS = [
    "scam",
    "scammed",
    "didn't receive",
    "did not receive",
    "not received",
    "no payment",
    "didn't pay",
    "did not pay",
    "hasn't paid",
    "has not paid",
    "fraud",
    "fake proof",
    "fake receipt",
    "dispute",
    "admin help",
    "need admin",
    "report",
    "stuck",
    "problem with order",
    "blocked me",
    "won't release",
    "wont release",
    "refund",
    "cancelled my order",
    "canceled my order"
]


def send_message(
    chat_id,
    text,
    message_thread_id=None,
    reply_to_message_id=None
):
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if message_thread_id:
        payload["message_thread_id"] = message_thread_id

    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id

    try:
        r = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json=payload,
            timeout=15
        )

        if not r.ok:
            logger.error("sendMessage failed: %s", r.text)

        return r

    except Exception:
        logger.exception("send_message failed")
        return None


def supabase_headers():
    return {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }


def save_subscriber(chat_id, username=None, first_name=None):
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        logger.warning("Supabase subscriber storage is not configured.")
        return False

    try:
        url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/telegram_subscribers"

        payload = {
            "chat_id": str(chat_id),
            "username": username,
            "first_name": first_name,
            "subscribed": True
        }

        response = requests.post(
            url,
            headers={
                **supabase_headers(),
                "Prefer": "resolution=merge-duplicates,return=minimal"
            },
            json=payload,
            timeout=15
        )

        if not response.ok:
            logger.error(
                "save_subscriber failed: %s",
                response.text
            )
            return False

        return True

    except Exception:
        logger.exception("save_subscriber failed")
        return False


def remove_subscriber(chat_id):
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return False

    try:
        url = (
            f"{SUPABASE_URL.rstrip('/')}"
            f"/rest/v1/telegram_subscribers"
            f"?chat_id=eq.{chat_id}"
        )

        response = requests.patch(
            url,
            headers=supabase_headers(),
            json={
                "subscribed": False
            },
            timeout=15
        )

        if not response.ok:
            logger.error(
                "remove_subscriber failed: %s",
                response.text
            )
            return False

        return True

    except Exception:
        logger.exception("remove_subscriber failed")
        return False


def get_subscribers():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return []

    try:
        url = (
            f"{SUPABASE_URL.rstrip('/')}"
            f"/rest/v1/telegram_subscribers"
            f"?subscribed=eq.true"
            f"&select=chat_id"
        )

        response = requests.get(
            url,
            headers=supabase_headers(),
            timeout=15
        )

        if not response.ok:
            logger.error(
                "get_subscribers failed: %s",
                response.text
            )
            return []

        data = response.json()

        return [
            str(row["chat_id"])
            for row in data
            if row.get("chat_id")
        ]

    except Exception:
        logger.exception("get_subscribers failed")
        return []


def broadcast_announcement(text):
    subscribers = get_subscribers()

    sent = 0
    failed = 0

    for chat_id in subscribers:

        response = send_message(
            chat_id,
            "📢 CEO Exchange Official Announcement\n\n" + text
        )

        if response is not None and response.ok:
            sent += 1
        else:
            failed += 1

            # If the user blocked the bot or the chat no longer exists,
            # remove them from future broadcasts.
            remove_subscriber(chat_id)

    return sent, failed


def handle_command(text):

    command = text.lower().split()[0].split("@")[0]

    commands = {

        "/start":
        """Welcome to CEO Exchange 👋

I am the official CEO Exchange support assistant.

I can help you with:

• P2P trading
• Exchange rates
• Buy and sell prices
• Merchants
• Security
• Disputes
• Announcements
• General CEO Exchange support

📢 By starting this bot, you can also receive official CEO Exchange announcements directly here.

Use /help to see all available commands.

Use /stop if you no longer want announcement notifications.""",

        "/help":
        """CEO Exchange Support 🛟

/rates - View current CEO Exchange rates
/buy - View the USD buy rate
/sell - View the USD sell rate
/p2p - Learn how P2P trading works
/merchant - Learn about P2P merchants
/security - P2P security and scam prevention
/dispute - Get help with a trading dispute
/announcements - View CEO Exchange announcements
/support - Get CEO Exchange support
/stop - Stop announcement notifications""",

        "/rates":
        """CEO Exchange Reference Rates 💱

BUY:
$1 = 190 ETB

SELL:
$1 = 180 ETB

Examples:

Buying $10 = 1,900 ETB
Selling $10 = 1,800 ETB""",

        "/buy":
        """CEO Exchange BUY Rate 💰

$1 USD = 190 ETB

Examples:

$5 = 950 ETB
$10 = 1,900 ETB
$50 = 9,500 ETB
$100 = 19,000 ETB""",

        "/sell":
        """CEO Exchange SELL Rate 💰

$1 USD = 180 ETB

Examples:

$5 = 900 ETB
$10 = 1,800 ETB
$50 = 9,000 ETB
$100 = 18,000 ETB""",

        "/p2p":
        """P2P Trading 🔄

P2P means Peer-to-Peer trading.

Users can buy and sell crypto with other users or merchants through available offers and supported payment methods.

Always check the order details carefully and verify payments before releasing crypto.""",

        "/merchant":
        """CEO Exchange Merchants 👤

Merchants provide P2P buy and sell offers.

Before opening an order, carefully check:

• Price
• Available amount
• Payment method
• Order limits
• Trading conditions

Never share sensitive account information with another user.""",

        "/security":
        """P2P Security 🔐

Never share:

• Passwords
• Private keys
• Seed phrases
• OTP codes
• Authentication codes

Never release crypto only because someone sends a screenshot saying they paid.

Always verify the actual payment in your account.""",

        "/dispute":
        """CEO Exchange Dispute Support 🛟

If you have:

• Payment problems
• A scam report
• Fake proof of payment
• A stuck order
• A refund problem
• Another trading issue

Contact a CEO Exchange admin and keep all relevant evidence for review.""",

        "/announcements":
        """CEO Exchange Announcements 📢

Official CEO Exchange announcements may include:

• Platform updates
• New features
• P2P updates
• Rate updates
• Maintenance
• Security alerts
• Merchant updates
• Important community information

Check the official CEO Exchange announcement topic for the latest updates.""",

        "/support":
        """CEO Exchange Support 🛟

I can help with general CEO Exchange and P2P questions.

For active orders, payment problems, disputes, or account-specific issues, please contact a human CEO Exchange admin.""",

        "/stop":
        """🔕 CEO Exchange announcement notifications have been turned off for you.

You can use /start at any time to subscribe again."""
    }

    return commands.get(command)


def ask_ai(user_text):

    try:

        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "content-type": "application/json"
            },
            json={
                "model": "openai/gpt-oss-20b",
                "max_tokens": 400,
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": user_text
                    }
                ]
            },
            timeout=30
        )

        resp.raise_for_status()

        data = resp.json()

        reply = data["choices"][0]["message"]["content"].strip()

        return reply or (
            "Sorry, I couldn't put together a reply just now."
        )

    except Exception:

        logger.exception("ask_ai failed")

        return (
            "Sorry, I hit an error answering that - "
            "an admin can help if it's urgent."
        )


def looks_like_escalation(text):

    t = text.lower()

    return any(
        kw in t
        for kw in ESCALATE_KEYWORDS
    )


def bot_was_addressed(message):

    text = message.get("text", "") or ""

    if message.get("chat", {}).get("type") == "private":
        return True

    if (
        BOT_USERNAME
        and f"@{BOT_USERNAME}".lower() in text.lower()
    ):
        return True

    reply = message.get("reply_to_message")

    if reply:

        replied_user = reply.get("from", {})

        if (
            replied_user.get("is_bot")
            and replied_user.get("username", "").lower()
            == BOT_USERNAME.lower()
        ):
            return True

    return False


@app.route("/webhook", methods=["POST"])
def webhook():

    update = request.get_json(
        force=True,
        silent=True
    ) or {}

    message = (
        update.get("message")
        or update.get("edited_message")
    )

    if not message:
        return jsonify(ok=True)

    text = message.get("text", "") or ""

    if not text:
        return jsonify(ok=True)

    chat_id = message["chat"]["id"]

    thread_id = message.get("message_thread_id")

    user = message.get("from", {})

    username = (
        user.get("username")
        or user.get("first_name")
        or "someone"
    )

    first_name = user.get("first_name")

    chat_type = message.get("chat", {}).get("type")

    # ============================================
    # PRIVATE CHAT / COMMANDS
    # ============================================

    if text.startswith("/"):

        command = text.lower().split()[0].split("@")[0]

        # START = subscribe to announcements
        if command == "/start":

            saved = save_subscriber(
                chat_id,
                username,
                first_name
            )

            reply = handle_command(text)

            if not saved:
                reply += (
                    "\n\n⚠️ I couldn't save your "
                    "announcement subscription right now."
                )

            send_message(
                chat_id,
                reply,
                message_thread_id=thread_id,
                reply_to_message_id=message["message_id"]
            )

            return jsonify(ok=True)

        # STOP = unsubscribe
        if command == "/stop":

            remove_subscriber(chat_id)

            send_message(
                chat_id,
                handle_command(text),
                message_thread_id=thread_id,
                reply_to_message_id=message["message_id"]
            )

            return jsonify(ok=True)

        # ADMIN ONLY
        if command == "/subscribers":

            if str(chat_id) != str(ADMIN_CHAT_ID):

                send_message(
                    chat_id,
                    "This command is only available to the CEO Exchange administrator."
                )

                return jsonify(ok=True)

            subscribers = get_subscribers()

            send_message(
                chat_id,
                f"📊 CEO Exchange Announcement Subscribers\n\nActive subscribers: {len(subscribers)}"
            )

            return jsonify(ok=True)

        command_reply = handle_command(text)

        if command_reply:

            send_message(
                chat_id,
                command_reply,
                message_thread_id=thread_id,
                reply_to_message_id=message["message_id"]
            )

            return jsonify(ok=True)

    # ============================================
    # ANNOUNCEMENT BROADCAST
    # ============================================

    # Only process announcements from the configured topic.
    #
    # IMPORTANT:
    # Set ANNOUNCEMENT_TOPIC_ID in Render to the actual
    # Telegram topic ID for your official announcement topic.

    if (
        chat_type in ["group", "supergroup"]
        and thread_id
        and ANNOUNCEMENT_TOPIC_ID
        and str(thread_id) == str(ANNOUNCEMENT_TOPIC_ID)
    ):

        # Do not broadcast commands as announcements.
        if not text.startswith("/"):

            sent, failed = broadcast_announcement(text)

            logger.info(
                "Announcement broadcast complete: sent=%s failed=%s",
                sent,
                failed
            )

            # Notify admin only through logs.
            return jsonify(
                ok=True,
                broadcast=True,
                sent=sent,
                failed=failed
            )

    # ============================================
    # ESCALATION
    # ============================================

    if looks_like_escalation(text):

        alert = (
            "\U0001F6A8 Possible issue flagged in CEO Exchange\n"
            f"From: @{username} (id {user.get('id')})\n"
            f"Chat: {chat_id}"
            + (
                f" (topic id {thread_id})"
                if thread_id
                else ""
            )
            + "\n\n"
            f"Message: {text}"
        )

        send_message(
            ADMIN_CHAT_ID,
            alert
        )

        send_message(
            chat_id,
            "Got it - flagging this for an admin now. Hang tight, someone will jump in.",
            message_thread_id=thread_id,
            reply_to_message_id=message["message_id"]
        )

        return jsonify(ok=True)

    # ============================================
    # AI SUPPORT
    # ============================================

    if bot_was_addressed(message):

        reply = ask_ai(text)

        send_message(
            chat_id,
            reply,
            message_thread_id=thread_id,
            reply_to_message_id=message["message_id"]
        )

    return jsonify(ok=True)


@app.route("/", methods=["GET"])
def health():

    return "CEO Exchange bot is running."


@app.route("/set-webhook", methods=["GET"])
def set_webhook():

    if not PUBLIC_URL:

        return jsonify(
            ok=False,
            error="Set the PUBLIC_URL environment variable first."
        ), 400

    r = requests.get(
        f"{TELEGRAM_API}/setWebhook",
        params={
            "url": f"{PUBLIC_URL.rstrip('/')}/webhook"
        }
    )

    return jsonify(r.json())


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
        )
