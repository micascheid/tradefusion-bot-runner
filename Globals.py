import os
from dotenv import load_dotenv
from datetime import datetime
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

def trade_duration(entry_time, exit_time):
    try:
        dt_entry = datetime.strptime(entry_time, '%Y-%m-%d H:%M:%S%z')
        dt_exit = datetime.strptime(exit_time, '%Y-%m-%d H:%M:%S%z')
        time_length = dt_exit - dt_entry

        s = time_length.total_seconds()
        days, remainder = divmod(s, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{days}:{hours}:{minutes} {seconds}"
    except ValueError:
        print("Unable to get trade duration, will return emty string")
        return ""


def pnl(position, entry_price, exit_price):
    if position == "long":
        return ((exit_price-entry_price)/entry_price)*100
    short_pnl = ((entry_price-exit_price)/entry_price)*100

    return round(short_pnl, 3)
