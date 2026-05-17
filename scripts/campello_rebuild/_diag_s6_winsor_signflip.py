"""DIAG (read-only): why does 1% winsorization flip the cash-DiD sign?

systematic-debugging Phase 1 — locate the firm-quarters that drive the
pre-winsor +0.148 vs post-winsor -0.03 swing. NO fix here.

Compares PRE-winsor step6 (2026-05-16_180746, raw CASH_DV max~151.6) vs
POST-winsor pooled (2026-05-16_200920). Shows the raw 2x2 DiD on
CASH_DV (indicative, NOT the FE estimate) by HIGH x POST, mean vs
median, and characterises the pre-winsor top-1% extreme tail
(treated/post concentration + industry) to tell denominator-pathology
from a genuine treated-post effect.
"""
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
S6 = ROOT / "outputs" / "campello_rebuild" / "step6_controls"
PRE = S6 / "2026-05-16_180746" / "controls.parquet"
POST = S6 / "2026-05-16_200920" / "controls.parquet"

COLS = ["gvkey", "cal_yr_qtr", "HIGH_BETA_UK", "POST", "CASH_DV", "fic100"]


def load(p):
    d = pq.read_table(p, columns=COLS).to_pandas()
    return d[d["HIGH_BETA_UK"].isin([0, 1]) & d["POST"].isin([0, 1])
            & d["CASH_DV"].notna()].copy()


def cell_table(d, tag):
    g = d.groupby(["HIGH_BETA_UK", "POST"])["CASH_DV"].agg(
        ["mean", "median", "count"])
    print(f"\n=== {tag}  CASH_DV by HIGH x POST ===")
    print(g.to_string())
    m = g["mean"].unstack()  # rows HIGH(0,1), cols POST(0,1)
    md = g["median"].unstack()
    did_mean = (m.loc[1, 1] - m.loc[1, 0]) - (m.loc[0, 1] - m.loc[0, 0])
    did_med = (md.loc[1, 1] - md.loc[1, 0]) - (md.loc[0, 1] - md.loc[0, 0])
    print(f"  raw 2x2 DiD (MEAN, indicative not FE):   {did_mean:+.4f}")
    print(f"  raw 2x2 DiD (MEDIAN, outlier-robust):    {did_med:+.4f}")


pre, post = load(PRE), load(POST)
print(f"PRE  rows={len(pre):,}  POST rows={len(post):,}")
cell_table(pre, "PRE-winsor (raw, max~151.6)")
cell_table(post, "POST-winsor pooled (cap~8.95)")

# pre-winsor extreme tail (top 1%) — who are they?
thr = pre["CASH_DV"].quantile(0.99)
ext = pre[pre["CASH_DV"] >= thr]
base_hp = ((pre["HIGH_BETA_UK"] == 1) & (pre["POST"] == 1)).mean()
ext_hp = ((ext["HIGH_BETA_UK"] == 1) & (ext["POST"] == 1)).mean()
print(f"\n=== PRE-winsor TOP 1% CASH_DV tail  (thr={thr:.3f}) ===")
print(f"  n_extreme            {len(ext):,}")
print(f"  CASH_DV  min/med/max  {ext['CASH_DV'].min():.2f} / "
      f"{ext['CASH_DV'].median():.2f} / {ext['CASH_DV'].max():.2f}")
print(f"  share HIGH==1        {(ext['HIGH_BETA_UK']==1).mean():.1%}  "
      f"(full sample {(pre['HIGH_BETA_UK']==1).mean():.1%})")
print(f"  share POST==1        {(ext['POST']==1).mean():.1%}  "
      f"(full sample {(pre['POST']==1).mean():.1%})")
print(f"  share HIGH&POST      {ext_hp:.1%}  (full sample {base_hp:.1%})  "
      f"-> concentration x{(ext_hp/base_hp if base_hp else float('nan')):.1f}")
print("  top fic100 in tail:")
print(ext["fic100"].value_counts().head(5).to_string())
