"""DIAG (read-only): pin the Campello §IV.C.1 treatment-tercile method.

Step-3 deviation confirmed (verbatim L1841-42 / L1850-54 / L2728): paper
groups are UNEQUAL (449 treated / 360 control, betaUK>0.68 / <0.28) — impossible
under our equal-COUNT quantile terciles of the nonnegative pool (~equal groups).

Decide the correct method by computing all three on the actual Step-2 betaUK
and reading the signature (treated vs control asymmetry; cut values):

  B  current code : quantile(1/3,2/3) of NONNEG pool          -> ~equal
  A  equal-WIDTH  : [0,max] split in 3 equal-width bands       -> ?
  C  full-dist    : quantile(1/3,2/3) of FULL betaUK dist,
                    control = bottom tercile AND betaUK>=0      -> treated>control?

Paper signature to match: treated COUNT > control COUNT; the betaUK<0
exclusion caveat is non-redundant (only C makes it non-redundant). NO fix
here — decision input only.
"""
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
S2 = ROOT / "outputs" / "campello_rebuild" / "step2_beta_uk" \
    / "2026-05-15_171458" / "beta_uk.parquet"

df = pq.read_table(S2).to_pandas()
b = pd.to_numeric(df["beta_uk"], errors="coerce").dropna()
n = len(b)
neg = int((b < 0).sum())
nonneg = b[b >= 0]
mx = float(nonneg.max())
print(f"step2: {S2}")
print(f"  firms betaUK     : {n:,}")
print(f"  betaUK < 0 (neg) : {neg:,}   nonneg: {len(nonneg):,}   "
      f"max nonneg: {mx:.4f}\n")


def report(tag, treated_mask, control_mask, c_lo, c_hi):
    t = int(treated_mask.sum())
    c = int(control_mask.sum())
    rel = "treated > control" if t > c else (
        "treated < control" if t < c else "treated == control")
    print(f"[{tag}]  cut_lo={c_lo:.4f}  cut_hi={c_hi:.4f}")
    print(f"        treated={t:,}  control={c:,}  -> {rel}  "
          f"(ratio t/c={t / c:.3f})" if c else f"        treated={t:,} control=0")
    print()


# B — current code: quantile terciles of the NONNEG pool
p33 = float(nonneg.quantile(1 / 3))
p67 = float(nonneg.quantile(2 / 3))
report("B current (quantile of NONNEG pool)",
       (b >= 0) & (b >= p67), (b >= 0) & (b <= p33), p33, p67)

# A — equal-WIDTH terciles of the value range [0, max]
c1 = mx / 3.0
c2 = 2.0 * mx / 3.0
report("A equal-WIDTH [0,max] bands",
       (b >= c2), (b >= 0) & (b <= c1), c1, c2)

# C — quantile terciles of the FULL distribution; control also requires betaUK>=0
P33 = float(b.quantile(1 / 3))
P67 = float(b.quantile(2 / 3))
report("C quantile of FULL dist, neg excluded from control",
       (b >= P67), (b >= 0) & (b <= P33), P33, P67)

print("paper signature: treated COUNT > control COUNT (449 vs 360); "
      "cuts ~0.68 / ~0.28; betaUK<0 caveat non-redundant.")
