__author__ = 'Alimohammad'
import smbus
import RPi.GPIO as GPIO
import time, math
import threading
from spotlight_config import Config


class RPi:
    def __init__(self):
        pass

    bus = smbus.SMBus(1)
    temperature_callback = None
    motion_callback = None

    @staticmethod
    def start(temperature_callback, motion_callback):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(Config.config["RPi_FAN_PIN"], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(Config.config["RPi_HEATER_PIN"], GPIO.OUT, initial=GPIO.LOW)
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
            data = RPi.bus.read_word_data(int(Config.config["RPi_ADC_ADDRESS"], 16),
                                          int(Config.config["RPi_TMP_CMD"], 16))
            data = RPi.reverse_byte_order(data) & 0x0fff
            temperature = (((data/4096.00)*5)-1.375)*1000/22.5
            Config.logger.info("[Temperature]" + str(temperature))
            RPi.temperature_callback(temperature)
            time.sleep(Config.config["temperature_reading_resolution"])

    @staticmethod
    def read_motion():
        sum_of_squares = sum_of_motion = counter = 0
        while True:
            start_time = time.time()
            data = RPi.bus.read_word_data(int(Config.config["RPi_ADC_ADDRESS"], 16),
                                          int(Config.config["RPi_MOTION_CMD"], 16))
            raw_motion = (RPi.reverse_byte_order(data) & 0x0fff) / 4.096
            Config.logger.info("[Motion]" + str(raw_motion))
            counter += 1
            sum_of_motion += raw_motion
            sum_of_squares += pow(raw_motion, 2)
            if counter == Config.config["occupancy_std_interval"]*1/Config.config["motion_reading_resolution"]:
                standard_deviation = math.sqrt((sum_of_squares / counter) - pow(sum_of_motion/counter, 2))
                RPi.motion_callback(standard_deviation)
                sum_of_squares = sum_of_motion = counter = 0
            end_time = time.time()
            time_difference = (end_time - start_time + 0.0008) \
                if (end_time - start_time + 0.0008) < Config.config["motion_reading_resolution"] \
                else Config.config["motion_reading_resolution"]
            time.sleep(Config.config["motion_reading_resolution"] - time_difference)

    @staticmethod
    def set_fan_speed(speed):
        # Converting 0.0-1.0 fan speed to a 12 bit voltage based number understandable by the ADC
        speed_voltage = (Config.config["fan_max_speed_voltage"] - Config.config["fan_min_speed_voltage"])*speed\
                        + Config.config["fan_min_speed_voltage"]
        speed_12bit = int((speed_voltage/Config.config["RPi_MAX_VOLTAGE"]) * 4096)
        RPi.bus.write_word_data(int(Config.config["RPi_DAC_ADDRESS"], 16),
                                int(Config.config["RPi_DAC_CMD"], 16), RPi.reverse_byte_order(speed_12bit))

    @staticmethod
    def set_fan_state(on):
        GPIO.output(Config.config["RPi_FAN_PIN"], on)

    @staticmethod
    def set_heater_state(on):
        GPIO.output(Config.config["RPi_HEATER_PIN"], on)

    @staticmethod
    def reverse_byte_order(data):
        dst = hex(data)[2:].replace('L', '')
        byte_count = len(dst[::2])
        val = 0
        for i, n in enumerate(range(byte_count)):
            d = data & 0xFF
            val |= (d << (8 * (byte_count - i - 1)))
            data >>= 8
        return val
