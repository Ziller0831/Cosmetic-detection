### 門檻值設定與過濾 ###
import cv2
import numpy as np

def nothing(x): # 數值調整迴圈
    pass

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

maxVal = 255

cv2.namedWindow('Setting')  # 命名視窗名稱
cv2.createTrackbar('Gray', 'Setting', maxVal//2, maxVal, nothing)   # 建立數值設定條


while 1:
    ret, frame = cap.read()
    BIamge, GIamge, RImage = cv2.split(frame)
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    th_val = cv2.getTrackbarPos('Red', 'Setting')

    retval, r = cv2.threshold(RImage, 0, maxVal, cv2.THRESH_OTSU)
    retval, g = cv2.threshold(GIamge, 0, maxVal, cv2.THRESH_OTSU)
    retval, b = cv2.threshold(BIamge, 0, maxVal, cv2.THRESH_OTSU)
    
    result = np.hstack([frame, r, g, b])

    cv2.imshow("0", frame)
    cv2.imshow("r", r) 
    cv2.imshow("g", g) 
    cv2.imshow("b", b) 
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()