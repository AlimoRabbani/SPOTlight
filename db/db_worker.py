import datetime
import rpyc
import math
from scipy import stats

from rpyc.utils.server import ThreadedServer
from pymongo import MongoClient
from pymongo import collection

from config import Config


class DBService(rpyc.Service):
    @staticmethod
    def exposed_update_device_app_version(device_id, version):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        spotlight_collection = collection.Collection(client.spotlight, "Devices")
        Config.logger.info("update device app version for %s: %s" % (device_id, version))
        spotlight_collection.update({"device_id": device_id}, {"$set": {"device_app_version": version}})
        client.close()

    @staticmethod
    def exposed_update_control_app_version(device_id, version):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        spotlight_collection = collection.Collection(client.spotlight, "Devices")
        Config.logger.info("update control app version for %s: %s" % (device_id, version))
        spotlight_collection.update({"device_id": device_id}, {"$set": {"control_app_version": version}})
        client.close()

    # region CONTROL_APP
    @staticmethod
    def exposed_update_control_app_version(device_id, version):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        spotlight_collection = collection.Collection(client.spotlight, "Devices")
        Config.logger.info("update control app version for %s: %s" % (device_id, version))
        spotlight_collection.update({"device_id": device_id}, {"$set": {"control_app_version": version}})
        client.close()

    def exposed_insert_temperature(self, temperature, device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        spotlight_collection = collection.Collection(client.spotlight, "Temperatures")
        now_time = datetime.datetime.utcnow()
        document = {"timestamp": now_time, "device_id": device_id, "temperature": float(temperature)}
        Config.logger.info("insert temperature:%s" % str(temperature))
        spotlight_collection.insert(document)

        device_collection = collection.Collection(client.spotlight, "Devices")
        device_collection.update({"device_id": device_id},
                                 {"$set": {"device_ip": self._conn._config['endpoints'][1][0],
                                           "latest_update": now_time,
                                           "latest_temperature": float(temperature)}})
        client.close()

    @staticmethod
    def exposed_insert_motion(motion, device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        spotlight_collection = collection.Collection(client.spotlight, "Motions")
        document = {"timestamp": datetime.datetime.utcnow(), "device_id": device_id, "std": float(motion)}
        Config.logger.info("insert motion_std:%s" % str(motion))
        spotlight_collection.insert(document)
        client.close()

    @staticmethod
    def exposed_insert_occupancy(occupancy, device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        spotlight_collection = collection.Collection(client.spotlight, "Occupancies")
        document = {"timestamp": datetime.datetime.utcnow(), "device_id": device_id, "occupancy": int(occupancy)}
        Config.logger.info("insert occupancy:%s" % str(occupancy))
        spotlight_collection.insert(document)
        client.close()

    @staticmethod
    def exposed_insert_state(heat_state, cool_state, fan_speed, device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
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
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        ppv_collection = collection.Collection(client.spotlight, "PPVs")
        document = {"timestamp": datetime.datetime.utcnow(), "device_id": device_id, "pmv": pmv, "ppv": ppv}
        Config.logger.info("insert pmv:%s ppv:%s" % (str(pmv), str(ppv)))
        ppv_collection.insert(document)
        client.close()

    @staticmethod
    def exposed_get_ppv_parameters(device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        device_collection = collection.Collection(client.spotlight, "Devices")
        device = device_collection.find_one({"device_id": device_id})
        Config.logger.info("fetched %s" % str(device))
        client.close()
        return device
    # endregion

    # region WEB_APP
    @staticmethod
    def exposed_get_user_by_email(email):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        user_collection = collection.Collection(client.spotlight, "Users")
        user = user_collection.find_one({"email": email})
        Config.logger.info("fetched user info for '%s'" % str(email))
        client.close()
        return user

    @staticmethod
    def exposed_get_user_by_user_id(user_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        user_collection = collection.Collection(client.spotlight, "Users")
        user = user_collection.find_one({"user_id": user_id})
        Config.logger.info("fetched user info for '%s'" % str(user_id))
        client.close()
        return user

    @staticmethod
    def exposed_update_forgot_password_secret(email, secret):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        user_collection = collection.Collection(client.spotlight, "Users")
        result = user_collection.update({"email": email}, {"$set": {"forgot_secret": secret}})
        Config.logger.info("created forgot password secret for '%s'" % str(email))
        client.close()
        if result:
            return True
        else:
            return False

    @staticmethod
    def exposed_change_password(user_id, password, salt):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        user_collection = collection.Collection(client.spotlight, "Users")
        user_collection.update({"user_id": user_id}, {"$set": {"password": password, "password_salt": salt}})
        user_collection.update({"user_id": user_id}, {"$unset": {"forgot_secret": ""}})
        Config.logger.info("Password successfully updated for '%s'" % str(user_id))
        client.close()

    @staticmethod
    def exposed_get_device(device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        device_collection = collection.Collection(client.spotlight, "Devices")
        device = device_collection.find_one({"device_id": device_id})
        Config.logger.info("fetched %s" % str(device))
        client.close()
        return device

    @staticmethod
    def exposed_get_devices(user_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        device_collection = collection.Collection(client.spotlight, "Devices")
        devices = list(device_collection.find({"user_id": user_id}))
        Config.logger.info("fetched %d devices for user '%s'" % (len(devices), str(user_id)))
        client.close()
        return list(devices)

    @staticmethod
    def exposed_get_all_devices():
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        device_collection = collection.Collection(client.spotlight, "Devices")
        devices = list(device_collection.find())
        Config.logger.info("fetched %d all devices" % len(devices))
        client.close()
        return list(devices)

    @staticmethod
    def exposed_get_training(device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        training_collection = collection.Collection(client.spotlight, "Training")
        training = training_collection.find_one({"device_id": device_id})
        Config.logger.info("fetched training %s for device '%s'" % (str(training), str(device_id)))
        client.close()
        return training

    @staticmethod
    def exposed_start_training(device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        training_collection = collection.Collection(client.spotlight, "Training")
        result = training_collection.insert({"device_id": device_id, "start_time": datetime.datetime.utcnow()})
        Config.logger.info("inserted training for device '%s'" % str(device_id))
        client.close()
        if result:
            return True
        else:
            return False

    @staticmethod
    def exposed_end_training(device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')

        training_collection = collection.Collection(client.spotlight, "Training")
        training_collection.remove({"device_id": device_id})

        votes_collection = collection.Collection(client.spotlight, "Votes")
        votes = list(votes_collection.find({"device_id": device_id}))

        if len(votes) > 5:
            pmv_list = list()
            vote_list = list()
            for vote in votes:
                pmv_list.append(vote["pmv"])
                vote_list.append(vote["vote"])
            line_regress = stats.linregress(pmv_list, vote_list)
            slope = min(max(line_regress[0], 0.5), 3.0)
            intercept = line_regress[1]
            if (not math.isnan(slope)) and (not math.isnan(intercept)):
                device_collection = collection.Collection(client.spotlight, "Devices")
                device_collection.update({"device_id": device_id},
                                         {"$set": {"device_parameter_a": slope, "device_parameter_b": intercept}})

        votes_collection = collection.Collection(client.spotlight, "Votes")
        votes_collection.remove({"device_id": device_id})

        Config.logger.info("Ended training for device '%s'" % str(device_id))
        client.close()
        return

    @staticmethod
    def exposed_update_offset(device_id, new_offset):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        offset_collection = collection.Collection(client.spotlight, "Offsets")
        now_time = datetime.datetime.utcnow()
        document = {"timestamp": now_time, "device_id": device_id, "offset": new_offset}
        offset_collection.insert(document)

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
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        ppv_collection = collection.Collection(client.spotlight, "PPVs")
        pmv_ppv_list = list(ppv_collection.find({"device_id": device_id, "timestamp": {"$gte": start_date}}).sort("timestamp", 1))
        Config.logger.info("fetched (pmv,ppv) for device '%s' from %s" %
                           (str(device_id), start_date.strftime("%Y-%m-%d %H:%M:%S")))
        client.close()
        skipper_value = (len(pmv_ppv_list) / 2000) + 1
        return pmv_ppv_list[0::skipper_value]

    @staticmethod
    def exposed_get_last_pmv_ppv(device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        ppv_collection = collection.Collection(client.spotlight, "PPVs")
        pmv_ppv_list = list(ppv_collection.find({"device_id": device_id}).sort("timestamp", -1).limit(1))
        Config.logger.info("fetched last (pmv,ppv) for device '%s'" % str(device_id))
        client.close()
        return pmv_ppv_list

    @staticmethod
    def exposed_get_temperature_list(device_id, start_date):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        temperature_collection = collection.Collection(client.spotlight, "Temperatures")
        temperature_list = list(temperature_collection.find({"device_id": device_id, "timestamp": {"$gte": start_date}}).sort("timestamp", 1))
        Config.logger.info("fetched temperatures for device '%s' from %s" %
                           (str(device_id), start_date.strftime("%Y-%m-%d %H:%M:%S")))
        client.close()
        skipper_value = (len(temperature_list) / 2000) + 1
        return temperature_list[0::skipper_value]

    @staticmethod
    def exposed_get_last_temperature(device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        temperature_collection = collection.Collection(client.spotlight, "Temperatures")
        temperature_list = list(temperature_collection.find({"device_id": device_id}).sort("timestamp", -1).limit(1))
        Config.logger.info("fetched last temperature for device '%s'" % str(device_id))
        client.close()
        return temperature_list

    @staticmethod
    def exposed_get_occupancy_list(device_id, start_date):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        occupancy_collection = collection.Collection(client.spotlight, "Occupancies")
        occupancy_list = list(occupancy_collection.find({"device_id": device_id, "timestamp": {"$gte": start_date}}).sort("timestamp", 1))
        Config.logger.info("fetched occupancies for device:'%s' from %s" %
                           (str(device_id), start_date.strftime("%Y-%m-%d %H:%M:%S")))
        client.close()
        occupancy_augmented_list = list()
        occupancy_augmented_list.append(occupancy_list[0])
        previous_occupancy = occupancy_list[0]["occupancy"]
        prev_in_augmented = True
        for i in range(1, len(occupancy_list)):
            if math.fabs(occupancy_list[i]["occupancy"] - previous_occupancy) > 0.5:
                if not prev_in_augmented:
                    occupancy_augmented_list.append(occupancy_list[i-1])
                occupancy_augmented_list.append(occupancy_list[i])
                prev_in_augmented = True
            else:
                prev_in_augmented = False
            previous_occupancy = occupancy_list[i]["occupancy"]
        occupancy_augmented_list.append(occupancy_list[-1])
        return occupancy_augmented_list

    @staticmethod
    def exposed_get_last_occupancy(device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        occupancy_collection = collection.Collection(client.spotlight, "Occupancies")
        occupancy_list = list(occupancy_collection.find({"device_id": device_id}).sort("timestamp", -1).limit(1))
        Config.logger.info("fetched last occupancy for device '%s'" % str(device_id))
        client.close()
        return occupancy_list

    @staticmethod
    def exposed_get_motion_list(device_id, start_date):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        motion_collection = collection.Collection(client.spotlight, "Motions")
        motion_list = list(motion_collection.find({"device_id": device_id, "timestamp": {"$gte": start_date}}).sort("timestamp", 1))
        Config.logger.info("fetched motions for device '%s' from %s" %
                           (str(device_id), start_date.strftime("%Y-%m-%d %H:%M:%S")))
        client.close()
        motion_augmented_list = list()
        motion_augmented_list.append(motion_list[0])
        previous_motion = motion_list[0]["std"]
        prev_in_augmented = True
        for i in range(1, len(motion_list)):
            if math.fabs(motion_list[i]["std"] - previous_motion) > 10 + (math.log10(len(motion_list)) - 1.5)*30:
                if not prev_in_augmented:
                    motion_augmented_list.append(motion_list[i-1])
                motion_augmented_list.append(motion_list[i])
                prev_in_augmented = True
            else:
                prev_in_augmented = False
            previous_motion = motion_list[i]["std"]
        motion_augmented_list.append(motion_list[-1])
        return motion_augmented_list

    @staticmethod
    def exposed_insert_vote(device_id, vote):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')

        training_collection = collection.Collection(client.spotlight, "Training")
        training = training_collection.find_one({"device_id": device_id})
        if not training:
            return False

        ppv_collection = collection.Collection(client.spotlight, "PPVs")
        pmv_ppv_dict = ppv_collection.find({"device_id": device_id}).sort("timestamp", -1).limit(1)
        pmv = pmv_ppv_dict[0]["pmv"]

        votes_collection = collection.Collection(client.spotlight, "Votes")
        result = votes_collection.insert({"device_id": device_id, "vote": vote, "pmv": pmv})

        votes_archive_collection = collection.Collection(client.spotlight, "Votes_Archive")
        votes_archive_collection.insert({"device_id": device_id, "training_start": training["start_time"],
                                         "vote": vote, "pmv": pmv})

        Config.logger.info("inserted (vote:%f, pmv:%f) for device '%s'" % (vote, pmv, str(device_id)))
        client.close()
        if result:
            return True
        else:
            return False

    @staticmethod
    def exposed_get_last_temperature_update(device_id):
        client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
        client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
        temperature_collection = collection.Collection(client.spotlight, "Temperatures")
        temperature_list = list(temperature_collection.find({"device_id": device_id}).sort("timestamp", -1).limit(1))
        Config.logger.info("fetched latest temperature update for device '%s'" % str(device_id))
        client.close()
        if len(temperature_list) == 1:
            return temperature_list[0]
        else:
            return None
    # endregion


if __name__ == "__main__":
    Config.initialize()
    Config.logger.info("SPOTstar db manager started...")
    server = ThreadedServer(DBService, hostname=Config.service_config["db_service_address"],
                            port=Config.service_config["db_service_port"], logger=Config.service_logger,
                            authenticator=None, protocol_config={"allow_pickle": True})
    server.start()
    #device manager will block on this line to listen for incoming RPC requests
    Config.logger.info("SPOTstar device manager shutting down...")
