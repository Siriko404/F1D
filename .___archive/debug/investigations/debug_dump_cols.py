
import pandas as pd
from pathlib import Path

# Dump CRSP Cols
try:
    crsp_path = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\1_Inputs\CRSP_DSF\CRSP_DSF_2002_Q1.parquet")
    if crsp_path.exists():
        df = pd.read_parquet(crsp_path)
        with open("cols_crsp.txt", "w") as f:
            f.write("\n".join(df.columns.tolist()))
    else:
        with open("cols_crsp.txt", "w") as f:
            f.write("CRSP File not found")
except Exception as e:
    with open("cols_crsp.txt", "w") as f:
        f.write(f"Error: {e}")

# Dump Unified Info Cols
try:
    unified_path = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\1_Inputs\Unified-info.parquet")
    if unified_path.exists():
        df = pd.read_parquet(unified_path)
        with open("cols_unified.txt", "w") as f:
            f.write("\n".join(df.columns.tolist()))
    else:
        with open("cols_unified.txt", "w") as f:
            f.write("Unified Info File not found")
except Exception as e:
    with open("cols_unified.txt", "w") as f:
        f.write(f"Error: {e}")
