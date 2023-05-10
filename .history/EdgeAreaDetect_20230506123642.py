import Vision
import cv2
import numpy as np

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cosmetic = Vision.EdgeDetector()

while len(AreaSizeData) < 10:
    frame = cosmetic.ImageCatch(cap)
    imgBinary = cosmetic.ImagePreProcess(frame)