"""Step-6 EPS-missingness integrity check (advisor-mandated, pre-Step-7).

EVIDENCE ONLY. Is the 24.5% eps_fpi6_lag missingness random, or correlated
with HIGH / POST / HIGH x POST? If any gap > ~5pp the with-EPS N=1,985
sample is non-randomly selected (IBES-link-induced selection) and the
ex-EPS sensitivity must carry equal weight. <30s. No fix, no regression.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
S6 = ROOT / "outputs" / "campello_rebuild" / "step6_controls"

d = sorted(x for x in S6.iterdir() if x.is_dir())[-1]
df = pq.read_table(d / "controls.parquet").to_pandas()
df["m"] = df["eps_fpi6_lag"].isna()
df["HP"] = (df["HIGH_BETA_UK"] == 1) & (df["POST"] == 1)

overall = df["m"].mean()


def gap(col, a, b):
    pa = df.loc[df[col] == a, "m"].mean()
    pb = df.loc[df[col] == b, "m"].mean()
    return round(pa, 4), round(pb, 4), round(abs(pa - pb) * 100, 2)


h1, h0, gh = gap("HIGH_BETA_UK", 1, 0)
p1, p0, gp = gap("POST", 1, 0)
hp1, hp0, ghp = gap("HP", True, False)
mx = max(gh, gp, ghp)
verdict = ("RANDOM — proceed with N=1,985 headline confidently"
           if mx <= 5.0 else
           "NON-RANDOM (>5pp) — IBES-link selection; ex-EPS sensitivity "
           "must carry equal weight; REPORT to advisor before Step 7")

rep = {
    "generated": datetime.now().isoformat(timespec="seconds"),
    "overall_eps_missing": round(overall, 4),
    "by_HIGH": {"HIGH=1": h1, "HIGH=0": h0, "gap_pp": gh},
    "by_POST": {"POST=1": p1, "POST=0": p0, "gap_pp": gp},
    "by_HIGHxPOST": {"HP=1": hp1, "HP=0": hp0, "gap_pp": ghp},
    "max_gap_pp": mx,
    "verdict": verdict,
}
(d / "eps_missing_integrity.json").write_text(json.dumps(rep, indent=2))

print("EPS-MISSINGNESS INTEGRITY CHECK")
print(f"  overall eps missing      : {overall*100:5.1f}%")
print(f"  by HIGH  1={h1*100:4.1f}% 0={h0*100:4.1f}%  gap={gh:4.1f}pp")
print(f"  by POST  1={p1*100:4.1f}% 0={p0*100:4.1f}%  gap={gp:4.1f}pp")
print(f"  by HIGHxPOST 1={hp1*100:4.1f}% else={hp0*100:4.1f}%  gap={ghp:4.1f}pp")
print(f"  max gap = {mx:.1f}pp")
print(f"\n  VERDICT: {verdict}")
print(f"  -> {d / 'eps_missing_integrity.json'}")
