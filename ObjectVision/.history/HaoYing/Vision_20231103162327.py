'''
********************************
    物件邊緣檢測 Edge Detection
********************************
負責整套程式中的影像處理, 物件篩選與座標轉換的部分

架構：
    class EdgeDetector:
    | 
    +-- def __init__(self, 物件名稱, CSV檔位置)
    |
    +-- def ImageCatch(self)
    |       return 影像
    |
    +-- def ImagePreProcess(self, 影像)
    |       return 二值化影像
    |
    +-- def ContoursCalc(self, 二值化影像):
    |       return 輪廓陣列
    |
    +-- def FeaturesCalc(self, 影像, 輪廓陣列)
    |       return 影像, 輪廓特徵陣列
    |
    +-- def _GPointCalc(self, 輪廓矩)
    |       return 重心X座標, 重心Y座標
    |
    +-- def _MinRectCircle(self, 輪廓)
    |       return 外矩形中點, 外矩形角點陣列
    |
    +-- def _AngleCalc(self, 外矩形角點陣列, 重心到中心向量)
    |       return 物件角度
    |
    +-- def Coordinate_TF(self, 像素X座標, 像素Y座標)
    |       return 世界系X座標, 世界系Y座標, 世界系Z座標
'''

import cv2
import os
import numpy as np
import math
import csv



class EdgeDetector:
    def __init__(self, ModeSW = 2, TF_parm = "", *ProductFeatures):

        ##! 請記得路徑是否正確
        # CurrentDir = "C:\\Users\\jcyu\\Documents\\GitHub\\OpenCV-image-process-test\\ObjectVision\\HaoYing"
        CurrentDir = os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        Camera2Robot_coord =  os.path.abspath(os.path.join(CurrentDir, "..\\Data\\Camera_to_Robot.csv"))
        
        ##* 載入產品參數
        _areaAvg       = ProductFeatures[0][0]
        _areaStd       = ProductFeatures[0][1]
        _productColor  = ProductFeatures[0][2]
        _catchOffset   = ProductFeatures[0][3]
        self._productHeight = ProductFeatures[0][4]

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        ##* 相機參數調整
        if   _productColor  == '深色':  ##* 深色物件淺色背景
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 220)  ##* 亮度調整
            self.cap.set(cv2.CAP_PROP_CONTRAST, 60)     ##* 對比調整
        elif _productColor  == '淺色':  ##* 淺色物件深色背景
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 140)
            self.cap.set(cv2.CAP_PROP_CONTRAST, 40)

        if not self.cap.isOpened():
            print("無法打開相機")

        self._modeSW = ModeSW
        ##% Working Mode
        if ModeSW == 2: 
            ##* Pixel2Camera parameters
            rvecMatrix, _ = cv2.Rodrigues(TF_parm["rvecs"])
            projectionMatrix = np.dot(TF_parm["camera_matrix"], np.hstack((rvecMatrix, TF_parm["tvecs"])))
            self.pseudoInverseProjection = np.linalg.pinv(projectionMatrix)

            ##* Camera2Robot Transform
            with open(Camera2Robot_coord) as CR_csv:
                CRList = list(csv.reader(CR_csv))
            self._X_offset = float(CRList[0][0])
            self._Y_offset = float(CRList[0][1])
            #
            # self._Z_offset = -538  ## 固定式吸盤的吸取高度 
            self._Z_offset = -475   ## 90度旋轉吸盤的吸取高度

            ##* HSV參數調整(視二值化效果而定)
            if   _productColor == '淺色': self.HSV_range = [np.array([180, 25, 255]),  np.array([0, 0, 155])]
            elif _productColor == '深色': self.HSV_range = [np.array([180, 25, 255]),  np.array([0, 0, 155])]
            else: print('Error: No such product color')

            ##* 輪廓面積界定
            self._AreaRange = [_areaAvg-_areaStd*2, _areaAvg+_areaStd*2]
            self.catchPoint = _catchOffset

            # print(self._AreaRange)

        elif ModeSW == 0: ##% Initialization mode
            self._AreaRange = [500, 10000]
            self.HSV_range   = [np.array([180, 25, 255]),  np.array([0, 0, 155])]

    
    ##@ Image catch
    def ImageCatch(self):
        ret, frame = self.cap.read()
        if not ret:
            print("無法讀取相機影像")
            return
        return frame
    ##@ -----------------------------------------------------

    ##@ HSV binarization and morphology
    def ImagePreProcess(self, imgSrc):
        HSV_img = cv2.cvtColor(imgSrc, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(HSV_img, self.HSV_range[1], self.HSV_range[0])
        imgBinary  = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        imgBinary = cv2.medianBlur(imgBinary, 5)
        return imgBinary
    ##@ -----------------------------------------------------

    ##@ Fine object contour and Filter
    def ContoursCalc(self, imgBinary):
        contours = cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
        contours = [contour for contour in contours if self._AreaRange[0] <= cv2.contourArea(contour) <= self._AreaRange[1]]
        return contours
    ##@ -----------------------------------------------------

    ##@ Calculate the contour feature
    def FeaturesCalc(self, frame, contours):
        minRectArray = []   ##* minimum rectangle array
        featuresArray  = []   ##* Output array(catch point[x, y], angle)

        for contour in contours:
            moment = cv2.moments(contour)
            gravity_p = np.array(self._GPointCalc(moment))
            center_p, minRect  = self._MinRectCircle(contour)  

            ##* 顯示輪廓最小外矩形邊的鄰近3點
            # cv2.circle(frame, minRect[0], 3, (100,100,255), 2)
            # cv2.circle(frame, minRect[1], 3, (150,50,200), 2)
            # cv2.circle(frame, minRect[2], 3, (80,255,90), 2)

            if self._modeSW == 2:
                G2C_vect = gravity_p - center_p  ##* Gravity to Center vector
                
                angle = self._AngleCalc(minRect, G2C_vect)
                catch_p = [int(center_p[0]+self.catchPoint*math.cos(math.radians(angle))), int(center_p[1]-self.catchPoint*math.sin(math.radians(angle)))]
                featuresArray.append([catch_p[0], catch_p[1], round(angle, 4)])
                cv2.circle(frame, catch_p, 5, (255,100,255), -1)


        cv2.drawContours(frame, contours, -1, (0,0,255), 2)

        for minRect in minRectArray:
            cv2.drawContours(frame, [minRect], 0, (0, 255, 0), 2)

        
        return frame, featuresArray
    ##@ -----------------------------------------------------

    ##@ Calculate the contour gravity point
    def _GPointCalc(self, moment):
        try:
            return int(moment['m10']/moment['m00']), int(moment['m01']/moment['m00'])
        except: 
            return 1
    ##@ -----------------------------------------------------
    
    ##@ Contour's minimal rectangle
    def _MinRectCircle(self, contour):
        rawMinRect = cv2.minAreaRect(contour)
        minRect = np.int0(cv2.boxPoints(rawMinRect))
        return np.int0(rawMinRect[0]), minRect
    ##@ -----------------------------------------------------
    
    ##@ 使用輪廓最小外矩形邊上的三個端點組合出向量再判斷物件方向與角度
    def _AngleCalc(self, minRect_P, G2C_vect):
        vect_a = minRect_P[1] - minRect_P[0]
        vect_b = minRect_P[2] - minRect_P[1]

        vect_a_val = (vect_a[0]**2+vect_a[1]**2)**0.5
        vect_b_val = (vect_b[0]**2+vect_b[1]**2)**0.5

        if(vect_a_val < vect_b_val):
            shortVect = np.array(vect_a)
            longVect = np.array(vect_b)
            vectVal = vect_b_val
        elif(vect_a_val > vect_b_val):
            shortVect = np.array(vect_b)
            longVect = np.array(vect_a)
            vectVal = vect_a_val
        else:
            return 90

        vect_GC_val = (G2C_vect[0]**2 + G2C_vect[1]**2)**0.5
        longG_C_cos = longVect @ G2C_vect / (vectVal * vect_GC_val)

        theta = cv2.fastAtan2(int(shortVect[0]), int(shortVect[1]))

        if longG_C_cos < 0 and longG_C_cos >= -1 and theta <= 90 and theta >= 0:     ##* 第三象限反轉
            shortVect = np.array([-shortVect[0], -shortVect[1]])
            theta = cv2.fastAtan2(int(shortVect[0]), int(shortVect[1]))
        elif longG_C_cos > 0 and longG_C_cos <= 1 and theta <= 180 and theta >= 90:  ##* 第四象限反轉
            shortVect = np.array([-shortVect[0], -shortVect[1]])
            theta = cv2.fastAtan2(int(shortVect[0]), int(shortVect[1]))
        
        return theta
    ##@ -----------------------------------------------------

    ##@ Pixel coordinate transfer to world coordinate
    def Coordinate_TF(self, pixel_x, pixel_y):
        homo2pixel = np.array([pixel_x, pixel_y, 1], dtype=np.float32).T
        world2homo = np.dot(self.pseudoInverseProjection, homo2pixel)
        world_x = self._X_offset + (world2homo[0] / world2homo[3])
        world_y = self._Y_offset - (world2homo[1] / world2homo[3]) 
        world_z = self._Z_offset + self._productHeight
        
        return world_x, world_y, world_z
    ##@ -----------------------------------------------------