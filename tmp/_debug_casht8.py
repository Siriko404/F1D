"""Debug CASH_T8 construction in variables panel."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d/"variables_panel.parquet").exists()], reverse=True)

panel = pd.read_parquet(runs[0] / "variables_panel.parquet")
print(f"Panel: {len(panel):,} obs")
print(f"Columns with atq/cheq/cash: {[c for c in panel.columns if any(k in c.lower() for k in ['atq','cheq','cash'])]}")

# Check if panel has raw cheq
if "cheq" not in panel.columns:
    print("\ncheq NOT in variables_panel — did_cash.py loads it from raw Compustat")
    # Load from Compustat for a sample gvkey
    comp = pd.read_parquet(ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet",
                           columns=["gvkey", "datadate", "atq", "cheq"])
    comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
    comp["datadate"] = pd.to_datetime(comp["datadate"])

    # Merge with panel for a few treated firms
    beta = pd.read_parquet(runs[0] / "beta_uk.parquet")
    # Actually use latest beta_uk dir
    beta_runs = sorted([d for d in OUT.iterdir() if (d/"beta_uk.parquet").exists()], reverse=True)
    beta = pd.read_parquet(beta_runs[0] / "beta_uk.parquet")
    nonneg = beta[beta["beta_uk"]>=0]
    t2 = nonneg["beta_uk"].quantile(2/3)
    top_gv = list(nonneg[nonneg["beta_uk"]>t2]["gvkey"].head(3))
    print(f"Sample top-tercile gvkeys: {top_gv}")

    # Get their data
    panel_sub = panel[panel["gvkey"].isin(top_gv)]
    comp_sub = comp[comp["gvkey"].isin(top_gv)]

    # Show raw cheq, atq for the DiD quarters
    qs = [20153, 20154, 20163, 20164]
    for gv in top_gv:
        print(f"\n=== gvkey={gv} ===")
        p = panel_sub[panel_sub["gvkey"]==gv].sort_values("cal_yr_qtr")
        c = comp_sub[comp_sub["gvkey"]==gv].sort_values("datadate")

        # Show T1 CASH for pre/post
        pre_p = p[p["cal_yr_qtr"].isin([20153,20154])]
        post_p = p[p["cal_yr_qtr"].isin([20163,20164])]
        print(f"  CASH_T1: pre={pre_p['CASH'].mean():.4f}  post={post_p['CASH'].mean():.4f}")

        # Compute CASH_T8 manually
        merged = p.merge(c[["gvkey","datadate","cheq"]], on=["gvkey","datadate"], how="left")
        # Need atq_lag1 and cheq_lag1 — shift from panel
        merged = merged.sort_values("cal_yr_qtr")
        merged["atq_lag1"] = merged.groupby("gvkey")["atq"].shift(1)
        merged["cheq_lag1"] = merged.groupby("gvkey")["cheq"].shift(1)
        denom = merged["atq_lag1"] - merged["cheq_lag1"]
        merged["CASH_T8_manual"] = np.where((denom.notna()) & (denom>0), merged["cheq"]/denom, np.nan)

        for q in qs:
            row = merged[merged["cal_yr_qtr"]==q]
            if len(row) > 0:
                print(f"  Q={q}: atq={row['atq'].values[0]:.2f}  cheq={row['cheq'].values[0]:.2f}  "
                      f"atq_lag1={row['atq_lag1'].values[0]:.2f}  cheq_lag1={row['cheq_lag1'].values[0]:.2f}  "
                      f"CASH_T1={row['CASH'].values[0]:.4f}  CASH_T8={row['CASH_T8_manual'].values[0]:.4f}")
else:
    print("cheq IS in panel")
