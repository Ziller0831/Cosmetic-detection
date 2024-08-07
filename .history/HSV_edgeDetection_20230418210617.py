## TODO:
import cv2
import numpy as np
import os

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

def nothing(x):
    pass

cap = cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

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

def image_preprocess(img_src):
    point1 = (156, 94)
    point2  = (504, 359)
    # frame = frame[point1[1]: point2[1], point1[0]: point2[0]]
    HSV_img = cv2.cvtColor(img_src, cv2.COLOR_BGR2HSV)
    HSV_img = cv2.GaussianBlur(HSV_img, (3, 3), 1)
    return HSV_img

## TODO:白色物品的HSV參數
WhiteLower = np.array([0, 0, 155])
WhiteUpper = np.array([180, 31, 255])

while 1:
    ret, frame = cap.read()  
    if not ret:
        print("Can't receive frame (stream  end?). Exiting ...")
        break

    W_mask = cv2.inRange(image_preprocess(frame), WhiteLower, WhiteUpper)
    # element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    binary = cv2.morphologyEx(W_mask, cv2.MORPH_OPEN, element)

    cv2.imshow("binary", binary)

    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    ## 輪廓周長小於136大於611的刪去
    min_size = 136
    max_size = 611
    delete_list = []
    for i in range(len(contours)):
        if (cv2.arcLength(contours[i], True) < min_size) or (cv2.arcLength(contours[i], True) > max_size):
            delete_list.append(i)

    contours = delet_contours(contours, delete_list)
    # print(len(contours), "contours left after length filter")



    for i in range(len(contours)):
        try:
            print(cv2.arcLength(contours[i], True),end="\r")
            moment = cv2.moments(contours[ i])
            pt = (int(moment['m10'] / moment['m00']), int(moment['m01'] / moment['m00']))
            cv2.circle(frame, pt, 2, (0,0,255), 2)
            text = "(" + str(pt[0]) + ", " + str(pt[1]) + ")" 
            cv2.putText(frame, text, (pt[0]+10, pt[1]+10), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 1, 8, 0);
        except:
            print('There is no target')
    
    cv2.drawContours(frame, contours, -1, (0,0,255), 5)
    cv2.imshow("Result", frame)
    # clearConsole()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()