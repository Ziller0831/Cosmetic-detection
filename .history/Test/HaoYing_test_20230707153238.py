'''## * 濠瀛 視覺辨識主程式
Python version: 3.9.13
openCV version: 4.6.0
numpy  version: 1.23.5
pandas version: 1.5.3
'''

##
import cv2
from time import time
import Vision 
import Setting
import FileProcess as FP

ChooseProduct = "透白口紅座"
Mode = 0
fps = 1            
AngleZero_offset = 0
CsvDir = r"./Test/Cosmetic_parameter.csv"

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if __name__ == "__main__":
    time_start = time()
    if Mode == 1: ##! 初始化模式
        initial = Setting.initialize()
        areaSizeData, areaMeanCont, areaStdCont = initial.AreaIdent(cap)
        FP.CSVDataOutput(ChooseProduct, CsvDir, areaSizeData, areaMeanCont, areaStdCont)
    elif Mode == 0: ##! 工作模式
        vision = Vision.EdgeDetector(Mode, ChooseProduct, CsvDir)
        time_start = time()
        while True:
            frame = vision.ImageCatch(cap)
            imgBinary = vision.ImagePreProcess(frame)
            object, contoursList = vision.ContoursCalc(imgBinary)
            frame, ResultArray, MinRectArray = vision.FeaturesCalc(frame, contoursList)

            results_mean = vision.FPSBuffer(fps, ResultArray)

            for result in results_mean:
                x_coordinate = int(result[0])
                y_coordinate = int(result[1])
                text = f"({x_coordinate}, {y_coordinate})"
                # cv2.putText(frame, text, (int(result[0]+10), int(result[1]+10)), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 64, 255), 2, 8, 0)

                
            fps = round(1/(time() - time_start), 2)
            cv2.putText(frame, f"fps:{str(fps)}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
            cv2.imshow("Result", frame)

            if object == 0:
                End = "旋轉盤轉動"
            else:
                End = f"{text}"
                
            print(End) ## End為輸出給的Delta robot的訊息
            time_start = time()

            if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
                break

cap.release()
cv2.destroyAllWindows()
