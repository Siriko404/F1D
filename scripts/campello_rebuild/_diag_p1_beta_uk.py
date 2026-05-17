"""Phase-1 diagnostic (systematic-debugging) — evidence ONLY, no fix.

Anomaly: Step-2 beta^UK has min -7.16 / max 6.64 / sd 0.86, 41% negative.
Question: why so fat-tailed? Prime suspect = shared design-matrix
collinearity (vol(FTSE100) vs vol(SP500)) destabilising every firm's OLS.

Instruments four boundaries:
  A. Shared design matrix X conditioning (corr, condition number, VIF).
  B. beta^UK vs beta_se coupling (collinearity signature).
  C. Near-tercile-cut fragility (does instability reach the treated/control
     boundary, or only the cosmetic tails?).
  D. Closed-form OLS correctness on synthetic data (rule out a code bug).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import step2_beta_uk as s2  # noqa: E402  (import-after-path is intentional)

ROOT = HERE.parents[1]
STEP2_BASE = ROOT / "outputs" / "campello_rebuild" / "step2_beta_uk"
STEP3_BASE = ROOT / "outputs" / "campello_rebuild" / "step3_treatment"


def latest(base: Path, name: str) -> Path:
    return sorted(d for d in base.iterdir() if d.is_dir())[-1] / name


print("=== PHASE-1 DIAGNOSTIC (evidence only) ===\n")

# ---- A. Shared design matrix conditioning -------------------------------
macro = s2.build_macro_vol()
M = macro[["vol_ftse", "vol_sp500", "vol_fx"]].copy()
print("A. DESIGN MATRIX  (60 monthly obs, shared by ALL firms)")
print("   pairwise corr:")
c = M.corr()
for a in M.columns:
    print("     " + "  ".join(f"{a}~{b}={c.loc[a,b]:+.3f}" for b in M.columns if b > a or (a, b) == (a, b) and b != a))
print(f"   corr(vol_ftse,vol_sp500) = {c.loc['vol_ftse','vol_sp500']:+.4f}")
print(f"   corr(vol_ftse,vol_fx)    = {c.loc['vol_ftse','vol_fx']:+.4f}")
print(f"   corr(vol_sp500,vol_fx)   = {c.loc['vol_sp500','vol_fx']:+.4f}")

X = np.column_stack([np.ones(len(M)), M.to_numpy(float)])
Xs = (M - M.mean()) / M.std()
print(f"   cond(X) [w/ intercept]        = {np.linalg.cond(X):,.1f}")
print(f"   cond(standardized regressors) = {np.linalg.cond(Xs.to_numpy()):,.1f}")
# VIF for vol_ftse: regress vol_ftse on [1, vol_sp500, vol_fx]
yv = M["vol_ftse"].to_numpy(float)
Zv = np.column_stack([np.ones(len(M)), M[["vol_sp500", "vol_fx"]].to_numpy(float)])
bb, *_ = np.linalg.lstsq(Zv, yv, rcond=None)
r2 = 1 - ((yv - Zv @ bb) ** 2).sum() / ((yv - yv.mean()) ** 2).sum()
print(f"   vol_ftse ~ vol_sp500+vol_fx : R^2={r2:.4f}  VIF={1/(1-r2):,.1f}")

# ---- B. beta vs se coupling --------------------------------------------
b2 = pq.read_table(latest(STEP2_BASE, "beta_uk.parquet")).to_pandas()
bu, se = b2["beta_uk"], b2["beta_se"]
print("\nB. beta^UK / beta_se")
qs = [.01, .05, .25, .50, .75, .95, .99]
print("   beta_uk pctiles " + " ".join(f"p{int(q*100)}={bu.quantile(q):+.3f}" for q in qs))
buckets = pd.cut(bu.abs(), [0, .5, 1, 2, 3, np.inf],
                 labels=["<0.5", "0.5-1", "1-2", "2-3", ">3"])
print("   |beta| buckets:", buckets.value_counts().reindex(
    ["<0.5", "0.5-1", "1-2", "2-3", ">3"]).to_dict())
print(f"   beta_se  median={se.median():.3f}  p90={se.quantile(.9):.3f}  "
      f"p99={se.quantile(.99):.3f}  max={se.max():.3f}")
print(f"   corr(|beta_uk|, beta_se) = {bu.abs().corr(se):+.3f}")
print(f"   firms with beta_se > 0.5 : {(se>0.5).sum():,} "
      f"({(se>0.5).mean()*100:.1f}%)")

# ---- C. near-cut fragility ---------------------------------------------
nn = bu[bu >= 0]
p33, p67 = nn.quantile(1/3), nn.quantile(2/3)
treated = b2[bu >= p67]
control = b2[(bu >= 0) & (bu <= p33)]
t_frag = (treated["beta_uk"] - p67).abs() < treated["beta_se"]
c_frag = (control["beta_uk"] - p33).abs() < control["beta_se"]
print("\nC. NEAR-CUT FRAGILITY  (is the treated/control SET stable?)")
print(f"   cuts p33={p33:.3f} p67={p67:.3f}")
print(f"   treated n={len(treated)}  within 1 SE of cut: {t_frag.sum()} "
      f"({t_frag.mean()*100:.1f}%)")
print(f"   control n={len(control)}  within 1 SE of cut: {c_frag.sum()} "
      f"({c_frag.mean()*100:.1f}%)")

# ---- D. OLS correctness on synthetic data ------------------------------
rng = np.random.default_rng(0)
true_b = np.array([0.02, 0.50, 0.30, -0.20])
Xsyn = X.copy()
Ysyn = (Xsyn @ true_b)[None, :] + rng.normal(0, 0.002, size=(500, len(Xsyn)))
bhat, _ = s2.ols_beta_uk(Ysyn, Xsyn)
print("\nD. OLS CORRECTNESS (synthetic, true beta_FTSE=0.50)")
print(f"   recovered beta_FTSE  mean={bhat[:,1].mean():+.4f}  "
      f"sd={bhat[:,1].std():.4f}  (expect ~0.50)")
print(f"   recovered intercept  mean={bhat[:,0].mean():+.4f}  (expect ~0.02)")
print("\n=== END PHASE-1 (no fix applied) ===")
