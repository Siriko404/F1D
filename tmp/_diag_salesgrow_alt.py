"""Test SALES_GROWTH alternative formulas + winsorizations."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname

panel = pd.read_parquet(latest("variables_panel.parquet"))

# Reload saleq
comp = pd.read_parquet(ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet",
                      columns=["gvkey", "datadate", "saleq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
comp["saleq"] = pd.to_numeric(comp["saleq"], errors="coerce")
comp = comp.drop_duplicates(subset=["gvkey", "datadate"], keep="last")

p = panel.merge(comp[["gvkey", "datadate", "saleq"]], on=["gvkey", "datadate"],
                how="left", suffixes=("_p", ""))
p = p.sort_values(["gvkey", "cal_yr_qtr"])
p["saleq_lag1"] = p.groupby("gvkey")["saleq"].shift(1)
p["saleq_lag4"] = p.groupby("gvkey")["saleq"].shift(4)

# Raw distribution before winsor
def stat(s, label):
    s = s.dropna()
    s = s.replace([np.inf, -np.inf], np.nan).dropna()
    print(f"  {label}: N={len(s):,}  mean={s.mean():.3f}  sd={s.std():.3f}  median={s.median():.3f}  p99={s.quantile(.99):.3f}  p1={s.quantile(.01):.3f}")

def wins_per_qtr(s, df, lo_q, hi_q):
    nv = pd.Series(np.nan, index=df.index)
    for q, idx in df.groupby("cal_yr_qtr").groups.items():
        v = s.loc[idx].dropna()
        if len(v) >= 10:
            lo, hi = v.quantile(lo_q), v.quantile(hi_q)
            nv.loc[idx] = s.loc[idx].clip(lo, hi)
        else:
            nv.loc[idx] = s.loc[idx]
    return nv

def wins_pooled(s, lo_q, hi_q):
    sv = s.dropna()
    lo, hi = sv.quantile(lo_q), sv.quantile(hi_q)
    return s.clip(lo, hi)

print("Anchor (Table 1 PA SALES_GROWTH): mean=0.16  sd=0.62  median=0.06  IQR=0.23  N=71,637")
print()

# YoY (current): (saleq - lag4) / |lag4|
yoy = np.where(p["saleq_lag4"] > 0,
                (p["saleq"] - p["saleq_lag4"]) / p["saleq_lag4"].abs(),
                np.nan)
yoy = pd.Series(yoy, index=p.index).replace([np.inf, -np.inf], np.nan)

stat(yoy, "V1: YoY, lag4>0 filter, no winsor")
stat(wins_per_qtr(yoy, p, 0.01, 0.99), "V2: YoY, lag4>0, wins 1/99 per_qtr (CURRENT)")
stat(wins_pooled(yoy, 0.01, 0.99), "V3: YoY, lag4>0, wins 1/99 pooled")
stat(wins_pooled(yoy, 0.005, 0.995), "V4: YoY, lag4>0, wins 0.5/99.5 pooled")
stat(wins_pooled(yoy, 0.025, 0.975), "V5: YoY, lag4>0, wins 2.5/97.5 pooled")

# YoY (no abs in denom)
yoy_noabs = np.where(p["saleq_lag4"].notna() & (p["saleq_lag4"] != 0),
                      (p["saleq"] - p["saleq_lag4"]) / p["saleq_lag4"],
                      np.nan)
yoy_noabs = pd.Series(yoy_noabs, index=p.index).replace([np.inf, -np.inf], np.nan)
stat(yoy_noabs, "V6: YoY, no abs in denom, no winsor")
stat(wins_pooled(yoy_noabs, 0.01, 0.99), "V7: YoY, no abs, wins 1/99 pooled")

# Log YoY
log_yoy = np.log(p["saleq"] / p["saleq_lag4"].where(p["saleq_lag4"] > 0))
log_yoy = pd.Series(log_yoy, index=p.index).replace([np.inf, -np.inf], np.nan)
stat(log_yoy, "V8: log(saleq / lag4)")
stat(wins_pooled(log_yoy, 0.01, 0.99), "V9: log(saleq / lag4), wins 1/99 pooled")

# Quarterly QoQ
qoq = np.where(p["saleq_lag1"] > 0,
                (p["saleq"] - p["saleq_lag1"]) / p["saleq_lag1"].abs(),
                np.nan)
qoq = pd.Series(qoq, index=p.index).replace([np.inf, -np.inf], np.nan)
stat(wins_pooled(qoq, 0.01, 0.99), "V10: QoQ (lag1), wins 1/99 pooled")

# No saleq_lag4 > 0 filter, just non-NaN
yoy_loose = (p["saleq"] - p["saleq_lag4"]) / p["saleq_lag4"].abs()
yoy_loose = yoy_loose.replace([np.inf, -np.inf], np.nan)
stat(yoy_loose, "V11: YoY, no lag4 filter, no winsor")
stat(wins_pooled(yoy_loose, 0.01, 0.99), "V12: YoY, no lag4 filter, wins 1/99 pooled")

# Trim variants (drop instead of clip)
def trim_pooled(s, lo_q, hi_q):
    sv = s.dropna()
    lo, hi = sv.quantile(lo_q), sv.quantile(hi_q)
    return s.where((s >= lo) & (s <= hi), np.nan)

stat(trim_pooled(yoy, 0.01, 0.99), "V13: YoY, trim 1/99 pooled (DROP)")
stat(trim_pooled(yoy, 0.005, 0.995), "V14: YoY, trim 0.5/99.5 pooled")
stat(trim_pooled(yoy, 0.025, 0.975), "V15: YoY, trim 2.5/97.5 pooled")

# Floor saleq_lag4 at $1M or $10M
yoy_floor1 = np.where(p["saleq_lag4"] > 1.0,
                       (p["saleq"] - p["saleq_lag4"]) / p["saleq_lag4"],
                       np.nan)
yoy_floor1 = pd.Series(yoy_floor1, index=p.index).replace([np.inf, -np.inf], np.nan)
stat(wins_pooled(yoy_floor1, 0.01, 0.99), "V16: YoY, lag4>$1M, wins 1/99")

yoy_floor10 = np.where(p["saleq_lag4"] > 10.0,
                        (p["saleq"] - p["saleq_lag4"]) / p["saleq_lag4"],
                        np.nan)
yoy_floor10 = pd.Series(yoy_floor10, index=p.index).replace([np.inf, -np.inf], np.nan)
stat(wins_pooled(yoy_floor10, 0.01, 0.99), "V17: YoY, lag4>$10M, wins 1/99")

# Combined: drop tiny lag4 + heavier winsor
yoy_combo = np.where(p["saleq_lag4"] > 1.0,
                      (p["saleq"] - p["saleq_lag4"]) / p["saleq_lag4"],
                      np.nan)
yoy_combo = pd.Series(yoy_combo, index=p.index).replace([np.inf, -np.inf], np.nan)
stat(wins_pooled(yoy_combo, 0.005, 0.995), "V18: YoY, lag4>$1M, wins 0.5/99.5")

# Different: maybe just no scaling - raw growth (saleq - lag4) without dividing
# Not the right formula but informational
