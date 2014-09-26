__author__ = 'Alimohammad'

from spotlight_config import Config
from spotlight_devices import RPi

import time
import threading

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
        Config.logger.info("[Motion_STD]" + str(standard_deviation))

    def temperature_updated(self, temperature):
        pass