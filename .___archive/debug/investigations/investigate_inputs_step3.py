"""Fast schema inspection - reads ONLY metadata, no data loading"""
import pyarrow.parquet as pq
from pathlib import Path

def inspect_schema(path, name):
    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"{'='*60}")
    
    if not Path(path).exists():
        print("  ERROR: File not found!")
        return
    
    # Read ONLY the schema (instant, no data loaded)
    schema = pq.read_schema(path)
    print(f"Columns ({len(schema)}):")
    for field in schema:
        print(f"  {field.name}: {field.type}")

root = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\1_Inputs")

# Compustat
inspect_schema(root / "comp_na_daily_all/comp_na_daily_all.parquet", "COMPUSTAT")

# IBES
inspect_schema(root / "tr_ibes/tr_ibes.parquet", "IBES")

# CCCL
inspect_schema(root / "CCCL instrument/instrument_shift_intensity_2005_2022.parquet", "CCCL Instrument")

# SDC
inspect_schema(root / "SDC/sdc-ma-merged.parquet", "SDC M&A")

# CRSP (sample)
inspect_schema(root / "CRSP_DSF/CRSP_DSF_2010_Q1.parquet", "CRSP DSF (Sample)")
