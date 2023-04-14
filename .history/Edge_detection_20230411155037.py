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

imgPath = '/media/sf_use_with_VM/2022WVT/image'
imgName = 'apple.png'

while 1:
    image = cv2.imread(imgPath+ '/' + imgName)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    th_val = cv2.getTrackbarPos('Gray', 'Setting')  # 獲取設定條數值
    ret, th1 = cv2.threshold(gray, th_val, maxGrayVal, cv2.THRESH_BINARY)   # 門檻值過濾 
    
    result = np.hstack([gray, th1])

    cv2.imshow('result', result)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()