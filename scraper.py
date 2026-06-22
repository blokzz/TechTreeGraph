import pandas as pd

df = pd.read_csv("Civ6Techs.csv", encoding="cp1250")
print(df.columns.tolist())
print(df.iloc[0])