import cv2
import numpy as np

class Image:
class EdgeDetector:
    def __init__(self,):
        pass
    
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
    
    def DeletContours(self, imgBinary):
        contoursList = []
        contours = cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        for contour in contours:
            contoursLength = cv2.arcLength(contour, True)
            if (contoursLength >= Contour_size[0]) and (contoursLength <= Contour_size[1]):
                contoursList.append(contour)
        return contoursList

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = EdgeDetector(np.array([[0, 0, 155],[180, 25, 255]]))
    while True:
        frame = W_lipstick.ImageCatch(cap)
        imgBinary = W_lipstick.ImagePreProcess(frame)
        cv2.imshow('binary', imgBinary)

        contours = W_lipstick

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break
    cv2.destroyAllWindows()