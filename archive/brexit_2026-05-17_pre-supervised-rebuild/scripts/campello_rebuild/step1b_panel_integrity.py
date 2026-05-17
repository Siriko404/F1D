"""Campello et al. (2022 JFQA) replication — STEP 1b: panel-integrity gate.

From-scratch rebuild. Implements ONLY Table C.1 filter #7 (the panel-length /
continuity requirement) on the Step-1 sample. Inserted BETWEEN Step 1 and
Step 2 so that beta^UK (Step 2) is estimated on the panel-integrity-gated
universe, matching Campello's filter ORDER (C.1 applies #7 before the
"drop if missing beta^UK" row). NO beta^UK, NO terciles, NO panel, NO DiD.
Step-1 itself is NOT modified — this is a separate, additive, reversible
stage (revert = flip USE_STEP1B in step2_beta_uk.py back to False).

Authoritative spec — Supplementary Table C.1, "Sample Selection", row 7
(extracted verbatim from the PDF, count column included):

    Drop if non-consecutive quarters, or less than 12 quarters of
    non-missing data                                          75,013 -> 56,081

C.1 filter #6 ("missing key variables: INVESTMENT, ASSETS, CASH_FLOW,
TOBIN_Q, SALES_GROWTH", 93,011 -> 75,013) is DELIBERATELY NOT applied here
(advisor + /systematic-debugging: one variable at a time; #6 also needs a
net-new INVESTMENT construct). #7 is isolated first because it is the single
largest non-size filter (-18,932 fq) and pure continuity arithmetic on the
existing Step-1 panel.

Interpretation of "non-consecutive quarters, or less than 12 quarters"
(LOGGED — Campello's wording is ambiguous; this is the strict reading and
is recorded in metadata so it is auditable if results don't reconcile):

    A firm is KEPT iff its Step-1 firm-quarters (already past C.1 #1-5, so
    each present quarter = a non-missing-fundamentals quarter) contain an
    UNBROKEN RUN of >= 12 consecutive calendar quarters within
    2010:Q1-2016:Q4. Otherwise the whole firm is dropped (all its rows).
    Firm-level keep/drop (not quarter-trimming) — preserves the C.1
    firm-quarter accounting and keeps the test clean. Quarter-trimming to
    the longest run is a documented future sensitivity, NOT done here.

NOTE on the Step-1 absolute-count gap: our Step-1 post-#5 universe is
~84,488 fq vs Campello's row-5 count 93,011 (~91%, different raw COMPUSTAT
vintage). The C.1 ledger therefore will NOT reproduce 75,013/56,081 in
absolute terms; track the SHAPE of the drop, not the absolute counts.

Output
------
outputs/campello_rebuild/step1b_panel_integrity/<timestamp>/
    sample.parquet   Step-1 schema, firms failing #7 removed
    metadata.json    interpretation, waterfall, run-length distribution

Run:  python scripts/campello_rebuild/step1b_panel_integrity.py
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
STEP1_BASE = ROOT / "outputs" / "campello_rebuild" / "step1_sample"
OUT_BASE = ROOT / "outputs" / "campello_rebuild" / "step1b_panel_integrity"

MIN_CONSECUTIVE_Q = 12          # C.1 #7 "less than 12 quarters" threshold
PANEL_LO, PANEL_HI = 20101, 20164  # 2010Q1..2016Q4 (Step-1 window)


def _abort(msg: str) -> None:
    print(f"\nABORT — {msg}")
    print("Step 1b panel-integrity NOT built. Resolve before proceeding.")
    sys.exit(1)


def latest_step1_sample() -> Path:
    if not STEP1_BASE.exists():
        _abort(f"Step-1 dir missing: {STEP1_BASE} (run step1_sample.py first)")
    subs = sorted([d for d in STEP1_BASE.iterdir() if d.is_dir()])
    if not subs:
        _abort(f"no Step-1 timestamp dirs under {STEP1_BASE}")
    p = subs[-1] / "sample.parquet"
    if not p.exists():
        _abort(f"sample.parquet missing in {subs[-1]}")
    return p


def _cyq_to_ordinal(cyq: int) -> int:
    """cal_yr_qtr (year*10+q) -> a monotone quarter index (year*4 + q-1) so
    that consecutive calendar quarters differ by exactly 1 across year
    boundaries (e.g. 20104 -> 20111 both map to adjacent ordinals)."""
    y, q = divmod(cyq, 10)
    return y * 4 + (q - 1)


def _longest_run(ordinals: np.ndarray) -> int:
    """Longest run of strictly consecutive integers in a sorted unique array."""
    if ordinals.size == 0:
        return 0
    o = np.sort(np.unique(ordinals))
    best = run = 1
    for i in range(1, o.size):
        run = run + 1 if o[i] == o[i - 1] + 1 else 1
        best = max(best, run)
    return best


def main() -> None:
    print("Campello replication — STEP 1b  panel-integrity gate (C.1 #7)\n")

    s1 = latest_step1_sample()
    df = pq.read_table(s1).to_pandas()
    df["cal_yr_qtr"] = df["cal_yr_qtr"].astype(int)
    n_fq_in = len(df)
    n_firms_in = df["gvkey"].nunique()
    print(f"Step-1 sample: {s1}")
    print(f"  in: {n_fq_in:,} firm-quarters / {n_firms_in:,} firms")

    # ---- PROBE / GUARD ---------------------------------------------------
    print("\nPROBE / GUARD")
    oos = sorted(q for q in df["cal_yr_qtr"].unique()
                 if not (PANEL_LO <= q <= PANEL_HI))
    if oos:
        _abort(f"Step-1 rows outside 2010Q1-2016Q4 panel: {oos} "
               f"(Step-1 window filter broken).")
    print(f"  all quarters within [{PANEL_LO}..{PANEL_HI}]  GUARD OK\n")

    # ---- APPLY C.1 #7 (firm-level: longest consecutive run >= 12) --------
    df["_ord"] = df["cal_yr_qtr"].map(_cyq_to_ordinal)
    per_firm = df.groupby("gvkey")["_ord"].agg(
        max_run=lambda s: _longest_run(s.to_numpy()),
        n_q=lambda s: int(np.unique(s.to_numpy()).size),
    )
    keep_firms = per_firm.index[per_firm["max_run"] >= MIN_CONSECUTIVE_Q]
    out = (df[df["gvkey"].isin(keep_firms)]
           .drop(columns=["_ord"])
           .sort_values(["gvkey", "datadate"]).reset_index(drop=True))

    n_fq_out = len(out)
    n_firms_out = out["gvkey"].nunique()
    # diagnostic alternatives (interpretation forks — recorded, not applied)
    alt_total_ge12 = int((per_firm["n_q"] >= MIN_CONSECUTIVE_Q).sum())
    rd = per_firm["max_run"]

    if n_firms_out == 0:
        _abort("C.1 #7 removed every firm — no firm has a >=12-quarter "
               "consecutive run. Check Step-1 window / encoding.")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = OUT_BASE / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_dir / "sample.parquet", index=False)

    metadata = {
        "step": "1b — panel-integrity gate (Campello 2022 JFQA Supplementary "
                "Table C.1 filter #7)",
        "step1_input": str(s1),
        "filter_verbatim": "Drop if non-consecutive quarters, or less than 12 "
                           "quarters of non-missing data (Table C.1 row 7; "
                           "Campello ledger 75,013 -> 56,081)",
        "interpretation_LOGGED": (
            "Strict reading: KEEP a firm iff its Step-1 firm-quarters contain "
            "an UNBROKEN RUN of >= 12 consecutive calendar quarters in "
            "2010Q1-2016Q4. Firm-level keep/drop (not quarter-trimming). "
            "Step-1 rows are post-C.1-#1-5 so each present quarter is a "
            "non-missing-fundamentals quarter. Quarter-trimming to the "
            "longest run = documented future sensitivity, not applied."),
        "threshold_min_consecutive_quarters": MIN_CONSECUTIVE_Q,
        "scope_note": "C.1 #6 (missing key vars incl. INVESTMENT) "
                      "deliberately NOT applied here — one variable at a "
                      "time (advisor + systematic-debugging); #6 is a "
                      "separate later stage requiring a net-new INVESTMENT "
                      "construct.",
        "absolute_count_caveat": "Step-1 post-#5 ~84,488 vs Campello row-5 "
                                 "93,011 (~91%, vendor vintage). C.1 ledger "
                                 "not reproducible in absolute terms; track "
                                 "the SHAPE of the drop.",
        "waterfall": {
            "firm_quarters_in": n_fq_in,
            "firm_quarters_out": n_fq_out,
            "firm_quarters_dropped": n_fq_in - n_fq_out,
            "firms_in": int(n_firms_in),
            "firms_out": int(n_firms_out),
            "firms_dropped": int(n_firms_in - n_firms_out),
            "campello_anchor_row6_to_row7": [75013, 56081],
        },
        "interpretation_fork_diagnostics": {
            "kept_rule_max_run_ge_12": int(n_firms_out),
            "alt_total_quarters_ge_12_ignoring_gaps": alt_total_ge12,
            "delta_strict_vs_total": int(alt_total_ge12 - n_firms_out),
        },
        "max_run_distribution": {
            "min": int(rd.min()), "p10": float(rd.quantile(.10)),
            "p25": float(rd.quantile(.25)), "p50": float(rd.quantile(.50)),
            "p75": float(rd.quantile(.75)), "p90": float(rd.quantile(.90)),
            "max": int(rd.max()),
        },
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print("RESULT — C.1 #7 panel-integrity gate")
    print(f"  firm-quarters: {n_fq_in:,} -> {n_fq_out:,} "
          f"(dropped {n_fq_in - n_fq_out:,})")
    print(f"  firms        : {n_firms_in:,} -> {n_firms_out:,} "
          f"(dropped {n_firms_in - n_firms_out:,})")
    print(f"  max-run dist : p10={rd.quantile(.10):.0f} "
          f"p50={rd.quantile(.50):.0f} p90={rd.quantile(.90):.0f} "
          f"max={int(rd.max())}")
    print(f"  fork check   : strict(max_run>=12)={n_firms_out:,}  "
          f"alt(total_q>=12 ignoring gaps)={alt_total_ge12:,}  "
          f"delta={alt_total_ge12 - n_firms_out:,}")
    print(f"  Campello anchor (shape only, NOT absolute): 75,013 -> 56,081")
    print(f"  -> {out_dir / 'sample.parquet'}")
    print(f"  -> {out_dir / 'metadata.json'}")
    print("\n  Panel-integrity gate built. beta^UK = STEP 2 "
          "(set USE_STEP1B=True in step2_beta_uk.py to consume this).")


if __name__ == "__main__":
    main()
