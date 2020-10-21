print("main2.py")
import sys
import platform
import numpy as np
import pandas as pd
from config import *

# GUI FILE
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent, QTimer)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient, QImage)
from PyQt5.QtWidgets import *

from ui_main2 import Ui_MainWindow

# Raspi Sensors and Actuators
# from ui_functions import *

try:
    import RPi.GPIO as gpio
    on_RPi = True
    kalibrasi_mode = True
    from raspi_function import main_input, main_output, main_vision, thermalCam
    print("work on raspberry pi")
except (ImportError, RuntimeError):
    on_RPi = False
    kalibrasi_mode = False
    logging.error("We are on Development mode")

from utils.vision_helper import draw_box_name

import cv2
import imutils
from imutils.video import VideoStream
from utils.centroidtracker import CentroidTracker
from collections import OrderedDict

import time
import datetime
import copy

# global variabel
bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 
         'Jun', 'Jul', 'Aug', 'Okt', 'Sep',
         'Nov', 'Dec']

imageThermal = np.zeros((400,300,3))
suhu = '0 C'
ct = CentroidTracker(maxDisappeared=16)
getData = False


futureObj = set()
myPeople = OrderedDict()

obj_center = {}
obj_bbox = {}
dict_suhu = {}

main_log = setup_logger(name = 'main_logs', log_file = 'main_logs', 
                        folder_name='main_logs', level = logging.DEBUG,
                        removePeriodically=True, to_console=True,
                        interval=10, backupCount=5, when='s')

thermal_log = setup_logger(name = 'thermal', log_file = 'thermal_logs', 
                        folder_name='thermal_logs', level = logging.DEBUG,
                        removePeriodically=True, to_console=True,
                        interval=1, backupCount=10, when='m')


class MainWindow(QMainWindow):
    pixel_list = []

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        path_cam = 'rtsp://admin:aiti12345@11.11.11.81:554/Streaming/channels/101'
        if on_RPi:
            path_cam1 = 'http://11.11.11.12:8555' 
            self.cap = VideoStream(src=path_cam1).start()
        else:
            path_cam1 = 0
            self.cap = VideoStream(src=path_cam1, usePiCamera=False).start()

        self.detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        time.sleep(2.0)

        # vision opetarion
        self.streamCamera = QTimer()
        self.streamCamera.start(20)
        self.streamCamera.timeout.connect(self.stream_camera_on)

        # input operation
        self.streamSensors = QTimer()
        self.streamSensors.start(10)
        self.streamSensors.timeout.connect(self.processing_sensors)

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


    def overlayImage(self, basicImage, transparantImage, alpha=0.4):

        y_offset=basicImage.shape[0]-transparantImage.shape[0]
        y_offset_2 = basicImage.shape[0]
        
        x_offset=0
        x_offset_2 = x_offset+transparantImage.shape[1]
        offset = 10
        
        output = basicImage[y_offset-offset:y_offset_2-offset, x_offset+offset:x_offset_2+offset] 
        
        output = cv2.addWeighted(src1 = transparantImage, 
                                 alpha = alpha, 
                                 src2 = output, 
                                 beta = 1 - alpha, 
                                 gamma = 0, 
                                 dst = output, 
                                 dtype = cv2.CV_32F,
                                 )
        
        basicImage[y_offset-offset:y_offset_2-offset, x_offset+offset:x_offset_2+offset] = output

        basicImage = cv2.rectangle(img = basicImage, 
                                   pt1 = (x_offset+offset, y_offset-offset),
                                   pt2 = (x_offset_2+offset, y_offset_2-offset), 
                                   color = (255,255,255),
                                   thickness=1,
                                   )

        return basicImage
        
    def stream_camera_on(self):
        global imageThermal, suhu, ct, myPeople, getData, futureObj
        global dict_suhu, obj_bbox, obj_center, koko

        # read image in BGR format
        first_tick = time.time()

        image = self.cap.read()
        start_time = time.time()
        image = cv2.resize(image, (400,300))

        # image = imutils.resize(image, width=400) # for face

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # for face
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        rects = self.detector.detectMultiScale(image = gray, 
                                               scaleFactor=1.1, 
                                               minNeighbors=5, 
                                               minSize=(30, 30),
                                               maxSize=(150,150),
                                               flags=cv2.CASCADE_SCALE_IMAGE,
                                               )

        boxes = [[x, y, x + w, y + h] for (x, y, w, h) in rects]
        h_img, w_img, ch = image.shape
        
        obj_center, obj_bbox = ct.update(boxes)
        # main_log.info(koko)
        # ------- Function for Doorlock --------
        if on_RPi:
            list_bboxes, dict_name, isNewPeople = main_vision()

            if list_bboxes is not None:
                obj_center, obj_bbox = ct.update(list_bboxes)


            if self.count_FPS % 10 == 0 or self.isThereNewObject(myPeople, obj_bbox) or isNewPeople:
                dict_suhu = {}
                my_obj = copy.deepcopy(obj_bbox)
                imageThermal, thermalData, dict_suhu, MainWindow.pixel_list = thermalCam.getThermal(image, my_obj)
                image = self.overlayImage(image, imageThermal, alpha=0.7)
                current_pixel = pd.DataFrame(data=MainWindow.pixel_list)
                thermal_log.info(current_pixel)

            else:
                image = self.overlayImage(image, imageThermal, alpha=0.7)

            if dict_suhu is None:
                dict_suhu = {}
            if dict_name is None:
                dict_name = {}

            self.count_FPS+=1

            # print('\n>>>>>>>> before\n [main2.py onRpi]',
            #         '\n*dict_name: ', dict_name, 
            #         '\n*obj_bbox : ', id(obj_bbox), obj_bbox, 
            #         '\n*dict_suhu: ', dict_suhu,
            #         '\nmyPeople'    , myPeople,
            #         '\n>>>>>>>>')

            if len(obj_bbox.keys()) > 0:
                #obj_center, obj_bbox = ct.update(list_bboxes) # ---- TRACKING update
                # print('\n>>>>>>>>\n main2.py list_bboxes:', list_bboxes, obj_bbox, '\n>>>>>>>>')
                for (objectID, single_bbox) in obj_bbox.items():

                    id_name = int(np.array(single_bbox).sum())
                    if len(myPeople) == 0:
                        myPeople[objectID] = ['no name', 'wait', (0,0)]

                    if id_name in list(dict_name.keys()):
                        # print('yuhu')
                        single_name = dict_name[id_name]
                        myPeople[objectID] = [single_name, 'wait', (0,0)]
                        # print(dict_suhu, dict_name)
                        self.insert_list(single_name)

                    
                    if len(dict_suhu) !=0 :
                        if objectID not in list(myPeople.keys()):
                            myPeople[objectID] = ['no data', 'wait', (0,0)]
                        if objectID not in list(dict_suhu.keys()):
                            myPeople[objectID] = ['no data', 'wait', (0,0)]
                        else:
                            coordinate = dict_suhu[objectID]['coordinate']
                            suhu_max= dict_suhu[objectID]['max']
                            myPeople[objectID][1] = suhu_max 
                            myPeople[objectID][2] = coordinate

            # print('\n<<<<<<<< after\n [main2.py onRpi]',
            #         '\n*dict_name:' , dict_name, 
            #         '\n*obj_bbox: ' , id(obj_bbox), obj_bbox, 
            #         '\n*dict_suhu: ', dict_suhu,
            #         '\nmyPeople'    , myPeople,
            #         '\n>>>>>>>>')

        else:
            pred_name='face'
            suhu = 36.8
        
        # ---- TRACKING
        if (self.count_FPS % 1 == 0) or start_time-time.time() < 3:
            obj_center, obj_bbox = ct.update(boxes)
            self.deleteExpireObject(myPeople, obj_center)
            # print('# Global Tracking', obj_center)


        # print("HEYY", myPeople, obj_center, boxes)
        # draw bbox
        for (objectID, centroid), single_bbox in zip(obj_center.items(), obj_bbox.values()):
            # print("test", myPeople, objectID)

            if objectID in myPeople.keys():
                # print("in 1 : ada kotak dan nama")
                draw_box_name(bbox = single_bbox, 
                              name = myPeople[objectID][0], 
                              frame = image, 
                              suhu = myPeople[objectID][1])

            elif len(boxes) != 0:
                # print("in 2 : ada kotak, nama tidak ada")
                draw_box_name(bbox = single_bbox, 
                              name = '_', 
                              frame = image, 
                              suhu=suhu)
            else:
                # print("in 3 : ", len(boxes))
                continue


        FPS =  1/ (time.time()-start_time)     
        cv2.putText(image, "FPS: {:.2f}".format(FPS), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 2)
        if self.count_FPS == 70:
            self.count_FPS = 0

        if kalibrasi_mode:
            image = cv2.resize(image, (400,300))
            mean_pix = np.mean(MainWindow.pixel_list)
            for ix,x in enumerate(range(0, 400, 400//8)):
                for iy, y in enumerate(range(0, 320, 320//8)):
                    
                    if (ix == 4 and iy == 4):
                        thickness = 2
                    else:
                        thickness = 1
                        
                    # line horizontal
                    cv2.line(img = image,
                            # y, x
                            pt1 = (x, 0), 
                            pt2 = (x, 300), 
                            color=(0,255,255),
                            thickness=thickness)
                    
                    # line vertikal
                    cv2.line(img = image,
                            pt1 = (0,  y), 
                            pt2 = (400,y), 
                            color=(0,255,255),
                            thickness=thickness)

                    if (MainWindow.pixel_list[ix][iy] > mean_pix+1):
                        thickness_text = 2
                    else: 
                        thickness_text = 1
                        
                    color_text = (0,255,255)
                    cv2.putText(img = image,
                                text = str(MainWindow.pixel_list[ix][iy]),
                                org = (x+5,y+25),
                                fontFace = cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale = 0.45, 
                                color = color_text,
                                thickness=thickness_text
                                )

        # get image infos
        height, width, channel = image.shape
        step = channel * width
        # create QImage from image
        qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
        # show image in img_label
        self.ui.lbl_video.setPixmap(QPixmap.fromImage(qImg))

    def processing_sensors(self):
        if on_RPi:
            main_input()


    def getNewObject(self, myObj, trackingObj):
        futureObject = set(trackingObj.keys()).difference(myObj.keys())
        for i in futureObject:
            myObj[i] = ['ga kenal', 'ERR']

        return futureObject, myObj

    def isThereNewObject(self, myObj, trackingObj):
        futureObject = set(trackingObj.keys()).difference(myObj.keys())
        if len(futureObject) > 0:
            return True
        else:
            return False

    def deleteExpireObject(self, myObj, trackingObj):
        diff = set(myObj.keys()).difference(trackingObj.keys())
        for i in diff:
            del myObj[i]

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
        self.ui.lbl_name_recog.setText("{} at {}".format(nama, time_masuk))


GLOBAL_STATE = 0 
have_pressed = -1

class UIFunctions(MainWindow):

    def maximize_restore(self):
        global GLOBAL_STATE
        status = GLOBAL_STATE

        # if not maximazed
        if status == 0:
            self.showMaximized()
            
            GLOBAL_STATE =1
            # self.ui.horizontalLayout_3.setContentMargins(0,0,0,0)
            self.ui.main.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(32, 74, 135, 255), stop:0.597015 rgba(48, 140, 198, 255));\nborder-radius:10px;")
            self.ui.btn_max.setToolTip("Restore")

        else:
            GLOBAL_STATE=0
            self.showNormal()
            self.resize(self.width()+1, self.height()+1)
            # self.ui.horizontalLayout_3.setContentsMargins(10,10,10,10)
            self.ui.main.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(32, 74, 135, 255), stop:0.597015 rgba(48, 140, 198, 255));\nborder-radius:20px;")
            self.ui.btn_min.setToolTip("Maximize")
            


    def uiDefinitions(self):
        # Remove Title Bar
        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint)

        self.setWindowFlag(QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.hide()
        # SET DROPSHADOW WINDOW
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(5)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(10)
        self.shadow.setColor(QColor(0, 0, 0, 10))

        # APPLY DROPSHADOW TO FRAME
        self.ui.main.setGraphicsEffect(self.shadow)


        # my function
        self.ui.btn_call.clicked.connect(lambda: UIFunctions.pressed_Call(self))

    ## BUTTONS FUCTION
    def pressed_Call(self):
        global have_pressed
        have_pressed *= -1
        if have_pressed > 0:
            self.ui.btn_call.setStyleSheet("border-image: url(:/icons/icon_set/btn_end_call.png);")
            self.ui.lbl_icon_lock.setStyleSheet("border-image: url(:/icons/icon_set/unlock.png);")
        else:
            self.ui.btn_call.setStyleSheet("border-image: url(:/icons/icon_set/call_btnic_call.png);")
            self.ui.lbl_icon_lock.setStyleSheet("border-image: url(:/icons/icon_set/lock.png);")
        str_time = str(datetime.datetime.now().strftime("%A %d-%m-%Y | %H:%M:%S"))        
        print(str_time)

    def showTime(self):
        str_time = str(datetime.datetime.now().strftime("%d-%m-%Y | %H:%M:%S"))
        self.ui.lbl_title.setText(_translate("MainWindow", "Door Lock | {}".format(str_time)))
        
    ## RETURN STATUS IF WINDOWS IS MAXIMIZE OR RESTAURED
    def returnStatus():
        return GLOBAL_STATE


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    if on_RPi:
        window.showFullScreen()
    sys.exit(app.exec_())
