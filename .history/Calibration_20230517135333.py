##* 相機標定
import numpy as np
import Vision
import cv2
from math import sqrt

MinRectArray = []
TargetEdgeSize = [90, 90]  ##! 90mm
Width = []
Height = []
count = 0

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = Vision.EdgeDetector(2)
    while True:
        frame = vision.ImageCatch(cap)
        imgBinary = vision.ImagePreProcess(frame)
        contoursList = vision.ContoursCalc(imgBinary)
        cv2.imshow("imgBinary", imgBinary)
        cv2.waitKey(1)
        for contour in contoursList:
            if cv2.contourArea(contour) > 100:
                corners = vision.MinRectCircle(contour)[1]
                Width.append(sqrt((corners[1][0] - corners[0][0])**2 + (corners[1][1] - corners[0][1])**2))
                Height.append(sqrt((corners[3][0] - corners[0][0])**2 + (corners[3][1] - corners[0][1])**2))
        count = count + 1
        if count == 100 or cv2.waitKey(1) & 0xFF == 27:
            break
    widthScale = TargetEdgeSize[0] / np.mean(np.array(Width, dtype=object))
    heightScale = TargetEdgeSize[1] / np.mean(np.array(Height, dtype=object))
    print(f"Width:{widthScale:.4f},Height:{heightScale:.4f}")
    
cv2.destroyAllWindows()
