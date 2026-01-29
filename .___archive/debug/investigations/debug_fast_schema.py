
import pyarrow.parquet as pq
from pathlib import Path

path = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\1_Inputs\comp_na_daily_all\comp_na_daily_all.parquet")
if path.exists():
    pf = pq.ParquetFile(path)
    print("Columns:", pf.schema.names)
else:
    print("File not found")
