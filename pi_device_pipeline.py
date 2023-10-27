import time,math
import picamera
from fractions import Fraction
from datetime import datetime
from get_sensor_data import get_data
from gpiozero import AngularServo
from publish import send,connect_mqtt,subscribe
from pathlib import Path
import configparser
import json
from mongo_client_helper import save_device_config,set_device_status,add_device_log,check_device_register
from sniff import record_gas_sensor_data
from bson import ObjectId
import os,subprocess



root_path = "/home/pi/looke-client"

isdevice_registered = check_device_register()

if isdevice_registered:
    save_device_config()     

servo = AngularServo(18, min_pulse_width=0.0006, max_pulse_width=0.0023)
config = configparser.ConfigParser()
config.read(root_path + "/config.ini")



device_configuration = config["device_configuration"]
device_id = device_configuration["device_id"]
device_thing = device_configuration["device_thing"]
device_name = device_configuration["name"]
deck = device_configuration["deck"]
pen = device_configuration["pen"]
location = device_configuration["location"]
lnc_id = device_configuration["lnc_id"]
tasks = device_configuration["tasks"]
count_config = device_configuration["count_config"]
sub_type = device_configuration["sub_type"]

sleep_duration_sec=device_configuration["sleep_duration_sec"]
total_distance=device_configuration["total_distance"]
number_of_collection_points=device_configuration["number_of_collection_points"]
collection_angle=device_configuration["collection_angle"]
image_zoom_level=device_configuration["image_zoom_level"]
record_duration_sec=device_configuration["record_duration_sec"]
record_angle=device_configuration["record_angle"]
collection_mode=device_configuration["collection_mode"]



curr_dt = datetime.now()
timestamp = int(round(curr_dt.timestamp()))
record_files=[]

left_videofile="{}_{}_left_video.h264".format(timestamp,device_thing)
right_videofile="{}_{}_right_video.h264".format(timestamp,device_thing)




print(left_videofile)

def leftside_video_capture_pipeline(camera):
    print("start left side video record")
    curr_dt = datetime.now()
    timestamp = str(int(round(curr_dt.timestamp())))
    videofilename = root_path+"/camera/{}".format(left_videofile)
    #set camera angle according device setting for record
    set_camera_angle(record_angle)
    camera.start_recording(videofilename)
    time.sleep(record_duration_sec)
    #for x in range(0,50):
    #    camera.zoom=(x/100.,x/100.,0.5,0.5)
    #    time.sleep(0.1)
    #time.sleep(1) 
    #camera.zoom=(0,0,1,1)
    camera.stop_recording()   
    record_files.append(left_videofile) 
    leftside_capture_images(camera)    

def leftside_capture_images(camera):
    
    for angle in collection_angle:
        print(angle)
        set_camera_angle(angle)
        for zoom in image_zoom_level:
            set_camera_zoom(camera,zoom)
            image_file_name = "{}_{}_{}_left_image{}.jpeg".format(timestamp,device_thing,angle,zoom)
            camera.capture(root_path + '/camera/'+ image_file_name)
            record_files.append(image_file_name)
            time.sleep(1)

    print("start left side capture image 0 degree")
    #camera position to angle 0
    set_camera_angle(0)
    for x in range(0,5):
        image_file_name = "{}_{}_{}_left_image{}.jpeg".format(timestamp,device_thing,0,x)
        camera.capture(root_path + '/camera/'+ image_file_name)
        record_files.append(image_file_name)
        time.sleep(1)
    print("start left side capture image 35 degree")
    #camera position to angle 35 degree
    set_camera_angle(35)
    for x in range(0,5):
        image_file_name = "{}_{}_{}_left_image{}.jpeg".format(timestamp,device_thing,35,x)
        camera.capture(root_path + '/camera/'+image_file_name)
        record_files.append(image_file_name)
        time.sleep(1)
    #camera position to angle 55 degree
    set_camera_angle(55)
    print("start left side capture image 55 degree")
    for x in range(0,5):
        image_file_name = "{}_{}_{}_left_image{}.jpeg".format(timestamp,device_thing,55,x)
        camera.capture(root_path + '/camera/'+image_file_name)
        record_files.append(image_file_name)
        time.sleep(1)    


def rightside_video_capture_pipeline(camera):
    print("start right side video recording")
    curr_dt = datetime.now()
    timestamp = str(int(round(curr_dt.timestamp())))
    videofilename = root_path + "/camera/{}".format(right_videofile)
    #set camera angle according device setting for record
    angle = record_angle * -1
    set_camera_angle(angle)
    camera.start_recording(videofilename)
    time.sleep(record_duration_sec)
    #for x in range(0,50):
    #    camera.zoom=(x/100.,x/100.,0.5,0.5)
    #    time.sleep(0.1)
    #time.sleep(1) 
    #camera.zoom=(0,0,1,1)
    camera.stop_recording()
    record_files.append(right_videofile)
    rightside_capture_images(camera)    

def rightside_capture_images(camera):

    for angle in collection_angle:
        print(angle)
        angle = angle * -1
        set_camera_angle(angle)
        for zoom in image_zoom_level:
            set_camera_zoom(camera,zoom)
            image_file_name = "{}_{}_{}_right_image{}.jpeg".format(timestamp,device_thing,angle,zoom)
            camera.capture(root_path + '/camera/'+ image_file_name)
            record_files.append(image_file_name)
            time.sleep(1)

    print("start right side capture image 0 degree")
    #camera position to angle 0
    set_camera_angle(0)
    for x in range(0,5):
        image_file_name = "{}_{}_{}_right_image{}.jpeg".format(timestamp,device_thing,0,x)
        camera.capture(root_path +'/camera/'+image_file_name)
        record_files.append(image_file_name)
        time.sleep(1)
    print("start right side capture image 35 degree")
    #camera position to angle 35 degree
    set_camera_angle(-35)
    for x in range(6,10):
        image_file_name = "{}_{}_{}_right_image{}.jpeg".format(timestamp,device_thing,35,x)
        camera.capture(root_path + '/camera/'+image_file_name)
        record_files.append(image_file_name)
        time.sleep(1)
    print("start right side capture image 55 degree")
    #camera position to angle 55 degree
    set_camera_angle(-55)
    for x in range(11,15):
        image_file_name = "{}_{}_{}_right_image{}.jpeg".format(timestamp,device_thing,55,x)
        camera.capture(root_path+ '/camera/'+image_file_name)
        record_files.append(image_file_name)
        time.sleep(1)    
    
def set_camera_angle(angle):
    servo.angle = angle
    time.sleep(2)
    #servo1.ChangeDutyCycle(0)

def set_camera_zoom(camera,mpx):
    camera.zoom=(0,0,0.5,0.5)

def check_mount_and_configured():
    mountpath = root_path + "/camera"
    ismount = os.path.ismount(mountpath)
    print("directory mount " + str(ismount))
    if ismount == False:        
        for f in os.listdir(mountpath):
            os.remove(os.path.join(mountpath, f))

        mount_command = "sudo sshfs -o allow_other,default_permissions,password_stdin nvidia@192.168.0.230:/home/nvidia/camera_stream/ /home/pi/looke-client/camera/  <<< {}".format('nvidia')
        subprocess.call(mount_command, shell=True, executable='/bin/bash')
        print("directory mount success")



def process_moving_device(camera,client):
    is_right = False
    is_left = False

    if collection_mode == 'both':
        is_right = True
        is_left = True
    elif collection_mode == 'only_left':
        is_left = True
    elif collection_mode == 'only_right':
        is_right = True  

    #set camera position left side
    if is_left == True:
        leftside_video_capture_pipeline(camera)  

    #set camera position right side
    if is_right == True:
        rightside_video_capture_pipeline(camera)  

    print(lnc_id)
    send_file_obj={
        "device_id":device_id,
        "device_thing":device_thing,
        "device_name":device_name,
        "deck" : deck,
        "pen" : pen,
        "location" : location,
        "exporterchannel" : lnc_id,
        "tasks":tasks,
        "files":record_files,
        "config":count_config
    }
    send(client,"$looke/filetransfer_status/"+device_thing,json.dumps(send_file_obj))

    print("recorded screen and images are successfully sent to edge device")

    print("start the receive data from sennsor and send to edge device")
    data = get_data()
    print(data)
    
    temperature = float(data["raw_temperature"])
    RH = 6.11 * 10 * ((7.5 * temperature)/(273.3 + temperature))
    WBT = temperature * math.atan(0.151977 * (RH + 8.313659)**(1/2)) + math.atan(temperature + RH) - math.atan(RH - 1.676331) + 0.00391838 *(RH)**(3/2) * math.atan(0.023101 * RH) - 4.686035 

    gas_sensor_data = record_gas_sensor_data()

    print(gas_sensor_data)
    send_sensor_obj={
        "device_id":device_id,
        "device_thing":device_thing,
        "device_name":device_name,
        "deck" : deck,
        "pen" : pen,
        "location" : location,
        "exporterchannel":lnc_id,
        "RH": RH,
        "NH3": gas_sensor_data["NH3"], 
        "WBT": WBT,
        "temperature": data["raw_temperature"],  
        "CO2": gas_sensor_data["CO2"], 
        "CH4":  gas_sensor_data["CH4"], 
        "sensor_data" : data
    }        

    send(client,"$looke/sensor_data_status/"+device_thing,json.dumps(send_sensor_obj))
    print("Send sensor data succefully.....")
    
    set_device_status(False)
    send(client,"$looke/device_status/"+device_thing,False)


    recordlog = { 
          "device": ObjectId(device_id),
          "exporterchannel": ObjectId(lnc_id),
          "logged_date": datetime.now(),
          "data_collected":"Gas sensor data, temperature and humidity",
          "status":True,          
          }
    add_device_log(recordlog)
    print('added device log...')





check_mount_and_configured()

mqtt_broker_setting = config["mqtt_broker"]
mqtthost = mqtt_broker_setting["host"]
mqttport = int(mqtt_broker_setting["port"])
print("mqtt host: ",mqtthost)
print("mqtt port: ",mqttport)

client=connect_mqtt(mqtthost,mqttport)    

if isdevice_registered == False:
    print("is device not registered")
    subscribe(client,device_thing)
    client.loop_forever()

set_device_status(True)
send(client,"$looke/device_status/"+device_thing,True)

subscribe(client,device_thing)

print("connected edged device successfully")

print("Now capture and record the screen and send to edge device.....")
Path(root_path+"/camera/").mkdir(parents=True, exist_ok=True)

print(sub_type)

if sub_type != "0":
    print("couting device")
    client.loop_forever()



with picamera.PiCamera() as camera:
   
    camera.resolution = (1920, 1080)
    #camera.framerate = Fraction(1, 6)
    camera.sensor_mode = 3
    #camera.shutter_speed = 6000000
    camera.iso = 800
    #camera.exposure_mode = 'off'     
    
    process_moving_device(camera,client)
   
    

