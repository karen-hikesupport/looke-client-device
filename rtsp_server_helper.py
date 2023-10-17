import os
from paho.mqtt import client as mqtt_client
import threading
import signal
import subprocess

def connect_mqtt(host,port):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client("rtsp_client_id")
    # client.username_pw_set(username, password)
    client.on_connect = on_connect    
    #client.on_log=on_log
    #client.on_disconnect = on_disconnect
    client._connect_timeout = 500
    client.connect(host, port,keepalive=0)    
    return client 

def subscribe(client: mqtt_client, device_thing:str):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe("$looke/device/" + device_thing + "/start_rtsp")  
    client.subscribe("$looke/device/"+device_thing+"/stop_rtsp")  
    client.on_message = on_message
    client.message_callback_add("$looke/device/" + device_thing + "/start_rtsp", on_message_start_rtsp)
    client.message_callback_add("$looke/device/"+device_thing+"/stop_rtsp", on_message_stop_rtsp) 



def on_message_start_rtsp(client, userdata, msg):
        print("start rtsp server")
        cmd="/home/pi/looke-client/gst-rtsp-server-1.14.4/examples/test-launch --gst-debug=3 '( rpicamsrc bitrate=8000000 awb-mode=tungsten preview=false ! video/x-h264, width=640, height=480, framerate=30/1 ! h264parse ! rtph264pay name=pay0 pt=96 )'"
        global pro
        pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid) 
        #pid =os.system("/home/pi/looke-client/gst-rtsp-server-1.14.4/examples/test-launch --gst-debug=3 '( rpicamsrc bitrate=8000000 awb-mode=tungsten preview=false ! video/x-h264, width=640, height=480, framerate=30/1 ! h264parse ! rtph264pay name=pay0 pt=96 )'")
        print("started rtsp server")        
        print(pro.pid)

def on_message_stop_rtsp(client, userdata, msg):
        print('stop rtsp server now')
        print(pro)
        os.killpg(os.getpgid(pro.pid), signal.SIGTERM) 
        print('stopped rtsp server now')
        


mqtthost = "192.168.0.230"
mqttport = 1883
client=connect_mqtt(mqtthost,mqttport) 
subscribe(client,"client_device")    
client.loop_forever()




