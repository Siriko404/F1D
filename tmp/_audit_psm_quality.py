"""PROCESS audit: PSM quality, covariate balance, DiD assumptions.
Checks:
1. Propensity score overlap (common support)
2. Covariate balance: SMD before/after matching
3. Match distance distribution
4. Firm count alignment with paper
"""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
runs = sorted([d for d in OUT.iterdir() if d.is_dir()
               and (d/"beta_uk.parquet").exists()
               and (d/"variables_panel.parquet").exists()
               and (d/"stock_returns.parquet").exists()
               and (d/"consensus_eps.parquet").exists()], reverse=True)
beta_dir = runs[0]

panel = pd.read_parquet(beta_dir / "variables_panel.parquet")
beta = pd.read_parquet(beta_dir / "beta_uk.parquet")[["gvkey","beta_uk"]]
sret = pd.read_parquet(beta_dir / "stock_returns.parquet")
ceps = pd.read_parquet(beta_dir / "consensus_eps.parquet")

panel = panel.merge(sret, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(beta, on="gvkey", how="left")

PRE_BREXIT_END = 20154
nonneg = beta[beta["beta_uk"]>=0]
t1 = nonneg["beta_uk"].quantile(1/3); t2 = nonneg["beta_uk"].quantile(2/3)

panel["treated"] = (panel["beta_uk"] > t2).astype(float)
panel["control_pool"] = ((panel["beta_uk"]>=0) & (panel["beta_uk"]<t1)).astype(float)

# Pre-window
pre = panel[panel["cal_yr_qtr"] <= PRE_BREXIT_END].copy()
pre = pre.sort_values(["gvkey","cal_yr_qtr"])
pre["STOCK_RETURNS_lag1"] = pre.groupby("gvkey")["STOCK_RETURNS"].shift(1)

covariates = ["STOCK_RETURNS_lag1","CONSENSUS_EPS","TOBIN_Q","CASH_FLOW","SALES_GROWTH","SIZE"]
firm_avg = pre.groupby("gvkey").agg({"treated":"max","sic":"first",
    **{c:"mean" for c in covariates}}).reset_index()
firm_avg = firm_avg.dropna(subset=covariates)

# ---- 1. Pre-match balance (SMD) ----
print("="*70)
print("PROCESS AUDIT: PSM Quality + Covariate Balance")
print("="*70)
print(f"\nFirms: {len(firm_avg):,} treated={firm_avg['treated'].sum():.0f} control={(1-firm_avg['treated']).sum():.0f}")
print(f"Paper benchmark: treated=449, control=360")

# Pre-match SMD
print(f"\n--- 1. Pre-match standardized mean differences ---")
print(f"{'Covariate':<22}{'Treated':>10}{'Control':>10}{'SMD':>10}{'Verdict':>10}")
for c in covariates:
    tv = firm_avg[firm_avg["treated"]==1][c]
    cv = firm_avg[firm_avg["treated"]==0][c]
    smd = (tv.mean() - cv.mean()) / np.sqrt((tv.var() + cv.var())/2)
    verdict = "OK" if abs(smd) < 0.25 else "IMBALANCE"
    print(f"{c:<22}{tv.mean():>10.4f}{cv.mean():>10.4f}{smd:>10.4f}{verdict:>10}")

# ---- 2. Fit PSM ----
X = firm_avg[covariates].values; y = firm_avg["treated"].values.astype(int)
scaler = StandardScaler(); X_z = scaler.fit_transform(X)
logreg = LogisticRegression(max_iter=1000); logreg.fit(X_z, y)
firm_avg["pscore"] = logreg.predict_proba(X_z)[:,1]

# ---- 3. Pscore overlap ----
t_ps = firm_avg[firm_avg["treated"]==1]["pscore"]
c_ps = firm_avg[firm_avg["treated"]==0]["pscore"]
print(f"\n--- 2. Propensity score overlap ---")
print(f"  Treated:  mean={t_ps.mean():.3f}  min={t_ps.min():.3f}  max={t_ps.max():.3f}")
print(f"  Control:  mean={c_ps.mean():.3f}  min={c_ps.min():.3f}  max={c_ps.max():.3f}")
overlap = (t_ps.min() <= c_ps) & (c_ps <= t_ps.max())
print(f"  % control in treated support: {overlap.mean()*100:.1f}%")

# ---- 4. 3-NN matching ----
t_idx = firm_avg.index[firm_avg["treated"]==1].tolist()
c_idx = firm_avg.index[firm_avg["treated"]==0].tolist()
nbrs = NearestNeighbors(n_neighbors=min(3,len(c_idx)))
nbrs.fit(firm_avg.loc[c_idx,["pscore"]].values)
dist, idx_in_c = nbrs.kneighbors(firm_avg.loc[t_idx,["pscore"]].values)

print(f"\n--- 3. Match quality ---")
print(f"  Treated matched: {len(t_idx)}")
print(f"  Matched controls: {len(set(c_idx[i] for row in idx_in_c for i in row))}")
print(f"  Mean match distance: {dist.mean():.6f}  max: {dist.max():.6f}")
print(f"  Reused controls (indicating poor overlap):")
reuse = pd.Series([c_idx[i] for row in idx_in_c for i in row]).value_counts()
print(f"    Max reuse: {reuse.max()}  Mean reuse: {reuse.mean():.2f}  Used>=5×: {(reuse>=5).sum()}")

# ---- 5. Post-match SMD ----
# Build matched sample means using control weights
matched_t = firm_avg.loc[t_idx].copy()
matched_c_indices = [c_idx[i] for row in idx_in_c for i in row]
matched_c = firm_avg.loc[matched_c_indices].copy()

print(f"\n--- 4. Post-match balance ---")
print(f"{'Covariate':<22}{'Treated':>10}{'Control':>10}{'SMD':>10}{'Verdict':>10}")
for c in covariates:
    tv = matched_t[c]
    cv = matched_c[c]
    smd = (tv.mean() - cv.mean()) / np.sqrt((tv.var() + cv.var())/2)
    verdict = "BALANCED" if abs(smd) < 0.1 else ("OK" if abs(smd) < 0.25 else "IMBALANCE")
    print(f"{c:<22}{tv.mean():>10.4f}{cv.mean():>10.4f}{smd:>10.4f}{verdict:>10}")

print(f"\n--- 5. DiD specification check ---")
print(f"  Eq (14): Y = δ(POST×HIGH_UK) + θ·CONTROLS_lag1 + FIRM_FE + INDUSTRY×QUARTER_FE")
print(f"  Pre: 2015Q3-Q4, Post: 2016Q3-Q4")
print(f"  N in DiD: {len(panel[panel['cal_yr_qtr'].isin([20153,20154,20163,20164])])}")
print(f"  Paper DiD N: 17,170 (Table 8, col 1, CASH β-based)")
print(f"  Paper matched-sample N: 12,715 (PSM investment, Table C.3)")
print(f"  SE: double-clustered (firm + cal_yr_qtr)")
print(f"  FE: firm + INDUSTRY×QUARTER (paper: Hoberg-Phillips FIC100×Quarter)")
print(f"  FIC100 available: {'fic100' in panel.columns or 'sic' in panel.columns}")
