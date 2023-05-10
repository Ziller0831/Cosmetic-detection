import Vision
import cv2
import numpy as np
import os

AreaSizeData = []
CheckPoint = [[320,240], [150,110], [150,375], [475,110], [475,110]]

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cosmetic = Vision.EdgeDetector(0)

for i, (x, y) in enumerate(CheckPoint):
    if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
        break
    
    while cv2.waitKey(1) & 0xFF != ord('q'):
        frame = cosmetic.ImageCatch(cap)
        cv2.circle(frame, (x, y), 5, (0,0,255), -1)
        cv2.imshow("Image", frame)
        print('請換下個位置，放置後請按Q',end='\r')
    
    while len(AreaSizeData) < 100:
        frame = cosmetic.ImageCatch(cap)
        imgBinary = cosmetic.ImagePreProcess(frame)
        contoursList = cosmetic.ContoursCalc(imgBinary)

        for contour in contoursList:
            if cv2.contourArea(contour) > 100:
                print(cv2.contourArea(contour))
                AreaSizeData.append(cv2.contourArea(contour))

        cv2.drawContours(frame, contoursList, -1, (0,0,255), 2)
        cv2.imshow("Result", frame)
        cv2.waitKey(1)

areaMeanCont = np.mean(np.array(AreaSizeData, dtype=object))
areaStdCont = np.std(np.array(AreaSizeData,  dtype=float), axis=0, ddof=1)

print(f'Area: Mean\n{areaMeanCont:.4f},{areaStdCont:.4f}')

cv2.destroyAllWindows()