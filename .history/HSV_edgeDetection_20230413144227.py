import cv2
import numpy as np

def nothing(x):
    pass

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

maxVal = 255

def contourSearch(ImgName, imgSource, contours, DrawOnBlack):
    if(DrawOnBlack):
        temp - np.ones(imgSource.shape, dtype=np.uint8) * 255
        cv2.drawContours(temp, contours, -1, (0, 0, 0)



while 1:
    ret, frame = cap.read()
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    cv2.imshow("gray", img)

    # img = cv2.GaussianBlur(img, (3, 3), 1)
    ret, binary = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY_INV)




    # cv2.imshow("0", frame)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()