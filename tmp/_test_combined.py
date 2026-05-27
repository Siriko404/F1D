"""Combine 30/70 quantile + min-C threshold to hit T=449, C=360."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
beta_dir = OUT / "20260527_010458"

beta = pd.read_parquet(beta_dir / "beta_uk.parquet")
nn = beta[beta["beta_uk"]>=0]
t1 = nn["beta_uk"].quantile(0.30); t2 = nn["beta_uk"].quantile(0.70)
print(f"30/70 cutoffs: t1={t1:.4f} t2={t2:.4f}")

T_count = (nn["beta_uk"]>=t2).sum()
print(f"T count: {T_count} (paper 449)")

# Iterate min-β threshold for C
print(f"\n{'min_β':>10}{'C_count':>10}{'|diff|':>10}")
for thresh in [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, t1*0.5]:
    c = ((nn["beta_uk"]>=thresh)&(nn["beta_uk"]<t1)).sum()
    print(f"{thresh:>10.4f}{c:>10}{abs(c-360):>10}")

# Find threshold that gives exactly 360
target = 360
sorted_c = nn[nn["beta_uk"]<t1].sort_values("beta_uk")
top_360 = sorted_c.nlargest(360, "beta_uk")
min_c_beta = top_360["beta_uk"].min()
print(f"\nExact C=360 needs min β = {min_c_beta:.4f}")

# Final method: 30/70 + take top 360 of bottom 30
panel = pd.read_parquet(beta_dir / "variables_panel.parquet")
sret = pd.read_parquet(beta_dir / "stock_returns.parquet")
ceps = pd.read_parquet(beta_dir / "consensus_eps.parquet")

panel = panel.merge(sret, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(beta[["gvkey","beta_uk"]], on="gvkey", how="left")

t_gv = set(nn[nn["beta_uk"]>=t2]["gvkey"])
c_gv = set(top_360["gvkey"])
print(f"\nT firms: {len(t_gv)}  C firms: {len(c_gv)}")

panel["HIGH_UK"] = panel["gvkey"].isin(t_gv).astype(float)
panel["LOW_UK"] = panel["gvkey"].isin(c_gv).astype(float)
panel = panel[(panel["HIGH_UK"]==1)|(panel["LOW_UK"]==1)].copy()
print(f"T+C panel obs (2010-2016): {len(panel):,}")

POST_Q = [20163,20164]
panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(float)
panel["TREAT_POST"] = panel["HIGH_UK"] * panel["POST"]

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

print(f"\n=== DiD with T=449 C=360 (paper-matched cohort sizes) ===")
for dv,label in [("CASH","CASH_T1"),("CASH_T8","CASH_T8")]:
    sub = panel.dropna(subset=[dv]+[f"{c}_lag1" for c in ctrl]).set_index(["gvkey","cal_yr_qtr"])
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
print(f"Paper Table 8: δ=+0.231*** N=17,170")
