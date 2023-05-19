##* 相機標定
import numpy as np
import Vision
import cv2

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = Vision.EdgeDetector(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream  end?). Exiting ...")
            exit()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR
        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break
cv2.destroyAllWindows()