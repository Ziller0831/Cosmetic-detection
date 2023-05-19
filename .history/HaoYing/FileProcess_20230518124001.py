from pandas import read_csv, DataFrame

##@ 將界定好的輪廓面積範圍送至.csv檔
def CSVDataInput(productName="", csv="", data="", mean="", std=""):
    fileName = read_csv(csv, encoding='BIG5').to_dict()
    csvData = DataFrame(fileName)
    product_index = next((key for key,name in fileName.get('產品名稱').items() if name == productName), None)
    resultData = [mean, std, max(data)-min(data)]
    csvData.loc[[product_index], ["面積平均","面積標準差", "最大-最小"]] = resultData

    csvData.to_csv(csv, index=False, encoding='BIG5')

def TxTInput(path):
    with open(path) as 

