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
    def exposed_insert_temperature(temperature, user_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        spotlight_collection = collection.Collection(client.spotlight, "Temperatures")
        document = {"timestamp": datetime.datetime.utcnow(), "user_id": user_id, "temperature": float(temperature)}
        Config.logger.info("insert temperature %s" % str(temperature))
        spotlight_collection.insert(document)
        client.close()

    @staticmethod
    def exposed_insert_motion(motion, user_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        spotlight_collection = collection.Collection(client.spotlight, "Motions")
        document = {"timestamp": datetime.datetime.utcnow(), "user_id": user_id, "motion": float(motion)}
        Config.logger.info("insert motion %s" % str(motion))
        spotlight_collection.insert(document)
        client.close()

    @staticmethod
    def exposed_insert_occupancy(occupancy, user_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        spotlight_collection = collection.Collection(client.spotlight, "Occupancy")
        document = {"timestamp": datetime.datetime.utcnow(), "user_id": user_id, "motion": int(occupancy)}
        Config.logger.info("insert occupancy %s" % str(occupancy))
        spotlight_collection.insert(document)
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
