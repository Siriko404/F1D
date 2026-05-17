"""Decisive check: is step1's 321,853 genuinely 2010Q1-2016Q4, or did the
2002-2018 raw leak through (window filter / grain bug)? Read-only.
"""
import sys
from pathlib import Path
import pyarrow.parquet as pq
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
S1 = sorted((ROOT / "outputs" / "campello_rebuild" / "step1_sample").iterdir())[-1] / "sample.parquet"

raw = pq.read_table(RAW, columns=["gvkey", "datadate"]).to_pandas()
raw["datadate"] = pd.to_datetime(raw["datadate"], errors="coerce")
print("=== RAW comp_na_daily_all ===")
print(f"  rows={len(raw):,}  gvkeys={raw['gvkey'].nunique():,}")
print(f"  datadate min={raw['datadate'].min()}  max={raw['datadate'].max()}")
print(f"  rows in 2010-01..2016-12 = "
      f"{raw['datadate'].between('2010-01-01','2016-12-31').sum():,}")

s1 = pq.read_table(S1, columns=["gvkey", "datadate", "cal_yr_qtr"]).to_pandas()
s1["datadate"] = pd.to_datetime(s1["datadate"], errors="coerce")
print(f"\n=== STEP1 OUTPUT  {S1} ===")
print(f"  rows={len(s1):,}  gvkeys={s1['gvkey'].nunique():,}")
print(f"  datadate min={s1['datadate'].min()}  max={s1['datadate'].max()}")
print(f"  unique (gvkey,datadate) = {s1.duplicated(['gvkey','datadate']).eq(False).sum():,}"
      f"  (dups={int(s1.duplicated(['gvkey','datadate']).sum())})")
print(f"  cal_yr_qtr min={s1['cal_yr_qtr'].min()} max={s1['cal_yr_qtr'].max()}")
print("  rows per calendar year:")
print(s1["datadate"].dt.year.value_counts().sort_index().to_string())
