from pandas import read_csv, DataFrame
import xml.etree.ElementTree as XET
import numpy as np

##@ 將界定好的輪廓面積範圍送至.csv檔
def CSVDataWrite(productName="", csv="", data="", mean="", std=""): 
    fileName = read_csv(csv, encoding='BIG5').to_dict()
    csvData = DataFrame(fileName)
    product_index = next((key for key,name in fileName.get('產品名稱').items() if name == productName), None)
    resultData = [mean, std, max(data)-min(data)]
    csvData.loc[[product_index], ["面積平均","面積標準差", "最大-最小"]] = resultData

    csvData.to_csv(csv, index=False, encoding='BIG5')

def CSVDataLoad(csv="", productName=""):
    product_dic    = read_csv(csv, encoding='BIG5').to_dict()
    product_index  = next((key for key,name in product_dic.get('產品名稱').items() if name == productName), None)
    Area_Avg       = product_dic.get('面積平均').get(product_index)
    Area_Std       = product_dic.get('面積標準差').get(product_index)
    product_color  = product_dic.get('產品顏色').get(product_index)
    catchOffset    = product_dic.get('吸取點').get(product_index)
    product_height = product_dic.get('物件橫躺高度').get(product_index)
    return Area_Avg, Area_Std, product_color, catchOffset, product_height

def XMLWrite(path, tag, messages):
    tree = XET.parse(path)
    root = tree.getroot()
    for subnode in root.findall(tag):
        subnode.text = str(messages)
    tree.write(path)

def XMLRead(path, tag):
    tree = XET.parse(path)
    root = tree.getroot()
    return root.find(tag).text