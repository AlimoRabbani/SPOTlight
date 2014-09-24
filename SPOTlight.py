__author__ = 'Alimohammad'
from Device import RPi

def main():
    rpi_instance = RPi()
    rpi_instance.temperature_callback = callback
    rpi_instance.motion_callback = callback

def callback(input):
    print "Called: " + str(input)

if __name__ == "__main__":
    main()

