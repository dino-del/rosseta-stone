# backend/forwarder.py

import socket
import threading


class Forwarder:
    def __init__(self, protocol="TCP", ip="127.0.0.1", port=50000):
        self.protocol = protocol.upper()
        self.ip = ip
        self.port = port
        self.lock = threading.Lock()
        self.sock = None

    def send(self, message: str):
        if self.protocol == "TCP":
            return self._send_tcp(message)
        elif self.protocol == "UDP":
            return self._send_udp(message)
        else:
            raise ValueError("Unsupported protocol: " + self.protocol)

    def _send_tcp(self, message: str):
        with self.lock:
            if not self.sock:
                try:
                    self.sock = socket.create_connection((self.ip, self.port), timeout=3)
                except Exception as e:
                    print(f"[Forwarder] TCP connect failed: {e}")
                    self.sock = None
                    return False
            try:
                self.sock.sendall(message.encode("utf-8"))
                return True
            except Exception as e:
                print(f"[Forwarder] TCP send error: {e}")
                self.sock = None
                return False

    def _send_udp(self, message: str):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(message.encode("utf-8"), (self.ip, self.port))
            sock.close()
            return True
        except Exception as e:
            print(f"[Forwarder] UDP send error: {e}")
            return False

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        self.sock = None
