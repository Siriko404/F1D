"""Quick DiD with BOTH CASH formulas (T1 and T8)."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0]

# Use latest dir that has BOTH beta_uk AND variables AND stock_returns AND consensus_eps
runs = sorted([d for d in OUT.iterdir() if d.is_dir()
               and (d/"beta_uk.parquet").exists()
               and (d/"variables_panel.parquet").exists()
               and (d/"stock_returns.parquet").exists()
               and (d/"consensus_eps.parquet").exists()
               and (d/"psm_matches.parquet").exists()], reverse=True)

if not runs:
    # Fall back: run without PSM matches (full sample)
    use_matched = False
    beta_dir = latest("beta_uk.parquet")
else:
    use_matched = True
    beta_dir = runs[0]

panel = pd.read_parquet(beta_dir / "variables_panel.parquet")
beta = pd.read_parquet(beta_dir / "beta_uk.parquet")
sret = pd.read_parquet(beta_dir / "stock_returns.parquet")
ceps = pd.read_parquet(beta_dir / "consensus_eps.parquet")
if use_matched:
    matches = pd.read_parquet(beta_dir / "psm_matches.parquet")

panel = panel.merge(sret, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(beta[["gvkey","beta_uk"]], on="gvkey", how="left")

# Treatment
nonneg = beta[beta["beta_uk"] >= 0]
t1 = nonneg["beta_uk"].quantile(1/3); t2 = nonneg["beta_uk"].quantile(2/3)
panel["HIGH_UK"] = (panel["beta_uk"] > t2).astype(float)
panel["LOW_UK"] = ((panel["beta_uk"] >= 0) & (panel["beta_uk"] < t1)).astype(float)
panel = panel[(panel["HIGH_UK"]==1) | (panel["LOW_UK"]==1)].copy()

PRE_Q = [20153, 20154]; POST_Q = [20163, 20164]
panel = panel[panel["cal_yr_qtr"].isin(PRE_Q + POST_Q)].copy()
panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(float)
panel["TREAT_POST"] = panel["HIGH_UK"] * panel["POST"]

# Match (if available)
if use_matched:
    mgv = set(matches["treated_gvkey"]) | set(matches["control_gvkey"])
    panel = panel[panel["gvkey"].isin(mgv)].copy()
    label = "matched"
else:
    label = "full"
print(f"Sample: {label}, {len(panel)} obs")

# Lag controls from FULL panel
full = pd.read_parquet(beta_dir / "variables_panel.parquet")
full = full.merge(sret, on=["gvkey","cal_yr_qtr"], how="left")
full = full.merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")
ctrl_cols = ["STOCK_RETURNS","TOBIN_Q","CASH_FLOW","SIZE","SALES_GROWTH","CONSENSUS_EPS"]
full = full.sort_values(["gvkey","cal_yr_qtr"])
for c in ctrl_cols:
    full[f"{c}_lag1"] = full.groupby("gvkey")[c].shift(1)
lag_data = full[["gvkey","cal_yr_qtr"] + [f"{c}_lag1" for c in ctrl_cols]]
panel = panel.merge(lag_data, on=["gvkey","cal_yr_qtr"], how="left")

# CASH_T1 = CASH from variables (cheq/atq_lag1) — Table 1 version
# CASH column already exists — check pre/post for both CASH and CASH_T8

for dv, label in [("CASH", "CASH [Table 1: cheq/atq_lag1]")]:
    sub = panel.dropna(subset=[dv] + [f"{c}_lag1" for c in ctrl_cols])
    pt = sub[(sub["HIGH_UK"]==1) & (sub["POST"]==1)][dv]
    pp = sub[(sub["HIGH_UK"]==1) & (sub["POST"]==0)][dv]
    ct = sub[(sub["HIGH_UK"]==0) & (sub["POST"]==1)][dv]
    cp = sub[(sub["HIGH_UK"]==0) & (sub["POST"]==0)][dv]
    did = (pt.mean() - pp.mean()) - (ct.mean() - cp.mean())
    print(f"\n=== {label} ===")
    print(f"  Treated PRE  mean={pp.mean():.4f}  N={len(pp)}")
    print(f"  Treated POST mean={pt.mean():.4f}  N={len(pt)}")
    print(f"  Control PRE  mean={cp.mean():.4f}  N={len(cp)}")
    print(f"  Control POST mean={ct.mean():.4f}  N={len(ct)}")
    print(f"  Raw DiD (means): {did:.4f}")
    print(f"  Paper: δ=+0.231 positive")

# Run regression
sub = panel.dropna(subset=["CASH"] + [f"{c}_lag1" for c in ctrl_cols])
sub = sub.set_index(["gvkey","cal_yr_qtr"])
exog_vars = ["TREAT_POST"] + [f"{c}_lag1" for c in ctrl_cols]
exog = sub[exog_vars]
exog["SIC2xQuarter"] = 0  # dummy — real code uses actual FE, approximating here
try:
    mod = PanelOLS(sub["CASH"], exog, entity_effects=True, time_effects=True)
    res = mod.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
    print(f"\n  PanelOLS δ = {res.params['TREAT_POST']:.4f}  SE={res.std_errors['TREAT_POST']:.4f}  t={res.tstats['TREAT_POST']:.2f}  p={res.pvalues['TREAT_POST']:.4f}")
    print(f"  N={res.nobs:,}  R²={res.rsquared:.4f}")
except Exception as e:
    print(f"  PanelOLS failed: {e}")
