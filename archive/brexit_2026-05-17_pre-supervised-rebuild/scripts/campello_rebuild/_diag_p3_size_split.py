"""Phase-3 diagnostic (systematic-debugging) — single hypothesis, minimal test.

Hypothesis: micro-cap concentration inflates our beta^UK noise beyond
Campello's (his $10M screen on HIS extract filtered a different population
than ours). Test: stratify beta^UK firms by firm-mean market cap over the
estimation window and compare SE-median + near-cut fragility per size
quartile.

If large firms = tight SE / low fragility while small firms = huge SE /
near-total fragility -> micro-cap noise dominates (paper-faithful fix path:
tighten size screen). If size barely matters -> noise is intrinsic, the
"faithful, no-fix" verdict ships.

Evidence ONLY. No fix. No pipeline change. Reuses Step-1 + Step-2 outputs.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
S1 = ROOT / "outputs" / "campello_rebuild" / "step1_sample"
S2 = ROOT / "outputs" / "campello_rebuild" / "step2_beta_uk"


def latest(base: Path, name: str) -> Path:
    return sorted(d for d in base.iterdir() if d.is_dir())[-1] / name


# --- beta^UK (Step 2) ---
b = pq.read_table(latest(S2, "beta_uk.parquet")).to_pandas()
b["gvkey"] = b["gvkey"].astype(str).str.zfill(6)

# --- firm-mean market cap over the beta^UK window (2010-2014) from Step 1 ---
s1 = pq.read_table(latest(S1, "sample.parquet"),
                   columns=["gvkey", "datadate", "mktcap"]).to_pandas()
s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
s1["datadate"] = pd.to_datetime(s1["datadate"], errors="coerce")
s1 = s1[(s1["datadate"] >= "2010-01-01") & (s1["datadate"] <= "2014-12-31")]
mc = s1.groupby("gvkey")["mktcap"].mean().rename("mc_mean").reset_index()

d = b.merge(mc, on="gvkey", how="left")
cov = d["mc_mean"].notna().mean()
print(f"beta^UK firms: {len(d):,} | with Step-1 mktcap 2010-2014: "
      f"{d['mc_mean'].notna().sum():,} ({cov*100:.1f}%)")
print(f"median firm-mean mktcap ($M): {d['mc_mean'].median():,.1f}  "
      f"| p25={d['mc_mean'].quantile(.25):,.1f}  "
      f"p75={d['mc_mean'].quantile(.75):,.1f}")

d = d.dropna(subset=["mc_mean"]).copy()

# relative tercile cuts on nonneg beta^UK (same rule as Step 3)
nn = d.loc[d["beta_uk"] >= 0, "beta_uk"]
p33, p67 = nn.quantile(1/3), nn.quantile(2/3)

d["grp"] = np.where(
    (d["beta_uk"] >= 0) & (d["beta_uk"] >= p67), "treated",
    np.where((d["beta_uk"] >= 0) & (d["beta_uk"] <= p33), "control", "other"))


def frag(row):
    if row["grp"] == "treated":
        return abs(row["beta_uk"] - p67) < row["beta_se"]
    if row["grp"] == "control":
        return abs(row["beta_uk"] - p33) < row["beta_se"]
    return np.nan


d["fragile"] = d.apply(frag, axis=1)
d["sizeQ"] = pd.qcut(d["mc_mean"], 4, labels=["Q1 small", "Q2", "Q3", "Q4 large"])

print(f"\nrelative cuts: p33={p33:.3f} p67={p67:.3f}\n")
print(f"{'sizeQ':<9} {'n':>5} {'medMktCap$M':>12} {'medSE':>7} "
      f"{'med|b|':>7} {'%neg':>6} {'TC n':>5} {'%frag(T/C)':>11}")
for q in ["Q1 small", "Q2", "Q3", "Q4 large"]:
    s = d[d["sizeQ"] == q]
    tc = s[s["grp"].isin(["treated", "control"])]
    fr = tc["fragile"].mean() * 100 if len(tc) else float("nan")
    print(f"{q:<9} {len(s):>5} {s['mc_mean'].median():>12,.0f} "
          f"{s['beta_se'].median():>7.3f} {s['beta_uk'].abs().median():>7.3f} "
          f"{(s['beta_uk']<0).mean()*100:>5.1f}% {len(tc):>5} {fr:>10.1f}%")

# focused contrast: bottom vs top size quartile
lo = d[d["sizeQ"] == "Q1 small"]
hi = d[d["sizeQ"] == "Q4 large"]
print(f"\nCONTRAST  small-Q1 vs large-Q4:")
print(f"  med SE   : {lo['beta_se'].median():.3f}  vs  {hi['beta_se'].median():.3f}")
print(f"  %|beta|>3: {(lo['beta_uk'].abs()>3).mean()*100:.1f}%  vs  "
      f"{(hi['beta_uk'].abs()>3).mean()*100:.1f}%")
lotc = lo[lo['grp'].isin(['treated','control'])]['fragile'].mean()*100
hitc = hi[hi['grp'].isin(['treated','control'])]['fragile'].mean()*100
print(f"  near-cut fragility: {lotc:.1f}%  vs  {hitc:.1f}%")
print("\n=== END PHASE-3 (no fix applied) ===")
