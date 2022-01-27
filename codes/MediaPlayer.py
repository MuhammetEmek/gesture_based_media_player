# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 11:26:59 2021

@author: memek
"""

import cv2
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGroupBox, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSlider, QStyle, QSizePolicy, QFileDialog, QMessageBox
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette, QFont
from PyQt5.QtCore import Qt, QUrl
from PyQt5 import QtCore, QtGui, QtWidgets
from HandDetector import HandDetector

# Constants
CAP_FRAME_HEIGHT    = 400
CAP_FRAME_WIDTH     = 400
MIN_VOLUME_VALUE    = 0
MAX_VOLUME_VALUE    = 100

GESTURE_ACTION_PREFIX      = "Gesture Action : "
GESTURE_ACTION_PLAY        = "Play"
GESTURE_ACTION_STOP        = "Stop"
GESTURE_ACTION_VOLUME_UP   = "Volume Up"
GESTURE_ACTION_VOLUME_DOWN = "Volume Down"
GESTURE_ACTION_VOLUME_MUTE = "Volume Mute"
GESTURE_ACTION_VOLUME_MAX  = "Volume Maximum !"
GESTURE_ACTION_IGNORE      = "Ignore"
GESTURE_ACTION_NO_HAND     = "No Hands !!"
FILE_SEPERATOR             = "/"

class MediaPlayer(QWidget):
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gesture Based Media Player")
        self.setGeometry(350, 100, 1300, 500)
        self.setWindowIcon(QIcon('player.png'))

        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)
        self.initUi()
        self.show()        


    def initUi(self):
        #create media player object
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        
        #create HandDetector object
        self.handDetector = HandDetector(detectionCon=0.7)

        #create videoWidget object
        videoWidget = QVideoWidget()        

        #create open button
        openBtn = QPushButton('Open Media')
        openBtn.clicked.connect(self.openFile)

        #create camera for capturing frames
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAP_FRAME_WIDTH)
        
        #create timer for period of capturing frames 
        self.timer = QtCore.QTimer(self, interval=2)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start()
       
        #create image_label for showing captured image
        self.cameraImage = QtWidgets.QLabel(self)
        self.cameraImage.setText("")
        self.cameraImage.setScaledContents(True)
        self.cameraImage.setObjectName("cameraImage")
                    
        #create button for playing
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.onPlayButonClick)

        #create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0,0)
        self.slider.sliderMoved.connect(self.setPosition)
        
        #create label for Volume
        volumeLabel = QLabel()
        volumeLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        volumeLabel.setText("Volume")
        volumeLabel.setStyleSheet("color:white")
        
        #create slider for Volume
        self.volumeSlider = QSlider(Qt.Horizontal)        
        self.volumeSlider.valueChanged[int].connect(self.changeVolume)    
        self.volumeSlider.setRange(MIN_VOLUME_VALUE, MAX_VOLUME_VALUE)
        self.volumeSlider.setValue(MAX_VOLUME_VALUE)
        self.volumeSlider.setGeometry(10, 450, 200, 35)

        #create label for errors
        self.mediaNameLabel = QLabel()
        self.mediaNameLabel.setFont(QFont('Arial', 20))
        self.mediaNameLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.mediaNameLabel.setText("")
        self.mediaNameLabel.setStyleSheet("color:white")
        
        #create label for Gesture Detection Result
        self.gestureResultLabel = QLabel()
        self.gestureResultLabel.setFont(QFont('Arial', 20))
        self.gestureResultLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.gestureResultLabel.setText("Action")
        self.gestureResultLabel.setStyleSheet("color:white")
        
        #create main layout
        mainLayout = QHBoxLayout()
        
        #create bottomLayout contains buttons and slider
        vbLeftBottomLayout = QHBoxLayout()
        vbLeftBottomLayout.setContentsMargins(0,0,0,0)    

        #set widgets to the hbox layout        
        vbLeftBottomLayout.addWidget(volumeLabel)
        vbLeftBottomLayout.addWidget(self.volumeSlider)        
        
        # create groupbox for gesture detection (camera output)
        cameraGroupBox = QGroupBox()    
                
        #add widgets to the hbox layout
        vbCameraLayout = QVBoxLayout()
        vbCameraLayout.addWidget(self.cameraImage)
        vbCameraLayout.addLayout(vbLeftBottomLayout)
        vbCameraLayout.addWidget(self.gestureResultLabel)
        cameraGroupBox.setLayout(vbCameraLayout)
        
        #create bottomLayout contains buttons and slider
        hbRightBottomLayout = QHBoxLayout()
        hbRightBottomLayout.setContentsMargins(0,0,0,0)

        #add widgets to the hbox layout
        hbRightBottomLayout.addWidget(openBtn)
        hbRightBottomLayout.addWidget(self.playBtn)
        hbRightBottomLayout.addWidget(self.slider)

        # create groupbox for media player
        mediaPlayerGroupBox = QGroupBox()
        
        #create vbox layout for mediaPlayer       
        vbMediaPlayerLayout = QVBoxLayout()
        vbMediaPlayerLayout.addWidget(videoWidget)
        vbMediaPlayerLayout.addLayout(hbRightBottomLayout)
        vbMediaPlayerLayout.addWidget(self.mediaNameLabel)
        mediaPlayerGroupBox.setLayout(vbMediaPlayerLayout)
        
        #add cameraGroupBox to mainLayout
        mainLayout.addWidget(cameraGroupBox)
        
        #add mediaPlayerGroupBox to mainLayout
        mainLayout.addWidget(mediaPlayerGroupBox)

        self.setLayout(mainLayout)
        self.mediaPlayer.setVideoOutput(videoWidget)

        #media player signals
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Quit?',
                                     'Are you sure you want to quit?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if not type(event) == bool:
                event.accept()
            else:
                self.closeApplication()
                
        else:
            if not type(event) == bool:
                event.ignore()       

    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Media")

        if filename != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.playBtn.setEnabled(True)
            self.mediaNameLabel.setText(self.getLocalFileName(filename))            

    def onPlayButonClick(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()
    
    def playMedia(self):
        self.mediaPlayer.play()
            
    def stopMedia(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            
    def changeVolume(self, value):
        self.mediaPlayer.setVolume(value)
        
    def volumeUp(self):
        currentVolume = self.volumeSlider.value()
        currentVolume = currentVolume + 1
        if currentVolume > MAX_VOLUME_VALUE:
            currentVolume = MAX_VOLUME_VALUE
            self.setGestureLabel(GESTURE_ACTION_VOLUME_MAX)
            
        self.volumeSlider.setValue(currentVolume)
        self.changeVolume(currentVolume)
        
    def volumeDown(self):
        currentVolume = self.volumeSlider.value()
        currentVolume = currentVolume - 1
        if currentVolume < MIN_VOLUME_VALUE:
            currentVolume = MIN_VOLUME_VALUE
            self.setGestureLabel(GESTURE_ACTION_VOLUME_MUTE)
            
        self.volumeSlider.setValue(currentVolume)
        self.changeVolume(currentVolume)
        
    def volumeMute(self):        
        self.volumeSlider.setValue(0)
        self.changeVolume(0)

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.slider.setValue(position)

    def durationChanged(self, duration):
        self.slider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)
        
    def setGestureLabel(self, actionText):
        gestureAction = GESTURE_ACTION_PREFIX + actionText
        self.gestureResultLabel.setText(gestureAction)
        
    def detectAndDisplayImage(self, img):        
        if img is not None:
            detectedImg = self.detectHandPosition(img)
            self.displayImage(detectedImg)
        else:
            print("Image is null !")
        
    def detectHandPosition(self, img):
        outImage     = self.handDetector.detectHands(img)
        handPosition = self.handDetector.getHandPosition()        
        
        if handPosition == HandDetector.HAND_POSITION_CLOSE:
            self.setGestureLabel(GESTURE_ACTION_PLAY)
            self.playMedia()
        elif handPosition == HandDetector.HAND_POSITION_OPEN:
            self.stopMedia()
            self.setGestureLabel(GESTURE_ACTION_STOP)
        elif handPosition == HandDetector.HAND_POSITION_THUMB_UP:
            self.setGestureLabel(GESTURE_ACTION_VOLUME_UP)
            self.volumeUp()
        elif handPosition == HandDetector.HAND_POSITION_THUMB_DOWN:
            self.setGestureLabel(GESTURE_ACTION_VOLUME_DOWN)
            self.volumeDown()
        elif handPosition == HandDetector.HAND_POSITION_VICTORY:
            self.setGestureLabel(GESTURE_ACTION_VOLUME_MUTE)
            self.volumeMute()                        
        elif handPosition == HandDetector.HAND_POSITION_NO_HAND:
            self.setGestureLabel(GESTURE_ACTION_NO_HAND)
        elif handPosition == HandDetector.HAND_POSITION_IGNORE:          
            self.setGestureLabel(GESTURE_ACTION_IGNORE)     
                
        return outImage        
        
    def displayImage(self, img):
        qformat = QtGui.QImage.Format_Indexed8
        if len(img.shape)==3 :
            if img.shape[2]==4:
                qformat = QtGui.QImage.Format_RGBA8888
            else:
                qformat = QtGui.QImage.Format_RGB888
                
        outImage = QtGui.QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        outImage = outImage.rgbSwapped()       
        self.cameraImage.setPixmap(QtGui.QPixmap.fromImage(outImage))   
            
    @QtCore.pyqtSlot()
    def updateFrame(self):
        success, image = self.cap.read()
        if success:
            image = cv2.flip(image, 1)
            self.detectAndDisplayImage(image)
            
    def getLocalFileName(self, fileName):    
        print(fileName)
        seperatorLastIndex = fileName.rfind(FILE_SEPERATOR)
        print(seperatorLastIndex)
        if seperatorLastIndex > 0:
            return fileName[seperatorLastIndex + 1:]
        else:
            return ''
        
    def closeApplication(self):   
        self.stopMedia()
        self.timer.stop()
        self.cap.release()        
        sys.exit()
        
        
app  = QApplication(sys.argv)
playerWindow = MediaPlayer()
sys.exit(app.exec_())