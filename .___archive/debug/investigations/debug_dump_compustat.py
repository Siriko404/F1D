
import pandas as pd
from pathlib import Path

try:
    path = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\1_Inputs\comp_na_daily_all\comp_na_daily_all.parquet")
    if path.exists():
        df = pd.read_parquet(path)
        with open("cols_compustat_daily.txt", "w") as f:
            f.write("\n".join(df.columns.tolist()))
    else:
        with open("cols_compustat_daily.txt", "w") as f:
            f.write("Comp Daily File not found")
except Exception as e:
    with open("cols_compustat_daily.txt", "w") as f:
        f.write(f"Error: {e}")
