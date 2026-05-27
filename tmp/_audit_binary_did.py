"""Audit binary DiD carefully. Check:
1. Treatment direction (HIGH_UK definition)
2. CASH variable per quarter (raw values)
3. Sign of mean differences
4. Whether wrong firms are treated"""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
beta_dir = OUT / "20260527_010458"

panel = pd.read_parquet(beta_dir / "variables_panel.parquet")
beta = pd.read_parquet(beta_dir / "beta_uk.parquet")
sret = pd.read_parquet(beta_dir / "stock_returns.parquet")
ceps = pd.read_parquet(beta_dir / "consensus_eps.parquet")

panel = panel.merge(sret, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(beta[["gvkey","beta_uk"]], on="gvkey", how="left")

# Paper's β^UK partition (page 22 verbatim): nonneg → terciles → top vs bottom
nonneg = beta[beta["beta_uk"]>=0]
print(f"β^UK distribution:")
print(f"  Total firms with β: {len(beta):,}")
print(f"  β >= 0: {len(nonneg):,}  β < 0: {(beta['beta_uk']<0).sum():,}")
t1 = nonneg["beta_uk"].quantile(1/3); t2 = nonneg["beta_uk"].quantile(2/3)
print(f"  Nonneg terciles: t1={t1:.4f}  t2={t2:.4f}")

# Test 4 partition specs
specs = {
    "Spec A: nonneg→tercile (TOP vs BOT)": (nonneg["beta_uk"]>=t2, (nonneg["beta_uk"]>=0)&(nonneg["beta_uk"]<t1)),
    "Spec B: all firms→tercile (TOP vs BOT)": (beta["beta_uk"]>=beta["beta_uk"].quantile(2/3), beta["beta_uk"]<beta["beta_uk"].quantile(1/3)),
    "Spec C: nonneg→tercile, BOT excludes near-0": (nonneg["beta_uk"]>=t2, (nonneg["beta_uk"]>=0.05)&(nonneg["beta_uk"]<t1)),
}
for name, (t_mask, c_mask) in specs.items():
    print(f"\n{name}")
    if "nonneg" in name and "all firms" not in name:
        t_gv = set(nonneg[t_mask]["gvkey"])
        c_gv = set(nonneg[c_mask]["gvkey"])
    else:
        t_gv = set(beta[t_mask]["gvkey"])
        c_gv = set(beta[c_mask]["gvkey"])
    print(f"  T={len(t_gv)}  C={len(c_gv)}  (paper: 449/360)")

# Best matching to paper N — use Spec C with min β = ?
print(f"\n--- Find min-β-control that gives C=360 ---")
sorted_nonneg = nonneg.sort_values("beta_uk")
top_t = nonneg[nonneg["beta_uk"]>=t2]
# Bottom tercile = 449 firms. Take 360 with highest β within that
n_t = len(top_t)
bottom_tercile = nonneg[nonneg["beta_uk"]<t1]
top_of_bottom_360 = bottom_tercile.nlargest(360, "beta_uk")
min_beta_control = top_of_bottom_360["beta_uk"].min()
print(f"  Top tercile N={n_t} (paper 449)")
print(f"  If control = top 360 of bottom tercile: min β = {min_beta_control:.4f}")

# Now CASH check
print(f"\n--- CASH mean by tercile and quarter ---")
for trt_label, trt_gv in [("HIGH_UK (top)", set(top_t["gvkey"])), ("LOW_UK (bottom)", set(bottom_tercile["gvkey"]))]:
    sub = panel[panel["gvkey"].isin(trt_gv)]
    print(f"\n{trt_label}: N firms={len(trt_gv):,}")
    for q in [20153, 20154, 20163, 20164]:
        qsub = sub[sub["cal_yr_qtr"]==q]
        print(f"  Q={q}: CASH mean={qsub['CASH'].mean():.4f}  N={len(qsub):,}")
