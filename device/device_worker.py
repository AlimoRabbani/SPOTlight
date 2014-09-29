__author__ = 'Alimohammad'

import rpyc
from rpyc.utils.server import ThreadedServer
from spotlight_devices import RPi
from rpi_config import Config


class DeviceService(rpyc.Service):
    @staticmethod
    def exposed_set_fan_speed(speed):
        RPi.set_fan_speed(speed)

    @staticmethod
    def exposed_set_fan_state(on):
        RPi.set_fan_state(on)

    @staticmethod
    def exposed_set_heater_state(on):
        RPi.set_heater_state(on)


def temperature_update_handler(temperature):
    decision_conn = rpyc.connect(Config.config["decision_service_address"], Config.config["decision_service_port"])
    decision_conn.root.temperature_update(temperature)


def motion_update_handler(motion):
    decision_conn = rpyc.connect(Config.config["decision_service_address"], Config.config["decision_service_port"])
    decision_conn.root.motion_update(motion)


if __name__ == "__main__":
    Config.initialize()
    server = ThreadedServer(DeviceService, hostname=Config.config["device_service_address"],
                            port=Config.config["device_service_port"], logger=Config.logger, authenticator=None)
    server.start()
    RPi.start(temperature_update_handler, motion_update_handler)