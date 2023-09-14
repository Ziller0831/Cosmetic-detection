'''
********************************
    HaoYing 視覺辨識 主程式
********************************
變數前方有底線的為區域變數(函式)

Python version: 3.9.13
openCV version: 4.6.0

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
CurrentDir = os.getcwd()
CSV_path = os.path.join(CurrentDir, "./Data/Cosmetic_parameter.csv")
XML_path = os.path.join(CurrentDir, "./Data/Setting.xml")



def ObjectContours(object):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)    # Image catch
    initial = Setting.initialize(object, CSV_path)
    _, areaMean, areaStd = initial.AreaIdent()  # 輪廓面積平均值, 輪廓面積標準差
    cap.release()

    FP.CSVDataWrite(object, CSV_path, areaMean, areaStd)
    return 100


def CameraCalibration():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    initial = Setting.initialize(None)
    [cameraMatrix, rVecs, tVecs] = initial.CameraCalibration(cap) # 相機畸變參數矩陣, 旋轉向量, 平移向量
    cap.release()

    # Upload the calibration parameter to XML file
    calibration = {"camera_matrix": cameraMatrix, "rvecs": rVecs, "tvecs": tVecs}
    for i in calibration:
        FP.XMLWrite(XML_path, str(i), [[float(num) for num in row] for row in calibration[str(i)]])

    return 100


def WorkMode_loop(Object):
    # UDP setup
    targetIP = '127.0.0.1'
    LetsviewPort = 65235
    python_port = 65234

    # Build UDP socket
    UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDP_socket.bind((target_ip, python_port))

    # Set the Timeout to 0.15 sec
    UDP_socket.settimeout(0.15)

    # Load the calibration parameters
    TF_para = {"camera_matrix": 0, "rvecs": 0, "tvecs": 0}
    for i in TF_para:
        TF_para[i] = FP.XMLRead(XML_path, str(i))
    

    objectData = FP.CSVDataLoad(CSV_path, Object)
    vision = Vision.EdgeDetector(2, TF_para, objectData)
    while True:
        try:
            UDP_recvMessage,_ = UDP_socket.recvfrom(1024)
            if (UDP_recvMessage.decode() == 'close'): break

        except ConnectionResetError: pass
        
        except socket.timeout: 
            frame = vision.ImageCatch()
            imgBinary = vision.ImagePreProcess(frame)
            try:
                contours = vision.ContoursCalc(imgBinary)
                frame, featuresArray, _ = vision.FeaturesCalc(frame, contours)
                featuresArray.sort(key=lambda x:x[1] , reverse=True)
                Output = [0, 0, 0, 0, 100]

                for result in featuresArray:
                    pixel_x = int(result[0])
                    pixel_y = int(result[1])
                    objectAngle = round(result[2]-AngleZeroOffset, 1)

                    if pixel_x <= 100 or pixel_x >= 550 or pixel_y <= 90 or pixel_y >= 600:
                        continue
                    
                    if objectAngle == 270:
                        continue

                    world_coordinate = vision.Coordinate_TF(pixel_x, pixel_y)
                    Output[0] = round(world_coordinate[0], 3)
                    Output[1] = round(world_coordinate[1], 3)
                    Output[2] = round(world_coordinate[2], 3)
                    Output[3] = (360 - objectAngle) % 360 + 90

                    if Output[3] > 180:
                        Output[3] = round(Output[3] - 360, 2)
                    
                    angle = f"({Output[3]:.1f})"
                    cv2.putText(frame, angle, (int(pixel_x+10),int(pixel_y+10)), cv2.FONT_HERSHEY_PLAIN,1.5,(255,64,255),2,8,0)

                    # Transfer the Message to Letsview with UDP
                    resultData = str(Output)
                    UDP_socket.sendto(resultData.encode(), (target_ip, Letview_port))

            except: pass

                    
            # except:
            cv2.imshow("Result", frame)
            cv2.imshow("img_binary", imgBinary)
            cv2.waitKey(1)
            #continue

    cv2.destroyAllWindows()
    return 'closed'










if __name__ == "__main__":

    WorkMode_loop("圓眼影")

    # ObjectContours("圓眼影")

    # CameraCalibration()


# cv2.destroyAllWindows()