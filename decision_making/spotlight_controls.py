__author__ = 'Alimohammad'

import rpyc
from rpyc.utils.server import ThreadedServer

from reactive_control import ReactiveControl
from decision_config import Config


class DecisionService(rpyc.Service):
    @staticmethod
    def exposed_temperature_updated(temperature):
        ReactiveControl.temperature_updated(temperature)

    @staticmethod
    def exposed_motion_updated(standard_deviation):
        ReactiveControl.motion_updated(standard_deviation)

if __name__ == "__main__":
    Config.initialize()
    server = ThreadedServer(DecisionService, hostname=Config.config["decision_service_address"],
                            port=Config.config["decision_service_port"], logger=None, authenticator=None)
    server.start()