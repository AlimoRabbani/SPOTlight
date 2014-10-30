#!/usr/bin/env python

__author__ = 'Alimohammad'

import rpyc
from rpyc.utils.server import ThreadedServer
import RPi.GPIO as GPIO

from spotlight_devices import RPi
from device_updater import Updater
from config import Config


class DeviceService(rpyc.Service):
    @staticmethod
    def exposed_set_fan_state(on, speed):
        RPi.set_fan_state(on)
        RPi.set_fan_speed(speed)

    @staticmethod
    def exposed_set_heater_state(on):
        RPi.set_heater_state(on)


def temperature_update_handler(temperature):
    try:
        control_conn = rpyc.connect(Config.service_config["control_service_address"],
                                    Config.service_config["control_service_port"])
        try:
            control_conn.root.temperature_updated(temperature)
            control_conn.close()
        except Exception, e:
            Config.logger.warning("Error sending temperature update to %s:%s" %
                                  (Config.service_config["control_service_address"],
                                   Config.service_config["control_service_port"]))
            Config.logger.error(e)
            control_conn.close()
    except Exception, e:
        Config.logger.warning("Error connecting to %s:%s" %
                              (Config.service_config["control_service_address"],
                               Config.service_config["control_service_port"]))
        Config.logger.error(e)


def motion_update_handler(motion):
    try:
        control_conn = rpyc.connect(Config.service_config["control_service_address"],
                                    Config.service_config["control_service_port"])
        try:
            control_conn.root.motion_updated(motion)
            control_conn.close()
        except Exception, e:
            Config.logger.warning("Error sending motion update to %s:%s" %
                                  (Config.service_config["control_service_address"],
                                   Config.service_config["control_service_port"]))
            Config.logger.error(e)
            control_conn.close()
    except Exception, e:
        Config.logger.warning("Error connecting to %s:%s" %
                              (Config.service_config["control_service_address"],
                               Config.service_config["control_service_port"]))
        Config.logger.error(e)

if __name__ == "__main__":
    Config.initialize()
    Config.logger.info("SPOTlight device worker started...")
    Updater.start()
    server = ThreadedServer(DeviceService, hostname=Config.service_config["device_service_address"],
                            port=Config.service_config["device_service_port"], logger=Config.service_logger,
                            authenticator=None)
    RPi.start(temperature_update_handler, motion_update_handler)
    server.start()
    #device manager will block on this line to listen for incoming RPC requests
    Config.logger.info("SPOTlight device worker shutting down...")
    GPIO.cleanup()
