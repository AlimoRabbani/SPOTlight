__author__ = 'Alimohammad'

import db
from decision_config import Config


class ReactiveControl:
    def __init__(self):
        pass

    @staticmethod
    def temperature_updated(temperature):
        db.insert({"temperature": temperature}, "Measurements")
        Config.logger.info("[Temperature][%s]" % str(temperature))

    @staticmethod
    def motion_updated(standard_deviation):
        db.insert({"motion": standard_deviation}, "Measurements")
        Config.logger.info("[Motion_STD][%s]" % str(standard_deviation))
