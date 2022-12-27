import datetime
import time

import firebase_admin
from firebase_admin import credentials, db
import json
from quants.mica.KrownCross import KrownCross
from quants.mica.CSP import CSP
from BotObj import BotObj
from BotFactory import BotFactory
from BotInterface import BotInterface
import requests
import time
from KlineDataMonitor import KlineDataMonitor

db_url = 'https://crudlearning-791df-default-rtdb.firebaseio.com/'



def db_initializer():
    file = open('bot_db_initialize.json', 'r')
    db_init_obj = json.load(file)
    cred = credentials.Certificate('firebase_credentials.json')
    firebase_admin.initialize_app(cred, {'databaseURL': db_url})
    ref = db.reference('/')
    if ref.get() is None:
        ref.set(db_init_obj)
    return ref


def db_get_active_bots(ref) -> dict:
    bots_to_create = ref.child('active_bots').get()
    return bots_to_create

def create_bot_list(live_bots) -> list:
    bot_obj_list = []
    for tf in live_bots:
        for bot_name, pairs in live_bots[tf].items():
            for pair in pairs:
                # print(f'name: {bot_name}, tf: {tf}, pair: {pair}')
                bot_obj_list.append(BotObj(name=bot_name, tf=tf, pair=pair))
    return bot_obj_list



if __name__ == '__main__':

    db_ref = db_initializer()


    #Get data pull of timeframes, bots and trading pair

    start_bot_runner = input("Would you like to start bot_runner?[y/n]")

    if start_bot_runner == "y":
        while start_bot_runner == "y":
            list_bots = create_bot_list(db_get_active_bots(db_ref))
            bot_factory = BotFactory(list_bots)
            my_new_bots = bot_factory.create()
            for bot in my_new_bots:
                bot.entry()
            start_bot_runner = input("Would you like to keep going?")
            if start_bot_runner != "y":
                print("exiting...")
                break

            time.sleep(5)


