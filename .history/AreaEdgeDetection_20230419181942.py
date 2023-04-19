import cv2
import numpy as np
import time

## *白色與透明工件在黑布下的HSV參數
WhiteLower = np.array([0, 0, 155])
WhiteUpper = np.array([180, 255, 255])

## *黑色工件在白紙板下的HSV參數
BlackLower = np.array([0, 0, 154])
BlackUpper = np.array([180, 255, 230])

Contour_area = [1000, 8000]


def nothing(x):
    pass

def delet_contours(contour, moment):
    contoursList = []
    if (moment['m00'] >= Contour_area[0]) and (moment['m00'] <= Contour_area[1]):
        contoursList.append(contour)
    return contoursList

def draw_min_rect_circle(contour):
    min_rect_array = []
    min_rect = cv2.minAreaRect(contour)  # min_area_rectangle
    min_rect = np.int0(cv2.boxPoints(min_rect))
    min_rect_array.append(min_rect)
    return min_rect_array

def imagePreprocess(img_src):
    HSV_img = cv2.cvtColor(img_src, cv2.COLOR_BGR2HSV)
    HSV_img = cv2.GaussianBlur(HSV_img, (3, 3), 1)
    w_mask = cv2.inRange(HSV_img, WhiteLower, WhiteUpper)
    b_mask = cv2.inRange(HSV_img, BlackLower, BlackUpper)
    outputImg = cv2.bitwise_or(w_mask, b_mask)
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    binary  = cv2.morphologyEx(outputImg, cv2.MORPH_CLOSE, element)
    return binary

def barycenterSearch(img_src, moment):       
        # print(moment['m00'], end="\n\r")
    pt = (int(moment['m10'] / moment['m00']), int(moment['m01'] / moment['m00']))
    cv2.circle(img_src, pt, 2, (0,0,255), 2)
    text = "(" + str(pt[0]) + ", " + str(pt[1]) + ")" 
    cv2.putText(img_src, text, (pt[0]+10, pt[1]+10), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 1, 8, 0);
    return img_src

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("Cannot open camera", end="\n\r")
    exit()


while 1:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream  end?). Exiting ...", end="\n\r")
        break

    imgBinary = imagePreprocess(frame)
    cv2.imshow("binary", imgBinary)
    RawContours = cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    contours = []
    for contour in RawContours:
        try:
            moment = cv2.moments(contour)
            contours = delet_contours(contour, moment)
            frame = barycenterSearch(frame, moment)
            min_rect_array = draw_min_rect_circle(contours)
        except:
            print('There is no target')

    # print(len(contours), "contours left after length filter",end="\n\r")


    cv2.drawContours(frame, contours, -1, (0,0,255), 2)
    for min_rect in min_rect_array:
        cv2.drawContours(frame, [min_rect], 0, (0, 255, 0), 2)
    cv2.imshow("Result", frame)

    if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
        break

cv2.destroyAllWindows()