'''
Haar Cascade Face detection with OpenCV  
    Based on tutorial by pythonprogramming.net
    Visit original post: https://pythonprogramming.net/haar-cascade-face-eye-detection-python-opencv-tutorial/  
Adapted by Marcelo Rovai - MJRoBot.org @ 7Feb2018 
'''

import numpy as np
import cv2
import time

# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades
faceCascade = cv2.CascadeClassifier('./utils/Cascades/haarcascade_frontalface_default.xml')
cctv = 'rtsp://admin:aiti12345@11.11.11.81:554/Streaming/channels/101/'
path_cam = 'rtsp://admin:aiti12345@11.11.11.81:554/Streaming/channels/101'
path_cam1 = 'http://11.11.11.12:8555' 
cap = cv2.VideoCapture(path_cam1)

while True:
    ret, img = cap.read()
    start_time = time.time()
    # img = cv2.flip(img, -1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        img,
        
        scaleFactor=1.2,
        minNeighbors=5
        ,     
        minSize=(20, 20)
    )

    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        tinggi = x+w
        lebar = y+h
        luas = tinggi * lebar
        print('tinggi:', tinggi, ' lebar: ', lebar, ' luas:',luas )
        
    FPS=1 /(time.time()-start_time)
    cv2.putText(img, 'FPS: '+'{:.2f}'.format(FPS), (10,50), cv2.FONT_HERSHEY_COMPLEX, 1,(0,0,255),1)
    cv2.imshow('video',img)

    k = cv2.waitKey(30) & 0xff
    if k == 27: # press 'ESC' to quit
        break

cap.release()
cv2.destroyAllWindows()
