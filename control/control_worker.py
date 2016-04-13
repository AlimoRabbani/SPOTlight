#!/usr/bin/env python

__author__ = 'Alimohammad'

import rpyc
from rpyc.utils.server import ThreadedServer
import threading
import esky
import sys

from reactive_control import ReactiveControl
from config import Config
from control_updater import Updater

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


class DecisionService(rpyc.Service):
    @staticmethod
    def exposed_temperature_updated(temperature):
        temperature_thread = threading.Thread(target=ReactiveControl.temperature_updated, args=(temperature, ))
        temperature_thread.daemon = True
        temperature_thread.start()

    @staticmethod
    def exposed_motion_updated(standard_deviation):
        motion_thread = threading.Thread(target=ReactiveControl.motion_updated, args=(standard_deviation, ))
        motion_thread.daemon = True
        motion_thread.start()

if __name__ == "__main__":
    Config.initialize()
    Config.connect_to_db()
    if hasattr(sys, "frozen"):
        app = esky.Esky(sys.executable, Config.update_config["update_url"])
        Config.logger.info("SPOTlight control worker %s started..." % app.active_version)
        app.cleanup()
        try:
            spotlight_collection = collection.Collection(Config.db_client.spotlight, "Devices")
            spotlight_collection.update_one({"device_id": Config.service_config["device_id"]}, {"$set": {"control_app_version": app.active_version}})
        except Exception, e:
            Config.handle_access_db_error(e)
    else:
        Config.logger.info("SPOTlight control worker started...")
    Updater.start()
    server = ThreadedServer(DecisionService, hostname=Config.service_config["control_service_address"],
                            port=Config.service_config["control_service_port"], logger=Config.service_logger,
                            authenticator=None)
    server.start()
    Config.logger.info("SPOTlight control worker shutting down...")
