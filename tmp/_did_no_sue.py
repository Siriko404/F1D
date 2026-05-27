"""DiD without CONSENSUS_EPS control — test if N bottleneck is worth dropping."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import shutil
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d/fname).exists()], reverse=True)
    return runs[0]

beta_dir = OUT / "20260527_010458"  # variant F
for fn in ["consensus_eps.parquet", "stock_returns.parquet"]:
    src = latest(fn) / fn; dst = beta_dir / fn
    if src != dst and not dst.exists(): shutil.copy(str(src), str(dst))

panel = pd.read_parquet(beta_dir / "variables_panel.parquet")
beta = pd.read_parquet(beta_dir / "beta_uk.parquet")
sret = pd.read_parquet(beta_dir / "stock_returns.parquet")
ceps = pd.read_parquet(beta_dir / "consensus_eps.parquet")

panel = panel.merge(sret, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(beta[["gvkey","beta_uk"]], on="gvkey", how="left")

PRE_Q=[20153,20154]; POST_Q=[20163,20164]
panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(float)
panel["POST_BETA"] = panel["POST"] * panel["beta_uk"]

panel = panel.sort_values(["gvkey","cal_yr_qtr"])
ctrl_full = ["STOCK_RETURNS","TOBIN_Q","CASH_FLOW","SIZE","SALES_GROWTH","CONSENSUS_EPS"]
ctrl_no_sue = ["STOCK_RETURNS","TOBIN_Q","CASH_FLOW","SIZE","SALES_GROWTH"]
for c in ctrl_full:
    panel[f"{c}_lag1"] = panel.groupby("gvkey")[c].shift(1)

# CASH_T8
comp = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
                       columns=["gvkey","datadate","atq","cheq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
for c in ["atq","cheq"]: comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp = comp.drop_duplicates(["gvkey","datadate"], keep="last")
panel = panel.merge(comp[["gvkey","datadate","cheq"]], on=["gvkey","datadate"], how="left")
panel = panel.sort_values(["gvkey","cal_yr_qtr"])
panel["atq_l1"] = panel.groupby("gvkey")["atq"].shift(1)
panel["cheq_l1"] = panel.groupby("gvkey")["cheq"].shift(1)
denom = panel["atq_l1"] - panel["cheq_l1"]
panel["CASH_T8"] = np.where((denom.notna())&(denom>0), panel["cheq"]/denom, np.nan)
for q, idx in panel.groupby("cal_yr_qtr").groups.items():
    v = panel.loc[idx,"CASH_T8"]
    if v.notna().sum()<10: continue
    lo, hi = v.quantile(0.01), v.quantile(0.99); panel.loc[idx,"CASH_T8"] = v.clip(lo, hi)

did = panel[panel["cal_yr_qtr"].isin(PRE_Q+POST_Q)].copy()

for dv, label in [("CASH","CASH_T1"), ("CASH_T8","CASH_T8")]:
    for ctrl_set, ctrl_name in [(ctrl_full, "with CONSENSUS_EPS"), (ctrl_no_sue, "without CONSENSUS_EPS")]:
        req = [dv,"beta_uk"] + [f"{c}_lag1" for c in ctrl_set]
        sub = did.dropna(subset=req).set_index(["gvkey","cal_yr_qtr"])
        exog = sub[["POST_BETA"]+[f"{c}_lag1" for c in ctrl_set]]
        try:
            mod = PanelOLS(sub[dv], exog, entity_effects=True, time_effects=True)
            res = mod.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
            b=res.params["POST_BETA"]; se=res.std_errors["POST_BETA"]
            t=res.tstats["POST_BETA"]; p=res.pvalues["POST_BETA"]
            sig = "***" if p<0.01 else "**" if p<0.05 else "*" if p<0.10 else ""
            print(f"{label} {ctrl_name:<25} δ={b:.4f}{sig}  SE={se:.4f}  t={t:.2f}  p={p:.4f}  N={res.nobs:,}")
        except Exception as e:
            print(f"{label} {ctrl_name}: {e}")
