__author__ = 'Alimohammad'

from spotlight_config import Config
from spotlight_devices import RPi

import time

class Reactive:
    def __init__(self):
        speed = 0.05
        while True:
            RPi.set_fan_speed(speed)
            speed += 0.05
            time.sleep(10)

    def motion_updated(self, standard_deviation):
        Config.logger.info("[Motion_STD]" + str(standard_deviation))

    def temperature_updated(self, temperature):
        pass