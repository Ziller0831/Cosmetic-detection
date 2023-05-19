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
        cv2.imshow("imgBinary", imgBinary)
        contoursList = cosmetic.ContoursCalc(imgBinary)

        for contour in contoursList:
            MinRectEdge = cosmetic.MinRectCircle(contour)

        frame, _, _ = cosmetic.FeaturesCalc(frame, contoursList)
        width = MinRectEdge.width

        cv2.imshow("Result", frame)
        print(MinRectEdge[1][0])
        # print(f'寬度：{MinRectEdge[1][0]}, 長度：{MinRectEdge[1][1]}', end='\r')

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break
cv2.destroyAllWindows()
