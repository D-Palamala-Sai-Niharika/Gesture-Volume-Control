import cv2
import mediapipe as mp
import time
import numpy as np
import math
import HandTrackingModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

######################
wCap, hCap = 640, 480
######################

cap = cv2.VideoCapture(0)
cap.set(3, wCap)
cap.set(4, hCap)

pTime = 0
cTime = 0

detector = htm.handDetector(detectionCon=0.7, maxHands=1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
#volume.GetVolumeRange()
#print(volume.GetVolumeRange())
volRange = volume.GetVolumeRange()
#print(volRange)
#volume.SetMasterVolumeLevel(-20.0, None)  #26
#volume.SetMasterVolumeLevel(-5.0, None)   #72
#volume.SetMasterVolumeLevel(0.0, None)    #100
minVol = volRange[0]
maxVol = volRange[1]
#print(minVol, maxVol)
vol = 0
#volBar = 0  #wrong for 1st value
volBar = 400
volPer = 0
area = 0
colVol = (0, 0, 255)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    #img = detector.findHands(img, draw=False)
    #lmList = detector.findPositions(img)
    lmList, bbox = detector.findPositions(img, draw=True)
    #print(lmList)
    #print(lmList[4])
    if (len(lmList)!= 0):

        # Filter based on size
        wB, hB = bbox[2]-bbox[0], bbox[3]-bbox[1]
        area = wB * hB // 100
        #print(area)

        if 250 < area < 1000:
            #print("yes")
            # Find Distance between index and thumb

            length, img, lineInfo = detector.findDistance(4, 8, img)
            #print(length)

            # Convert Volume

            # length range 50 - 300
            # volume range -65.25 - 0.0
            #vol = np.interp(length, [50, 300], [minVol, maxVol])
            #print(vol, int(length))
            volBar = np.interp(length, [50, 200], [400, 150])
            volPer = np.interp(length, [50, 200], [0, 100])


            # Reduce Resolution to make it smoother

            smoothness = 10
            volPer = smoothness * round(volPer / smoothness)

            # Check fingers up

            fingers = detector.fingersUp()
            print(fingers)

            # If pinky is down set volume

            if fingers[4] == 0:
                #volume.SetMasterVolumeLevel(vol, None)
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                #indication that u have set the volume
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 0, 255), cv2.FILLED)
                colVol = (255, 0, 0)
                time.sleep(0.25)
            else:
                colVol = (0, 0, 255)

    # Drawings

    cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 255), 3)
    #cv2.rectangle(img, (50, int(vol)), (85, 400), (0, 0, 255), cv2.FILLED)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 0, 255), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)}%', (50, 450), 2, cv2.FONT_HERSHEY_PLAIN, (0, 0, 255), 2)
    cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(img, f'Vol set: {int(cVol)}%', (400, 50), 2, cv2.FONT_HERSHEY_PLAIN, colVol, 2)

    # Frame rate

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    #print(str(int(fps)))
    cv2.putText(img, f'FPS:{int(fps)}', (40, 50), 2, cv2.FONT_HERSHEY_PLAIN, (0, 0, 255), 2)

    cv2.imshow("HandTracking", img)
    cv2.waitKey(1)