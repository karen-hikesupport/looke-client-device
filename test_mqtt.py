# python 3.6

import random
import time
from paho.mqtt import client as mqtt_client
import configparser,json


config = configparser.ConfigParser()
config.read("config.ini")
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'
# username = 'emqx'
# password = 'public'



def connect_mqtt(host,port):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(host, port)
    return client


def publish(client,topic,msg):            
    print(topic)
    print(msg)
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")
       

def subscribe(client: mqtt_client, device_id:str):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe("$looke/sensor_data_status/client_device")    
    client.on_message = on_message
    client.message_callback_add("$looke/sensor_data_status/client_device", on_message_save_config)    

def on_message_save_config(client, userdata, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")    
    


def send(client,topic, msg):        
        publish(client,topic,msg)
    

def run():
    client = connect_mqtt("192.168.0.230",1883)

    send_sensor_obj={
        "device_id":1,
        "deck" : "1",
        "pen" : "1",
        "location" : "1",
        "exporterchannel":"54545",
        "RH": "1",
        "NH3": "2", 
        "WBT": 1,
        "temperature": "2",  
        "CO2": "2", 
        "CH4":  "2", 
        #"sensor_data" : data
    }  

    publish(client,"$looke/sensor_data_status/client_device",json.dumps(send_sensor_obj))
    client.loop_forever()


if __name__ == '__main__':
    run()