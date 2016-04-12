__author__ = 'Alimohammad'

from esky import bdist_esky
from distutils.core import setup

setup(name="device",
      version="1.3",
      scripts=["device_worker.py", "config.py", "spotlight_devices.py", "device_updater.py", ]
      )