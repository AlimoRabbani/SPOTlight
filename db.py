from pymongo import MongoClient
from pymongo import collection
from spotlight_config import Config


def insert(document, collection_name):
    client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
    client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
    spotlight_collection = collection.Collection(client.spotlight, collection_name)
    spotlight_collection.insert(document)
    client.close()