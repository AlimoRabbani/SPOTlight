__author__ = 'Alimohammad'

import json
import logging


class Config:
    config = dict()
    db_config = dict()
    logger = logging.getLogger("SPOTlight")

    def __init__(self):
        pass

    @staticmethod
    def initialize():
        Config.config = json.loads(open("config.json").read())
        Config.db_config = json.loads(open("db.json").read())

        logger = logging.getLogger("SPOTlight")
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler('spotlight.log')
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)


        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        Config.logger.info("Configurations loaded...")


