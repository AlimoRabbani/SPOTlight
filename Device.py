__author__ = 'Alimohammad'
import smbus
import sched, time, math
import threading
import logging


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

        temperature_thread = threading.Thread(target=self.read_temperature_scheduler)
        temperature_thread.daemon = True
        temperature_thread.start()

        motion_thread = threading.Thread(target=self.read_motion_scheduler)
        motion_thread.daemon = True
        motion_thread.start()

    def read_temperature_scheduler(self):
        tmp_scheduler = sched.scheduler(time.time, time.sleep)
        tmp_scheduler.enter(0, 1, self.read_temperature, (tmp_scheduler,))
        tmp_scheduler.run()

    def read_temperature(self, scheduler):
        start_time = time.time()
        data = self.bus.read_word_data(RPi.ADC_ADDRESS, RPi.TMP_CMD)
        data = RPi.reverse_byte_order(data) & 0x0fff
        temperature = (((data/4096.00)*5)-1.375)*1000/22.5
        RPi.logger.info("[Temperature]" + str(temperature))
        end_time = time.time()
        scheduler.enter(end_time - start_time, 1, self.read_temperature, (scheduler,))

    def read_motion_scheduler(self):
        motion_scheduler = sched.scheduler(time.time, time.sleep)
        motion_scheduler.enter(0, 1, self.read_motion, (motion_scheduler,))
        motion_scheduler.run()

    def read_motion(self, scheduler):
        start_time = time.time()
        data = self.bus.read_word_data(RPi.ADC_ADDRESS, RPi.MOTION_CMD)
        raw_motion = (RPi.reverse_byte_order(data) & 0x0fff) / 4.096
        RPi.logger.info("[Motion]" + str(raw_motion))
        # standard_deviation = math.sqrt((sum_of_squares / counter) - pow(sum_of_motion/counter, 2))
        # RPi.logger.info("[Occupancy]" + str(standard_deviation))
        # self.occupancy_callback(standard_deviation)
        end_time = time.time()
        scheduler.enter(end_time - start_time, 1, self.read_motion, (scheduler,))

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
