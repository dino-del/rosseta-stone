# backend/listener.py
import socket
import threading
from datetime import datetime

class UDPListener(threading.Thread):
    def __init__(self, port, on_packet):
        super().__init__(daemon=True)
        self.port = port
        self.on_packet = on_packet  # Callback: (data:str, addr:tuple, timestamp:str)
        self.running = False

    def run(self):
        self.running = True
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", self.port))

        while self.running:
            try:
                data, addr = sock.recvfrom(65535)
                timestamp = datetime.now().isoformat()
                decoded = data.decode(errors="replace")
                self.on_packet(decoded, addr, timestamp)
            except Exception as e:
                print(f"[UDPListener] Error: {e}")

        sock.close()

    def stop(self):
        self.running = False
