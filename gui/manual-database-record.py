from backend.models import Packet
from backend import database
from datetime import datetime

sample = Packet(
    timestamp=datetime.utcnow().isoformat(),
    sender_ip="127.0.0.1",
    sender_port=12345,
    raw_data='<event uid="TestUnit" time="2025-04-08T12:00:00Z"><point lat="47.6" lon="-122.3" /></event>',
    status="RECEIVED"
)
database.log_packet_obj(sample)