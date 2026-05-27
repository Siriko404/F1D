"""Test cross-analyst SUE WITH cross-sectional demean per cal_yr_qtr."""
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
    & (ibes["FISCALP"] == "QTR")
    & (ibes["FPI_n"] == 6)
]

d = base.sort_values(["TICKER", "FPEDATS", "STATPERS"]).drop_duplicates(
    subset=["TICKER", "FPEDATS"], keep="last").copy()

d["ACTUAL_n"] = pd.to_numeric(d["ACTUAL"], errors="coerce")
d["MEANEST_n"] = pd.to_numeric(d["MEANEST"], errors="coerce")
d["STDEV_n"] = pd.to_numeric(d["STDEV"], errors="coerce")
d["SUE"] = (d["ACTUAL_n"] - d["MEANEST_n"]) / d["STDEV_n"].replace(0, np.nan)

# cal_yr_qtr
yr = d["FPEDATS"].dt.year
qtr = d["FPEDATS"].dt.quarter
prev_qtr = np.where(qtr == 1, 4, qtr - 1)
prev_yr = np.where(qtr == 1, yr - 1, yr)
d["cal_yr_qtr"] = (prev_yr * 10 + prev_qtr).astype(np.int64)

# Map to gvkey
comp_tic = pd.read_parquet(f"{ROOT}/inputs/comp_na_daily_all/comp_na_daily_all.parquet",
                            columns=["gvkey", "tic", "datadate"])
comp_tic["gvkey"] = comp_tic["gvkey"].astype(str).str.zfill(6)
comp_tic["datadate"] = pd.to_datetime(comp_tic["datadate"])
comp_tic = comp_tic[(comp_tic["datadate"] >= "2010-01-01") & (comp_tic["datadate"] <= "2017-03-31")]
comp_tic["cal_yr_qtr"] = (comp_tic["datadate"].dt.year * 10
                            + comp_tic["datadate"].dt.quarter).astype(np.int64)
comp_tic = comp_tic[["gvkey", "tic", "cal_yr_qtr"]].drop_duplicates()

m = d.merge(comp_tic, left_on=["OFTIC", "cal_yr_qtr"],
              right_on=["tic", "cal_yr_qtr"], how="inner")
m = m.drop_duplicates(subset=["gvkey", "cal_yr_qtr"], keep="first")

runs = sorted([d for d in os.listdir(f"{ROOT}/outputs/campello_v2")
                if os.path.exists(f"{ROOT}/outputs/campello_v2/{d}/variables_panel.parquet")], reverse=True)
panel = pd.read_parquet(f"{ROOT}/outputs/campello_v2/{runs[0]}/variables_panel.parquet")
sample_gvkeys = set(panel["gvkey"].unique())
m = m[m["gvkey"].isin(sample_gvkeys)]

def stat(label, s):
    s = s.dropna()
    lo, hi = s.quantile(0.01), s.quantile(0.99)
    s_w = s.clip(lo, hi)
    iqr = s_w.quantile(.75) - s_w.quantile(.25)
    print(f"  {label:<55} N={len(s_w):,}  mean={s_w.mean():.3f}  "
          f"sd={s_w.std():.3f}  median={s_w.median():.3f}  IQR={iqr:.3f}")

print(f"  {'ANCHOR:':<55} N=42,031  mean=0.07   sd=3.51   median=0.09   IQR=2.05\n")

# Raw cross-analyst SUE
stat("SUE = (ACT-MEAN)/STDEV (cross-analyst)", m["SUE"])

# Demean by industry-quarter (use sic from compustat). But quicker: just cal_yr_qtr demean
m["SUE_dm_q"] = m.groupby("cal_yr_qtr")["SUE"].transform(lambda x: x - x.mean())
stat("SUE − mean(SUE | cal_yr_qtr) [cross-sec demean]", m["SUE_dm_q"])

m["SUE_dm_qmed"] = m.groupby("cal_yr_qtr")["SUE"].transform(lambda x: x - x.median())
stat("SUE − median(SUE | cal_yr_qtr) [cross-sec demed]", m["SUE_dm_qmed"])
