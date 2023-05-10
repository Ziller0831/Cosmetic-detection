'''## * 物件邊緣檢測 Edge Detection
Python version: 3.9.13
openCV version: 4.6.0
numpy  version: 1.23.5
pandas version: 1.5.3
'''
import cv2
import numpy as np
import pandas as pd
from math import sin, cos, radians

ProductName = "長樣品蓋"  # Input from UI
CsvDir = r"C:\Users\jcyu\Documents\GitHub\OpenCV-image-process-test\Cosmetic_parameter.csv"

class ImageCalibration:
    def __init__(self):
        pass

class EdgeDetector:
    def __init__(self, ProductName = "", CsvDir = ""):
        product_dic = pd.read_csv(CsvDir, encoding='BIG5').to_dict()
        product_index = next((key for key,value in product_dic.get('產品名稱').items() if value == ProductName), None)
        length_Avg = product_dic.get('產品輪廓周長').get(product_index)
        length_Std = product_dic.get('周長標準差').get(product_index)
        product_color = product_dic.get('產品顏色').get(product_index)

        # self.length_range = [length_Avg-length_Std*5, length_Avg+length_Std*5] #[Min length, Max length]
        self.length_range = [300, 350]
        if product_color == '淺色': self.HSV_range = [np.array([180, 25, 255]), np.array([0, 0, 155])]
        elif product_color == '深色': self.HSV_range = [np.array([180, 255, 230]), np.array([0, 0, 154])]
        else: print('Error: No such product color')
    
    def ImageCatch(self, cap):
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream  end?). Exiting ...")
            exit()
        return frame

    def ImagePreProcess(self, img_src):
        HSV_img = cv2.cvtColor(img_src, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(HSV_img, self.HSV_range[1], self.HSV_range[0])
        imgBinary  = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
        return imgBinary
    
    def ContoursCalc(self, imgBinary):
        contours = cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
        contoursList = [contour for contour in contours if self.length_range[0] <= cv2.arcLength(contour, True) <= self.length_range[1]]
        return contoursList
        
    def FeaturesCalc(self, frame, contoursList):
        ArrowLength = 50
        MinRectArray = []
        ResultArray = []

        for contour in contoursList:
            moment = cv2.moments(contour)
            gravityPoint = np.array(self.GPointCalc(moment))
            centerPoint, minRect, rawAngle = self.MinRectCircle(contour)
            MinRectArray.append(minRect)

            deltaX, deltaY = gravityPoint - centerPoint
            angle = self.AngleIndentify(deltaX, deltaY, 90-rawAngle)
            ResultArray.append([centerPoint[0], centerPoint[1], round(angle, 4)])
            
            endPoint = [int(centerPoint[0]+ArrowLength*cos(radians(angle))), int(centerPoint[1]+(-ArrowLength*sin(radians(angle))))]
            cv2.arrowedLine(frame, centerPoint, (endPoint[0], endPoint[1]), (255,100,0), 2)
            cv2.circle(frame, centerPoint, 5, (0,0,255), -1)
            cv2.circle(frame, gravityPoint, 5, (0,0,255), -1)
        return frame, ResultArray, MinRectArray

    def GPointCalc(self, moment):
        return int(moment['m10']/moment['m00']), int(moment['m01']/moment['m00'])
    
    def MinRectCircle(self, contour):
        rawMinRect = cv2.minAreaRect(contour)
        min_rect = np.int0(cv2.boxPoints(rawMinRect))
        return np.int0(rawMinRect[0]), min_rect, round(rawMinRect[2], 4)
    
    def AngleIndentify(self, deltaX, deltaY, angle):
        if deltaX > 0: return angle if deltaY < 0 else 0 if deltaY == 0 else (angle+270) if deltaY > 0 else None
        if deltaX < 0: return (angle+90) if deltaY < 0 else (angle+180) if deltaY > 0 else (angle+180) if deltaY == 0 else None
        if deltaX == 0: return (angle+90) if deltaY < 0 else (angle+270) if deltaY > 0 else 0

class



if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = EdgeDetector(ProductName, CsvDir)
    while True:
        frame = cosmetic.ImageCatch(cap)
        imgBinary = cosmetic.ImagePreProcess(frame)
        # cv2.imshow('binary', imgBinary)

        contoursList = cosmetic.ContoursCalc(imgBinary)
        frame, ResultArray, MinRectArray = cosmetic.FeaturesCalc(frame, contoursList)

        cv2.drawContours(frame, contoursList, -1, (0,0,255), 2)
        for minRect in MinRectArray:
            cv2.drawContours(frame, [minRect], 0, (0, 255, 0), 2) # print(minRect)
        cv2.drawContours(frame, contoursList,-1, (255,0,0), 2)

        cv2.imshow("Result", frame)

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break
    cv2.destroyAllWindows()