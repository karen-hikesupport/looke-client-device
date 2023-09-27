# python3.6

import random
import configparser
from paho.mqtt import client as mqtt_client


config = configparser.ConfigParser()
config.read("config.ini")

mqtt_broker_setting = config["mqtt_broker"]
broker = mqtt_broker_setting["host"]
port = int(mqtt_broker_setting["port"])


device_configuration = config["device_configuration"]
device_id = device_configuration["device_thing"]


# Generate a Client ID with the subscribe prefix.
client_id = device_id
deviceStatusTopic = "$looke/device/"+client_id+"/status"
deviceStatusOkTopic = "$looke/device/"+client_id+"/status_receive"
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