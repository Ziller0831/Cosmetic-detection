import Vision
import cv2
import numpy as np
import os

AreaSizeData = []

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cosmetic = Vision.EdgeDetector(0)

while True:
    frame = cosmetic.ImageCatch(cap)
    imgBinary = cosmetic.ImagePreProcess(frame)
    cv2.imshow("Binary", imgBinary)

    

    while len(AreaSizeData) < 100:
            
        contoursList = cosmetic.ContoursCalc(imgBinary)

        for contour in contoursList:
            if cv2.contourArea(contour) > 500:
                print(cv2.contourArea(contour))
                AreaSizeData.append(cv2.contourArea(contour))

        cv2.drawContours(frame, contoursList, -1, (0,0,255), 2)
        cv2.imshow("Result", frame)
        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break

areaMeanCont = np.mean(np.array(AreaSizeData, dtype=object))
areaStdCont = np.std(np.array(AreaSizeData,  dtype=float), axis=0, ddof=1)

print(f'Area: Mean\n{areaMeanCont:.4f},{areaStdCont:.4f}')

cv2.destroyAllWindows()