#!/usr/bin/env python

__author__ = 'Alimohammad'

from spotlight_config import Config
Config.initialize()

# from spotlight_devices import RPi
import time
# import RPi.GPIO as GPIO

# from pmv import PMVs
# from spotlight_update import Updater
# from spotlight_controls import Reactive
from db import spotlight_collection

def main():
    Config.logger.info("SPOTlight v%s Started" % Config.config["version_id"])
    # Updater.start()
    # controller = Reactive()
    # controller.start()
    # RPi.start(controller.temperature_updated, controller.motion_updated)

    # logger.debug(str(PMV.calculate_pmv(0.5, 25.0, 25.0, 1.2, 0.0, 100.0)))

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        Config.logger.info("Keyboard interrupt received. Cleaning up...")
        # GPIO.cleanup()



def callback(input_occupancy):
    Config.logger.debug("Occupancy Update Called: " + str(input_occupancy))

if __name__ == "__main__":
    main()

