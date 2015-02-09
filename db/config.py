__author__ = 'Alimohammad'

import json
import logging
import logging.handlers

class Config:
    db_config = dict()
    service_config = dict()
    update_config = dict()
    logger = logging.getLogger("SPOTlight DB")
    service_logger = logging.getLogger("SPOTlight DB Services")

    def __init__(self):
        pass

    @staticmethod
    def initialize():
        Config.service_config = json.loads(open("config_service.json").read())
        Config.db_config = json.loads(open("config_db.json").read())
        Config.update_config = json.loads(open("config_update.json").read())

        logger = logging.getLogger("SPOTlight DB")
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.handlers.RotatingFileHandler(Config.log_path + 'db.log', maxBytes=20000000, backupCount=5)
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        service_logger = logging.getLogger("SPOTlight DB Services")
        service_logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.handlers.RotatingFileHandler(Config.log_path + 'db_services.log', maxBytes=20000000, backupCount=5)
        file_handler.setLevel(logging.DEBUG)

        file_handler.setFormatter(formatter)

        service_logger.addHandler(file_handler)


        Config.logger.info("Configurations loaded...")