import Vision
import cv2
import numpy as np

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cosmetic = Vision.EdgeDetector()

    while True:
        frame = cosmetic.ImageCatch(cap)
        imgBinary = cosmetic.ImagePreProcess(frame)
        # cv2.imshow('binary', imgBinary)

        contoursList = cosmetic.ContoursCalc(imgBinary)
        frame, ResultArray, MinRectArray = cosmetic.FeaturesCalc(frame, contoursList)

        cv2.drawContours(frame, contoursList, -1, (0,0,255), 2)
        for minRect in MinRectArray:
            cv2.drawContours(frame, [minRect], 0, (0, 255, 0), 2) # print(minRect)
        cv2.drawContours(frame, contoursList,-1, (255,0,0), 2)

        cv2.imshow("Result", frame)

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break
    cv2.destroyAllWindows()
