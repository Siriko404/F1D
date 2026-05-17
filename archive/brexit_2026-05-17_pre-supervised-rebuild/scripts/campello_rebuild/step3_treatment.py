"""Campello et al. (2022 JFQA) replication — STEP 3: treatment assignment.

From-scratch rebuild. Assigns treated / control from the Step-2 per-firm
beta^UK. NO panel, NO POST window, NO DiD, NO controls, NO comparison to any
prior F1D output. Timeline (Step 4) and the DiD model (Step 5+) are
deliberately NOT scaffolded here.

Authoritative spec — §IV.C.1 Identification (PDF p.16 / journal p.3193):
    "we characterize firms as treated (control) units if they are in the
     upper (bottom) tercile of the nonnegative range of the beta^UK
     distribution. ... we do not include firms that benefit from uncertainty
     ... (firms with beta^UK < 0) ... this could lead to overestimation
     biases. ... 449 unique firms ... treated (beta^UK > 0.68) ... 360 ...
     control (beta^UK < 0.28)."

Operationalization (primary-source-pinned, NOT a judgment call)
---------------------------------------------------------------
The verbatim says "tercile of the nonnegative range of the beta^UK
DISTRIBUTION" => RELATIVE terciles of the nonnegative beta^UK pool. The
0.68 / 0.28 are Campello's REALIZED tercile breakpoints in his universe
(descriptive), not absolute laws. Faithful from-scratch recipe:

    nonneg pool      = firms with beta^UK >= 0
    p33, p67         = tercile breakpoints of that pool
    HIGH_BETA_UK = 1 (treated)  if beta^UK >= 0 AND beta^UK >= p67
    HIGH_BETA_UK = 0 (control)  if beta^UK >= 0 AND beta^UK <= p33
    HIGH_BETA_UK = NaN          middle tercile, OR beta^UK < 0 (excluded:
                                negative-beta firms are dropped from the
                                contrast to avoid overestimation bias)

0.68 / 0.28 and 449 / 360 are recorded in metadata as PAPER ANCHORS for
validation only. The continuous-treatment variant (paper: "include all
values of beta^UK") is a DIFFERENT specification (investment Table 2 col 1),
not the cash baseline (Table 8 col 1 uses the tercile dummy) — out of scope
for this step.

Output
------
outputs/campello_rebuild/step3_treatment/<timestamp>/
    treatment.parquet   gvkey, beta_uk, beta_se, HIGH_BETA_UK
    metadata.json       rule, breakpoints, counts, paper anchors

Run:  python scripts/campello_rebuild/step3_treatment.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
STEP2_BASE = ROOT / "outputs" / "campello_rebuild" / "step2_beta_uk"
OUT_BASE = ROOT / "outputs" / "campello_rebuild" / "step3_treatment"

MIN_NONNEG = 30  # below this a tercile cut is meaningless -> abort

# Campello's realized tercile breakpoints + counts (paper p.3193). PAPER
# ANCHORS for validation only; the rule is relative terciles, not these.
CAMPELLO_TOP_CUT = 0.68
CAMPELLO_BOT_CUT = 0.28
CAMPELLO_N_TREATED = 449
CAMPELLO_N_CONTROL = 360


def _abort(msg: str) -> None:
    print(f"\nABORT — {msg}")
    print("Step 3 treatment NOT built. Resolve before proceeding.")
    sys.exit(1)


def latest_step2() -> Path:
    if not STEP2_BASE.exists():
        _abort(f"Step-2 dir missing: {STEP2_BASE} (run step2_beta_uk.py first)")
    subs = sorted([d for d in STEP2_BASE.iterdir() if d.is_dir()])
    if not subs:
        _abort(f"no Step-2 timestamp dirs under {STEP2_BASE}")
    p = subs[-1] / "beta_uk.parquet"
    if not p.exists():
        _abort(f"beta_uk.parquet missing in {subs[-1]}")
    return p


def main() -> None:
    print("Campello replication — STEP 3  treatment assignment\n")

    s2 = latest_step2()
    df = pq.read_table(s2).to_pandas()
    print(f"Step-2 beta^UK: {s2}\n  firms: {len(df):,}")
    if "beta_uk" not in df.columns:
        _abort("Step-2 parquet has no 'beta_uk' column.")

    print("\nPROBE / GUARD")
    nonneg = df.loc[df["beta_uk"] >= 0, "beta_uk"]
    n_neg = int((df["beta_uk"] < 0).sum())
    print(f"  nonneg beta^UK: {len(nonneg):,}   negative (excluded): {n_neg:,}")
    if len(nonneg) < MIN_NONNEG:
        _abort(f"only {len(nonneg)} nonneg beta^UK — tercile cut meaningless.")
    print("  GUARD OK\n")

    # Campello §IV.C.1 VERBATIM: treated (control) = upper (bottom) TERCILE
    # of the nonnegative range of the beta^UK distribution. 33rd/67th
    # percentile (equal-count terciles) of the nonneg pool; negatives
    # (beta^UK < 0) excluded from the contrast (overestimation-bias,
    # verbatim). 0.68/0.28 = Campello's REALIZED breakpoints (validation
    # anchors, not imposed). D5 absolute-cut reverted 2026-05-17 — the
    # paper states a METHOD; 0.68/0.28 are its outcome, not parameters.
    p33 = float(nonneg.quantile(1 / 3))   # 33rd pctile of nonneg pool
    p67 = float(nonneg.quantile(2 / 3))   # 67th pctile of nonneg pool

    high = pd.Series(np.nan, index=df.index, dtype="float64")
    nn = df["beta_uk"] >= 0
    high[nn & (df["beta_uk"] >= p67)] = 1.0          # treated = top tercile
    high[nn & (df["beta_uk"] <= p33)] = 0.0          # control = bottom tercile
    df["HIGH_BETA_UK"] = high

    n_treated = int((df["HIGH_BETA_UK"] == 1).sum())
    n_control = int((df["HIGH_BETA_UK"] == 0).sum())
    n_middle = int(((df["beta_uk"] >= 0) & df["HIGH_BETA_UK"].isna()).sum())

    out = (df[["gvkey", "beta_uk", "beta_se", "HIGH_BETA_UK"]]
           .sort_values("gvkey").reset_index(drop=True))

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = OUT_BASE / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_dir / "treatment.parquet", index=False)

    metadata = {
        "step": "3 — treatment assignment (Campello 2022 JFQA §IV.C.1)",
        "step2_input": str(s2),
        "rule": ("Campello §IV.C.1 VERBATIM: treated (control) = upper "
                 "(bottom) TERCILE of the NONNEGATIVE range of the beta^UK "
                 "distribution (33rd/67th percentile, equal-count); negatives "
                 "(beta^UK<0) excluded from the contrast (verbatim). 0.68/0.28 "
                 "= Campello's REALIZED breakpoints (validation anchors, NOT "
                 "imposed). D5 absolute-cut reverted 2026-05-17: paper states "
                 "a method; 0.68/0.28 are its realized outcome."),
        "breakpoints_relative_nonneg_p33_p67": {"p33": p33, "p67": p67},
        "assignment": {
            "treated_HIGH_1": "beta^UK >= 0 AND beta^UK >= p67",
            "control_HIGH_0": "beta^UK >= 0 AND beta^UK <= p33",
            "excluded_NaN": "middle tercile OR beta^UK < 0",
        },
        "counts": {
            "treated": n_treated, "control": n_control,
            "middle_unused": n_middle, "negative_excluded": n_neg,
            "total_firms": int(len(df)),
        },
        "paper_anchors_validation_only": {
            "campello_realized_cuts": {"top": CAMPELLO_TOP_CUT,
                                       "bottom": CAMPELLO_BOT_CUT},
            "campello_counts": {"treated": CAMPELLO_N_TREATED,
                                "control": CAMPELLO_N_CONTROL},
            "note": "0.68/0.28 are Campello's realized breakpoints, not an "
                    "absolute rule; recorded for validation only",
        },
        "out_of_scope": "POST window=Step4, DiD model=Step5+, continuous-"
                        "treatment variant = different spec (not cash baseline)",
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print("RESULT — treatment assignment")
    print(f"  tercile cuts (33/67 pct, nonneg pool): p33={p33:.4f}  "
          f"p67={p67:.4f}")
    print(f"  TREATED (HIGH=1): {n_treated:,}")
    print(f"  CONTROL (HIGH=0): {n_control:,}")
    print(f"  middle (unused) : {n_middle:,}")
    print(f"  negative (excl) : {n_neg:,}")
    print(f"\n  Campello anchors (paper, validation only — NOT prior-F1D):")
    print(f"    realized cuts  : top {CAMPELLO_TOP_CUT}  bottom {CAMPELLO_BOT_CUT}")
    print(f"    counts         : {CAMPELLO_N_TREATED} treated / "
          f"{CAMPELLO_N_CONTROL} control")
    print(f"  -> {out_dir / 'treatment.parquet'}")
    print(f"  -> {out_dir / 'metadata.json'}")
    print("\n  Treatment assigned. POST window = STEP 4, DiD = STEP 5+ "
          "(NOT built here).")


if __name__ == "__main__":
    main()
