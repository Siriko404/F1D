import pandas as pd
from pathlib import Path
import os

print("--- CRSP CHECK ---")
crsp_path = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\1_Inputs\CRSP_DSF\CRSP_DSF_2002_Q1.parquet")
if crsp_path.exists():
    df = pd.read_parquet(crsp_path)
    cols = set(df.columns)
    required = {'PRC', 'VOL', 'ASKHI', 'BIDLO', 'dhi', 'dlo', 'prc', 'vol'}
    found = required.intersection(cols)
    print(f"CRSP Columns found: {sorted(list(found))}")
    print(f"Sample cols: {list(cols)[:5]}")
else:
    print("CRSP not found")

print("\n--- UNIFIED INFO CHECK ---")
unified_path = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\1_Inputs\Unified-info.parquet")
if unified_path.exists():
    df = pd.read_parquet(unified_path)
    cols = [c for c in df.columns if 'CCCL' in c.upper() or 'SHIFT' in c.upper()]
    print(f"Unified Info potential matches: {cols}")
else:
    print("Unified Info not found")

print("\n--- FILE SEARCH ---")
root = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\1_Inputs")
for path in root.rglob("*"):
    if "AUDIT" in path.name.upper() or "CCCL" in path.name.upper() or "SHIFT" in path.name.upper():
        print(f"Found candidate file: {path.name}")
