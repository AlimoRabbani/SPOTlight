import datetime
import rpyc
import json

from rpyc.utils.server import ThreadedServer
from pymongo import MongoClient
from pymongo import collection

from config import Config
from db_updater import Updater


class DBService(rpyc.Service):
    @staticmethod
    def exposed_insert(document, collection_name):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        spotlight_collection = collection.Collection(client.spotlight, collection_name)
        common_fields = {"timestamp": datetime.datetime.utcnow()}
        document = json.loads(document)
        Config.logger.info("insert: %s into %s" % (document, collection_name))
        spotlight_collection.insert(dict(common_fields.items() + document.items()))
        client.close()

if __name__ == "__main__":
    Config.initialize()
    Config.logger.info("SPOTlight db manager started...")
    Updater.start()
    server = ThreadedServer(DBService, hostname=Config.service_config["db_service_address"],
                            port=Config.service_config["db_service_port"], logger=Config.service_logger,
                            authenticator=None)
    server.start()
    #device manager will block on this line to listen for incoming RPC requests
    Config.logger.info("SPOTlight device manager shutting down...")
