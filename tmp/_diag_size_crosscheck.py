"""SIZE cross-check: validate our β^UK tercile membership against Campello's
published Table 1 moment.

Campello (Table 1 Panels B/C, p.3198):
  Treated (top tercile β^UK):  SIZE (log assets) mean 6.11
  Control (bottom tercile):    SIZE (log assets) mean 7.25
  → treated firms are SMALLER (verbatim §IV.D: "firms in the treatment group
    are smaller as measured by total assets").
  fn22: "The 449 firms in the top tercile of β^UK had average assets of
    $2.81 billion in 2016:Q2."

If OUR treated come out LARGER than control, our β ranking is inverted/corrupt
→ step2 (β estimation) is the bug, not step3 (the tercile rule).

SIZE = log(atq). We report mean log(atq) and mean atq ($M) per group, both
over the full step1 panel-quarters and (separately) at 2016Q2 to match fn22.
Read-only.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]


def _latest(sub: str) -> Path:
    base = ROOT / "outputs" / "campello_rebuild" / sub
    return sorted(d for d in base.iterdir() if d.is_dir())[-1]


def main() -> None:
    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    trt = pd.read_parquet(_latest("step3_treatment") / "treatment.parquet",
                          columns=["gvkey", "group", "in_step1", "beta_uk"])
    trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)
    tc = trt[trt["in_step1"] & trt["group"].isin(["treated", "control"])].copy()

    df = s1.merge(tc[["gvkey", "group", "beta_uk"]], on="gvkey", how="inner")
    df = df[df["atq"] > 0].copy()
    df["log_assets"] = np.log(df["atq"])

    print("=" * 64)
    print("SIZE CROSS-CHECK — our β^UK terciles vs Campello Table 1 B/C")
    print("=" * 64)

    def _report(sub: pd.DataFrame, tag: str) -> None:
        print(f"\n[{tag}]")
        for grp in ("treated", "control"):
            g = sub[sub["group"] == grp]
            la = g["log_assets"]
            at = g["atq"]
            print(f"  {grp:<8}  log(atq) mean={la.mean():.2f} med={la.median():.2f}"
                  f"   atq($M) mean={at.mean():,.0f} med={at.median():,.0f}"
                  f"   β^UK mean={g['beta_uk'].mean():.3f}"
                  f"   n_firms={g['gvkey'].nunique():,}  n_fq={len(g):,}")

    # All step1 panel-quarters
    _report(df, "ALL step1 panel-quarters")
    # 2016Q2 to match fn22 ($2.81B avg assets for treated)
    _report(df[df["cal_yr_qtr"] == 20162], "2016Q2 only (matches fn22)")

    print("\n" + "-" * 64)
    print("Campello target:  treated log(atq) 6.11 (SMALLER) | control 7.25")
    print("                  fn22: treated avg assets $2.81B @ 2016Q2")
    print("VERDICT: if our treated > control on size → β ranking inverted.")


if __name__ == "__main__":
    main()
