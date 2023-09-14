'''## * 濠瀛 視覺辨識主程式
Python version: 3.9.13
openCV version: 4.6.0

視覺辨識拆分為3個功能
    ObjectContours    -> 產品輪廓標定
    CameraCalibration -> 相機校正與對Robot標定(使用張氏標定法)
    WorkMode_loop     -> 視覺辨識
'''

import cv2
import socket
import HaoYing.Vision as Vision
import HaoYing.FileProcess as FP
import HaoYing.Setting as Setting

AngleZero_offset = 0 ##* 0度為x軸正向 順時針範圍0~G360度
CSV_path = r"C:\Users\TEST\Desktop\HaoYing_Final\ObjectVision\Data\Cosmetic_parameter.csv"
XML_path = r"C:\Users\TEST\Desktop\HaoYing_Final\ObjectVision\Data\Setting.xml"


def ObjectContours(object):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)    # Image catch
    initial = Setting.initialize(object)
    _, areaMean, areaStd = initial.AreaIdent()  # 輪廓面積平均值, 輪廓面積標準差
    cap.release()

    FP.CSVDataWrite(object, CSV_path, areaMean, areaStd)
    return 100


def CameraCalibration():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    initial = Setting.initialize(None)
    [cameraMatrix, rVecs, tVecs] = initial.CameraCalibration(cap) # 香雞
    cap.release()

    # Upload the calibration parameter to XML file
    calibration = {"camera_matrix": cameraMatrix, "rvecs": rVecs, "tvecs": tVecs}
    for i in calibration:
        FP.XMLWrite(XML_path, str(i), [[float(num) for num in row] for row in calibration[str(i)]])

    return 100


def WorkMode_loop(Object):
    # UDP setup
    target_ip = '127.0.0.1'
    LV_port = 65235
    PY_port = 65234

    # Build UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((target_ip, PY_port))

    # Set the Timeout to 0.15 sec
    udp_socket.settimeout(0.15)

    TF_para = {"camera_matrix": 0, "rvecs": 0, "tvecs": 0}
    for i in TF_para:
        TF_para[i] = FP.XMLRead(XML_path, str(i))
    
    #TODO: 改名
    csv_path = FP.CSVDataLoad(CSV_path, Object)
    vision = Vision.EdgeDetector(2, TF_para, Object, csv_path,)

    while True:
        try:
            data, sender = udp_socket.recvfrom(1024)
            # print(f"從 {sender} 收到訊息: {data.decode()}")
            if (data.decode() == 'close'):
                # print("關閉連線")
                break
        except ConnectionResetError:
            pass
            # print("遠端主機已強制關閉連線。")
        except socket.timeout: 
            frame = vision.ImageCatch()
            img_binary = vision.ImagePreProcess(frame)
            try:
                global result_array
                contours = vision.ContoursCalc(img_binary)
                frame, result_array, _ = vision.FeaturesCalc(frame, contours)
                result_array.sort(key=lambda x:x[1] , reverse=True)
                Output = [0, 0, 0, 0, 100]

                for result in result_array:
                    pixel_x = int(result[0])
                    pixel_y = int(result[1])
                    object_angle = round(result[2]-AngleZero_offset, 1)

                    if pixel_x <= 100 or pixel_x >= 550 or pixel_y <= 90 or pixel_y >= 600:
                        continue
                    
                    if object_angle == 270:
                        continue

                    world_coordinate = vision.Coordinate_TF(pixel_x, pixel_y)
                    Output[0] = round(world_coordinate[0], 3)
                    Output[1] = round(world_coordinate[1], 3)
                    Output[2] = round(world_coordinate[2], 3)
                    Output[3] = (360 - object_angle) % 360 + 90

                    if Output[3] > 180:
                        Output[3] = round(Output[3] - 360, 2)
                    
                    text = f"({Output[3]:.1f})"
                    cv2.putText(frame, text, (int(pixel_x+10),int(pixel_y+10)), cv2.FONT_HERSHEY_PLAIN,1.5,(255,64,255),2,8,0)

                    # 將訊息透過UDP發送到目標
                    text = str(Output)
                    udp_socket.sendto(text.encode(), (target_ip, LV_port))
            # print(f"訊息 {Output} 已經成功傳送")
            except:
                pass

                    
            # except:
            cv2.imshow("Result", frame)
            cv2.imshow("img_binary", img_binary)
            cv2.waitKey(1)
            #continue

    cv2.destroyAllWindows()
    return 'closed'










if __name__ == "__main__":

    WorkMode_loop("圓眼影")

    # ObjectContours("圓眼影")

    # CameraCalibration()


# cv2.destroyAllWindows()