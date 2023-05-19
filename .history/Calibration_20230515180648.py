##* 相機標定
import numpy as np
import Vision
import cv2

MinRectArray = []

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = Vision.EdgeDetector(2)
    while True:
        frame = cosmetic.ImageCatch(cap)
        imgBinary = cosmetic.ImagePreProcess(frame)
        contoursList = cosmetic.ContoursCalc(imgBinary)

        for contour in contoursList:
            MinRectEdge = cosmetic.MinRectCircle(contour)
            MinRectArray.append(minRect)

        for minRect in MinRectArray:
            MinRectEdge = cv2.minAreaRect(contour)

        cv2.imshow("Result", frame)
        print("寬度：", MinRectEdge[1][0],end='\r')
        print("長度：", minRect[1][1],end='\r')

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break
cv2.destroyAllWindows()
