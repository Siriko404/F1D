"""Sweep DiD specifications to triangulate sign mismatch.

Vary: outcome definition × sample × window.
Goal: find any combo that gives positive δ on CASH, then trace why.
"""
import logging
from pathlib import Path
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.WARNING)

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname

panel = pd.read_parquet(latest("variables_panel.parquet"))
beta = pd.read_parquet(latest("beta_uk.parquet"))[["gvkey", "beta_uk"]]
sret = pd.read_parquet(latest("stock_returns.parquet"))
ceps = pd.read_parquet(latest("consensus_eps.parquet"))
matches = pd.read_parquet(latest("psm_matches.parquet"))

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
p = p.merge(beta, on="gvkey", how="left")
p = p.sort_values(["gvkey", "cal_yr_qtr"])
p["atq_lag1_q"] = p.groupby("gvkey")["atq"].shift(1)
p["cheq_lag1_q"] = p.groupby("gvkey")["cheq"].shift(1)

# Two CASH definitions
p["CASH_T1"] = np.where(p["atq_lag1_q"] > 0, p["cheq"] / p["atq_lag1_q"], np.nan)
denom_t8 = p["atq_lag1_q"] - p["cheq_lag1_q"]
p["CASH_T8"] = np.where(denom_t8.notna() & (denom_t8 > 0), p["cheq"] / denom_t8, np.nan)
for c in ["CASH_T1", "CASH_T8"]:
    p[c] = p[c].replace([np.inf, -np.inf], np.nan)
    # winsorize 1%/99% per quarter
    new_v = pd.Series(np.nan, index=p.index)
    for q, idx in p.groupby("cal_yr_qtr").groups.items():
        v = p.loc[idx, c]
        if v.notna().sum() >= 10:
            lo, hi = v.quantile(0.01), v.quantile(0.99)
            new_v.loc[idx] = v.clip(lo, hi)
        else:
            new_v.loc[idx] = v
    p[c] = new_v

# Tercile assignment
nonneg = beta[beta["beta_uk"] >= 0]
t1 = nonneg["beta_uk"].quantile(1/3)
t2 = nonneg["beta_uk"].quantile(2/3)
p["HIGH_UK"] = (p["beta_uk"] > t2).astype(float)
p["LOW_UK"] = ((p["beta_uk"] >= 0) & (p["beta_uk"] < t1)).astype(float)

# Build lagged controls on full panel
ctrl_cols = ["STOCK_RETURNS", "TOBIN_Q", "CASH_FLOW", "SIZE", "SALES_GROWTH", "CONSENSUS_EPS"]
for c in ctrl_cols:
    p[f"{c}_lag1"] = p.groupby("gvkey")[c].shift(1)

matched_gv = set(matches["treated_gvkey"]) | set(matches["control_gvkey"])

# Window variants
WINDOWS = {
    "Std (15Q3Q4 → 16Q3Q4)": ([20153, 20154], [20163, 20164]),
    "Wide (15 full → 16 full)": ([20151, 20152, 20153, 20154], [20161, 20162, 20163, 20164]),
    "Tight (15Q4 → 16Q3)": ([20154], [20163]),
    "Brexit-adj (16Q1Q2 → 16Q3Q4)": ([20161, 20162], [20163, 20164]),
}

def run_one(outcome, sample, pre_q, post_q):
    """Return (delta, se, t, p_val, n)."""
    from linearmodels import PanelOLS

    df = p.copy()
    df = df[(df["HIGH_UK"] == 1) | (df["LOW_UK"] == 1)]
    df = df[df["cal_yr_qtr"].isin(pre_q + post_q)]
    df["POST"] = df["cal_yr_qtr"].isin(post_q).astype(float)
    df["TREAT_POST"] = df["HIGH_UK"] * df["POST"]

    if sample == "matched":
        df = df[df["gvkey"].isin(matched_gv)]

    required = [outcome] + [f"{c}_lag1" for c in ctrl_cols]
    df = df.dropna(subset=required)
    if len(df) < 50:
        return None

    df["firm_id"] = df["gvkey"].astype("category").cat.codes
    df["time_id"] = df["cal_yr_qtr"]
    df["sic2"] = df["sic"].fillna(-1).astype(int) // 100
    df["ind_qtr"] = df["sic2"].astype(str) + "_" + df["cal_yr_qtr"].astype(str)
    df_idx = df.set_index(["firm_id", "time_id"])
    y = df_idx[outcome]
    X_cols = ["TREAT_POST"] + [f"{c}_lag1" for c in ctrl_cols]
    iq_dum = pd.get_dummies(df_idx["ind_qtr"], prefix="iq", drop_first=True).astype(float)
    X = pd.concat([df_idx[X_cols], iq_dum], axis=1)
    try:
        m = PanelOLS(y, X, entity_effects=True, drop_absorbed=True)
        res = m.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
        return (res.params["TREAT_POST"], res.std_errors["TREAT_POST"],
                res.tstats["TREAT_POST"], res.pvalues["TREAT_POST"], int(res.nobs))
    except Exception as e:
        return f"ERR: {e}"

print(f"{'Outcome':<10}{'Sample':<10}{'Window':<32}{'δ':>10}{'SE':>8}{'t':>8}{'p':>8}{'N':>8}")
print("-" * 92)
for outcome in ["CASH_T1", "CASH_T8"]:
    for sample in ["matched", "full"]:
        for wname, (pre_q, post_q) in WINDOWS.items():
            r = run_one(outcome, sample, pre_q, post_q)
            if r is None:
                continue
            if isinstance(r, str):
                print(f"{outcome:<10}{sample:<10}{wname:<32}{r}")
                continue
            d, se, t, pv, n = r
            sig = "***" if pv < 0.01 else "**" if pv < 0.05 else "*" if pv < 0.10 else ""
            print(f"{outcome:<10}{sample:<10}{wname:<32}{d:>+10.4f}{se:>8.4f}{t:>8.2f}{pv:>8.3f}{n:>8,} {sig}")

print("\nPaper Table 8 CASH: δ ≈ +0.231 ***")
