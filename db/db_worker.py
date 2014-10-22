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
    def exposed_insert_temperature(temperature, device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        spotlight_collection = collection.Collection(client.spotlight, "Temperatures")
        document = {"timestamp": datetime.datetime.utcnow(), "device_id": device_id, "temperature": float(temperature)}
        Config.logger.info("insert temperature:%s" % str(temperature))
        spotlight_collection.insert(document)
        client.close()

    @staticmethod
    def exposed_insert_motion(motion, device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        spotlight_collection = collection.Collection(client.spotlight, "Motions")
        document = {"timestamp": datetime.datetime.utcnow(), "device_id": device_id, "std": float(motion)}
        Config.logger.info("insert motion_std:%s" % str(motion))
        spotlight_collection.insert(document)
        client.close()

    @staticmethod
    def exposed_insert_occupancy(occupancy, device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        spotlight_collection = collection.Collection(client.spotlight, "Occupancies")
        document = {"timestamp": datetime.datetime.utcnow(), "device_id": device_id, "occupancy": int(occupancy)}
        Config.logger.info("insert occupancy:%s" % str(occupancy))
        spotlight_collection.insert(document)
        client.close()

    @staticmethod
    def exposed_insert_state(heat_state, cool_state, fan_speed, device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        spotlight_collection = collection.Collection(client.spotlight, "States")
        document = {"timestamp": datetime.datetime.utcnow(), "device_id": device_id, "heat": heat_state,
                    "cool": cool_state, "speed": fan_speed}
        Config.logger.info("insert state heat:%s cool:%s speed:%s" %
                           (str(heat_state), str(cool_state), str(fan_speed)))
        spotlight_collection.insert(document)
        client.close()

    @staticmethod
    def exposed_insert_ppv(pmv, ppv, device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        ppv_collection = collection.Collection(client.spotlight, "PPVs")
        document = {"timestamp": datetime.datetime.utcnow(), "device_id": device_id, "pmv": pmv, "ppv": ppv}
        Config.logger.info("insert pmv:%s ppv:%s" % (str(pmv), str(ppv)))
        ppv_collection.insert(document)
        client.close()

    @staticmethod
    def exposed_get_ppv_parameters(device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        device_collection = collection.Collection(client.spotlight, "Devices")
        device = device_collection.find_one({"device_id": device_id})
        Config.logger.info("fetched %s" % str(device))
        client.close()
        return device

    @staticmethod
    def exposed_get_user(user_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        user_collection = collection.Collection(client.spotlight, "Users")
        user = user_collection.find_one({"email": user_id})
        Config.logger.info("fetched %s" % str(user))
        client.close()
        return user

if __name__ == "__main__":
    Config.initialize()
    Config.logger.info("SPOTlight db manager started...")
    Updater.start()
    server = ThreadedServer(DBService, hostname=Config.service_config["db_service_address"],
                            port=Config.service_config["db_service_port"], logger=Config.service_logger,
                            authenticator=None, protocol_config={"allow_pickle": True})
    server.start()
    #device manager will block on this line to listen for incoming RPC requests
    Config.logger.info("SPOTlight device manager shutting down...")
