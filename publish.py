# python 3.6

import random
import time
from paho.mqtt import client as mqtt_client
import configparser
import socket,json
import getmac
import mongo_client_helper
import subprocess, os
import get_process
import looke_constant


root_path = looke_constant.root_path
base_path = looke_constant.base_path

config = configparser.ConfigParser()
config.read( root_path + "/config.ini")


device_configuration = config["device_configuration"]
device_thing = device_configuration["device_thing"]
print(device_thing)
# Generate a Client ID with the publish prefix.
client_id = f'publish'
# username = 'emqx'
# password = 'public'

def on_log(client, userdata, level, buf):
    print(datetime.datetime.now(), buf)

def on_disconnect(client, userdata, rc):    
    print("disconnected OK")

def connect_mqtt(host,port):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect    
    client.on_log=on_log
    client.on_disconnect = on_disconnect
    client._connect_timeout = 5000
    client.connect(host, port,keepalive=0)    
    return client


def publish(client,topic,msg):            
    print(topic)   
    result = client.publish(topic, msg, qos=2, retain=False)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")
       

def subscribe(client: mqtt_client, device_thing:str):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe("/device/" + device_thing + "/save_config")  
    client.subscribe("$looke/device/"+device_thing+"/status")  
    client.subscribe("$looke/device/" + device_thing + "/start_rtsp")  
    client.subscribe("$looke/device/"+device_thing+"/stop_rtsp")  
    client.subscribe("$looke/device/" + device_thing + "/start_countzone")
    client.subscribe("$looke/device/" + device_thing + "/stop_countzone")
    client.on_message = on_message
    client.message_callback_add("/device/" + device_thing + "/save_config", on_message_save_config)
    client.message_callback_add("$looke/device/"+device_thing+"/status", on_message_status_check)   
    client.message_callback_add("$looke/device/" + device_thing + "/start_rtsp", on_message_start_rtsp)
    client.message_callback_add("$looke/device/"+device_thing+"/stop_rtsp", on_message_stop_rtsp)  
    client.message_callback_add("$looke/device/" + device_thing + "/start_countzone", on_message_start_countzone)
    client.message_callback_add("$looke/device/" + device_thing + "/stop_countzone", on_message_stop_countzone)

def on_message_save_config(client, userdata, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    config.set('device_configuration', 'deck', '1')
    config.set('device_configuration', 'pen', '1')
    config.set('device_configuration', 'location', '1')
    config.set('device_configuration', 'data_interval', '1')
    #config.set('device_configuration', 'tasks', ["animal_counting","lameness"])


def on_message_status_check(client, userdata, msg):
    record =json.loads(msg.payload.decode())
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    deviceStatusTopic = "$looke/device/"+device_thing+"/status"
    deviceStatusOkTopic = "$looke/device/"+device_thing+"/status_receive"
    if msg.topic == deviceStatusTopic:
            local_ip = get_local_ip()
            mac = getmac.get_mac_address()
            print(local_ip)
            print(mac)
            if mac == record["mac_address"] and device_thing == record["thing"]:
                print("match mac address")            
                device_info ={
                    'success':True,
                    'ip_address':local_ip,
                    'mac_address':mac
                }
                print(json.dumps(device_info))
                client.publish(deviceStatusOkTopic,json.dumps(device_info))
                #client.loop_stop()
                print("published done")   
            else:
                print("not match mac address")
                device_info ={
                    'success':False, 
                    'message':"associated device mac address is different."                   
                }
                client.publish(deviceStatusOkTopic,json.dumps(device_info))
            #exit()

def on_message_start_rtsp(client, userdata, msg):
        print("start rtsp server")
        cmd= base_path + "/gst-rtsp-server-1.14.4/examples/test-launch --gst-debug=3 '( rpicamsrc bitrate=8000000 awb-mode=tungsten preview=false ! video/x-h264, width=640, height=480, framerate=30/1 ! h264parse ! rtph264pay name=pay0 pt=96 )'"
        global pro
        pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid) 
        #pid =os.system("/home/pi/looke-client/gst-rtsp-server-1.14.4/examples/test-launch --gst-debug=3 '( rpicamsrc bitrate=8000000 awb-mode=tungsten preview=false ! video/x-h264, width=640, height=480, framerate=30/1 ! h264parse ! rtph264pay name=pay0 pt=96 )'")
        print("started rtsp server")        
        print(pro.pid)
        local_ip = get_local_ip()
        rtps_address = "rtsp://"+local_ip+":8554/test"
        mongo_client_helper.set_device_rtsp(rtps_address,pro.pid)

def on_message_stop_rtsp(client, userdata, msg):
        record =json.loads(msg.payload.decode())
        print('stop rtsp server now')
        print(pro)
        os.killpg(record["pid"], signal.SIGTERM) 
        local_ip = get_local_ip()
        rtps_address = "rtsp://"+local_ip+":8554/test"
        mongo_client_helper.set_device_rtsp(rtps_address,0)
        print('stopped rtsp server now')


def on_message_start_countzone(client, userdata, msg):
        get_process.stop_process('python3', 8000)
        print("start rtsp server")
        cmd="python3 " + root_path + "/rpi_camera_surveillance_system.py"
        global pro
        pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid) 
        #pid =os.system("/home/pi/looke-client/gst-rtsp-server-1.14.4/examples/test-launch --gst-debug=3 '( rpicamsrc bitrate=8000000 awb-mode=tungsten preview=false ! video/x-h264, width=640, height=480, framerate=30/1 ! h264parse ! rtph264pay name=pay0 pt=96 )'")
        print("started count config")        
        print(pro.pid)
        
def on_message_stop_countzone(client, userdata, msg):
        get_process.stop_process('python3', 8000)

def send(client,topic, msg):        
        publish(client,topic,msg)


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('192.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
  

