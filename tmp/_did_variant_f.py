"""DiD with locked Variant F β + paper-matched cohort.
Method:
  β source: 20260527_022856 (Variant F: vol_FTSE realized + vol_SP500 + VIX + vol_FX, 60mo)
  Cohort:   nonneg β → 30/70 quantile, T=top-30, C=top-360-of-bottom-30 (paper T=449/C=360)
  Test:    CASH_T1 + CASH_T8 (paper Table 8 uses T8)
  Spec:    PanelOLS, firm FE + time FE, 2-way cluster, lag-1 controls
"""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
beta_dir = OUT / "20260527_022856"  # Variant F locked

beta = pd.read_parquet(beta_dir / "beta_uk.parquet")
nn = beta[beta["beta_uk"]>=0].copy()
t1 = nn["beta_uk"].quantile(0.30); t2 = nn["beta_uk"].quantile(0.70)
print(f"30/70 cutoffs: t1={t1:.4f} t2={t2:.4f}  (paper 0.28/0.68)")

T_count = (nn["beta_uk"]>=t2).sum()
top_360 = nn[nn["beta_uk"]<t1].nlargest(360, "beta_uk")
t_gv = set(nn[nn["beta_uk"]>=t2]["gvkey"])
c_gv = set(top_360["gvkey"])
print(f"T firms: {len(t_gv)}  C firms: {len(c_gv)}  (paper T=449 / C=360)")

# Panel + variables
panel = pd.read_parquet(beta_dir / "variables_panel.parquet")
sret  = pd.read_parquet(beta_dir / "stock_returns.parquet")
ceps  = pd.read_parquet(beta_dir / "consensus_eps.parquet")
panel = panel.merge(sret, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(beta[["gvkey","beta_uk"]], on="gvkey", how="left")

panel["HIGH_UK"] = panel["gvkey"].isin(t_gv).astype(float)
panel["LOW_UK"]  = panel["gvkey"].isin(c_gv).astype(float)
panel_tc = panel[(panel["HIGH_UK"]==1)|(panel["LOW_UK"]==1)].copy()
print(f"T+C panel obs (2010-2016): {len(panel_tc):,}  (paper 17,170)")

POST_Q = [20163, 20164]
panel_tc["POST"] = panel_tc["cal_yr_qtr"].isin(POST_Q).astype(float)
panel_tc["TREAT_POST"] = panel_tc["HIGH_UK"] * panel_tc["POST"]

panel_tc = panel_tc.sort_values(["gvkey","cal_yr_qtr"])
ctrl = ["STOCK_RETURNS","TOBIN_Q","CASH_FLOW","SIZE","SALES_GROWTH","CONSENSUS_EPS"]
for c in ctrl:
    panel_tc[f"{c}_lag1"] = panel_tc.groupby("gvkey")[c].shift(1)

# Build CASH_T1 + CASH_T8 from compustat
comp = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
                       columns=["gvkey","datadate","atq","cheq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
for c in ["atq","cheq"]: comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp = comp.drop_duplicates(["gvkey","datadate"], keep="last")
panel_tc = panel_tc.merge(comp[["gvkey","datadate","cheq"]], on=["gvkey","datadate"], how="left")
panel_tc = panel_tc.sort_values(["gvkey","cal_yr_qtr"])
panel_tc["atq_l1"]  = panel_tc.groupby("gvkey")["atq"].shift(1)
panel_tc["cheq_l1"] = panel_tc.groupby("gvkey")["cheq"].shift(1)
denom = panel_tc["atq_l1"] - panel_tc["cheq_l1"]
panel_tc["CASH_T8"] = np.where((denom.notna())&(denom>0), panel_tc["cheq"]/denom, np.nan)
# Winsorize 1/99 by quarter
for q, idx in panel_tc.groupby("cal_yr_qtr").groups.items():
    v = panel_tc.loc[idx,"CASH_T8"]
    if v.notna().sum()<10: continue
    lo, hi = v.quantile(0.01), v.quantile(0.99); panel_tc.loc[idx,"CASH_T8"] = v.clip(lo, hi)

# Build linear β interaction
panel["beta_post"] = panel["beta_uk"] * panel["cal_yr_qtr"].isin(POST_Q).astype(float)
panel = panel.sort_values(["gvkey","cal_yr_qtr"])
for c in ctrl:
    panel[f"{c}_lag1"] = panel.groupby("gvkey")[c].shift(1)
panel = panel.merge(comp[["gvkey","datadate","cheq"]], on=["gvkey","datadate"], how="left")
panel = panel.sort_values(["gvkey","cal_yr_qtr"])
panel["atq_l1"]  = panel.groupby("gvkey")["atq"].shift(1)
panel["cheq_l1"] = panel.groupby("gvkey")["cheq"].shift(1)
den2 = panel["atq_l1"] - panel["cheq_l1"]
panel["CASH_T8"] = np.where((den2.notna())&(den2>0), panel["cheq"]/den2, np.nan)
for q, idx in panel.groupby("cal_yr_qtr").groups.items():
    v = panel.loc[idx,"CASH_T8"]
    if v.notna().sum()<10: continue
    lo, hi = v.quantile(0.01), v.quantile(0.99); panel.loc[idx,"CASH_T8"] = v.clip(lo, hi)

def run(p, treat_col, dv, label):
    cols_need = [dv, treat_col] + [f"{c}_lag1" for c in ctrl]
    sub = p.dropna(subset=cols_need).set_index(["gvkey","cal_yr_qtr"])
    exog = sub[[treat_col]+[f"{c}_lag1" for c in ctrl]]
    try:
        mod = PanelOLS(sub[dv], exog, entity_effects=True, time_effects=True)
        res = mod.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
        b=res.params[treat_col]; se=res.std_errors[treat_col]
        t=res.tstats[treat_col]; p_v=res.pvalues[treat_col]
        sig="***" if p_v<0.01 else "**" if p_v<0.05 else "*" if p_v<0.10 else ""
        return f"  {label}: δ={b:+.4f}{sig:<3}  SE={se:.4f}  t={t:+.2f}  p={p_v:.4f}  N={res.nobs:,}"
    except Exception as e:
        return f"  {label}: ERROR {e}"

print(f"\n=== DiD on MATCHED COHORT (T=449/C=360, binary) ===")
print(run(panel_tc, "TREAT_POST", "CASH",    "CASH_T1"))
print(run(panel_tc, "TREAT_POST", "CASH_T8", "CASH_T8 (paper)"))

print(f"\n=== DiD on FULL panel (linear β interaction) ===")
print(run(panel, "beta_post", "CASH",    "CASH_T1"))
print(run(panel, "beta_post", "CASH_T8", "CASH_T8 (paper)"))

print(f"\nPaper Table 8: δ=+0.231*** N=17,170")
