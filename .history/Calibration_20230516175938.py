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
        frame = cosmetic.ImageCatch(cap)
        imgBinary = cosmetic.ImagePreProcess(frame)
        contoursList = cosmetic.ContoursCalc(imgBinary)
        cv2.imshow("imgBinary", imgBinary)
        cv2.waitKey(1)
        for contour in contoursList:
            if cv2.contourArea(contour) > 100:
                corners = cosmetic.MinRectCircle(contour)[1]
                Width.append(sqrt((corners[1][0] - corners[0][0])**2 + (corners[1][1] - corners[0][1])**2))
                Height.append(sqrt((corners[3][0] - corners[0][0])**2 + (corners[3][1] - corners[0][1])**2))
        count = count + 1
        if count == 100 or cv2.waitKey(1) & 0xFF == 27:
            break
    witdthScale = TargetEdgeSize[0] / np.mean(np.array(Width, dtype=object))
    witdthScale = TargetEdgeSize[1] / np.mean(np.array(Height, dtype=object))
    print(f"Width:{widthMean:.4f},Height:{heightMean:.4f}")
    
cv2.destroyAllWindows()
