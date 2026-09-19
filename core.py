from telebot import types

def start_text(has_key, is_group=False, bot_username=""):
    if not has_key:
        if is_group:
            return (
                "<b>Bridges AI — Group Setup</b>\n\n"
                "To interact with the intelligence in group discussions, "
                "please connect your personal Gemini API key privately.\n\n"
                f"→ <a href='https://t.me/{bot_username}?start=key'>Connect Key in Private</a>"
            )
        return (
            "<b>Bridges AI</b>\n"
            "<i>A seamless bridge between human thought and intelligence.</i>\n\n"
            "No middlemen. No data selling. Unthrottled access directly from Google.\n\n"
            "To ignite the engine, connect your personal Gemini key:\n"
            "→ <b><a href='https://aistudio.google.com/app/apikey'>Get your free API key in 10 seconds</a></b>\n\n"
            "Simply paste the key in your next message."
        )
    return (
        "<b>Bridges AI — Ready.</b>\n\n"
        "The bridge is open. You can interact with the intelligence anywhere:\n"
        "• <b>Direct:</b> Send any thought or question right here\n"
        "• <b>Groups:</b> Use <code>/ai &lt;prompt&gt;</code> in team chats\n"
        f"• <b>Everywhere:</b> Type <code>@{bot_username} &lt;query&gt;</code> in any conversation\n\n"
        "<i>What are we creating today?</i>"
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
    return "<b>Bridges AI:</b> Your access period has expired. Use /sub to renew."

def admin_stats_text(total_users, active_subs, db_size_str):
    return (
        "<b>Bridges AI — Core Metrics ⚙️</b>\n\n"
        f"• <b>Total Registered:</b> {total_users}\n"
        f"• <b>Active Subscriptions:</b> {active_subs}\n"
        f"• <b>Database Footprint:</b> {db_size_str}"
    )