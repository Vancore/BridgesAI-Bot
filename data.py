import sqlite3
import threading
import os
from cryptography.fernet import Fernet
from config import encryption_key, ADMIN_ID
import time

def connection_lock(func):
    def wrapper(self, *args, **kwargs):
        with self.lock:
            return func(self, *args, **kwargs)
    return wrapper

class Database:
    def __init__ (self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA busy_timeout=5000;")
        self.lock = threading.Lock() 
        self.cipher = Fernet(encryption_key)
        self.create_tables()

    #create
    @connection_lock
    def create_tables(self):
        with self.conn:
            self.conn.execute("""CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, api_key TEXT, pro_until INTEGER DEFAULT 0)""")
            self.conn.execute("""CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, role TEXT, content TEXT)""")
            self.conn.execute("""CREATE INDEX IF NOT EXISTS idx_history_user_id ON history(user_id)""")


    #add
    @connection_lock
    def add_user(self, uid):
        now = int(time.time())
        trial_seconds = 14 * 86400
        trial_until = now + trial_seconds
        with self.conn:
            self.conn.execute("INSERT OR IGNORE INTO users (user_id, pro_until) VALUES (?, ?)", (uid, trial_until))

    #key management
    @connection_lock
    def set_api_key(self, uid, key):
        encrypted_key = self.cipher.encrypt(key.encode()).decode()
        with self.conn:
            self.conn.execute("""INSERT INTO users (user_id, api_key) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET api_key = excluded.api_key""", (uid, encrypted_key))

    @connection_lock
    def get_api_key(self, uid):
        cursor = self.conn.cursor()
        cursor.execute("SELECT api_key FROM users WHERE user_id = ?", (uid,))
        row = cursor.fetchone()
        if row and row[0]:
            try:
                return self.cipher.decrypt(row[0].encode()).decode()
            except Exception:
                return None
        return None

    @connection_lock
    def delete_api_key(self, uid):
        with self.conn:
            self.conn.execute("UPDATE users SET api_key = NULL WHERE user_id = ?", (uid,))


    #history
    @connection_lock
    def add_message(self, uid, role, content):
        with self.conn:
            self.conn.execute("INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)",(uid, role, content))

    @connection_lock
    def get_history(self, uid, limit=20):
        cursor = self.conn.cursor()
        cursor.execute("""SELECT role, content FROM ( SELECT id, role, content FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?) ORDER BY id ASC""", (uid, limit))
        return cursor.fetchall()

    @connection_lock
    def clear_history(self, uid):
        with self.conn:
            self.conn.execute("DELETE FROM history WHERE user_id = ?", (uid,))



    # pro management (помесячная)
    @connection_lock
    def is_pro(self, uid):
        if uid == ADMIN_ID:
            return True
        cursor = self.conn.cursor()
        cursor.execute("SELECT pro_until FROM users WHERE user_id = ?", (uid,))
        row = cursor.fetchone()
        if row and row[0]:
            return row[0] > int(time.time())
        return False

    @connection_lock
    def add_pro_days(self, uid, days=30):
        now = int(time.time())
        seconds_to_add = days * 86400
        cursor = self.conn.cursor()
        cursor.execute("SELECT pro_until FROM users WHERE user_id = ?", (uid,))
        row = cursor.fetchone()
        current_until = row[0] if (row and row[0]) else 0
        if current_until > now:
            new_until = current_until + seconds_to_add
        else:
            new_until = now + seconds_to_add
        with self.conn:
            self.conn.execute("UPDATE users SET pro_until = ? WHERE user_id = ?", (new_until, uid))

    @connection_lock
    def get_pro_expiry(self, uid):
        cursor = self.conn.cursor()
        cursor.execute("SELECT pro_until FROM users WHERE user_id = ?", (uid,))
        row = cursor.fetchone()
        return row[0] if (row and row[0]) else 0




    @connection_lock
    def get_stats(self):
        now = int(time.time())
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE pro_until > ?", (now,))
        active_subs = cursor.fetchone()[0]
        return total_users, active_subs

db = Database("data.db")
            
