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
cv2.createTrackbar('H_L', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('Green', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('Blue', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('Red', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('Green', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('Blue', 'Setting', maxVal//2, maxVal, nothing)   # 建立數值設定條


while 1:
    ret, frame = cap.read()
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    HIamge, SIamge, VImage = cv2.split(img)
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    R_val = cv2.getTrackbarPos('Red', 'Setting')


    retval, r = cv2.threshold(RImage, R_val, maxVal, cv2.THRESH_OTSU)

    

    cv2.imshow("0", frame)
    cv2.imshow("r", RImage) 

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()