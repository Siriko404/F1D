
import pandas as pd
from pathlib import Path

path = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\1_Inputs\CRSPCompustat_CCM\CRSPCompustat_CCM.parquet")
if path.exists():
    df = pd.read_parquet(path)
    cols = set(df.columns)
    required = {'at', 'dltt', 'dlc', 'ceq', 'csho', 'prcc_f', 'mkvalt', 'ni', 'ib'}
    found = required.intersection(cols)
    missing = required - cols
    print(f"Found: {sorted(list(found))}")
    print(f"Missing: {sorted(list(missing))}")
else:
    print("File not found")
