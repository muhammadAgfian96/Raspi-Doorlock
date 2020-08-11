# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test_2.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 600)
        MainWindow.setMinimumSize(QtCore.QSize(1024, 600))
        MainWindow.setMaximumSize(QtCore.QSize(1024, 600))
        MainWindow.setStyleSheet("background-color: rgb(46, 52, 54);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.ic_vid = QtWidgets.QLabel(self.centralwidget)
        self.ic_vid.setGeometry(QtCore.QRect(220, 110, 601, 341))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ic_vid.sizePolicy().hasHeightForWidth())
        self.ic_vid.setSizePolicy(sizePolicy)
        self.ic_vid.setStyleSheet("border-radius:20px;")
        self.ic_vid.setText("")
        self.ic_vid.setPixmap(QtGui.QPixmap(":/img2/bg_vid.png"))
        self.ic_vid.setScaledContents(True)
        self.ic_vid.setObjectName("ic_vid")
        self.ic_title = QtWidgets.QLabel(self.centralwidget)
        self.ic_title.setGeometry(QtCore.QRect(350, 30, 351, 41))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ic_title.sizePolicy().hasHeightForWidth())
        self.ic_title.setSizePolicy(sizePolicy)
        self.ic_title.setText("")
        self.ic_title.setPixmap(QtGui.QPixmap(":/img2/aiti2.png"))
        self.ic_title.setScaledContents(True)
        self.ic_title.setObjectName("ic_title")
        self.txt_welcom = QtWidgets.QLabel(self.centralwidget)
        self.txt_welcom.setGeometry(QtCore.QRect(280, 470, 481, 31))
        font = QtGui.QFont()
        font.setFamily("Noto Sans CJK KR")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.txt_welcom.setFont(font)
        self.txt_welcom.setTextFormat(QtCore.Qt.RichText)
        self.txt_welcom.setAlignment(QtCore.Qt.AlignCenter)
        self.txt_welcom.setWordWrap(True)
        self.txt_welcom.setObjectName("txt_welcom")
        self.mail = QtWidgets.QLabel(self.centralwidget)
        self.mail.setGeometry(QtCore.QRect(490, 520, 71, 61))
        self.mail.setText("")
        self.mail.setPixmap(QtGui.QPixmap(":/img2/call.png"))
        self.mail.setScaledContents(True)
        self.mail.setObjectName("mail")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.txt_welcom.setText(_translate("MainWindow", "Halo Selamat Datang di AITI DIGITAL INDONESIA"))

import test_2_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

