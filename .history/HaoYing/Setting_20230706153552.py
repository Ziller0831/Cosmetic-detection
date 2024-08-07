import cv2
from numpy import array, mean, std
from math import sqrt

import Vision
import FileProcess as FP

ProductName = "長樣品瓶"

CsvDir = r"./Cosmetic_parameter.csv"

##@ 用於一開始的初始化
class initialize:
    def __init__(self):
        self.vision = Vision.EdgeDetector(1)
        self.CheckPoint = [[320,240], [150,110], [150,375], [475,375], [475,110]]
        self.TargetEdgeSize = 90
        self.CatchPhotoNums = 5
        self.key = cv2.waitKey(1) & 0xFF

    ##@ 界定產品的輪廓面積範圍
    def AreaIdent(self, cap):
        AreaSizeData = []
        for i, (x, y) in enumerate(self.CheckPoint):
            if self.key == 27: ## 27 = ESC
                break
            print('')
            while self.key != ord('q'):
                frame = self.vision.ImageCatch(cap)
                cv2.circle(frame, (x, y), 5, (0,0,255), -1)
                cv2.imshow("Image", frame)
                print('請換下個位置，放置後請按Q',end='\r')
            print('')
            for i in range(100):
                print(f'請勿進入鏡頭範圍，目前搜尋數據量:{i+1}', end = '\r')
                frame = self.vision.ImageCatch(cap)
                imgBinary = self.vision.ImagePreProcess(frame)
                contoursList = self.vision.ContoursCalc(imgBinary)
                for contour in contoursList:
                    if cv2.contourArea(contour) > 100:
                        AreaSizeData.append(cv2.contourArea(contour))
        cv2.drawContours(frame, contoursList, -1, (0,0,255), 2)
        cv2.waitKey(1)
        areaMeanCont = mean(array(AreaSizeData, dtype=object))
        areaStdCont = std(array(AreaSizeData,  dtype=float), axis=0, ddof=1)
        return AreaSizeData, areaMeanCont, areaStdCont
    
    ##@ 取得用於座標轉換的縮放因子
    def ScaleCalc(self, cap):
        print(end='\r')
        Width = []
        Height = []
        while self.key != ord('q'):
            frame = self.vision.ImageCatch(cap)
            cv2.circle(frame, self.CheckPoint[0], 5, (0,0,255), -1)
            cv2.imshow("Image", frame)
            print('將校正板放置在紅點處，放置後請按Q',end='\r')
        print('')
        for i in range(100):
            print(f'請勿進入鏡頭範圍，目前搜尋數據量:{i+1}', end = '\r')
            frame = self.vision.ImageCatch(cap)
            imgBinary = self.vision.ImagePreProcess(frame)
            contoursList = self.vision.ContoursCalc(imgBinary)
            for contour in contoursList:
                if cv2.contourArea(contour) > 100:
                    corners = self.vision.MinRectCircle(contour)[1]
                    Width.append(sqrt((corners[1][0] - corners[0][0])**2 + (corners[1][1] - corners[0][1])**2))
                    Height.append(sqrt((corners[3][0] - corners[0][0])**2 + (corners[3][1] - corners[0][1])**2))
        widthScale = self.TargetEdgeSize / mean(array(Width, dtype=object))
        heightScale = self.TargetEdgeSize / mean(array(Height, dtype=object))
        scale = (widthScale+heightScale)/2
        return scale
    
    ##@ 相機標定
    def Chessboard_Catch(self):
        while count < self.CatchPhotoNums:
            frame = self.vision.ImageCatch(cap)
            cv2.imshow("Webcam", frame)
            print('將校正板放置在紅點處，放置後請按Q',end='\r')
            if self.key != ord('q'):
                cv2.imwrite(f"ChessBoard_{count}", frame)
            

    def Camera_Calibration(self, frame):
        pass
    



if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    initial = initialize()

    areaSizeData, areaMeanCont, areaStdCont = initial.AreaIdent(cap)
    scale = initial.ScaleCalc()

    FP.CSVDataInput(ProductName, CsvDir, areaSizeData, areaMeanCont, areaStdCont)

    print(f'\nArea: Mean std Max-min Scale\n{areaMeanCont:.4f},{areaStdCont:.4f},{max(areaSizeData)-min(areaSizeData):.4f}, {scale}')

cv2.destroyAllWindows()