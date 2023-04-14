import cv2
import numpy as np

def nothing(x):
    pass

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

maxVal = 255

cv2.namedWindow('Setting')  # 命名視窗名稱
cv2.createTrackbar('H_Low', 'Setting', maxVal//2, 180, nothing)
cv2.createTrackbar('H_High', 'Setting', maxVal//2, 180, nothing)
cv2.createTrackbar('S_LOW', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('S_High', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('V_Low', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('V_High', 'Setting', maxVal//2, maxVal, nothing)   # 建立數值設定條


while 1:
    ret, frame = cap.read()
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    HIamge, SIamge, VImage = cv2.split(img)
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    
    HL_val = cv2.getTrackbarPos('H_Low', 'Setting')
    HH_val = cv2.getTrackbarPos('H_High', 'Setting')
    SL_val = cv2.getTrackbarPos('S_LOW', 'Setting')
    SH_val = cv2.getTrackbarPos('S_High', 'Setting')
    VL_val = cv2.getTrackbarPos('V_Low', 'Setting')
    VH_val = cv2.getTrackbarPos('V_High', 'Setting')

    lower = np.array([HL_val, SL_val, VL_val])
    upper = np.array([HH_val, SH_val, VH_val


    mask = cv2.inRange(HIamge, lower, upper)

    

    cv2.imshow("0", frame)
    cv2.imshow("r", RImage) 

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()