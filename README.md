# Bridges AI 🌉

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue?logo=telegram)](https://core.telegram.org/bots)
[![Gemini](https://img.shields.io/badge/Google-Gemini%20API-brightgreen?logo=google)](https://aistudio.google.com/)

**Bridges AI** is a high-performance, privacy-first Telegram bot bridging human interaction with Google's state-of-the-art Gemini AI models. 

Built around the **BYOK (Bring Your Own Key)** architecture, it eliminates costly third-party markups, respects user data privacy, and enables lightning-fast AI interactions directly through Telegram—across direct messages, group chats, and inline mode.

---

## 🌐 Language Versions
- [English (Current)](README.md)
- [Русский (Russian)](README.ru.md)

---

## ✨ Key Features

- 🔑 **BYOK (Bring Your Own Key):** Users connect their personal Google Gemini API key. Zero telemetry, zero token markup, direct API connection.
- 🔐 **Military-Grade Encryption:** User API keys are encrypted at rest using **Fernet (AES-128-CBC + HMAC-SHA256)** authentication before touching the database.
- 💬 **Context-Aware Dialogue Engine:** Multi-turn conversational memory with strict role-alternation validation (`user` ↔ `model`) and automated rolling-window pruning.
- 👥 **Multi-Context Integration:**
  - **Direct Messages:** Full context-rich conversational chat.
  - **Group Chats:** Use `/ai <prompt>` with smart typing indicators and group-safe context.
  - **Inline Mode:** Type `@BotUsername <query>` in any chat across Telegram for on-the-fly answers.
- ⭐️ **Telegram Stars Monetization:** Built-in subscription tiers (1 Month, 3 Months, Lifetime) natively payable via Telegram Stars (`XTR`).
- ⚡ **High-Concurrency SQLite Backend:** Optimized SQLite database running in **WAL mode** (Write-Ahead Logging) protected with reentrant thread synchronization (`RLock`).
- 🛡️ **Anti-Flood & HTML Sanitization:** Built-in sliding TTL rate-limiting and custom HTML entity isolation to prevent code-block corruption and Markdown injection crashes.

---

## 🏗️ Architecture & Security

```
Telegram Client ────────► TeleBot Worker Pool (20 threads)
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
       Database (data.py)             AI Engine (ai_engine.py)
   ┌───────────────────────┐       ┌────────────────────────────┐
   │ SQLite3 (WAL Mode)    │       │ Role Alternation Guard     │
   │ Fernet AES-128 Key Enc│       │ Safety Filter Error Catcher│
   │ 40-Message Rolling Win│       │ Google GenAI Client Pool   │
   └───────────────────────┘       └─────────────┬──────────────┘
                                                 │
                                                 ▼
                                     Google Gemini Cloud API
```

---

## 📋 Prerequisites

- **Python 3.10+**
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- A Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Vancore/BridgesAI-Bot
cd BridgesAI-Bot
```

### 2. Create and Activate a Virtual Environment
```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate Encryption Key & Configure
Generate a secure 32-byte Fernet key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Edit `config.py` (or set up environment variables):
```python
TOKEN = "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ"   # Your Telegram Bot Token
ADMIN_ID = 123456789                              # Your numeric Telegram User ID
encryption_key = b"PASTE_YOUR_GENERATED_KEY_HERE=" # Fernet encryption key in bytes
```

### 5. Launch the Bot
```bash
python bot.py
```

---

## 🕹️ Bot Commands

### User Commands
| Command | Description |
| :--- | :--- |
| `/start` | Launch the bot, view welcome instructions, and trigger 14-day trial |
| `/clear` | Wipe conversation history and reset context memory |
| `/deletekey` | Safely remove the linked Gemini API key and all dialogue history |
| `/status` | Check remaining subscription days and account status |
| `/sub` | Open subscription catalog payable via Telegram Stars |
| `/ai <prompt>` | Trigger AI response inside group chats |

### Inline Mode
Type `@YourBotUsername <query>` inside any chat across Telegram for instant answers.

### Admin Commands
| Command | Format | Description |
| :--- | :--- | :--- |
| `/stats` | `/stats` | View total users, active subscribers, and DB disk footprint |
| `/give` or `/get` | `/give <uid> <days>` | Manually grant or extend Pro days to any user ID |

---

## 📦 Project Structure

```
├── bot.py           # Telegram bot controller, routing, and message handlers
├── ai_engine.py     # Google GenAI API communication & role validation
├── data.py          # Thread-safe SQLite database manager & Fernet encryption
├── core.py          # UI templates, HTML message generators, and keyboards
├── config.py        # Credentials and security configuration
├── requirements.txt # Project dependencies
├── README.md        # English documentation
└── README.ru.md     # Russian documentation
```