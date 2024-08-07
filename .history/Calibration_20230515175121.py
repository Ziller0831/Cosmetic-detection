##* 相機標定
import numpy as np
import Vision
import cv2

PatternSize = (6, 8)
Criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
ObjPoints = []
ImgPoints = []

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = Vision.EdgeDetector(0)
    while True:
        frame = cosmetic.ImageCatch(cap)
        imgBinary = cosmetic.ImagePreProcess(frame)
        contoursList = cosmetic.ContoursCalc(imgBinary)
        frame, _, MinRectArray = cosmetic.FeaturesCalc(frame, contoursList)

        cv2.drawContours(frame, contoursList, -1, (0,0,255), 2)


       

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break
cv2.destroyAllWindows()
