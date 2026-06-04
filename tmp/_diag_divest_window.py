"""Test DIVESTITURES T across different pre-Brexit windows."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname

panel = pd.read_parquet(latest("variables_panel.parquet"))
beta = pd.read_parquet(latest("beta_uk.parquet"))[["gvkey", "beta_uk"]]
sret = pd.read_parquet(latest("stock_returns.parquet"))
ceps = pd.read_parquet(latest("consensus_eps.parquet"))
panel = panel.merge(sret, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(beta, on="gvkey", how="left")

# Treated/control by β tercile (top/bottom of nonneg)
nonneg = beta[beta["beta_uk"] >= 0]
t1 = nonneg["beta_uk"].quantile(1/3)
t2 = nonneg["beta_uk"].quantile(2/3)
panel["treated"] = (panel["beta_uk"] > t2).astype(float)
panel["control_pool"] = ((panel["beta_uk"] >= 0) & (panel["beta_uk"] < t1)).astype(float)

# Simple PSM for now (no matching - just compare top vs bot tercile)
treated_gv = set(panel[panel["treated"]==1]["gvkey"].unique())
control_gv = set(panel[panel["control_pool"]==1]["gvkey"].unique())
print(f"Treated firms (top tercile β): {len(treated_gv)}")
print(f"Control firms (bot tercile β): {len(control_gv)}")
print(f"Paper Panel B (top tercile β): DIVESTITURES (×100) = 0.10")
print(f"Paper Panel C (bot tercile β): DIVESTITURES (×100) = 0.08")
print()

# Test windows
for end_q in [20154, 20153, 20152, 20151, 20144, 20154]:
    label = {20154:"<=2015Q4", 20153:"<=2015Q3", 20152:"<=2015Q2", 20151:"<=2015Q1", 20144:"<=2014Q4"}[end_q]
    pre = panel[panel["cal_yr_qtr"] <= end_q]
    t_pre = pre[pre["gvkey"].isin(treated_gv)]["DIVESTITURES"]
    c_pre = pre[pre["gvkey"].isin(control_gv)]["DIVESTITURES"]
    print(f"  {label:<12} T: {(t_pre.mean()*100):.3f} (N={t_pre.notna().sum():,})   C: {(c_pre.mean()*100):.3f} (N={c_pre.notna().sum():,})")

# Also test 2015Q3-Q4 only (2 quarters)
print("\nNarrow window (2015Q3-Q4 only):")
pre = panel[(panel["cal_yr_qtr"] >= 20153) & (panel["cal_yr_qtr"] <= 20154)]
t_pre = pre[pre["gvkey"].isin(treated_gv)]["DIVESTITURES"]
c_pre = pre[pre["gvkey"].isin(control_gv)]["DIVESTITURES"]
print(f"  2015Q3-Q4 only: T: {(t_pre.mean()*100):.3f} (N={t_pre.notna().sum():,})   C: {(c_pre.mean()*100):.3f} (N={c_pre.notna().sum():,})")
