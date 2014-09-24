__author__ = 'Alimohammad'
import smbus
import time

class RPi:
    ADC_ADDRESS = 0x34
    TMP_CMD = 0x61
    MOTION_CMD = 0x63

    def __init__(self):
        self.temperature = 24
        self.motion = 0
        self.read_temperature()
        self.read_motion()

    def read_temperature(self):
        bus = smbus.SMBus(1)
        data = bus.read_word_data(RPi.ADC_ADDRESS, RPi.TMP_CMD)
        data = RPi.reverse_byte_order(data) & 0x0fff
        print (((data/4096.00)*5)-1.375)*1000/22.5
        self.temperature_callback(1)

    def read_motion(self):
        bus = smbus.SMBus(1)
        data = bus.read_word_data(RPi.ADC_ADDRESS, RPi.MOTION_CMD)
        data = RPi.reverse_byte_order(data) & 0x0fff
        print data/4.096
        self.motion_callback(2)

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
