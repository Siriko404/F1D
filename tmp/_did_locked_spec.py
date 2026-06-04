"""DiD per LOCKED spec (campello_variable_lockin.md lines 374, 778, 1909, 1972).
  β cutoffs:  HARD  T = β > 0.68, C = β < 0.28
  Sample:    T ∪ C firms, 2010Q1-2016Q4
  DV:        CASH_T8 = cheq / (atq_lag1 - cheq_lag1)
  Controls:  TOBIN_Q, CASH_FLOW, SIZE, SALES_GROWTH, CONSENSUS_EPS, STOCK_RETURNS (all lagged t-1)
  POST:      = 1 if quarter ∈ {2016Q3, 2016Q4}
  FE:        firm + Hoberg-Phillips FIC100 × calendar-quarter
  β source:  Variant F (20260527_022856)
"""
import warnings; warnings.filterwarnings("ignore")
import zipfile
from io import BytesIO
from pathlib import Path
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT  = ROOT/"outputs"/"campello_v2"
bdir = OUT/"20260527_023553"  # Paper-verbatim 3-ctrl β

# --- β + HARD cutoffs per paper p3193 ---
beta = pd.read_parquet(bdir/"beta_uk.parquet")
t_gv = set(beta.loc[beta["beta_uk"]>0.68, "gvkey"])
c_gv = set(beta.loc[(beta["beta_uk"]>=0)&(beta["beta_uk"]<0.28), "gvkey"])
print(f"Hard cutoffs T(β>0.68)={len(t_gv):,}  C(0≤β<0.28)={len(c_gv):,}  (paper 449/360)")

# --- Panel ---
panel = pd.read_parquet(bdir/"variables_panel.parquet")
sret  = pd.read_parquet(bdir/"stock_returns.parquet")
ceps  = pd.read_parquet(bdir/"consensus_eps.parquet")
p = panel.merge(sret, on=["gvkey","cal_yr_qtr"], how="left").merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")

# --- Add CASH_T8 ---
comp = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
                       columns=["gvkey","datadate","atq","cheq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
for c in ["atq","cheq"]: comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp = comp.drop_duplicates(["gvkey","datadate"], keep="last")
p = p.merge(comp[["gvkey","datadate","cheq"]], on=["gvkey","datadate"], how="left")
p = p.sort_values(["gvkey","cal_yr_qtr"])
p["atq_l1"]  = p.groupby("gvkey")["atq"].shift(1)
p["cheq_l1"] = p.groupby("gvkey")["cheq"].shift(1)
denom = p["atq_l1"] - p["cheq_l1"]
p["CASH_T8"] = np.where((denom.notna())&(denom>0), p["cheq"]/denom, np.nan)
# Winsorize 1/99 by quarter
for q, idx in p.groupby("cal_yr_qtr").groups.items():
    v = p.loc[idx,"CASH_T8"]
    if v.notna().sum()<10: continue
    lo, hi = v.quantile(0.01), v.quantile(0.99); p.loc[idx,"CASH_T8"] = v.clip(lo, hi)

# --- Lagged controls ---
ctrl = ["STOCK_RETURNS","TOBIN_Q","CASH_FLOW","SIZE","SALES_GROWTH","CONSENSUS_EPS"]
for c in ctrl:
    p[f"{c}_lag1"] = p.groupby("gvkey")[c].shift(1)

# --- Hoberg-Phillips FIC100 industry ---
with zipfile.ZipFile(ROOT/"inputs"/"Brexit_replication"/"HobergPhillips_FIC"/"FIC_Data.zip") as zf:
    with zf.open("fic_data.txt") as f:
        fic = pd.read_csv(BytesIO(f.read()), sep="\t", usecols=["gvkey","year","icode100"],
                          dtype={"gvkey":"Int64","year":"Int64","icode100":"Int64"})
fic["gvkey"] = fic["gvkey"].astype(str).str.zfill(6)
fic = fic.rename(columns={"icode100":"fic100","year":"cal_yr"})
p["cal_yr"] = (p["cal_yr_qtr"]//10).astype(int)
p = p.merge(fic, on=["gvkey","cal_yr"], how="left")
print(f"FIC100 coverage: {p['fic100'].notna().mean()*100:.1f}%")

# --- Filter to T+C ---
p["HIGH_UK"]  = p["gvkey"].isin(t_gv).astype(int)
p["LOW_UK"]   = p["gvkey"].isin(c_gv).astype(int)
p_tc = p[(p["HIGH_UK"]==1)|(p["LOW_UK"]==1)].copy()
print(f"T+C panel obs (raw): {len(p_tc):,}  firms={p_tc['gvkey'].nunique():,}  (paper N=17,170)")

p_tc["POST"] = p_tc["cal_yr_qtr"].isin([20163, 20164]).astype(float)
p_tc["TREAT_POST"] = p_tc["HIGH_UK"] * p_tc["POST"]
p_tc["industry_q"] = p_tc["fic100"].fillna(-1).astype(int).astype(str) + "_" + p_tc["cal_yr_qtr"].astype(str)

# --- Run DiD ---
def run_did(p_in, label, use_indq):
    cols = ["CASH_T8","TREAT_POST"] + [f"{c}_lag1" for c in ctrl] + (["industry_q"] if use_indq else [])
    sub = p_in.dropna(subset=cols).copy()
    if "industry_q" in cols:
        idx_ind = sub.set_index(["industry_q","cal_yr_qtr"])
    sub = sub.set_index(["gvkey","cal_yr_qtr"])
    exog = sub[["TREAT_POST"]+[f"{c}_lag1" for c in ctrl]]
    try:
        if use_indq:
            # Firm FE + industry-quarter dummies
            ind_dum = pd.get_dummies(sub["industry_q"], drop_first=True, dtype=float)
            exog2 = pd.concat([exog, ind_dum], axis=1)
            mod = PanelOLS(sub["CASH_T8"], exog2, entity_effects=True)
        else:
            mod = PanelOLS(sub["CASH_T8"], exog, entity_effects=True, time_effects=True)
        res = mod.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
        b=res.params["TREAT_POST"]; se=res.std_errors["TREAT_POST"]
        t=res.tstats["TREAT_POST"]; pv=res.pvalues["TREAT_POST"]
        sig="***" if pv<0.01 else "**" if pv<0.05 else "*" if pv<0.10 else ""
        print(f"  {label}: δ={b:+.4f}{sig:<3}  SE={se:.4f}  t={t:+.2f}  p={pv:.4f}  N={res.nobs:,}")
    except Exception as e:
        print(f"  {label}: ERROR {type(e).__name__}: {str(e)[:200]}")

print("\n=== DiD on T(β>0.68) vs C(β<0.28), CASH_T8 (Table 8 spec) ===")
run_did(p_tc, "Firm FE + Quarter FE (simpler)",         use_indq=False)
run_did(p_tc, "Firm FE + Industry×Quarter (paper)",      use_indq=True)
print("Paper Table 8 col 1: δ=+0.231***  N=17,170")
