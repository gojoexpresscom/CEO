import os
import logging
from datetime import datetime, timezone
from html import escape

import requests
from flask import Flask, request, jsonify


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ceo-exchange-bot")

app = Flask(__name__)


# ============================================================
# REQUIRED ENVIRONMENT VARIABLES
# ============================================================

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
ADMIN_CHAT_ID = os.environ["ADMIN_CHAT_ID"]

BOT_USERNAME = os.environ.get("BOT_USERNAME", "")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "")


# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY",
    ""
)


# ============================================================
# TELEGRAM TOPICS
# ============================================================

# Official announcement topic
ANNOUNCEMENT_TOPIC_ID = os.environ.get(
    "ANNOUNCEMENT_TOPIC_ID",
    ""
)

# New-member welcome topic
WELCOME_TOPIC_ID = os.environ.get(
    "WELCOME_TOPIC_ID",
    ""
)


TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# ============================================================
# CEO EXCHANGE AI SYSTEM PROMPT
# ============================================================

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


# ============================================================
# ESCALATION KEYWORDS
# ============================================================

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
    "canceled my order",
]


# ============================================================
# TELEGRAM DELIVERY ERRORS
# ============================================================

UNREACHABLE_MARKERS = [
    "bot was blocked",
    "user is deactivated",
    "chat not found",
    "peer_id_invalid",
    "bot can't initiate conversation",
    "bot is not a member",
]


# ============================================================
# TIME
# ============================================================

def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# TELEGRAM SEND MESSAGE
# ============================================================

def send_message(
    chat_id,
    text,
    message_thread_id=None,
    reply_to_message_id=None,
    parse_mode=None,
):
    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    if message_thread_id:
        payload["message_thread_id"] = message_thread_id

    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id

    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        response = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json=payload,
            timeout=15,
        )

        if not response.ok:
            logger.error(
                "sendMessage failed chat_id=%s: %s",
                chat_id,
                response.text,
            )

        return response

    except Exception:
        logger.exception(
            "send_message failed chat_id=%s",
            chat_id,
        )

        return None


# ============================================================
# TELEGRAM ERROR CHECK
# ============================================================

def is_unreachable_error(response):
    if response is None:
        return False, "no response from Telegram"

    try:
        data = response.json()
    except Exception:
        return False, getattr(
            response,
            "text",
            None,
        )

    description = data.get(
        "description",
        "",
    )

    lowered = description.lower()

    for marker in UNREACHABLE_MARKERS:
        if marker in lowered:
            return True, description

    return False, description or None


# ============================================================
# SUPABASE CONFIG
# ============================================================

def supabase_configured():
    return bool(
        SUPABASE_URL
        and SUPABASE_SERVICE_ROLE_KEY
    )


def supabase_headers():
    return {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": (
            f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
        ),
        "Content-Type": "application/json",
    }


# ============================================================
# SUBSCRIBERS
# ============================================================

def save_subscriber(
    chat_id,
    username=None,
    first_name=None,
):
    if not supabase_configured():
        logger.warning(
            "Supabase subscriber storage "
            "is not configured."
        )
        return False

    try:
        url = (
            f"{SUPABASE_URL.rstrip('/')}"
            "/rest/v1/telegram_subscribers"
            "?on_conflict=chat_id"
        )

        now = now_iso()

        payload = {
            "chat_id": str(chat_id),
            "username": username,
            "first_name": first_name,
            "subscribed": True,
            "updated_at": now,
            "last_seen_at": now,
        }

        response = requests.post(
            url,
            headers={
                **supabase_headers(),
                "Prefer": (
                    "resolution=merge-duplicates,"
                    "return=minimal"
                ),
            },
            json=payload,
            timeout=15,
        )

        if not response.ok:
            logger.error(
                "save_subscriber failed "
                "chat_id=%s: %s",
                chat_id,
                response.text,
            )
            return False

        return True

    except Exception:
        logger.exception(
            "save_subscriber failed chat_id=%s",
            chat_id,
        )
        return False


def remove_subscriber(chat_id):
    if not supabase_configured():
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
                "subscribed": False,
                "updated_at": now_iso(),
            },
            timeout=15,
        )

        if not response.ok:
            logger.error(
                "remove_subscriber failed "
                "chat_id=%s: %s",
                chat_id,
                response.text,
            )
            return False

        return True

    except Exception:
        logger.exception(
            "remove_subscriber failed chat_id=%s",
            chat_id,
        )
        return False


def touch_last_seen(chat_id):
    if not supabase_configured():
        return

    try:
        url = (
            f"{SUPABASE_URL.rstrip('/')}"
            "/rest/v1/telegram_subscribers"
            f"?chat_id=eq.{chat_id}"
            "&subscribed=eq.true"
        )

        requests.patch(
            url,
            headers=supabase_headers(),
            json={
                "last_seen_at": now_iso()
            },
            timeout=15,
        )

    except Exception:
        logger.exception(
            "touch_last_seen failed chat_id=%s",
            chat_id,
        )


def update_subscriber_stats(
    chat_id,
    total_announcements_sent=None,
    total_delivery_failures=None,
    last_announcement_at=None,
):
    if not supabase_configured():
        return

    payload = {
        "updated_at": now_iso()
    }

    if total_announcements_sent is not None:
        payload[
            "total_announcements_sent"
        ] = total_announcements_sent

    if total_delivery_failures is not None:
        payload[
            "total_delivery_failures"
        ] = total_delivery_failures

    if last_announcement_at is not None:
        payload[
            "last_announcement_at"
        ] = last_announcement_at

    try:
        url = (
            f"{SUPABASE_URL.rstrip('/')}"
            "/rest/v1/telegram_subscribers"
            f"?chat_id=eq.{chat_id}"
        )

        response = requests.patch(
            url,
            headers=supabase_headers(),
            json=payload,
            timeout=15,
        )

        if not response.ok:
            logger.error(
                "update_subscriber_stats failed "
                "chat_id=%s: %s",
                chat_id,
                response.text,
            )

    except Exception:
        logger.exception(
            "update_subscriber_stats failed "
            "chat_id=%s",
            chat_id,
        )


def get_active_subscribers():
    if not supabase_configured():
        return []

    try:
        url = (
            f"{SUPABASE_URL.rstrip('/')}"
            "/rest/v1/telegram_subscribers"
            "?subscribed=eq.true"
            "&select="
            "chat_id,"
            "total_announcements_sent,"
            "total_delivery_failures"
        )

        response = requests.get(
            url,
            headers=supabase_headers(),
            timeout=15,
        )

        if not response.ok:
            logger.error(
                "get_active_subscribers failed: %s",
                response.text,
            )
            return []

        return response.json()

    except Exception:
        logger.exception(
            "get_active_subscribers failed"
        )
        return []


# ============================================================
# ANNOUNCEMENTS
# ============================================================

def create_announcement(
    text,
    topic_id=None,
):
    if not supabase_configured():
        return None

    try:
        url = (
            f"{SUPABASE_URL.rstrip('/')}"
            "/rest/v1/telegram_announcements"
        )

        payload = {
            "message_text": text,
            "topic_id": (
                str(topic_id)
                if topic_id
                else None
            ),
        }

        response = requests.post(
            url,
            headers={
                **supabase_headers(),
                "Prefer": "return=representation",
            },
            json=payload,
            timeout=15,
        )

        if not response.ok:
            logger.error(
                "create_announcement failed: %s",
                response.text,
            )
            return None

        data = response.json()

        if isinstance(data, list) and data:
            return data[0].get("id")

        return None

    except Exception:
        logger.exception(
            "create_announcement failed"
        )
        return None


def update_announcement_totals(
    announcement_id,
    sent,
    failed,
):
    if (
        not supabase_configured()
        or not announcement_id
    ):
        return

    try:
        url = (
            f"{SUPABASE_URL.rstrip('/')}"
            "/rest/v1/telegram_announcements"
            f"?id=eq.{announcement_id}"
        )

        requests.patch(
            url,
            headers=supabase_headers(),
            json={
                "total_sent": sent,
                "total_failed": failed,
            },
            timeout=15,
        )

    except Exception:
        logger.exception(
            "update_announcement_totals failed "
            "announcement_id=%s",
            announcement_id,
        )


def record_delivery(
    announcement_id,
    chat_id,
    status,
    error_message=None,
):
    if (
        not supabase_configured()
        or not announcement_id
    ):
        return

    try:
        url = (
            f"{SUPABASE_URL.rstrip('/')}"
            "/rest/v1/"
            "telegram_announcement_deliveries"
        )

        payload = {
            "announcement_id": announcement_id,
            "chat_id": str(chat_id),
            "status": status,
            "error_message": error_message,
        }

        response = requests.post(
            url,
            headers=supabase_headers(),
            json=payload,
            timeout=15,
        )

        if not response.ok:
            logger.error(
                "record_delivery failed "
                "chat_id=%s: %s",
                chat_id,
                response.text,
            )

    except Exception:
        logger.exception(
            "record_delivery failed chat_id=%s",
            chat_id,
        )


def broadcast_announcement(
    text,
    topic_id=None,
):
    announcement_id = create_announcement(
        text,
        topic_id,
    )

    subscribers = get_active_subscribers()

    sent = 0
    failed = 0
    now = now_iso()

    for subscriber in subscribers:

        chat_id = subscriber.get(
            "chat_id"
        )

        response = send_message(
            chat_id,
            "📢 CEO Exchange Official Announcement\n\n"
            + text,
        )

        if (
            response is not None
            and response.ok
        ):
            sent += 1

            new_sent_total = (
                subscriber.get(
                    "total_announcements_sent"
                )
                or 0
            ) + 1

            update_subscriber_stats(
                chat_id,
                total_announcements_sent=(
                    new_sent_total
                ),
                last_announcement_at=now,
            )

            record_delivery(
                announcement_id,
                chat_id,
                "sent",
            )

            logger.info(
                "Announcement delivered "
                "chat_id=%s",
                chat_id,
            )

        else:
            failed += 1

            unreachable, description = (
                is_unreachable_error(
                    response
                )
            )

            new_failed_total = (
                subscriber.get(
                    "total_delivery_failures"
                )
                or 0
            ) + 1

            update_subscriber_stats(
                chat_id,
                total_delivery_failures=(
                    new_failed_total
                ),
            )

            record_delivery(
                announcement_id,
                chat_id,
                "failed",
                description,
            )

            if unreachable:
                remove_subscriber(
                    chat_id
                )

                logger.info(
                    "Unsubscribed unreachable "
                    "chat_id=%s reason=%s",
                    chat_id,
                    description,
                )

            else:
                logger.warning(
                    "Announcement delivery failed "
                    "chat_id=%s reason=%s",
                    chat_id,
                    description,
                )

    update_announcement_totals(
        announcement_id,
        sent,
        failed,
    )

    logger.info(
        "Broadcast complete "
        "announcement_id=%s "
        "topic_id=%s "
        "sent=%s "
        "failed=%s",
        announcement_id,
        topic_id,
        sent,
        failed,
    )

    return sent, failed


# ============================================================
# WELCOME NEW MEMBERS
# ============================================================

def get_member_display_name(member):
    """
    Get the best human-readable name for a new member.
    """

    first_name = (
        member.get("first_name")
        or ""
    ).strip()

    last_name = (
        member.get("last_name")
        or ""
    ).strip()

    username = (
        member.get("username")
        or ""
    ).strip()

    full_name = " ".join(
        part
        for part in [
            first_name,
            last_name,
        ]
        if part
    ).strip()

    if full_name:
        return full_name

    if username:
        return username

    return "there"


def create_user_mention(member):
    """
    Creates a real Telegram clickable mention.

    This works even when the member does not have
    a Telegram username.
    """

    user_id = member.get("id")

    display_name = escape(
        get_member_display_name(member)
    )

    if user_id:
        return (
            f'<a href="tg://user?id={user_id}">'
            f"{display_name}"
            f"</a>"
        )

    username = (
        member.get("username")
        or ""
    ).strip()

    if username:
        return (
            f"@{escape(username)}"
        )

    return display_name


def send_welcome_message(
    chat_id,
    member,
):
    """
    Send a professional personalized welcome
    to the dedicated WELCOME topic.
    """

    if not WELCOME_TOPIC_ID:
        logger.warning(
            "WELCOME_TOPIC_ID is not configured."
        )
        return None

    mention = create_user_mention(
        member
    )

    welcome_text = f"""👋 <b>Welcome to CEO Exchange, {mention}!</b>

We're pleased to have you with us. 🤝

<b>🏦 What is CEO Exchange?</b>

CEO Exchange is a P2P crypto trading community where members can learn about and participate in P2P trading, merchants, exchange rates, orders, payment verification, security, and more.

<b>🤖 Meet your CEO Exchange AI Support Assistant</b>

I'm here to help whenever you have a question about CEO Exchange or general P2P trading.

You can ask me about:

• P2P trading
• Buy &amp; sell rates
• Merchants
• Orders
• Payment verification
• Escrow
• Security &amp; scam prevention
• General CEO Exchange questions

<b>💬 How do you use the AI?</b>

It's very simple.

You do <b>not</b> need to use a special command.

Just mention <b>@{escape(BOT_USERNAME or "CEO_SupportA_bot")}</b> anywhere in the group and ask your question.

For example:

<code>@{escape(BOT_USERNAME or "CEO_SupportA_bot")} How does P2P trading work?</code>

The AI will respond and explain things as clearly and respectfully as possible.

<b>🔐 Important security reminder</b>

Never share your:

• Password
• OTP or authentication code
• Private key
• Seed phrase
• Sensitive account information

with anyone, including people claiming to be admins or support.

⚠️ For active orders, payment disputes, suspected scams, or account-specific problems, a human CEO Exchange admin may need to review the situation.

<b>Welcome to the CEO Exchange community, {mention}! 🚀</b>

We hope you have a safe, respectful, and great experience with us."""

    return send_message(
        chat_id,
        welcome_text,
        message_thread_id=int(
            WELCOME_TOPIC_ID
        ),
        parse_mode="HTML",
    )


def welcome_new_members(
    chat_id,
    new_members,
):
    """
    Welcome every new member in the WELCOME topic.
    """

    if not new_members:
        return

    if not WELCOME_TOPIC_ID:
        logger.warning(
            "New members detected but "
            "WELCOME_TOPIC_ID is missing."
        )
        return

    for member in new_members:

        # Ignore bots joining the group.
        if member.get("is_bot"):
            logger.info(
                "Skipping welcome for bot "
                "user_id=%s",
                member.get("id"),
            )
            continue

        logger.info(
            "New member joined "
            "user_id=%s username=%s "
            "first_name=%s",
            member.get("id"),
            member.get("username"),
            member.get("first_name"),
        )

        response = send_welcome_message(
            chat_id,
            member,
        )

        if response is not None and response.ok:
            logger.info(
                "Welcome message sent "
                "for user_id=%s "
                "topic_id=%s",
                member.get("id"),
                WELCOME_TOPIC_ID,
            )
        else:
            logger.error(
                "Failed to send welcome "
                "for user_id=%s",
                member.get("id"),
            )


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

You can use /start at any time to subscribe again.""",
    }
    return commands.get(command)


# ============================================================
# GROQ AI
# ============================================================

def ask_ai(user_text):

    try:

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": (
                    f"Bearer {GROQ_API_KEY}"
                ),
                "content-type": (
                    "application/json"
                ),
            },
            json={
                "model": "openai/gpt-oss-20b",
                "max_tokens": 400,
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_text,
                    },
                ],
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        reply = (
            data["choices"][0]["message"]
            ["content"]
            .strip()
        )

        return (
            reply
            or
            "Sorry, I couldn't put together "
            "a reply just now."
        )

    except Exception:

        logger.exception(
            "ask_ai failed"
        )

        return (
            "Sorry, I hit an error answering "
            "that - an admin can help if it's urgent."
        )


# ============================================================
# ESCALATION
# ============================================================

def looks_like_escalation(text):

    lowered = text.lower()

    return any(
        keyword in lowered
        for keyword in ESCALATE_KEYWORDS
    )


# ============================================================
# WAS BOT ADDRESSED?
# ============================================================

def bot_was_addressed(message):

    text = message.get(
        "text",
        "",
    ) or ""

    # Private messages always go to AI.
    if (
        message.get(
            "chat",
            {}
        ).get("type")
        == "private"
    ):
        return True

    # Mention the bot anywhere.
    if (
        BOT_USERNAME
        and
        f"@{BOT_USERNAME}".lower()
        in text.lower()
    ):
        return True

    # Reply directly to the bot.
    reply = message.get(
        "reply_to_message"
    )

    if reply:

        replied_user = reply.get(
            "from",
            {}
        )

        replied_username = (
            replied_user.get(
                "username",
                ""
            )
            or ""
        ).lower()

        if (
            replied_user.get(
                "is_bot"
            )
            and
            BOT_USERNAME
            and
            replied_username
            == BOT_USERNAME.lower()
        ):
            return True

    return False


# ============================================================
# WEBHOOK
# ============================================================

@app.route(
    "/webhook",
    methods=["POST"]
)
def webhook():

    update = (
        request.get_json(
            force=True,
            silent=True,
        )
        or {}
    )

    message = (
        update.get("message")
        or
        update.get("edited_message")
    )

    if not message:
        return jsonify(ok=True)

    # ========================================================
    # NEW MEMBERS
    # ========================================================

    new_members = message.get(
        "new_chat_members"
    )

    if new_members:

        chat = message.get(
            "chat",
            {}
        )

        chat_id = chat.get(
            "id"
        )

        chat_type = chat.get(
            "type"
        )

        if chat_type in [
            "group",
            "supergroup",
        ]:

            welcome_new_members(
                chat_id,
                new_members,
            )

        return jsonify(
            ok=True
        )

    # ========================================================
    # TEXT
    # ========================================================

    text = message.get(
        "text",
        "",
    ) or ""

    if not text:
        return jsonify(
            ok=True
        )

    chat = message.get(
        "chat",
        {}
    )

    chat_id = chat.get(
        "id"
    )

    message_id = message.get(
        "message_id"
    )

    thread_id = message.get(
        "message_thread_id"
    )

    user = message.get(
        "from",
        {}
    )

    username = (
        user.get("username")
        or
        user.get("first_name")
        or
        "someone"
    )

    first_name = user.get(
        "first_name"
    )

    chat_type = chat.get(
        "type"
    )


    # ========================================================
    # LOG EVERY INCOMING MESSAGE
    # ========================================================

    logger.info(
        "Incoming message "
        "chat_id=%s "
        "message_id=%s "
        "thread_id=%s "
        "username=%s "
        "chat_type=%s "
        "text=%r",
        chat_id,
        message_id,
        thread_id,
        username,
        chat_type,
        text[:200],
    )


    # ========================================================
    # PRIVATE CHAT ACTIVITY
    # ========================================================

    if chat_type == "private":

        touch_last_seen(
            chat_id
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

            if chat_type == "private":

                saved = save_subscriber(
                    chat_id,
                    username,
                    first_name,
                )

                reply = handle_command(
                    text
                )

                if not saved:

                    reply += (
                        "\n\n⚠️ I couldn't save "
                        "your announcement "
                        "subscription right now."
                    )

            else:

                reply = handle_command(
                    text
                )

            send_message(
                chat_id,
                reply,
                message_thread_id=thread_id,
                reply_to_message_id=message_id,
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
                reply_to_message_id=message_id,
            )

            return jsonify(
                ok=True
            )


        # ----------------------------------------------------
        # ADMIN SUBSCRIBERS
        # ----------------------------------------------------

        if command == "/subscribers":

            if (
                str(chat_id)
                !=
                str(ADMIN_CHAT_ID)
            ):

                send_message(
                    chat_id,
                    "This command is only available "
                    "to the CEO Exchange administrator.",
                )

                return jsonify(
                    ok=True
                )

            subscriber_count = len(
                get_active_subscribers()
            )

            send_message(
                chat_id,
                "📊 CEO Exchange "
                "Announcement Subscribers\n\n"
                f"Active subscribers: "
                f"{subscriber_count}",
            )

            return jsonify(
                ok=True
            )


        # ----------------------------------------------------
        # OTHER COMMANDS
        # ----------------------------------------------------

        command_reply = handle_command(
            text
        )

        if command_reply:

            send_message(
                chat_id,
                command_reply,
                message_thread_id=thread_id,
                reply_to_message_id=message_id,
            )

            return jsonify(
                ok=True
            )


    # ========================================================
    # OFFICIAL ANNOUNCEMENT
    # ========================================================

    if (
        chat_type
        in [
            "group",
            "supergroup",
        ]
        and
        thread_id
        and
        ANNOUNCEMENT_TOPIC_ID
        and
        str(thread_id)
        ==
        str(ANNOUNCEMENT_TOPIC_ID)
        and
        not text.startswith("/")
    ):

        logger.info(
            "Processing announcement "
            "chat_id=%s "
            "topic_id=%s "
            "message_id=%s",
            chat_id,
            thread_id,
            message_id,
        )

        sent, failed = (
            broadcast_announcement(
                text,
                topic_id=thread_id,
            )
        )

        return jsonify(
            ok=True,
            broadcast=True,
            sent=sent,
            failed=failed,
        )


    # ========================================================
    # ESCALATION
    # ========================================================

    if looks_like_escalation(
        text
    ):

        alert = (
            "🚨 Possible issue flagged "
            "in CEO Exchange\n"
            f"From: @{username} "
            f"(id {user.get('id')})\n"
            f"Chat: {chat_id}"
            +
            (
                f" (topic id {thread_id})"
                if thread_id
                else ""
            )
            +
            "\n\n"
            f"Message: {text}"
        )

        send_message(
            ADMIN_CHAT_ID,
            alert,
        )

        send_message(
            chat_id,
            "Got it - flagging this for an admin now. "
            "Hang tight, someone will jump in.",
            message_thread_id=thread_id,
            reply_to_message_id=message_id,
        )

        logger.info(
            "Escalation flagged "
            "chat_id=%s "
            "user=%s "
            "thread_id=%s",
            chat_id,
            username,
            thread_id,
        )

        return jsonify(
            ok=True
        )


    # ========================================================
    # AI SUPPORT
    # ========================================================

    # IMPORTANT:
    # The AI only answers when:
    #
    # 1. User is in private chat
    # 2. User mentions the bot
    # 3. User replies directly to the bot
    #
    # Ordinary group messages are ignored.

    if bot_was_addressed(
        message
    ):

        reply = ask_ai(
            text
        )

        send_message(
            chat_id,
            reply,
            message_thread_id=thread_id,
            reply_to_message_id=message_id,
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

    return (
        "CEO Exchange bot is running."
    )


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
                "Set the PUBLIC_URL "
                "environment variable first."
            ),
        ), 400

    response = requests.get(
        f"{TELEGRAM_API}/setWebhook",
        params={
            "url": (
                f"{PUBLIC_URL.rstrip('/')}"
                "/webhook"
            )
        },
        timeout=15,
    )

    return jsonify(
        response.json()
    )


# ============================================================
# START FLASK
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000,
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
    )
