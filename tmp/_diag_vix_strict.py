"""Test VIX β^UK with stricter filters + verify TS demean alternative."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname

# Use latest β (VIX_eom-based)
beta = pd.read_parquet(latest("beta_uk.parquet"))
print(f"β^UK loaded: N={len(beta):,}, mean={beta['beta_uk'].mean():.3f}")

panel = pd.read_parquet(latest("variables_panel.parquet"))
sret = pd.read_parquet(latest("stock_returns.parquet"))
ceps = pd.read_parquet(latest("consensus_eps.parquet"))
comp = pd.read_parquet(ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet",
                      columns=["gvkey", "datadate", "atq", "cheq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
comp["atq"] = pd.to_numeric(comp["atq"], errors="coerce")
comp["cheq"] = pd.to_numeric(comp["cheq"], errors="coerce")
comp = comp.drop_duplicates(subset=["gvkey", "datadate"], keep="last")

p = panel.merge(sret, on=["gvkey", "cal_yr_qtr"], how="left")
p = p.merge(ceps, on=["gvkey", "cal_yr_qtr"], how="left")
p = p.merge(comp[["gvkey", "datadate", "cheq"]], on=["gvkey", "datadate"], how="left",
            suffixes=("_p", ""))
p = p.sort_values(["gvkey", "cal_yr_qtr"])
p["atq_lag1_q"] = p.groupby("gvkey")["atq"].shift(1)
p["cheq_lag1_q"] = p.groupby("gvkey")["cheq"].shift(1)
denom = p["atq_lag1_q"] - p["cheq_lag1_q"]
p["CASH_T8"] = np.where(denom.notna() & (denom > 0), p["cheq"] / denom, np.nan)
p["CASH_T8"] = p["CASH_T8"].replace([np.inf, -np.inf], np.nan)
nv = pd.Series(np.nan, index=p.index)
for q, idx in p.groupby("cal_yr_qtr").groups.items():
    v = p.loc[idx, "CASH_T8"]
    if v.notna().sum() >= 10:
        lo, hi = v.quantile(0.01), v.quantile(0.99)
        nv.loc[idx] = v.clip(lo, hi)
    else:
        nv.loc[idx] = v
p["CASH_T8"] = nv

ctrl_cols = ["STOCK_RETURNS", "TOBIN_Q", "CASH_FLOW", "SIZE", "SALES_GROWTH", "CONSENSUS_EPS"]
for c in ctrl_cols:
    p[f"{c}_lag1"] = p.groupby("gvkey")[c].shift(1)

def did(filter_fn, label):
    from linearmodels import PanelOLS
    bsub = filter_fn(beta).copy()
    if len(bsub) < 100:
        print(f"  {label}: SKIP")
        return
    nonneg = bsub[bsub["beta_uk"] >= 0]
    t1 = nonneg["beta_uk"].quantile(1/3)
    t2 = nonneg["beta_uk"].quantile(2/3)
    df = p.merge(bsub[["gvkey", "beta_uk"]], on="gvkey", how="left")
    df["HIGH_UK"] = (df["beta_uk"] > t2).astype(float)
    df["LOW_UK"] = ((df["beta_uk"] >= 0) & (df["beta_uk"] < t1)).astype(float)
    df = df[(df["HIGH_UK"] == 1) | (df["LOW_UK"] == 1)]
    df = df[df["cal_yr_qtr"].isin([20153, 20154, 20163, 20164])]
    df["POST"] = df["cal_yr_qtr"].isin([20163, 20164]).astype(float)
    df["TREAT_POST"] = df["HIGH_UK"] * df["POST"]
    required = ["CASH_T8"] + [f"{c}_lag1" for c in ctrl_cols]
    df = df.dropna(subset=required)
    df["firm_id"] = df["gvkey"].astype("category").cat.codes
    df["time_id"] = df["cal_yr_qtr"]
    df["sic2"] = df["sic"].fillna(-1).astype(int) // 100
    df["ind_qtr"] = df["sic2"].astype(str) + "_" + df["cal_yr_qtr"].astype(str)
    df_idx = df.set_index(["firm_id", "time_id"])
    y = df_idx["CASH_T8"]
    X_cols = ["TREAT_POST"] + [f"{c}_lag1" for c in ctrl_cols]
    iq_dum = pd.get_dummies(df_idx["ind_qtr"], prefix="iq", drop_first=True).astype(float)
    X = pd.concat([df_idx[X_cols], iq_dum], axis=1)
    m = PanelOLS(y, X, entity_effects=True, drop_absorbed=True)
    res = m.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
    d = res.params["TREAT_POST"]
    pv = res.pvalues["TREAT_POST"]
    sig = "***" if pv < 0.01 else "**" if pv < 0.05 else "*" if pv < 0.10 else ""
    print(f"  {label:<45}  δ={d:+.4f} {sig:<3}  p={pv:.3f}  Nβ={len(bsub)}  Ntr={int((df['HIGH_UK']==1).sum())}  N={int(res.nobs):,}  t1={t1:.3f} t2={t2:.3f}")

did(lambda b: b, "Baseline (all VIX-β)")
did(lambda b: b[b["n_months"] == 60], "VIX-β, n_months=60")
did(lambda b: b[b["r2"] >= 0.20], "VIX-β, r²>=0.20")
did(lambda b: b[b["r2"] >= 0.30], "VIX-β, r²>=0.30")
did(lambda b: b[(b["n_months"] == 60) & (b["r2"] >= 0.20)], "VIX-β, full 60 + r²>=0.20")
did(lambda b: b[(b["n_months"] == 60) & (b["r2"] >= 0.30)], "VIX-β, full 60 + r²>=0.30")
did(lambda b: b[b["beta_uk"].abs() < 2], "VIX-β, |β|<2")

print("\nPaper target: δ ≈ +0.231 ***")
