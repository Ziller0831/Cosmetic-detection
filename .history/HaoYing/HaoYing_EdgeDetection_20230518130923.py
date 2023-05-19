'''## * 濠瀛 視覺辨識主程式
Python version: 3.9.13
openCV version: 4.6.0
numpy  version: 1.23.5
pandas version: 1.5.3
'''

import cv2
import numpy as np
import pandas as pd
from math import sin, cos, radians, sqrt

import Vision 
import EdgeAreaDetect as EAD
import FileProcess as FP

# ChooseProduct = "長樣品瓶"
Mode = 0
CsvDir = r"./HaoYing/Cosmetic_parameter.csv"
TxTDir = r"./HaoYing/InputData.txt"

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if __name__ == "__main__":
    ChooseProduct = FP.TxTInput(TxTDir)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if Mode == 1:
        vision = Vision.EdgeDetector(Mode)
        initial = EAD.initialize()
        areaSizeData, areaMeanCont, areaStdCont = initial.AreaIdent()
        scale = initial.ScaleCalc()
        FP.CSVDataInput(ChooseProduct, CsvDir, areaSizeData, areaMeanCont, areaStdCont)
    elif Mode == 0:
        vision = Vision.EdgeDetector(0, ProductName, CsvDir)
        while True:
            frame = vision.ImageCatch(cap)
            imgBinary = vision.ImagePreProcess(frame)
            # cv2.imshow('binary', imgBinary)

            contoursList = vision.ContoursCalc(imgBinary)
            frame, ResultArray, MinRectArray = vision.FeaturesCalc(frame, contoursList)

            cv2.imshow("Result", frame)

            if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
                break


cv2.destroyAllWindows()
