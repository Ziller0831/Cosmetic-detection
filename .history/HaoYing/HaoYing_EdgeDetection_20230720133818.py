'''## * 濠瀛 視覺辨識主程式
Python version: 3.9.13
openCV version: 4.6.0
numpy  version: 1.23.5
pandas version: 1.5.3
'''

import cv2
from time import time
import Vision 
import Setting
import FileProcess as FP
import TCP

Choose_product = "長樣品蓋"
Mode = 2
fps = 30            
AngleZero_offset = 0 ##* 0度為x軸正向 順時針範圍0~G360度
Csv_Dir = r"./HaoYing/Cosmetic_parameter.csv"
TCP_host = "0.0.0.0"
TCP_port = "7000"

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if __name__ == "__main__":
    time_start = time()

    if Mode == 0:  ##! 物件輪廓選擇mode
        initial = Setting.initialize()
        area_size, area_mean, area_std = initial.AreaIdent(cap)
        FP.CSVDataWrite(Choose_product, Csv_Dir, area_size, area_mean, area_std)

    elif Mode == 1: ##! 相機標定mode
        initial = Setting.initialize()
        [camera_matrix, rvecs, tvecs] = initial.CameraCalibration(cap)
        calibration = {"camera_matrix": camera_matrix, "rvecs": rvecs, "tvecs": tvecs}

        for i in calibration:
            FP.XMLWrite(r".\HaoYing\Setting.xml", str(i),  [[float(num) for num in row] for row in calibration[str(i)]])
    
    elif Mode == 2: ##! working mode
        TF_para = {"camera_matrix": 0, "rvecs": 0, "tvecs": 0}
        for i in TF_para:
            TF_para[i] = FP.XMLRead(r".\HaoYing\Setting.xml", str(i))

        vision = Vision.EdgeDetector(Mode, Choose_product, TF_para)
        time_start = time()

        while True:
            frame = vision.ImageCatch(cap)
            img_binary = vision.ImagePreProcess(frame)
            contours = vision.ContoursCalc(img_binary)
            frame, result_array, _ = vision.FeaturesCalc(frame, contours)

            results_mean = vision.FPSBuffer(fps, result_array)
            # print(results_mean)

            for result in results_mean:
                pixel_x = int(result[0])
                pixel_y = int(result[1])
                # pixel_z = int(result[2])
                object_angle = result[2]-AngleZero_offset

                text = f"({pixel_x}, {pixel_y}, {object_angle:.1f})"

                cv2.putText(frame, text, (int(pixel_x+10),int(pixel_y+10)), cv2.FONT_HERSHEY_PLAIN,1.5,(255,64,255),2,8,0)
                world_x, world_y = vision.Coordinate_TF([pixel_x, pixel_y, 1])

                # print(text)
            # recall = TCP.Client(TCP_host, TCP_port, text)
            # print(recall)

            fps = round(1/(time()-time_start), 2)

            cv2.putText(frame, f"fps:{str(fps)}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
            cv2.imshow("Result", frame)

            time_start = time()
            if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
                break

cap.release()
cv2.destroyAllWindows()
