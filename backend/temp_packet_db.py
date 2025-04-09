
import sqlite3
import os
from datetime import datetime, timedelta

TEMP_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "temp_msg_log.db")


def init_temp_db():
    conn = sqlite3.connect(TEMP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            sender_ip TEXT,
            sender_port INTEGER,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()


def log_temp_message(timestamp, sender_ip, sender_port, data):
    conn = sqlite3.connect(TEMP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (timestamp, sender_ip, sender_port, data)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, sender_ip, sender_port, data))
    conn.commit()
    conn.close()


def fetch_recent_temp_messages(limit_minutes=10):
    conn = sqlite3.connect(TEMP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, data FROM messages ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    print(f"[DEBUG] FETCHED ALL: {len(rows)} rows")
    conn.close()
    return rows
def debug_print_all_messages():
    print(f"[DEBUG] Reading from DB: {TEMP_DB_PATH}")
    conn = sqlite3.connect(TEMP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, sender_ip, sender_port, data FROM messages")
    rows = cursor.fetchall()
    print(f"[DEBUG] Total messages in DB: {len(rows)}")
    for r in rows:
        print(f"[DB ROW] {r[0]} | {r[1]}:{r[2]} → {r[3][:40]}")
    conn.close()