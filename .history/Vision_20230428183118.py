import cv2
import numpy as np

class ImageCalibration:
    def __init__(self):
        pass

z
if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = EdgeDetector(np.array([[0, 0, 155],[180, 25, 255]]))
    while True:
        frame = W_lipstick.ImageCatch(cap)
        imgBinary = W_lipstick.ImagePreProcess(frame)
        cv2.imshow('binary', imgBinary)

        contours = W_lipstick

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break
    cv2.destroyAllWindows()