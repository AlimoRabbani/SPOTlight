__author__ = 'Alimohammad'

import sched
import threading
import time
import sys
import esky

import os
from esky.util import appdir_from_executable

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
            try:
                if app.find_update() is not None:
                    app.auto_update(callback=Updater.update_callback)
                    app_exe = esky.util.appexe_from_executable(sys.executable)
                    os.execv(app_exe, [app_exe] + sys.argv[1:])
            except Exception, e:
                Config.logger.warn("Error updating app")
                Config.logger.error(e)
            app.cleanup()
        scheduler.enter(int(Config.update_config["update_interval"]), 1, Updater.auto_update, (scheduler, ))

    @staticmethod
    def update_callback(update_dict):
        Config.logger.info(str(update_dict["status"]))