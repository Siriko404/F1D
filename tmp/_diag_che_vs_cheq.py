"""Test if Table 8 'total cash holdings' = che (just cash) instead of cheq (cash+short-term).
Also test other COMPUSTAT cash-related fields."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname

# Check what cash-related columns are in compustat
comp = pd.read_parquet(ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet")
cash_cols = [c for c in comp.columns if 'ch' in c.lower() or 'cash' in c.lower()]
print(f"Cash-related columns in COMPUSTAT: {cash_cols}")

# Check coverage
for c in cash_cols:
    if c in comp.columns:
        nn = pd.to_numeric(comp[c], errors="coerce").notna().sum()
        print(f"  {c}: {nn:,} non-null obs")
