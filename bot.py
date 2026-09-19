import telebot
from config import TOKEN, ADMIN_ID
from data import db
import core
import ai_engine
from telebot.apihelper import ApiTelegramException
import time
import threading
from telebot import types
from cachetools import TTLCache
import html
import re
import os


bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=20)

flood_cache = TTLCache(maxsize=10000, ttl=1.0)
flood_lock = threading.Lock()

BOT_USERNAME = bot.get_me().username

def is_flooding(uid):
    with flood_lock:
        if uid in flood_cache:
            return True
        flood_cache[uid] = True
        return False


def markdown_to_html(text):
    if not text:
        return ""
    text = html.escape(text)
    code_blocks = []
    def save_pre(m):
        code_blocks.append(f"<pre>{m.group(1)}</pre>")
        return f"%%%CODE_BLOCK_{len(code_blocks)-1}%%%"
    def save_code(m):
        code_blocks.append(f"<code>{m.group(1)}</code>")
        return f"%%%CODE_BLOCK_{len(code_blocks)-1}%%%"
    text = re.sub(r"```(?:[a-zA-Z0-9_-]+)?\n?(.*?)```", save_pre, text, flags=re.DOTALL)
    text = re.sub(r"`([^`\n]+)`", save_code, text)
    text = re.sub(r"!\[([^\]]*)\]\((https?://[^\s)]+)\)", r'<a href="\2">🖼 \1</a>', text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"^\s*[-*_]{3,}\s*$", r"—" * 15, text, flags=re.MULTILINE)
    text = re.sub(r"^(?:#{1,6})\s+(.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*&gt;\s*(.+)$", r"<blockquote>\1</blockquote>", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<b><i>\1</i></b>", text)
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"^[\*\-]\s+(.+)$", r"• \1", text, flags=re.MULTILINE)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    for idx, block in enumerate(code_blocks):
        text = text.replace(f"%%%CODE_BLOCK_{idx}%%%", block)

    return text

def send_smart(chat_id, text):
    MAX_LEN = 3800
    if len(text) > MAX_LEN:
        for i in range(0, len(text), MAX_LEN):
            chunk = text[i:i + MAX_LEN]
            bot.send_message(chat_id, chunk)
        return
    formatted_text = markdown_to_html(text)
    try:
        bot.send_message(chat_id, formatted_text, parse_mode="HTML")
    except Exception:
        bot.send_message(chat_id, text)


@bot.message_handler(commands=['start'])
def start_handler(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if is_flooding(uid):
        return
    db.add_user(uid)
    is_group = message.chat.type != 'private'
    has_key = db.get_api_key(uid) is not None
    bot_username = BOT_USERNAME
    text = core.start_text(has_key, is_group=is_group, bot_username=bot_username)
    bot.send_message(chat_id, text, parse_mode="HTML")


@bot.message_handler(commands=['clear'])
def clear_history_handler(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if is_flooding(uid):
        return
    if message.chat.type != 'private':
        bot.send_message(chat_id, "Conversation memory is only maintained in private chat.")
        return
    db.clear_history(uid)
    bot.send_message(chat_id, core.history_cleared(), parse_mode="HTML")


@bot.message_handler(commands=['deletekey'])
def reset_key_handler(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if is_flooding(uid):
        return
    if message.chat.type != 'private':
        bot.send_message(chat_id, "API keys can only be managed in private chat.")
        return
    if not db.get_api_key(uid):
        bot.send_message(chat_id, core.no_key_to_reset_text(), parse_mode="HTML")
        return
    db.delete_api_key(uid)
    db.clear_history(uid)
    bot.send_message(chat_id, core.key_reset_text(), parse_mode="HTML")


@bot.message_handler(commands=['ai'])
def group_ai_handler(message):
    if message.chat.type == 'private':
        return
    uid = message.from_user.id
    chat_id = message.chat.id
    if is_flooding(uid):
        return
    parts = message.text.split(None, 1)
    if len(parts) < 2:
        send_smart(chat_id, "Please include your prompt after /ai.")
        return
    text = parts[1].strip()
    key = db.get_api_key(uid)
    if not key:
        bot_username = BOT_USERNAME
        name = message.from_user.first_name or "there"
        name = html.escape(message.from_user.first_name or "there")
        bot.send_message(chat_id, core.group_no_key_text(bot_username, name), parse_mode="HTML")
        return
    if not db.is_pro(uid):
        bot_username = BOT_USERNAME
        name = message.from_user.first_name or "there"
        name = html.escape(message.from_user.first_name or "there")
        bot.send_message(chat_id, core.group_no_pro_text(bot_username, name), parse_mode="HTML")
        return
    bot.send_chat_action(chat_id, "typing")
    ok, msg = ai_engine.send_message(key, [], text)
    send_smart(chat_id, msg)



@bot.message_handler(commands=['sub'])
def donate_handler(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if is_flooding(uid):
        return
    if message.chat.type != 'private':
        bot.send_message(chat_id, "Subscriptions can only be purchased in private chat.")
        return
    bot.send_message(chat_id, core.donate_menu_text(), reply_markup=core.donate_markup(), parse_mode="HTML")


@bot.message_handler(commands=['status'])
def status_handler(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if is_flooding(uid):
        return
    is_admin = (uid == ADMIN_ID)
    is_active = db.is_pro(uid)
    expiry = db.get_pro_expiry(uid)
    now = int(time.time())
    is_lifetime = False
    days_left = 0
    if is_active and not is_admin:
        diff = expiry - now
        if diff > 10 * 365 * 86400:
            is_lifetime = True
        else:
            days_left = max(0, diff // 86400)
    text = core.status_text(
        days_left=days_left,
        is_active=is_active,
        is_lifetime=is_lifetime,
        is_admin=is_admin
    )
    bot.send_message(chat_id, text, parse_mode="HTML")


@bot.message_handler(commands=['stats'])
def admin_stats_handler(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if is_flooding(uid):
        return
    if uid != ADMIN_ID:
        return
    total_users, active_subs = db.get_stats()
    db_file = "data.db"
    total_bytes = 0
    for file in [db_file, f"{db_file}-wal", f"{db_file}-shm"]:
        if os.path.exists(file):
            total_bytes += os.path.getsize(file)
    if total_bytes < 1024 * 1024:
        db_size_str = f"{total_bytes / 1024:.2f} KB"
    else:
        db_size_str = f"{total_bytes / (1024 * 1024):.2f} MB"
    bot.send_message(chat_id, core.admin_stats_text(total_users, active_subs, db_size_str), parse_mode="HTML")


@bot.message_handler(commands=['get', 'give'])
def give_days_handler(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if uid != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) != 3:
        bot.send_message(
            chat_id, 
            "<b>Format:</b> <code>/get &lt;uid&gt; &lt;days&gt;</code>\nExample: <code>/get 123456789 30</code>", 
            parse_mode="HTML"
        )
        return
    try:
        target_uid = int(parts[1])
        days = int(parts[2])
    except ValueError:
        bot.send_message(chat_id, "Error: UID and days must be valid integers.")
        return
    if days <= 0:
        bot.send_message(chat_id, "Error: Days count must be greater than zero.")
        return
    db.add_pro_days(target_uid, days=days)
    new_expiry = db.get_pro_expiry(target_uid)
    date_str = time.strftime("%b %d, %Y", time.localtime(new_expiry))
    bot.send_message(
        chat_id,
        f"<b>Access Granted.</b>\n"
        f"• <b>User ID:</b> <code>{target_uid}</code>\n"
        f"• <b>Added:</b> {days} days\n"
        f"• <b>Active until:</b> {date_str}",
        parse_mode="HTML"
    )
    try:
        bot.send_message(
            target_uid,
            f"<b>Bridges AI — Access Extended.</b>\n"
            f"Your access has been extended by <b>{days}</b> days.\n"
            f"Active until: <b>{date_str}</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass


@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_sub:"))
def send_sub_invoice(call):
    uid = call.from_user.id
    plan = call.data.split(":")[1]
    plans = {
        "30": {
            "title": "Bridges AI — 1 Month Access",
            "desc": "30 days of full access to Bridges AI across all chats.",
            "stars": 75,
            "payload": "sub_30"
        },
        "90": {
            "title": "Bridges AI — 3 Months Access",
            "desc": "90 days of full access with reduced rate.",
            "stars": 150,
            "payload": "sub_90"
        },
        "lifetime": {
            "title": "Bridges AI — Lifetime Access",
            "desc": "Unlimited lifetime access to Bridges AI.",
            "stars": 499,
            "payload": "sub_lifetime"
        }
    }
    if plan not in plans:
        return
    item = plans[plan]
    prices = [types.LabeledPrice(label=item["title"], amount=item["stars"])]
    bot.send_invoice(
        chat_id=call.message.chat.id,
        title=item["title"],
        description=item["desc"],
        invoice_payload=item["payload"],
        provider_token="",
        currency="XTR",
        prices=prices
    )
    bot.answer_callback_query(call.id)


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    uid = message.chat.id
    payload = message.successful_payment.invoice_payload
    if payload == "sub_30":
        db.add_pro_days(uid, days=30)
        plan_name = "1 Month (30 Days)"
    elif payload == "sub_90":
        db.add_pro_days(uid, days=90)
        plan_name = "3 Months (90 Days)"
    elif payload == "sub_lifetime":
        db.add_pro_days(uid, days=36500)
        plan_name = "Lifetime Access"
    else:
        db.add_pro_days(uid, days=30)
        plan_name = "Standard Access"
    bot.send_message(uid, core.payment_success_text(plan_name), parse_mode="HTML")



@bot.message_handler(func=lambda message: True, content_types=['text'])
def all_handler(message):
    uid = message.chat.id
    if message.chat.type != 'private':
        return
    if is_flooding(uid):
        return
    text = message.text.strip()
    key = db.get_api_key(uid)
    if not key:
        ok, msg = ai_engine.validate_key(text)
        if ok:
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except Exception:
                pass
            db.set_api_key(uid, text)
        send_smart(uid, msg)
        return
    if not db.is_pro(uid):
        bot.send_message(uid, core.not_pro(), parse_mode="HTML")
        return
    bot.send_chat_action(uid, "typing")
    history = db.get_history(uid)
    ok, msg = ai_engine.send_message(key, history, text)
    if ok:
        db.add_message(uid, "user", text)
        db.add_message(uid, "model", msg)
    send_smart(uid, msg)




@bot.inline_handler(func=lambda query: True)
def inline_query_handler(query):
    uid = query.from_user.id
    user_text = query.query.strip()
    if is_flooding(uid):
        return
    if len(user_text) < 3:
        return
    bot_username = BOT_USERNAME
    key = db.get_api_key(uid)
    if not key:
        no_key_article = types.InlineQueryResultArticle(
            id="no_key",
            title="API Key Required",
            description=f"Open private chat with @{bot_username} to connect your key.",
            input_message_content=types.InputTextMessageContent(
                message_text=f"Please connect your Gemini API key in private chat with @{bot_username} first."
            )
        )
        try:
            bot.answer_inline_query(query.id, [no_key_article], cache_time=1, is_personal=True)
        except Exception:
            pass
        return
    if not db.is_pro(uid):
        no_sub_article = types.InlineQueryResultArticle(
            id="no_sub",
            title="Subscription Expired",
            description="Your access has expired. Click to view how to renew.",
            input_message_content=types.InputTextMessageContent(
                message_text=f"⚠️ My Bridges AI access has expired. Renewing via @{bot_username}."
            )
        )
        try:
            bot.answer_inline_query(query.id, [no_sub_article], cache_time=1, is_personal=True)
        except Exception:
            pass
        return
    ok, ai_response = ai_engine.send_message(key, [], user_text)
    if not ok:
        error_article = types.InlineQueryResultArticle(
            id="error",
            title="Execution Error",
            description=ai_response,
            input_message_content=types.InputTextMessageContent(message_text=ai_response)
        )
        try:
            bot.answer_inline_query(query.id, [error_article], cache_time=1, is_personal=True)
        except Exception:
            pass
        return
    if len(ai_response) > 3000:
        too_long_article = types.InlineQueryResultArticle(
            id="too_long",
            title="Response Too Long",
            description="The answer is too detailed for inline mode. Use bot chat.",
            input_message_content=types.InputTextMessageContent(
                message_text=f"⚠️ This response exceeds the inline limit.\nPlease ask @{bot_username} directly in a private chat."
            )
        )
        try:
            bot.answer_inline_query(query.id, [too_long_article], cache_time=5, is_personal=True)
        except Exception:
            pass
        return
    short_preview = ai_response[:80].replace("\n", " ") + "..."
    try:
        formatted_html = markdown_to_html(ai_response)
        article = types.InlineQueryResultArticle(
            id="gemini_res",
            title="Bridges AI Response",
            description=short_preview,
            input_message_content=types.InputTextMessageContent(
                message_text=formatted_html,
                parse_mode="HTML"
            )
        )
        bot.answer_inline_query(query.id, [article], cache_time=5, is_personal=True)
    except Exception:
        try:
            fallback = types.InlineQueryResultArticle(
                id="gemini_res",
                title="Bridges AI Response",
                description=short_preview,
                input_message_content=types.InputTextMessageContent(
                    message_text=ai_response,
                    parse_mode=None
                )
            )
            bot.answer_inline_query(query.id, [fallback], cache_time=5, is_personal=True)
        except Exception:
            pass


bot.infinity_polling()