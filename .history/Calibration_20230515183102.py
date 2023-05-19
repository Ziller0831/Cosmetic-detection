##* 相機標定
import numpy as np
import Vision
import cv2

MinRectArray = []
TargetEdgeSize = [0.09, 0.09]  ##!0.09m

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = Vision.EdgeDetector(2)
    while True:
        frame = cosmetic.ImageCatch(cap)
        imgBinary = cosmetic.ImagePreProcess(frame)
        cv2.imshow("imgBinary", imgBinary)
        contoursList = cosmetic.ContoursCalc(imgBinary)

        for contour in contoursList:
            MinRectEdge = cosmetic.MinRectCircle(contour)

        frame, _, _ = cosmetic.FeaturesCalc(frame, contoursList)
        width = MinRectEdge[1][0]
        height = MinRectEdge[1][1]

        cv2.imshow("Result", frame)
        print(f'寬度：{width}, 長度：{height}', end='\r')

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break
cv2.destroyAllWindows()
