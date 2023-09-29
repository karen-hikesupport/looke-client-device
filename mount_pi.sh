#!/bin/sh

sshfs -o allow_other,default_permissions,password_stdin nvidia@192.168.0.230:/home/nvidia/camera_stream/ /home/pi/looke-client/camera/  <<< "$nvidia"

