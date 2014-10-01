__author__ = 'Alimohammad'

import rpyc
from config import Config
from pmv import PMV


class ReactiveControl:
    def __init__(self):
        pass

    occupancy_bucket_value = 0
    a = 1
    b = 0
    current_air_speed = 0.0
    current_heater_state = False
    current_fan_state = False
    current_temperature = 25

    @staticmethod
    def temperature_updated(temperature):
        Config.logger.info("[Temperature][%s]" % str(temperature))
        try:
            db_conn = rpyc.connect(Config.service_config["db_service_address"], Config.service_config["db_service_port"])
            try:
                db_conn.root.insert_temperature(temperature, Config.service_config["user_id"])
                db_conn.close()
            except Exception, e:
                Config.logger.warning("There was a problem inserting to db")
                Config.logger.error(e)
                db_conn.close()
        except Exception, e:
            Config.logger.warning("There was a problem connecting to db")
            Config.logger.error(e)

        ReactiveControl.current_temperature = temperature
        PMV.add_pmv(PMV.calculate_pmv(0.5, float(temperature), float(temperature), 1.2,
                                      float(ReactiveControl.current_air_speed), 100.0))

    @staticmethod
    def motion_updated(standard_deviation):
        Config.logger.info("[Motion_STD][%s]" % str(standard_deviation))
        try:
            db_conn = rpyc.connect(Config.service_config["db_service_address"], Config.service_config["db_service_port"])
            try:
                db_conn.root.insert_motion(standard_deviation,Config.service_config["user_id"])
                db_conn.close()
            except Exception, e:
                Config.logger.warning("There was a problem inserting to db")
                Config.logger.error(e)
                db_conn.close()
        except Exception, e:
            Config.logger.warning("There was a problem connecting to db")
            Config.logger.error(e)
        ReactiveControl.update_occupancy_bucket(standard_deviation)
        #calculate new a, b if there is a vote
        #insert (PMV, vote) to database and read during initiation
        PMV.empty_list()
        ReactiveControl.make_decision()

    @staticmethod
    def update_occupancy_bucket(standard_deviation):
        #update occupancy bucket based on threshold
        if standard_deviation > Config.control_config["occupancy_motion_threshold"]:
            if ReactiveControl.occupancy_bucket_value < Config.control_config["occupancy_bucket_size"]:
                ReactiveControl.occupancy_bucket_value += 1
        elif ReactiveControl.occupancy_bucket_value > 0:
            ReactiveControl.occupancy_bucket_value -= 1
        Config.logger.info("[Occupancy][%s]" % str(ReactiveControl.occupancy_bucket_value))
        try:
            db_conn = rpyc.connect(Config.service_config["db_service_address"], Config.service_config["db_service_port"])
            try:
                db_conn.root.insert_occupancy(ReactiveControl.occupancy_bucket_value, Config.service_config["user_id"])
                db_conn.close()
            except Exception, e:
                Config.logger.warning("There was a problem inserting to db")
                Config.logger.error(e)
                db_conn.close()
        except Exception, e:
            Config.logger.warning("There was a problem connecting to db")
            Config.logger.error(e)

    @staticmethod
    def make_decision():
        ppv = ReactiveControl.b +\
              ReactiveControl.a * PMV.calculate_pmv(0.5, float(ReactiveControl.current_temperature),
                                                    float(ReactiveControl.current_temperature), 1.2, 0.0, 100.0)
        if ReactiveControl.occupancy_bucket_value == 0 and ReactiveControl.current_heater_state:
            if ReactiveControl.set_heat_state(False):
                ReactiveControl.insert_state_to_db()
        elif ReactiveControl.occupancy_bucket_value == 0 and ReactiveControl.current_fan_state:
            if ReactiveControl.set_cool_state(False, 0):
                ReactiveControl.insert_state_to_db()
        elif (ReactiveControl.occupancy_bucket_value > 0 and ReactiveControl.current_fan_state
              and ppv < Config.control_config["pmv_threshold"]):
            if ReactiveControl.set_cool_state(False, 0):
                ReactiveControl.insert_state_to_db()
        elif (ReactiveControl.occupancy_bucket_value > 0 and ReactiveControl.current_heater_state
              and ppv > 0 - Config.control_config["pmv_threshold"]):
            if ReactiveControl.set_heat_state(False):
                ReactiveControl.insert_state_to_db()
        elif (ReactiveControl.occupancy_bucket_value == Config.control_config["occupancy_bucket_size"] and
                      ppv > Config.control_config["pmv_threshold"]):
            speed = 2.1
            #calculate the perfect air speed
            if ReactiveControl.set_cool_state(True, speed):
                ReactiveControl.insert_state_to_db()
        elif (ReactiveControl.occupancy_bucket_value == Config.control_config["occupancy_bucket_size"]
              and ReactiveControl.current_heater_state is False and ppv < 0 - Config.control_config["pmv_threshold"]):
            if ReactiveControl.set_heat_state(True):
                ReactiveControl.insert_state_to_db()


    @staticmethod
    def insert_state_to_db():
        try:
            db_conn = rpyc.connect(Config.service_config["db_service_address"], Config.service_config["db_service_port"])
            try:
                db_conn.root.insert_state(ReactiveControl.current_heater_state, ReactiveControl.current_fan_state,
                                          ReactiveControl.current_air_speed, Config.service_config["user_id"])
                db_conn.close()
            except Exception, e:
                Config.logger.warning("There was a problem inserting state to db")
                Config.logger.error(e)
                db_conn.close()
        except Exception, e:
            Config.logger.warning("There was a problem connecting to db")
            Config.logger.error(e)

    @staticmethod
    def set_heat_state(on):
        try:
            device_conn = rpyc.connect(Config.service_config["device_service_address"],
                                       Config.service_config["device_service_port"])
            try:
                device_conn.root.set_heater_state(on)
                device_conn.close()
                ReactiveControl.current_heater_state = on
                if on:
                    ReactiveControl.current_air_speed = Config.control_config["max_fan_speed"]
                else:
                    ReactiveControl.current_air_speed = 0
                Config.logger.info("[Set Heater State][%s]" % str(on))
                return True
            except Exception, e:
                Config.logger.warning("Error sending heater state to %s:%s" %
                                      (Config.service_config["device_service_address"],
                                       Config.service_config["device_service_port"]))
                Config.logger.error(e)
                device_conn.close()
                return False
        except Exception, e:
            Config.logger.warning("Error connecting to %s:%s" %
                                  (Config.service_config["device_service_address"],
                                   Config.service_config["device_service_port"]))
            Config.logger.error(e)
            return False

    @staticmethod
    def set_cool_state(on, speed):
        relative_speed = speed / Config.control_config["max_fan_speed"]
        try:
            device_conn = rpyc.connect(Config.service_config["device_service_address"],
                                       Config.service_config["device_service_port"])
            try:
                device_conn.root.set_fan_state(on, relative_speed)
                device_conn.close()
                ReactiveControl.current_fan_state = on
                ReactiveControl.current_air_speed = speed
                Config.logger.info("[Set Fan State][%s]" % str(on))
                Config.logger.info("[Set Fan Speed][Absolute][%s][Relative][%s]" % (str(speed), str(relative_speed)))
                return True
            except Exception, e:
                Config.logger.warning("Error sending fan state to %s:%s" %
                                      (Config.service_config["device_service_address"],
                                       Config.service_config["device_service_port"]))
                Config.logger.error(e)
                device_conn.close()
                return False
        except Exception, e:
            Config.logger.warning("Error connecting to %s:%s" %
                                  (Config.service_config["device_service_address"],
                                   Config.service_config["device_service_port"]))
            Config.logger.error(e)
            return False