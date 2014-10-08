__author__ = 'Alimohammad'

import json
import logging


class Config:
    rpi_config = dict()
    service_config = dict()
    update_config = dict()
    logger = logging.getLogger("SPOTlight RPi")
    service_logger = logging.getLogger("SPOTlight Device Services")

    def __init__(self):
        pass

    @staticmethod
    def initialize():
        Config.rpi_config = json.loads(open("config_rpi.json").read())
        Config.service_config = json.loads(open("config_service.json").read())
        Config.update_config = json.loads(open("config_update.json").read())

        logger = logging.getLogger("SPOTlight RPi")
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler('rpi.log')
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

        file_handler = logging.FileHandler('device_services.log')
        file_handler.setLevel(logging.DEBUG)

        file_handler.setFormatter(formatter)

        service_logger.addHandler(file_handler)

        Config.logger.info("Configurations loaded...")