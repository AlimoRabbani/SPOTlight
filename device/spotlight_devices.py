__author__ = 'Alimohammad'
import smbus
import RPi.GPIO as GPIO
import time
import math
import threading

from config import Config


class RPi:
    def __init__(self):
        pass

    bus = smbus.SMBus(1)
    temperature_callback = None
    motion_callback = None

    @staticmethod
    def start(temperature_callback, motion_callback):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(Config.rpi_config["RPi_FAN_PIN"], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(Config.rpi_config["RPi_HEATER_PIN"], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(Config.rpi_config["RPi_DAC_AUX_PIN"], GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(Config.rpi_config["RPi_DAC_LDAC_PIN"], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(Config.rpi_config["RPi_STATUS_PIN"], GPIO.OUT, initial=GPIO.LOW)

        RPi.bus.write_word_data(int(Config.rpi_config["RPi_DAC_ADDRESS"], 16),
                                int(Config.rpi_config["RPi_DAC_REF_CMD"], 16), 0)

        RPi.temperature_callback = temperature_callback
        RPi.motion_callback = motion_callback

        temperature_thread = threading.Thread(target=RPi.read_temperature)
        temperature_thread.daemon = True
        temperature_thread.start()

        motion_thread = threading.Thread(target=RPi.read_motion)
        motion_thread.daemon = True
        motion_thread.start()

    @staticmethod
    def read_temperature():
        while True:
            data = RPi.bus.read_word_data(int(Config.rpi_config["RPi_ADC_ADDRESS"], 16),
                                          int(Config.rpi_config["RPi_TMP_CMD"], 16))
            data = RPi.reverse_byte_order(data) & 0x0fff
            temperature = (((data/4096.00)*5)-1.375)*1000/22.5
            Config.logger.info("[Temperature][%s]" % str(temperature))
            temperature_update_thread = threading.Thread(target=RPi.temperature_callback.__func__, args=(temperature, ))
            temperature_update_thread.daemon = True
            temperature_update_thread.start()
            time.sleep(Config.rpi_config["temperature_reading_resolution"])

    @staticmethod
    def read_motion():
        current_status = False
        sum_of_squares = sum_of_motion = counter = 0
        while True:
            start_time = time.time()
            current_status = not current_status
            GPIO.output(Config.rpi_config["RPi_STATUS_PIN"], current_status)
            data = RPi.bus.read_word_data(int(Config.rpi_config["RPi_ADC_ADDRESS"], 16),
                                          int(Config.rpi_config["RPi_MOTION_CMD"], 16))
            raw_motion = (RPi.reverse_byte_order(data) & 0x0fff) / 4.096
            Config.logger.debug("[Motion][%s][%s]" % (str(raw_motion), format(data, '02x')))
            counter += 1
            sum_of_motion += raw_motion
            sum_of_squares += pow(raw_motion, 2)
            if counter == int(Config.rpi_config["occupancy_std_interval"]*1/Config.rpi_config["motion_reading_resolution"]):
                standard_deviation = math.sqrt((sum_of_squares / counter) - pow(sum_of_motion/counter, 2))
                Config.logger.info("[Motion_STD][%s]" % str(standard_deviation))
                motion_update_thread = threading.Thread(target=RPi.motion_callback.__func__, args=(standard_deviation, ))
                motion_update_thread.daemon = True
                motion_update_thread.start()
                sum_of_squares = sum_of_motion = counter = 0
            end_time = time.time()
            time_difference = (end_time - start_time + 0.0008) \
                if (end_time - start_time + 0.0008) < Config.rpi_config["motion_reading_resolution"] \
                else Config.rpi_config["motion_reading_resolution"]
            time.sleep(Config.rpi_config["motion_reading_resolution"] - time_difference)

    @staticmethod
    def set_fan_speed(speed):
        # Converting 0.0-1.0 fan speed to a 12 bit voltage based number understandable by the ADC
        speed_voltage = (Config.rpi_config["fan_max_speed_voltage"] - Config.rpi_config["fan_min_speed_voltage"])*speed\
                        + Config.rpi_config["fan_min_speed_voltage"]
        speed_12bit = int((speed_voltage/(Config.rpi_config["RPi_MAX_VOLTAGE"] - Config.rpi_config["RPi_MIN_VOLTAGE"])) * 4096 * 16)
        Config.logger.info("[Fan_Speed][%s][Fan_Voltage][%s][Bit_Value][%s]"
                           % (str(speed), str(speed_voltage), format(RPi.reverse_byte_order(speed_12bit), '02x')))
        RPi.bus.write_word_data(int(Config.rpi_config["RPi_DAC_ADDRESS"], 16),
                                int(Config.rpi_config["RPi_DAC_LOAD_CMD"], 16), RPi.reverse_byte_order(speed_12bit))

    @staticmethod
    def set_fan_state(on):
        GPIO.output(Config.rpi_config["RPi_FAN_PIN"], on)
        Config.logger.info("[Fan_State][%s]" % str(on))

    @staticmethod
    def set_heater_state(on):
        RPi.set_fan_state(on)
        if on:
            RPi.set_fan_speed(1.0)
        else:
            RPi.set_fan_speed(0.0)
        GPIO.output(Config.rpi_config["RPi_HEATER_PIN"], on)
        Config.logger.info("[Heater_State][%s]" % str(on))

    @staticmethod
    def reverse_byte_order(data, byte_count=2):
        val = 0
        for i, n in enumerate(range(byte_count)):
            d = data & 0xFF
            val |= (d << (8 * (byte_count - i - 1)))
            data >>= 8
        return val

