#!/usr/bin/env python

import datetime

from pymongo import MongoClient
from pymongo import collection

from config import Config


def main():
    client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
    client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
    db = client.spotlight
    db_all = client.spotlight_all

    bulk_remove = db.Temperatures.initialize_ordered_bulk_op()

    one_month_ago = datetime.datetime.utcnow() + datetime.timedelta(weeks=-4)
    result = db_all.Temperatures.insert_many(db.Temperatures.find({"timestamp": {"$lte" : one_month_ago}}))

    bulk_remove.find({"timestamp": {"$lte" : one_month_ago}}).remove()

    if result:
        bulk_remove.execute()

    client.close()

if __name__ == "__main__":
    Config.initialize()
    Config.logger.info("SPOTlight db manager started...")
    main()
