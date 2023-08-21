from gpiozero import AngularServo
from time import sleep

servo = AngularServo(18, min_pulse_width=0.0006, max_pulse_width=0.0023)

while True:
    angle = int(input('Enter angle between 0 & 180: '))
    print(angle)
    servo.angle = angle
    sleep(2)




# while (True):
#     print("angel 90")
#     servo.angle = 90
#     sleep(2)
#     print("angel 0")
#     servo.angle = 0
#     sleep(2)
#     print("angel -90")
#     servo.angle = -90
#     sleep(2)