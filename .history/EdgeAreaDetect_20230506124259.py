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
        