__author__ = 'Alimohammad'

from esky import bdist_esky
from distutils.core import setup

setup(name="device",
      version="1.1",
      scripts=["device_worker.py", "config.py", "spotlight_devices.py", "device_updater.py", ],
      data_files=[("", ["config_rpi.json", "config_service.json", "config_update.json"])]
      )