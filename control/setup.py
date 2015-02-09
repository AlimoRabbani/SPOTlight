__author__ = 'Alimohammad'

from esky import bdist_esky
from distutils.core import setup

setup(name="control",
      version="1.2",
      scripts=["control_worker.py", "config.py", "pmv.py", "reactive_control.py", "control_updater.py", ]
      )