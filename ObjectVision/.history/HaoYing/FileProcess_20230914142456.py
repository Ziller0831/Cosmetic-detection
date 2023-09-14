'''## * HaoYing 視覺辨識主程式
************
Python version: 3.9.13
openCV version: 4.6.0

視覺辨識拆分為3個功能
    ObjectContours    -> 產品輪廓標定
    CameraCalibration -> 相機校正與對Robot標定(使用張氏標定法)
    WorkMode_loop     -> 視覺辨識
'''

from pandas import read_csv, DataFrame
import xml.etree.ElementTree as XET
import numpy as np
import ast


##@ Rewrite .csv data
def CSVDataWrite(productName="", csvPath="", areaMean="", areaStd=""):
    fileName = read_csv(csvPath, encoding='BIG5').to_dict() 
    productIndex = next((key for key, name in fileName.get('global result_array').items() if name == productName), None)
    resultData = [areaMean, areaStd]

    csv_data = DataFrame(fileName)
    csv_data.loc[[productIndex], ["面積平均","面積標準差"]] = resultData
    csv_data.to_csv(csvPath, index = False, encoding = 'BIG5')


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


##@ Rewrite .xml data
def XMLWrite(path, tag, message):
    tree = XET.parse(path)
    root = tree.getroot()
    for subnode in root.findall(tag):
        subnode.text = str(message)
    tree.write(path)


##@ Load .xml data
def XMLRead(path, *tag):
    tree = XET.parse(path)
    root = tree.getroot()
    for i in range(0, len(tag)):
        return  np.array(ast.literal_eval(root.find(tag[i]).text ))