__author__ = 'Alimohammad'

import sched
import threading
import time
import sys
import esky

from config import Config

# This class checks for updates periodically.

class Updater:
    def __init__(self):
        pass

    @staticmethod
    def start():
        update_thread = threading.Thread(target=Updater.update_worker)
        update_thread.daemon = True
        update_thread.start()
        Config.logger.info("Updater started...")

    @staticmethod
    def update_worker():
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(0, 1, Updater.auto_update, (scheduler, ))
        scheduler.run()

    @staticmethod
    def auto_update(scheduler):
        if hasattr(sys, "frozen"):
            app = esky.Esky(sys.executable, Config.update_config["update_url"])
            app.auto_update(callback=Updater.update_callback)
        scheduler.enter(int(Config.update_config["update_interval"]), 1, Updater.auto_update, (scheduler, ))

    @staticmethod
    def update_callback(update_dict):
        Config.logger.info(update_dict["status"])