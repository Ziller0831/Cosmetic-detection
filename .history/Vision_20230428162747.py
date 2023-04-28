import cv2
import numpy as np

class VisionData:
    def __init__(self, HSV_values):
        self.WorkMode = []
        self.LowerValue = HSV_values[0]
        self.UpperValue = HSV_values[1]
    
    def ImageCatch(self, cap):
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream  end?). Exiting ...")
        else:
            return frame


    def ImagePreProcess(self, img_src):
        HSV_img = cv2.cvtColor(img_src, cv2.COLOR_BGR2HSV)
        HSV_img = cv2.GaussianBlur(HSV_img, (3, 3), 1)
        mask = cv2.inRange(HSV_img, self.LowerValue, self.UpperValue)
        element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary  = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, element)
        return binary
    

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    HSV_value = np.array([0, 0, 155],[180, 25, 255])
    W_lipstick = VisionData()
    while True:
        frame = W_lipstick.ImageCatch(cap)
        imgBinary = W_lipstick.ImagePreProcess(frame)
        cv2.imshow('binary', imgBinary)
    