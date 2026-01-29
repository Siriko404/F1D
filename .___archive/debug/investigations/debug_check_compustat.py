
import pandas as pd
from pathlib import Path

path = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\1_Inputs\CRSPCompustat_CCM\CRSPCompustat_CCM.parquet")
if path.exists():
    df = pd.read_parquet(path)
    print("Combined Stats:")
    print("Columns:", df.columns.tolist())
else:
    print("File not found at main path, checking subfiles...")
    root = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\1_Inputs\CRSPCompustat_CCM")
    for p in root.glob("*.parquet"):
        try:
            df = pd.read_parquet(p)
            print(f"File: {p.name}")
            print(f"Columns: {df.columns.tolist()[:50]}") # First 50
        except:
            pass
