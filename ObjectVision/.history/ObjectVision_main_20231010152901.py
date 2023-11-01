'''
********************************
    HaoYing 視覺辨識 主程式
********************************

* 使用前請記得確認程式中變數(CurrentDir)是否正確指向\\ObjectVision\\HaoYing的路徑
* Main 的第29行
* Vision 的第22行
* Setting 的第17行
##! 請記得路徑的\要使用\\才不會有問題

視覺辨識拆分為3個功能
    ObjectContours    -> 產品輪廓標定
    CameraCalibration -> 相機校正與對Robot標定(使用張氏標定法)
    WorkMode_loop     -> 視覺辨識
'''

import cv2
import os
import socket
import HaoYing.Vision as Vision
import HaoYing.FileProcess as FP
import HaoYing.Setting as Setting

AngleZeroOffset = 0 ##* 0度為x軸正向 順時針範圍0~G360度

##! 請記得路徑是否正確
CurrentDir = "C:\\Users\\jcyu\\Documents\\GitHub\\OpenCV-image-process-test\\ObjectVision\\HaoYing"

CSV_path = os.path.abspath(os.path.join(CurrentDir, "..\\Data\\Cosmetic_parameter.csv"))
XML_path =  os.path.abspath(os.path.join(CurrentDir, "..\\Data\\Setting.xml"))



def ObjectContours(object):  ##* Image catch
    initial = Setting.initialize(object, CSV_path)
    areaMean, areaStd = initial.AreaIdent()  ##* 輪廓面積平均值, 輪廓面積標準差

    FP.CSVDataWrite(object, CSV_path, areaMean, areaStd)
    return 100


def CameraCalibration():
    initial = Setting.initialize(None, CSV_path)
    [cameraMatrix, rVecs, tVecs] = initial.CameraCalibration() ##* 相機畸變參數矩陣, 旋轉向量, 平移向量

    # Upload the calibration parameter to XML file
    calibration = {"camera_matrix": cameraMatrix, "rvecs": rVecs, "tvecs": tVecs}
    for i in calibration:
        FP.XMLWrite(XML_path, str(i), [[float(num) for num in row] for row in calibration[str(i)]])

    return 100


def WorkMode_loop(Object):
    ##* UDP setup
    targetIP = '127.0.0.1'
    LetsviewPort = 65235
    pythonPort = 65234

    ##* Build UDP socket
    UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDP_socket.bind((targetIP, pythonPort))

    ##* Set the Timeout to 0.15 sec
    UDP_socket.settimeout(0.15)

    ##* Load the calibration parameters
    TF_paras = {"camera_matrix": 0, "rvecs": 0, "tvecs": 0}
    for TF_para in TF_paras:
        TF_paras[TF_para] = FP.XMLRead(XML_path, str(TF_para))
    
    ##* Input object Data
    objectData = FP.CSVDataLoad(CSV_path, Object)

    ##* 實例化EdgeDetector類別
    vision = Vision.EdgeDetector(2, TF_paras, objectData)
    while True:
        try:
            UDP_recvMessage,_ = UDP_socket.recvfrom(1024)
            if (UDP_recvMessage.decode() == 'close'): break

        except ConnectionResetError: pass
        
        except socket.timeout: 
            # frame = vision.ImageCatch()
            frame = cv2.imread("C:\\Users\\jcyu\\Downloads\\vv_1.png")
            imgBinary = vision.ImagePreProcess(frame)
            contours = vision.ContoursCalc(imgBinary)
            frame, featuresArray = vision.FeaturesCalc(frame, contours)
            featuresArray.sort(key=lambda x:x[1] , reverse=True)
            Output = [0, 0, 0, 0, 100]
            resultData = [0, 0, 0, 0, 100]


            for feature in featuresArray:
                pixel_x = int(feature[0])
                pixel_y = int(feature[1])
                objectAngle = round(feature[2]-AngleZeroOffset, 1)

                if pixel_x <= 80 or pixel_x >= 550 or pixel_y <= 90 or pixel_y >= 650: 
                    continue    ##* 超過抓取邊界的跳過
                if objectAngle == 270: 
                    continue ##* 物件角度為270的跳過

                world_coordinate = vision.Coordinate_TF(pixel_x, pixel_y)
                Output[0] = round(world_coordinate[0], 3)
                Output[1] = round(world_coordinate[1], 3)
                Output[2] = round(world_coordinate[2], 3)
                Output[3] = (360 - objectAngle) % 360 + 90

                if Output[3] > 180:
                    Output[3] = round(Output[3] - 360, 2)
                
                angle = f"({Output[3]:.1f})"
                cv2.putText(frame, angle, (int(pixel_x+10),int(pixel_y+10)), cv2.FONT_HERSHEY_PLAIN,1.5,(255,64,255),2,8,0)

            ##* Transfer the Message to Letsview with UDP
            resultData = str(Output)
            UDP_socket.sendto(resultData.encode(), (targetIP, LetsviewPort))
            print (resultData)

            ##* 顯示最終結果圖(Result)與二值化圖(img_binary)
            
            cv2.imshow("img_binary", imgBinary)
            cv2.imshow("Result", frame)
            cv2.waitKey(1)

    cv2.destroyAllWindows()
    return 'closed'




if __name__ == "__main__":

    WorkMode_loop("白長樣品蓋")

    # ObjectContours("圓眼影")
    
    # CameraCalibration()


# cv2.destroyAllWindows()