import Vision
import cv2
import numpy as np

AreaSizeData = []

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cosmetic = Vision.EdgeDetector(0)

while len(AreaSizeData) < 100:
    frame = cosmetic.ImageCatch(cap)
    imgBinary = cosmetic.ImagePreProcess(frame)
    contoursList = cosmetic.ContoursCalc(imgBinary)

    for contour in contoursList:
        if cv2.contourArea(contour) > 500:
            print(cv2.contourArea(contour))
            AreaSizeData.append(cv2.contourArea(contour))

    cv2.drawContours(frame, contours, -1, (0,0,255), 2)
    cv2.imshow("Result", frame)