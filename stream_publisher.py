

import cv2
import threading
import paho.mqtt.client as mqtt


class Stream_publisher:
    
    def __init__(self,topic, video_address=0,start_stream=True, host="192.168.0.230", port=1883) -> None :
       
        
        self.client = mqtt.Client()  # create new instance
        self.client.connect(host, port)
        self.topic=topic
        self.video_source=video_address

        #self.cam = cv2.VideoCapture(0)  # webcam
        #self.cam = cv2.VideoCapture("example_video.mkv")  # place video file 
        self.cam = cv2.VideoCapture(self.video_source)  

        self.streaming_thread= threading.Thread(target=self.stream)
        if start_stream:
            self.streaming_thread.start()
    
    def start_streaming(self):
        self.streaming_thread.start()

    def stream(self):
        print("Streaming from video source : {}".format(self.video_source))
        while True:
            _ , img = self.cam.read()
            #img = cv2.resize(img, (640 ,480))  # to reduce resolution 
            img_str = cv2.imencode('.jpg', img)[1].tobytes()
            print(img_str)
            self.client.publish(self.topic, img_str)
            

if __name__ == "__main__":
    webcam= Stream_publisher("test", video_address=1)  # streaming from webcam (0) to  topic : "test"
    #file= Stream_publisher("test", video_address="kungfu-panda.mkv")  # streaming from a file to  topic : "test"
    
