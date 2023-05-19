##* 相機標定
import numpy as np
import Vision
import cv2
import V

PatternSize = (6, 8)
Criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
ObjPoints = []
ImgPoints = []

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = Vision.EdgeDetector(0)
    while True:
        ret, frame = cap.read()
        if not ret: exit()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


        cv2.imshow("Gray", gray)

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break
cv2.destroyAllWindows()
