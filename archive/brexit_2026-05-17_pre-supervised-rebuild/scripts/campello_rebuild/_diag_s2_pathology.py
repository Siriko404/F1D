"""DIAG (read-only): pin the SPECIFIC betaUK pathology before any step2 fix.

Advisor discriminator — fat tails vs 41%-negative are different pathologies:
  * fat tails  -> outlier/functional-form (log/winsor could help)
  * 41% neg    -> LOW PRECISION (60 obs, collinear) -> ~50% wrong-sign by
                  noise; log-transform CANNOT fix this.

Decision rule on the 802 negative-betaUK firms:
  >=80% with |t|<1  -> NOISE  -> precision lever (weekly freq / drop SP500)
  many with |t|>1.65 -> robust sign-flip -> functional form / logs on table
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
from step2_beta_uk import build_macro_vol  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
S2 = (ROOT / "outputs" / "campello_rebuild" / "step2_beta_uk"
      / "2026-05-15_171458" / "beta_uk.parquet")

d = pq.read_table(S2).to_pandas()
b = d["beta_uk"].astype(float)
se = d["beta_se"].astype(float)
t = b / se
neg = b < 0
pos = b >= 0

print(f"\n=== betaUK PATHOLOGY DIAG  (n={len(d)}) ===")
print(f"median betaUK(all)={b.median():.4f}  median SE(all)={se.median():.4f}"
      f"  max={b.max():.3f}  min={b.min():.3f}")


def block(mask, label):
    tt = t[mask].abs()
    bb = b[mask]
    n = int(mask.sum())
    print(f"\n[{label}]  n={n} ({n/len(d)*100:.1f}%)")
    if n:
        print(f"  median betaUK = {bb.median():.4f}")
        print(f"  median |t|    = {tt.median():.3f}")
        print(f"  %|t|<1    (noise)      = {(tt < 1).mean()*100:.1f}%")
        print(f"  %|t|>1.65 (10% sig)    = {(tt > 1.65).mean()*100:.1f}%")
        print(f"  %|t|>1.96 (5% sig)     = {(tt > 1.96).mean()*100:.1f}%")


block(neg, "NEGATIVE betaUK")
block(pos, "NONNEG betaUK")

# macro design collinearity (rebuild the 60-month X exactly as step2 does)
print("\n=== macro vol design (60 months) ===")
m = build_macro_vol()
X = m[["vol_ftse", "vol_sp500", "vol_fx"]].astype(float)
print("corr:")
print(X.corr().round(3).to_string())


def vif(df, c):
    y = df[c].to_numpy()
    Z = np.column_stack([np.ones(len(df)), df.drop(columns=[c]).to_numpy()])
    coef, *_ = np.linalg.lstsq(Z, y, rcond=None)
    rss = ((y - Z @ coef) ** 2).sum()
    tss = ((y - y.mean()) ** 2).sum()
    r2 = 1 - rss / tss
    return float("inf") if r2 >= 1 else 1.0 / (1.0 - r2)


for c in X.columns:
    print(f"  VIF[{c}] = {vif(X, c):.2f}")
Xs = (X - X.mean()) / X.std()
print(f"  cond(standardized X) = {np.linalg.cond(Xs.to_numpy()):.2f}")

print("\n--- VERDICT INPUT: read %|t|<1 among NEGATIVE betaUK ---")
print("  >=80% |t|<1  => precision pathology (weekly-freq / drop SP500)")
print("  else robust  => functional-form (log) candidate")
