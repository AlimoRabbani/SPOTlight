__author__ = 'Alimohammad'

from flask import current_app
import hashlib
import datetime
import rpyc
import pickle
from dateutil import tz

class User:
    def __init__(self, user_dict):
        self.user_id = user_dict["user_id"]
        self.name = user_dict["name"]
        self.email = user_dict["email"]
        self.hashed_password = user_dict["password"]
        self.password_salt = user_dict["password_salt"]
        self.phone = user_dict["phone"]
        self.role = user_dict["role"]
        self.authenticated = False
        self.active = True
        self.anonymous = False

    @staticmethod
    def get(email=None, user_id=None):
        user_dict = None
        try:
            db_conn = rpyc.connect(current_app.config["custom_config"]["db_service_address"],
                                   current_app.config["custom_config"]["db_service_port"],
                                   config={"allow_pickle": True})
            try:
                if email:
                    user_dict = pickle.loads(pickle.dumps(db_conn.root.get_user_by_email(email)))
                elif user_id:
                    user_dict = pickle.loads(pickle.dumps(db_conn.root.get_user_by_user_id(user_id)))
                db_conn.close()
            except Exception, e:
                current_app.logger.warn("There was a problem reading from db")
                current_app.logger.error(e)
                db_conn.close()
        except Exception, e:
            current_app.logger.warning("There was a problem connecting to db")
            current_app.logger.error(e)

        if user_dict is not None:
            user = User(user_dict)
            user.authenticated = True
            return user
        return None

    def get_device(self, device_id):
        device_dict = None
        try:
            db_conn = rpyc.connect(current_app.config["custom_config"]["db_service_address"],
                                   current_app.config["custom_config"]["db_service_port"],
                                   config={"allow_pickle": True})
            try:
                device_dict = pickle.loads(pickle.dumps(db_conn.root.get_device(device_id)))
                db_conn.close()
            except Exception, e:
                current_app.logger.warn("There was a problem reading from db")
                current_app.logger.error(e)
                db_conn.close()
        except Exception, e:
            current_app.logger.warning("There was a problem connecting to db")
            current_app.logger.error(e)
        device = None
        if device_dict:
            device = Device(device_dict)
            if device.device_owner == self.user_id or self.role == "admin":
                return device
        return device

    def find_devices(self):
        return Device.find_devices(self.user_id)

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
        try:
            db_conn = rpyc.connect(current_app.config["custom_config"]["db_service_address"],
                                   current_app.config["custom_config"]["db_service_port"],
                                   config={"allow_pickle": True})
            try:
                devices = pickle.loads(pickle.dumps(db_conn.root.get_devices(user_id)))
                db_conn.close()
            except Exception, e:
                current_app.logger.warn("There was a problem reading from db")
                current_app.logger.error(e)
                db_conn.close()
        except Exception, e:
            current_app.logger.warning("There was a problem connecting to db")
            current_app.logger.error(e)
        device_list = list()
        for device_dict in devices:
            device = Device(device_dict)
            device_list.append(device)
        return device_list

    def get_owner(self):
        user = User.get(user_id=self.device_owner)
        return user

    @staticmethod
    def find_all_devices():
        devices = None
        try:
            db_conn = rpyc.connect(current_app.config["custom_config"]["db_service_address"],
                                   current_app.config["custom_config"]["db_service_port"],
                                   config={"allow_pickle": True})
            try:
                devices = pickle.loads(pickle.dumps(db_conn.root.get_all_devices()))
                db_conn.close()
            except Exception, e:
                current_app.logger.warn("There was a problem reading from db")
                current_app.logger.error(e)
                db_conn.close()
        except Exception, e:
            current_app.logger.warning("There was a problem connecting to db")
            current_app.logger.error(e)
        device_list = list()
        for device_dict in devices:
            device = Device(device_dict)
            device_list.append(device)
        return device_list

    def get_training(self):
        training = None
        try:
            db_conn = rpyc.connect(current_app.config["custom_config"]["db_service_address"],
                                   current_app.config["custom_config"]["db_service_port"],
                                   config={"allow_pickle": True})
            try:
                training = pickle.loads(pickle.dumps(db_conn.root.get_training(self.device_id)))
                db_conn.close()
            except Exception, e:
                current_app.logger.warn("There was a problem reading from db")
                current_app.logger.error(e)
                db_conn.close()
        except Exception, e:
            current_app.logger.warning("There was a problem connecting to db")
            current_app.logger.error(e)
        return training

    def start_training(self):
        result = False
        try:
            db_conn = rpyc.connect(current_app.config["custom_config"]["db_service_address"],
                                   current_app.config["custom_config"]["db_service_port"])
            try:
                result = db_conn.root.start_training(self.device_id)
                db_conn.close()
            except Exception, e:
                current_app.logger.warn("There was a problem inserting to db")
                current_app.logger.error(e)
                db_conn.close()
        except Exception, e:
            current_app.logger.warning("There was a problem connecting to db")
            current_app.logger.error(e)
        return result

    def end_training(self):
        try:
            db_conn = rpyc.connect(current_app.config["custom_config"]["db_service_address"],
                                   current_app.config["custom_config"]["db_service_port"])
            try:
                db_conn.root.end_training(self.device_id)
                db_conn.close()
            except Exception, e:
                current_app.logger.warn("There was a problem ending training")
                current_app.logger.error(e)
                db_conn.close()
        except Exception, e:
            current_app.logger.warning("There was a problem connecting to db")
            current_app.logger.error(e)

    def update_offset(self, new_offset):
        result = False
        try:
            db_conn = rpyc.connect(current_app.config["custom_config"]["db_service_address"],
                                   current_app.config["custom_config"]["db_service_port"])
            try:
                result = db_conn.root.update_offset(self.device_id, new_offset)
                db_conn.close()
            except Exception, e:
                current_app.logger.warn("There was a problem updating db")
                current_app.logger.error(e)
                db_conn.close()
        except Exception, e:
            current_app.logger.warning("There was a problem connecting to db")
            current_app.logger.error(e)
        return result

    def submit_vote(self, vote):
        result = False
        try:
            db_conn = rpyc.connect(current_app.config["custom_config"]["db_service_address"],
                                   current_app.config["custom_config"]["db_service_port"])
            try:
                result = db_conn.root.insert_vote(self.device_id, vote)
                db_conn.close()
            except Exception, e:
                current_app.logger.warn("There was a problem inserting to db")
                current_app.logger.error(e)
                db_conn.close()
        except Exception, e:
            current_app.logger.warning("There was a problem connecting to db")
            current_app.logger.error(e)
        return result

    def get_pmv_ppv_list(self, start_date):
        pmv_ppv_list = list()
        try:
            db_conn = rpyc.connect(current_app.config["custom_config"]["db_service_address"],
                                   current_app.config["custom_config"]["db_service_port"],
                                   config={"allow_pickle": True, "allow_public_attrs": True})
            try:
                pmv_ppv_list = pickle.loads(pickle.dumps(db_conn.root.get_pmv_ppv_list(self.device_id, start_date)))
                db_conn.close()
            except Exception, e:
                current_app.logger.warn("There was a problem reading from db")
                current_app.logger.error(e)
                db_conn.close()
        except Exception, e:
            current_app.logger.warning("There was a problem connecting to db")
            current_app.logger.error(e)
        pmv_list = list()
        ppv_list = list()
        for pmv_ppv_item in pmv_ppv_list:
            pmv_list.append([(pmv_ppv_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, pmv_ppv_item["pmv"]])
            ppv_list.append([(pmv_ppv_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, pmv_ppv_item["ppv"]])
        return [pmv_list, ppv_list]

    def get_last_pmv_ppv(self):
        pmv_ppv_list = list()
        try:
            db_conn = rpyc.connect(current_app.config["custom_config"]["db_service_address"],
                                   current_app.config["custom_config"]["db_service_port"],
                                   config={"allow_pickle": True, "allow_public_attrs": True})
            try:
                pmv_ppv_list = pickle.loads(pickle.dumps(db_conn.root.get_last_pmv_ppv(self.device_id)))
                db_conn.close()
            except Exception, e:
                current_app.logger.warn("There was a problem reading from db")
                current_app.logger.error(e)
                db_conn.close()
        except Exception, e:
            current_app.logger.warning("There was a problem connecting to db")
            current_app.logger.error(e)
        pmv_list = list()
        ppv_list = list()
        for pmv_ppv_item in pmv_ppv_list:
            pmv_list.append([(pmv_ppv_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, pmv_ppv_item["pmv"]])
            ppv_list.append([(pmv_ppv_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, pmv_ppv_item["ppv"]])
        return [pmv_list, ppv_list]

    def get_occupancy_temperature_list(self, start_date):
        temperature_list = list()
        occupancy_list = list()
        try:
            db_conn = rpyc.connect(current_app.config["custom_config"]["db_service_address"],
                                   current_app.config["custom_config"]["db_service_port"],
                                   config={"allow_pickle": True, "allow_public_attrs": True})
            try:
                temperature_list = pickle.loads(pickle.dumps(db_conn.root.get_temperature_list(self.device_id, start_date)))
                occupancy_list = pickle.loads(pickle.dumps(db_conn.root.get_occupancy_list(self.device_id, start_date)))
                db_conn.close()
            except Exception, e:
                current_app.logger.warn("There was a problem reading from db")
                current_app.logger.error(e)
                db_conn.close()
        except Exception, e:
            current_app.logger.warning("There was a problem connecting to db")
            current_app.logger.error(e)
        temperature_modified_list = list()
        for temperature_item in temperature_list:
            temperature_modified_list.append([(temperature_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, temperature_item["temperature"]])

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
            occupancy_modified_list.append([(occupancy_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, current_occupancy])
        return [occupancy_modified_list, temperature_modified_list]

    def get_last_occupancy_temperature(self):
        temperature_list = list()
        occupancy_list = list()
        try:
            db_conn = rpyc.connect(current_app.config["custom_config"]["db_service_address"],
                                   current_app.config["custom_config"]["db_service_port"],
                                   config={"allow_pickle": True, "allow_public_attrs": True})
            try:
                temperature_list = pickle.loads(pickle.dumps(db_conn.root.get_last_temperature(self.device_id)))
                occupancy_list = pickle.loads(pickle.dumps(db_conn.root.get_last_occupancy(self.device_id)))
                db_conn.close()
            except Exception, e:
                current_app.logger.warn("There was a problem reading from db")
                current_app.logger.error(e)
                db_conn.close()
        except Exception, e:
            current_app.logger.warning("There was a problem connecting to db")
            current_app.logger.error(e)
        temperature_modified_list = list()
        for temperature_item in temperature_list:
            temperature_modified_list.append([(temperature_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, temperature_item["temperature"]])

        occupancy_modified_list = list()
        for occupancy_item in occupancy_list:
            occupancy_modified_list.append([(occupancy_item["timestamp"] - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, occupancy_item["occupancy"]/2.0])
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
