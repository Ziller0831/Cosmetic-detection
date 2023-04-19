import cv2
import numpy as np

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

cv2.namedWindow('Setting')  # 命名視窗名稱
cv2.createTrackbar('min_size', 'Setting', 0, 500, nothing)
cv2.createTrackbar('max_size', 'Setting', 400, 1000, nothing)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    point1 = (100, 100)
    point2  = (500, 380)
    ret, frame = cap.read()

    frame = frame[point1[1]: point2[1], point1[0]: point2[0]]
    if not ret:
        print("Cannot receive frame")
        break
    
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ## Laplacian()
    Laplace_output = cv2.Laplacian(img, -1, 1, 5)
    cv2.imshow("Laplacian", Laplace_output)
    img_out = Laplace_output



    ## Contours process
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    img_out = cv2.morphologyEx(img_out, cv2.MORPH_CLOSE, element)
    # cv2.imshow("Graph", img_out)
    contours, hierarchy = cv2.findContours(img_out, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # cv2.drawContours(frame, contours, -1, (0,0,255), 5)
    # cv2.imshow("Result", frame)

    min_size = 136
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