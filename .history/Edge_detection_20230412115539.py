### 門檻值設定與過濾 ###
import cv2
import numpy as np

def nothing(x): # 數值調整迴圈
    pass

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

maxGrayVal = 255

cv2.namedWindow('Setting')  # 命名視窗名稱
cv2.createTrackbar('Gray', 'Setting', maxGrayVal//2, maxGrayVal, nothing)   # 建立數值設定條


while 1:
    ret, frame = cap.read()
    b, g, r = cv2.split(frame)
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # th_val = cv2.getTrackbarPos('Gray', 'Setting')

    retval, r = cv2.threshold(r, 0, 255, cv2.THRESH_OTSU)
    retval, g = cv2.threshold(g, 0, 255, cv2.THRESH_OTSU)
    retval, b = cv2.threshold(b, 0, 255, cv2.THRESH_OTSU)
    
    result = np.hstack([image, r])

    cv2.imshow('Setting', result)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()