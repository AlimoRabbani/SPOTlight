__author__ = 'Alimohammad'
from Device import RPi
import logging


logger = logging.getLogger("RPi Logger")
logger.setLevel(logging.NOTSET)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('rpi.log')
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)


file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def main():
    rpi_instance = RPi(callback)


def callback(input_occupancy):
    logger.debug("Occupancy Update Called: " + str(input_occupancy))

if __name__ == "__main__":
    main()

