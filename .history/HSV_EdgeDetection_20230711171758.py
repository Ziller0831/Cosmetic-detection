'''## * 物件邊緣檢測 Edge Detection
Python version: 3.9.13
openCV version: 4.6.0
numpy  version: 1.23.5
'''
import cv2
import numpy as np
import time
from math import sin, cos, radians

# class Edge_detection:
#     def __init__(self):
#         pass

# TODO:建立校正程式

# TODO:將每個物件的參數加進來獨立化
#*白色與透明工件在黑布下的HSV參數
WhiteLower = np.array([0, 0, 155])
WhiteUpper = np.array([180, 25, 255])

#* 黑色工件在白紙板下的HSV參數
BlackLower = np.array([0, 0, 154])
BlackUpper = np.array([180, 255, 230])

Contour_size = [136, 611]
TargetFPS = 1         ##* 數值越大FPS越高，資料越不穩定
AngleZero_offset = 90 ##* 0度為x軸正向 順時針範圍0~G360度
ArrowLength = 40

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
    return [contour for contour in contours if Contour_size[0] <= cv2.arcLength(contour, True) <= Contour_size[1]]

def MinRectCircle(contour):
    rawMinRect = cv2.minAreaRect(contour)  # min_area_rectangle
    min_rect = np.int0(cv2.boxPoints(rawMinRect))
    return np.int0(rawMinRect[0]), min_rect, round(rawMinRect[2], 4), rawMinRect[1]

def GravityCalc(moment):
    return int(moment['m10'] / moment['m00']), int(moment['m01'] / moment['m00'])

## TODO: 當質心與矩形中心重合時 None無法被round處理造成報錯
# def AngleIndentify(deltaX, deltaY, angle):
    # if deltaX > 0: return angle if deltaY < 0 else 0 if deltaY == 0 else (angle+270) if deltaY > 0 else None
    # if deltaX < 0: return (angle+90) if deltaY < 0 else (angle+180) if deltaY > 0 else (angle+180) if deltaY == 0 else None
    # # if deltaX == 0: return (angle+90) if deltaY < 0 else (angle+270) if deltaY > 0 else 0
    # if deltaX > 0:
    #     if deltaY < 0:
    #         return angle, 0         # 第一象限
    #     elif deltaY == 0:
    #         return 0, 1         # X軸
    #     elif deltaY > 0:
    #         return (angle + 270), 2   # 第四象限
    # elif deltaX < 0:
    #     if deltaY < 0:
    #         return (angle + 90), 3    # 第二象限
    #     elif deltaY > 0:
    #         return (angle + 180), 4   # 第三象限
    #     elif deltaY == 0:
    #         return 180, 5   # -X軸
    # elif deltaX == 0:  # deltaX == 0
    #     if deltaY < 0:
    #         return 90, 6    # Y軸
    #     elif deltaY > 0:
    #         return 270, 7   # -Y軸
    #     elif deltaY == 0:
    #         return angle, 8
    # else:
    #     pass
# def AngleIndentify2(angle, diag_diff):
#     if diag_diff[0] > diag_diff[1] and angle > 85:
#         return 90 - angle, 1
#     elif diag_diff[0] < diag_diff[1] and angle < 190:
#         return angle - 90, 2
#     else:
#         return angle, 3

# def AngleIndentify(deltaX, deltaY, angle):
#     pass


if __name__ == '__main__':
    # ED = Edge_detection()
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
        cv2.imshow("frame", frame)

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
            center_point, minRect, rawTheta, MinSize = MinRectCircle(contour)
            x, y, w, h = cv2.boundingRect(contour)

            # cv2.rectangle(frame, (x, y), (x + w, y + h), (200, 200, 200), 2)

            deltaX, deltaY = gravity_point - center_point
            # print(f"X差{deltaX}, Y差{deltaY}")
            # print(MinSize)

            # theta = cv2.fastAtan2(float(deltaY), float(deltaX))

            vector_a = minRect[1] - minRect[0]
            vector_b = minRect[2] - minRect[1]

            vector_a_value = (vector_a[0]**2+vector_a[1]**2)**0.5
            vector_b_value = (vector_b[0]**2+vector_b[1]**2)**0.5



            if(vector_a_value < vector_b_value):
                vector = vector_a
                point1 = (minRect[0] + minRect[1])//2
                point2 = (minRect[2] + minRect[3])//2
            elif(vector_a_value > vector_b_value):
                vector = vector_b
                point1 = (minRect[0] + minRect[3])//2
                point2 = (minRect[1] + minRect[2])//2
            
            theta = cv2.fastAtan2(int(vector[0]), int(vector[1]))

            # print(f"{minRect[0]}, {minRect[1]},{minRect[2]},{vector}, {theta:.4f}")

            vector_aa = gravity_point - point1
            vector_bb = point2 - gravity_point

            length1 = ((vector_aa[0])**2+(vector_aa[1])**2)**0.5
            length2 = ((vector_bb[0])**2+(vector_bb[1])**2)**0.5

            # if(length1 < length2):
            vector1 = vector_aa
            # elif(length1 > length2):
            #     vector1 = point2 - gravity_point
            
            theta1 = cv2.fastAtan2(int(vector1[0]), int(vector1[1]))
            
            # print(f"{gravity_point}, {point1},{point2},{vector1},{length1:.4f},{length2:.4f}. {theta:.4f}, {theta1:.4f}")
            # print(f"{gravity_point}, {point1},,{point2},{vector1},{length1:.4f},{length2:.4f}. {theta:.4f}, {theta1:.4f}")

            # theta, func = AngleIndentify(deltaX, deltaY, 90-rawTheta)
            # theta, func2 = AngleIndentify2(theta, abs(diff))

            # print(f"X差{deltaX}, Y差{deltaY}, {diff}, rawTheta:{90-rawTheta:.2f}, theta:{theta:.2f}, {func}")


            minRect_array.append(minRect)




            endPoint = [int(center_point[0]+ArrowLength*cos(radians(theta1))), int(center_point[1]+(-ArrowLength*sin(radians(theta1))))]
            
            cv2.circle(frame, center_point, 3, (100,255,100), -1)
            # cv2.circle(frame, point1, 3, (100,150,255), 3)
            cv2.circle(frame, point2, 3, (150,100,255), 3)
            cv2.circle(frame, minRect[0], 3, (100,100,255), 2)
            cv2.circle(frame, minRect[1], 3, (150,50,200), 2)
            cv2.circle(frame, minRect[2], 3, (80,255,90), 2)
            # cv2.arrowedLine(frame, minRect[1], minRect[0], (255,100,0), 2)
            # cv2.arrowedLine(frame, minRect[2], minRect[1], (255,100,100), 2)
            cv2.arrowedLine(frame, center_point, endPoint, (100,100,100), 2)
            # cv2.circle(frame, minRect[3], 3, (255,100,50), 2)
            resultData.append([center_point[0], center_point[1], round(theta, 4)])

        # resultData = [[center_point[0], center_point[1], round(theta, 4)],...]
        
        if dataBuffer:
            diff_buffer = len(dataBuffer) - int(fps//TargetFPS) + 1
            dataBuffer = dataBuffer[diff_buffer if diff_buffer >= 0 else 0:]
        dataBuffer.append(resultData)
        # print(int(fps//TargetFPS), len(dataBuffer))#, dataBuffer)
        # print(np.array(dataBuffer).shape)
        if not dataBuffer[0]: continue
        results_mean = np.mean(np.array(dataBuffer, dtype=object), axis=0)
        ##* 顯示角度的標準差，需要在開，因為會導致程式Break
        angleData = []
        for arrayPerScan in dataBuffer: angleData.append([objectInArray[-1] for objectInArray in arrayPerScan])
        # print(f"ang:{angleData}")
        # results_stdev = np.std(np.array(angleData, dtype=float), axis=0, ddof=1)
        # print(f"stdev{results_stdev}")


        for result in results_mean: 
            text = f"({int(result[0])}, {int(result[1])}, {result[2]:.1f})" ## fstring
            # text = "({0}, {1})".format(str(gravity_point[0]), str(gravity_point[1])) ##另一種打法
            cv2.putText(frame, text, (int(result[0]+10), int(result[1]+10)), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 64, 255), 2, 8, 0)
            # cv2.putText(frame, text, (gravity_point[0]+10, gravity_point[1]+10), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 3, 8, 1)
            # print(len(contours), "contours left after length filter",end="\r")

        cv2.drawContours(frame, contours, -1, (0,0,255), 2)
        # for minRect in minRect_array:
        #     cv2.drawContours(frame, [minRect], 0, (0, 255, 0), 2)
        #     # print(minRect)
        cv2.drawContours(frame, approx_array,-1, (255,0,0), 2)
        fps = round(1/(time.time() - time_start), 2)


        # cv2.circle(Result, raw_minRect[0], 2, (0,255,255), 2)
        cv2.putText(frame, f"fps:{str(fps)}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
        cv2.imshow("Result", frame)

        time_start = time.time()
        if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
            break

    cv2.destroyAllWindows()