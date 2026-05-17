"""Step-4 diagnostic (systematic-debugging Phase 1) — evidence ONLY, no fix.

Anomaly: Step-4 panel has 348 treated / 374 control firms vs Step-3's
391 / 391. Hypothesis-to-rule-out: the gvkey join (step1.astype(str) vs
step3.astype(str)) silently drops zero-padded-vs-int key mismatches, so the
60 'missing' firms are a JOIN BUG, not real 2015-16 attrition.

Decisive test: rebuild the panel-firm count two ways and compare.
  A. astype(str)            (exactly what step4_timeline.py does)
  B. astype(str).zfill(6)   (the normalization the earlier diagnostics used)
If B recovers ~391/391 -> step4's join is buggy. If A==B -> the 60 are
genuine attrition (firm absent from ALL four window quarters in Step-1).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
S1 = ROOT / "outputs" / "campello_rebuild" / "step1_sample"
S3 = ROOT / "outputs" / "campello_rebuild" / "step3_treatment"
WINDOW = {20153, 20154, 20163, 20164}


def latest(b: Path, f: str) -> Path:
    return sorted(d for d in b.iterdir() if d.is_dir())[-1] / f


s1p, s3p = latest(S1, "sample.parquet"), latest(S3, "treatment.parquet")
samp = pq.read_table(s1p, columns=["gvkey", "cal_yr_qtr"]).to_pandas()
trt = pq.read_table(s3p, columns=["gvkey", "HIGH_BETA_UK"]).to_pandas()

print("RAW dtypes")
print(f"  step1 gvkey : {samp['gvkey'].dtype}  e.g. {samp['gvkey'].iloc[:3].tolist()}")
print(f"  step3 gvkey : {trt['gvkey'].dtype}  e.g. {trt['gvkey'].iloc[:3].tolist()}")
samp["cal_yr_qtr"] = samp["cal_yr_qtr"].astype(int)
win = samp[samp["cal_yr_qtr"].isin(WINDOW)]
tb = trt[trt["HIGH_BETA_UK"].isin([0.0, 1.0])].copy()


def firms_in_panel(norm) -> tuple[int, int]:
    w = win.assign(g=norm(win["gvkey"]))
    t = tb.assign(g=norm(tb["gvkey"]))
    p = w.merge(t[["g", "HIGH_BETA_UK"]], on="g", how="inner")
    return (p.loc[p["HIGH_BETA_UK"] == 1, "g"].nunique(),
            p.loc[p["HIGH_BETA_UK"] == 0, "g"].nunique())


A = firms_in_panel(lambda s: s.astype(str))
B = firms_in_panel(lambda s: s.astype(str).str.zfill(6))
print(f"\nA astype(str)        treated={A[0]}  control={A[1]}")
print(f"B astype(str).zfill6 treated={B[0]}  control={B[1]}")

# direct attrition check under the strict (zfill) normalization
g1 = set(win["gvkey"].astype(str).str.zfill(6))
miss = tb.assign(g=tb["gvkey"].astype(str).str.zfill(6))
miss = miss[~miss["g"].isin(g1)]
print(f"\nStep-3 treated/control firms with ZERO rows in any of the 4 "
      f"window quarters (zfill-normalized): {len(miss)}")
print(f"  of which treated={int((miss['HIGH_BETA_UK']==1).sum())}  "
      f"control={int((miss['HIGH_BETA_UK']==0).sum())}")
print(f"  sample missing gvkeys: {miss['g'].head(8).tolist()}")

if A == B:
    print("\nVERDICT: join is dtype-robust (A==B). The 60 are GENUINE "
          "2015-16 attrition (firm absent from all 4 window qtrs in Step-1).")
else:
    print("\nVERDICT: A != B -> step4_timeline.py gvkey join is BUGGY "
          "(zero-pad mismatch). step4 needs .str.zfill(6) on both keys.")
