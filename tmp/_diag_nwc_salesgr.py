"""Test NWC + SALES_GROWTH alternative definitions against anchors."""
import pandas as pd
import numpy as np
import os

ROOT = r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D"

runs = sorted([d for d in os.listdir(f"{ROOT}/outputs/campello_v2")
                if os.path.exists(f"{ROOT}/outputs/campello_v2/{d}/variables_panel.parquet")], reverse=True)
panel = pd.read_parquet(f"{ROOT}/outputs/campello_v2/{runs[0]}/variables_panel.parquet")

# Reload compustat extras
comp = pd.read_parquet(f"{ROOT}/inputs/comp_na_daily_all/comp_na_daily_all.parquet",
    columns=["gvkey", "datadate", "actq", "lctq", "cheq", "atq", "saleq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
for c in ["actq", "lctq", "cheq", "atq", "saleq"]:
    comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp = comp.drop_duplicates(subset=["gvkey", "datadate"], keep="last")

m = panel.merge(comp[["gvkey", "datadate", "actq", "lctq", "cheq", "atq", "saleq"]],
                  on=["gvkey", "datadate"], how="left", suffixes=("", "_r"))

# Use raw cheq/atq from compustat
m["cheq"] = m["cheq_r"] if "cheq_r" in m.columns else m["cheq"]
m["atq"]  = m["atq_r"]  if "atq_r"  in m.columns else m["atq"]

m = m.sort_values(["gvkey", "cal_yr_qtr"])

def winsorize_pooled(s):
    s = s.dropna()
    lo, hi = s.quantile(0.01), s.quantile(0.99)
    return s.clip(lo, hi)

def stat(label, s):
    s_w = winsorize_pooled(s)
    iqr = s_w.quantile(.75) - s_w.quantile(.25)
    print(f"  {label:<55} N={len(s_w):,}  mean={s_w.mean():.3f}  "
          f"sd={s_w.std():.3f}  median={s_w.median():.3f}  IQR={iqr:.3f}")

print("--- NWC alternatives ---")
print(f"  {'ANCHOR Table 1 Panel A NWC:':<55} mean=0.04   sd=0.19   median=0.03   IQR=0.20\n")

# Current def
stat("(actq - lctq - cheq) / atq_lag1",
     (m["actq"] - m["lctq"] - m["cheq"]) / m["atq_lag1"])

# Alt 1: (actq - cheq - lctq) / atq_lag1   (same as above)
# Alt 2: (actq - cheq) - lctq, with lctq net of short-term debt
# Alt 3: scaled by contemporaneous atq
stat("(actq - lctq - cheq) / atq (contemp)",
     (m["actq"] - m["lctq"] - m["cheq"]) / m["atq"])

# Alt 4: paper-specific: cheq subtracted before computing WC
stat("((actq - cheq) - lctq) / atq_lag1 (same)",
     ((m["actq"] - m["cheq"]) - m["lctq"]) / m["atq_lag1"])

print("\n--- SALES_GROWTH alternatives ---")
print(f"  {'ANCHOR Table 1 Panel A SALES_GROWTH:':<55} mean=0.16   sd=0.62   median=0.06   IQR=0.23\n")

m["saleq_lag4"] = m.groupby("gvkey")["saleq"].shift(4)
m["saleq_lag1"] = m.groupby("gvkey")["saleq"].shift(1)

# YoY (current)
stat("(saleq_t - saleq_t-4) / |saleq_t-4|",
     (m["saleq"] - m["saleq_lag4"]) / m["saleq_lag4"].abs())

# QoQ
stat("(saleq_t - saleq_t-1) / |saleq_t-1|",
     (m["saleq"] - m["saleq_lag1"]) / m["saleq_lag1"].abs())

# Log YoY
stat("log(saleq_t / saleq_t-4)",
     np.log(m["saleq"] / m["saleq_lag4"].replace(0, np.nan)))

# YoY without abs() in denom
stat("(saleq_t - saleq_t-4) / saleq_t-4",
     (m["saleq"] - m["saleq_lag4"]) / m["saleq_lag4"])
