'''
********************************
    HaoYing 變數儲存 副程式
********************************
'''

import os
import cv2
import glob
import numpy as np
import HaoYing.Vision as Vision
import HaoYing.FileProcess as FP


##@ 初始化
class initialize:
    def __init__(self, object, csvPath):
        objectData = FP.CSVDataLoad(csvPath, object)
        self._vision = Vision.EdgeDetector(0, Product_features = objectData)
        self._CheckPoint = [[320,240], [150,110], [150,375], [475,375], [475,110]]  # 顯示在畫面的紅點座標
        self._wordColor = (0, 255, 255)    # 字的顏色
        self._position = (0, 20)           # 字的位置

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
                cv2.rectangle(frame, (0,0), (655,25), (0,0,0), cv2.FILLED)
                cv2.putText(frame, text, self._position, cv2.FONT_HERSHEY_COMPLEX_SMALL,1,self._wordColor,1)
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

        
        cv2.drawContours(frame, contours, -1, (0,0,255), 2)
        cv2.waitKey(1)

        areaMeanCont = np.mean(np.array(AreaSizeData, dtype=object))
        areaStdCont  = np.std(np.array(AreaSizeData,  dtype=float), axis=0, ddof=1)

        return _, areaMeanCont, areaStdCont

    ##@ 棋盤格截圖
    def _ChessboardCatch(self, cap):
        os.chdir("C:/Users/TEST/Desktop/HaoYing_Final/ObjectVision/CalibrationImage")
        # print(_chessboard_path)
        count = 0
        while count < 15:
            frame = self._vision.ImageCatch()
            text = f'Place the Calibration board and press Enter({count}/15)'
            cv2.rectangle(frame, (0,0), (655,25), (0,0,0), cv2.FILLED)
            cv2.putText(frame, text, self._position, cv2.FONT_HERSHEY_COMPLEX_SMALL,1,self._wordColor,1)
            cv2.imshow("Calibration", frame)
            if cv2.waitKey(1) & 0xFF == 13:
                frame = self._vision.ImageCatch()
                cv2.imwrite(str(count)+'.png', frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
                count += 1
            if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
                break
        cv2.destroyAllWindows()

    
    def _StandardCatch(self, cap):
        os.chdir("C:/Users/TEST/Desktop/HaoYing_Final/ObjectVision")
        while True:
            frame = self._vision.ImageCatch()
            text = 'Place the Calibration board and press Enter'
            cv2.rectangle(frame, (0,0), (655,25), (0,0,0), cv2.FILLED)
            cv2.putText(frame, text, self._position, cv2.FONT_HERSHEY_COMPLEX_SMALL,1,self._wordColor,1)
            cv2.imshow("Standard", frame)
            if  cv2.waitKey(1) & 0xFF == 13:
                frame = self._vision.ImageCatch()
                cv2.imwrite("Standard.png", frame)
                break
            if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
                break

        cv2.destroyAllWindows()

    
    def CameraCalibration(self, cap):
        """
        ##@ 相機標定
        """
        objp = np.zeros((np.prod(self._Chessboard), 3), dtype=np.float32)
        objp[:, :2] = np.mgrid[0:self._Chessboard[0], 0:self._Chessboard[1]].T.reshape(-1, 2) * self._Chessboard_squareSize

        objpoints = []  # 物體座標
        imgpoints = []  # 影像座標

        
        self._ChessboardCatch(cap)
        os.chdir("C:/Users/TEST/Desktop/HaoYing_Final/ObjectVision/")
        image_paths = glob.glob("CalibrationImage/*.png")

        for image_path in image_paths:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, self._Chessboard, None)
            if ret == True:
                objpoints.append(objp)
                imgpoints.append(corners)

                cv2.drawChessboardCorners(img, self._Chessboard, corners, ret)
                cv2.imshow("Chessboard corners", img)
                cv2.waitKey(100)

        cv2.destroyAllWindows()

        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        print(f"Camera inner parameter: {camera_matrix}")
        print(f"Camera distortion parameter:{dist_coeffs}")

        # _standard_path = os.path.join(self._path, 'standard', 'Standard.png')
        self._StandardCatch(cap)
        std_img = cv2.imread("Standard.png")
        gray = cv2.cvtColor(std_img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, self._Chessboard, None)

        if ret == True:
            objpoints.append(objp)
            imgpoints.append(corners)
        
        _, rvecs, tvecs = cv2.solvePnP(objp, corners, camera_matrix, dist_coeffs)

        axis_length = self._Chessboard_squareSize * 2  # 座標軸的長度
        std_img = cv2.drawFrameAxes(std_img, camera_matrix, dist_coeffs, rvecs, tvecs, axis_length)

        std_img = cv2.circle(std_img, (int(corners[0][0][0]), int(corners[0][0][1])), 5, (0, 0, 255), -1)
        # print("原點像素位置:", corners[0][0])
        cv2.imshow('Image', std_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return camera_matrix, rvecs, tvecs