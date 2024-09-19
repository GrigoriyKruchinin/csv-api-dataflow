import pandas as pd


def extract_ticker(row: pd.Series) -> str:
    for value in row:
        value_str = str(value)
        if 2 <= len(value_str) <= 6 and value_str.isupper():
            return value_str
    return None
