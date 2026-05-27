"""Test alt CONSENSUS_EPS scalings to find one matching anchor mean=0.07, sd=3.51."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")

# Load IBES tr_ibes yearly files
ibes_dir = ROOT / "inputs" / "tr_ibes"
frames = []
cols_want = ["TICKER", "OFTIC", "CUSIP", "STATPERS", "MEASURE", "FISCALP", "FPI",
             "MEANEST", "MEDEST", "FPEDATS", "USFIRM", "CURCODE", "ACTUAL", "STDEV"]
for y in range(2009, 2018):
    fp = ibes_dir / f"tr_ibes_{y}.parquet"
    if fp.exists():
        df = pd.read_parquet(fp)
        keep = [c for c in cols_want if c in df.columns]
        frames.append(df[keep])
ibes = pd.concat(frames, ignore_index=True)
print(f"Loaded IBES: {len(ibes):,} rows, columns={list(ibes.columns)}")

ibes["STATPERS"] = pd.to_datetime(ibes["STATPERS"])
ibes["FPEDATS"] = pd.to_datetime(ibes["FPEDATS"])
ibes = ibes[(ibes["MEASURE"] == "EPS")
            & (ibes["FISCALP"] == "QTR")
            & (ibes["FPI"] == "6")
            & (ibes["CURCODE"] == "USD")
            & (ibes["USFIRM"] == 1)]
ibes = ibes[(ibes["FPEDATS"] >= "2010-01-01") & (ibes["FPEDATS"] <= "2017-03-31")]
ibes = ibes[ibes["STATPERS"] < ibes["FPEDATS"]]
print(f"After QTR/EPS/window filters: {len(ibes):,}")

ibes = ibes.sort_values(["TICKER", "FPEDATS", "STATPERS"])
ibes = ibes.drop_duplicates(subset=["TICKER", "FPEDATS"], keep="last")
print(f"Latest consensus per (TICKER, FPEDATS): {len(ibes):,}")

ibes["STDEV"] = pd.to_numeric(ibes["STDEV"], errors="coerce")
ibes["ACTUAL"] = pd.to_numeric(ibes["ACTUAL"], errors="coerce")
ibes["MEANEST"] = pd.to_numeric(ibes["MEANEST"], errors="coerce")
ibes["MEDEST"] = pd.to_numeric(ibes["MEDEST"], errors="coerce")

# Diagnostics on STDEV distribution
print(f"\n--- STDEV distribution ---")
sv = ibes["STDEV"].dropna()
print(f"  N={len(sv):,}  mean={sv.mean():.4f}  median={sv.median():.4f}")
print(f"  p1={sv.quantile(.01):.6f}  p5={sv.quantile(.05):.6f}  p25={sv.quantile(.25):.4f}")
print(f"  p75={sv.quantile(.75):.4f}  p95={sv.quantile(.95):.4f}  p99={sv.quantile(.99):.4f}")
print(f"  STDEV=0: {(sv==0).sum():,}  STDEV<0.01: {(sv<0.01).sum():,}  STDEV<0.05: {(sv<0.05).sum():,}")

# Anchor: mean=0.07, sd=3.51, median=0.09 (Table 1 PA panel-wide)
ANCHOR = "mean=0.07  sd=3.51  median=0.09"

def stat(s, label, target=ANCHOR):
    s_w = s.dropna()
    if len(s_w) == 0:
        print(f"  {label}: empty")
        return
    print(f"  {label}: N={len(s_w):,}  mean={s_w.mean():.4f}  sd={s_w.std():.4f}  median={s_w.median():.4f}  IQR={s_w.quantile(.75)-s_w.quantile(.25):.4f}")

def wins_pooled(s, lo_q, hi_q):
    s = s.copy()
    lo, hi = s.quantile(lo_q), s.quantile(hi_q)
    return s.clip(lo, hi)

print(f"\nAnchor (Table 1 Panel A): {ANCHOR}, N=42,031, IQR=2.05")
print()

# Variant 1: raw SUE (no winsorization)
sue_raw = (ibes["ACTUAL"] - ibes["MEANEST"]) / ibes["STDEV"].replace(0, np.nan)
stat(sue_raw, "V1 raw SUE (no winsor)")

# Variant 2: 1%/99% winsorize pooled
stat(wins_pooled(sue_raw, 0.01, 0.99), "V2 SUE wins 1/99 pooled")

# Variant 3: 5%/95%
stat(wins_pooled(sue_raw, 0.05, 0.95), "V3 SUE wins 5/95 pooled")

# Variant 4: median-based SUE
sue_med = (ibes["ACTUAL"] - ibes["MEDEST"]) / ibes["STDEV"].replace(0, np.nan)
stat(wins_pooled(sue_med, 0.01, 0.99), "V4 SUE w/ MEDEST not MEANEST, wins 1/99")

# Variant 5: floor STDEV at $0.01
sd_floor = ibes["STDEV"].clip(lower=0.01)
sue_floor = (ibes["ACTUAL"] - ibes["MEANEST"]) / sd_floor
stat(wins_pooled(sue_floor, 0.01, 0.99), "V5 SUE w/ STDEV floored at 0.01, wins 1/99")

# Variant 6: floor STDEV at $0.05
sd_floor5 = ibes["STDEV"].clip(lower=0.05)
sue_floor5 = (ibes["ACTUAL"] - ibes["MEANEST"]) / sd_floor5
stat(wins_pooled(sue_floor5, 0.01, 0.99), "V6 SUE w/ STDEV floored at 0.05, wins 1/99")

# Variant 7: drop STDEV<0.05 entirely
mask = ibes["STDEV"] >= 0.05
sue_drop = sue_raw.where(mask, np.nan)
stat(wins_pooled(sue_drop, 0.01, 0.99), "V7 SUE dropping STDEV<0.05, wins 1/99")

# Variant 8: drop STDEV<0.01
mask1 = ibes["STDEV"] >= 0.01
sue_drop1 = sue_raw.where(mask1, np.nan)
stat(wins_pooled(sue_drop1, 0.01, 0.99), "V8 SUE dropping STDEV<0.01, wins 1/99")

# Variant 9: trim instead of winsorize
def trim(s, lo_q, hi_q):
    lo, hi = s.quantile(lo_q), s.quantile(hi_q)
    return s.where((s >= lo) & (s <= hi), np.nan)
stat(trim(sue_raw, 0.01, 0.99), "V9 SUE trim 1/99 pooled (drop)")

# Variant 10: Foster-Olsen-Shevlin time-series SD per firm
# Use rolling 8-quarter SD of past forecast errors
print("\nBuilding V10: Foster-Olsen-Shevlin time-series SUE...")
ibes["FE"] = ibes["ACTUAL"] - ibes["MEANEST"]
ibes = ibes.sort_values(["TICKER", "FPEDATS"])
# Rolling 8-quarter SD of past forecast errors per ticker
ibes["FE_lag1"] = ibes.groupby("TICKER")["FE"].shift(1)
def rolling_sd(g):
    return g.rolling(8, min_periods=4).std()
ibes["FE_TS_SD"] = ibes.groupby("TICKER")["FE_lag1"].transform(rolling_sd)
sue_fos = ibes["FE"] / ibes["FE_TS_SD"].replace(0, np.nan)
stat(wins_pooled(sue_fos.dropna(), 0.01, 0.99), "V10 Foster-Olsen-Shevlin SUE, wins 1/99")

# Variant 11: scaled by stock price (need to estimate)
# Skip — would need to merge with CRSP

# Variant 12: cross-sec winsorize per cal_yr_qtr at 1%/99%
ibes["cal_yr_qtr"] = ibes["FPEDATS"].dt.year * 10 + ibes["FPEDATS"].dt.quarter
nv = pd.Series(np.nan, index=ibes.index)
sue_t = (ibes["ACTUAL"] - ibes["MEANEST"]) / ibes["STDEV"].replace(0, np.nan)
ibes["sue_t"] = sue_t
for q, idx in ibes.groupby("cal_yr_qtr").groups.items():
    v = ibes.loc[idx, "sue_t"]
    if v.notna().sum() >= 10:
        lo, hi = v.quantile(0.01), v.quantile(0.99)
        nv.loc[idx] = v.clip(lo, hi)
    else:
        nv.loc[idx] = v
stat(nv, "V12 SUE wins 1/99 per cal_yr_qtr")
