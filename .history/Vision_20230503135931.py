import cv2
import numpy as np

class ImageCalibration:
    def __init__(self):
        pass

class EdgeDetector:
    def __init__(self):
        pass
    
    def ImageCatch(self, cap):
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream  end?). Exiting ...")
            exit()
        return frame

    def ImagePreProcess(self, img_src):
        HSV_img = cv2.cvtColor(img_src, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(HSV_img, self.LowerValue, self.UpperValue)
        binary  = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
        return binary
    
    def DeletContours(self, imgBinary):
        contours = cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
        contoursList = [contour for contour in contours if Contour_size[0] <= cv2.arcLength
        return contoursList

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = EdgeDetector(np.array([[0, 0, 155],[180, 25, 255]]))
    while True:
        frame = cosmetic.ImageCatch(cap)
        imgBinary = cosmetic.ImagePreProcess(frame)
        cv2.imshow('binary', imgBinary)

        contours = cosmetic

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break
    cv2.destroyAllWindows()