'''## * 物件邊緣檢測 Edge Detection
Python version: 3.9.13
openCV version: 4.6.0
numpy  version: 1.23.5
'''
import cv2
import numpy as np
import time

# *料件選擇
# Identified_item = [0]

# switch = {
#     A: []
# }

# TODO:將每個物件的參數加進來獨立化
# *白色與透明工件在黑布下的HSV參數
WhiteLower = np.array([0, 0, 155])
WhiteUpper = np.array([180, 25, 255])

# *黑色工件在白紙板下的HSV參數
BlackLower = np.array([0, 0, 154])
BlackUpper = np.array([180, 255, 230])

Contour_size = [136, 611]


def nothing(x):
    pass

def ImagePreprocess(img_src):
    HSV_img = cv2.cvtColor(img_src, cv2.COLOR_BGR2HSV)
    HSV_img = cv2.GaussianBlur(HSV_img, (3, 3), 1)
    w_mask = cv2.inRange(HSV_img, WhiteLower, WhiteUpper)
    b_mask = cv2.inRange(HSV_img, BlackLower, BlackUpper)
    outputImg = cv2.bitwise_or(w_mask, b_mask)
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    binary  = cv2.morphologyEx(outputImg, cv2.MORPH_CLOSE, element)
    return binary

def DeletContours(contours):
    contoursList = []
    for contour in contours:
        contoursLength = cv2.arcLength(contour, True)
        if (contoursLength >= Contour_size[0]) and (contoursLength <= Contour_size[1]):
            contoursList.append(contour)
    return contoursList

def MinRectCircle(contour):
    rawMinRect = cv2.minAreaRect(contour)  # min_area_rectangle
    min_rect = np.int0(cv2.boxPoints(rawMinRect))
    # if((rawMinRect[1][1]/rawMinRect[1][0]) < 1):
    #     rawMinRect[2] =  90 + rawMinRect[2]
    # print(rawMinRect[2])
    return np.int0(rawMinRect[0]), min_rect

def GravityCalc(moment):
    return int(moment['m10'] / moment['m00']), int(moment['m01'] / moment['m00'])


if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    time_start = time.time()
    while True:
        minRect_array = []
        approx_array = []
        approxCenter_array = []
        ret, frame = cap.read()  
        if not ret:
            print("Can't receive frame (stream  end?). Exiting ...")
            break

        imgBinary = ImagePreprocess(frame)
        cv2.imshow("binary", imgBinary)

        contours = DeletContours(cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0])

        for contour in contours:
            moment = cv2.moments(contour)
            gravity_point = GravityCalc(moment)
            center_point, minRect = MinRectCircle(contour)

            minRect_array.append(minRect)
            
            approx = cv2.approxPolyDP(contour,2,True)
            approx_array.append(approx)
            approxCenter_array = 
            cv2.circle(frame, center_point, 2, (0,255,0), 2)
            cv2.circle(frame, gravity_point, 2, (0,0,255), 2)
            cv2.line(frame, center_point, gravity_point, (255,0,0), 1)

            text = f"({str(gravity_point[0])}, {str(gravity_point[1])})" ## fstring
            # text = "({0}, {1})".format(str(gravity_point[0]), str(gravity_point[1])) ##另一種打法
            cv2.putText(frame, text, (gravity_point[0]+10, gravity_point[1]+10), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 1, 8, 0)
            # print(len(contours), "contours left after length filter",end="\r")

        cv2.drawContours(frame, contours, -1, (0,0,255), 2)
        for minRect in minRect_array:
            cv2.drawContours(frame, [minRect], 0, (0, 255, 0), 2)
            # print(minRect)
        cv2.drawContours(frame, approx_array,-1, (255,0,0), 2)
        time_spent = round(1/(time.time() - time_start), 2)


        # cv2.circle(Result, raw_minRect[0], 2, (0,255,255), 2)
        cv2.putText(frame, f"fps:{str(time_spent)}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
        cv2.imshow("Result", frame)

        time_start = time.time()
        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break

    cv2.destroyAllWindows()