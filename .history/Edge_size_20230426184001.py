import cv2
import numpy as np

#*白色與透明工件在黑布下的HSV參數
WhiteLower = np.array([0, 0, 155])
WhiteUpper = np.array([180, 25, 255])

#* 黑色工件在白紙板下的HSV參數
BlackLower = np.array([0, 0, 154])
BlackUpper = np.array([180, 255, 230])

Contour_size = [100, 1000]

AreaSizeData = []
LengthSizeData = []

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

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    while len(SizeData) < 100: ## 樣本數
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream  end?). Exiting ...")
            break

        imgBinary = ImagePreprocess(frame)
        cv2.imshow("binary", imgBinary)
        contours = DeletContours(cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0])

        for contour in contours:
            print(cv2.contourArea(contour))
            print(cv2.arcLength(contour))
            AreaSizeData.append(cv2.contourArea(contour))
            LengthSizeData.append(cv2.arcLength(contour))

        cv2.drawContours(frame, contours, -1, (0,0,255), 2)
        cv2.imshow("Result", frame)
        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break

    areaMaxCont = max(AreaSizeData)
    areaMinCont = min(AreaSizeData)
    areaMeanCont = np.mean(np.array(AreaSizeData, dtype=object))
    areaStdCont = np.std(np.array(AreaSizeData,  dtype=float), axis=0, ddof=1)
    print('AreaContours','Max:', areaMaxCont, 'Min:', areaMinCont, "Mean:", areaMeanCont, 'Std:', areaStdCont)

    LengthMaxCont = max(LengthSizeData)
    LengthMinCont = min(ALengthSizeData)
    LengthMeanCont = np.mean(np.array(AreaSizeData, dtype=object))
    LengthStdCont = np.std(np.array(AreaSizeData,  dtype=float), axis=0, ddof=1)
    print('LengthContours','Max:', areaMaxCont, 'Min:', areaMinCont, "Mean:", areaMeanCont, 'Std:', areaStdCont)
    cv2.destroyAllWindows()