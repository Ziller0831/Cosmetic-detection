import cv2
import numpy as np

cv2.namedWindow('Setting')  # 命名視窗名稱
cv2.createTrackbar('thres_1', 'Setting', 0, 500, nothing)
cv2.createTrackbar('thres_2', 'Setting', 400, 1000, nothing)

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

# cv2.namedWindow('Setting')  # 命名視窗名稱
# cv2.createTrackbar('min_size', 'Setting', 0, 500, nothing)
# cv2.createTrackbar('max_size', 'Setting', 400, 1000, nothing)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
        min_size_gray = cv2.getTrackbarPos('min_size', 'Setting')
    max_size_gray = cv2.getTrackbarPos('max_size', 'Setting')
    point1 = (156, 94)
    point2  = (504, 359)
    ret, frame = cap.read()

    # frame = frame[point1[1]: point2[1], point1[0]: point2[0]]
    if not ret:
        print("Cannot receive frame")
        break
    # min_size = cv2.getTrackbarPos('min_size', 'Setting')
    # max_size = cv2.getTrackbarPos('max_size', 'Setting')
    
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (13, 13), 1)

    ## Laplacian()
    Laplace_output = cv2.Laplacian(img, -1, 1, 5)
    Limg_out = (Laplace_output//32)*32
    # Limg_out = cv2.equalizeHist(Limg_out)
    cv2.imshow("Laplacian", Limg_out)

    ## Sobel()
    sobel_output = cv2.Sobel(img, -1, 1, 1, 1, 7)
    Simg_out = sobel_output
    # img_out = cv2.equalizeHist(Simg_out)
    cv2.imshow("Sobel", Simg_out)

    ## Canny()
    canny_output = cv2.Canny(img, 36, ㄆ)
    Cimg_out = canny_output
    # img_out = cv2.equalizeHist(Simg_out)
    cv2.imshow("Canny", Cimg_out)

    img_out = Cimg_out

    ## Contours process
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    img_out = cv2.morphologyEx(img_out, cv2.MORPH_CLOSE, element)
    # cv2.imshow("Graph", img_out)
    contours, hierarchy = cv2.findContours(img_out, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # cv2.drawContours(frame, contours, -1, (0,0,255), 5)
    # cv2.imshow("Result", frame)

    min_size = 330
    max_size = 611
    delete_list = []
    for i in range(len(contours)):
        if (cv2.arcLength(contours[i], True) < min_size) or (cv2.arcLength(contours[i], True) > max_size):
            delete_list.append(i)

    contours = delet_contours(contours, delete_list)
    
    cv2.drawContours(frame, contours, -1, (0,0,255), 5)
    cv2.imshow("Result", frame)




    if cv2.waitKey(1) == ord('q'):
        break  

cap.release()
cv2.destroyAllWindows()