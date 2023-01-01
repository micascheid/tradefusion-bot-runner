from firebase_admin import credentials, db
from Globals import DB_URL
import firebase_admin
import json


def db_initializer():
    file = open('bot_db_initialize.json', 'r')
    db_init_obj = json.load(file)
    cred = credentials.Certificate('firebase_credentials.json')

    # try:
    #     firebase_admin.get_app()
    # except ValueError as e:
    firebase_admin.initialize_app(cred, options={'databaseURL': DB_URL})

    ref = db.reference('/')
    if ref.get() is None:
        ref.set(db_init_obj)
    return ref
