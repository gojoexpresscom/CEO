import os
import logging
import requests
from flask import Flask, request, jsonify

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("ceo-exchange-bot")

app = Flask(__name__)


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
ADMIN_CHAT_ID = os.environ["ADMIN_CHAT_ID"]

BOT_USERNAME = os.environ.get("BOT_USERNAME", "")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "")

# Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY",
    ""
)

# IMPORTANT:
# Leave this EMPTY for now.
# We will get the correct topic ID from Render logs.
ANNOUNCEMENT_TOPIC_ID = os.environ.get(
    "ANNOUNCEMENT_TOPIC_ID",
    ""
)

TELEGRAM_API = (
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
)


# ============================================================
# CEO EXCHANGE AI SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are the official support assistant for CEO Exchange.

CEO Exchange is a real P2P crypto trading platform and
Telegram community.

Your job is to professionally help users understand:

- CEO Exchange
- P2P trading
- Buying and selling crypto
- Merchants
- Orders
- Escrow
- Payment verification
- Security
- Scam prevention
- Disputes
- Announcements
- Exchange rates
- General crypto concepts

CEO Exchange is NOT Binance and is not officially affiliated
with Binance.

Never claim Binance owns, operates, controls, guarantees,
or officially supports CEO Exchange.

CEO Exchange is intended for real P2P trading activity.

==================================================
CURRENT CEO EXCHANGE REFERENCE RATES
==================================================

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

If the user asks for a conversion and it is unclear whether
they are buying or selling, ask which direction.

These are CEO Exchange reference rates.

Do NOT call them official Ethiopian government rates.

Do NOT call them universal Ethiopian market rates.

==================================================
P2P
==================================================

P2P means Peer-to-Peer.

Typical process:

1. Find an offer.
2. Check price.
3. Check payment method.
4. Check limits.
5. Open the order.
6. Complete payment.
7. Provide proof if required.
8. Seller verifies actual payment.
9. Crypto is released.
10. Order is completed.

Never tell a seller to release crypto only because the buyer
claims they paid.

A screenshot is not guaranteed proof of payment.

==================================================
SECURITY
==================================================

Never ask users for:

- Passwords
- Private keys
- Seed phrases
- OTP codes
- Authentication codes

Never tell users to release crypto outside an active order.

Warn about:

- Fake payment screenshots
- Fake receipts
- Fake admins
- Fake support accounts
- Phishing
- Social engineering
- Edited transaction screenshots
- Fake crypto release messages

If something looks suspicious, tell the user to stop and
contact a CEO Exchange admin.

==================================================
DISPUTES
==================================================

Escalate:

- Scam
- Fraud
- Missing payment
- Payment not received
- Fake proof
- Wrong payment
- Stuck order
- Seller not releasing crypto
- Refund problems
- Suspicious transactions
- Account problems

Do not decide who is right or wrong.

Do not guarantee refunds.

Do not guarantee recovery of funds.

Tell the user to keep evidence and allow an admin to review.

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

Never pretend to see private information.

==================================================
TELEGRAM
==================================================

This AI is a Telegram support assistant.

Do not claim to automatically know the entire Telegram
history.

Do not claim to see private Telegram conversations.

Official announcements should only be treated as official
when they are actually provided by the CEO Exchange system.

==================================================
COMMUNICATION STYLE
==================================================

Be:

- Friendly
- Professional
- Natural
- Clear
- Helpful

Simple question = simple answer.

Detailed question = detailed answer.

Never insult users.

Never argue with users.

Never invent CEO Exchange rules.

If you are unsure about an exact fee, limit, KYC requirement,
processing time, withdrawal rule, merchant requirement, or
other platform rule, tell the user that an admin should
confirm the current rule.

==================================================
IMPORTANT
==================================================

Never invent information.

Never claim access to private user data.

Never guarantee a trade is safe.

Never claim to have read Telegram history that was not
provided to you.
"""


# ============================================================
# ESCALATION KEYWORDS
# ============================================================

ESCALATE_KEYWORDS = [
    "scam",
    "scammed",
    "fraud",
    "fake proof",
    "fake receipt",
    "didn't receive",
    "did not receive",
    "not received",
    "no payment",
    "didn't pay",
    "did not pay",
    "hasn't paid",
    "has not paid",
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


# ============================================================
# TELEGRAM SEND MESSAGE
# ============================================================

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
        payload["reply_to_message_id"] = (
            reply_to_message_id
        )

    try:

        response = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json=payload,
            timeout=15
        )

        if not response.ok:

            logger.error(
                "Telegram sendMessage failed: %s",
                response.text
            )

        return response

    except Exception:

        logger.exception(
            "send_message failed"
        )

        return None


# ============================================================
# SUPABASE HEADERS
# ============================================================

def supabase_headers():

    return {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": (
            f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
        ),
        "Content-Type": "application/json"
    }


# ============================================================
# SAVE / UPDATE TELEGRAM SUBSCRIBER
# ============================================================

def save_subscriber(
    chat_id,
    username=None,
    first_name=None
):

    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:

        logger.warning(
            "Supabase is not configured."
        )

        return False

    try:

        url = (
            f"{SUPABASE_URL.rstrip('/')}"
            "/rest/v1/telegram_subscribers"
        )

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
                "Prefer": (
                    "resolution=merge-duplicates,"
                    "return=minimal"
                )
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

        logger.exception(
            "save_subscriber failed"
        )

        return False


# ============================================================
# UPDATE LAST SEEN
# ============================================================

def update_last_seen(
    chat_id,
    username=None,
    first_name=None
):

    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return False

    try:

        url = (
            f"{SUPABASE_URL.rstrip('/')}"
            "/rest/v1/telegram_subscribers"
            f"?chat_id=eq.{chat_id}"
        )

        payload = {
            "username": username,
            "first_name": first_name,
            "subscribed": True,
            "last_seen_at": "now()"
        }

        response = requests.patch(
            url,
            headers=supabase_headers(),
            json=payload,
            timeout=15
        )

        return response.ok

    except Exception:

        logger.exception(
            "update_last_seen failed"
        )

        return False


# ============================================================
# UNSUBSCRIBE
# ============================================================

def remove_subscriber(chat_id):

    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return False

    try:

        url = (
            f"{SUPABASE_URL.rstrip('/')}"
            "/rest/v1/telegram_subscribers"
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

        return response.ok

    except Exception:

        logger.exception(
            "remove_subscriber failed"
        )

        return False


# ============================================================
# GET ACTIVE SUBSCRIBERS
# ============================================================

def get_subscribers():

    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return []

    try:

        url = (
            f"{SUPABASE_URL.rstrip('/')}"
            "/rest/v1/telegram_subscribers"
            "?subscribed=eq.true"
            "&select=chat_id"
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

        logger.exception(
            "get_subscribers failed"
        )

        return []


# ============================================================
# AI
# ============================================================

def ask_ai(user_text):

    try:

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",

            headers={
                "Authorization": (
                    f"Bearer {GROQ_API_KEY}"
                ),
                "Content-Type": "application/json"
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

        response.raise_for_status()

        data = response.json()

        reply = (
            data["choices"][0]["message"]["content"]
            .strip()
        )

        return reply or (
            "Sorry, I couldn't prepare a response right now."
        )

    except Exception:

        logger.exception(
            "ask_ai failed"
        )

        return (
            "Sorry, I couldn't answer that right now. "
            "If this involves an active trade or payment, "
            "please contact a CEO Exchange admin."
        )


# ============================================================
# ESCALATION DETECTION
# ============================================================

def looks_like_escalation(text):

    text = text.lower()

    return any(
        keyword in text
        for keyword in ESCALATE_KEYWORDS
    )


# ============================================================
# BOT WAS ADDRESSED
# ============================================================

def bot_was_addressed(message):

    text = message.get("text", "") or ""

    chat_type = (
        message.get("chat", {}).get("type")
    )

    # Private chat
    if chat_type == "private":
        return True

    # Mention
    if BOT_USERNAME:

        mention = (
            f"@{BOT_USERNAME}"
        ).lower()

        if mention in text.lower():
            return True

    # Reply to bot
    reply = message.get(
        "reply_to_message"
    )

    if reply:

        replied_user = reply.get(
            "from",
            {}
        )

        if replied_user.get("is_bot"):

            bot_username = (
                replied_user.get("username", "")
                .lower()
            )

            if (
                bot_username
                and bot_username
                == BOT_USERNAME.lower()
            ):
                return True

    return False


# ============================================================
# COMMANDS
# ============================================================

def handle_command(text):

    command = (
        text.lower()
        .split()[0]
        .split("@")[0]
    )

    commands = {

        "/start":
        """Welcome to CEO Exchange 👋

I am the official CEO Exchange support assistant.

I can help with:

• P2P trading
• Buy & sell rates
• Merchants
• Security
• Disputes
• Announcements
• General CEO Exchange support

📢 You are now subscribed to official CEO Exchange announcements.

Use /help to see available commands.

Use /stop to stop announcement notifications.""",

        "/help":
        """CEO Exchange Support 🛟

/rates — Current CEO Exchange rates
/buy — USD buy rate
/sell — USD sell rate
/p2p — Learn about P2P
/merchant — Merchant information
/security — Security & scam prevention
/dispute — Trading dispute help
/announcements — Announcement information
/support — Human support information
/stop — Stop announcements""",

        "/rates":
        """CEO Exchange Reference Rates 💱

BUY:
$1 = 190 ETB

SELL:
$1 = 180 ETB

Buying $10 = 1,900 ETB
Selling $10 = 1,800 ETB""",

        "/buy":
        """CEO Exchange BUY Rate 💰

$1 USD = 190 ETB

$5 = 950 ETB
$10 = 1,900 ETB
$50 = 9,500 ETB
$100 = 19,000 ETB""",

        "/sell":
        """CEO Exchange SELL Rate 💰

$1 USD = 180 ETB

$5 = 900 ETB
$10 = 1,800 ETB
$50 = 9,000 ETB
$100 = 18,000 ETB""",

        "/p2p":
        """P2P Trading 🔄

P2P means Peer-to-Peer.

Users can buy and sell crypto with other users or merchants.

Always check:

• Price
• Payment method
• Limits
• Order conditions

Never release crypto until the actual payment has been verified.""",

        "/merchant":
        """CEO Exchange Merchants 👤

Merchants provide P2P offers.

Before opening an order, check:

• Price
• Available amount
• Payment method
• Limits
• Trading conditions

Never share passwords, OTPs, private keys or seed phrases.""",

        "/security":
        """P2P Security 🔐

Never share:

• Passwords
• Private keys
• Seed phrases
• OTP codes
• Authentication codes

Never release crypto based only on a screenshot.

Always verify the actual payment.""",

        "/dispute":
        """CEO Exchange Dispute Support 🛟

For:

• Scam
• Missing payment
• Fake proof
• Stuck order
• Refund problem
• Seller not releasing crypto

Keep all evidence and contact a CEO Exchange admin.""",

        "/announcements":
        """CEO Exchange Official Announcements 📢

Official announcements may include:

• Platform updates
• New features
• P2P updates
• Rate updates
• Maintenance
• Security alerts
• Merchant updates
• Promotions

You can receive official announcements directly from this bot.""",

        "/support":
        """CEO Exchange Support 🛟

I can answer general CEO Exchange and P2P questions.

For active orders, payments, disputes or account-specific
issues, please contact a human CEO Exchange administrator.""",

        "/stop":
        """🔕 Announcement notifications have been turned off.

Send /start anytime to subscribe again."""
    }

    return commands.get(command)


# ============================================================
# BROADCAST ANNOUNCEMENT
# ============================================================

def broadcast_announcement(text):

    subscribers = get_subscribers()

    sent = 0
    failed = 0

    logger.info(
        "Broadcasting announcement to %s subscribers",
        len(subscribers)
    )

    for chat_id in subscribers:

        response = send_message(
            chat_id,
            "📢 CEO Exchange Official Announcement\n\n"
            + text
        )

        if response is not None and response.ok:

            sent += 1

        else:

            failed += 1

            # Telegram may reject the message if the user
            # blocked the bot or deleted the chat.

            remove_subscriber(chat_id)

    logger.info(
        "Broadcast finished | sent=%s | failed=%s",
        sent,
        failed
    )

    return sent, failed


# ============================================================
# WEBHOOK
# ============================================================

@app.route(
    "/webhook",
    methods=["POST"]
)
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

        return jsonify(
            ok=True
        )

    text = (
        message.get("text", "")
        or ""
    )

    if not text:

        return jsonify(
            ok=True
        )

    chat = message.get(
        "chat",
        {}
    )

    user = message.get(
        "from",
        {}
    )

    chat_id = chat.get("id")

    chat_type = chat.get(
        "type"
    )

    thread_id = message.get(
        "message_thread_id"
    )

    username = (
        user.get("username")
        or user.get("first_name")
        or "someone"
    )

    first_name = user.get(
        "first_name"
    )

    message_id = message.get(
        "message_id"
    )

    # ========================================================
    # THIS IS THE IMPORTANT LOG
    # ========================================================

    logger.info(
        "CHAT=%s THREAD=%s TEXT=%s",
        chat_id,
        thread_id,
        text
    )

  logger.info(
        "USER=%s | USER_ID=%s | CHAT_TYPE=%s | MESSAGE_ID=%s",
        username,
        user.get("id"),
        chat_type,
        message_id
    )

    # ========================================================
    # UPDATE USER ACTIVITY
    # ========================================================

    if chat_type == "private":

        update_last_seen(
            chat_id,
            username,
            first_name
        )

    # ========================================================
    # COMMANDS
    # ========================================================

    if text.startswith("/"):

        command = (
            text.lower()
            .split()[0]
            .split("@")[0]
        )

        # ----------------------------------------------------
        # START
        # ----------------------------------------------------

        if command == "/start":

            saved = save_subscriber(
                chat_id,
                username,
                first_name
            )

            reply = handle_command(
                text
            )

            if not saved:

                reply += (
                    "\n\n⚠️ Your subscription could not "
                    "be saved right now."
                )

            send_message(
                chat_id,
                reply,
                message_thread_id=thread_id,
                reply_to_message_id=message_id
            )

            return jsonify(
                ok=True
            )

        # ----------------------------------------------------
        # STOP
        # ----------------------------------------------------

        if command == "/stop":

            remove_subscriber(
                chat_id
            )

            send_message(
                chat_id,
                handle_command(text),
                message_thread_id=thread_id,
                reply_to_message_id=message_id
            )

            return jsonify(
                ok=True
            )

        # ----------------------------------------------------
        # ADMIN SUBSCRIBER COUNT
        # ----------------------------------------------------

        if command == "/subscribers":

            if str(chat_id) != str(
                ADMIN_CHAT_ID
            ):

                send_message(
                    chat_id,
                    "⛔ Admin only."
                )

                return jsonify(
                    ok=True
                )

            subscribers = get_subscribers()

            send_message(
                chat_id,
                "📊 CEO Exchange Subscribers\n\n"
                f"Active subscribers: {len(subscribers)}"
            )

            return jsonify(
                ok=True
            )

        # ----------------------------------------------------
        # NORMAL COMMAND
        # ----------------------------------------------------

        command_reply = handle_command(
            text
        )

        if command_reply:

            send_message(
                chat_id,
                command_reply,
                message_thread_id=thread_id,
                reply_to_message_id=message_id
            )

            return jsonify(
                ok=True
            )

    # ========================================================
    # ANNOUNCEMENT TOPIC DETECTION
    # ========================================================

    if (
        chat_type in [
            "group",
            "supergroup"
        ]
        and thread_id
    ):

        # ALWAYS SHOW TOPIC INFORMATION IN LOGS
        logger.info(
            "TELEGRAM TOPIC DETECTED | "
            "CHAT_ID=%s | THREAD_ID=%s | TEXT=%s",
            chat_id,
            thread_id,
            text
        )

        # Only broadcast after we configure the topic ID.
        if (
            ANNOUNCEMENT_TOPIC_ID
            and str(thread_id)
            == str(ANNOUNCEMENT_TOPIC_ID)
        ):

            if not text.startswith("/"):

                sent, failed = (
                    broadcast_announcement(
                        text
                    )
                )

                return jsonify(
                    ok=True,
                    broadcast=True,
                    sent=sent,
                    failed=failed
                )

    # ========================================================
    # ESCALATION
    # ========================================================

    if looks_like_escalation(text):

        alert = (
            "🚨 CEO Exchange Support Alert\n\n"
            f"User: @{username}\n"
            f"User ID: {user.get('id')}\n"
            f"Chat ID: {chat_id}\n"
            f"Chat type: {chat_type}\n"
            f"Thread ID: {thread_id}\n\n"
            f"Message:\n{text}"
        )

        send_message(
            ADMIN_CHAT_ID,
            alert
        )

        send_message(
            chat_id,
            "Got it. I've flagged this for a CEO Exchange "
            "admin. Please keep any payment or order evidence.",
            message_thread_id=thread_id,
            reply_to_message_id=message_id
        )

        return jsonify(
            ok=True
        )

    # ========================================================
    # AI SUPPORT
    # ========================================================

    if bot_was_addressed(message):

        reply = ask_ai(
            text
        )

        send_message(
            chat_id,
            reply,
            message_thread_id=thread_id,
            reply_to_message_id=message_id
        )

    return jsonify(
        ok=True
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/",
    methods=["GET"]
)
def health():

    return "CEO Exchange bot is running."


# ============================================================
# SET WEBHOOK
# ============================================================

@app.route(
    "/set-webhook",
    methods=["GET"]
)
def set_webhook():

    if not PUBLIC_URL:

        return jsonify(
            ok=False,
            error=(
                "PUBLIC_URL environment variable "
                "is not configured."
            )
        ), 400

    try:

        response = requests.get(
            f"{TELEGRAM_API}/setWebhook",
            params={
                "url": (
                    f"{PUBLIC_URL.rstrip('/')}"
                    "/webhook"
                )
            },
            timeout=15
        )

        return jsonify(
            response.json()
        )

    except Exception:

        logger.exception(
            "set_webhook failed"
        )

        return jsonify(
            ok=False,
            error="Failed to configure webhook."
        ), 500


# ============================================================
# START SERVER
# ============================================================

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
