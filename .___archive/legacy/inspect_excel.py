import pandas as pd
import sys

input_path = r"c:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D/1_Inputs/CEO Dismissal Data 2021.02.03.xlsx"

try:
    df = pd.read_excel(input_path)
    print("Columns:", df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head().to_string())
    print("\nData Types:")
    print(df.dtypes)
except Exception as e:
    print(f"Error reading Excel file: {e}")
