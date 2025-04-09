# udp_data_router_gui.py
# Author: James Di Natale
# Enhanced UDP listener and re-broadcaster with dynamic transformation, GUI, and format control

import socket
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import time
from datetime import datetime
import xml.etree.ElementTree as ET
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(SCRIPT_DIR, "telemetry_log.db")
ERROR_LOG = os.path.join(SCRIPT_DIR, "udp_router_errors.txt")

if not os.path.exists(ERROR_LOG):
    with open(ERROR_LOG, "w") as f:
        f.write("[Error Log Initialized]\n\n")

message_counts = {"RECEIVED": 0, "FORWARDED": 0, "IGNORED": 0, "ERROR": 0}

current_packet = ""

# === Database Functions ===
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
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

def insert_log(timestamp, sender, data, status="RECEIVED"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO telemetry (timestamp, sender_ip, sender_port, raw_data, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, sender[0], sender[1], data, status))
    conn.commit()
    conn.close()

def fetch_unprocessed():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, raw_data FROM telemetry WHERE status = 'RECEIVED'")
    results = cursor.fetchall()
    conn.close()
    return results

def update_status(log_id, status, data=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if data:
        cursor.execute("UPDATE telemetry SET status=?, raw_data=? WHERE id=?", (status, data, log_id))
    else:
        cursor.execute("UPDATE telemetry SET status=? WHERE id=?", (status, log_id))
    conn.commit()
    conn.close()

# === Formatter Functions ===
def transform(data, fmt, overrides):
    try:
        root = ET.fromstring(data.strip())
        uid = overrides.get("uid") or root.attrib.get("uid", "unknown")
        timestamp = overrides.get("timestamp") or root.attrib.get("time", datetime.now().isoformat())
        point = root.find("point")
        lat = overrides.get("lat") or point.attrib.get("lat", "0")
        lon = overrides.get("lon") or point.attrib.get("lon", "0")
        alt = overrides.get("alt") or point.attrib.get("hae", "0")

        if fmt == "Simdis XML":
            return f'<simdis><platform id="{uid}" lat="{lat}" lon="{lon}" alt="{alt}" time="{timestamp}"/></simdis>'
        elif fmt == "JSON":
            return json.dumps({"uid": uid, "lat": lat, "lon": lon, "alt": alt, "timestamp": timestamp})
        elif fmt == "Raw XML":
            return data
        elif fmt == "CoT":
            return f'<event version="2.0" uid="{uid}" type="a-f-G" time="{timestamp}" start="{timestamp}" stale="{timestamp}"><point lat="{lat}" lon="{lon}" hae="{alt}" ce="9999.0" le="9999.0"/></event>'
        else:
            raise ValueError("Unsupported format")
    except Exception as e:
        raise ValueError(f"Transform error: {e}")

# === Forwarder Classes ===
class Forwarder:
    def __init__(self, protocol, ip, port):
        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.sock = None

    def connect(self):
        if self.protocol == "TCP":
            try:
                self.sock = socket.create_connection((self.ip, self.port))
                return True
            except:
                return False
        elif self.protocol == "UDP":
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return True

    def send(self, data):
        try:
            if self.protocol == "TCP":
                self.sock.sendall(data.encode())
            else:
                self.sock.sendto(data.encode(), (self.ip, self.port))
            return True
        except:
            return False

# === Listener ===
class UDPListener:
    def __init__(self, port, on_packet):
        self.port = port
        self.running = False
        self.on_packet = on_packet

    def start(self):
        self.running = True
        threading.Thread(target=self.listen, daemon=True).start()

    def stop(self):
        self.running = False

    def listen(self):
        init_db()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", self.port))
        while self.running:
            data, addr = sock.recvfrom(65535)
            text = data.decode(errors="replace")
            global current_packet
            current_packet = text
            insert_log(datetime.now().isoformat(), addr, text)
            message_counts["RECEIVED"] += 1
            self.on_packet(text)
        sock.close()

# === GUI ===
class RouterGUI:
    def __init__(self, master):
        self.master = master
        master.title("UDP Router")

        self.listener = None
        self.forwarder = None

        tk.Label(master, text="UDP Listen Port").pack()
        self.port_entry = tk.Entry(master)
        self.port_entry.insert(0, "40000")
        self.port_entry.pack()

        tk.Label(master, text="Forwarding Protocol").pack()
        self.protocol_cb = ttk.Combobox(master, values=["TCP", "UDP"])
        self.protocol_cb.set("TCP")
        self.protocol_cb.pack()

        tk.Label(master, text="Destination IP").pack()
        self.ip_entry = tk.Entry(master)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack()

        tk.Label(master, text="Destination Port").pack()
        self.dest_entry = tk.Entry(master)
        self.dest_entry.insert(0, "50000")
        self.dest_entry.pack()

        tk.Label(master, text="Output Format").pack()
        self.format_cb = ttk.Combobox(master, values=["Simdis XML", "CoT", "JSON", "Raw XML"])
        self.format_cb.set("Simdis XML")
        self.format_cb.pack()

        tk.Label(master, text="Override UID").pack()
        self.uid_entry = tk.Entry(master)
        self.uid_entry.pack()

        tk.Label(master, text="Override Lat, Lon, Alt").pack()
        self.lat_entry = tk.Entry(master)
        self.lon_entry = tk.Entry(master)
        self.alt_entry = tk.Entry(master)
        self.lat_entry.pack()
        self.lon_entry.pack()
        self.alt_entry.pack()

        self.start_btn = tk.Button(master, text="Start Listener", command=self.start)
        self.start_btn.pack(pady=5)

        self.packet_view = tk.Text(master, height=10, wrap="word")
        self.packet_view.pack()

    def on_packet_received(self, text):
        self.packet_view.delete("1.0", tk.END)
        self.packet_view.insert(tk.END, text)

    def start(self):
        port = int(self.port_entry.get())
        self.listener = UDPListener(port, self.on_packet_received)
        self.listener.start()

        self.forwarder = Forwarder(self.protocol_cb.get(), self.ip_entry.get(), int(self.dest_entry.get()))
        if self.forwarder.connect():
            threading.Thread(target=self.forward_loop, daemon=True).start()

    def forward_loop(self):
        while True:
            for log_id, raw in fetch_unprocessed():
                try:
                    formatted = transform(raw, self.format_cb.get(), {
                        "uid": self.uid_entry.get(),
                        "lat": self.lat_entry.get(),
                        "lon": self.lon_entry.get(),
                        "alt": self.alt_entry.get(),
                        "timestamp": None
                    })
                    if self.forwarder.send(formatted):
                        update_status(log_id, "FORWARDED", formatted)
                    else:
                        update_status(log_id, "ERROR")
                except:
                    update_status(log_id, "IGNORED")
            time.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = RouterGUI(root)
    root.mainloop()