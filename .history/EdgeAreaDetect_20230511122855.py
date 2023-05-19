import Vision
import cv2
import numpy as np
import pandas as pd

ProductName = "長樣品瓶"
# ProductColor = "長樣品蓋"

CsvDir = r"./Cosmetic_parameter.csv"


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

def CSVDataInput(csv="", data="", mean, std):
    fileName = pd.read_csv(csv, encoding='BIG5').to_dict()
    csvData = pd.DataFrame(fileName)
    product_index = next((key for key,name in fileName.get('產品名稱').items() if name == ProductName), None)
    resultData = [mean, std, max(data)-min(data)]
    csvData.loc[[product_index], ["面積平均","面積標準差", "最大-最小"]] = resultData

    csvData.to_csv(csv, index=False, encoding='BIG5')


if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cosmetic = Vision.EdgeDetector(0)
    initial = ContourBoundaryIdent()

    areaSizeData = initial.AreaIdent()
    areaMeanCont, areaStdCont = initial.SatisticsCalc(areaSizeData)

    CSVDataInput(CsvDir)



    print(f'\nArea: Mean std Max-min\n{areaMeanCont:.4f},{areaStdCont:.4f},{max(areaSizeData)-min(areaSizeData):.4f}')
    


cv2.destroyAllWindows()