import cv2
import numpy as np
import pandas as pd

ProductName = '樣品蓋(長)'  # Input from UI
CsvDir = "Cosmetic_parameter.csv"

class ImageCalibration:
    def __init__(self):
        pass

class EdgeDetector:
    def __init__(self, ProductName = "", CsvDir=""):
        product_dic = pd.read_csv(CsvDir).to_dict()
        product_index = next((key for key,value in product_dic.get('產品名稱').items() if value == ProductName), None)
        length_Avg = product_dic.get('周長平均').get(product_index)
        length_Std = product_dic.get('周常標準差').get(product_index)
        area_Avg = product_dic.get('面積平均').get(product_index)
        area_Std = product_dic.get('面積標準差').get(product_index)
        product_color = product_dic.get('產品顏色').get(product_index)

        length_range = [length_Avg+length_Std*3, length_Avg-length_Std*3] #[Max length, Min length]
        area_range = [area_Avg+area_Std*3, area_Avg-area_Std*3] #[Max area, Min area]
        if product_color == '淺色': HSV_range = [[180, 25, 255], [0, 0, 155]]
        elif product_color == '深色': HSV_range = [[180, 255, 230], [0, 0, 154]]
        else: print('Error: No such product color')
    
    def ImageCatch(self, cap):
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream  end?). Exiting ...")
            exit()
        return frame

    def ImagePreProcess(self, img_src):
        HSV_img = cv2.cvtColor(img_src, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(HSV_img, self.HSV_range, self.HSV_range)
        binary  = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
        return binary
    
    def DeletContours(self, imgBinary):
        contours = cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
        contoursList = [contour for contour in contours if self.length_range[0] <= cv2.arcLength(contour, True) <= self.length_range[1]]
        return contoursList

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = EdgeDetector("")
    while True:
        frame = cosmetic.ImageCatch(cap)
        imgBinary = cosmetic.ImagePreProcess(frame)
        cv2.imshow('binary', imgBinary)

        # contours = cosmetic.DeletContours(imgBinary)

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break
    cv2.destroyAllWindows()