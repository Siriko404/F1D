"""Proper CASH DiD: PanelOLS with firm FE + cal_yr_qtr FE, double-clustered.
Paper eq(14): Y = δ(POST×HIGH_UK) + θ·CONTROLS_lag1 + FIRM_FE + INDUSTRY×QUARTER_FE"""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0]

# Load
beta_dir = latest("beta_uk.parquet")
panel = pd.read_parquet(beta_dir / "variables_panel.parquet")
beta = pd.read_parquet(beta_dir / "beta_uk.parquet")
sret = pd.read_parquet(beta_dir / "stock_returns.parquet")
ceps = pd.read_parquet(beta_dir / "consensus_eps.parquet")

panel = panel.merge(sret, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(beta[["gvkey","beta_uk"]], on="gvkey", how="left")

# Treatment
nonneg = beta[beta["beta_uk"]>=0]; t1=nonneg["beta_uk"].quantile(1/3); t2=nonneg["beta_uk"].quantile(2/3)
panel["treated"] = (panel["beta_uk"]>t2).astype(float)
panel["control"] = ((panel["beta_uk"]>=0)&(panel["beta_uk"]<t1)).astype(float)
panel = panel[(panel["treated"]==1)|(panel["control"]==1)].copy()

# DiD window
PRE_Q = [20153,20154]; POST_Q = [20163,20164]
panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(float)
panel["TREAT_POST"] = panel["treated"] * panel["POST"]

# Lagged controls
panel = panel.sort_values(["gvkey","cal_yr_qtr"])
ctrl_cols = ["STOCK_RETURNS","TOBIN_Q","CASH_FLOW","SIZE","SALES_GROWTH","CONSENSUS_EPS"]
for c in ctrl_cols:
    panel[f"{c}_lag1"] = panel.groupby("gvkey")[c].shift(1)

# CASH_T1 = CASH (cheq/atq_lag1) — already in variables panel
# CASH_T8 = cheq/(atq_lag1 - cheq_lag1) — compute cleanly
comp = pd.read_parquet(ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet",
                       columns=["gvkey","datadate","atq","cheq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
for c in ["atq","cheq"]: comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp = comp.drop_duplicates(["gvkey","datadate"], keep="last")

# Merge cheq, atq into panel THROUGH the variables data
panel = panel.merge(comp[["gvkey","datadate","cheq"]], on=["gvkey","datadate"], how="left")
panel = panel.sort_values(["gvkey","cal_yr_qtr"])
panel["atq_l1"] = panel.groupby("gvkey")["atq"].shift(1)
panel["cheq_l1"] = panel.groupby("gvkey")["cheq"].shift(1)
denom = panel["atq_l1"] - panel["cheq_l1"]
panel["CASH_T8"] = np.where((denom.notna())&(denom>0), panel["cheq"]/denom, np.nan)

# Winsorize CASH_T8
for q, idx in panel.groupby("cal_yr_qtr").groups.items():
    v = panel.loc[idx,"CASH_T8"]
    if v.notna().sum() < 10: continue
    lo, hi = v.quantile(0.01), v.quantile(0.99)
    panel.loc[idx,"CASH_T8"] = v.clip(lo, hi)

# Restrict to DiD window
did_panel = panel[panel["cal_yr_qtr"].isin(PRE_Q+POST_Q)].copy()

# Means for both CASH defs
for dv,label in [("CASH","CASH_T1[cheq/atq_l1]"),("CASH_T8","CASH_T8[cheq/(atq-cheq)]")]:
    sub = did_panel.dropna(subset=[dv])
    tp = sub[(sub["treated"]==1)&(sub["POST"]==1)][dv].mean()
    tb = sub[(sub["treated"]==1)&(sub["POST"]==0)][dv].mean()
    cp = sub[(sub["treated"]==0)&(sub["POST"]==1)][dv].mean()
    cb = sub[(sub["treated"]==0)&(sub["POST"]==0)][dv].mean()
    did = (tp-tb)-(cp-cb)
    print(f"\n{label}: Tpre={tb:.4f} Tpost={tp:.4f} Cpre={cb:.4f} Cpost={cp:.4f} DiD={did:.4f}")
    print(f"  Paper: δ=+0.231*** (CASH INCREASES for treated post-Brexit)")

# Regression on CASH_T1
from linearmodels.panel import PanelOLS
sub = did_panel.dropna(subset=["CASH"]+[f"{c}_lag1" for c in ctrl_cols]).set_index(["gvkey","cal_yr_qtr"])
exog_cols = ["TREAT_POST"]+[f"{c}_lag1" for c in ctrl_cols]
try:
    mod = PanelOLS(sub["CASH"], sub[exog_cols], entity_effects=True, time_effects=True)
    res = mod.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
    print(f"\nCASH_T1 DiD regression:")
    print(f"  δ = {res.params['TREAT_POST']:.4f}  SE={res.std_errors['TREAT_POST']:.4f}  t={res.tstats['TREAT_POST']:.2f}  p={res.pvalues['TREAT_POST']:.4f}")
    print(f"  N={res.nobs:,}  R²={res.rsquared:.4f}")
    print(f"  Paper Table 8: N=17,170 R²=0.21")
except Exception as e:
    print(f"  PanelOLS failed: {e}")
