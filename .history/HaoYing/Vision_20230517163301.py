'''## * 物件邊緣檢測 Edge Detection
Python version: 3.9.13
openCV version: 4.6.0
numpy  version: 1.23.5
pandas version: 1.5.3
'''

import cv2
from numpy import array, deg2rad, int0
import pandas as pd
from math import sin, cos, radians

ProductName = "長樣品蓋"  # Input from UI
CsvDir = r"C:/Users/jcyu/Documents/GitHub/OpenCV-image-process-test/HaoYing/Cosmetic_parameter.csv"

class EdgeDetector:
    def __init__(self, ModeSW = 0,  ProductName = "", CsvDir = "", Trans_X = 1, Trans_Y = 1, Rotation = 0, scale = 0.5):
        self.ModeSW = ModeSW
        if ModeSW == 0: ##% Working Mode
            product_dic = pd.read_csv(CsvDir, encoding='BIG5').to_dict()
            product_index = next((key for key,name in product_dic.get('產品名稱').items() if name == ProductName), None)
            Area_Avg = product_dic.get('面積平均').get(product_index)
            Area_Std = product_dic.get('面積標準差').get(product_index)
            product_color = product_dic.get('產品顏色').get(product_index)
            catchoffset = product_dic.get('吸取點').get(product_index)

            self.Area_range = [Area_Avg-Area_Std*5, Area_Avg+Area_Std*5]
            if product_color == '淺色': self.HSV_range = [array([180, 25, 255]), array([0, 0, 155])]
            elif product_color == '深色': self.HSV_range = [array([180, 255, 230]), array([0, 0, 154])]
            else: print('Error: No such product color')

            self.translation_x = Trans_X
            self.translation_y = Trans_Y
            self.rotation_Angle = deg2rad(Rotation)
            self.scale = scale
            self.catchPoint = catchLocal
        elif ModeSW == 1: ##% EdgeAreaDetect mode
            self.Area_range = [500, 500000]
            self.HSV_range = [array([180, 25, 255]), array([0, 0, 155])]

    
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
        contoursList = [contour for contour in contours if self.Area_range[0] <= cv2.contourArea(contour) <= self.Area_range[1]]
        return contoursList
        
    def FeaturesCalc(self, frame, contoursList):
        ArrowLength = 50
        MinRectArray = []
        ResultArray = []
        for contour in contoursList:
            moment = cv2.moments(contour)
            gravityPoint = array(self.GPointCalc(moment))
            centerPoint, minRect, rawAngle = self.MinRectCircle(contour)
            MinRectArray.append(minRect)
            if self.ModeSW != 2:
                deltaX, deltaY = gravityPoint - centerPoint
                angle = self.AngleIndentify(deltaX, deltaY, 90-rawAngle)
                ResultArray.append([centerPoint[0], centerPoint[1], round(angle, 4)])
            
                endPoint = [int(centerPoint[0]+ArrowLength*cos(radians(angle))), int(centerPoint[1]+(-ArrowLength*sin(radians(angle))))]
                CatchPoint = [int(centerPoint[0]+self.catchPoint*cos(radians(angle))), int(centerPoint[1]+(-self.catchPoint*sin(radians(angle))))]
                cv2.arrowedLine(frame, centerPoint, (endPoint[0], endPoint[1]), (255,100,0), 2)
                cv2.circle(frame, centerPoint, 5, (0,0,255), -1)
                cv2.circle(frame, gravityPoint, 5, (0,0,255), -1)
                cv2.circle(frame, CatchPoint, 5, (255,100,0), -1)
        if self.ModeSW != 2: cv2.drawContours(frame, contoursList, -1, (0,0,255), 2)
        for minRect in MinRectArray:
            cv2.drawContours(frame, [minRect], 0, (0, 255, 0), 2) # print(minRect)
        return frame, ResultArray, MinRectArray

    def GPointCalc(self, moment):
        return int(moment['m10']/moment['m00']), int(moment['m01']/moment['m00'])
    
    def MinRectCircle(self, contour):
        rawMinRect = cv2.minAreaRect(contour)
        min_rect = int0(cv2.boxPoints(rawMinRect))
        return int0(rawMinRect[0]), min_rect, round(rawMinRect[2], 4)
    
    def AngleIndentify(self, deltaX, deltaY, angle):
        if deltaX > 0: return angle if deltaY < 0 else 0 if deltaY == 0 else (angle+270) if deltaY > 0 else None
        if deltaX < 0: return (angle+90) if deltaY < 0 else (angle+180) if deltaY > 0 else (angle+180) if deltaY == 0 else None
        if deltaX == 0: return (angle+90) if deltaY < 0 else (angle+270) if deltaY > 0 else 0

    def Coordinate_TF(self):
        pass
    


if __name__ == '__main__':
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