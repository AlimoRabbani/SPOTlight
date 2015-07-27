#!/usr/bin/env python

import datetime

from pymongo import MongoClient
from pymongo import collection
from config import Config


def clean_temperatures():
    print "-----------cleaning temperatures started-----------"
    client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
    client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
    db = client.spotlight
    db_all = client.spotlight_all
    bulk_remove = db.Temperatures.initialize_ordered_bulk_op()
    one_week_ago = datetime.datetime.utcnow() + datetime.timedelta(weeks=-1)

    print "found " + str(db.Temperatures.find({"timestamp": {"$lte": one_week_ago}}).count()) + " expired items"

    print "inserting expired items into backup database..."
    result = db_all.Temperatures.insert_many(list(db.Temperatures.find({"timestamp": {"$lte": one_week_ago}})))

    bulk_remove.find({"timestamp": {"$lte": one_week_ago}}).remove()
    if result:
        print "removing expired items from main database..."
        bulk_remove.execute()

    client.close()
    print "-----------cleaning up expired temperatures finished-----------"


def clean_states():
    print "-----------cleaning states started-----------"
    client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
    client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
    db = client.spotlight
    db_all = client.spotlight_all
    bulk_remove = db.States.initialize_ordered_bulk_op()
    one_week_ago = datetime.datetime.utcnow() + datetime.timedelta(weeks=-1)

    print "found " + str(db.States.find({"timestamp": {"$lte": one_week_ago}}).count()) + " expired items"

    print "inserting expired items into backup database..."
    result = db_all.States.insert_many(list(db.States.find({"timestamp": {"$lte": one_week_ago}})))

    bulk_remove.find({"timestamp": {"$lte": one_week_ago}}).remove()
    if result:
        print "removing expired items from main database..."
        bulk_remove.execute()

    client.close()
    print "-----------cleaning up expired states finished-----------"


def clean_occupancies():
    print "-----------cleaning occupancies started-----------"
    client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
    client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
    db = client.spotlight
    db_all = client.spotlight_all
    bulk_remove = db.Occupancies.initialize_ordered_bulk_op()
    one_week_ago = datetime.datetime.utcnow() + datetime.timedelta(weeks=-1)

    print "found " + str(db.Occupancies.find({"timestamp": {"$lte": one_week_ago}}).count()) + " expired items"

    print "inserting expired items into backup database..."
    result = db_all.Occupancies.insert_many(list(db.Occupancies.find({"timestamp": {"$lte": one_week_ago}})))

    bulk_remove.find({"timestamp": {"$lte": one_week_ago}}).remove()
    if result:
        print "removing expired items from main database..."
        bulk_remove.execute()

    client.close()
    print "-----------cleaning up expired occupancies finished-----------"


def clean_ppvs():
    print "-----------cleaning ppvs started-----------"
    client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
    client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
    db = client.spotlight
    db_all = client.spotlight_all
    bulk_remove = db.PPVs.initialize_ordered_bulk_op()
    one_week_ago = datetime.datetime.utcnow() + datetime.timedelta(weeks=-1)

    print "found " + str(db.PPVs.find({"timestamp": {"$lte": one_week_ago}}).count()) + " expired items"

    print "inserting expired items into backup database..."
    result = db_all.PPVs.insert_many(list(db.PPVs.find({"timestamp": {"$lte": one_week_ago}})))

    bulk_remove.find({"timestamp": {"$lte": one_week_ago}}).remove()
    if result:
        print "removing expired items from main database..."
        bulk_remove.execute()

    client.close()
    print "-----------cleaning up expired ppvs finished-----------"


def clean_motions():
    print "-----------cleaning motions started-----------"
    client = MongoClient(host=Config.db_config["mongo_server"], port=Config.db_config["mongo_port"])
    client.the_database.authenticate(Config.db_config["mongo_user"], Config.db_config["mongo_password"], source='spotlight')
    db = client.spotlight
    db_all = client.spotlight_all
    bulk_remove = db.Motions.initialize_ordered_bulk_op()
    one_week_ago = datetime.datetime.utcnow() + datetime.timedelta(weeks=-1)

    print "found " + str(db.Motions.find({"timestamp": {"$lte": one_week_ago}}).count()) + " expired items"

    print "inserting expired items into backup database..."
    result = db_all.Motions.insert_many(list(db.Motions.find({"timestamp": {"$lte": one_week_ago}})))

    bulk_remove.find({"timestamp": {"$lte": one_week_ago}}).remove()
    if result:
        print "removing expired items from main database..."
        bulk_remove.execute()

    client.close()
    print "-----------cleaning up expired motions finished-----------"


def main():
    clean_temperatures()
    clean_motions()
    clean_occupancies()
    clean_ppvs()
    clean_states()


if __name__ == "__main__":
    Config.initialize()
    Config.logger.info("SPOTstar db cleaner started...")
    main()
