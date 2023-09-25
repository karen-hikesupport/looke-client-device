# python3.6

import random
import configparser
from paho.mqtt import client as mqtt_client


config = configparser.ConfigParser()
config.read("config.ini")

mqtt_broker_setting = config["mqtt_broker"]
broker = mqtt_broker_setting["host"]
port = int(mqtt_broker_setting["port"])
topic = "python/mqtt"
# Generate a Client ID with the subscribe prefix.
client_id = 'client_device'
deviceStatusTopic = "/device/"+client_id+"/status"
deviceStatusOkTopic = "/device/"+client_id+"/status_receive"
# username = 'emqx'
# password = 'public'


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if msg.topic == deviceStatusTopic:
            client.publish(deviceStatusOkTopic,"all ok")

    client.subscribe(deviceStatusTopic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()