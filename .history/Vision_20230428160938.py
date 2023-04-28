import cv2
import numpy as np

class VisionData:
    def __init__(self, Lower, Upper):
        self.WorkMode = []
        self.LowerValue = Lower
        self.UpperValue = Upper

    def ImagePreProcess(self, img_src):
        HSV_img = cv2.cvtColor(img_src, cv2.COLOR_BGR2HSV)
        HSV_img = cv2.GaussianBlur(HSV_img, (3, 3), 1)
        w_mask = cv2.inRange(HSV_img, self.LowerValue[0], WhiteUpper[1])
        outputImg = cv2.bitwise_or(w_mask, b_mask)
        element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary  = cv2.morphologyEx(outputImg, cv2.MORPH_CLOSE, element)
        return binary
    

if __name__ == '__main__':
    while True:
            
    