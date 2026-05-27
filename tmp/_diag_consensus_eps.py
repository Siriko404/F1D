"""Diagnostic: trace CONSENSUS_EPS data flow component by component.

Find WHICH layer (FPI filter, USFIRM, CURCODE, ESTFLAG, sample filter, scale)
explains the divergence from anchor (N=42K, mean=0.07, sd=3.51).
"""
import zipfile
import numpy as np
import pandas as pd

ROOT = r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D"

# Load IBES with all relevant cols
with zipfile.ZipFile(f"{ROOT}/inputs/tr_ibes/ibes_statsum.zip") as z:
    name = z.namelist()[0]
    with z.open(name) as f:
        ibes = pd.read_csv(f, dtype={"TICKER": "str", "OFTIC": "str", "CUSIP": "str"},
                            low_memory=False)
print(f"C1 raw load:                                       {len(ibes):>10,}")
print(f"  unique TICKERS: {ibes['TICKER'].nunique():,}")
print(f"  FPI value counts:\n{ibes['FPI'].value_counts().head(10)}")
print(f"  FISCALP counts:\n{ibes['FISCALP'].value_counts()}")
print(f"  USFIRM counts:\n{ibes['USFIRM'].value_counts()}")
print(f"  CURCODE counts:\n{ibes['CURCODE'].value_counts().head(5)}")
print(f"  ESTFLAG counts:\n{ibes['ESTFLAG'].value_counts()}")

# Step-by-step funnel
ibes["STATPERS"] = pd.to_datetime(ibes["STATPERS"])
ibes["FPEDATS"] = pd.to_datetime(ibes["FPEDATS"])

f2 = ibes[(ibes["MEASURE"] == "EPS") & (ibes["FISCALP"] == "QTR")]
print(f"\nC2a MEASURE=EPS & FISCALP=QTR:                    {len(f2):>10,}")

f2 = f2[(f2["FPEDATS"] >= "2010-01-01") & (f2["FPEDATS"] <= "2017-03-31")]
print(f"C2b + FPEDATS in window:                          {len(f2):>10,}")

f2 = f2[f2["STATPERS"] < f2["FPEDATS"]]
print(f"C2c + STATPERS before FPEDATS:                    {len(f2):>10,}")

# Apply paper-typical IBES filters one at a time
f3 = f2[f2["USFIRM"] == 1]
print(f"C3 + USFIRM=1:                                    {len(f3):>10,}")

# FPI filter — paper says "1-quarter-ahead"; IBES FPI=6 = 1Q-ahead quarterly forecast
# but FISCALP=QTR includes FPI 6/7/8/9 (Q+1, Q+2, Q+3, Q+4)
# Convert FPI to numeric (mixed-type col)
f3["FPI_n"] = pd.to_numeric(f3["FPI"], errors="coerce")
f4 = f3[f3["FPI_n"] == 6]
print(f"C4 + FPI=6 (1Q-ahead only):                       {len(f4):>10,}")

# CURCODE=USD
f5 = f4[f4["CURCODE"] == "USD"]
print(f"C5 + CURCODE=USD:                                 {len(f5):>10,}")

# ESTFLAG — IBES uses 'P' = primary EPS, 'D' = diluted. Paper likely uses primary.
print(f"  ESTFLAG counts at C5:\n{f5['ESTFLAG'].value_counts()}")
f6 = f5[f5["ESTFLAG"] == "P"]
print(f"C6 + ESTFLAG=P (Primary):                         {len(f6):>10,}")

# Dedup to latest STATPERS per (TICKER, FPEDATS)
f7 = f6.sort_values(["TICKER", "FPEDATS", "STATPERS"]).drop_duplicates(
    subset=["TICKER", "FPEDATS"], keep="last")
print(f"C7 dedup latest per (TICKER, FPEDATS):            {len(f7):>10,}")

# Map to gvkey via OFTIC = tic
comp_tic = pd.read_parquet(f"{ROOT}/inputs/comp_na_daily_all/comp_na_daily_all.parquet",
                            columns=["gvkey", "tic", "datadate"])
comp_tic["gvkey"] = comp_tic["gvkey"].astype(str).str.zfill(6)
comp_tic["datadate"] = pd.to_datetime(comp_tic["datadate"])
comp_tic = comp_tic[(comp_tic["datadate"] >= "2010-01-01") & (comp_tic["datadate"] <= "2017-03-31")]
comp_tic["cal_yr_qtr"] = (comp_tic["datadate"].dt.year * 10
                            + comp_tic["datadate"].dt.quarter).astype(np.int64)
comp_tic = comp_tic[["gvkey", "tic", "cal_yr_qtr"]].drop_duplicates()

# Build cal_yr_qtr for IBES (t = quarter BEFORE FPEDATS, since FPEDATS is the forecast TARGET)
f7 = f7.copy()
yr = f7["FPEDATS"].dt.year
qtr = f7["FPEDATS"].dt.quarter
prev_qtr = np.where(qtr == 1, 4, qtr - 1)
prev_yr = np.where(qtr == 1, yr - 1, yr)
f7["cal_yr_qtr"] = (prev_yr * 10 + prev_qtr).astype(np.int64)

merged = f7.merge(comp_tic, left_on=["OFTIC", "cal_yr_qtr"],
                   right_on=["tic", "cal_yr_qtr"], how="inner")
merged = merged.drop_duplicates(subset=["gvkey", "cal_yr_qtr"], keep="first")
print(f"C8 mapped to gvkey via OFTIC=tic:                 {len(merged):>10,}")

# Filter to SAMPLE gvkeys
import os
out_root = f"{ROOT}/outputs/campello_v2"
runs = sorted([d for d in os.listdir(out_root)
                if os.path.exists(f"{out_root}/{d}/variables_panel.parquet")], reverse=True)
panel = pd.read_parquet(f"{out_root}/{runs[0]}/variables_panel.parquet")
sample_gvkeys = set(panel["gvkey"].unique())
final = merged[merged["gvkey"].isin(sample_gvkeys)]
print(f"C9 filter to sample gvkeys (N={len(sample_gvkeys)}):       {len(final):>10,}")

# Distribution
s = final["MEANEST"].dropna()
print(f"\n--- Raw MEANEST distribution (no winsorization) ---")
print(f"N={len(s):,}  mean={s.mean():.3f}  sd={s.std():.3f}  median={s.median():.3f}")
print(f"p01={s.quantile(0.01):.3f}  p05={s.quantile(0.05):.3f}  p25={s.quantile(0.25):.3f}")
print(f"p75={s.quantile(0.75):.3f}  p95={s.quantile(0.95):.3f}  p99={s.quantile(0.99):.3f}")
print(f"min={s.min():.3f}  max={s.max():.3f}")

# Test winsorization at 1%/99% pooled
lo, hi = s.quantile(0.01), s.quantile(0.99)
s_w = s.clip(lo, hi)
print(f"\n--- After pooled 1%/99% winsorization ---")
print(f"N={len(s_w):,}  mean={s_w.mean():.3f}  sd={s_w.std():.3f}  median={s_w.median():.3f}")

print(f"\n>>> ANCHOR: N=42,031  mean=0.07  sd=3.51  median=0.09")
