from data import db
from telebot import types
import time

def start_text(has_key, is_group=False, bot_username=""):
    if not has_key:
        if is_group:
            return (
                "<b>Bridges AI — Group Setup.</b>\n"
                "A seamless bridge between human thought and intelligence.\n\n"
                "To interact in groups, please connect your Gemini API key privately.\n\n"
                f"👉 <a href='https://t.me/{bot_username}?start=key'>Connect API Key in Private</a>"
            )
        return (
            "<b>Bridges AI.</b>\n"
            "A seamless bridge between human thought and intelligence.\n\n"
            "To begin, connect your personal Gemini API key.\n"
            "You can get one in seconds right here:\n"
            "https://aistudio.google.com/app/apikey\n\n"
            "Simply send the key in your next message."
        )
    return (
        "<b>Bridges AI.</b>\n"
        "The system is ready. What are we creating today?"
    )

def group_no_key_text(bot_username, user_name):
    return (
        f"<b>Bridges AI.</b>\n"
        f"Hello, {user_name}. To use the assistant, please connect your Gemini API key in a private chat for security.\n\n"
        f"👉 <a href='https://t.me/{bot_username}?start=key'>Click here to connect your key</a>"
    )


def group_no_pro_text(bot_username, user_name):
    return (
        f"<b>Bridges AI — Access Required.</b>\n"
        f"Hello, {user_name}. Your access period has expired.\n\n"
        f"To continue using the assistant in group chats, please renew your subscription in private:\n"
        f"👉 <a href='https://t.me/{bot_username}'>Renew Access</a>"
    )

def not_pro():
    return (
        "<b>Bridges AI — Access Expired.</b>\n"
        "Your active subscription has ended.\n\n"
        "Please renew your access to continue interacting with the system."
    )


def history_cleared():
    return (
        "<b>Bridges AI — Context Cleared.</b>\n"
        "Your conversation memory has been wiped. Starting fresh."
    )

def key_reset_text():
    return (
        "<b>Bridges AI — Key Reset.</b>\n"
        "Your API key and context have been completely removed.\n\n"
        "Send your new Gemini API key in the next message to reconnect."
    )

def no_key_to_reset_text():
    return (
        "<b>Bridges AI.</b>\n"
        "You don't have an active API key linked yet.\n\n"
        "Simply send your key here to connect."
    )


def donate_menu_text():
    return (
        "<b>Bridges AI — Access Extension.</b>\n"
        "Support the infrastructure and unlock uninterrupted access to the model.\n\n"
        "Choose your access plan below:"
    )

def donate_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_1m = types.InlineKeyboardButton("⭐️ 1 Month — 75 Stars", callback_data="buy_sub:30")
    btn_3m = types.InlineKeyboardButton("⭐️ 3 Months — 150 Stars", callback_data="buy_sub:90")
    btn_life = types.InlineKeyboardButton("♾️ Lifetime Access — 499 Stars", callback_data="buy_sub:lifetime")
    markup.add(btn_1m, btn_3m, btn_life)
    return markup

def payment_success_text(plan_name):
    return (
        "<b>Bridges AI — Access Extended!</b> ⭐️\n\n"
        f"Your plan: <b>{plan_name}</b> has been successfully activated.\n"
        "Thank you for supporting Bridges AI. The system is fully operational."
    )



def status_text(days_left, is_active, is_lifetime=False, is_admin=False):
    if is_admin:
        return "<b>Bridges AI:</b> Unlimited administrator access."
    if is_lifetime:
        return "<b>Bridges AI:</b> Lifetime access active ♾️"
    if is_active:
        return f"<b>Bridges AI:</b> {days_left} days of access remaining."
    return "<b>Bridges AI:</b> Your access period has expired. Use /donate to renew."

def admin_stats_text(total_users, active_subs, db_size_str):
    return (
        "<b>Bridges AI — Core Metrics ⚙️</b>\n\n"
        f"• <b>Total Registered:</b> {total_users}\n"
        f"• <b>Active Subscriptions:</b> {active_subs}\n"
        f"• <b>Database Footprint:</b> {db_size_str}"
    )