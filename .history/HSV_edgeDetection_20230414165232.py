import cv2
import numpy as np

def nothing(x):
    pass

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

maxVal = 255

## 在影像上將輪廓框選
def contourSearch(ImgName, imgSource, contours, DrawOnBlack):
    if(DrawOnBlack):
        temp = np.ones(imgSource.shape, dtype=np.uint8) * 255
        cv2.drawContours(temp, contours, -1, (0, 0, 0), 2)
    else:
        temp = imgSource.copy()
        cv2.drawContours(temp, contours, -1, (0, 0, 255), 2)
    
    cv2.imshow(ImgName, temp)

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
        print("Can't receive frame (stream end?). Exiting ...")
        break

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.imshow("Raw", frame)

    img = cv2.GaussianBlur(img, (3, 3), 1)
    ret, binary = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY_INV)  # 使用Binary來
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)) # 返回指定形状和尺寸的结构元素
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, element)

    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    contourSearch("find contours", img, contours, True)

    deletList = []
    c, row, column = hierarchy.shape
    for i in range(row):
        if hierarchy[0, i, 2] > 0 or hierarchy[0, i, 3] > 0:
            deletList.append(i)
    contours = delet_contours(contours, deletList)

    min_size = 20
    max_size = 500
    delete_list = []
    for i in range(len(contours)):
        if (cv2.arcLength(contours[i], True) < min_size) or (cv2.arcLength(contours[i], True) > max_size):
            delete_list.append(i)

    contours = delet_contours(contours, delete_list)
    print(len(contours), "contours left after length filter")
    contourSearch("contours after length filtering", img, contours, False)

    result = img.copy()
    x, y, w, h = cv2.bound


    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()