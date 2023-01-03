import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv('db_url')

TIME_FRAME_TO_SEC = {
    "5m": 300,
    "30m": 1800,
    "1h": 3600,
    "2h": 7200,
    "4h": 14400
}

INTERVAL_UNITS = {
    "m": "minutes",
    "h": "hours",
    "d": "days",
    "w": "weeks"
}
