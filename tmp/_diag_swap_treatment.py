"""Critical test: SWAP treated↔control. If δ flips to positive, β^UK is inverted.

Also: characterize β^UK distribution + firm types to compare to paper.
"""
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname

panel = pd.read_parquet(latest("variables_panel.parquet"))
beta = pd.read_parquet(latest("beta_uk.parquet"))
sret = pd.read_parquet(latest("stock_returns.parquet"))
ceps = pd.read_parquet(latest("consensus_eps.parquet"))

comp = pd.read_parquet(ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet",
                      columns=["gvkey", "datadate", "atq", "cheq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
comp["atq"] = pd.to_numeric(comp["atq"], errors="coerce")
comp["cheq"] = pd.to_numeric(comp["cheq"], errors="coerce")
comp = comp.drop_duplicates(subset=["gvkey", "datadate"], keep="last")

print("=" * 80)
print("β^UK distribution full")
print("=" * 80)
b = beta["beta_uk"]
print(f"  N={len(b):,}  mean={b.mean():.3f}  sd={b.std():.3f}")
print(f"  min={b.min():.3f}  p10={b.quantile(.10):.3f}  p25={b.quantile(.25):.3f}")
print(f"  p50={b.median():.3f}  p75={b.quantile(.75):.3f}  p90={b.quantile(.90):.3f}  max={b.max():.3f}")
print(f"  β<0: {(b<0).sum():,} ({(b<0).mean()*100:.1f}%)")
print(f"  β>=0: {(b>=0).sum():,} ({(b>=0).mean()*100:.1f}%)")
print()
print(f"r2 distribution (regression fit quality):")
print(f"  mean={beta['r2'].mean():.3f}  median={beta['r2'].median():.3f}")
print(f"  p10={beta['r2'].quantile(.10):.3f}  p90={beta['r2'].quantile(.90):.3f}")
print(f"  r2<0.10: {(beta['r2']<0.10).sum():,}  r2>0.50: {(beta['r2']>0.50).sum():,}")
print()
print("Paper benchmark (lockin PARA_07):")
print(f"  treated tercile boundary β > 0.68 — paper")
print(f"  control tercile boundary β < 0.28 — paper")

# Compare cutoffs
nonneg = beta[beta["beta_uk"] >= 0]
t1 = nonneg["beta_uk"].quantile(1/3)
t2 = nonneg["beta_uk"].quantile(2/3)
print(f"  My nonneg-β terciles: t1={t1:.3f}, t2={t2:.3f}")

# Build CASH_T8 + lagged controls
p = panel.merge(sret, on=["gvkey", "cal_yr_qtr"], how="left")
p = p.merge(ceps, on=["gvkey", "cal_yr_qtr"], how="left")
p = p.merge(comp[["gvkey", "datadate", "cheq"]], on=["gvkey", "datadate"], how="left",
            suffixes=("_p", ""))
p = p.merge(beta[["gvkey", "beta_uk"]], on="gvkey", how="left")
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

PRE_Q = [20153, 20154]
POST_Q = [20163, 20164]

def run_did(p, high_mask, low_mask, label):
    from linearmodels import PanelOLS
    df = p.copy()
    df["HIGH_UK"] = high_mask
    df["LOW_UK"] = low_mask
    df = df[(df["HIGH_UK"] == 1) | (df["LOW_UK"] == 1)]
    df = df[df["cal_yr_qtr"].isin(PRE_Q + POST_Q)]
    df["POST"] = df["cal_yr_qtr"].isin(POST_Q).astype(float)
    df["TREAT_POST"] = df["HIGH_UK"] * df["POST"]
    required = ["CASH_T8"] + [f"{c}_lag1" for c in ctrl_cols]
    df = df.dropna(subset=required)
    if len(df) < 50:
        print(f"{label}: too few obs ({len(df)})")
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
    se = res.std_errors["TREAT_POST"]
    pv = res.pvalues["TREAT_POST"]
    n_t = (df["HIGH_UK"] == 1).sum()
    n_c = (df["LOW_UK"] == 1).sum()
    print(f"  {label}:  δ={d:+.4f}  SE={se:.4f}  p={pv:.3f}  N={int(res.nobs):,}  "
          f"(N_treat={n_t}, N_ctrl={n_c})")

print()
print("=" * 80)
print("Swap test: CASH_T8 DiD, full sample (no PSM), Std window")
print("=" * 80)

# Original: HIGH=top tercile, LOW=bottom tercile
h_orig = (p["beta_uk"] > t2).astype(float)
l_orig = ((p["beta_uk"] >= 0) & (p["beta_uk"] < t1)).astype(float)
run_did(p, h_orig, l_orig, "Original (HIGH = top β tercile)")

# Swap: HIGH=bottom tercile, LOW=top tercile
run_did(p, l_orig, h_orig, "SWAPPED (HIGH = bottom β tercile)")

# Alternative 1: HIGH=NEGATIVE β (firms benefiting from UK uncertainty)
h_neg = (p["beta_uk"] < 0).astype(float)
l_pos = ((p["beta_uk"] >= 0) & (p["beta_uk"] < t1)).astype(float)
run_did(p, h_neg, l_pos, "ALT1: HIGH = neg β (excluded by paper)")

# Alternative 2: HIGH=top β tercile (regardless of sign)
all_t1 = beta["beta_uk"].quantile(1/3)
all_t2 = beta["beta_uk"].quantile(2/3)
h_top = (p["beta_uk"] > all_t2).astype(float)
l_bot = (p["beta_uk"] < all_t1).astype(float)
run_did(p, h_top, l_bot, "ALT2: terciles of ALL β (not just nonneg)")

# Alternative 3: median split nonneg
med = nonneg["beta_uk"].median()
h_med = ((p["beta_uk"] >= 0) & (p["beta_uk"] > med)).astype(float)
l_med = ((p["beta_uk"] >= 0) & (p["beta_uk"] <= med)).astype(float)
run_did(p, h_med, l_med, "ALT3: median split (nonneg only)")

print()
print("=" * 80)
print("Per-firm β^UK characterization — top 20 / bottom 20")
print("=" * 80)
# Sort firms by β^UK and report sic distribution
beta_sic = beta.merge(panel[["gvkey", "sic"]].drop_duplicates("gvkey"), on="gvkey")
beta_sic["sic2"] = beta_sic["sic"].fillna(-1).astype(int) // 100

print("\nTop 20 β^UK firms — gvkey | β^UK | r2 | sic2 | n_months:")
top = beta_sic.nlargest(20, "beta_uk")
for _, r in top.iterrows():
    print(f"  {r['gvkey']}  β={r['beta_uk']:+.3f}  r2={r['r2']:.2f}  sic2={int(r['sic2'])}  n_m={r['n_months']}")

print("\nBottom 20 β^UK firms:")
bot = beta_sic.nsmallest(20, "beta_uk")
for _, r in bot.iterrows():
    print(f"  {r['gvkey']}  β={r['beta_uk']:+.3f}  r2={r['r2']:.2f}  sic2={int(r['sic2'])}  n_m={r['n_months']}")

print("\nTreated (β > t2={:.3f}) SIC2 distribution top 10:".format(t2))
print(beta_sic[beta_sic["beta_uk"] > t2]["sic2"].value_counts().head(10).to_string())

print("\nControl (0 <= β < t1={:.3f}) SIC2 distribution top 10:".format(t1))
print(beta_sic[(beta_sic["beta_uk"] >= 0) & (beta_sic["beta_uk"] < t1)]["sic2"].value_counts().head(10).to_string())
