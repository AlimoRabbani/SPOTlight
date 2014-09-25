__author__ = 'Alimohammad'

from spotlight_config import Config


class Reactive:
    def __init__(self):
        pass

    def motion_updated(self, standard_deviation):
        Config.logger.info("[Motion_STD]" + str(standard_deviation))

    def temperature_updated(self, temperature):
        Config.logger.info("[Temperature2]" + str(temperature))
