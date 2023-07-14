import cv2
import numpy as np
from math import sqrt
import glob

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

        self.Chessboard = (9,6)
        self.Chessboard_squareSize = 24 # mm
        self.Chessboard_path = r"./HaoYing/Chessboard_image/"

    ##@ 界定產品的輪廓面積範圍
    def AreaIdent(self, cap):
        AreaSizeData = []
        for i, (x, y) in enumerate(self.CheckPoint):
            if  cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
                break
            print('')
            while  cv2.waitKey(1) & 0xFF != ord('q'):
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
        areaMeanCont = np.mean(np.array(AreaSizeData, dtype=object))
        areaStdCont = np.std(np.array(AreaSizeData,  dtype=float), axis=0, ddof=1)
        return AreaSizeData, areaMeanCont, areaStdCont
    
    ##@ 取得用於座標轉換的縮放因子
    def ScaleCalc(self, cap):
        print(end='\r')
        Width = []
        Height = []
        while  cv2.waitKey(1) & 0xFF != ord('q'):
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
        widthScale = self.TargetEdgeSize / np.mean(np.array(Width, dtype=object))
        heightScale = self.TargetEdgeSize / np.mean(np.array(Height, dtype=object))
        scale = (widthScale+heightScale)/2
        return scale
    
    ##@ 相機標定
    def Chessboard_Catch(self):
        count = 0
        while count < 10:
            frame = self.vision.ImageCatch(cap)
            cv2.imshow("Webcam", frame)
            print('將校正板放置在紅點處，放置後請按Q',end='\r')
            if  cv2.waitKey(1) & 0xFF != ord('q'):
                cv2.imwrite(self.Chessboard_path+str(count)+'.png', frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
                print(f"已拍攝並儲存照片 {count}")
                count += 1
            if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
                break
        cv2.destroyAllWindows()
        cap.release()
    
    def Standard_Catch(self):
        while count < 1:
            frame = self.vision.ImageCatch(cap)
            cv2.imshow("Webcam", frame)
            print('將校正板放置在紅點處，放置後請按Q',end='\r')
            if  cv2.waitKey(1) & 0xFF != ord('q'):
                cv2.imwrite("Standard.png", frame)
                print("拍照完成")
                count += 1
            if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
                break
        cv2.destroyAllWindows()
        cap.release()
    
    def Camera_Calibration(self):
        objp = np.zeros((np.prod(self.Chessboard), 3), dtype=np.float32)
        objp[:, :2] = np.mgrid[0:self.Chessboard[0], 0:self.Chessboard[1]].T.reshape(-1, 2) * self.Chessboard_squareSize

        objpoints = []  # 物體座標
        imgpoints = []  # 影像座標

        self.Chessboard_Catch()
        image_paths = glob.glob(self.Chessboard_path+"*.png")
        for image_path in image_paths:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BRG2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, self.Chessboard, None)
            if ret == True:
                objpoints.append(objp)
                imgpoints.append(corners)

                cv2.drawChessboardCorners
    



if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    initial = initialize()

    areaSizeData, areaMeanCont, areaStdCont = initial.AreaIdent(cap)
    scale = initial.ScaleCalc()

    FP.CSVDataInput(ProductName, CsvDir, areaSizeData, areaMeanCont, areaStdCont)

    print(f'\nArea: Mean std Max-min Scale\n{areaMeanCont:.4f},{areaStdCont:.4f},{max(areaSizeData)-min(areaSizeData):.4f}, {scale}')

cv2.destroyAllWindows()