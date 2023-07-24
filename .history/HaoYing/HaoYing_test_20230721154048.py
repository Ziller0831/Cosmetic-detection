'''## * 濠瀛 視覺辨識主程式
Python version: 3.9.13
openCV version: 4.6.0
numpy  version: 1.23.5
pandas version: 1.5.3
'''

import cv2
import HaoYing.Vision as Vision
import HaoYing.FileProcess as FP
import HaoYing.Setting as Setting
import HaoYing.TCP as TCP

import os

Choose_product = "長樣品蓋"
Mode = 2          
AngleZero_offset = 0 ##* 0度為x軸正向 順時針範圍0~G360度
TCP_host = "0.0.0.0"
TCP_port = "7000"

# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)


# def ObjectContours(Choose_product, Csv_Dir):  ##! 物件輪廓選擇mode
#     initial = Setting.initialize()
#     area_size, area_mean, area_std = initial.AreaIdent(cap)
#     FP.CSVDataWrite(Choose_product, Csv_Dir, area_size, area_mean, area_std)

# def CameraCalibration(Mode = 1):
#     initial = Setting.initialize()
#     [camera_matrix, rvecs, tvecs] = initial.CameraCalibration(cap)
#     calibration = {"camera_matrix": camera_matrix, "rvecs": rvecs, "tvecs": tvecs}

#     for i in calibration:
#         FP.XMLWrite(r".\HaoYing\Setting.xml", str(i),  [[float(num) for num in row] for row in calibration[str(i)]])



def WorkMode(Product):
    home = os.getcwd()
home
    TF_para = {"camera_matrix": 0, "rvecs": 0, "tvecs": 0}
    for i in TF_para:
        TF_para[i] = FP.XMLRead(r"E:\HaoYing\Setting.xml", str(i))
    
    frame = cv2.imread('E:\HaoYing\circle.png')
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

    product_features = FP.CSVDataLoad("E:\HaoYing\Cosmetic_parameter.csv", Product)
    vision = Vision.EdgeDetector(2, TF_para, product_features)
    output = [0, 0, 0, 0, 0]

    # frame = vision.ImageCatch(cap)
    img_binary = vision.ImagePreProcess(frame)
    contours = vision.ContoursCalc(img_binary)
    frame, result_array, _ = vision.FeaturesCalc(frame, contours)
        

    for result in result_array:
        pixel_x = int(result[0])
        pixel_y = int(result[1])
        object_angle = round(result[2]-AngleZero_offset, 1)

        text = f"({pixel_x}, {pixel_y}, {object_angle:.1f})"

        cv2.putText(frame, text, (int(pixel_x+10),int(pixel_y+10)), cv2.FONT_HERSHEY_PLAIN,1.5,(255,64,255),2,8,0)
        world_coordinate = vision.Coordinate_TF(pixel_x, pixel_y)
        output[0] = round(world_coordinate[0], 3)
        output[1] = round(world_coordinate[1], 3)
        output[2] = round(world_coordinate[2], 3)
        output[3] = object_angle
        output[4] = 70
        
    cv2.imshow("Result", frame)

    cv2.waitKey(2000)
    return output

if __name__ == "__main__":
    # time_start = time()
    x, y, z, angle, speed = WorkMode("長樣品蓋")

    print(x, y, z, angle, speed)
    


# cap.release()
cv2.destroyAllWindows()
