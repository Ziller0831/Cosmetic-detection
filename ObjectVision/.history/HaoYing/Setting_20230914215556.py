'''
********************************
        初始化 副程式
********************************

相機標定與校正用的方法：https://www.twblogs.net/a/5ee7e4b5da5a4e62b6f87b50
'''

import os
import cv2
import glob
import numpy as np
import HaoYing.Vision as Vision
import HaoYing.FileProcess as FP

CurrentDir = os.getcwd()

def TextPrint(frame, text):
    wordColor = (0, 255, 255)    # 字的顏色
    position = (0, 20)           # 字的位置
    cv2.rectangle(frame, (0,0), (655,25), (0,0,0), cv2.FILLED)
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, wordColor, 1)


##@ 初始化
class initialize:
    def __init__(self, object, csvPath):
        objectData = FP.CSVDataLoad(csvPath, object)
        self._vision = Vision.EdgeDetector(0, "", objectData)
        self._CheckPoint = [[320,240], [150,110], [150,375], [475,375], [475,110]]  # 顯示在畫面的紅點座標

        self._Chessboard = (8,5)           # 棋盤格的長寬數量
        self._Chessboard_squareSize = 20   # 棋盤格小格的長度 mm


    ##@ 界定產品的輪廓面積範圍
    def AreaIdent(self):
        AreaSizeData = []
        for i, (x, y) in enumerate(self._CheckPoint):
            while  cv2.waitKey(1) & 0xFF != 13:
                frame = self._vision.ImageCatch()
                imgBinary = self._vision.ImagePreProcess(frame)
                cv2.circle(frame, (x, y), 5, (0,0,255), -1)
                text = 'Change to the next place and press Enter'
                TextPrint(frame, text)
                cv2.imshow("ObjectContours", frame)
                cv2.imshow("ObjectContoursBinary", imgBinary)
                

            for i in range(100):
                cv2.destroyAllWindows()
                frame = self._vision.ImageCatch()
                imgBinary = self._vision.ImagePreProcess(frame)
                contours = self._vision.ContoursCalc(imgBinary)
                text = f'Dont enter the camera vision, Select data number:{i+1}'
                for contour in contours:
                    if cv2.contourArea(contour) > 100:
                        AreaSizeData.append(cv2.contourArea(contour))

        areaMean = np.mean(np.array(AreaSizeData, dtype=object))
        areaStd  = np.std(np.array(AreaSizeData,  dtype=float), axis=0, ddof=1)
        return areaMean, areaStd


    ##@ 拍攝校準用棋盤格
    def _ChessboardCatch(self):
        workPath = os.path.join(CurrentDir, "./CalibrationImage")
        os.chdir(workPath)

        count = 0
        while count < 15:
            frame = self._vision.ImageCatch()
            text = f'Place the Calibration board and press Enter({count}/15)'
            TextPrint(frame, text)
            cv2.imshow("Calibration", frame)

            if cv2.waitKey(1) & 0xFF == 13: ##* ASCII 13=Enter
                frame = self._vision.ImageCatch()
                cv2.imwrite(str(count)+'.png', frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
                count += 1
            
            if cv2.waitKey(1) & 0xFF == 27: break
        cv2.destroyAllWindows()


    ##@ 拍攝標定用棋盤格
    def _StandardCatch(self):
        workPath = CurrentDir
        os.chdir(workPath)

        while True:
            frame = self._vision.ImageCatch()
            text = 'Place the Calibration board and press Enter'
            TextPrint(frame, text)
            cv2.imshow("Standard", frame)
            if  cv2.waitKey(1) & 0xFF == 13:
                frame = self._vision.ImageCatch()
                cv2.imwrite("Standard.png", frame)
                break
            if cv2.waitKey(1) & 0xFF == 27: break

        cv2.destroyAllWindows()


    ##@ 相機標定
    def CameraCalibration(self):
        objp = np.zeros((np.prod(self._Chessboard), 3), dtype=np.float32)
        objp[:, :2] = np.mgrid[0:self._Chessboard[0], 0:self._Chessboard[1]].T.reshape(-1, 2) * self._Chessboard_squareSize

        objPoints = []  # 物體座標
        imgPoints = []  # 影像座標

        self._ChessboardCatch()
        os.chdir(CurrentDir)
        imagePaths = glob.glob("CalibrationImage/*.png")

        for imagePath in imagePaths:
            img = cv2.imread(imagePath)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cv2.imshow("ddd", img)
            print()
            ret, corners = cv2.findChessboardCorners(gray, self._Chessboard, None)

            # 驗證圖片格式
            if not cv2.imread(imagePath).dtype == cv2.CV_8UC3:
                raise ValueError("Image format is not correct.")

            # 檢查圖片是否為空或損壞
            if cv2.imread(imagePath).size == 0:
                raise ValueError("Image is empty or corrupted.")
            
            if ret == True:
                objPoints.append(objp)
                imgPoints.append(corners)

                cv2.drawChessboardCorners(img, self._Chessboard, corners, ret)
                cv2.imshow("Chessboard corners", img)
                cv2.waitKey(100)

        cv2.destroyAllWindows()

        ret, cameraMatrix, distCoeffs, rvecs, tvecs = cv2.calibrateCamera(objPoints, imgPoints, gray.shape[::-1], None, None)
        print(f"Camera inner parameter: {cameraMatrix}")
        print(f"Camera distortion parameter:{distCoeffs}")

        self._StandardCatch()
        stdImg = cv2.imread("Standard.png")
        gray = cv2.cvtColor(stdImg, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, self._Chessboard, None)

        if ret == True:
            objPoints.append(objp)
            imgPoints.append(corners)
        
        _, rvecs, tvecs = cv2.solvePnP(objp, corners, cameraMatrix, distCoeffs)

        axis_length = self._Chessboard_squareSize * 2
        stdImg = cv2.drawFrameAxes(stdImg, cameraMatrix, distCoeffs, rvecs, tvecs, axis_length)

        stdImg = cv2.circle(stdImg, (int(corners[0][0][0]), int(corners[0][0][1])), 5, (0, 0, 255), -1)
        # print("原點像素位置:", corners[0][0])
        cv2.imshow('Image', stdImg)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return cameraMatrix, rvecs, tvecs