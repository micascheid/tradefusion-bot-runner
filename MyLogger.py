from datetime import datetime
import pytz
import time
from Globals import TIME_FRAME_TO_SEC
import logging


# def get_time(timeframe=None) -> datetime:
#     tz = pytz.timezone('UTC')
#     if timeframe is not None:
#         timeframe_sec = TIME_FRAME_TO_SEC[timeframe]
#         t_now = time.time()
#         next_run_time = datetime.fromtimestamp((t_now - (t_now % timeframe_sec)), tz=tz)
#         return next_run_time.replace(microsecond=0)
#     return datetime.fromtimestamp(time.time(), tz=tz).replace(microsecond=0)


def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logging.setLevel(logging.INFO)
    logger.addHandler(handler)








