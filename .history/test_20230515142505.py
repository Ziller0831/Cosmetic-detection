#* 物件邊緣檢測 Edge Detection

import Vision
import cv2

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = Vision.EdgeDetector(0)
    while True:
        frame = cosmetic.ImageCatch(cap)
        imgBinary = cosmetic.ImagePreProcess(frame)
        cv2.imshow('binary', imgBinary)

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break
cv2.destroyAllWindows()