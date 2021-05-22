import sys
import numpy as np
import pyzbar.pyzbar as pyzbar
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
import sqlite3
import cv2
font = cv2.FONT_HERSHEY_PLAIN

from ui_main_window import *

class MainWindow(QWidget):
    # class constructor
    def __init__(self):
        # call QWidget constructor
        global sayac
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        conn=sqlite3.connect("data.db")
        cursor=conn.cursor()
        conn.commit()
        # create a timer
        self.timer = QTimer()
        # set timer timeout callback function
        self.timer.timeout.connect(self.viewCam)
        self.ui.image_label.setPixmap(QPixmap("webcam.png"))
        # set control_bt callback clicked  function
        self.ui.yklm_btn.clicked.connect(self.controlTimer)
        self.setStyleSheet("background-color: rgb(111, 186, 255);")
        self.ui.cikis_bt.setStyleSheet("background-color:black;color:white")
        self.ui.yoklama_bt.setStyleSheet("background-color:black;color:white")
        self.ui.qrcode_bt.setStyleSheet("background-color:black;color:white")
        self.ui.control_bt.setStyleSheet("background-color:black;color:white")
        self.ui.yklm_btn.setStyleSheet("background-color:black;color:white")
        self.ui.sql_tbl.setVisible(False)
        self.ui.yoklama_bt.clicked.connect(self.yoklamaGetir)
        self.ui.cikis_bt.clicked.connect(self.close)
        self.ui.groupBox_2.setStyleSheet("background-color: rgb(146, 255, 206);")
        self.ui.groupBox.setEnabled(False)
        self.ui.groupBox_2.setEnabled(False)
        self.ui.control_bt.clicked.connect(self.kontrol)
        
    # view camera
    def kontrol(self):
        self.ui.groupBox_2.setEnabled(True)
    def viewCam(self):
        self.setStyleSheet("background-color: red;")
        conn=sqlite3.connect("data.db")
        cursor=conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS isimler(numara,adsoyad,Hafta1,Hafta2,Hafta3,Hafta4,Hafta5,Hafta6,Hafta7,Hafta8,Hafta9,Hafta10,Hafta11,Hafta12,Hafta13,Hafta14)")
        #cursor.execute('INSERT INTO isimler VALUES (?)',(str(obj.data),))
        conn.commit()
    
        a=""
        #liste=list()
        #detector = cv2.QRCodeDetector()
        # read image in BGR format
        
        ret, image = self.cap.read()
        #data,bbox,_=detector.detectAndDecode(image)
        #if(data):     
        #    print(data)
        decodedObjects = pyzbar.decode(image)
        hft=(self.ui.cmb_hafta.currentText())
        for obj in decodedObjects:

            cursor.execute("UPDATE isimler SET "+hft+"= 'false' WHERE "+hft+" IS NULL")
            conn.commit()
            self.setStyleSheet("background-color: green;")
            #a=str(obj.data)[2:-1]
            a=(str(obj.data)[2:-1]).split('-')
            cv2.putText(image, a[0], (50, 50), font, 2,(0, 0, 255), 3)
            cv2.putText(image, a[1], (50, 80), font, 2,(0, 0, 255), 3)
            #print(obj.data)
            cursor.execute("INSERT INTO isimler(numara,adsoyad) VALUES (?,?)",(a[0],a[1],))
            conn.commit()
            #cursor.execute('INSERT INTO isimler VALUES (?)',(str(obj.data),))
            cursor.execute("UPDATE isimler SET "+hft+"= 'true' WHERE numara = ?",(str(a[0]),))
            conn.commit()
            cursor.execute('DELETE FROM isimler WHERE rowid NOT IN (SELECT min(rowid) FROM isimler GROUP BY numara)')
            conn.commit()
            #if a not in liste:
                #liste.append(a)
                #a=""
                #print(liste)
                #print(len(liste))
        
        # convert image to RGB format
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # get image infos
        height, width, channel = image.shape
        step = channel * width
        # create QImage from image
        qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
        # show image in img_label
        self.ui.image_label.setPixmap(QPixmap.fromImage(qImg))

    # start/stop timer
    def controlTimer(self):
        
        self.ui.cikis_bt.setVisible(False)
        self.ui.qrcode_bt.setVisible(False)
        self.ui.yoklama_bt.setVisible(False)
        self.ui.control_bt.setVisible(False)
        # if timer is stopped
        if not self.timer.isActive():
            # create video capture
            self.cap = cv2.VideoCapture(0)
            # start timer
            self.timer.start(20)
            # update control_bt text
            self.ui.yklm_btn.setText("Yoklama Bitir")
            
        # if timer is started
        else:
            self.ui.image_label.setPixmap(QPixmap("webcam.png"))
            self.setStyleSheet("background-color: rgb(111, 186, 255);")
            self.ui.cikis_bt.setVisible(True)
            self.ui.qrcode_bt.setVisible(True)
            self.ui.yoklama_bt.setVisible(True)
            self.ui.control_bt.setVisible(True)
            # stop timer
            self.timer.stop()
            # release video capture
            self.cap.release()
            # update control_bt text
            self.ui.yklm_btn.setText("Yoklama Başlat")

    def yoklamaGetir(self):  
        while (self.ui.sql_tbl.rowCount() > 0):
            self.ui.sql_tbl.removeRow(0)
        self.ui.sql_tbl.setStyleSheet("background-color:white;")
        self.ui.sql_tbl.setVisible(True)
        conn=sqlite3.connect("data.db")
        cursor=conn.cursor()
        self.ui.sql_tbl.clear()
        self.ui.sql_tbl.setHorizontalHeaderLabels(('Numara','Ad Soyad','Hafta1','Hafta2','Hafta3','Hafta4','Hafta5','Hafta6','Hafta7','Hafta8','Hafta9','Hafta10','Hafta11','Hafta12','Hafta13','Hafta14','Toplam Devamsızlık'))
            
        cursor.execute("SELECT * FROM isimler")
        for satirIndex,satirVeri in enumerate(cursor):
            self.ui.sql_tbl.insertRow(satirIndex)
            devam=0   
            for sutunIndex,sutunVeri in enumerate(satirVeri):    
                self.ui.sql_tbl.setItem(satirIndex,sutunIndex,QtWidgets.QTableWidgetItem(str(sutunVeri)))
                if(self.ui.sql_tbl.item(satirIndex, sutunIndex).text()=="true"):
                    self.ui.sql_tbl.item(satirIndex, sutunIndex).setBackground(QtGui.QColor(0,250,0))
                    devam+=1
                    self.ui.sql_tbl.setItem(satirIndex,16,QtWidgets.QTableWidgetItem(str(devam)))
                elif(self.ui.sql_tbl.item(satirIndex, sutunIndex).text()=="false"):
                    self.ui.sql_tbl.item(satirIndex, sutunIndex).setBackground(QtGui.QColor(250,0,0))
                elif(self.ui.sql_tbl.item(satirIndex, sutunIndex).text()=="None"):
                    self.ui.sql_tbl.setItem(satirIndex,sutunIndex,QtWidgets.QTableWidgetItem(str("-")))
                else:
                    pass
        header = self.ui.sql_tbl.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        for i in range(17):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # create and show mainWindow
    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())
