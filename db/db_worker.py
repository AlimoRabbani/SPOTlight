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

    #Exposed methods for the web application
    @staticmethod
    def exposed_get_user(user_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        user_collection = collection.Collection(client.spotlight, "Users")
        user = user_collection.find_one({"email": user_id})
        Config.logger.info("fetched user info for '%s'" % str(user_id))
        client.close()
        return user

    @staticmethod
    def exposed_get_device(device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        device_collection = collection.Collection(client.spotlight, "Devices")
        device = device_collection.find_one({"device_id": device_id})
        Config.logger.info("fetched %s" % str(device))
        client.close()
        return device

    @staticmethod
    def exposed_get_devices(user_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        device_collection = collection.Collection(client.spotlight, "Devices")
        devices = list(device_collection.find({"user_id": user_id}))
        Config.logger.info("fetched %d devices for user '%s'" % (len(devices), str(user_id)))
        client.close()
        return list(devices)

    @staticmethod
    def exposed_get_training(device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        training_collection = collection.Collection(client.spotlight, "Training")
        training = training_collection.find_one({"device_id": device_id})
        Config.logger.info("fetched training %s for device '%s'" % (str(training), str(device_id)))
        client.close()
        return training

    @staticmethod
    def exposed_start_training(device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        training_collection = collection.Collection(client.spotlight, "Training")
        result = training_collection.insert({"device_id": device_id, "start_time": datetime.datetime.utcnow()})
        Config.logger.info("inserted training for device '%s'" % str(device_id))
        client.close()
        if result:
            return True
        else:
            return False

    @staticmethod
    def exposed_update_offset(device_id, new_offset):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        device_collection = collection.Collection(client.spotlight, "Devices")
        result = device_collection.update({"device_id": device_id}, {"$set": {"device_parameter_offset": new_offset}})
        Config.logger.info("updated offset for device '%s'" % str(device_id))
        client.close()
        if result:
            return True
        else:
            return False

    @staticmethod
    def exposed_get_pmv_ppv_list(device_id, start_date):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        ppv_collection = collection.Collection(client.spotlight, "PPVs")
        pmv_ppv_list = list(ppv_collection.find({"device_id": device_id, "timestamp": {"$gte": start_date}}))
        Config.logger.info("fetched (pmv,ppv) for device '%s' from %s" %
                           (str(device_id), start_date.strftime("%Y-%m-%d %H:%M:%S")))
        client.close()
        return pmv_ppv_list

    @staticmethod
    def exposed_get_temperature_list(device_id, start_date):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        temperature_collection = collection.Collection(client.spotlight, "Temperatures")
        temperature_list = list(temperature_collection.find({"device_id": device_id, "timestamp": {"$gte": start_date}}).sort("timestamp", 1))
        Config.logger.info("fetched temperatures for device '%s' from %s" %
                           (str(device_id), start_date.strftime("%Y-%m-%d %H:%M:%S")))
        client.close()
        return temperature_list

    @staticmethod
    def exposed_get_occupancy_list(device_id, start_date):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        occupancy_collection = collection.Collection(client.spotlight, "Occupancies")
        occupancy_list = list(occupancy_collection.find({"device_id": device_id, "timestamp": {"$gte": start_date}}).sort("timestamp", 1))
        Config.logger.info("fetched occupancies for device:'%s' from %s" %
                           (str(device_id), start_date.strftime("%Y-%m-%d %H:%M:%S")))
        client.close()
        return occupancy_list

    @staticmethod
    def exposed_get_motion_list(device_id, start_date):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        motion_collection = collection.Collection(client.spotlight, "Motions")
        motion_list = list(motion_collection.find({"device_id": device_id, "timestamp": {"$gte": start_date}}).sort("timestamp", 1))
        Config.logger.info("fetched motions for device '%s' from %s" %
                           (str(device_id), start_date.strftime("%Y-%m-%d %H:%M:%S")))
        client.close()
        return motion_list

    @staticmethod
    def exposed_insert_vote(device_id, vote):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='admin')
        ppv_collection = collection.Collection(client.spotlight, "PPVs")
        pmv_ppv_dict = ppv_collection.find({"device_id": device_id}).sort("timestamp", -1).limit(1)
        pmv = pmv_ppv_dict[0]["pmv"]

        votes_collection = collection.Collection(client.spotlight, "Votes")
        result = votes_collection.insert({"device_id": device_id, "vote": vote, "pmv": pmv})
        Config.logger.info("inserted (vote:%f, pmv:%f) for device '%s'" % (vote, pmv, str(device_id)))
        client.close()
        if result:
            return True
        else:
            return False

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
