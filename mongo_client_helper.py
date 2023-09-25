# importing module
from pymongo import MongoClient
import socket
import json
import datetime
import os
import configparser  

config = configparser.ConfigParser()
config.read("config.ini")


mqtt_broker_setting = config["mqtt_broker"]
mqtthost = mqtt_broker_setting["host"]


device_configuration = config["device_configuration"]
device_id = device_configuration["device_id"]


# creation of MongoClient
client=MongoClient()  
# Connect with the portnumber and host
client = MongoClient("mongodb://"+mqtthost+":27017/")  
# Access database
mydatabase = client["db"]  
# Access collection of the database
devicecollection=mydatabase["devices"]


def save_device_config():
    result = devicecollection.find_one({'thingName':device_id})
    if result is None:
        print("no result")
    else:
        config.set('device_configuration', 'deck', result.deck)
        config.set('device_configuration', 'pen', result.pen)
        config.set('device_configuration', 'location', result.location)
        config.set('device_configuration', 'data_interval', result.dataInterval)
        config.set('device_configuration', 'start_time', result.start_time)
        config.set('device_configuration', 'end_time', result.end_time)

def set_device_status(status:bool):
    result = devicecollection.find_one({'thingName':device_id})
    if result is None:
        print("no result")
    else:
        devicecollection.update({"_id" : result._id }, {"$set" : {"status" :status}})
