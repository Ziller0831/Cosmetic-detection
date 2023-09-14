'''
********************************
HaoYing 物件邊緣檢測 Edge Detection
********************************
'''

import cv2
import os
import numpy as np
import math
import csv

CurrentDir = os.getcwd()
Camera2Robot_coord = os.path.join(CurrentDir, "./Data/Camera_to_Robot.csv")


class EdgeDetector:
    def __init__(self, ModeSW = 2, TF_parm = "", *Product_features):
        _area_avg       = Product_features[0][0]
        _area_Std       = Product_features[0][1]
        _product_color  = Product_features[0][2]
        self._catch_offset   = Product_features[0][3]
        self._product_height = Product_features[0][4]

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        if   _product_color  == '深色':
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 220)
            self.cap.set(cv2.CAP_PROP_CONTRAST, 60)
        elif _product_color  == '淺色':
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 140)
            self.cap.set(cv2.CAP_PROP_CONTRAST, 40)

        if not self.cap.isOpened():
            print("無法打開相機")

        self._modeSW = ModeSW

        ##% Working Mode
        if ModeSW == 2: 
            ##* Pixel2Camera parameters
            rvecMatrix, _ = cv2.Rodrigues(TF_parm["rvecs"])
            projection_matrix = np.dot(TF_parm["camera_matrix"], np.hstack((rvec_matrix, TF_parm["tvecs"])))
            self.pseudo_inverse_projection = np.linalg.pinv(projection_matrix)

            ##* Camera2Robot Transform
            with open(Camera2Robot_coord) as CR_csv:
                CRList = list(csv.reader(CR_csv))
            
            self._X_offset = float(CRList[0][0])
            self._Y_offset = float(CRList[0][1])
            self._Z_offset = -538

            self._Area_range = [_area_avg-_area_Std*3, _area_avg+_area_Std*3]

            if   _product_color == '淺色': self.HSV_range = [np.array([180, 25, 255]),  np.array([0, 0, 155])]
            elif _product_color == '深色': self.HSV_range = [np.array([180, 25, 255]),  np.array([0, 0, 155])]
            else: print('Error: No such product color')

            self.catchPoint = self._catch_offset

        elif ModeSW == 0: ##% EdgeAreaDetect mode
            self._Area_range = [500, 10000]
            self.HSV_range   = [np.array([180, 25, 255]),  np.array([0, 0, 155])]
            # self.HSV_range = [np.array([180, 255, 230]), np.array([0, 0, 154])]
    
    ##@ Image catch
    def ImageCatch(self):
        ret, frame = self.cap.read()
        if not ret:
            print("無法讀取相機影像")
            return
        return frame


    ##@ HSV binarization and morphology
    def ImagePreProcess(self, img_src):
        HSV_img = cv2.cvtColor(img_src, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(HSV_img, self.HSV_range[1], self.HSV_range[0])
        img_binary  = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        img_binary = cv2.medianBlur(img_binary, 5)
        return img_binary
    
    ##@ Fine contour and select
    def ContoursCalc(self, img_binary):
        contours = cv2.findContours(img_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
        contours = [contour for contour in contours if self._Area_range[0] <= cv2.contourArea(contour) <= self._Area_range[1]]
        return contours
        
    ##@ Calculate the contour feature
    def FeaturesCalc(self, frame, contours):
        minRect_array = []
        result_array  = []

        for contour in contours:
            print(cv2.contourArea(contour))
            moment = cv2.moments(contour)
            gravity_p = np.array(self._GPointCalc(moment))
            center_p, minRect, _ = self._MinRectCircle(contour)        
            minRect_array.append(minRect)

            cv2.circle(frame, minRect[0], 3, (100,100,255), 2)
            cv2.circle(frame, minRect[1], 3, (150,50,200), 2)
            cv2.circle(frame, minRect[2], 3, (80,255,90), 2)

            if self._modeSW == 2:
                GC_vect = gravity_p - center_p
                
                try:
                    angle = self._AngleCalc(minRect, GC_vect)
                    catch_p = [int(center_p[0]+self.catchPoint*math.cos(math.radians(angle))), int(center_p[1]-self.catchPoint*math.sin(math.radians(angle)))]
                    # cv2.arrowedLine(frame, center_p, (catch_p[0], catch_p[1]), (255,100,0), 2)
                    result_array.append([catch_p[0], catch_p[1], round(angle, 4)])
                except:
                    pass
                # cv2.circle(frame, center_p, 5, (100,255,100), -1)
                # cv2.circle(frame, gravity_p, 5, (0,0,255), -1)
                cv2.circle(frame, catch_p, 5, (255,100,255), -1)

        if self._modeSW != 2:
            cv2.drawContours(frame, contours, -1, (0,0,255), 2)

        for minRect in minRect_array:
            cv2.drawContours(frame, [minRect], 0, (0, 255, 0), 2)
        
        return frame, result_array, minRect_array

    ##@ Calculate the contour gravity point
    def _GPointCalc(self, moment):
        try:
            return int(moment['m10']/moment['m00']), int(moment['m01']/moment['m00'])
        except:
            return 1

    ##@ Contour's minimal rectangle
    def _MinRectCircle(self, contour):
        raw_MinRect = cv2.minAreaRect(contour)
        min_rect = np.int0(cv2.boxPoints(raw_MinRect))
        return np.int0(raw_MinRect[0]), min_rect, round(raw_MinRect[2], 4)
    
    ##@ Use minimal rectangle point to calculate the object angle
    def _AngleCalc(self, minRect_P, GC_vect):
        vect_a = minRect_P[1] - minRect_P[0]
        vect_b = minRect_P[2] - minRect_P[1]

        vect_a_val = (vect_a[0]**2+vect_a[1]**2)**0.5
        vect_b_val = (vect_b[0]**2+vect_b[1]**2)**0.5

        if(vect_a_val < vect_b_val):
            short_vect = np.array(vect_a)
            long_vect = np.array(vect_b)
            vect_val = vect_b_val
        elif(vect_a_val > vect_b_val):
            short_vect = np.array(vect_b)
            long_vect = np.array(vect_a)
            vect_val = vect_a_val

        vect_GC_val = (GC_vect[0]**2 + GC_vect[1]**2)**0.5
        longG_C_cos = long_vect @ GC_vect / (vect_val * vect_GC_val)

        theta = cv2.fastAtan2(int(short_vect[0]), int(short_vect[1]))

        if longG_C_cos < 0 and longG_C_cos >= -1 and theta <= 90 and theta >= 0: ## 第三象限反轉
            short_vect = np.array([-short_vect[0], -short_vect[1]])
            theta = cv2.fastAtan2(int(short_vect[0]), int(short_vect[1]))
        elif longG_C_cos > 0 and longG_C_cos <= 1 and theta <= 180 and theta >= 90:  ## 第四象限反轉
            short_vect = np.array([-short_vect[0], -short_vect[1]])
            theta = cv2.fastAtan2(int(short_vect[0]), int(short_vect[1]))
        else:
            pass
        
        return theta

    ##@ Pixel coordinate transfer to world coordinate
    def Coordinate_TF(self, pixel_x, pixel_y):
        homo2pixel = np.array([pixel_x, pixel_y, 1], dtype=np.float32).T
        world2homo = np.dot(self.pseudo_inverse_projection, homo2pixel)
        world_x = self._X_offset + (world2homo[0] / world2homo[3])
        world_y = self._Y_offset - (world2homo[1] / world2homo[3]) 
        world_z = self._Z_offset + self._product_height
        #world_z = -441 #-475
        
        return world_x, world_y, world_z