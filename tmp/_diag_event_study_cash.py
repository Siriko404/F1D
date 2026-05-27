"""Event-study diagnostic: CASH_T8 means by treated/control across all 28 quarters.

Goal: distinguish sign-mismatch root cause:
  - If treated firms have CHRONICALLY-declining cash → composition error (β^UK picks wrong firms)
  - If treated firms parallel-trend pre-Brexit then drop post → behavioral, paper wrong
  - If treated firms parallel pre then RISE post → my code/window error
"""
import os
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname

panel = pd.read_parquet(latest("variables_panel.parquet"))
beta = pd.read_parquet(latest("beta_uk.parquet"))[["gvkey", "beta_uk"]]
matches = pd.read_parquet(latest("psm_matches.parquet"))

# Build CASH_T8
comp = pd.read_parquet(ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet",
                      columns=["gvkey", "datadate", "atq", "cheq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
comp["atq"] = pd.to_numeric(comp["atq"], errors="coerce")
comp["cheq"] = pd.to_numeric(comp["cheq"], errors="coerce")
comp = comp.drop_duplicates(subset=["gvkey", "datadate"], keep="last")

panel = panel.merge(comp[["gvkey", "datadate", "cheq"]], on=["gvkey", "datadate"],
                   how="left", suffixes=("_p", ""))
panel = panel.merge(beta, on="gvkey", how="left")
panel = panel.sort_values(["gvkey", "cal_yr_qtr"])
panel["atq_lag1_q"] = panel.groupby("gvkey")["atq"].shift(1)
panel["cheq_lag1_q"] = panel.groupby("gvkey")["cheq"].shift(1)

denom = panel["atq_lag1_q"] - panel["cheq_lag1_q"]
panel["CASH_T8"] = np.where(denom.notna() & (denom > 0),
                              panel["cheq"] / denom, np.nan)
panel["CASH_T8"] = panel["CASH_T8"].replace([np.inf, -np.inf], np.nan)

# Tercile assignment
nonneg = beta[beta["beta_uk"] >= 0]
t1 = nonneg["beta_uk"].quantile(1/3)
t2 = nonneg["beta_uk"].quantile(2/3)
print(f"β^UK terciles (nonneg only): t1={t1:.4f}  t2={t2:.4f}")

panel["HIGH_UK"] = (panel["beta_uk"] > t2).astype(float)
panel["LOW_UK"] = ((panel["beta_uk"] >= 0) & (panel["beta_uk"] < t1)).astype(float)

# Restrict to matched sample
matched_gv = set(matches["treated_gvkey"]) | set(matches["control_gvkey"])
m_panel = panel[panel["gvkey"].isin(matched_gv)].copy()
m_panel = m_panel[(m_panel["HIGH_UK"] == 1) | (m_panel["LOW_UK"] == 1)]

# Winsorize CASH_T8 per quarter
def wins(g):
    v = g["CASH_T8"]
    if v.notna().sum() < 10:
        return v
    lo, hi = v.quantile(0.01), v.quantile(0.99)
    return v.clip(lo, hi)
m_panel["CASH_T8_w"] = m_panel.groupby("cal_yr_qtr").apply(
    lambda g: wins(g), include_groups=False).reset_index(level=0, drop=True)

# Means by quarter and treatment group
print("\n--- CASH_T8 by quarter × group (matched sample) ---")
print(f"{'Quarter':<10}{'N_t':>6}{'N_c':>6}{'Mean_T':>10}{'Mean_C':>10}{'Diff(T-C)':>12}")
print("-" * 60)
for q in sorted(m_panel["cal_yr_qtr"].unique()):
    qd = m_panel[m_panel["cal_yr_qtr"] == q]
    t = qd[qd["HIGH_UK"] == 1]["CASH_T8_w"]
    c = qd[qd["HIGH_UK"] == 0]["CASH_T8_w"]
    if t.notna().sum() < 5 or c.notna().sum() < 5:
        continue
    print(f"{q:<10}{t.notna().sum():>6}{c.notna().sum():>6}"
          f"{t.mean():>10.3f}{c.mean():>10.3f}{t.mean()-c.mean():>12.3f}")

# Identify treated firms — top SIC industries, sample of names
print("\n--- Treated firm top SIC2 industries ---")
treated_firms = m_panel[m_panel["HIGH_UK"] == 1].groupby("gvkey").first()
treated_firms["sic2"] = (treated_firms["sic"].fillna(-1).astype(int) // 100)
print(treated_firms["sic2"].value_counts().head(10))

print("\n--- Control firm top SIC2 industries ---")
control_firms = m_panel[m_panel["LOW_UK"] == 1].groupby("gvkey").first()
control_firms["sic2"] = (control_firms["sic"].fillna(-1).astype(int) // 100)
print(control_firms["sic2"].value_counts().head(10))

print(f"\nTreated firms: {len(treated_firms)} | Control firms: {len(control_firms)}")
