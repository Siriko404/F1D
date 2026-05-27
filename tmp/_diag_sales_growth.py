"""Test SALES_GROWTH alternative definitions. Anchor mean=0.16 sd=0.62 p50=0.06.
Current: (saleq-saleq_t-4)/|saleq_t-4| → mean=0.083 sd=0.352 (half)."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")

OUT = ROOT / "outputs" / "campello_v2"
runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / "variables_panel.parquet").exists()], reverse=True)
panel = pd.read_parquet(runs[0] / "variables_panel.parquet")

# Need raw saleq - reload from sample
comp = pd.read_parquet(ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet",
                       columns=["gvkey", "datadate", "saleq", "saley", "atq", "indfmt", "datafmt"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
comp = comp[(comp["indfmt"]=="INDL") & (comp["datafmt"]=="STD")]
comp = comp[(comp["datadate"] >= "2008-01-01") & (comp["datadate"] <= "2017-03-31")]
# Sample gvkeys
sample_gv = set(panel["gvkey"].unique())
comp = comp[comp["gvkey"].isin(sample_gv)].sort_values(["gvkey", "datadate"]).reset_index(drop=True)
comp["cal_yr_qtr"] = (comp["datadate"].dt.year * 10 + comp["datadate"].dt.quarter).astype(np.int64)
for c in ["saleq", "saley", "atq"]:
    comp[c] = pd.to_numeric(comp[c], errors="coerce")

# DV1: (saleq - saleq_t-4) / |saleq_t-4|  -- current
comp["saleq_t4"] = comp.groupby("gvkey")["saleq"].shift(4)
comp["sg_yoy_abs"] = np.where(comp["saleq_t4"].abs() > 0,
                               (comp["saleq"] - comp["saleq_t4"]) / comp["saleq_t4"].abs(),
                               np.nan)

# DV2: (saleq - saleq_t-1) / |saleq_t-1|  -- quarter-over-quarter
comp["saleq_t1"] = comp.groupby("gvkey")["saleq"].shift(1)
comp["sg_qoq_abs"] = np.where(comp["saleq_t1"].abs() > 0,
                               (comp["saleq"] - comp["saleq_t1"]) / comp["saleq_t1"].abs(),
                               np.nan)

# DV3: TTM (4-qtr trailing sum) growth
comp["ttm"] = comp.groupby("gvkey")["saleq"].transform(lambda x: x.rolling(4, min_periods=4).sum())
comp["ttm_lag"] = comp.groupby("gvkey")["ttm"].shift(4)
comp["sg_ttm"] = np.where(comp["ttm_lag"].abs() > 0,
                           (comp["ttm"] - comp["ttm_lag"]) / comp["ttm_lag"].abs(),
                           np.nan)

# DV4: scaled by atq_lag1
comp["atq_t1"] = comp.groupby("gvkey")["atq"].shift(1)
comp["sg_yoy_atq"] = np.where(comp["atq_t1"].abs() > 0,
                               (comp["saleq"] - comp["saleq_t4"]) / comp["atq_t1"],
                               np.nan)

# DV5: log growth ln(saleq) - ln(saleq_t-4)
mask = (comp["saleq"] > 0) & (comp["saleq_t4"] > 0)
comp["sg_log"] = np.where(mask, np.log(comp["saleq"]) - np.log(comp["saleq_t4"]), np.nan)

# Winsorize each at 1%/99% and report
def winz(s):
    s = s.replace([np.inf, -np.inf], np.nan)
    lo, hi = s.quantile(0.01), s.quantile(0.99)
    return s.clip(lo, hi)

# Restrict to 2010Q1-2017Q1 like paper sample
m = (comp["cal_yr_qtr"] >= 20101) & (comp["cal_yr_qtr"] <= 20171)
print(f"Sample 2010Q1-2017Q1 firm-qtrs: {m.sum():,}")
print(f"Anchor (Table 1 PA): N=71,637  mean=0.16  sd=0.62  p50=0.06\n")
print(f"{'Variant':<20}{'N':>8}{'mean':>10}{'sd':>10}{'p50':>10}")
for col in ["sg_yoy_abs", "sg_qoq_abs", "sg_ttm", "sg_yoy_atq", "sg_log"]:
    s = winz(comp.loc[m, col]).dropna()
    print(f"{col:<20}{len(s):>8,}{s.mean():>10.4f}{s.std():>10.4f}{s.median():>10.4f}")
