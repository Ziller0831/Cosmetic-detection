'''## * 物件邊緣檢測 Edge Detection
Python version: 3.9.13
openCV version: 4.6.0
numpy  version: 1.23.5
'''
import cv2
import numpy as np
import time
import statistics

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
TargetFPS = 1
AngleZero_offset = 90 ##* 0度為x軸正向 順時針範圍0~360度


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
    return np.int0(rawMinRect[0]), min_rect, round(rawMinRect[2], 4)

def GravityCalc(moment):
    return int(moment['m10'] / moment['m00']), int(moment['m01'] / moment['m00'])

## TODO: 當質心與矩形中心重合時 None無法被round處理造成報錯
def AngleIndentify(deltaX, deltaY, angle):
    if deltaX > 0: return angle if deltaY < 0 else 0 if deltaY == 0 else (angle+270) if deltaY > 0 else None
    if deltaX < 0: return (angle+90) if deltaY < 0 else (angle+180) if deltaY > 0 else (angle+180) if deltaY == 0 else None
    if deltaX == 0: return (angle+90) if deltaY < 0 else (angle+270) if deltaY > 0 else 0

if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    fps = 30
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    time_start = time.time()
    dataBuffer = [[]]
    while True:
        minRect_array = []
        approx_array = []
        ret, frame = cap.read()  
        if not ret:
            print("Can't receive frame (stream  end?). Exiting ...")
            break

        imgBinary = ImagePreprocess(frame)
        cv2.imshow("binary", imgBinary)
        
        contours = DeletContours(cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0])
        # print(len(contours), fps,int(fps//TargetFPS))
        # if dataBuffer:
        #     dataBuffer = [[]] if dataBuffer[-1][0] == 0 else dataBuffer
        # else:
        #     dataBuffer = []
        resultData = []
        for contour in contours:
            moment = cv2.moments(contour)
            gravity_point = np.array(GravityCalc(moment))
            center_point, minRect, rawTheta = MinRectCircle(contour)

            deltaX, deltaY = gravity_point - center_point

            theta = AngleIndentify(deltaX, deltaY, 90-rawTheta)
            resultData.append([center_point[0], center_point[1], round(theta, 4)])
            # try:
            #     print("%3.2f, %3.2f"%(rawTheta-AngleZero_offset, theta-AngleZero_offset), end = "\r")
            # except:
            #     continue
            
            minRect_array.append(minRect)
            
            cv2.circle(frame, center_point, 1, (0,255,0), -1)
            cv2.circle(frame, gravity_point, 1, (0,0,255), -1)
            
            cv2.line(frame, center_point, gravity_point, (255,0,0), 1)

        # resultData = [[center_point[0], center_point[1], round(theta, 4)],...]
        
        if dataBuffer:
            diff_buffer = len(dataBuffer) - int(fps//TargetFPS) + 1
            dataBuffer = dataBuffer[diff_buffer if diff_buffer >= 0 else 0:]
        dataBuffer.append(resultData)
        # print(int(fps//TargetFPS), len(dataBuffer), dataBuffer)
        # print(np.array(dataBuffer).shape)
        if not dataBuffer[0]: continue
        results_mean = np.mean(np.array(dataBuffer, dtype=object), axis=0)
        # if dataBuffer[1:][0][2]
        # results_stdev = statistics.stdev(dataBuffer[0 if dataBuffer[0] else 1:][0][2])
        angleData = []
        for array in dataBuffer:
            angleData.append([sublist[-1] for sublist in array])
        angleData = angleData[1:]
        print(len(angleData))
        results_stdev = np.std(np.array(dataBuffer, dtype=float), axis=0, ddof=1)
        # print(results_mean, dataBuffer[:,:,2])


        for result in results_mean: 
            text = f"({int(result[0])}, {int(result[1])}, {result[2]-AngleZero_offset:.1f})" ## fstring
            # text = "({0}, {1})".format(str(gravity_point[0]), str(gravity_point[1])) ##另一種打法
            cv2.putText(frame, text, (int(result[0]+10), int(result[1]+10)), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 64, 255), 2, 8, 0)
            # cv2.putText(frame, text, (gravity_point[0]+10, gravity_point[1]+10), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 3, 8, 1)
            # print(len(contours), "contours left after length filter",end="\r")

        cv2.drawContours(frame, contours, -1, (0,0,255), 2)
        for minRect in minRect_array:
            cv2.drawContours(frame, [minRect], 0, (0, 255, 0), 2)
            # print(minRect)
        cv2.drawContours(frame, approx_array,-1, (255,0,0), 2)
        fps = round(1/(time.time() - time_start), 2)


        # cv2.circle(Result, raw_minRect[0], 2, (0,255,255), 2)
        cv2.putText(frame, f"fps:{str(fps)}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
        cv2.imshow("Result", frame)

        time_start = time.time()
        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break

    cv2.destroyAllWindows()