import cv2
import numpy as np
import glob
import HaoYing.Vision as Vision
import os


# @ 用於一開始的初始化
class initialize:
    def __init__(self):
        self._vision = Vision.EdgeDetector(0)
        self._CheckPoint = [[320, 240], [150, 110],
                            [150, 375], [475, 375], [475, 110]]
        self._TargetEdgeSize = 90

        self._Chessboard = (8, 5)
        self._Chessboard_squareSize = 20  # mm
        self._path = os.path.join(os.path.dirname(
            os.getcwd()), 'HaoYing0801', 'CalibrationImage')

    # @ 界定產品的輪廓面積範圍
    def AreaIdent(self):
        AreaSizeData = []
        for i, (x, y) in enumerate(self._CheckPoint):
            if cv2.waitKey(1) & 0xFF == 27:  # 27 = ESC
                break
            print('')

            while cv2.waitKey(1) & 0xFF != 13:
                frame = self._vision.ImageCatch()
                cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
                cv2.imshow("Image", frame)
                print('請換下個位置，放置後請按Q', end='\r')
            print('')
            for i in range(100):
                print(f'請勿進入鏡頭範圍，目前搜尋數據量:{i+1}', end='\r')
                frame = self._vision.ImageCatch()
                imgBinary = self._vision.ImagePreProcess(frame)
                contours = self._vision.ContoursCalc(imgBinary)
                for contour in contours:
                    if cv2.contourArea(contour) > 100:
                        AreaSizeData.append(cv2.contourArea(contour))

        areaMeanCont = np.mean(np.array(AreaSizeData, dtype=object))
        areaStdCont = np.std(
            np.array(AreaSizeData,  dtype=float), axis=0, ddof=1)
        return AreaSizeData, areaMeanCont, areaStdCont

    # @ 棋盤格截圖
    def _ChessboardCatch(self):
        _chessboard_path = os.path.join(self._path, 'chessboard')
        print(_chessboard_path)
        count = 0
        while count < 10:
            frame = self._vision.ImageCatch()
            cv2.imshow("Webcam", frame)
            print('將校正板放置在紅點處, 放置後請按Enter', end='\r')
            key = cv2.waitKey(1)
            if key == 13:
                cv2.imwrite(_chessboard_path + str(count)+'.png',
                            frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
                print(f"已拍攝並儲存照片 {count}")
                count += 1
            if cv2.waitKey(1) & 0xFF == 27:
                break
        cv2.destroyAllWindows()

    # @ 標定棋盤格截圖
    def _StandardCatch(self):
        while True:
            frame = self._vision.ImageCatch()
            cv2.imshow("Webcam", frame)
            print('將校正板放置在紅點處, 放置後請按Enter', end='\r')
            key = cv2.waitKey(1)
            if key == 13:
                cv2.imwrite(self._path+"Standard.png", frame)
                print("拍照完成")
                break
            if cv2.waitKey(1) & 0xFF == 27:  # 27 = ESC
                break
        cv2.destroyAllWindows()

    # @ 相機標定
    def CameraCalibration(self):
        objp = np.zeros((np.prod(self._Chessboard), 3), dtype=np.float32)
        objp[:, :2] = np.mgrid[0:self._Chessboard[0], 0:self._Chessboard[1]
                               ].T.reshape(-1, 2) * self._Chessboard_squareSize

        objpoints = []  # 物體座標
        imgpoints = []  # 影像座標

        self._ChessboardCatch()
        _chessboard_path = os.path.join(self._path, 'chessboard')
        image_paths = glob.glob(_chessboard_path+"*.png")

        for image_path in image_paths:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(
                gray, self._Chessboard, None)
            
            if ret == True:
                objpoints.append(objp)
                imgpoints.append(corners)
                cv2.drawChessboardCorners(img, self._Chessboard, corners, ret)
                cv2.imshow("Chessboard corners", img)
                cv2.waitKey(100)

        cv2.destroyAllWindows()

        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, gray.shape[::-1], None, None)
        print(f"Camera inner parameter: {camera_matrix}")
        print(f"Camera distortion parameter:{dist_coeffs}")

        # _standard_path = os.path.join(self._path, 'standard', 'Standard.png')
        self._StandardCatch()
        std_img = cv2.imread(self._path+"Standard.png")
        gray = cv2.cvtColor(std_img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, self._Chessboard, None)

        if ret == True:
            objpoints.append(objp)
            imgpoints.append(corners)

        _, rvecs, tvecs = cv2.solvePnP(
            objp, corners, camera_matrix, dist_coeffs)

        axis_length = self._Chessboard_squareSize * 2  # 座標軸的長度
        std_img = cv2.drawFrameAxes(
            std_img, camera_matrix, dist_coeffs, rvecs, tvecs, axis_length)

        std_img = cv2.circle(std_img, (int(corners[0][0][0]), int(
            corners[0][0][1])), 5, (0, 0, 255), -1)
        print("原點像素位置:", corners[0][0])
        cv2.imshow('Image', std_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return camera_matrix, rvecs, tvecs
