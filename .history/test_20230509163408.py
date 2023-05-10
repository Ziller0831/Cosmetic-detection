import pandas as pd

data = {
    'Name': ['John', 'Alice', 'Bob'],
    'Age': [25, 30, 35],
    'Country': ['USA', 'Canada', 'UK']
}

filename = 'data.csv'

df = pd.DataFrame(data)
df.to_csv(filename, index=False)

print("Data has been written to", filename)