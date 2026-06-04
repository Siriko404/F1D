"""Diagnose N drop in DiD regression. Where does 18,510 → 9,510 come from?"""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
beta_dir = ROOT/"outputs"/"campello_v2"/"20260527_022856"

beta = pd.read_parquet(beta_dir/"beta_uk.parquet")
nn = beta[beta["beta_uk"]>=0]
t1 = nn["beta_uk"].quantile(0.30); t2 = nn["beta_uk"].quantile(0.70)
t_gv = set(nn[nn["beta_uk"]>=t2]["gvkey"])
c_gv = set(nn[nn["beta_uk"]<t1].nlargest(360,"beta_uk")["gvkey"])

panel = pd.read_parquet(beta_dir/"variables_panel.parquet")
sret  = pd.read_parquet(beta_dir/"stock_returns.parquet")
ceps  = pd.read_parquet(beta_dir/"consensus_eps.parquet")
p = panel.merge(sret, on=["gvkey","cal_yr_qtr"], how="left").merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")
p = p[p["gvkey"].isin(t_gv|c_gv)].copy()
print(f"After T+C filter: {len(p):,} obs ({p['gvkey'].nunique():,} firms)")

ctrl = ["STOCK_RETURNS","TOBIN_Q","CASH_FLOW","SIZE","SALES_GROWTH","CONSENSUS_EPS"]
p = p.sort_values(["gvkey","cal_yr_qtr"])
for c in ctrl:
    p[f"{c}_lag1"] = p.groupby("gvkey")[c].shift(1)

# Coverage diagnostic
print(f"\nVariable coverage (T+C cohort, 2010-2016):")
for c in ctrl:
    pct = p[f"{c}_lag1"].notna().mean()*100
    print(f"  {c:<20}_lag1: {pct:.1f}%  ({p[f'{c}_lag1'].notna().sum():,}/{len(p):,})")

# CASH formula
comp = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
                       columns=["gvkey","datadate","atq","cheq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
for c in ["atq","cheq"]: comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp = comp.drop_duplicates(["gvkey","datadate"], keep="last")
p = p.merge(comp[["gvkey","datadate","cheq"]], on=["gvkey","datadate"], how="left")
p = p.sort_values(["gvkey","cal_yr_qtr"])
p["atq_l1"] = p.groupby("gvkey")["atq"].shift(1)
p["cheq_l1"] = p.groupby("gvkey")["cheq"].shift(1)
p["CASH_T8"] = np.where((p["atq_l1"].notna())&(p["cheq_l1"].notna())&((p["atq_l1"]-p["cheq_l1"])>0),
                        p["cheq"]/(p["atq_l1"]-p["cheq_l1"]), np.nan)

print(f"\nCoverage with DV constraint:")
print(f"  CASH (T1): {p['CASH'].notna().sum():,}")
print(f"  CASH_T8:   {p['CASH_T8'].notna().sum():,}")

# Stepwise drop with CASH_T8
masks = {}
masks["all"] = p["CASH_T8"].notna()
masks["+STOCK_RET"]   = masks["all"] & p["STOCK_RETURNS_lag1"].notna()
masks["+TOBIN_Q"]     = masks["+STOCK_RET"] & p["TOBIN_Q_lag1"].notna()
masks["+CASH_FLOW"]   = masks["+TOBIN_Q"] & p["CASH_FLOW_lag1"].notna()
masks["+SIZE"]        = masks["+CASH_FLOW"] & p["SIZE_lag1"].notna()
masks["+SALES_GROWTH"]= masks["+SIZE"] & p["SALES_GROWTH_lag1"].notna()
masks["+CONSENSUS_EPS"]=masks["+SALES_GROWTH"] & p["CONSENSUS_EPS_lag1"].notna()

prev = len(p)
print(f"\nStepwise drop (target paper N=17,170):")
print(f"  start (T+C): {prev:,}")
for k,m in masks.items():
    n = m.sum()
    print(f"  after {k:<18}: {n:,}  (Δ={n-prev:+,})")
    prev = n

# Try DiD without CONSENSUS_EPS (it's the killer)
print(f"\nN with NO CONSENSUS_EPS in controls:")
ctrl5 = [c for c in ctrl if c!="CONSENSUS_EPS"]
need5 = ["CASH_T8"] + [f"{c}_lag1" for c in ctrl5]
print(f"  CASH_T8: {p.dropna(subset=need5).shape[0]:,}")
