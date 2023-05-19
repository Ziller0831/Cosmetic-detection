##* 相機標定
import numpy as np
import Vision
import cv2

MinRectArray = []
TargetEdgeSize = [0.09, 0.09]  ##! 0.09m
Width = []
Height = []

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = Vision.EdgeDetector(2)
    while True:
        frame = cosmetic.ImageCatch(cap)
        imgBinary = cosmetic.ImagePreProcess(frame)
        contoursList = cosmetic.ContoursCalc(imgBinary)

        # for contour in contoursList:
        #     if cv2.contourArea(contour) > 100:
        #         Width.append(np.amax(cosmetic.MinRectCircle(contour)[1]))
        #         Height.append(np.amin(cosmetic.MinRectCircle(contour)[1]))
    widthMean = np.mean(np.array(Width, dtype=object))
    heightMean = np.mean(np.array(Height, dtype=object))
    print(f"Width:{widthMean},Height:{heightMean}")
    
cv2.destroyAllWindows()
