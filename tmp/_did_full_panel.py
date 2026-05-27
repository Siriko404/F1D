"""DiD on FULL panel 2010Q1-2016Q4. POST=1 only in 2016Q3-Q4.
Paper Table 8 N=17,170 → ~21 quarters per firm × 809 firms."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

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

# Binary treatment
nonneg = beta[beta["beta_uk"]>=0]
t1 = nonneg["beta_uk"].quantile(1/3); t2 = nonneg["beta_uk"].quantile(2/3)
panel["HIGH_UK"] = (panel["beta_uk"]>t2).astype(float)
panel["LOW_UK"] = ((panel["beta_uk"]>=0)&(panel["beta_uk"]<t1)).astype(float)
panel = panel[(panel["HIGH_UK"]==1)|(panel["LOW_UK"]==1)].copy()
print(f"Treated firms: {panel[panel['HIGH_UK']==1]['gvkey'].nunique()}")
print(f"Control firms: {panel[panel['LOW_UK']==1]['gvkey'].nunique()}")

# POST = 1 in 2016Q3 OR 2016Q4. Use FULL panel 2010Q1-2016Q4.
POST_Q = [20163,20164]
panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(float)
panel["TREAT_POST"] = panel["HIGH_UK"] * panel["POST"]

# Lag controls
panel = panel.sort_values(["gvkey","cal_yr_qtr"])
ctrl = ["STOCK_RETURNS","TOBIN_Q","CASH_FLOW","SIZE","SALES_GROWTH","CONSENSUS_EPS"]
for c in ctrl:
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
denom = panel["atq_l1"]-panel["cheq_l1"]
panel["CASH_T8"] = np.where((denom.notna())&(denom>0), panel["cheq"]/denom, np.nan)
for q, idx in panel.groupby("cal_yr_qtr").groups.items():
    v = panel.loc[idx,"CASH_T8"]
    if v.notna().sum()<10: continue
    lo, hi = v.quantile(0.01), v.quantile(0.99); panel.loc[idx,"CASH_T8"] = v.clip(lo, hi)

# Try multiple DiD window definitions
windows = {
    "FULL 2010Q1-2016Q4": panel,
    "4Q (2015Q3-Q4 vs 2016Q3-Q4)": panel[panel["cal_yr_qtr"].isin([20153,20154,20163,20164])],
    "8Q (2015Q1-Q4 vs 2016Q1-Q4)": panel[panel["cal_yr_qtr"].isin([20151,20152,20153,20154,20161,20162,20163,20164])],
    "PRE=2010-2015Q4 + POST=2016Q3-Q4": panel[(panel["cal_yr_qtr"]<=20154)|(panel["cal_yr_qtr"].isin([20163,20164]))],
}
for wname, did in windows.items():
    print(f"\n========== WINDOW: {wname} (N={len(did):,}) ==========")

    for dv,label in [("CASH","CASH_T1"),("CASH_T8","CASH_T8")]:
        sub = did.dropna(subset=[dv]+[f"{c}_lag1" for c in ctrl]).set_index(["gvkey","cal_yr_qtr"])
        exog = sub[["TREAT_POST"]+[f"{c}_lag1" for c in ctrl]]
        try:
            mod = PanelOLS(sub[dv], exog, entity_effects=True, time_effects=True)
            res = mod.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
            b=res.params["TREAT_POST"]; se=res.std_errors["TREAT_POST"]
            t=res.tstats["TREAT_POST"]; p=res.pvalues["TREAT_POST"]
            sig="***" if p<0.01 else "**" if p<0.05 else "*" if p<0.10 else ""
            print(f"  {label}: δ={b:.4f}{sig}  SE={se:.4f}  t={t:.2f}  p={p:.4f}  N={res.nobs:,}")
        except Exception as e:
            print(f"  {label}: {e}")
print(f"\nPaper Table 8 col 1: δ=+0.231*** N=17,170")
