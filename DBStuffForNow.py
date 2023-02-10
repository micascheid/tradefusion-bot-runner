import sys

from firebase_admin import credentials, db, firestore

import BotsEnum
from Globals import DB_URL
import firebase_admin
import json
import os


def db_initializer():
    cred = credentials.Certificate('firebase_firestore_credentials_mltradefusion.json')
    firebase_admin.initialize_app(cred)


def db_init_data_check() -> None:
    #Final db structure is not conclusive and will be worked on further after discussion with usage of mvp by quants.
    # For now, I will hard code it in as seen below
    for key in BotsEnum.bots_enum_dict.keys():
        doc_query = firestore.client().collection('entry').document(key).get()
        if doc_query.to_dict() is None:
            firestore.client().collection('entry').document(key).set('')

    if len(firestore.client().collection(u'quant_names').get()) > 0:
        return
    quant1 = {
        "bots": {
            "krowncross": {
                "strat_type": "trend",
                "trading_pairs": ["BTCUSDT, ETHUSD, LTCUSD"],
                "timeframes": ["1h", "2h", "4h"]
            },
            "csp": {
                "strat_type": "mean_reversion",
                "trading_pairs": ["BTCUSDT, ETHUSD"],
                "timeframes": ["5m", "30m", "1h"]
            }
        },
        "about": {
            "twitter": "link1",
            "blog": "big_bad_blog.com"
        }
    }
    quant2 = {
        "bots": {
            "krowncross_v2": {
                "strat_type": "trend",
                "trading_pairs": ["BTCUSDT, ETHUSD, LTCUSD"],
                "timeframes": ["1h", "2h", "4h"]
            },
            "csp_v2": {
                "strat_type": "mean_reversion",
                "trading_pairs": ["BTCUSDT, ETHUSD"],
                "timeframes": ["5m", "30m", "1h"]
            }
        }
    }

    actbot5m = {"csp": ["LTCUSD", "ADAUSD", "BTCUSDT"],
                "krowncross": ["BTCUSDT"]}
    actbot30m = {"csp": ["BTCUSDT", "LTCUSD"],
                 "krowncross": ["ETHUSD", "LTCUSD"]}
    actbot1h = {"csp": ["LTCUSD", "ADAUSD"],
                "krowncross": ["BTCUSDT", "ADAUSD"]}

    timeframe5m = {u"pairs": ["BTCUSDT", "ADAUSD", "LTCUSD"]}
    timeframe30m = {u"pairs": ["BTCUSDT", "LTCUSD", "ETHUSD"]}
    timeframe1h = {u"pairs": ["ADAUSD", "BTCUSDT", "LTCUSD"]}

    db = firestore.client()
    db.collection(u'quant_names').document(u'mica').set(quant1)
    db.collection(u'quant_names').document(u'quant_bro').set(quant2)
    db.collection(u'active_bots').document(u'5m').set(actbot5m)
    db.collection(u'active_bots').document(u'30m').set(actbot30m)
    db.collection(u'active_bots').document(u'1h').set(actbot1h)
    db.collection(u'timeframe_pairs').document(u'5m').set(timeframe5m)
    db.collection(u'timeframe_pairs').document(u'30m').set(timeframe30m)
    db.collection(u'timeframe_pairs').document(u'1h').set(timeframe1h)
