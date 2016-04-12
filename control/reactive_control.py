__author__ = 'Alimohammad'

import rpyc
from config import Config
from pmv import PMV

import datetime
import socket

from pymongo import MongoClient
from pymongo import collection


def connect_to_db():
    client = MongoClient(host=Config.db_config["db_address"], port=Config.db_config["db_port"])
    client.the_database.authenticate(Config.db_config["db_user"],
                                     Config.db_config["db_password"],
                                     source=Config.db_config["db_auth_source"])
    return client


def handle_db_error(client, e):
    Config.logger.warn("There was a problem connecting to db")
    Config.logger.error(e)
    if client:
        client.close()


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 53))
        ip = s.getsockname()[0]
        s.close()
    except Exception, e:
        Config.logger.error(e)
        s.close()
        ip = ''
    return ip



class ReactiveControl:
    def __init__(self):
        pass

    occupancy_bucket_value = 0
    current_air_speed = 0.0
    current_heat_state = False
    current_cool_state = False
    current_temperature = 25

    @staticmethod
    def temperature_updated(temperature):
        Config.logger.info("[Temperature][%s]" % str(temperature))
        client = None
        try:
            client = connect_to_db()
            spotlight_collection = collection.Collection(client.spotlight, "Temperatures")
            now_time = datetime.datetime.utcnow()
            document = {"timestamp": now_time, "device_id": Config.service_config["device_id"], "temperature": float(temperature)}
            spotlight_collection.insert_one(document)

            device_collection = collection.Collection(client.spotlight, "Devices")
            device_collection.update_one({"device_id": Config.service_config["device_id"]},
                                         {"$set": {"device_ip": get_ip(),
                                                   "latest_update": now_time,
                                                   "latest_temperature": float(temperature)}})
            client.close()
        except Exception, e:
            handle_db_error(client, e)
        ReactiveControl.current_temperature = temperature

    @staticmethod
    def motion_updated(standard_deviation):
        Config.logger.info("[Motion_STD][%s]" % str(standard_deviation))
        client = None
        try:
            client = connect_to_db()
            spotlight_collection = collection.Collection(client.spotlight, "Motions")
            document = {"timestamp": datetime.datetime.utcnow(),
                        "device_id": Config.service_config["device_id"],
                        "std": float(standard_deviation)}
            spotlight_collection.insert_one(document)
            client.close()
        except Exception, e:
            handle_db_error(client, e)
        PMV.update_parameters()
        ReactiveControl.update_occupancy_bucket(standard_deviation)
        ReactiveControl.make_decision()

    @staticmethod
    def update_occupancy_bucket(standard_deviation):
        #update occupancy bucket based on threshold
        if standard_deviation > Config.control_config["occupancy_motion_threshold"]:
            if ReactiveControl.occupancy_bucket_value < Config.control_config["occupancy_bucket_size"]:
                ReactiveControl.occupancy_bucket_value += 1
        elif ReactiveControl.occupancy_bucket_value > 0:
            ReactiveControl.occupancy_bucket_value -= 1
        Config.logger.info("[Occupancy][%s]" % str(ReactiveControl.occupancy_bucket_value))
        client = None
        try:
            client = connect_to_db()
            spotlight_collection = collection.Collection(client.spotlight, "Occupancies")
            document = {"timestamp": datetime.datetime.utcnow(),
                        "device_id": Config.service_config["device_id"],
                        "occupancy": int(ReactiveControl.occupancy_bucket_value)}
            spotlight_collection.insert_one(document)
            client.close()
        except Exception, e:
            handle_db_error(client, e)

    @staticmethod
    def make_decision():
        ppv = PMV.calculate_ppv(0.5, float(ReactiveControl.current_temperature),
                                float(ReactiveControl.current_temperature), 1.2, 0.0, 60.0)
        if ReactiveControl.occupancy_bucket_value == 0 and ReactiveControl.current_heat_state:
            if ReactiveControl.set_heat_state(False):
                ReactiveControl.insert_state_to_db()
        elif ReactiveControl.occupancy_bucket_value == 0 and ReactiveControl.current_cool_state:
            if ReactiveControl.set_cool_state(False, 0):
                ReactiveControl.insert_state_to_db()
        elif (ReactiveControl.occupancy_bucket_value > 0 and ReactiveControl.current_cool_state
              and ppv < Config.control_config["pmv_threshold"]):
            if ReactiveControl.set_cool_state(False, 0):
                ReactiveControl.insert_state_to_db()
        elif (ReactiveControl.occupancy_bucket_value > 0 and ReactiveControl.current_heat_state
              and ppv > 0 - Config.control_config["pmv_threshold"]):
            if ReactiveControl.set_heat_state(False):
                ReactiveControl.insert_state_to_db()
        elif (ReactiveControl.occupancy_bucket_value == Config.control_config["occupancy_bucket_size"] and
                      ppv > Config.control_config["pmv_threshold"]):
            speed = ReactiveControl.calculate_air_speed()
            if ReactiveControl.set_cool_state(True, speed):
                ReactiveControl.insert_state_to_db()
        elif (ReactiveControl.occupancy_bucket_value == Config.control_config["occupancy_bucket_size"]
              and ReactiveControl.current_heat_state is False and ppv < 0 - Config.control_config["pmv_threshold"]):
            if ReactiveControl.set_heat_state(True):
                ReactiveControl.insert_state_to_db()
        ReactiveControl.insert_ppv_to_db()

    @staticmethod
    def calculate_air_speed():
        air_speed = 0.0
        while air_speed <= 2.1:
            ppv = PMV.calculate_ppv(0.5, float(ReactiveControl.current_temperature),
                                    float(ReactiveControl.current_temperature), 1.2, air_speed, 60.0)
            if Config.control_config["pmv_threshold"] > ppv > 0 - Config.control_config["pmv_threshold"]:
                return air_speed
            else:
                air_speed += 0.1
        return air_speed

    @staticmethod
    def set_heat_state(on):
        try:
            device_conn = rpyc.connect(Config.service_config["device_service_address"],
                                       Config.service_config["device_service_port"])
            try:
                device_conn.root.set_heater_state(on)
                device_conn.close()
                ReactiveControl.current_heat_state = on
                if on:
                    ReactiveControl.current_air_speed = Config.control_config["max_fan_speed"]
                else:
                    ReactiveControl.current_air_speed = 0
                Config.logger.info("[Set Heater State][%s]" % str(on))
                return True
            except Exception, e:
                Config.logger.warning("Error sending heater state to %s:%s" %
                                      (Config.service_config["device_service_address"],
                                       Config.service_config["device_service_port"]))
                Config.logger.error(e)
                device_conn.close()
                return False
        except Exception, e:
            Config.logger.warning("Error connecting to %s:%s" %
                                  (Config.service_config["device_service_address"],
                                   Config.service_config["device_service_port"]))
            Config.logger.error(e)
            return False

    @staticmethod
    def set_cool_state(on, speed):
        relative_speed = float(speed) / Config.control_config["max_fan_speed"]
        try:
            device_conn = rpyc.connect(Config.service_config["device_service_address"],
                                       Config.service_config["device_service_port"])
            try:
                device_conn.root.set_fan_state(on, relative_speed)
                device_conn.close()
                ReactiveControl.current_cool_state = on
                ReactiveControl.current_air_speed = float(speed)
                Config.logger.info("[Set Fan State][%s]" % str(on))
                Config.logger.info("[Set Fan Speed][Absolute][%s][Relative][%s]" %
                                   (str(float(speed)), str(relative_speed)))
                return True
            except Exception, e:
                Config.logger.warning("Error sending fan state to %s:%s" %
                                      (Config.service_config["device_service_address"],
                                       Config.service_config["device_service_port"]))
                Config.logger.error(e)
                device_conn.close()
                return False
        except Exception, e:
            Config.logger.warning("Error connecting to %s:%s" %
                                  (Config.service_config["device_service_address"],
                                   Config.service_config["device_service_port"]))
            Config.logger.error(e)
            return False

    @staticmethod
    def insert_state_to_db():
        client = None
        try:
            client = connect_to_db()
            spotlight_collection = collection.Collection(client.spotlight, "States")
            document = {"timestamp": datetime.datetime.utcnow(),
                        "device_id": Config.service_config["device_id"],
                        "heat": ReactiveControl.current_heat_state,
                        "cool": ReactiveControl.current_cool_state,
                        "speed": ReactiveControl.current_air_speed}
            spotlight_collection.insert_one(document)
            client.close()
        except Exception, e:
            handle_db_error(client, e)

    @staticmethod
    def insert_ppv_to_db():
        ppv = PMV.calculate_ppv(0.5, float(ReactiveControl.current_temperature),
                                float(ReactiveControl.current_temperature), 1.2, 0.0, 60.0)
        pmv = PMV.calculate_pmv(0.5, float(ReactiveControl.current_temperature),
                                float(ReactiveControl.current_temperature), 1.2, 0.0, 60.0)
        if ReactiveControl.current_cool_state:
            ppv = PMV.calculate_ppv(0.5, float(ReactiveControl.current_temperature),
                                    float(ReactiveControl.current_temperature), 1.2,
                                    ReactiveControl.current_air_speed, 60.0)
            pmv = PMV.calculate_pmv(0.5, float(ReactiveControl.current_temperature),
                                    float(ReactiveControl.current_temperature), 1.2,
                                    ReactiveControl.current_air_speed, 60.0)
        client = None
        try:
            client = connect_to_db()
            ppv_collection = collection.Collection(client.spotlight, "PPVs")
            document = {"timestamp": datetime.datetime.utcnow(),
                        "device_id": Config.service_config["device_id"],
                        "pmv": pmv,
                        "ppv": ppv}
            ppv_collection.insert_one(document)
            client.close()
        except Exception, e:
            handle_db_error(client, e)
