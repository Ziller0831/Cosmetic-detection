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
import File

ChooseProduct = "長樣品瓶"
Mode = 0
CsvDir = r"./HaoYing/Cosmetic_parameter.csv"
TxTDir = r"./HaoYing/InputData.txt"

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if __name__ == "__main__":
    ProductName = FP.TxTInput(TxTDir)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if Mode == 0:
        vision = Vision.EdgeDetector(1)
        initial = EAD.initialize()

        areaSizeData, areaMeanCont, areaStdCont = initial.AreaIdent()
        scale = initial.ScaleCalc()

        FP.CSVDataInput(ProductName, CsvDir, areaSizeData, areaMeanCont, areaStdCont)

    print(f'\nArea: Mean std Max-min Scale\n{areaMeanCont:.4f},{areaStdCont:.4f},{max(areaSizeData)-min(areaSizeData):.4f}, {scale}')

cv2.destroyAllWindows()
