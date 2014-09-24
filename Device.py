__author__ = 'Alimohammad'
import smbus
import time
import threading
import math
import logging
import sys


class RPi:
    logger = logging.getLogger("RPi Logger")

    ADC_ADDRESS = 0x34
    TMP_CMD = 0x61
    MOTION_CMD = 0x63

    def __init__(self, occupancy_callback):
        self.temperature = 24
        self.motion = 0
        self.bus = smbus.SMBus(1)
        self.occupancy_callback = occupancy_callback

        temperature_thread = threading.Thread(target=self.read_temperature)
        temperature_thread.daemon = False
        temperature_thread.start()

        motion_thread = threading.Thread(target=self.read_motion)
        motion_thread.daemon = False
        motion_thread.start()

    def read_temperature(self):
        try:
            while True:
                data = self.bus.read_word_data(RPi.ADC_ADDRESS, RPi.TMP_CMD)
                data = RPi.reverse_byte_order(data) & 0x0fff
                temperature = (((data/4096.00)*5)-1.375)*1000/22.5
                RPi.logger.info("[Occupancy]" + str(temperature))
                time.sleep(10)
        except KeyboardInterrupt:
            sys.exit()

    def read_motion(self):
        try:
            counter = 0
            sum_of_squares = 0
            sum_of_motion = 0
            while True:
                data = self.bus.read_word_data(RPi.ADC_ADDRESS, RPi.MOTION_CMD)
                raw_motion = (RPi.reverse_byte_order(data) & 0x0fff) / 4.096
                RPi.logger.info("[Motion]" + str(raw_motion))
                sum_of_motion += raw_motion
                sum_of_squares += pow(raw_motion, 2)
                counter += 1
                if counter == 240:
                    standard_deviation = math.sqrt((sum_of_squares / counter) - pow(sum_of_motion/counter, 2))
                    RPi.logger.info("[Occupancy]" + str(standard_deviation))
                    counter = sum_of_squares = sum_of_motion = 0
                    self.occupancy_callback(2)
                time.sleep(0.5)
        except KeyboardInterrupt:
            sys.exit()

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
