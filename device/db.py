import datetime

from pymongo import MongoClient
from pymongo import collection
from config import Config


def insert(document, collection_name):
    client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
    client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
    spotlight_collection = collection.Collection(client.spotlight, collection_name)
    common_fields = {"timestamp": datetime.datetime.utcnow(), "mac_address": Config.service_config["mac_address"]}
    spotlight_collection.insert(dict(common_fields.items() + document.items()))
    client.close()