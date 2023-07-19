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
        self._vision = Vision.EdgeDetector(1)
        self._CheckPoint = [[320,240], [150,110], [150,375], [475,375], [475,110]]
        self._TargetEdgeSize = 90

        self._Chessboard = (9,6)
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
    
    ##@ 棋盤格截圖
    def ChessboardCatch(self, cap):
        count = 0
        while count < 10:
            frame = self.vision.ImageCatch(cap)
            cv2.imshow("Webcam", frame)
            print('將校正板放置在紅點處, 放置後請按Enter',end='\r')
            key = cv2.waitKey(1)
            if  key == 13:
                cv2.imwrite(self.Chessboard_path+str(count)+'.png', frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
                print(f"已拍攝並儲存照片 {count}")
                count += 1
            if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
                break
        cv2.destroyAllWindows()

    
    def StandardCatch(self, cap):
        while True:
            frame = self.vision.ImageCatch(cap)
            cv2.imshow("Webcam", frame)
            print('將校正板放置在紅點處, 放置後請按Enter',end='\r')
            key = cv2.waitKey(1)
            if  key == 13:
                cv2.imwrite(self.Chessboard_path+"Standard.png", frame)
                print("拍照完成")
                break
            if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
                break

        cv2.destroyAllWindows()

    ##@ 相機標定
    def CameraCalibration(self, cap):
        objp = np.zeros((np.prod(self.Chessboard), 3), dtype=np.float32)
        objp[:, :2] = np.mgrid[0:self.Chessboard[0], 0:self.Chessboard[1]].T.reshape(-1, 2) * self.Chessboard_squareSize

        objpoints = []  # 物體座標
        imgpoints = []  # 影像座標

        self.ChessboardCatch(cap)
        image_paths = glob.glob(self.Chessboard_path+"*.png")
        for image_path in image_paths:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, self.Chessboard, None)
            if ret == True:
                objpoints.append(objp)
                imgpoints.append(corners)

                cv2.drawChessboardCorners(img, self.Chessboard, corners, ret)
                cv2.imshow("Chessboard corners", img)
                cv2.waitKey(100)
        cv2.destroyAllWindows()

        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        print(f"Camera inner parameter: {camera_matrix}")
        print(f"Camera distortion parameter:{dist_coeffs}")

        self.StandardCatch(cap)
        std_img = cv2.imread(r'.\HaoYing\Standard.png')
        gray = cv2.cvtColor(std_img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, self.Chessboard, None)

        if ret == True:
            objpoints.append(objp)
            imgpoints.append(corners)
        
        _, rvecs, tvecs = cv2.solvePnP(objp, corners, camera_matrix, dist_coeffs)

        axis_length = self.Chessboard_squareSize * 2  # 座標軸的長度
        img = cv2.drawFrameAxes(img, camera_matrix, dist_coeffs, rvecs, tvecs, axis_length)

        img = cv2.circle(img, (int(corners[0][0][0]), int(corners[0][0][1])), 5, (0, 0, 255), -1)
        print("原點像素位置:", corners[0][0])
        cv2.imshow('Image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return camera_matrix, rvecs, tvecs
    



if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    initial = initialize()

    areaSizeData, areaMeanCont, areaStdCont = initial.AreaIdent(cap)
    scale = initial.ScaleCalc()

    FP.CSVDataInput(ProductName, CsvDir, areaSizeData, areaMeanCont, areaStdCont)

    print(f'\nArea: Mean std Max-min Scale\n{areaMeanCont:.4f},{areaStdCont:.4f},{max(areaSizeData)-min(areaSizeData):.4f}, {scale}')

cv2.destroyAllWindows()