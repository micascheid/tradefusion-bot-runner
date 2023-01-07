import os
from dotenv import load_dotenv
from datetime import datetime
from enum import Enum
from datetime import timedelta

load_dotenv()
DB_URL = os.getenv('db_url')
LIVE_PNL = "live_pnl"
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


class Entry(Enum):
    CLOSE = "Close"
    LIVE_PNL = "live_pnl"
    POSITION = "position"
    PRICE_ENTRY = "price_entry"
    TIME_IN = "time_in"


class Exit(Enum):
    PNL = "pnl"
    PRICE_EXIT = "price_exit"
    TIME_OUT = "time_out"
    TRADE_DURATION = "trade_duration"


def trade_duration(entry_time, exit_time):
    try:
        dt_entry = datetime.strptime(entry_time, '%Y-%m-%d %H:%M:%S%z')
        dt_exit = datetime.strptime(exit_time, '%Y-%m-%d %H:%M:%S%z')
        time_length = dt_exit - dt_entry

        s = time_length.total_seconds()
        days, remainder = divmod(s, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        return '{:02}:{:02}:{:02}'.format(int(days), int(hours), int(minutes))
    except ValueError:
        print("Unable to get trade duration, will return emty string")
        return ""


def pnl(position, entry_price, exit_price):
    if position == "long":
        return ((exit_price-entry_price)/entry_price)*100
    short_pnl = ((entry_price-exit_price)/entry_price)*100

    return round(short_pnl, 3)
