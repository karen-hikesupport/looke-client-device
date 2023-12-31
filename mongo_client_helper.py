# importing module
from pymongo import MongoClient
import socket
import json
import datetime
import os
import configparser  
import getmac
import subprocess
import looke_constant


root_path = looke_constant.root_path

config = configparser.ConfigParser()
config.read(root_path + "/config.ini")


mqtt_broker_setting = config["mqtt_broker"]
mqtthost = mqtt_broker_setting["host"]


device_configuration = config["device_configuration"]
device_thing = device_configuration["device_thing"]


# creation of MongoClient
client=MongoClient()  
# Connect with the portnumber and host
client = MongoClient("mongodb://"+mqtthost+":27017/")  
# Access database
mydatabase = client["db"]  
# Access collection of the database
devicecollection=mydatabase["devices"]
devicelogcollection=mydatabase["device.logs"]
recordcollection=mydatabase["records"]
eventscollection=mydatabase["events"]
settingscollection=mydatabase["settings"]



def check_device_register():
    result = devicecollection.find_one({'thingName':device_thing})       
    if result is None:
        return False
    else:
        return True

def save_device_config():
    result = devicecollection.find_one({'thingName':device_thing})       
    if result is None:
        print("no result")
    else:
        config.set('device_configuration', 'deck', str(result.get("deck")))
        config.set('device_configuration', 'pen', str(result.get("pen")))
        config.set('device_configuration', 'device_id', str(result.get("_id")))
        config.set('device_configuration', 'lnc_id', str(result["exporterchannel"]))
        config.set('device_configuration', 'data_interval', str(result.get("dataInterval")))
        #config.set('device_configuration', 'start_time', result["start_time"])
        #config.set('device_configuration', 'end_time', result["end_time"])
        config.set('device_configuration', 'locations', str(result.get("locations")))
        config.set('device_configuration', 'feedAndWaterReview', str(result.get("feedAndWaterReview")))
        config.set('device_configuration', 'feedWaterTime', str(result.get("feedWaterTime")))
        config.set('device_configuration', 'name', str(result.get("name")))
        config.set('device_configuration', 'count_config', str(result.get("count_config")))
        config.set('device_configuration', 'sub_type', str(result.get("sub_type")))

        config.set('device_configuration', 'sleep_duration_sec', str(result.get("sleep_duration_sec")))
        config.set('device_configuration', 'total_distance', str(result.get("total_distance")))
        config.set('device_configuration', 'number_of_collection_points', str(result.get("number_of_collection_points")))
        config.set('device_configuration', 'collection_angle', str(result.get("collection_angle")))
        config.set('device_configuration', 'image_zoom_level', str(result.get("image_zoom_level")))
        config.set('device_configuration', 'record_duration_sec', str(result.get("record_duration_sec")))
        config.set('device_configuration', 'record_angle', str(result.get("record_angle")))
        config.set('device_configuration', 'collection_mode', str(result.get("collection_mode")))
        

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

def set_device_status(status:bool):    
    result = devicecollection.update_one({'thingName':device_thing}, {"$set" : {"status" :status}})   
    print(result)  

def set_device_rtsp(rtspaddress:str, pid :int):    
    result = devicecollection.update_one({'thingName':device_thing}, {"$set" : {"rtsp_address" :rtspaddress, "rtps_process_id":pid}})   
    print(result) 

    


def deleteDevice():
    result = devicecollection.delete_many({'thingName':'client_device'})

def deleteAllevents():
    result = eventscollection.delete_many({})    

def update_to_client_device():    
    devicecollection.update_one({'thingName':'client_device'}, {"$set" : {"type" :1}})   


def add_device_log(record:any):    
    rec_id1 = devicelogcollection.insert_one(record)
    print(rec_id1)

def get_device_log():    
    for x in devicelogcollection.find():
        print(x)

def get_records():    
    for x in eventscollection.find():
        print(x)   

def get_settings():    
    for x in settingscollection.find():
        print(x) 
            

def set_edgedevice_online():
        result = devicecollection.update_one({'name':'Edge Device'}, {"$set" : {"status" :True}})         

def delete_all_file():
        mountpath = "/home/pi/looke-client-device/camera"
        for f in os.listdir(mountpath):
            os.remove(os.path.join(mountpath, f))

#mount_command = "sudo sshfs -o allow_other,default_permissions,password_stdin nvidia@192.168.0.230:/home/nvidia/camera_stream/ /home/pi/looke-client/camera/  <<< {}".format('nvidia')
#subprocess.call(mount_command, shell=True, executable='/bin/bash')

#print(getmac.get_mac_address())
#deleteDevice()
#result = check_device_register()
#delete_all_file()
#deleteAllevents()
#get_settings()