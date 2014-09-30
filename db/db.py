import datetime
import rpyc

from rpyc.utils.server import ThreadedServer
from pymongo import MongoClient
from pymongo import collection

from config import Config


def insert(document, collection_name):
    client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
    client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
    spotlight_collection = collection.Collection(client.spotlight, collection_name)
    common_fields = {"timestamp": datetime.datetime.utcnow()}
    spotlight_collection.insert(dict(common_fields.items() + document.items()))
    client.close()

if __name__ == "__main__":
    pass