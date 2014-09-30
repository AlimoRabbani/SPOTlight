#!/usr/bin/env python

__author__ = 'Alimohammad'

import rpyc
from rpyc.utils.server import ThreadedServer

from reactive_control import ReactiveControl
from config import Config
from control_updater import Updater


class DecisionService(rpyc.Service):
    @staticmethod
    def exposed_temperature_updated(temperature):
        ReactiveControl.temperature_updated(temperature)

    @staticmethod
    def exposed_motion_updated(standard_deviation):
        ReactiveControl.motion_updated(standard_deviation)

if __name__ == "__main__":
    Config.initialize()
    Config.logger.info("SPOTlight device manager started...")
    Updater.start()
    server = ThreadedServer(DecisionService, hostname=Config.service_config["control_service_address"],
                            port=Config.service_config["control_service_port"], logger=Config.service_logger,
                            authenticator=None, protocol_config={"allow_public_attrs" : True})
    server.start()
    Config.logger.info("SPOTlight decision maker shutting down...")
