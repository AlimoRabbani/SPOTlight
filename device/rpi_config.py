__author__ = 'Alimohammad'

import json
import logging


class Config:
    config = dict()
    logger = logging.getLogger("SPOTlight RPi")

    def __init__(self):
        pass

    @staticmethod
    def initialize():
        Config.config = json.loads(open("rpi_config.json").read())

        logger = logging.getLogger("SPOTlight RPi")
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler('rpi.log')
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        Config.logger.info("Configurations loaded...")