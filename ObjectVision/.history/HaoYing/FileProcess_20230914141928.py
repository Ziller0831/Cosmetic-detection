from pandas import read_csv, DataFrame
import xml.etree.ElementTree as XET
import numpy as np
import ast


##@ 將界定好的輪廓面積範圍送至.csv檔
def CSVDataWrite(productName="", csvPath="", mean="", std=""):
    fileName = read_csv(csvPath, encoding='BIG5').to_dict() 
    productIndex = next((key for key, name in fileName.get('global result_array').items() if name == productName), None)
    resultData = [mean, std]

    csv_data = DataFrame(fileName)
    csv_data.loc[[productIndex], ["面積平均","面積標準差"]] = resultData
    csv_data.to_csv(csvPath, index = False, encoding = 'BIG5')


def CSVDataLoad(csvPath="", productName=""):
    productDic    = read_csv(csvPath, encoding='BIG5').to_dict()
    productIndex  = next((key for key,name in productDic.get('產品名稱').items() if name == productName), None)

    areaAvg       = productDic.get('面積平均').get(productIndex)
    areaStd       = productDic.get('面積標準差').get(productIndex)
    productColor  = productDic.get('產品顏色').get(productIndex)
    catchOffset   = productDic.get('吸取點').get(productIndex)
    productHeight = productDic.get('物件橫躺高度').get(productIndex)

    return area_avg, area_std, product_color, catch_offset, product_height


def XMLWrite(path, tag, message):
    tree = XET.parse(path)
    root = tree.getroot()
    for subnode in root.findall(tag):
        subnode.text = str(message)
    tree.write(path)


def XMLRead(path, *tag):
    tree = XET.parse(path)
    root = tree.getroot()
    for i in range(0, len(tag)):
        return  np.array(ast.literal_eval(root.find(tag[i]).text ))