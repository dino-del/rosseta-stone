# backend/database.py

import sqlite3
import os
from backend.models import Packet

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "udp_data_log.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS packets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            sender_ip TEXT,
            sender_port INTEGER,
            raw_data TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()


def log_packet_obj(pkt: Packet):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO packets (timestamp, sender_ip, sender_port, raw_data, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (pkt.timestamp, pkt.sender_ip, pkt.sender_port, pkt.raw_data, pkt.status))
    conn.commit()
    conn.close()


def update_packet_status(packet_id, status, new_data=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if new_data:
        cursor.execute('''
            UPDATE packets
            SET status = ?, raw_data = ?
            WHERE id = ?
        ''', (status, new_data, packet_id))
    else:
        cursor.execute('''
            UPDATE packets
            SET status = ?
            WHERE id = ?
        ''', (status, packet_id))
    conn.commit()
    conn.close()


def fetch_packets_by_status(status="RECEIVED"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, raw_data, timestamp, sender_ip, sender_port
        FROM packets
        WHERE status = ?
    ''', (status,))
    rows = cursor.fetchall()
    conn.close()
    return rows
