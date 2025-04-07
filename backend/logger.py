# backend/logger.py

import os
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "udp_data_errors.log")


def log_error(message: str):
    timestamp = datetime.utcnow().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_PATH, "a") as f:
        f.write(f"{timestamp} {message}\n")


def log_info(message: str):
    timestamp = datetime.utcnow().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_PATH, "a") as f:
        f.write(f"{timestamp} INFO: {message}\n")
