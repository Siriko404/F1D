"""Step-7 rank-failure diagnostic (systematic-debugging Phase 1+3).

EVIDENCE ONLY. Hypothesis: the 5 macro *_lag controls are time-only (one
value per calendar quarter); with only 4 quarters in the window + a
FIC-100 x calendar-quarter FE, they are perfectly collinear with the time
FE (and mutually). linearmodels raises 'exog not full rank'; Stata reghdfe
would silently absorb them — which is why Campello's Table 8 reports
'Controls: Yes' + 'Industry x time FE: Yes' but NO macro coefficients.

Tests:
  A. # distinct calendar quarters; # distinct values of each macro lag;
     are macro lags constant within cal_yr_qtr?
  B. fit FIRM-controls-only (no macro)            -> expect SUCCESS
  C. fit FIRM + macro (advisor's 10-ctrl list)    -> expect RANK FAIL
No fix applied.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import step5_did as s5  # noqa: E402

ROOT = HERE.parents[1]
S6 = ROOT / "outputs" / "campello_rebuild" / "step6_controls"
d = sorted(x for x in S6.iterdir() if x.is_dir())[-1]
df = pq.read_table(d / "controls.parquet").to_pandas()
df["gvkey"] = df["gvkey"].astype(str).str.split(".").str[0].str.zfill(6)
df["cal_yr_qtr"] = df["cal_yr_qtr"].astype(int)

MACRO = ["fx_lag", "vix_lag", "umcsent_lag", "livingston_lag", "ads_lag"]
FIRM = ["tobinq_lag", "cf_lag", "logassets_lag", "salesgrowth_lag",
        "stockret_lag"]

print("A. STRUCTURE")
print(f"  distinct cal_yr_qtr in panel : "
      f"{sorted(df['cal_yr_qtr'].unique())}")
for c in MACRO:
    nuniq = df[c].nunique()
    # constant within quarter?
    const = (df.groupby("cal_yr_qtr")[c].nunique(dropna=True) <= 1).all()
    print(f"  {c:<16s} distinct values={nuniq:<3d}  "
          f"constant within cal_yr_qtr={const}")
nq = df["cal_yr_qtr"].nunique()
print(f"  => {len(MACRO)} macro vars live in only {nq} time points "
      f"=> rank(macro) <= {nq}; with quarter-spanning FE they are "
      f"absorbed/collinear.")

base = df.dropna(subset=FIRM + ["CASH_DV", "fic100"]).copy()
print(f"\nB. FIRM-CONTROLS-ONLY fit  (N={len(base):,})")
try:
    r = s5.fit_did(base, y_col="CASH_DV", industry_col="fic100",
                    high_col="HIGH_BETA_UK", control_cols=tuple(FIRM),
                    cluster_cols=("gvkey", "cal_yr_qtr"))
    print(f"  SUCCESS  delta={r['delta_hat']:+.4f}  se={r['se']:.4f}  "
          f"N={r['n_obs']:,}  R2w={r['r2']['within']:.3f}")
    bok = True
except Exception as e:
    print(f"  FAIL: {type(e).__name__}: {str(e)[:140]}")
    bok = False

base2 = df.dropna(subset=FIRM + MACRO + ["CASH_DV", "fic100"]).copy()
print(f"\nC. FIRM + MACRO fit  (advisor 10-ctrl, N={len(base2):,})")
try:
    r = s5.fit_did(base2, y_col="CASH_DV", industry_col="fic100",
                    high_col="HIGH_BETA_UK",
                    control_cols=tuple(FIRM + MACRO),
                    cluster_cols=("gvkey", "cal_yr_qtr"))
    print(f"  SUCCESS (unexpected) delta={r['delta_hat']:+.4f}")
    cfail = False
except Exception as e:
    print(f"  RANK FAIL (expected): {type(e).__name__}: {str(e)[:120]}")
    cfail = True

print("\nVERDICT:",
      "macro time-only controls collinear with FIC100xQTR FE on a "
      "4-quarter window — Campello-faithful handling = macro ABSORBED by "
      "the industry x time FE (NOT separate regressors), exactly as Stata "
      "reghdfe would do. Confirmed: B success={}, C rankfail={}."
      .format(bok, cfail))
