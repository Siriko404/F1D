#!/usr/bin/env python3
"""Verify which of inputs/SDC/Filters.txt are actually reflected in sdc-ma-merged.parquet."""
import pandas as pd, numpy as np
from pathlib import Path

P = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\inputs\SDC\sdc-ma-merged.parquet")
df = pd.read_parquet(P)
n = len(df)
print(f"NROWS {n:,}\nCOLS {list(df.columns)}\n")

def vc(col, top=15):
    if col not in df.columns:
        print(f"[{col}] -- COLUMN ABSENT"); return
    print(f"[{col}] nulls={df[col].isna().sum():,}")
    print(df[col].astype(str).value_counts(dropna=False).head(top).to_string())
    print()

# Filter 1: financials (SIC 6000-6999) / utilities (4900-4949)
def sic_band(col):
    if col not in df.columns: print(f"  {col} ABSENT"); return
    s = pd.to_numeric(df[col], errors="coerce")
    fin = s.between(6000, 6999).sum(); util = s.between(4900, 4949).sum()
    print(f"  {col}: financial(6000-6999)={fin:,}  utility(4900-4949)={util:,}  nonnull={s.notna().sum():,}")
print("=== F1 financials/utilities (SIC) ===")
sic_band("Acquiror SIC"); sic_band("Target SIC")
print()

# Dates / range (F6 dedup context, sample window)
da = pd.to_datetime(df["Date Announced"], errors="coerce")
print(f"=== Date Announced: min {da.min()} max {da.max()} nulls {da.isna().sum():,} ===\n")

# F3/F4/F5 deal-type fields
print("=== F3/F4/F5 deal-type / form fields ===")
for c in ["Form of the Deal", "M&A Type", "Deal Type", "SDC Deal Type"]:
    vc(c)

# F6: duplicates per acquiror-target pair (earliest-only?)
print("=== F6 earliest-per-bid ===")
print(f"  SDC Deal No unique? {df['SDC Deal No'].is_unique}  (n unique {df['SDC Deal No'].nunique():,})")
pair = df.groupby(["Acquiror 6-digit CUSIP", "Target 6-digit CUSIP"]).size()
print(f"  acq-tgt CUSIP pairs: {len(pair):,}  pairs with >1 row: {(pair>1).sum():,}  max rows/pair: {pair.max()}")
print()

# F7: min deal value $1M
print("=== F7 deal value >= $1M ===")
dv = pd.to_numeric(df["Deal Value (USD Millions)"], errors="coerce")
print(f"  nonnull {dv.notna().sum():,}  null {dv.isna().sum():,}  min {dv.min()}  <1M {((dv<1)).sum():,}  ==0 {(dv==0).sum():,}")
print(f"  pctiles {np.round(dv.quantile([.0,.01,.05,.5]).values,4)}")
print()

# F9: US targets ; acquirer nation
print("=== F9 target nation / acquirer nation ===")
vc("Target Nation"); vc("Acquiror Nation")

# F10: hostile present?
print("=== F10 Deal Attitude ===")
vc("Deal Attitude")

# Public status (context)
print("=== Public status (context) ===")
vc("Target Public Status"); vc("Acquiror Public Status"); vc("Deal Status")
