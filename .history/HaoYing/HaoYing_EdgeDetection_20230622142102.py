'''## * 濠瀛 視覺辨識主程式
Python version: 3.9.13
openCV version: 4.6.0
numpy  version: 1.23.5
pandas version: 1.5.3
'''

import cv2
from time import time

import Vision 
import EdgeAreaDetect as EAD
import FileProcess as FP

ChooseProduct = "透白口紅座"
##! 模式1為初始化模式，模式0為工作模式
Mode = 0
fps = 30
AngleZero_offset = 0 ##* 0度為x軸正向 順時針範圍0~G360度
CsvDir = r"./HaoYing/Cosmetic_parameter.csv"
TxTDir = r"./HaoYing/InputData.txt"

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

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
        time_start = time()
        while True:
            frame = vision.ImageCatch(cap)
            imgBinary = vision.ImagePreProcess(frame)
            contoursList = vision.ContoursCalc(imgBinary)
            frame, ResultArray, MinRectArray = vision.FeaturesCalc(frame, contoursList)

            results_mean = vision.FPSBuffer(fps, ResultArray)

            for result in results_mean: 
                text = f"({int(result[0])}, {int(result[1])}, {result[2]-AngleZero_offset:.1f})"
                cv2.putText(frame, text, (int(result[0]+10), int(result[1]+10)), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 64, 255), 2, 8, 0)       
                
            fps = round(1/(time() - time_start), 2)
            cv2.putText(frame, f"fps:{str(fps)}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
            cv2.imshow("Result", frame)

            time_start = time()

            if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
                break

cap.release()
cv2.destroyAllWindows()
