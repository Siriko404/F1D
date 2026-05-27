"""Round 3: hunt for the centered+wide-tail variable matching anchor.

Anchor signature: N=42K, mean≈0, sd≈3.51, median≈0, IQR≈2.05.
Distribution is centered and wide → likely surprise, revision, or
forecast scaled by some firm-specific deflator.
"""
import zipfile, os
import numpy as np
import pandas as pd

ROOT = r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D"

with zipfile.ZipFile(f"{ROOT}/inputs/tr_ibes/ibes_statsum.zip") as z:
    name = z.namelist()[0]
    with z.open(name) as f:
        ibes = pd.read_csv(f, dtype={"TICKER": "str", "OFTIC": "str"}, low_memory=False)

ibes["STATPERS"] = pd.to_datetime(ibes["STATPERS"])
ibes["FPEDATS"] = pd.to_datetime(ibes["FPEDATS"])
ibes["FPI_n"] = pd.to_numeric(ibes["FPI"], errors="coerce")

base = ibes[
    (ibes["MEASURE"] == "EPS")
    & (ibes["CURCODE"] == "USD")
    & (ibes["USFIRM"] == 1)
    & (ibes["FPEDATS"] >= "2010-01-01")
    & (ibes["FPEDATS"] <= "2017-03-31")
    & (ibes["STATPERS"] < ibes["FPEDATS"])
]

# === filter Q+1 ===
d6 = base[(base["FISCALP"] == "QTR") & (base["FPI_n"] == 6)].copy()

# Get latest STATPERS per (TICKER, FPEDATS) AND second-latest (for revision)
d6 = d6.sort_values(["TICKER", "FPEDATS", "STATPERS"])
d6["rank_in"] = d6.groupby(["TICKER", "FPEDATS"]).cumcount(ascending=False)  # 0 = latest

# Use latest STATPERS row
d6_latest = d6[d6["rank_in"] == 0].copy()

# Add CRSP daily price for prccq-style scaling — use Compustat prccq_lag instead (simpler)
comp = pd.read_parquet(f"{ROOT}/inputs/comp_na_daily_all/comp_na_daily_all.parquet",
                        columns=["gvkey", "tic", "datadate", "prccq", "cshoq", "atq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
comp = comp[(comp["datadate"] >= "2010-01-01") & (comp["datadate"] <= "2017-03-31")]
comp["cal_yr_qtr"] = (comp["datadate"].dt.year * 10
                       + comp["datadate"].dt.quarter).astype(np.int64)
for c in ["prccq", "cshoq", "atq"]:
    comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp_tic = comp[["gvkey", "tic", "cal_yr_qtr", "prccq", "cshoq", "atq"]].drop_duplicates(
    subset=["gvkey", "cal_yr_qtr"], keep="last"
)
# lagged price within gvkey
comp_tic = comp_tic.sort_values(["gvkey", "cal_yr_qtr"])
comp_tic["prccq_lag"] = comp_tic.groupby("gvkey")["prccq"].shift(1)
comp_tic["atq_lag"] = comp_tic.groupby("gvkey")["atq"].shift(1)

# Map cal_yr_qtr for d6 (quarter before FPEDATS)
yr = d6_latest["FPEDATS"].dt.year
qtr = d6_latest["FPEDATS"].dt.quarter
prev_qtr = np.where(qtr == 1, 4, qtr - 1)
prev_yr = np.where(qtr == 1, yr - 1, yr)
d6_latest["cal_yr_qtr"] = (prev_yr * 10 + prev_qtr).astype(np.int64)

m = d6_latest.merge(comp_tic, left_on=["OFTIC", "cal_yr_qtr"],
                      right_on=["tic", "cal_yr_qtr"], how="inner")
m = m.drop_duplicates(subset=["gvkey", "cal_yr_qtr"], keep="first")

# Sample filter
runs = sorted([d for d in os.listdir(f"{ROOT}/outputs/campello_v2")
                if os.path.exists(f"{ROOT}/outputs/campello_v2/{d}/variables_panel.parquet")], reverse=True)
panel = pd.read_parquet(f"{ROOT}/outputs/campello_v2/{runs[0]}/variables_panel.parquet")
sample_gvkeys = set(panel["gvkey"].unique())
m = m[m["gvkey"].isin(sample_gvkeys)]

m["MEANEST_n"] = pd.to_numeric(m["MEANEST"], errors="coerce")
m["ACTUAL_n"] = pd.to_numeric(m["ACTUAL"], errors="coerce")
m["STDEV_n"] = pd.to_numeric(m["STDEV"], errors="coerce")

def stat(label, s):
    s = s.dropna()
    lo, hi = s.quantile(0.01), s.quantile(0.99)
    s_w = s.clip(lo, hi)
    iqr = s_w.quantile(.75) - s_w.quantile(.25)
    print(f"  {label:<55} N={len(s_w):,}  mean={s_w.mean():.3f}  "
          f"sd={s_w.std():.3f}  median={s_w.median():.3f}  IQR={iqr:.3f}")

print(f"  {'ANCHOR (Table 1 Panel A):':<55} N=42,031  mean=0.07   sd=3.51   median=0.09   IQR=2.05\n")

# Revision: MEANEST - prev quarter's MEANEST for same FIRM (within gvkey)
m_sorted = m.sort_values(["gvkey", "cal_yr_qtr"])
m_sorted["MEANEST_lag1"] = m_sorted.groupby("gvkey")["MEANEST_n"].shift(1)
stat("Forecast revision: MEANEST_t - MEANEST_{t-1}",
     m_sorted["MEANEST_n"] - m_sorted["MEANEST_lag1"])

# Surprise scaled by STDEV (SUE)
stat("(ACTUAL - MEANEST) / STDEV",
     (m["ACTUAL_n"] - m["MEANEST_n"]) / m["STDEV_n"].replace(0, np.nan))

# Surprise scaled by price
stat("(ACTUAL - MEANEST) / prccq × 100",
     (m["ACTUAL_n"] - m["MEANEST_n"]) / m["prccq"] * 100)

# Surprise × 100 (cents)
stat("(ACTUAL - MEANEST) × 100",
     (m["ACTUAL_n"] - m["MEANEST_n"]) * 100)

# MEANEST scaled by price
stat("MEANEST / prccq × 100",
     m["MEANEST_n"] / m["prccq"] * 100)

# MEANEST × 4 (annualize from quarterly)
stat("MEANEST × 4 (annualize)",
     m["MEANEST_n"] * 4)

# Standardized MEANEST: (MEANEST - lag MEANEST) / |MEANEST_lag|
m_sorted2 = m_sorted.copy()
stat("(MEANEST - MEANEST_lag) / |MEANEST_lag|",
     (m_sorted2["MEANEST_n"] - m_sorted2["MEANEST_lag1"]) / m_sorted2["MEANEST_lag1"].abs())

# MEANEST as fraction of book equity / shares — earnings yield
stat("MEANEST × 4 / prccq_lag",
     m["MEANEST_n"] * 4 / m["prccq_lag"])

# Cross-section z-score per cal_yr_qtr × magnification
m["MEANEST_z"] = m.groupby("cal_yr_qtr")["MEANEST_n"].transform(
    lambda x: (x - x.mean()) / x.std())
stat("MEANEST z-scored within cal_yr_qtr",
     m["MEANEST_z"])

# MEANEST cross-section demeaned (within cal_yr_qtr) -- no SD scaling
m["MEANEST_dm"] = m.groupby("cal_yr_qtr")["MEANEST_n"].transform(
    lambda x: x - x.mean())
stat("MEANEST cross-section demeaned (within cal_yr_qtr)",
     m["MEANEST_dm"])

# (Median demeaned)
m["MEANEST_dm_med"] = m.groupby("cal_yr_qtr")["MEANEST_n"].transform(
    lambda x: x - x.median())
stat("MEANEST median-demeaned (within cal_yr_qtr)",
     m["MEANEST_dm_med"])
