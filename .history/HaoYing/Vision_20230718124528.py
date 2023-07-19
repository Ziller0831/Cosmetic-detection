'''## * 物件邊緣檢測 Edge Detection
Python version: 3.9.13
openCV version: 4.6.0
numpy  version: 1.23.5
pandas version: 1.5.3
'''

import cv2
import FileProcess as FP
import numpy as np
import math

CsvDir = r"./HaoYing/Cosmetic_parameter.csv"

# ProductName = "透白口紅座"  # Input from UI


class EdgeDetector:
    def __init__(self, ModeSW = 0,  Product_name = "", TF_parm = ""):
        self.ModeSW = ModeSW

        ##* FPSBuffer Parameters
        Target_FPS = 10
        self._Data_buffer = [[]]

        if ModeSW == 0: ##% Working Mode
            _area_avg, _, _product_color, catch_offset, product_height =FP.CSVDataLoad(CsvDir, Product_name)

            ##* Coordinate transform parameters
            rvec_matrix, _ = cv2.Rodrigues(TF_parm["rvecs"])
            projection_matrix = np.dot(TF_parm["camera_matrix"], np.hstack((rvec_matrix, TF_parm["tvecs"])))
            self.pseudo_inverse_projection = np.linalg.pinv(projection_matrix)

            self._X_offset = 0
            self._Y_offset = 0
            self._Z_offset = product_height

            self.Area_range = [_area_avg-_area_avg*5, _area_avg+_area_avg*5]
            if   _product_color == '淺色': self.HSV_range = [np.array([180, 25, 255]),  np.array([0, 0, 155])]
            elif _product_color == '深色': self.HSV_range = [np.array([180, 255, 230]), np.array([0, 0, 154])]
            else: print('Error: No such product color')

            self.catchPoint = catch_offset

        elif ModeSW == 1: ##% EdgeAreaDetect mode
            self.Area_range = [500, 500000]
            self.HSV_range = [np.array([180, 25, 255]), np.array([0, 0, 155])]
    
    ##@ Camera catch
    def ImageCatch(self, cap):
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream  end?). Exiting ...")
            exit()
        return frame
    
    ##@ HSV binarization and morphology
    def ImagePreProcess(self, img_src):
        HSV_img = cv2.cvtColor(img_src, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(HSV_img, self.HSV_range[1], self.HSV_range[0])
        img_binary  = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
        # print(img_src.shape)
        return img_binary
    
    ##@ Fine contour and select
    def ContoursCalc(self, img_binary):
        contours = cv2.findContours(img_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
        contour_list = [contour for contour in contours if self.Area_range[0] <= cv2.contourArea(contour) <= self.Area_range[1]]
        return contour_list
        
    ##@ Calculate the contour feature
    def FeaturesCalc(self, frame, contour_list):
        arrow_length = 50
        minRect_array = []
        Result_array = []

        for contour in contour_list:

            moment = cv2.moments(contour)
            gravity_p = np.array(self._GPointCalc(moment))
            center_p, minRect, _ = self._MinRectCircle(contour)        
            minRect_array.append(minRect)

            if self.ModeSW != 2:

                _, deltaY = center_p - gravity_p
                angle = self._AngleCalc(minRect, deltaY)
                
                Result_array.append([center_p[0], center_p[1], round(angle, 4)])
            
                arrow_p = [int(center_p[0]+arrow_length*math.cos(math.radians(angle))), int(center_p[1]-arrow_length*math.sin(math.radians(angle)))]
                # CatchPoint = [int(center_p[0]+self.catchPoint*cos(radians(angle))), int(center_p[1]-self.catchPoint*sin(radians(angle)))]

                cv2.arrowedLine(frame, center_p, (arrow_p[0], arrow_p[1]), (255,100,0), 2)
                cv2.circle(frame, center_p, 5, (100,255,100), -1)
                cv2.circle(frame, gravity_p, 5, (0,0,255), -1)
                # cv2.circle(frame, CatchPoint, 5, (255,0,255), -1)

        if self.ModeSW != 2:
            cv2.drawContours(frame, contour_list, -1, (0,0,255), 2)

        for minRect in minRect_array:
            cv2.drawContours(frame, [minRect], 0, (0, 255, 0), 2)
        
        return frame, Result_array, minRect_array

    ##@ Calculate the contour gravity point
    def _GPointCalc(self, moment):
        return int(moment['m10']/moment['m00']), int(moment['m01']/moment['m00'])
    
    ##@ Contour's minimal rec
    def _MinRectCircle(self, contour):
        raw_MinRect = cv2.minAreaRect(contour)
        min_rect = np.int0(cv2.boxPoints(raw_MinRect))
        return np.int0(raw_MinRect[0]), min_rect, round(raw_MinRect[2], 4)
    
    ##@ 利用輪廓最小外矩形角度計算
    def _AngleCalc(self, minRect_P, deltaY):
        vector_a = minRect_P[1] - minRect_P[0]
        vector_b = [2] - minRect_P[1]

        vector_a_val = (vector_a[0]**2+vector_a[1]**2)**0.5
        vector_b_val = (vector_b[0]**2+vector_b[1]**2)**0.5

        if(vector_a_val < vector_b_val):
            vector = vector_a
        elif(vector_a_val > vector_b_val):
            vector = vector_b
        
        theta = cv2.fastAtan2(int(vector[0]), int(vector[1]))

        if deltaY < 0:
            return (theta + 180)%360
        else:
            return theta

    ##@ FPS緩衝器(用於讓數值穩定)
    def FPSBuffer(self, fps = 30, result_data = None):
        if self.Data_buffer:
            diff_buffer = len(self.Data_buffer) - int(fps//self.Target_FPS) + 1
            self.Data_buffer = self.Data_buffer[diff_buffer if diff_buffer >= 0 else 0:]
        
        self.Data_buffer.append(result_data)
        results_mean = np.mean(np.array(self.Data_buffer, dtype=object), axis=0)

        return results_mean

    ##@ Pixel coordinate transfer to world coordinate
    def Coordinate_TF(self, pixel_coordinate):
        homo2pixel = np.array([pixel_coordinate], dtype=np.float32).T
        homo2world = np.dot(self.pseudo_inverse_projection, homo2pixel)
        world_x = homo2world[0] / homo2world[3]
        world_y = homo2world[1] / homo2world[3]

        return world_x, world_y