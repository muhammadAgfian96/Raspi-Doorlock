import sys
import platform

try:
    import RPi.GPIO as gpio
    on_RPi = True
except (ImportError, RuntimeError):
    on_RPi = False

# GUI FILE
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent, QTimer)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient, QImage)
from PyQt5.QtWidgets import *
from ui_main2 import Ui_MainWindow

# Raspi Sensors and Actuators
from ui_functions import *


import cv2
import time
import datetime
bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 
         'Jun', 'Jul', 'Aug', 'Okt', 'Sep',
         'Nov', 'Dec']


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        path_cam = 'rtsp://admin:aiti12345@11.11.11.81:554/Streaming/channels/101'
        path_cam1 = 'http://11.11.11.12:8555' 
        self.cap = cv2.VideoCapture(0)
        time.sleep(1)
        # create a timer
        self.streamTimer = QTimer()
        self.streamTimer.start(20)
        # set timer timeout callback function
        self.streamTimer.timeout.connect(self.stream_camera_on)

        self.showtimeTimer = QTimer()
        self.showtimeTimer.setInterval(1000)
        self.showtimeTimer.timeout.connect(self.showTime)
        self.showtimeTimer.start()

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
        ########################################################################
        self.show()

    ## APP EVENTS
    ########################################################################
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    
    def stream_camera_on(self):
        # read image in BGR format
        ret, image = self.cap.read()
        # convert image to RGB format
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h_img, w_img, ch =image.shape
        h_1 = h_img//2
        w_1  = w_img//2
        # print(h_1, w_1)
        constant_val = 100
        # image = cv2.resize(image, (608,608))
        cv2.putText(image, "Put Your Face Here in Box", 
                    (w_1-constant_val, h_1-constant_val-5),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255,0,0), thickness=1)
        cv2.rectangle(image, 
                        (w_1-constant_val, h_1-constant_val), 
                        (w_1+constant_val, h_1+constant_val), 
                        (255,0,0), thickness=3)
        # get image infos
        height, width, channel = image.shape
        step = channel * width
        # create QImage from image
        qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
        # show image in img_label
        self.ui.lbl_video.setPixmap(QPixmap.fromImage(qImg))
        
        # ------- Function for Doorlock --------
        if on_RPi:
            ui_iot.Open_status
            bbox, pred_name = ui_iot.main()
            if bbox is not None:
                self.insert_list(pred_name)


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
        self.ui.lbl_name.setText("{} masuk di jam {}".format(nama, time_masuk) )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    if on_RPi:
        window.showFullScreen()
    sys.exit(app.exec_())