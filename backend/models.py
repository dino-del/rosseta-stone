# backend/models.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Packet:
    timestamp: str
    sender_ip: str
    sender_port: int
    raw_data: str
    status: str = "RECEIVED"


@dataclass
class Overrides:
    uid: Optional[str] = None
    lat: Optional[str] = None
    lon: Optional[str] = None
    alt: Optional[str] = None

    def to_dict(self):
        return {k: v for k, v in vars(self).items() if v is not None}
