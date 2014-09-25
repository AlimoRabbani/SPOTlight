__author__ = 'Alimohammad'

import urllib2
import httplib
import sched
import time
import json
import threading
import logging
import os

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64decode

from spotlight_config import Config

# This class checks for updates periodically.
# If an update is found, it starts downloading all the source files
# specified in the json files and verifies their signatures against the public key.
# If all files are verified, it replaces them and restarts the main application

# Signature code is a courtesy of https://launchkey.com/docs/api/encryption


class Updater:
    def __init__(self):
        pass

    @staticmethod
    def start():
        update_thread = threading.Thread(target=Updater.update_worker)
        update_thread.daemon = True
        update_thread.start()
        Config.logger.info("Updater started...")

    @staticmethod
    def update_worker():
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(0, 1, Updater.check_for_update, (scheduler, ))
        scheduler.run()

    @staticmethod
    def check_for_update(scheduler):
        try:
            request = urllib2.urlopen(Config.config["update_url"])
            response = request.read()
            version_info = json.loads(response)
            if float(version_info["version_id"]) > float(Config.config["version_id"]):
                Config.logger.info("Version " + str(version_info["version_id"]) + " found.")
                Updater.perform_update(version_info)
            else:
                Config.logger.info("Already on newest version: v%s" % str(version_info["version_id"]))
        except urllib2.HTTPError, e:
            Config.logger.warning("Unable to get latest version info - HTTPError = " + str(e.reason))
        except urllib2.URLError, e:
            Config.logger.warning("Unable to get latest version info - URLError = " + str(e.reason))
        except httplib.HTTPException, e:
            Config.logger.warning("Unable to get latest version info - HTTPException")
        except Exception, e:
            Config.logger.warning("Unable to get latest version info - Exception = " + e)
        scheduler.enter(int(Config.config["update_interval"]), 1, Updater.check_for_update, (scheduler, ))

    @staticmethod
    def perform_update(version_info):
        try:
            for updated_file in version_info["files"]:
                updated_file["tempFile"] = Updater.download_file(updated_file)
        except Exception, e:
            Config.logger.error(e)
            return
        for updated_file in version_info["files"]:
            with open(updated_file["file_name"], "wb") as source_file:
                source_file.write(updated_file["tempFile"])
        new_config = json.loads(open("config.json").read())
        Config.logger.info("Updated to version " + str(version_info["version_id"]))
        Config.logger.info("Restarting...")
        os.execv(new_config["main_file"], ('', ))

    @staticmethod
    def download_file(updated_file):
        downloaded_file = (urllib2.urlopen(updated_file['file_url'])).read()
        is_verified = Updater.verify_sign(Config.config["public_key"], updated_file["signature"], downloaded_file)
        if is_verified:
            return downloaded_file
        else:
            raise Exception("Could not verify signature for " + updated_file["file_name"])

    @staticmethod
    def verify_sign(public_key_loc, signature, data):
        pub_key = open(public_key_loc, "r").read()
        rsa_key = RSA.importKey(pub_key)
        signer = PKCS1_v1_5.new(rsa_key)
        digest = SHA256.new()
        digest.update(data)
        if signer.verify(digest, b64decode(signature)):
            return True
        return False

