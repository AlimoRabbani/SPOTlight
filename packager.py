__author__ = 'Alimohammad'

import json
import os
import shutil

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode

from spotlight_config import Config

# This application makes a package of the application.
# It signs each file with the private key and saves all the info in update.json.
# At the end, the folder named "package" contains all the files required to
# automatically update all instances of SPOTlight.
# The packager folder should be uploaded on the server

# Signature code is a courtesy of https://launchkey.com/docs/api/encryption

package_directory = "package"
main_url = "http://onible.com/SPOTlight/"
private_key_location = "SPOTlight_key.private"
source_files = ["spotlight.py", "spotlight_update.py", "spotlight_config.py", "spotlight_devices",
                "spotlight_controls.py", "pmv.py", "config.json"]

Config.initialize()


def main():
    if not os.path.exists(package_directory):
        os.makedirs(package_directory)
    update = dict()
    update["version_id"] = Config.config["version_id"]
    update["files"] = list()
    for source_file_name in source_files:
        new_source_file = dict()
        new_source_file["file_url"] = main_url + source_file_name
        new_source_file["file_name"] = source_file_name
        new_source_file["signature"] = sign_data(private_key_location, open(source_file_name, "rb").read())
        update["files"].append(new_source_file)
    with open(os.path.join(package_directory, "update.json"), "w") as outfile:
        json.dump(update, outfile)

    for source_file_name in source_files:
        file_name = str(os.path.join(package_directory, source_file_name))
        shutil.copy2(source_file_name, file_name)


def sign_data(private_key_loc, data):
    key = open(private_key_loc, "r").read()
    rsa_key = RSA.importKey(key)
    signer = PKCS1_v1_5.new(rsa_key)
    digest = SHA256.new()
    digest.update(data)
    sign = signer.sign(digest)
    return b64encode(sign)

if __name__ == "__main__":
    main()
