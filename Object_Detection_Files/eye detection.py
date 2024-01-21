#!/usr/bin/python3
import subprocess
import numpy as np
import cv2
import os
import time
import sys
import math
import glob
import signal

check = 1

# clear ram
pics = glob.glob('/run/shm/test*.jpg')
for t in range(0,len(pics)):
    os.remove(pics[t])

def Camera_start(wx,hx):
    global p
    rpistr = "libcamera-vid -t 0 --segment 1 --codec mjpeg -n -o /run/shm/test%06d.jpg --width " + str(wx) + " --height " + str(hx)
    p = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid)

#initialise variables
width        = 720
height       = 540
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade  = cv2.CascadeClassifier('haarcascade_eye.xml')
open_eyes_detected = 0
face_detected = 0
start = 0
cv2.namedWindow('Frame')
Text = "Left Mouse click on picture to EXIT, Right Mouse click for eye detaction ON/OFF"
ttrat = time.time()

#define mouse clicks (LEFT to EXIT, RIGHT to switch eye detcetion ON/OFF)
def mouse_action(event, x, y, flags, param):
    global p,check
    if event == cv2.EVENT_LBUTTONDOWN:
        os.killpg(p.pid, signal.SIGTERM)
        cv2.destroyAllWindows()
        sys.exit()
    if event == cv2.EVENT_RBUTTONDOWN:
        if check == 0:
            check = 1
        else:
            check = 0
            
cv2.setMouseCallback('Frame',mouse_action)

# start capturing images
Camera_start(width,height)

# main loop
while True:
    # remove message after 3 seconds
    if time.time() - ttrat > 3 and ttrat > 0:
        Text =""
        ttrat = 0
        
    # load image   
    pics = glob.glob('/run/shm/test*.jpg')
    while len(pics) < 2:
        pics = glob.glob('/run/shm/test*.jpg')
    pics.sort(reverse=True)
    img = cv2.imread(pics[1])
    if len(pics) > 2:
        for tt in range(2,len(pics)):
            os.remove(pics[tt])
            
    # detect face and eyes
    if check == 1: 
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        face_detected = 0
        # identify face
        for (x,y,w,h) in faces:
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            face_detected = 1
            face_size = math.sqrt((w*w)+(y*y))
            #cv2.putText(img,"Face Size : " + str(int(face_size)), (10, height - 50), 0, 0.6, (0, 255, 0))
            roi_gray = gray[y:y+(h), x:x+w]
            roi_color = img[y:y+h, x:x+w]
            open_eyes_detected = 0
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.25,5)
            # identify open eyes
            for (ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
                open_eyes_detected = 1
                cv2.putText(img,"Eyes Open: " + str(len(eyes)), (10, height - 30), 0, 0.6, (0, 255, 0))
            
        # show time eyes not open
        if face_detected == 1 and open_eyes_detected == 1 and start != 0:
            Text = "Eyes Last Closed for " + str("%3.2f" % (time.time()-start)) + " Secs"
            ttrat = time.time()
            start = 0
        # start timer on loss of open eyes
        if face_detected == 1 and open_eyes_detected == 0 and start == 0:
            start = time.time()
        if face_detected == 1 and open_eyes_detected == 0 and start != 0:
            cv2.putText(img,"Eyes Closed: " + str("%3.2f" % (time.time()-start)) + " Secs", (10, height - 30), 0, 0.6, (0, 0, 255))
        # clear timer if face and eys lost
        if face_detected == 0 and open_eyes_detected == 0:
            start = 0
    #display image
    cv2.putText(img,Text, (10, height - 10), 0, 0.4, (0, 255, 255))
    cv2.imshow('Frame',img)
    cv2.waitKey(10)
 