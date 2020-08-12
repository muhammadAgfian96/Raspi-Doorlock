import sys
import platform
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent, QTimer)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient, QImage)
from PyQt5.QtWidgets import *

# GUI FILE
from ui_main import Ui_MainWindow

# IMPORT FUNCTIONS
from ui_functions import *
import ui_iot

import cv2
import time
import datetime


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        path_cam = 'http://11.11.11.12:8555'
        self.cap = cv2.VideoCapture(path_cam)
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
        self.ui.title_bar.mouseMoveEvent = moveWindow

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
        image = cv2.resize(image, (720,386))

        # get image infos
        height, width, channel = image.shape
        step = channel * width
        # create QImage from image
        qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
        # show image in img_label
        self.ui.label_img_stream.setPixmap(QPixmap.fromImage(qImg))
        
        ui_iot.Open_status
        bbox, pred_name = ui_iot.main()
        if bbox is not None:
            self.insert_list(pred_name)


    def showTime(self):
        str_time = str(datetime.datetime.now().strftime("%d-%m-%Y - %H:%M:%S"))
        self.ui.lbl_title.setText("Door Lock | {}".format(str_time))
    
    def insert_list(self,nama):
        time_masuk = "%s" % (str(datetime.datetime.now().strftime("%H:%M:%S"))) #:%S
        self.ui.lbl_name.setText("{} masuk di jam {}".format(nama, time_masuk) )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    sys.exit(app.exec_())