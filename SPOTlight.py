__author__ = 'Alimohammad'
from Device import RPi
import logging


logger = logging.getLogger("RPi Logger")
logger.setLevel(logging.INFO)
handler = logging.FileHandler('rpi.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def main():
    rpi_instance = RPi(callback)


def callback(input_id):
    print "Called: " + str(input_id)

if __name__ == "__main__":
    main()

