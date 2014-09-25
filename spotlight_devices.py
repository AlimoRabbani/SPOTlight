__author__ = 'Alimohammad'
import smbus
import time, math
import threading
from spotlight_config import Config


class RPi:
    def __init__(self):
        pass

    bus = smbus.SMBus(1)
    temperature_callback = None
    motion_callback = None

    @classmethod
    def start(cls, temperature_callback, motion_callback):
        cls.temperature_callback = temperature_callback
        cls.motion_callback = motion_callback

        temperature_thread = threading.Thread(target=cls.read_temperature)
        temperature_thread.daemon = True
        temperature_thread.start()

        motion_thread = threading.Thread(target=cls.read_motion)
        motion_thread.daemon = True
        motion_thread.start()

    @classmethod
    def read_temperature(cls):
        while True:
            data = cls.bus.read_word_data(int(Config.config["RPi_ADC_ADDRESS"], 16), int(Config.config["RPi_TMP_CMD"], 16))
            data = RPi.reverse_byte_order(data) & 0x0fff
            temperature = (((data/4096.00)*5)-1.375)*1000/22.5
            Config.logger.info("[Temperature]" + str(temperature))
            cls.temperature_callback(temperature)
            time.sleep(Config.config["temperature_reading_resolution"])

    @classmethod
    def read_motion(cls):
        sum_of_squares = sum_of_motion = counter = 0
        while True:
            start_time = time.time()
            data = cls.bus.read_word_data(int(Config.config["RPi_ADC_ADDRESS"], 16), int(Config.config["RPi_MOTION_CMD"], 16))
            raw_motion = (RPi.reverse_byte_order(data) & 0x0fff) / 4.096
            Config.logger.info("[Motion]" + str(raw_motion))
            counter += 1
            sum_of_motion += raw_motion
            sum_of_squares += pow(raw_motion, 2)
            if counter == Config.config["occupancy_std_interval"]*1/Config.config["motion_reading_resolution"]:
                standard_deviation = math.sqrt((sum_of_squares / counter) - pow(sum_of_motion/counter, 2))
                cls.motion_callback(standard_deviation)
                sum_of_squares = sum_of_motion = counter = 0
            end_time = time.time()
            time_difference = (end_time - start_time + 0.0008) \
                if (end_time - start_time + 0.0008) < Config.config["motion_reading_resolution"] \
                else Config.config["motion_reading_resolution"]
            time.sleep(Config.config["motion_reading_resolution"] - time_difference)

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
