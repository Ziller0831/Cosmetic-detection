'''## * 物件邊緣檢測 Edge Detection
Python version: 3.9.13
openCV version: 4.6.0
numpy  version: 1.23.5
pandas version: 1.5.3
'''

import cv2
import FileProcess as FP
import numpy as np
from math import sin, cos, radians

CsvDir = r"./HaoYing/Cosmetic_parameter.csv"
TxTDir = r"./HaoYing/InputData.txt"

# ProductName = "透白口紅座"  # Input from UI

##@ 影像視覺辨識
class EdgeDetector:
    def __init__(self, ModeSW = 0,  ProductName = "", CsvDir = "", TFParm = ""):
        self.ModeSW = ModeSW

        ##* FPSBuffer Parameters
        self.TargetFPS = 10
        self.DataBuffer = [[]]

        if ModeSW == 0: ##% Working Mode
            Area_Avg, Area_Std, product_color, catchOffset, product_height =FP.CSVDataLoad(CsvDir, ProductName)

            ##* Coordinate transform parameters
            rvec_matrix, _ = cv2.Rodrigues(TFParm["rvecs"])
            projection_matrix = np.dot(TFParm["camera_matrix"], np.hstack((rvec_matrix, TFParm["tvecs"])))
            self.pseudo_inverse_projection = np.linalg.pinv(projection_matrix)

            self.X_offset = 0
            self.Y_offset = 0
            self.Z_offset = product_height

            self.Area_range = [Area_Avg-Area_Std*5, Area_Avg+Area_Std*5]
            if   product_color == '淺色': self.HSV_range = [np.array([180, 25, 255]),  np.array([0, 0, 155])]
            elif product_color == '深色': self.HSV_range = [np.array([180, 255, 230]), np.array([0, 0, 154])]
            else: print('Error: No such product color')

            self.catchPoint = catchOffset

        elif ModeSW == 1: ##% EdgeAreaDetect mode
            self.Area_range = [500, 500000]
            self.HSV_range = [np.array([180, 25, 255]), np.array([0, 0, 155])]
    
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
        img_binary  = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
        return img_binary
    
    ##@ 輪廓框選與篩選
    def ContoursCalc(self, img_binary):
        contours = cv2.findContours(img_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
        contour_list = [contour for contour in contours if self.Area_range[0] <= cv2.contourArea(contour) <= self.Area_range[1]]
        return contour_list
        
    ##@ 計算輪廓的特徵
    def FeaturesCalc(self, frame, contour_list):
        arrow_length = 50
        MinRectArray = []
        ResultArray = []

        for contour in contour_list:

            moment = cv2.moments(contour)
            gravityPoint = np.array(self.GPointCalc(moment))
            centerPoint, minRect, rawAngle = self.MinRectCircle(contour)        
            MinRectArray.append(minRect)

            if self.ModeSW != 2:

                deltaX, deltaY = centerPoint - gravityPoint ##! 角度計算法則在評估
                angle = self.AngleCalc(minRect, deltaY)
                # print(f"{rawAngle},{deltaX*5},{deltaY*5}", end="\r")
                
                ResultArray.append([centerPoint[0], centerPoint[1], round(angle, 4)])
            
                endPoint = [int(centerPoint[0]+arrow_length*cos(radians(angle))), int(centerPoint[1]-arrow_length*sin(radians(angle)))]
                CatchPoint = [int(centerPoint[0]+self.catchPoint*cos(radians(angle))), int(centerPoint[1]-self.catchPoint*sin(radians(angle)))]

                cv2.arrowedLine(frame, centerPoint, (endPoint[0], endPoint[1]), (255,100,0), 2)
                cv2.circle(frame, centerPoint, 5, (100,255,100), -1)
                cv2.circle(frame, gravityPoint, 5, (0,0,255), -1)
                # cv2.circle(frame, CatchPoint, 5, (255,0,255), -1)

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
        min_rect = np.int0(cv2.boxPoints(rawMinRect))
        return np.int0(rawMinRect[0]), min_rect, round(rawMinRect[2], 4)
    
    ##@ 利用輪廓最小外矩形角度計算
    def AngleCalc(self, minRectPoint, deltaY):
        vector_a = minRectPoint[1] - minRectPoint[0]
        vector_b = minRectPoint[2] - minRectPoint[1]

        vector_a_value = (vector_a[0]**2+vector_a[1]**2)**0.5
        vector_b_value = (vector_b[0]**2+vector_b[1]**2)**0.5

        if(vector_a_value < vector_b_value):
            vector = vector_a
        elif(vector_a_value > vector_b_value):
            vector = vector_b
        
        theta = cv2.fastAtan2(int(vector[0]), int(vector[1]))

        if deltaY < 0:
            return (theta + 180)%360
        else:
            return theta

    ##@ FPS緩衝器(用於讓數值穩定)
    def FPSBuffer(self, fps = 30, resultData = None):
        if self.DataBuffer:
            diff_buffer = len(self.DataBuffer) - int(fps//self.TargetFPS) + 1
            self.DataBuffer = self.DataBuffer[diff_buffer if diff_buffer >= 0 else 0:]
        self.DataBuffer.append(resultData)
        results_mean = np.mean(np.array(self.DataBuffer, dtype=object), axis=0)
        return results_mean

    ##@ Pixel coordinate transfer to world coordinate
    def Coordinate_TF(self, pixel_coordinate):
        homogeneous2pixel = np.array([pixel_coordinate], dtype=np.float32).T
        homogeneous2world = np.dot(self.pseudo_inverse_projection, homogeneous2pixel)
        world_x = homogeneous2world[0] / homogeneous2world[3]
        world_y = homogeneous2world[1] / homogeneous2world[3]

        return world_x, world_y
    


if __name__ == '__main__':
    ProductName = FP.TxTInput(TxTDir)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    vision = EdgeDetector(0, ProductName, CsvDir)
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