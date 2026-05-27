"""Test Foster-Olsen-Shevlin time-series SUE construction."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")

import zipfile
zpath = ROOT / "inputs" / "tr_ibes" / "ibes_statsum.zip"
with zipfile.ZipFile(zpath) as z:
    name = z.namelist()[0]
    with z.open(name) as f:
        ibes = pd.read_csv(
            f,
            usecols=["TICKER", "OFTIC", "STATPERS", "MEASURE", "FISCALP", "FPI",
                     "MEANEST", "MEDEST", "FPEDATS", "USFIRM", "CURCODE",
                     "ACTUAL", "STDEV"],
            dtype={"TICKER": "str", "OFTIC": "str"},
            low_memory=False,
        )
print(f"IBES total: {len(ibes):,}")
ibes["FPI"] = pd.to_numeric(ibes["FPI"], errors="coerce")

ibes["STATPERS"] = pd.to_datetime(ibes["STATPERS"])
ibes["FPEDATS"] = pd.to_datetime(ibes["FPEDATS"])
ibes = ibes[(ibes["MEASURE"] == "EPS")
            & (ibes["FISCALP"] == "QTR")
            & (ibes["FPI"] == 6)
            & (ibes["CURCODE"] == "USD")
            & (ibes["USFIRM"] == 1)]
ibes = ibes[ibes["STATPERS"] < ibes["FPEDATS"]]
ibes = ibes.sort_values(["TICKER", "FPEDATS", "STATPERS"])
ibes = ibes.drop_duplicates(subset=["TICKER", "FPEDATS"], keep="last")
ibes["ACTUAL"] = pd.to_numeric(ibes["ACTUAL"], errors="coerce")
ibes["MEANEST"] = pd.to_numeric(ibes["MEANEST"], errors="coerce")
ibes["STDEV"] = pd.to_numeric(ibes["STDEV"], errors="coerce")
ibes = ibes.dropna(subset=["ACTUAL", "MEANEST"])

# Forecast error
ibes["FE"] = ibes["ACTUAL"] - ibes["MEANEST"]

# Sort by ticker + FPEDATS
ibes = ibes.sort_values(["TICKER", "FPEDATS"]).reset_index(drop=True)

# Time-series SD of past forecast errors (rolling 8 quarters)
ibes["FE_shifted"] = ibes.groupby("TICKER")["FE"].shift(1)
def roll_sd(g, w):
    return g.rolling(w, min_periods=4).std()

# Compute time-series SD with various windows
for w in [4, 8, 12, 16, 20]:
    ibes[f"FE_TSD_w{w}"] = ibes.groupby("TICKER")["FE_shifted"].transform(lambda g: g.rolling(w, min_periods=max(2, w//2)).std())

# Also: TSD of past actuals (random walk model: FE = ACTUAL - ACTUAL_lag4)
ibes["ACTUAL_lag4"] = ibes.groupby("TICKER")["ACTUAL"].shift(4)
ibes["FE_rw"] = ibes["ACTUAL"] - ibes["ACTUAL_lag4"]
ibes["FE_rw_shifted"] = ibes.groupby("TICKER")["FE_rw"].shift(1)
for w in [8]:
    ibes[f"FE_rw_TSD_w{w}"] = ibes.groupby("TICKER")["FE_rw_shifted"].transform(lambda g: g.rolling(w, min_periods=max(2, w//2)).std())

# Compute SUEs
ibes["cal_yr_qtr"] = ibes["FPEDATS"].dt.year * 10 + ibes["FPEDATS"].dt.quarter
# Restrict to anchor window 2010-2017 (cal_yr_qtr_of_forecast)
# Actually anchor is on quarter t (the quarter being forecast = FPEDATS quarter)
# Let me compute panel-wide stats for FPEDATS in 2010-2017

ibes_test = ibes[(ibes["FPEDATS"] >= "2010-01-01") & (ibes["FPEDATS"] <= "2017-03-31")].copy()
print(f"FPEDATS 2010-2017 obs: {len(ibes_test):,}")

ANCHOR = "Table 1 PA: mean=0.07  sd=3.51  median=0.09  IQR=2.05"

def wins_pooled(s, lo_q, hi_q):
    sv = s.dropna()
    if len(sv) == 0:
        return s
    lo, hi = sv.quantile(lo_q), sv.quantile(hi_q)
    return s.clip(lo, hi)

def show(s, label):
    s = s.replace([np.inf, -np.inf], np.nan).dropna()
    if len(s) == 0:
        print(f"  {label}: empty")
        return
    iqr = s.quantile(.75) - s.quantile(.25)
    print(f"  {label}: N={len(s):,}  mean={s.mean():.4f}  sd={s.std():.4f}  median={s.median():.4f}  IQR={iqr:.4f}")

print(f"\nAnchor: {ANCHOR}, N=42,031")

ibes_test["MEDEST"] = pd.to_numeric(ibes_test["MEDEST"], errors="coerce")

# Variant: cross-sec STDEV (analyst dispersion)
sue_cs = (ibes_test["FE"] / ibes_test["STDEV"].replace(0, np.nan))
show(wins_pooled(sue_cs, 0.01, 0.99), "CURRENT: SUE = FE/STDEV, wins 1/99")

# Variant: MEDEST instead of MEANEST
fe_med = ibes_test["ACTUAL"] - ibes_test["MEDEST"]
sue_med = fe_med / ibes_test["STDEV"].replace(0, np.nan)
show(wins_pooled(sue_med, 0.01, 0.99), "MEDEST SUE = (A-MED)/STDEV, wins 1/99")

# Variant: subtract firm's TS mean SUE (per-firm demeaning)
ibes_test = ibes_test.sort_values(["TICKER", "FPEDATS"]).reset_index(drop=True)
ibes_test["sue_raw_t"] = (ibes_test["ACTUAL"] - ibes_test["MEANEST"]) / ibes_test["STDEV"].replace(0, np.nan)
ibes_test["sue_raw_t"] = ibes_test["sue_raw_t"].replace([np.inf, -np.inf], np.nan)
ibes_test["sue_demeaned"] = ibes_test.groupby("TICKER")["sue_raw_t"].transform(lambda x: x - x.mean())
show(wins_pooled(ibes_test["sue_demeaned"], 0.01, 0.99), "per-firm TS demeaned SUE")

# Variant: WINSORIZE BEFORE demean
sue_w = wins_pooled(ibes_test["sue_raw_t"], 0.01, 0.99)
sue_w_dm = sue_w.groupby(ibes_test["TICKER"]).transform(lambda x: x - x.mean())
show(sue_w_dm, "winsor then per-firm demean")

# Per-firm MEDIAN demean
sue_med_dm = sue_w.groupby(ibes_test["TICKER"]).transform(lambda x: x - x.median())
show(sue_med_dm, "winsor then per-firm MEDIAN demean")

# Global median subtract
g_med = sue_w.median()
print(f"  global median: {g_med:.4f}")
show(sue_w - g_med, "winsor then subtract global median")

# Global panel mean subtract
g_mean = sue_w.mean()
print(f"  global mean: {g_mean:.4f}")
show(sue_w - g_mean, "winsor then subtract global mean")

# Per-firm demean with MIN forecasts requirement
n_per_firm = ibes_test.groupby("TICKER").size()
big_firms = n_per_firm[n_per_firm >= 8].index
sue_w_dm_filt = sue_w.where(ibes_test["TICKER"].isin(big_firms))
sue_w_dm_8 = sue_w_dm_filt.groupby(ibes_test["TICKER"]).transform(lambda x: x - x.mean())
show(sue_w_dm_8, "winsor + per-firm demean (>=8 obs per firm)")

# Variant: FOS time-series SD of FE, various windows
for w in [4, 8, 12, 16, 20]:
    sue_ts = ibes_test["FE"] / ibes_test[f"FE_TSD_w{w}"].replace(0, np.nan)
    show(wins_pooled(sue_ts, 0.01, 0.99), f"FOS-TS SUE = FE/SD(FE)[t-1:t-{w}], wins 1/99")

# Variant: FOS random-walk: SUE = (ACTUAL - ACTUAL_lag4) / SD(FE_rw_lag1:lag8)
sue_rw = ibes_test["FE_rw"] / ibes_test[f"FE_rw_TSD_w8"].replace(0, np.nan)
show(wins_pooled(sue_rw, 0.01, 0.99), "FOS-RW SUE = (A-A_lag4)/SD(FE_rw)[lag1:lag8]")

# What if STDEV is scaled differently — maybe paper expects STDEV in cents
# (multiply by 100)
sue_x100 = ibes_test["FE"] / (ibes_test["STDEV"] * 100).replace(0, np.nan)
show(wins_pooled(sue_x100, 0.01, 0.99), "SUE w/ STDEV scaled x100")
