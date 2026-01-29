
import pandas as pd
from pathlib import Path

path = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\1_Inputs\CCCL instrument\instrument_shift_intensity_2005_2022.parquet")
if path.exists():
    print("Found CCCL Instrument!")
    try:
        df = pd.read_parquet(path)
        print("Columns:", df.columns.tolist())
    except Exception as e:
        print(f"Error reading parquet: {e}")
else:
    print("File not found at expected path")
