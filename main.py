from datetime import datetime
import numpy
import numpy as np
import pytz
import requests
from pandas import DataFrame

from KlineDataMonitor import KlineDataMonitor
import time
from DBPaths import DBPaths
import firebase_admin
from firebase_admin import credentials, db
from apscheduler.schedulers.background import BackgroundScheduler
from BotFactory import BotFactory
from BotObj import BotObj
import DBStuffForNow

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


REF = DBStuffForNow.db_initializer()

def db_get_active_bots() -> dict:
    return REF.child(DBPaths.ACTIVEBOTS.value).get()

def db_get_active_tfs() -> dict:
    return REF.child(DBPaths.ACTIVETFS.value).get()

def db_get_timeframes_pairs() -> dict:
    return REF.child(DBPaths.TIMEFRAMES_PAIRS.value).get()

def create_bot_list(live_bots) -> list:
    bot_obj_list = []
    for tf in live_bots:
        for bot_name, pairs in live_bots[tf].items():
            for pair in pairs:
                bot_obj_list.append(BotObj(name=bot_name, tf=tf, pair=pair))
    return bot_obj_list


def kline_data_monitor_manager() -> {KlineDataMonitor}:
    active_tfs_pairs = db_get_timeframes_pairs()
    new_dict = {}
    for k in active_tfs_pairs.keys():
        for pair in active_tfs_pairs[k]:
            new_dict[k+pair] = KlineDataMonitor(name=k+pair, tf=k, pair=pair)
    return new_dict


def calc_job_times(timeframe) -> {}:
    timeframe_sec = TIME_FRAME_TO_SEC[timeframe]
    tf_unit = timeframe[-1]
    t_amount = int(timeframe[:-1])
    interval_val = INTERVAL_UNITS[tf_unit]
    t_now = time.time()
    tz = pytz.timezone('UTC')
    next_run_time = datetime.fromtimestamp((t_now - (t_now%TIME_FRAME_TO_SEC[timeframe])) + TIME_FRAME_TO_SEC[
        timeframe], tz=tz)
    return {interval_val: t_amount, 'next_run_time': next_run_time}



def Main():
    start_bot_runner = input("Would you like to start bot_runner?[y/n]")
    data_monitors = []
    list_bots = []
    if start_bot_runner == "y":
        while start_bot_runner != "n":
            # Check the bots and the timeframe and pairs I need to make them on
            list_bots = create_bot_list(db_get_active_bots())
            print("Finished pulling bots from db")

            # Delegate the bot making task to the factory
            bot_factory = BotFactory(list_bots)

            # Instantiate all bots
            my_new_bots = bot_factory.create()

            # Create the data monitors per time frame
            data_monitors = kline_data_monitor_manager()

            # Attach all bots to their perspective data monitor
            for key in data_monitors.keys():
                temp_list = [bot for bot in my_new_bots if bot.get_tf()+bot.get_pair() == key]
                for b in temp_list:
                    data_monitors[key].attach(b)

            # Add job with each data monitor and pass in data monitor
            scheduler = BackgroundScheduler()
            for key, monitor in data_monitors.items():
                tf = monitor.get_tf()
                pair = monitor.get_pair()
                job_details_dict = calc_job_times(tf)
                scheduler.add_job(data_pull, 'interval', args=[tf, pair, monitor], **job_details_dict)
            scheduler.start()

            start_bot_runner = input("Would you like to keep going?")
            if start_bot_runner == "n":
                print("exiting...")
                break
            if start_bot_runner == "ltc":
                data_monitors['1hLTCUSD'].data = 10
            time.sleep(5)


def kline_url_builder(tf, pair):
    return f'https://api.binance.us/api/v3/klines?symbol={pair}&interval={tf}'

def data_pull(tf, pair, data_monitor):
    print("being called to print data")
    url = kline_url_builder(tf, pair)
    resp = requests.get(url).json()
    data = binance_to_dataframe(resp)
    data_monitor.data = data

def binance_to_dataframe(dub_arr) -> DataFrame:
    np_arr = np.array(dub_arr)
    np_arr = numpy.delete(np_arr, range(5, 12), axis=1)
    columns = ['timestamp', 'Open', 'High', 'Low', 'Close']
    df = DataFrame(data=np_arr, columns=columns)
    df['timestamp'] = df['timestamp'].apply(lambda epoch: datetime.fromtimestamp(int(epoch)/1000).astimezone(
        tz=pytz.timezone('UTC')))
    df = df.set_index('timestamp')
    return df


if __name__ == '__main__':
    Main()

    # test_dict = REF.child('active_bots')
    # print(test_dict)


