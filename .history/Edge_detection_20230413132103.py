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
cv2.createTrackbar('Blue', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('H_Low', 'Setting', maxVal//2, 180, nothing)
cv2.createTrackbar('H_High', 'Setting', maxVal//2, 180, nothing)
cv2.createTrackbar('S_LOW', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('S_High', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('V_Low', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('V_High', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('Gray', 'Setting', maxGrayVal//2, maxGrayVal, nothing)


while 1:
    ret, frame = cap.read()
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    BIamge, GIamge, RImage = cv2.split(frame)
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    R_val = cv2.getTrackbarPos('Red', 'Setting')
    G_val = cv2.getTrackbarPos('Green', 'Setting')
    B_val = cv2.getTrackbarPos('Blue', 'Setting')

    retval, r = cv2.threshold(RImage, R_val, maxVal, cv2.THRESH_BINARY)
    retval, g = cv2.threshold(GIamge, G_val, maxVal, cv2.THRESH_BINARY)
    retval, b = cv2.threshold(BIamge, B_val, maxVal, cv2.THRESH_BINARY)


    HL_val = cv2.getTrackbarPos('H_Low', 'Setting')
    HH_val = cv2.getTrackbarPos('H_High', 'Setting')
    SL_val = cv2.getTrackbarPos('S_LOW', 'Setting')
    SH_val = cv2.getTrackbarPos('S_High', 'Setting')
    VL_val = cv2.getTrackbarPos('V_Low', 'Setting')
    VH_val = cv2.getTrackbarPos('V_High', 'Setting')

    lower = np.array([HL_val, SL_val, VL_val])
    upper = np.array([HH_val, SH_val, VH_val])

    mask = cv2.inRange(img, lower, upper)
    

    cv2.imshow("Raw", frame)
    cv2.imshow("Red", r) 
    cv2.imshow("Green", g) 
    cv2.imshow("Blue", b)
    cv2.imshow("HSV", mask) 
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()