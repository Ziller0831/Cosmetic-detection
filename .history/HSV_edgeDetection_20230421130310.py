'''## * 物件邊緣檢測 Edge Detection
Python version: 3.9.13
openCV version: 4.6.0
numpy  version: 1.23.5
'''
import cv2
import numpy as np

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
            # print(contoursLength)
    return contoursList

def MinRectCircle(contour):
    raw_min_rect = cv2.minAreaRect(contour)  # min_area_rectangle
    min_rect = np.int0(cv2.boxPoints(raw_min_rect))
    return np.int0(raw_min_rect[0]), min_rect

def GravityCalc(moment):
    return int(moment['m10'] / moment['m00']), int(moment['m01'] / moment['m00'])


if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    while True:
        minRect_array = []
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

            cv2.line(frame, center_point, gravity_point, 2, (255,0,0))

            cv2.circle(frame, center_point, 2, (0,255,0), 2)
            cv2.circle(frame, gravity_point, 2, (0,0,255), 2)

            text = f"({str(gravity_point[0])}ㄝstr(gravity_point[1]) + )"
            cv2.putText(frame, text, (gravity_point[0]+10, gravity_point[1]+10), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 1, 8, 0);
            print(len(contours), "contours left after length filter",end="\r")


        
        cv2.drawContours(frame, contours, -1, (0,0,255), 2)
        for min_rect in minRect_array:
            cv2.drawContours(frame, [min_rect], 0, (0, 255, 0), 2)

        # cv2.circle(Result, raw_minRect[0], 2, (0,255,255), 2)
        cv2.imshow("Result", frame)

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break

    cv2.destroyAllWindows()