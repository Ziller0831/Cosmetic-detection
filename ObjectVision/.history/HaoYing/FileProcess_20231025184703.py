'''
********************************
    HaoYing 變數儲存 副程式
********************************
負責從xml跟csv中載入變數或儲存變數的程式
CSV 儲存辨識物件的參數
XML 儲存相機標定與校正的結果

架構：
    +-- def CSVDataWrite(物件名稱, CSV路徑, 輪廓面積平均, 輪廓面積標準差)
    |
    +-- def CSVDataLoad(CSV路徑)
    |
    +-- def XMLWrite
    |
    +-- def XMLRead
'''

from pandas import read_csv, DataFrame
import xml.etree.ElementTree as XET
import numpy as np
import ast


##@ Rewrite .csv data
def CSVDataWrite(productName="", csvPath="", areaMean="", areaStd=""):
    csv_data = read_csv(csvPath, encoding='BIG5')
    
    # 尋找符合productName的行索引
    productIndex = csv_data[csv_data['產品名稱'] == productName].index
    if not productIndex.empty:
        # 如果找到了，更新該行的特定列的值
        csv_data.loc[productIndex, ["面積平均", "面積標準差"]] = [areaMean, areaStd]
        csv_data.to_csv(csvPath, index=False, encoding='BIG5')
    else:
        print(f"產品名稱 {productName} 在CSV中未找到。")
##@ -----------------------------------------------------


##@ Load .csv data
def CSVDataLoad(csvPath="", productName=""):
    productDic    = read_csv(csvPath, encoding='BIG5').to_dict()
    productIndex  = next((key for key,name in productDic.get('產品名稱').items() if name == productName), None)

    areaMean      = productDic.get('面積平均').get(productIndex)
    areaStd       = productDic.get('面積標準差').get(productIndex)
    productColor  = productDic.get('產品顏色').get(productIndex)
    catchOffset   = productDic.get('吸取點').get(productIndex)
    productHeight = productDic.get('物件橫躺高度').get(productIndex)

    return areaMean, areaStd, productColor, catchOffset, productHeight
##@ -----------------------------------------------------


##@ Rewrite .xml data
def XMLWrite(path, tag, message):
    tree = XET.parse(path)
    root = tree.getroot()
    for subnode in root.findall(tag):
        subnode.text = str(message)
    tree.write(path)
##@ -----------------------------------------------------


##@ Load .xml data
def XMLRead(path, *tag):
    tree = XET.parse(path)
    root = tree.getroot()
    for i in range(0, len(tag)):
        return  np.array(ast.literal_eval(root.find(tag[i]).text ))
##@ -----------------------------------------------------