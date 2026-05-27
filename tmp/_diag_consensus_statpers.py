"""Test H3: STATPERS dedup logic affects distribution width.

Compare 3 dedup strategies:
  A: latest STATPERS strictly before FPEDATS  (current code — too close)
  B: STATPERS in quarter t (where t = cal_yr_qtr; forecast at end of t for t+1)
  C: STATPERS in MONTH equal to last month of quarter t
"""
import zipfile
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

# Filters: EPS, QTR, FPI=6 (1Q-ahead), USD, US, in window, STATPERS<FPEDATS
ibes = ibes[
    (ibes["MEASURE"] == "EPS")
    & (ibes["FISCALP"] == "QTR")
    & (ibes["FPI_n"] == 6)
    & (ibes["CURCODE"] == "USD")
    & (ibes["USFIRM"] == 1)
    & (ibes["FPEDATS"] >= "2010-01-01")
    & (ibes["FPEDATS"] <= "2017-03-31")
    & (ibes["STATPERS"] < ibes["FPEDATS"])
]
print(f"After all filters: {len(ibes):,}")

# Compute t = quarter before FPEDATS (forecast target = t+1, so t = FPEDATS quarter - 1)
yr = ibes["FPEDATS"].dt.year
qtr = ibes["FPEDATS"].dt.quarter
prev_qtr = np.where(qtr == 1, 4, qtr - 1)
prev_yr = np.where(qtr == 1, yr - 1, yr)
ibes["cal_yr_qtr_t"] = (prev_yr * 10 + prev_qtr).astype(np.int64)

# STATPERS year/quarter
ibes["statpers_yq"] = (ibes["STATPERS"].dt.year * 10
                        + ibes["STATPERS"].dt.quarter).astype(np.int64)

# === Strategy A: latest STATPERS strictly before FPEDATS ===
a = ibes.sort_values(["TICKER", "FPEDATS", "STATPERS"]).drop_duplicates(
    subset=["TICKER", "FPEDATS"], keep="last"
)

# === Strategy B: STATPERS falls in quarter t (forecast made within t for target t+1) ===
b = ibes[ibes["statpers_yq"] == ibes["cal_yr_qtr_t"]]
b = b.sort_values(["TICKER", "FPEDATS", "STATPERS"]).drop_duplicates(
    subset=["TICKER", "FPEDATS"], keep="last"  # latest snapshot within quarter t
)

# === Strategy C: STATPERS in last MONTH of quarter t ===
def last_month_of_qtr(q):
    return q * 3  # Q1→3, Q2→6, Q3→9, Q4→12
ibes["t_last_month"] = ibes["cal_yr_qtr_t"].astype(int).map(
    {q: ((q // 10) * 100 + last_month_of_qtr(q % 10)) for q in ibes["cal_yr_qtr_t"].unique()}
)
ibes["statpers_ym"] = (ibes["STATPERS"].dt.year * 100 + ibes["STATPERS"].dt.month).astype(np.int64)
c = ibes[ibes["statpers_ym"] == ibes["t_last_month"]]
c = c.sort_values(["TICKER", "FPEDATS", "STATPERS"]).drop_duplicates(
    subset=["TICKER", "FPEDATS"], keep="last"
)

# Filter to sample gvkeys
comp_tic = pd.read_parquet(f"{ROOT}/inputs/comp_na_daily_all/comp_na_daily_all.parquet",
                            columns=["gvkey", "tic", "datadate"])
comp_tic["gvkey"] = comp_tic["gvkey"].astype(str).str.zfill(6)
comp_tic["datadate"] = pd.to_datetime(comp_tic["datadate"])
comp_tic = comp_tic[(comp_tic["datadate"] >= "2010-01-01") & (comp_tic["datadate"] <= "2017-03-31")]
comp_tic["cal_yr_qtr"] = (comp_tic["datadate"].dt.year * 10
                            + comp_tic["datadate"].dt.quarter).astype(np.int64)
comp_tic = comp_tic[["gvkey", "tic", "cal_yr_qtr"]].drop_duplicates()

import os
runs = sorted([d for d in os.listdir(f"{ROOT}/outputs/campello_v2")
                if os.path.exists(f"{ROOT}/outputs/campello_v2/{d}/variables_panel.parquet")], reverse=True)
panel = pd.read_parquet(f"{ROOT}/outputs/campello_v2/{runs[0]}/variables_panel.parquet")
sample_gvkeys = set(panel["gvkey"].unique())

def attach_and_stats(df, label):
    df = df.rename(columns={"cal_yr_qtr_t": "cal_yr_qtr"})
    m = df.merge(comp_tic, left_on=["OFTIC", "cal_yr_qtr"],
                   right_on=["tic", "cal_yr_qtr"], how="inner")
    m = m.drop_duplicates(subset=["gvkey", "cal_yr_qtr"], keep="first")
    m = m[m["gvkey"].isin(sample_gvkeys)]
    s = m["MEANEST"].dropna()
    # winsorize pooled 1%/99%
    lo, hi = s.quantile(0.01), s.quantile(0.99)
    s_w = s.clip(lo, hi)
    print(f"  {label}: N={len(s_w):,}  mean={s_w.mean():.3f}  sd={s_w.std():.3f}  "
          f"median={s_w.median():.3f}  IQR={s_w.quantile(.75)-s_w.quantile(.25):.3f}")

print("\n--- Strategy comparison (post-winsorization) ---")
attach_and_stats(a, "A: latest before FPEDATS                 ")
attach_and_stats(b, "B: STATPERS in quarter t                 ")
attach_and_stats(c, "C: STATPERS in last month of quarter t   ")
print(f"  ANCHOR:                                    N=42,031  mean=0.07   sd=3.51   median=0.09   IQR=2.05")
