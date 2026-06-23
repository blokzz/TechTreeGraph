import pandas as pd
import numpy as np

def preprocess_data():
    """
    Preprocessing data from Civ6Techs.csv.
    Returns a pandas DataFrame with the preprocessed data.
    """
    df = pd.read_csv("Civ6Techs.csv", encoding="cp1250")
    df = df.drop(columns=df.columns[2:5])
    df['Science_cost'] = df['Science_cost'].fillna(0).astype(int)
    df['Leads to'] = df['Leads to'].str.split('\n')
    df = df.replace(r'[\n\t]', ' ', regex=True).replace(np.nan, "None")
    return df
