import pandas as pd

CsvDir = r"./Cosmetic_parameter.csv"
FileName = pd.read_csv(CsvDir, encoding='BIG5').to_dict()
print(FileName)