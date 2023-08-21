
import os
import sys
import time
import json
import threading
import hashlib
import base64
import paho.mqtt.client as mqtt


deviceId="camera1"
HOST = "192.168.0.230"
PORT = 1883
PUBTOPIC = "/file"+"/"+deviceId
SUBTOPIC = PUBTOPIC+"/status"
CHUNKSIZE = 999
chunknumber = 0


lock = threading.Lock()
client = mqtt.Client()


def my_json(msg):
    return json.dumps(msg)  # object2string


def my_exit(err):
    os._exit(err)
    os.kill(os.getpid)


def my_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def my_publish(msg):
    try:
        client.publish(PUBTOPIC, my_json(msg), qos=0)
        if msg["end"] is False:
            print(
                "send chunk:", msg["chunknumber"], "time:",
                int(time.time()-float(msg["timeid"])), "sec")
    except Exception as e:
        print("ERR: publish", e)


def my_send(myfile):
    print('In my send function')    
    """ split, send chunk and wait lock release
    """
    global chunknumber
    time.sleep(2)   # pause for mqtt subscribe
    timeid = str(int(time.time()))
    filesize = os.path.getsize(myfile)
    filehash = my_md5(myfile)

    payload = {
        "deviceId": deviceId,
        "timeid": timeid,
        "filename": myfile,
        "filesize": filesize,
        "filehash": filehash,
        "encode": "base64",
        "chunknumber":0,
        "chunkdata":"",
        "chunkhash":"",
        "chunksize":999,
        "end": False}

    with open(myfile, 'rb') as f:
        while True:
            print(CHUNKSIZE)
            chunk = f.read(CHUNKSIZE)
            print(chunk)
            if chunk:
                data = base64.b64encode(chunk)
                payload.update({
                    "chunkdata": data.decode(),
                    "chunknumber": chunknumber,
                    "chunkhash": hashlib.md5(data).hexdigest(),
                    "chunksize": len(chunk)})
                my_publish(payload)
                lock.acquire()
                chunknumber += 1
            else:
                print(payload)
                del payload["chunknumber"]
                del payload["chunkdata"]
                del payload["chunkhash"]
                del payload["chunksize"]
                payload.update({"end": True})
                print("END transfer file:", myfile)
                my_publish(payload)
                print('after transfer pi going to sleep after 3 minute')
                delete_video()
                print('video deleted and now get sensor data and publish')                
                #sleepPi()
                break
    time.sleep(1)
    my_exit(0)


def my_event(top, msg):
    """ receive confirmation to save chunk
    and release lock for next msg
    """
    print(msg)
    global chunknumber
    try:
        j = json.loads(msg.decode())
    except Exception as e:
        print("ERR: json2msg", e)
        my_exit(2)
    try:
        if j["chunknumber"] == chunknumber:
            lock.release()
    except Exception as e:
        print("ERR: in json", e)
        my_exit(3)


def on_connect(client, userdata, flags, rc):
    print("OK Connected with result code "+str(rc))
    client.subscribe(SUBTOPIC)
    print("subscribe to:", SUBTOPIC)


def on_message(client, userdata, msg):
    ev = threading.Thread(target=my_event, args=(msg.topic, msg.payload))
    ev.daemon = True
    ev.start()

def delete_video():
     if os.path.exists("/home/pi/looke-client/camera/videos/left_capture_video.h264"):
        os.remove("/home/pi/looke-client/camera/videos/left_capture_video.h264")


def main(recorded,myfile="/home/pi/looke-client/camera/videos/left_capture_video.h264"):
    print('now start transfering the file')
    tm = time.time()
    if not os.path.isfile(myfile):
        print("ERR: no file", myfile)
        return 1

    print("START transfer file", myfile, ", chunksize =", CHUNKSIZE, "byte")
    # client.connect("localhost", 1883, 60)
    # client.connect("broker.hivemq.com", 1883, 60)
    client.connect(HOST, PORT, 60)
    # client.connect("test.mosquitto.org")
    client.on_connect = on_connect
    client.on_message = on_message

    if recorded:
       my_thread = threading.Thread(target=my_send, args=(myfile,))
       my_thread.daemon = True
       my_thread.start()       
    else:
       timeid = str(int(time.time()))
       my_thread = threading.Thread(target=get_sensor_data_and_publish, args=(timeid,))
       my_thread.daemon = True
       my_thread.start()
    
    client.loop_forever()

    


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print(__doc__)
        main()