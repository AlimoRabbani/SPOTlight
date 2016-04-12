#!/usr/bin/env python

__author__ = 'Alimohammad'

import rpyc
from rpyc.utils.server import ThreadedServer
import RPi.GPIO as GPIO
import esky
import sys
import time

from spotlight_devices import RPi
from device_updater import Updater
from config import Config

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

class DeviceService(rpyc.Service):
    @staticmethod
    def exposed_set_fan_state(on, speed):
        try:
            RPi.set_fan_state(on)
            time.sleep(0.1)
            RPi.set_fan_speed(speed)
        except Exception, e:
            Config.logger.warning("Error Accessing Fan...")
            Config.logger.error(e)
            raise e


    @staticmethod
    def exposed_set_heater_state(on):
        try:
            RPi.set_heater_state(on)
        except Exception, e:
            Config.logger.warning("Error Accessing Heater...")
            Config.logger.error(e)
            raise e


def temperature_update_handler(temperature):
    try:
        control_conn = rpyc.connect(Config.service_config["control_service_address"],
                                    Config.service_config["control_service_port"])
        try:
            control_conn.root.temperature_updated(temperature)
            control_conn.close()
        except Exception, e:
            Config.logger.warning("Error sending temperature update to %s:%s" %
                                  (Config.service_config["control_service_address"],
                                   Config.service_config["control_service_port"]))
            Config.logger.error(e)
            control_conn.close()
    except Exception, e:
        Config.logger.warning("Error connecting to %s:%s" %
                              (Config.service_config["control_service_address"],
                               Config.service_config["control_service_port"]))
        Config.logger.error(e)


def motion_update_handler(motion):
    try:
        control_conn = rpyc.connect(Config.service_config["control_service_address"],
                                    Config.service_config["control_service_port"])
        try:
            control_conn.root.motion_updated(motion)
            control_conn.close()
        except Exception, e:
            Config.logger.warning("Error sending motion update to %s:%s" %
                                  (Config.service_config["control_service_address"],
                                   Config.service_config["control_service_port"]))
            Config.logger.error(e)
            control_conn.close()
    except Exception, e:
        Config.logger.warning("Error connecting to %s:%s" %
                              (Config.service_config["control_service_address"],
                               Config.service_config["control_service_port"]))
        Config.logger.error(e)

if __name__ == "__main__":
    Config.initialize()
    if hasattr(sys, "frozen"):
        app = esky.Esky(sys.executable, Config.update_config["update_url"])
        Config.logger.info("SPOTlight device worker %s started..." % app.active_version)
        app.cleanup()
        client = None
        try:
            client = connect_to_db()
            spotlight_collection = collection.Collection(client.spotlight, "Devices")
            spotlight_collection.update_one({"device_id": Config.service_config["device_id"]}, {"$set": {"device_app_version": app.active_version}})
            client.close()
        except Exception, e:
            handle_db_error(client, e)
    else:
        Config.logger.info("SPOTlight device worker started...")
    Updater.start()
    server = ThreadedServer(DeviceService, hostname=Config.service_config["device_service_address"],
                            port=Config.service_config["device_service_port"], logger=Config.service_logger,
                            authenticator=None)
    RPi.start(temperature_update_handler, motion_update_handler)
    server.start()
    #device manager will block on this line to listen for incoming RPC requests
    Config.logger.info("SPOTlight device worker shutting down...")
    GPIO.cleanup()
