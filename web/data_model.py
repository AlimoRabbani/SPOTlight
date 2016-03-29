__author__ = 'Alimohammad'

from flask import current_app
import hashlib
import datetime
from dateutil import tz
import random
import string
import hashlib
import uuid
from pymongo import MongoClient
from pymongo import collection
import math
from scipy import stats

def connect_to_db():
    client = MongoClient(host=current_app.config["custom_config"]["db_address"],
                         port=current_app.config["custom_config"]["db_port"])
    client.the_database.authenticate(current_app.config["custom_config"]["db_user"],
                                     current_app.config["custom_config"]["db_password"],
                                     source=current_app.config["custom_config"]["db_auth_source"])
    return client


def handle_db_error(client, e):
    current_app.logger.warn("There was a problem connecting to db")
    current_app.logger.error(e)
    if client:
        client.close()


class User:
    def __init__(self, user_dict):
        self.user_id = user_dict["user_id"]
        self.name = user_dict["name"]
        self.email = user_dict["email"]
        self.hashed_password = user_dict["password"]
        self.password_salt = user_dict["password_salt"]
        self.phone = user_dict["phone"]
        self.role = user_dict["role"]
        if "forgot_secret" in user_dict:
            self.forgot_secret = user_dict["forgot_secret"]
        self.authenticated = False
        self.active = True
        self.anonymous = False

    @staticmethod
    def get(email=None, user_id=None):
        user_dict = None
        client = None
        try:
            client = connect_to_db()
            user_collection = collection.Collection(client.spotlight, "Users")
            user_dict = None
            if email:
                user_dict = user_collection.find_one({"email": email})
            elif user_id:
                user_dict = user_collection.find_one({"user_id": user_id})

            client.close()
        except Exception, e:
            handle_db_error(client, e)

        if user_dict is not None:
            user = User(user_dict)
            user.authenticated = True
            return user
        return None

    def get_device(self, device_id):
        device_dict = None
        client = None
        try:
            client = connect_to_db()
            device_collection = collection.Collection(client.spotlight, "Devices")
            device_dict = device_collection.find_one({"device_id": device_id})
            client.close()
        except Exception, e:
            handle_db_error(client, e)
        device = None
        if device_dict:
            device = Device(device_dict)
            if device.device_owner == self.user_id or self.role == "admin":
                return device
        return device

    def find_devices(self):
        return Device.find_devices(self.user_id)

    def forgot_password(self):
        result = None
        secret = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
        client = None
        try:
            client = connect_to_db()
            user_collection = collection.Collection(client.spotlight, "Users")
            result = user_collection.update_one({"email": self.email}, {"$set": {"forgot_secret": secret}})
            client.close()
        except Exception, e:
            handle_db_error(client, e)
        if result:
            self.forgot_secret = secret
            return True
        else:
            return False

    @staticmethod
    def validate_reset_secret(user_id, secret):
        user = User.get(user_id=user_id)
        try:
            if user.forgot_secret == secret:
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def change_password(user_id, new_password):
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(new_password + salt).hexdigest()
        client = None

        try:
            client = connect_to_db()
            user_collection = collection.Collection(client.spotlight, "Users")
            user_collection.update_one({"user_id": user_id},
                                       {"$set": {"password": hashed_password, "password_salt": salt}})
            user_collection.update_one({"user_id": user_id}, {"$unset": {"forgot_secret": ""}})
            client.close()
        except Exception, e:
            handle_db_error(client, e)

    def authenticate(self, password):
        hashed_password = hashlib.sha512(password + self.password_salt).hexdigest()
        if hashed_password == self.hashed_password:
            return True
        else:
            return False

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return self.anonymous

    def get_id(self):
        return self.email


class Device:
    def __init__(self, device_dict):
        self.device_id = device_dict["device_id"]
        self.device_owner = device_dict["user_id"]
        self.device_parameter_a = device_dict["device_parameter_a"]
        self.device_parameter_b = device_dict["device_parameter_b"]
        self.device_parameter_offset = device_dict["device_parameter_offset"]
        self.device_location = device_dict["device_location"]
        self.device_ip = device_dict["device_ip"]
        self.device_mac = device_dict["device_mac"]
        self.box_number = device_dict["box_number"]


        # self.control_app_version = device_dict["box_number"]

        self.is_alive = True
        self.is_overheating = False

        self.device_app_version = None
        self.latest_temperature = None
        self.latest_update_time = None

        try:
            self.device_app_version = device_dict["device_app_version"]
        except KeyError:
            current_app.logger.warn("No device app version for '%s'" % self.device_id)

        try:
            self.latest_temperature = device_dict["latest_temperature"]
        except KeyError:
            current_app.logger.warn("No latest temperature for '%s'" % self.device_id)

        try:
            from_zone = tz.tzutc()
            to_zone = tz.tzlocal()
            utc = device_dict["latest_update"].replace(tzinfo=from_zone)
            self.latest_update_time = utc.astimezone(to_zone)
        except KeyError:
            current_app.logger.warn("No latest update for '%s'" % self.device_id)

        self.update_warnings()

    @staticmethod
    def find_devices(user_id):
        devices = None
        client = None
        try:
            client = connect_to_db()
            device_collection = collection.Collection(client.spotlight, "Devices")
            devices = list(device_collection.find({"user_id": user_id}))
            client.close()
        except Exception, e:
            handle_db_error(client, e)
        device_list = list()
        for device_dict in devices:
            device = Device(device_dict)
            device_list.append(device)
        return device_list

    @staticmethod
    def find_all_devices():
        devices = None
        client = None
        try:
            client = connect_to_db()
            device_collection = collection.Collection(client.spotlight, "Devices")
            devices = list(device_collection.find())
            client.close()
        except Exception, e:
            handle_db_error(client, e)

        device_list = list()
        for device_dict in devices:
            device = Device(device_dict)
            device_list.append(device)
        return device_list

    def get_training(self):
        training = None
        client = None
        try:
            client = connect_to_db()
            training_collection = collection.Collection(client.spotlight, "Training")
            training = training_collection.find_one({"device_id": self.device_id})
            client.close()
        except Exception, e:
            handle_db_error(client, e)
        return training

    def start_training(self):
        result = None
        client = None
        try:
            client = connect_to_db()
            training_collection = collection.Collection(client.spotlight, "Training")
            result = training_collection.insert_one({"device_id": self.device_id,
                                                     "start_time": datetime.datetime.utcnow()})
            client.close()
        except Exception, e:
            handle_db_error(client, e)
        if result:
            return True
        else:
            return False

    def end_training(self):
        client = None
        try:
            client = connect_to_db()
            training_collection = collection.Collection(client.spotlight, "Training")
            training_collection.delete_one({"device_id": self.device_id})

            votes_collection = collection.Collection(client.spotlight, "Votes")
            votes = list(votes_collection.find({"device_id": self.device_id}))

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
                    device_collection.update_one({"device_id": self.device_id},
                                                 {"$set": {"device_parameter_a": slope,
                                                           "device_parameter_b": intercept}})

            votes_collection = collection.Collection(client.spotlight, "Votes")
            votes_collection.delete_one({"device_id": self.device_id})
            client.close()
        except Exception, e:
            handle_db_error(client, e)

    def update_offset(self, new_offset):
        result = None
        client = None
        try:
            client = connect_to_db()
            offset_collection = collection.Collection(client.spotlight, "Offsets")
            now_time = datetime.datetime.utcnow()
            document = {"timestamp": now_time, "device_id": self.device_id, "offset": new_offset}
            offset_collection.insert_one(document)

            device_collection = collection.Collection(client.spotlight, "Devices")
            result = device_collection.update_one({"device_id": self.device_id},
                                                  {"$set": {"device_parameter_offset": new_offset}})
            client.close()
        except Exception, e:
            handle_db_error(client, e)
        if result:
            return True
        else:
            return False

    def submit_vote(self, vote):
        client = None
        try:
            client = connect_to_db()
            training_collection = collection.Collection(client.spotlight, "Training")
            training = training_collection.find_one({"device_id": self.device_id})
            if not training:
                return False

            ppv_collection = collection.Collection(client.spotlight, "PPVs")
            pmv_ppv_dict = ppv_collection.find({"device_id": self.device_id}).sort("timestamp", -1).limit(1)
            pmv = pmv_ppv_dict[0]["pmv"]

            votes_collection = collection.Collection(client.spotlight, "Votes")
            result = votes_collection.insert_one({"device_id": self.device_id, "vote": vote, "pmv": pmv})

            votes_archive_collection = collection.Collection(client.spotlight, "Votes_Archive")
            votes_archive_collection.insert_one({"device_id": self.device_id,
                                                 "training_start": training["start_time"],
                                                 "vote": vote,
                                                 "pmv": pmv})
            client.close()
            if result:
                return True
            else:
                return False
        except Exception, e:
            handle_db_error(client, e)
        return False

    def get_pmv_ppv_list(self, start_date):
        pmv_ppv_list = list()
        client = None
        try:
            client = connect_to_db()
            ppv_collection = collection.Collection(client.spotlight, "PPVs")
            temp_list = list(ppv_collection.find({"device_id": self.device_id,
                                                  "timestamp": {"$gte": start_date}}).sort("timestamp", 1))
            client.close()
            skipper_value = (len(pmv_ppv_list) / 2000) + 1
            pmv_ppv_list = temp_list[0::skipper_value]
        except Exception, e:
            handle_db_error(client, e)
        pmv_list = list()
        ppv_list = list()
        for pmv_ppv_item in pmv_ppv_list:
            pmv_list.append([(pmv_ppv_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, pmv_ppv_item["pmv"]])
            ppv_list.append([(pmv_ppv_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, pmv_ppv_item["ppv"]])
        return [pmv_list, ppv_list]

    def get_last_pmv_ppv(self):
        pmv_ppv_list = list()
        client = None
        try:
            client = connect_to_db()
            ppv_collection = collection.Collection(client.spotlight, "PPVs")
            pmv_ppv_list = list(ppv_collection.find({"device_id": self.device_id}).sort("timestamp", -1).limit(1))
            client.close()
        except Exception, e:
            handle_db_error(client, e)
        pmv_list = list()
        ppv_list = list()
        for pmv_ppv_item in pmv_ppv_list:
            pmv_list.append([(pmv_ppv_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, pmv_ppv_item["pmv"]])
            ppv_list.append([(pmv_ppv_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, pmv_ppv_item["ppv"]])
        return [pmv_list, ppv_list]

    def get_occupancy_temperature_list(self, start_date):
        temperature_list = list()
        occupancy_list = list()
        client = None
        try:
            client = connect_to_db()
            temperature_collection = collection.Collection(client.spotlight, "Temperatures")
            occupancy_collection = collection.Collection(client.spotlight, "Occupancies")
            temperature_temp_list =\
                list(temperature_collection.find({"device_id": self.device_id,
                                                  "timestamp": {"$gte": start_date}}).sort("timestamp", 1))
            skipper_value = (len(temperature_list) / 2000) + 1
            temperature_list = temperature_temp_list[0::skipper_value]
            occupancy_temp_list =\
                list(occupancy_collection.find({"device_id": self.device_id,
                                                "timestamp": {"$gte": start_date}}).sort("timestamp", 1))
            client.close()
            occupancy_list = list()
            occupancy_list.append(occupancy_temp_list[0])
            previous_occupancy = occupancy_temp_list[0]["occupancy"]
            prev_in_augmented = True
            for i in range(1, len(occupancy_temp_list)):
                if math.fabs(occupancy_temp_list[i]["occupancy"] - previous_occupancy) > 0.5:
                    if not prev_in_augmented:
                        occupancy_list.append(occupancy_temp_list[i-1])
                    occupancy_list.append(occupancy_temp_list[i])
                    prev_in_augmented = True
                else:
                    prev_in_augmented = False
                previous_occupancy = occupancy_temp_list[i]["occupancy"]
            occupancy_list.append(occupancy_temp_list[-1])
        except Exception, e:
            handle_db_error(client, e)

        temperature_modified_list = list()
        for temperature_item in temperature_list:
            item = [(temperature_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0,
                    temperature_item["temperature"]]
            temperature_modified_list.append(item)

        occupancy_modified_list = list()
        previous_occupancy = 0
        for occupancy_item in occupancy_list:
            current_occupancy = int(occupancy_item["occupancy"])
            if current_occupancy == 1 and previous_occupancy == 2:
                current_occupancy = 1
            elif current_occupancy == 1 and previous_occupancy == 0:
                current_occupancy = 0
            elif current_occupancy == 2:
                current_occupancy = 1
            previous_occupancy = current_occupancy
            item = [(occupancy_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0,
                    current_occupancy]
            occupancy_modified_list.append(item)
        return [occupancy_modified_list, temperature_modified_list]

    def get_last_occupancy_temperature(self):
        temperature_list = list()
        occupancy_list = list()
        client = None
        try:
            client = connect_to_db()
            temperature_collection = collection.Collection(client.spotlight, "Temperatures")
            occupancy_collection = collection.Collection(client.spotlight, "Occupancies")
            temperature_list =\
                list(temperature_collection.find({"device_id": self.device_id}).sort("timestamp", -1).limit(1))
            occupancy_list =\
                list(occupancy_collection.find({"device_id": self.device_id}).sort("timestamp", -1).limit(1))
            client.close()
            return temperature_list
        except Exception, e:
            handle_db_error(client, e)
        temperature_modified_list = list()
        for temperature_item in temperature_list:
            item = [(temperature_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0,
                    temperature_item["temperature"]]
            temperature_modified_list.append(item)
        occupancy_modified_list = list()
        for occupancy_item in occupancy_list:
            item = [(occupancy_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0,
                    occupancy_item["occupancy"]/2.0]
            occupancy_modified_list.append(item)
        return [occupancy_modified_list, temperature_modified_list]

    def update_warnings(self):
        self.is_alive = False
        if not self.latest_update_time:
            return
        if (datetime.datetime.utcnow().replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal()) - self.latest_update_time).total_seconds() < current_app.config["custom_config"]["keepalive_interval"]:
            self.is_alive = True
        if self.latest_temperature < current_app.config["custom_config"]["overheating_threshold"]:
            self.is_overheating = False
        else:
            self.is_overheating = True
