import os
import logging
import requests
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ceo-exchange-bot")

app = Flask(__name__)

# ---- required environment variables (set these in Render, not in this file) ----
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]             # free, no card - console.groq.com/keys
ADMIN_CHAT_ID = os.environ["ADMIN_CHAT_ID"]          # your personal Telegram chat id (see README)
BOT_USERNAME = os.environ.get("BOT_USERNAME", "")    # your bot's @username, no "@"
PUBLIC_URL = os.environ.get("PUBLIC_URL", "")        # e.g. https://ceo-exchange-bot.onrender.com

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

SYSTEM_PROMPT = """You are the support assistant for CEO Exchange, a P2P crypto trading Telegram group.
You help members understand how P2P trading and merchant orders work: escrow, order limits,
proof of payment, how disputes get resolved, and general platform navigation.

Rules:
- Be concise, direct, and friendly - a few sentences, not an essay, unless asked for detail.
- You do NOT have live access to any specific user's account, balance, or order status. If someone
  asks about a specific order or transaction, tell them clearly you can't see account data and that
  it needs a human admin - don't guess or make up order details.
- Never confirm, deny, or vouch for whether a specific trade or trading partner is safe/legit.
- Never give financial or investment advice (price predictions, "should I buy/sell", etc.) - redirect
  to the Trading Discussion topic for opinions, and be clear those are just community opinions.
- If you're not sure about an exact platform rule (fees, limits, timing), say so plainly rather than
  inventing an answer, and suggest they ping an admin.
- Keep a human, un-corporate tone - this is a trading community, not a bank hotline.
"""

# Phrases that suggest an actual problem, not just a general question - tune this list over time
# based on what you actually see come through.
ESCALATE_KEYWORDS = [
    "scam", "scammed", "didn't receive", "did not receive", "not received",
    "no payment", "didn't pay", "did not pay", "hasn't paid", "has not paid",
    "fraud", "fake proof", "fake receipt", "dispute", "admin help", "need admin",
    "report", "stuck", "problem with order", "blocked me", "won't release",
    "wont release", "refund", "cancelled my order", "canceled my order",
]


def send_message(chat_id, text, message_thread_id=None, reply_to_message_id=None):
    payload = {"chat_id": chat_id, "text": text}
    if message_thread_id:
        payload["message_thread_id"] = message_thread_id
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id
    r = requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=15)
    if not r.ok:
        logger.error("sendMessage failed: %s", r.text)


def ask_ai(user_text):
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "content-type": "application/json",
            },
            json={
                "model": "openai/gpt-oss-20b",  # Updated to current active Groq model
                "max_tokens": 400,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text},
                ],
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        reply = data["choices"][0]["message"]["content"].strip()
        return reply or "Sorry, I couldn't put together a reply just now - try again in a minute."
    except Exception:
        logger.exception("ask_ai failed")
        return "Sorry, I hit an error answering that - an admin can help if it's urgent."


def looks_like_escalation(text):
    t = text.lower()
    return any(kw in t for kw in ESCALATE_KEYWORDS)


def bot_was_addressed(message):
    text = message.get("text", "") or ""
    if message.get("chat", {}).get("type") == "private":
        return True
    if BOT_USERNAME and f"@{BOT_USERNAME}".lower() in text.lower():
        return True
    reply = message.get("reply_to_message")
    if reply:
        replied_user = reply.get("from", {})
        if replied_user.get("is_bot") and replied_user.get("username", "").lower() == BOT_USERNAME.lower():
            return True
    return False


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True, silent=True) or {}
    message = update.get("message") or update.get("edited_message")
    if not message:
        return jsonify(ok=True)

    text = message.get("text", "") or ""
    if not text:
        return jsonify(ok=True)

    chat_id = message["chat"]["id"]
    thread_id = message.get("message_thread_id")
    user = message.get("from", {})
    username = user.get("username") or user.get("first_name", "someone")

    # Escalation runs on every message in the group, regardless of whether the bot was @mentioned -
    # people reporting a real problem usually aren't thinking to tag the bot.
    if looks_like_escalation(text):
        alert = (
            "\U0001F6A8 Possible issue flagged in CEO Exchange\n"
            f"From: @{username} (id {user.get('id')})\n"
            f"Chat: {chat_id}" + (f" (topic id {thread_id})" if thread_id else "") + "\n\n"
            f"Message: {text}"
        )
        send_message(ADMIN_CHAT_ID, alert)
        send_message(
            chat_id,
            "Got it - flagging this for an admin now. Hang tight, someone will jump in.",
            message_thread_id=thread_id,
            reply_to_message_id=message["message_id"],
        )
        return jsonify(ok=True)

    if bot_was_addressed(message):
        reply = ask_ai(text)
        send_message(chat_id, reply, message_thread_id=thread_id, reply_to_message_id=message["message_id"])

    return jsonify(ok=True)


@app.route("/", methods=["GET"])
def health():
    return "CEO Exchange bot is running."


@app.route("/set-webhook", methods=["GET"])
def set_webhook():
    """Visit this URL once after deploying (and again if the URL ever changes)."""
    if not PUBLIC_URL:
        return jsonify(ok=False, error="Set the PUBLIC_URL environment variable first."), 400
    r = requests.get(f"{TELEGRAM_API}/setWebhook", params={"url": f"{PUBLIC_URL.rstrip('/')}/webhook"})
    return jsonify(r.json())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
      
