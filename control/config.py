__author__ = 'Alimohammad'

import json
import logging
import os
import sys
import logging.handlers
from pymongo import MongoClient


def handle_db_error(e):
    Config.logger.warn("There was a problem connecting to db")
    Config.logger.error(e)
    if Config.db_client:
        Config.db_client.close()


class Config:
    control_config = dict()
    service_config = dict()
    update_config = dict()
    db_config = dict()
    db_client = None
    logger = logging.getLogger("SPOTlight Decision")
    service_logger = logging.getLogger("SPOTlight Decision Services")
    resource_path = "/home/pi/control_config/"
    log_path = "/var/log/SPOTlight/"

    def __init__(self):
        pass

    @staticmethod
    def handle_access_db_error(e):
        Config.logger.warn("There was a problem accessing db")
        Config.logger.error(e)
        Config.connect_to_db()

    @staticmethod
    def connect_to_db():
        if Config.db_client:
            Config.db_client.close()
        Config.db_client = None
        try:
            Config.db_client = MongoClient(host=Config.db_config["db_address"], port=Config.db_config["db_port"])
            Config.db_client.the_database.authenticate(Config.db_config["db_user"],
                                                       Config.db_config["db_password"],
                                                       source=Config.db_config["db_auth_source"])
        except Exception, e:
            handle_db_error(e)

    @staticmethod
    def initialize():
        Config.control_config = json.loads(open(Config.resource_path + "config_control.json").read())
        Config.service_config = json.loads(open(Config.resource_path + "config_service.json").read())
        Config.update_config = json.loads(open(Config.resource_path + "config_update.json").read())
        Config.db_config = json.loads(open(Config.resource_path + "config_db.json").read())

        logger = logging.getLogger("SPOTlight Decision")
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.handlers.RotatingFileHandler(Config.log_path + 'control.log', maxBytes=20000000, backupCount=5)
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        service_logger = logging.getLogger("SPOTlight Decision Services")
        service_logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.handlers.RotatingFileHandler(Config.log_path + 'control_services.log', maxBytes=20000000, backupCount=5)
        file_handler.setLevel(logging.INFO)

        file_handler.setFormatter(formatter)

        service_logger.addHandler(file_handler)

        Config.connect_to_db()

        Config.logger.info("Configurations loaded...")