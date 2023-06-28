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
from time import time

import Vision 
import EdgeAreaDetect as EAD
import FileProcess as FP

ChooseProduct = "長樣品蓋"
##! 模式1為初始化模式，模式0為工作模式
Mode = 0
fps = 30
AngleZero_offset = 1
CsvDir = r"./HaoYing/Cosmetic_parameter.csv"
TxTDir = r"./HaoYing/InputData.txt"

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('HaoYing.mp4', fourcc, 32, (640, 480))

if __name__ == "__main__":
    time_start = time()
    # ChooseProduct = FP.TxTInput(TxTDir)
    if Mode == 1:
        initial = EAD.initialize()
        areaSizeData, areaMeanCont, areaStdCont = initial.AreaIdent(cap)
        scale = initial.ScaleCalc(cap)
        FP.CSVDataInput(ChooseProduct, CsvDir, areaSizeData, areaMeanCont, areaStdCont)
    elif Mode == 0:
        vision = Vision.EdgeDetector(Mode, ChooseProduct, CsvDir)
        while True:
            frame = vision.ImageCatch(cap)
            imgBinary = vision.ImagePreProcess(frame)
            contoursList = vision.ContoursCalc(imgBinary)
            frame, ResultArray, MinRectArray = vision.FeaturesCalc(frame, contoursList)
            results_mean = vision.FPSBuffer(fps, ResultArray)
            for result in results_mean: 
                text = f"({int(result[0])}, {int(result[1])}, {result[2]-AngleZero_offset:.1f})" 
            cv2.imshow("Result", frame)
            if cv2.waitKey(1) & 0xFF != ord('p'):
                out.write(frame)
            if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
                break
            fps = round(1/(time() - time_start), 2)

cap.release()
out.release()
cv2.destroyAllWindows()
