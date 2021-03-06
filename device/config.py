__author__ = 'Alimohammad'

import json
import logging
import os
import sys
import logging.handlers

class Config:
    rpi_config = dict()
    service_config = dict()
    update_config = dict()
    db_config = dict()
    logger = logging.getLogger("SPOTlight RPi")
    service_logger = logging.getLogger("SPOTlight Device Services")
    resource_path = "/home/pi/device_config/"
    log_path = "/var/log/SPOTlight/"

    def __init__(self):
        pass

    @staticmethod
    def initialize():
        Config.rpi_config = json.loads(open(Config.resource_path + "config_rpi.json").read())
        Config.service_config = json.loads(open(Config.resource_path + "config_service.json").read())
        Config.update_config = json.loads(open(Config.resource_path + "config_update.json").read())
        Config.db_config = json.loads(open(Config.resource_path + "config_db.json").read())

        logger = logging.getLogger("SPOTlight RPi")
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.handlers.RotatingFileHandler(Config.log_path + 'rpi.log', maxBytes=20000000, backupCount=5)

        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        service_logger = logging.getLogger("SPOTlight Device Services")
        service_logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.handlers.RotatingFileHandler(Config.log_path + 'device_services.log', maxBytes=20000000, backupCount=5)
        file_handler.setLevel(logging.DEBUG)

        file_handler.setFormatter(formatter)

        service_logger.addHandler(file_handler)

        Config.logger.info("Configurations loaded...")