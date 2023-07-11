'''## * 物件邊緣檢測 Edge Detection
Python version: 3.9.13
openCV version: 4.6.0
numpy  version: 1.23.5
pandas version: 1.5.3
'''

import cv2
import FileProcess as FP
from numpy import array, int0, mean

CsvDir = r"./HaoYing/Cosmetic_parameter.csv"
TxTDir = r"./HaoYing/InputData.txt"

# ProductName = "透白口紅座"  # Input from UI

##@ 影像視覺辨識
class EdgeDetector:
    def __init__(self, ModeSW = 0,  ProductName = "", CsvDir = "", Trans_X = 1, Trans_Y = 1, Rotation = 0, scale = 0.5):
        self.ModeSW = ModeSW
        ##* FPSBuffer Parameters
        self.TargetFPS = 10
        self.DataBuffer = [[]]

        if ModeSW == 0: ##% Working Mode
            Area_Avg, Area_Std, product_color, catchOffset, product_height =FP.CSVDataLoad(CsvDir, ProductName)
            ##* Camera2Delta coordinates transform parameters
            self.X_offset = 0
            self.Y_offset = 0
            self.Z_offset = product_height

            self.Area_range = [Area_Avg-Area_Std*5, Area_Avg+Area_Std*5]
            if product_color == '淺色': self.HSV_range = [array([180, 25, 255]), array([0, 0, 155])]
            elif product_color == '深色': self.HSV_range = [array([180, 255, 230]), array([0, 0, 154])]
            else: print('Error: No such product color')

            self.catchPoint = catchOffset
        elif ModeSW == 1: ##% EdgeAreaDetect mode
            self.Area_range = [500, 500000]
            self.HSV_range = [array([180, 25, 255]), array([0, 0, 155])]
    
    ##@ 畫面補捉
    def ImageCatch(self, cap):
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream  end?). Exiting ...")
            exit()
        return frame
    
    ##@ 將影像HSV二值化並形態學處理
    def ImagePreProcess(self, img_src):
        HSV_img = cv2.cvtColor(img_src, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(HSV_img, self.HSV_range[1], self.HSV_range[0])
        imgBinary  = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
        return imgBinary
    
    ##@ 輪廓框選與篩選
    def ContoursCalc(self, imgBinary):
        contours = cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
        contoursList = [contour for contour in contours if self.Area_range[0] <= cv2.contourArea(contour) <= self.Area_range[1]]
        if contoursList > 0:
        return contoursList
        
    ##@ 計算輪廓的特徵
    def FeaturesCalc(self, frame, contoursList):
        MinRectArray = []
        ResultArray = []
        for contour in contoursList:
            centerPoint, minRect, Angle = self.MinRectCircle(contour)        
            MinRectArray.append(minRect)
            if self.ModeSW != 2:
                ResultArray.append([centerPoint[0], centerPoint[1]])
                cv2.circle(frame, centerPoint, 5, (100,255,100), -1)
        if self.ModeSW != 2: 
            cv2.drawContours(frame, contoursList, -1, (0,0,255), 2)
        for minRect in MinRectArray:
            cv2.drawContours(frame, [minRect], 0, (0, 255, 0), 2) # print(minRect)
        return frame, ResultArray, MinRectArray

    ##@ 輪廓重心點計算
    def GPointCalc(self, moment):
        return int(moment['m10']/moment['m00']), int(moment['m01']/moment['m00'])
    
    ##@ 輪廓最小外接矩形
    def MinRectCircle(self, contour):
        rawMinRect = cv2.minAreaRect(contour)
        min_rect = int0(cv2.boxPoints(rawMinRect))
        return int0(rawMinRect[0]), min_rect, round(rawMinRect[2], 4)

    ##@ FPS緩衝器(用於讓數值穩定)
    def FPSBuffer(self, fps = 30, resultData = None):
        if self.DataBuffer:
            diff_buffer = len(self.DataBuffer) - int(fps//self.TargetFPS) + 1
            self.DataBuffer = self.DataBuffer[diff_buffer if diff_buffer >= 0 else 0:]
        self.DataBuffer.append(resultData)
        results_mean = mean(array(self.DataBuffer, dtype=object), axis=0)
        return results_mean

    ##@ Camera coordinate transfer to Delta Robot coordinate
    def Coordinate_TF(self, camera_coordinate):
        robot_x = camera_coordinate[0] + self.X_offset
        robot_y = camera_coordinate[1] + self.Y_offset
        robot_z = camera_coordinate[2] + self.Z_offset

        return (robot_x, robot_y, robot_z)
    


if __name__ == '__main__':
    ProductName = FP.TxTInput(TxTDir)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    vision = EdgeDetector(0, ProductName, CsvDir)
    while True:
        frame = vision.ImageCatch(cap)
        imgBinary = vision.ImagePreProcess(frame)

        contoursList = vision.ContoursCalc(imgBinary)
        frame, ResultArray, MinRectArray = vision.FeaturesCalc(frame, contoursList)

        cv2.imshow("Result", frame)

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break
    cv2.destroyAllWindows()