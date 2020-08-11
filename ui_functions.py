from main import *
import datetime
import cv2

GLOBAL_STATE = 0 

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

        # MAXIMIZE / RESTORE
        self.ui.btn_max.clicked.connect(lambda: UIFunctions.maximize_restore(self))

        # MINIMIZE
        self.ui.btn_min.clicked.connect(lambda: self.showMinimized())

        # CLOSE
        self.ui.btn_exit.clicked.connect(lambda: self.close())

        ## ==> CREATE SIZE GRIP TO RESIZE WINDOW
        self.sizegrip = QSizeGrip(self.ui.frame_grip)
        self.sizegrip.setStyleSheet("QSizeGrip { width: 10px; height: 10px; margin: 5px } QSizeGrip:hover { background-color: rgb(150, 200, 202, 255) }")
        self.sizegrip.setToolTip("Resize Window")

        # my function
        self.ui.btn_call.clicked.connect(lambda: UIFunctions.pressed_Call(self))

    ## BUTTONS FUCTION
    def pressed_Call(self):
        print("pressed Call")

    def showTime(self):
        str_time = str(datetime.datetime.now().strftime("%d-%m-%Y | %H:%M:%S"))
        self.ui.lbl_title.setText(_translate("MainWindow", "Door Lock | {}".format(str_time)))
        
    ## RETURN STATUS IF WINDOWS IS MAXIMIZE OR RESTAURED
    def returnStatus():
        return GLOBAL_STATE