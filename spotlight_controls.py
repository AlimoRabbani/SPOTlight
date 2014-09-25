__author__ = 'Alimohammad'

from spotlight_config import Config


class Reactive:
    def __init__(self):
        pass

    @staticmethod
    def motion_updated(standard_deviation):
        Config.logger.info("[Motion_STD]" + str(standard_deviation))

    @staticmethod
    def temperature_updated(temperature):
        Config.logger.info("[Temperature2]" + str(temperature))
