import logging
import os
from dotenv import load_dotenv
from datetime import datetime
from enum import Enum
import time
import math
import pytz
from datetime import timedelta

logger = logging.getLogger('root')
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
    LAST_CLOSING_PRICE = 'last_closing_price'
    IN_TRADE = "in_trade"
    CLOSE = "Close"
    LIVE_PNL = "live_pnl"
    POSITION = "position"
    PRICE_ENTRY = "price_entry"
    TIME_IN = "time_in"
    TRADE_DURATION = "trade_duration"


class Exit(Enum):
    PNL = "pnl"
    PRICE_EXIT = "price_exit"
    TIME_OUT = "time_out"


class Current(Enum):
    TRADE_DURATION = "trade_duration"
    LAST_UPDATE_TIME = "last_update_time"

class LTO(Enum):
    LIVE_TRADE = "live_trade"
    CURRENT_IND_VAL = "current_ind_val"
    CURRENT_IND_LONG = "current_ind_long"
    CURRENT_IND_SHORT = "current_ind_short"


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
        logging.error("Unable to get trade duration, will return empty string")
        return ""


def pnl(position, entry_price, exit_price):
    if position == "long":
        return ((exit_price-entry_price)/entry_price)*100
    short_pnl = ((entry_price-exit_price)/entry_price)*100

    return round(short_pnl, 3)


def precision_handling(some_dict) -> dict:
    for key, value in some_dict.items():
        if isinstance(some_dict[key], float):
            if math.floor(some_dict[key]) == 0:
                some_dict[key] = round(some_dict[key], 4)
            else:
                some_dict[key] = round(some_dict[key], 2)
    return some_dict

