from firebase_admin import credentials, db, firestore
from Globals import DB_URL
import firebase_admin
import json
import os

os.environ['FIRESTORE_EMULATOR_HOST'] = 'localhost:8080'

def db_initializer():
    # file = open('bot_db_initialize.json', 'r')
    # db_init_obj = json.load(file)
    cred = credentials.Certificate('firebase_firestore_credentials_micascheid.json')
    firebase_admin.initialize_app(cred)

    # try:
    #     firebase_admin.get_app()
    # except ValueError as e:

    # return ref
