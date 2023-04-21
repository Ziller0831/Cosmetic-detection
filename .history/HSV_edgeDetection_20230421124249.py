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
    return min_rect

# def ContoursDetail(img_src, contours):
#     angle = []
#     for contour in contours:
#         try:
#             moment = cv2.moments(contour)
#             ## * 質心計算
#             Centroid = (int(moment['m10'] / moment['m00']), int(moment['m01'] / moment['m00']))
#             # print(Centroid) 
#             cv2.circle(img_src, Centroid, 2, (0,0,255), 2)
#             text = "(" + str(Centroid[0]) + ", " + str(Centroid[1]) + ")"
#             cv2.putText(img_src, text, (Centroid[0]+10, Centroid[1]+10), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 1, 8, 0);
#             ## * 方向計算
#             m20   = moment['m20']
#             m02   = moment['m02']
#             m11   = moment['m11']
#             angle = np.degrees(0.5 * np.arctan2(2*m11, m20-m02))
#             # print(angle, end="\r")
#         except:
#             print('There is no target', end="\r")
#     return img_src, angle

def Centroid(moment):
    Centroid = (int(moment['m10'] / moment['m00']), int(moment['m01'] / moment['m00']))
    return Centroid


if __name__ == '__main__':
    minRect_array = []

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    while True:
        ret, frame = cap.read()  
        if not ret:
            print("Can't receive frame (stream  end?). Exiting ...")
            break

        imgBinary = ImagePreprocess(frame)
        cv2.imshow("binary", imgBinary)

        contours = DeletContours(cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0])

        for contour in contours:
            moment = cv2.moments(contour)
            Centroid_point = Centroid(moment)

            minRect_array.append(MinRectCircle(contour))

            cv2.circle(frame, Centroid_point, 2, (0,0,255), 2)
            text = "(" + str(Centroid_point[0]) + ", " + str(Centroid_point[1]) + ")"
            cv2.putText(frame, text, (Centroid_point[0]+10, Centroid_point[1]+10), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 1, 8, 0);
            print(len(contours), "contours left after length filter",end="\r")



        
        cv2.drawContours(frame, contours, -1, (0,0,255), 2)
        for min_rect in minRect_array:
            cv2.drawContours(frame, [min_rect], 0, (0, 255, 0), 2)

        # cv2.circle(Result, raw_minRect[0], 2, (0,255,255), 2)
        # cv2.imshow("Result", Result)

        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break

    cv2.destroyAllWindows()