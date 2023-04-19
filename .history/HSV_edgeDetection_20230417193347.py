import cv2
import numpy as np

def nothing(x):
    pass

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

    ## 輪廓周長小於300大於500的刪去
    min_size = 250
    max_size = 500
cv2.namedWindow('Setting')  # 命名視窗名稱
cv2.createTrackbar('min_size', 'Setting', maxVal//2, maxVal, nothing)
cv2.createTrackbar('max_size', 'Setting', maxVal//2, maxVal, nothing)

## 篩選輪廓
def delet_contours(contours, delete_list):
    delta = 0
    for i in range(len(delete_list)):
        # print("i= ", i)
        contours = list(contours)
        del contours[delete_list[i] - delta]
        contours = tuple(contours)
        delta = delta + 1
    return contours



while 1:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream  end?). Exiting ...")
        break

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


    img = cv2.GaussianBlur(img, (3, 3), 1)
    ret, binary = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY_INV)  # 使用Binary來
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)) # 返回指定形状和尺寸的结构元素
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, element)

    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    deletList = []
    try:
        c, row, column = hierarchy.shape
        for i in range(row):
            if hierarchy[0, i, 2] > 0 or hierarchy[0, i, 3] > 0:
                deletList.append(i)
                contours = delet_contours(contours, deletList)
    except:
        print('There is no target')

    delete_list = []
    for i in range(len(contours)):
        if (cv2.arcLength(contours[i], True) < min_size) or (cv2.arcLength(contours[i], True) > max_size):
            delete_list.append(i)

    contours = delet_contours(contours, delete_list)
    # print(len(contours), "contours left after length filter")



    for i in range(len(contours)):
        try:
            print(cv2.arcLength(contours[i], True))
            moment = cv2.moments(contours[ i])
            pt = (int(moment['m10'] / moment['m00']), int(moment['m01'] / moment['m00']))
            cv2.circle(frame, pt, 2, (0,0,255), 2)
            text = "(" + str(pt[0]) + ", " + str(pt[1]) + ")" 
            cv2.putText(frame, text, (pt[0]+10, pt[1]+10), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 1, 8, 0);
        except:
            print('There is no target')
    
    cv2.drawContours(frame, contours, -1, (0,0,255), 5)
    cv2.imshow("Result", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()