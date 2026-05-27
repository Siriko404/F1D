"""DiD on balanced panel + alternative winsorization strategies."""
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

nonneg = beta[beta["beta_uk"] >= 0]
t1 = nonneg["beta_uk"].quantile(1/3)
t2 = nonneg["beta_uk"].quantile(2/3)
p["HIGH_UK"] = (p["beta_uk"] > t2).astype(float)
p["LOW_UK"] = ((p["beta_uk"] >= 0) & (p["beta_uk"] < t1)).astype(float)

ctrl_cols = ["STOCK_RETURNS", "TOBIN_Q", "CASH_FLOW", "SIZE", "SALES_GROWTH", "CONSENSUS_EPS"]
for c in ctrl_cols:
    p[f"{c}_lag1"] = p.groupby("gvkey")[c].shift(1)

# Build CASH_T8 with winsorization variants
def wins_per_qtr(s, df, lo_q, hi_q):
    nv = pd.Series(np.nan, index=df.index)
    for q, idx in df.groupby("cal_yr_qtr").groups.items():
        v = s.loc[idx]
        if v.notna().sum() >= 10:
            lo, hi = v.quantile(lo_q), v.quantile(hi_q)
            nv.loc[idx] = v.clip(lo, hi)
        else:
            nv.loc[idx] = v
    return nv

def wins_pooled(s, lo_q, hi_q):
    lo, hi = s.quantile(lo_q), s.quantile(hi_q)
    return s.clip(lo, hi)

raw_cash = np.where(
    (p["atq_lag1_q"] - p["cheq_lag1_q"]) > 0,
    p["cheq"] / (p["atq_lag1_q"] - p["cheq_lag1_q"]),
    np.nan,
)
raw_cash = pd.Series(raw_cash, index=p.index).replace([np.inf, -np.inf], np.nan)

PRE_Q = [20153, 20154]
POST_Q = [20163, 20164]

def did(p, cash_col, label, sample="full", balanced=False):
    from linearmodels import PanelOLS
    df = p.copy()
    df["CASH_T8"] = cash_col

    matched_gv = set(matches["treated_gvkey"]) | set(matches["control_gvkey"])
    if sample == "matched":
        df = df[df["gvkey"].isin(matched_gv)]

    df = df[(df["HIGH_UK"] == 1) | (df["LOW_UK"] == 1)]
    df = df[df["cal_yr_qtr"].isin(PRE_Q + POST_Q)]
    df["POST"] = df["cal_yr_qtr"].isin(POST_Q).astype(float)
    df["TREAT_POST"] = df["HIGH_UK"] * df["POST"]
    required = ["CASH_T8"] + [f"{c}_lag1" for c in ctrl_cols]
    df = df.dropna(subset=required)

    if balanced:
        # Keep firms present in all 4 quarters
        counts = df.groupby("gvkey")["cal_yr_qtr"].nunique()
        bal = counts[counts == 4].index
        df = df[df["gvkey"].isin(bal)]

    if len(df) < 50:
        print(f"  {label:<60}  SKIP")
        return
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
    print(f"  {label:<60}  δ={d:+.4f} {sig:<3}  p={pv:.3f}  N={int(res.nobs):,}")

# Test winsorization variants × sample × balanced
print("=" * 100)
print("CASH DiD: winsorization variants × sample × balanced/unbalanced")
print("=" * 100)

cash_99 = wins_per_qtr(raw_cash, p, 0.01, 0.99)
cash_95 = wins_per_qtr(raw_cash, p, 0.025, 0.975)
cash_5 = wins_per_qtr(raw_cash, p, 0.05, 0.95)
cash_pooled = wins_pooled(raw_cash, 0.01, 0.99)
cash_none = raw_cash.where(raw_cash < 5, np.nan).where(raw_cash > 0, np.nan)  # drop extreme but no clip

for cl, ccol in [("wins 1/99 per-qtr (curr)", cash_99),
                  ("wins 2.5/97.5 per-qtr", cash_95),
                  ("wins 5/95 per-qtr", cash_5),
                  ("wins 1/99 pooled", cash_pooled),
                  ("clip raw to [0, 5]", cash_none)]:
    for sample in ["full", "matched"]:
        for bal in [False, True]:
            label = f"{cl} | {sample} | bal={bal}"
            did(p, ccol, label, sample=sample, balanced=bal)

print("\nPaper Table 8 CASH: δ ≈ +0.231 ***")
