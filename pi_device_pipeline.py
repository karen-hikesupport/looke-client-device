import time
import picamera
from fractions import Fraction
from datetime import datetime
from get_sensor_data import get_data
from gpiozero import AngularServo
from publish import send,connect_mqtt
from pathlib import Path
import configparser


servo = AngularServo(18, min_pulse_width=0.0006, max_pulse_width=0.0023)
config = configparser.ConfigParser()
config.read("config.ini")

def leftside_video_capture_pipeline(camera):
    print("start left side video record")
    curr_dt = datetime.now()
    timestamp = str(int(round(curr_dt.timestamp())))
    videofilename = "camera/videos/left_capture_video.h264"
    camera.start_recording(videofilename)
    time.sleep(10)
    for x in range(0,50):
        camera.zoom=(x/100.,x/100.,0.5,0.5)
        time.sleep(0.1)
    time.sleep(1) 
    camera.zoom=(0,0,1,1)
    camera.stop_recording()    
    leftside_capture_images(camera)    

def leftside_capture_images(camera):
    print("start left side capture image 0 degree")
    #camera position to angle 0
    set_camera_angle(0)
    for x in range(0,5):
        camera.capture('camera/images/left_image'+str(x)+'.jpeg')
        time.sleep(1)
    print("start left side capture image 35 degree")
    #camera position to angle 35 degree
    set_camera_angle(35)
    for x in range(5,10):
        camera.capture('camera/images/left_image'+str(x)+'.jpeg')
        time.sleep(1)
    #camera position to angle 55 degree
    set_camera_angle(55)
    print("start left side capture image 55 degree")
    for x in range(11,15):
        camera.capture('camera/images/left_image'+str(x)+'.jpeg')
        time.sleep(1)    


def rightside_video_capture_pipeline(camera):
    print("start right side video recording")
    curr_dt = datetime.now()
    timestamp = str(int(round(curr_dt.timestamp())))
    videofilename = "camera/videos/right_capture_video.h264"
    camera.start_recording(videofilename)
    time.sleep(10)
    for x in range(0,50):
        camera.zoom=(x/100.,x/100.,0.5,0.5)
        time.sleep(0.1)
    time.sleep(1) 
    camera.zoom=(0,0,1,1)
    camera.stop_recording()
    rightside_capture_images(camera)    

def rightside_capture_images(camera):
    print("start right side capture image 0 degree")
    #camera position to angle 0
    set_camera_angle(0)
    for x in range(0,5):
        camera.capture('camera/images/right_image'+str(x)+'.jpeg')
        time.sleep(1)
    print("start right side capture image 35 degree")
    #camera position to angle 35 degree
    set_camera_angle(-35)
    for x in range(6,10):
        camera.capture('camera/images/right_image'+str(x)+'.jpeg')
        time.sleep(1)
    print("start right side capture image 55 degree")
    #camera position to angle 55 degree
    set_camera_angle(-55)
    for x in range(11,15):
        camera.capture('camera/images/right_image'+str(x)+'.jpeg')
        time.sleep(1)    
    
def set_camera_angle(angle):
    servo.angle = angle
    time.sleep(2)
    #servo1.ChangeDutyCycle(0)

with picamera.PiCamera() as camera:

    mqtt_broker_setting = config["mqtt_broker"]
    mqtthost = mqtt_broker_setting["host"]
    mqttport = int(mqtt_broker_setting["port"])
    print(mqtthost)
    print(mqttport)
    

    camera.resolution = (1920, 1080)
    #camera.framerate = Fraction(1, 6)
    camera.sensor_mode = 3
    #camera.shutter_speed = 6000000
    camera.iso = 800
    #camera.exposure_mode = 'off'     


    client=connect_mqtt(mqtthost,mqttport)

    Path("/home/pi/looke-client/camera/").mkdir(parents=True, exist_ok=True)
    Path("/home/pi/looke-client/camera/videos").mkdir(parents=True, exist_ok=True)
    Path("/home/pi/looke-client/camera/images").mkdir(parents=True, exist_ok=True)

    leftside_video_capture_pipeline(camera)  
    #set camera position right side
    rightside_video_capture_pipeline(camera)  

    send(client,"device1/filetransfer_status/","done")
    data = get_data()
    print(data)

    
