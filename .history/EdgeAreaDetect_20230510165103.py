import Vision
import cv2
import numpy as np
import pandas as pd
from pandas import DataFrame

ProductName = "長樣品瓶"
ProductColor = "淺色"

CsvDir = r"./Cosmetic_parameter.csv"
FileName = pd.read_csv(CsvDir, encoding='BIG5').to_dict()
df = pd.DataFrame(FileName)


class ContourBoundaryIdent:
    def __init__(self):
        self.CheckPoint = [[320,240], [150,110], [150,375], [475,375], [475,110]]

    def AreaIdent(self):
        AreaSizeData = []
        for i, (x, y) in enumerate(self.CheckPoint):
            if cv2.waitKey(1) & 0xFF == 27: ## 27 = ESC
                break
            print('')
            while cv2.waitKey(1) & 0xFF != ord('q'):
                frame = cosmetic.ImageCatch(cap)
                cv2.circle(frame, (x, y), 5, (0,0,255), -1)
                cv2.imshow("Image", frame)
                print('請換下個位置，放置後請按Q',end='\r')
            print('')
            for i in range(100):
                print(f'請勿進入鏡頭範圍，目前搜尋數據量:{i+1}', end = '\r')
                frame = cosmetic.ImageCatch(cap)
                imgBinary = cosmetic.ImagePreProcess(frame)
                contoursList = cosmetic.ContoursCalc(imgBinary)
                for contour in contoursList:
                    if cv2.contourArea(contour) > 100:
                        AreaSizeData.append(cv2.contourArea(contour))
        cv2.drawContours(frame, contoursList, -1, (0,0,255), 2)
        cv2.waitKey(1)
        return AreaSizeData
    
    def SatisticsCalc(self, AreaSizeData):
        areaMeanCont = np.mean(np.array(AreaSizeData, dtype=object))
        areaStdCont = np.std(np.array(AreaSizeData,  dtype=float), axis=0, ddof=1)
        return areaMeanCont, areaStdCont

# class CSV_DataProcess:
#     def __init__(self, CsvDir):
#         FileName = pd.read_csv(CsvDir, encoding='BIG5').to_dict()
#         pass

#     def DataDownload(self):


if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = Vision.EdgeDetector(0)
    initial = ContourBoundaryIdent()

    areaSizeData = initial.AreaIdent()
    areaMeanCont, areaStdCont = initial.SatisticsCalc(AreaSizeData)

    resultData

    print(f'\nArea: Mean std Max-min\n{areaMeanCont:.4f},{areaStdCont:.4f},{max(AreaSizeData)-min(AreaSizeData):.4f}')
    

# product_dic = {
#     '產品名稱': [ProductName],
#     '面積大小': [partAreaMeanCont],
#     '面積標準差': [partAreaStdCont],
#     '最大-最小': [max(AreaSizeData)-min(AreaSizeData)],
#     '產品顏色': [ProductColor]
# }

# product_index = next((i for i, name in enumerate(product_dic['產品名稱']) if name == ProductName), None)

# if product_index is not None:
#     csvData = {
#         '產品名稱': [product_dic['產品名稱'][product_index]],
#         '面積大小': [product_dic['面積大小'][product_index]],
#         '面積標準差': [product_dic['面積標準差'][product_index]],
#         '最大-最小': [product_dic['最大-最小'][product_index]],
#         '產品顏色': [product_dic['產品顏色'][product_index]]
#     }
#     df = pd.DataFrame(csvData)
#     CsvDir = r"./Cosmetic_parameter.csv"
#     df.to_csv(CsvDir, index=False, encoding='BIG5')


cv2.destroyAllWindows()