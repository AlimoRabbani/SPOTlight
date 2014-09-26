__author__ = 'Alimohammad'

import time
import threading
import db

from spotlight_config import Config
from spotlight_devices import RPi

class Reactive:
    def __init__(self):
        pass

    def start(self):
        control_thread = threading.Thread(target=self.control_worker)
        control_thread.daemon = True
        control_thread.start()

    def control_worker(self):
        RPi.set_fan_speed(0.0)
        time.sleep(10)
        RPi.set_fan_speed(1.0)
        time.sleep(10)
        RPi.set_fan_speed(0.5)
        time.sleep(10)
        RPi.set_heater_state(True)
        RPi.set_fan_state(True)

    def motion_updated(self, standard_deviation):
        db.insert({"motion": standard_deviation}, "Measurements")
        Config.logger.info("[Motion_STD]" + str(standard_deviation))

    def temperature_updated(self, temperature):
        db.insert({"temperature": temperature}, "Measurements")
        Config.logger.info("[Temperature]" + str(temperature))