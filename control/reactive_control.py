__author__ = 'Alimohammad'

import rpyc
from config import Config


class ReactiveControl:
    def __init__(self):
        pass

    @staticmethod
    def temperature_updated(temperature):
        db_conn = rpyc.connect(Config.service_config["db_service_address"], Config.service_config["db_service_port"])
        db_conn.root.insert({"temperature": temperature, "user_id": Config.service_config["user_id"]}, "Measurements")
        db_conn.close()
        Config.logger.info("[Temperature][%s]" % str(temperature))

    @staticmethod
    def motion_updated(standard_deviation):
        db_conn = rpyc.connect(Config.service_config["db_service_address"], Config.service_config["db_service_port"])
        db_conn.root.insert({"motion": standard_deviation, "user_id": Config.service_config["user_id"]}, "Measurements")
        db_conn.close()
        Config.logger.info("[Motion_STD][%s]" % str(standard_deviation))
