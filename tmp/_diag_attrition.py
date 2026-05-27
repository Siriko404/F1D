"""Check sample attrition + lagged-total-assets convention."""
import warnings; warnings.filterwarnings("ignore")
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

nonneg = beta[beta["beta_uk"] >= 0]
t1 = nonneg["beta_uk"].quantile(1/3)
t2 = nonneg["beta_uk"].quantile(2/3)

p = panel.merge(beta, on="gvkey", how="left")
p["HIGH_UK"] = (p["beta_uk"] > t2).astype(float)
p["LOW_UK"] = ((p["beta_uk"] >= 0) & (p["beta_uk"] < t1)).astype(float)

# Sample attrition check
matched_gv = set(matches["treated_gvkey"]) | set(matches["control_gvkey"])
m = p[p["gvkey"].isin(matched_gv)]
m = m[(m["HIGH_UK"] == 1) | (m["LOW_UK"] == 1)]

# Counts in 4 key quarters
print("--- Treated/control firm presence by quarter (matched sample) ---")
print(f"{'Quarter':<10}{'N_t':>8}{'N_c':>8}{'%attrition_t':>15}{'%attrition_c':>15}")
print("-" * 56)
N_t_base = m[(m["HIGH_UK"] == 1) & (m["cal_yr_qtr"] == 20153)]["gvkey"].nunique()
N_c_base = m[(m["LOW_UK"] == 1) & (m["cal_yr_qtr"] == 20153)]["gvkey"].nunique()
for q in [20151, 20152, 20153, 20154, 20161, 20162, 20163, 20164]:
    qd = m[m["cal_yr_qtr"] == q]
    n_t = qd[qd["HIGH_UK"] == 1]["gvkey"].nunique()
    n_c = qd[qd["LOW_UK"] == 1]["gvkey"].nunique()
    att_t = (1 - n_t/N_t_base) * 100 if N_t_base else np.nan
    att_c = (1 - n_c/N_c_base) * 100 if N_c_base else np.nan
    print(f"{q:<10}{n_t:>8}{n_c:>8}{att_t:>14.1f}%{att_c:>14.1f}%")

# Firms present in BOTH 2015Q3 AND 2016Q4 (no attrition)
treat_pre = set(m[(m["HIGH_UK"] == 1) & (m["cal_yr_qtr"] == 20153)]["gvkey"])
treat_post = set(m[(m["HIGH_UK"] == 1) & (m["cal_yr_qtr"] == 20164)]["gvkey"])
ctrl_pre = set(m[(m["LOW_UK"] == 1) & (m["cal_yr_qtr"] == 20153)]["gvkey"])
ctrl_post = set(m[(m["LOW_UK"] == 1) & (m["cal_yr_qtr"] == 20164)]["gvkey"])
print(f"\n--- Survivorship ---")
print(f"Treated: 2015Q3 N={len(treat_pre)} → 2016Q4 N={len(treat_post)}  attrited={len(treat_pre - treat_post)}  added={len(treat_post - treat_pre)}")
print(f"Control: 2015Q3 N={len(ctrl_pre)} → 2016Q4 N={len(ctrl_post)}  attrited={len(ctrl_pre - ctrl_post)}  added={len(ctrl_post - ctrl_pre)}")

# Balanced-only DiD test
balanced_treat = treat_pre & treat_post
balanced_ctrl = ctrl_pre & ctrl_post
balanced = balanced_treat | balanced_ctrl
print(f"\nBalanced sample (in all 4 key quarters): treated={len(balanced_treat)}, control={len(balanced_ctrl)}")

# Lagged total assets convention check: t-1 (quarter) vs t-4 (year)
comp = pd.read_parquet(ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet",
                      columns=["gvkey", "datadate", "atq", "cheq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
comp["atq"] = pd.to_numeric(comp["atq"], errors="coerce")
comp["cheq"] = pd.to_numeric(comp["cheq"], errors="coerce")
comp = comp.drop_duplicates(subset=["gvkey", "datadate"], keep="last")
ptst = p.merge(comp[["gvkey", "datadate", "cheq"]], on=["gvkey", "datadate"],
                how="left", suffixes=("_p", ""))
ptst = ptst.sort_values(["gvkey", "cal_yr_qtr"])
ptst["atq_lag1_q"] = ptst.groupby("gvkey")["atq"].shift(1)
ptst["atq_lag4_q"] = ptst.groupby("gvkey")["atq"].shift(4)
ptst["cheq_lag1_q"] = ptst.groupby("gvkey")["cheq"].shift(1)
ptst["cheq_lag4_q"] = ptst.groupby("gvkey")["cheq"].shift(4)

# CASH_T8 with lag1 vs lag4
ptst["CASH_T8_lag1"] = np.where(
    (ptst["atq_lag1_q"] - ptst["cheq_lag1_q"]) > 0,
    ptst["cheq"] / (ptst["atq_lag1_q"] - ptst["cheq_lag1_q"]),
    np.nan,
)
ptst["CASH_T8_lag4"] = np.where(
    (ptst["atq_lag4_q"] - ptst["cheq_lag4_q"]) > 0,
    ptst["cheq"] / (ptst["atq_lag4_q"] - ptst["cheq_lag4_q"]),
    np.nan,
)
print(f"\n--- CASH_T8 with lag1 vs lag4 denominator (anchor: mean ~0.17 per Table C.2) ---")
for label, col in [("lag1 (quarter)", "CASH_T8_lag1"), ("lag4 (year)", "CASH_T8_lag4")]:
    v = ptst[col].replace([np.inf, -np.inf], np.nan).dropna()
    print(f"  {label}: N={len(v):,}  mean={v.mean():.3f}  median={v.median():.3f}  p90={v.quantile(.9):.3f}")
