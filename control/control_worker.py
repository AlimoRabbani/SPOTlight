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
    if hasattr(sys, "frozen"):
        app = esky.Esky(sys.executable, Config.update_config["update_url"])
        Config.logger.info("SPOTlight control worker %s started..." % app.active_version)
        app.cleanup()
        client = None
        try:
            client = connect_to_db()
            spotlight_collection = collection.Collection(client.spotlight, "Devices")
            spotlight_collection.update_one({"device_id": Config.service_config["device_id"]}, {"$set": {"control_app_version": app.active_version}})
            client.close()
        except Exception, e:
            handle_db_error(client, e)
        except Exception, e:
            Config.logger.warning("Error connecting to %s:%s" %
                                  (Config.service_config["db_service_address"],
                                   Config.service_config["db_service_port"]))
            Config.logger.error(e)
    else:
        Config.logger.info("SPOTlight control worker started...")
    Updater.start()
    server = ThreadedServer(DecisionService, hostname=Config.service_config["control_service_address"],
                            port=Config.service_config["control_service_port"], logger=Config.service_logger,
                            authenticator=None)
    server.start()
    Config.logger.info("SPOTlight control worker shutting down...")
