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
cv2.createTrackbar('Red', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('Green', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('Blue', 'Setting', maxVal//2, maxVal, nothing)   # 建立數值設定條


while 1:
    ret, frame = cap.read()
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    BIamge, GIamge, RImage = cv2.split(img)
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    R_val = cv2.getTrackbarPos('Red', 'Setting')
    G_val = cv2.getTrackbarPos('Green', 'Setting')
    B_val = cv2.getTrackbarPos('Blue', 'Setting')

    retval, r = cv2.threshold(RImage, R_val, maxVal, cv2.THRESH_BINARY)
    retval, g = cv2.threshold(GIamge, G_val, maxVal, cv2.THRESH_BINARY)
    retval, b = cv2.threshold(BIamge, B_val, maxVal, cv2.THRESH_BINARY)
    

    cv2.imshow("0", frame)
    cv2.imshow("r", ) 
    cv2.imshow("g", GIamge) 
    cv2.imshow("b", BIamge) 
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()