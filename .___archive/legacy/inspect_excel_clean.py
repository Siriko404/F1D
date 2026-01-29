import pandas as pd
import sys

input_path = r"c:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D/1_Inputs/CEO Dismissal Data 2021.02.03.xlsx"

try:
    df = pd.read_excel(input_path)
    print("COLUMNS_START")
    for col in df.columns:
        print(col)
    print("COLUMNS_END")
except Exception as e:
    print(f"Error reading Excel file: {e}")
