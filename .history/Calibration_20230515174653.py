##* 相機標定
import numpy as np
import Vision
import cv2

PatternSize = (6, 8)
Criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
ObjPoints = []
ImgPoints = []

ObjP = np.zeros((1, PatternSize[0]*PatternSize[1], 3), np.float32)
ObjP[0,:,:2] = np.mgrid[0:PatternSize[0], 0:PatternSize[1]].T.reshape(-1, 2)
PrevImgShape = None

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = Vision.EdgeDetector(0)
    while True:
        ret, frame = cap.read()
        if not ret: exit()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, PatternSize, cv2.CALIB_CB_ADAPTIVE_THRESH+
    	 cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
        
        if ret == True:
            ObjPoints.append(ObjP)
            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),Criteria)
            ImgPoints.append(corners2)
            img = cv2.drawChessboardCorners(img, PatternSize, corners2,ret)
        cv2.imshow('img', img)
        cv2.waitKey(0)

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break
cv2.destroyAllWindows()
