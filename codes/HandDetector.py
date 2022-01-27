# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 10:11:40 2021

@author: memek
"""

import cv2
import numpy as np
import mediapipe as mp

# Static variables
mpHands      = mp.solutions.hands
mpDraw       = mp.solutions.drawing_utils
mpConnType   = mpHands.HAND_CONNECTIONS

# Constants
FINGER_POSITION_UP   = 1
FINGER_POSITION_DOWN = 0
ALL_FINGERS_UP       = 5
ALL_FINGERS_DOWN     = 0
THUMB_TIP_ID         = 0
PINKY_TIP_ID         = 4
AXIS_HORIZONTAL      = 1
AXIS_VERTICAL        = 2
FINGER_TIP_IDS       = [4, 8, 12, 16, 20]

class HandDetector():
    
    HAND_DIRECTION_LEFT       = "Left"
    HAND_DIRECTION_RIGHT      = "Right"
    HAND_DIRECTION_NONE       = "None"
    HAND_POSITION_OPEN        = "Open"
    HAND_POSITION_CLOSE       = "Close"
    HAND_POSITION_THUMB_UP    = "ThumbUp"
    HAND_POSITION_THUMB_DOWN  = "ThumbDown"
    HAND_POSITION_VICTORY     = "Victory"    
    HAND_POSITION_NO_HAND     = "NoHand"
    HAND_POSITION_IGNORE      = "Ignore"
        
    def __init__(self, mode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, trackCon=0.5):        
        self.hands = mpHands.Hands(mode, maxHands, modelComplexity, detectionCon, trackCon)        
        self.handDirection = self.HAND_DIRECTION_NONE     
        
    def detectHands(self, img, draw=True):
        img.flags.writeable = False      
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        img.flags.writeable = True        
    
        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:                
                mpDraw.draw_landmarks(img, hand_landmarks, mpConnType)
        
        #find landMarks
        self.findLandMarks(img)
        
        return img
    
    def findLandMarks(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bbox = []
        self.landmarks_list = []
        self.handDirection = self.HAND_DIRECTION_NONE
        if self.results.multi_hand_landmarks:
            if self.results.multi_handedness:
                # label gives if hand is left or right
                label = self.results.multi_handedness[handNo].classification[0].label
                # account for inversion in webcams
                if label == self.HAND_DIRECTION_LEFT:
                    self.handDirection = self.HAND_DIRECTION_RIGHT
                elif label == self.HAND_DIRECTION_RIGHT:
                    self.handDirection = self.HAND_DIRECTION_LEFT
                
            myHand = self.results.multi_hand_landmarks[handNo]
            
            for id, landmark in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                xList.append(cx)
                yList.append(cy)
                
                self.landmarks_list.append([id, cx, cy, label])        
                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                bbox = xmin, ymin, xmax, ymax
                
                # draw fingers
                if draw:
                    cv2.circle(img, (cx, cy), 3, (255, 0, 255), cv2.FILLED)
    
            if draw:
                cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),(bbox[2] + 20, bbox[3] + 20), (0, 255, 0), 2)
    
        return self.landmarks_list, bbox
    
    def getFingersUp(self):
        fingers = []
        # Thumb
        if self.handDirection == self.HAND_DIRECTION_RIGHT  and self.getFingerHorizontalPosition(FINGER_TIP_IDS[THUMB_TIP_ID]) > self.getFingerHorizontalPosition(FINGER_TIP_IDS[THUMB_TIP_ID]-1):  #Right Thumb    
            fingers.append(FINGER_POSITION_UP)
        elif self.handDirection == self.HAND_DIRECTION_LEFT and self.getFingerHorizontalPosition(FINGER_TIP_IDS[THUMB_TIP_ID]) < self.getFingerHorizontalPosition(FINGER_TIP_IDS[THUMB_TIP_ID]-1):  #Left Thumb    
            fingers.append(FINGER_POSITION_UP)
        else:
            fingers.append(FINGER_POSITION_DOWN)
                   
        # Other Fingers
        for id in range(1, 5):
            if self.getFingerVerticalPosition(FINGER_TIP_IDS[id]) < self.getFingerVerticalPosition(FINGER_TIP_IDS[id] - 2):
                fingers.append(FINGER_POSITION_UP)
            else:
                fingers.append(FINGER_POSITION_DOWN)
                    
        return fingers
    
    def isVolumePosition(self):    
        if self.handDirection == self.HAND_DIRECTION_LEFT:
            # Is hand vertical
            if self.getFingerHorizontalPosition(FINGER_TIP_IDS[THUMB_TIP_ID]-2) < self.getFingerHorizontalPosition(FINGER_TIP_IDS[PINKY_TIP_ID] - 2):
                return False
            
            for id in range(1, 5):
                if self.getFingerHorizontalPosition(FINGER_TIP_IDS[id]) < self.getFingerHorizontalPosition(FINGER_TIP_IDS[id] - 2):
                    return False
        else:
             # Is hand vertical
            if self.getFingerHorizontalPosition(FINGER_TIP_IDS[THUMB_TIP_ID]-2) > self.getFingerHorizontalPosition(FINGER_TIP_IDS[PINKY_TIP_ID] - 2):
                return False
            
            for id in range(1, 5):
                if self.getFingerHorizontalPosition(FINGER_TIP_IDS[id]) > self.getFingerHorizontalPosition(FINGER_TIP_IDS[id] - 2):
                    return False         
                    
        return True
        
    def getFingerHorizontalPosition(self, finderId):        
        try:
            return self.landmarks_list[finderId][AXIS_HORIZONTAL]
        except (IndexError, ValueError):
            return FINGER_POSITION_DOWN
    
    def getFingerVerticalPosition(self, finderId):        
        try:
            return self.landmarks_list[finderId][AXIS_VERTICAL]
        except (IndexError, ValueError):
            return FINGER_POSITION_DOWN
        
    def getHandPosition(self):
        upFingers      = self.getFingersUp()
        sumOfUpFingers = np.sum(upFingers)
        
        try:
            if self.handDirection == self.HAND_DIRECTION_NONE:
                return self.HAND_POSITION_NO_HAND     
            elif self.isVolumePosition():
                if self.getFingerVerticalPosition(FINGER_TIP_IDS[THUMB_TIP_ID]) > self.getFingerVerticalPosition(FINGER_TIP_IDS[THUMB_TIP_ID] - 1):
                    return self.HAND_POSITION_THUMB_DOWN
                else:
                    return self.HAND_POSITION_THUMB_UP
            elif sumOfUpFingers == 2 and upFingers[1] == FINGER_POSITION_UP and upFingers[2] == FINGER_POSITION_UP:
                return self.HAND_POSITION_VICTORY
            elif sumOfUpFingers == ALL_FINGERS_UP:
                return self.HAND_POSITION_OPEN
            elif sumOfUpFingers == ALL_FINGERS_DOWN:
                return self.HAND_POSITION_CLOSE
            else:
                return self.HAND_POSITION_IGNORE
        except (IndexError, ValueError):
            return self.HAND_POSITION_IGNORE
        

# For testing....
if False:
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)   
    detector = HandDetector(detectionCon=0.7)
    while True:
        success, img = cap.read()
        if success:
            img = detector.detectHands(img)
        
            print(detector.getHandPosition())
            print('---------------------------------')
            cv2.imshow("Img", cv2.flip(img, 1))
            cv2.waitKey(1)    