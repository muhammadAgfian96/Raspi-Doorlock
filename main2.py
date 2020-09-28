import sys
import platform
import numpy as np


# GUI FILE
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent, QTimer)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient, QImage)
from PyQt5.QtWidgets import *
from ui_main2 import Ui_MainWindow

# Raspi Sensors and Actuators
from ui_functions import *




try:
    import RPi.GPIO as gpio
    on_RPi = True
    print("work on raspberry pi")
except (ImportError, RuntimeError):
    on_RPi = False

from utils.vision_helper import draw_box_name
import raspi_function as rpi

import cv2
import time
import datetime


import threading

bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 
         'Jun', 'Jul', 'Aug', 'Okt', 'Sep',
         'Nov', 'Dec']

arrayTherm = np.zeros((240,240,3))
suhu = '0 C'

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        path_cam = 'rtsp://admin:aiti12345@11.11.11.81:554/Streaming/channels/101'
        path_cam1 = 'http://11.11.11.12:8555' 
        self.cap = cv2.VideoCapture(path_cam1)
        time.sleep(1)


        # vision opetarion
        self.streamCamera = QTimer()
        self.streamCamera.start(20)
        self.streamCamera.timeout.connect(self.stream_camera_on)

        # input operation
        self.streamSensors = QTimer()
        self.streamSensors.start(10)
        self.streamSensors.timeout.connect(self.processing_sensors)

        # output operation
        #self.streamActuators = QTimer()
        #self.streamActuators.start(5)
        #self.streamActuators.timeout.connect(self.processing_output)


        # for update time on display
        self.streamDate = QTimer()
        self.streamDate.setInterval(1000)
        self.streamDate.timeout.connect(self.showTime)
        self.streamDate.start()
        self.count_FPS = 0

        # MOVE WINDOW
        def moveWindow(event):
            # RESTORE BEFORE MOVE
            if UIFunctions.returnStatus() == 1:
                UIFunctions.maximize_restore(self)

            # IF LEFT CLICK MOVE WINDOW
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        # SET TITLE BAR
        self.ui.fr_jam.mouseMoveEvent = moveWindow

        ## ==> SET UI DEFINITIONS
        UIFunctions.uiDefinitions(self)


        ## SHOW ==> MAIN WINDOW
        self.show()

    ## APP EVENTS
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def visionThermal(self,image):
        arrayTherm = rpi.thermalCam.getThermal()
        # -------- overlay thermal ----------
        y_offset=image.shape[0]-arrayTherm.shape[0]
        x_offset=0

        alpha = 0.5
        output = image[y_offset:y_offset+arrayTherm.shape[0], x_offset:x_offset+arrayTherm.shape[1]] 
        cv2.addWeighted(arrayTherm, alpha, output, 1 - alpha, 0, output)
        image[y_offset:y_offset+arrayTherm.shape[0], x_offset:x_offset+arrayTherm.shape[1]] = output
        return image

    def stream_camera_on(self):
        global arrayTherm, suhu

        # read image in BGR format
        ret, image = self.cap.read()
        # convert image to RGB format
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h_img, w_img, ch = image.shape
        h_1 = h_img//2
        w_1  = w_img//2
        constant_val = 100
        # image = cv2.resize(image, (608,608))
        # cv2.putText(image, "Put Your Face Here in Box", 
        #             (w_1-constant_val, h_1-constant_val-5),
        #             cv2.FONT_HERSHEY_COMPLEX, 0.5, (255,0,0), thickness=1)
        # cv2.rectangle(image, 
        #                 (w_1-constant_val, h_1-constant_val), 
        #                 (w_1+constant_val, h_1+constant_val), 
        #                 (255,0,0), thickness=3)
        



        

        # ------- Function for Doorlock --------
        if on_RPi:
            if self.count_FPS % 5 == 0 :
                arrayTherm, suhu = rpi.thermalCam.getThermal()

                # -------- overlay thermal ----------
                y_offset=image.shape[0]-arrayTherm.shape[0]
                x_offset=0

                alpha = 0.5
                output = image[y_offset:y_offset+arrayTherm.shape[0], x_offset:x_offset+arrayTherm.shape[1]] 
                cv2.addWeighted(arrayTherm, alpha, output, 1 - alpha, 0, output)
                image[y_offset:y_offset+arrayTherm.shape[0], x_offset:x_offset+arrayTherm.shape[1]] = output
                
                self.count_FPS = 0
            else:
                y_offset=image.shape[0]-arrayTherm.shape[0]
                x_offset=0
                alpha = 0.5

                output = image[y_offset:y_offset+arrayTherm.shape[0], x_offset:x_offset+arrayTherm.shape[1]] 
                cv2.addWeighted(arrayTherm, alpha, output, 1 - alpha, 0, output)
                image[y_offset:y_offset+arrayTherm.shape[0], x_offset:x_offset+arrayTherm.shape[1]] = output
            
            self.count_FPS+=1
            # rpi.Open_status
            bbox, pred_name = rpi.main_vision()
            if bbox is not None and pred_name.lower() != "unknown":
                self.insert_list(pred_name+' '+'{:.2f}'.format(suhu+7.4)+' C ')
                draw_box_name(bbox, pred_name, image)


        # get image infos
        height, width, channel = image.shape
        step = channel * width
        # create QImage from image
        qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
        # show image in img_label
        self.ui.lbl_video.setPixmap(QPixmap.fromImage(qImg))
        

    def processing_sensors(self):
        if on_RPi:
            rpi.main_input()
        

    #def processing_output(self):
    #    if on_RPi:
    #        rpi.main_output()
        

    def showTime(self):
        str_time = str(datetime.datetime.now().strftime("%H:%M"))
        self.ui.lbl_jam.setText("{}".format(str_time))
        hari=str(datetime.datetime.now().strftime("%A")) 
        tanggal=str(datetime.datetime.now().strftime("%d")) 
        idx_bulan=int(datetime.datetime.now().strftime("%m")) 
        bulan_name = bulan[idx_bulan-1]
        # hari = hari[:3]
        self.ui.lbl_tanggal.setText(f"{hari}, {tanggal} {bulan_name}")
    
    def insert_list(self,nama):
        time_masuk = "%s" % (str(datetime.datetime.now().strftime("%H:%M:%S"))) #:%S
        self.ui.lbl_name_recog.setText("{} @ {}".format(nama, time_masuk) )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    # threadThermal = threading.Thread(target=MainWindow.visionThermal, args=image)
    # threadThermal.start()
    if on_RPi:
        window.showFullScreen()
    sys.exit(app.exec_())
