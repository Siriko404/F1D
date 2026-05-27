"""Compare β^UK rank correlation: VFTSE vs realized FTSE vol."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

# VFTSE-β (latest proper run)
runs_vftse = sorted([d for d in OUT.iterdir() if d.is_dir() and (d/"beta_uk.parquet").exists()
                     and "20260527_005430" in str(d)], reverse=True)
beta_vftse = pd.read_parquet(runs_vftse[0] / "beta_uk.parquet")
beta_vftse = beta_vftse.rename(columns={"beta_uk": "beta_vftse"})

# Realized-vol β (variant F: vol_FTSE_real + vol_SP500_real + VIX + vol_FX)
# Find latest save_beta_vix output
runs_vix = sorted([d for d in OUT.iterdir() if d.is_dir() and (d/"beta_uk.parquet").exists()
                   and "20260526_235751" in str(d)], reverse=True)
beta_vix = pd.read_parquet(runs_vix[0] / "beta_uk.parquet")
beta_vix = beta_vix.rename(columns={"beta_uk": "beta_vix"})

# Merge and compare
merged = beta_vftse.merge(beta_vix, on="gvkey", how="inner")
print(f"Firms in both: {len(merged):,}")
print(f"Rank correlation: {merged[['beta_vftse','beta_vix']].corr(method='spearman').iloc[0,1]:.4f}")
print(f"Pearson correlation: {merged[['beta_vftse','beta_vix']].corr().iloc[0,1]:.4f}")

# Agreement on top tercile assignment
for label, col in [("VFTSE β", "beta_vftse"), ("VIX β", "beta_vix")]:
    nonneg = merged[merged[col] >= 0]
    t2 = nonneg[col].quantile(2/3)
    top_set = set(nonneg[nonneg[col] > t2]["gvkey"])
    print(f"\n{label}: {len(top_set)} top-tercile firms")

# Overlap in top-tercile firms between the two methods
nonneg_vftse = merged[merged["beta_vftse"] >= 0]
t2_vftse = nonneg_vftse["beta_vftse"].quantile(2/3)
top_vftse = set(nonneg_vftse[nonneg_vftse["beta_vftse"] > t2_vftse]["gvkey"])

nonneg_vix = merged[merged["beta_vix"] >= 0]
t2_vix = nonneg_vix["beta_vix"].quantile(2/3)
top_vix = set(nonneg_vix[nonneg_vix["beta_vix"] > t2_vix]["gvkey"])

overlap = top_vftse & top_vix
print(f"\nTop-tercile overlap: {len(overlap)} / {len(top_vftse)} VFTSE-top ({len(overlap)/len(top_vftse)*100:.1f}%)")
print(f"  VFTSE-top = {len(top_vftse)}, VIX-top = {len(top_vix)}")

# Quick check: do the two β methods select firms with different characteristics?
panel = pd.read_parquet(runs_vftse[0] / "variables_panel.parquet")
# Pre-Brexit values
pre = panel[panel["cal_yr_qtr"] <= 20154].groupby("gvkey")[["DIVESTITURES","CASH","SALES_GROWTH","TOBIN_Q"]].mean().reset_index()

pre_vftse_top = pre[pre["gvkey"].isin(top_vftse)]
pre_vix_top = pre[pre["gvkey"].isin(top_vix)]
print(f"\n=== Firm characteristics: Top-tercile firms ===")
print(f"{'Method':<12}{'N':>6}{'DIVEST':>10}{'CASH':>10}{'SG':>10}{'TOBIN_Q':>10}")
print(f"  VFTSE-top: N={len(pre_vftse_top):>4}  DIV={(pre_vftse_top['DIVESTITURES'].mean()*100):.3f}  CASH={pre_vftse_top['CASH'].mean():.3f}  SG={pre_vftse_top['SALES_GROWTH'].mean():.3f}  Q={pre_vftse_top['TOBIN_Q'].mean():.3f}")
print(f"  VIX-top:   N={len(pre_vix_top):>4}  DIV={(pre_vix_top['DIVESTITURES'].mean()*100):.3f}  CASH={pre_vix_top['CASH'].mean():.3f}  SG={pre_vix_top['SALES_GROWTH'].mean():.3f}  Q={pre_vix_top['TOBIN_Q'].mean():.3f}")
print(f"  Paper:      N=449     DIV=0.129   CASH=0.175   SG=0.195   Q=1.948")
