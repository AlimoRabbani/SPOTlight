__author__ = 'Alimohammad'

import rpyc
from config import Config


class ReactiveControl:
    def __init__(self):
        pass

    @staticmethod
    def temperature_updated(temperature):
        db_conn = rpyc.connect(Config.service_config["db_service_address"], Config.service_config["db_service_port"])
        db_conn.root.insert_temperature(temperature, Config.service_config["user_id"])
        db_conn.close()
        Config.logger.info("[Temperature][%s]" % str(temperature))

    @staticmethod
    def motion_updated(standard_deviation):
        db_conn = rpyc.connect(Config.service_config["db_service_address"], Config.service_config["db_service_port"])
        db_conn.root.insert_motion(standard_deviation,Config.service_config["user_id"])
        db_conn.close()
        Config.logger.info("[Motion_STD][%s]" % str(standard_deviation))
