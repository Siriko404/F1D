"""Campello et al. (2022 JFQA) replication — STEP 4: DiD timeline / window.

From-scratch rebuild. Builds ONLY the eq-14 DiD sample (full panel) and the
POST dummy. NO eq-14 interaction, NO controls, NO fixed effects, NO clustered
SE, NO cash DV, NO continuous-beta^UK variant, NO comparison to any prior
F1D output. Step 5+ are deliberately NOT scaffolded here.

Authoritative spec
------------------
Main text, Campello et al. 2022 JFQA, §IV.C.2 "Timeline" + §IV.C.3
"Empirical Model" (PDF p.18-19 / journal p.3195-3196), verbatim from the
curated extraction tmp/campello_v2/main_p18.txt + main_p19.txt:

  §IV.C.2: "We focus on a relatively short window around the Brexit vote ...
   We limit our analysis to the end of 2016 due to the start of the Trump
   administration in Jan. 2017. We show in later robustness checks that
   results also hold for a window that excludes Trump's election."

  §IV.C.3 (eq-14): "Y = alpha + delta*[POST . HIGH_UK_EXPOSURE]
   + theta*CONTROLS_{i,t-1} + SUM FIRM_i + SUM (INDUSTRY_j x QUARTER_t)
   + eps_{i,t} ... POST_t equals 1 if the time period is in the 2016:Q3-Q4
   window."

  §IV.C.3: "Differences over the 2016:Q3-Q4 period are taken relative to the
   same two quarters in the previous year (2015:Q3-Q4) in order to minimize
   the impact of seasonal effects."

Operationalization (A4 audit correction, 2026-05-16)
----------------------------------------------------
eq-14 is a FULL-PANEL difference-in-differences over Campello's whole
2010:Q1-2016:Q4 sample (the Step-1 window) with a POST dummy — NOT a
4-calendar-quarter subset. A prior build restricted the regression to
{2015Q3,2015Q4,2016Q3,2016Q4}; the A4 audit verified that as a bug against
(i) eq-14 verbatim above, (ii) the firm counts in §IV.C.1, and (iii) the
eq-14-faithful F1D production runner whose N matches Campello's 17,170.
The "2016:Q3-Q4 relative to 2015:Q3-Q4" seasonal alignment is delivered by
the INDUSTRY_j x QUARTER_t fixed effects on the full panel (Step 5/7), NOT
by subsetting calendar quarters here.

    POST dummy = 1  iff  cal_yr_qtr in {20163, 20164}  else 0   (verbatim)
    panel      = ALL Step-1 firm-quarters (2010Q1..2016Q4) for firms
                 assigned treated/control in Step 3
                 (HIGH_BETA_UK in {0,1}; middle tercile + neg-beta dropped)

Anchor events (context only, not a filter): Feb 22, 2016 (Cameron announces
referendum date) and Jun 23, 2016 (the vote). End-2016 cap is the BASELINE;
the Trump-excluded window is a later robustness check, not built.

Output
------
outputs/campello_rebuild/step4_timeline/<timestamp>/
    panel.parquet   gvkey, datadate, cal_yr_qtr, HIGH_BETA_UK, POST
    metadata.json    window spec, counts, self-checks, paper anchors

Run:  python scripts/campello_rebuild/step4_timeline.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
STEP1_BASE = ROOT / "outputs" / "campello_rebuild" / "step1_sample"
STEP3_BASE = ROOT / "outputs" / "campello_rebuild" / "step3_treatment"
OUT_BASE = ROOT / "outputs" / "campello_rebuild" / "step4_timeline"

# §IV.C.3 eq-14: FULL 2010Q1-2016Q4 panel + POST dummy (NOT a 4-qtr subset).
# cal_yr_qtr = year*10 + quarter (Step-1 encoding). A4 audit correction
# 2026-05-16: the prior {2015/2016 Q3-Q4} 4-quarter restriction was a bug —
# eq-14 is a full-panel POST-dummy DiD; seasonal alignment is delivered by
# the IND_j x QTR_t fixed effects (Step 5/7), not by subsetting quarters.
POST_QTRS = {20163, 20164}         # "POST_t = 1 iff 2016:Q3-Q4" (verbatim)
PANEL_LO, PANEL_HI = 20101, 20164  # eq-14 panel = Step-1 window 2010Q1-2016Q4


def _abort(msg: str) -> None:
    print(f"\nABORT — {msg}")
    print("Step 4 timeline NOT built. Resolve before proceeding.")
    sys.exit(1)


def _latest(base: Path, fname: str, runner: str) -> Path:
    if not base.exists():
        _abort(f"missing dir {base} (run {runner} first)")
    subs = sorted([d for d in base.iterdir() if d.is_dir()])
    if not subs:
        _abort(f"no timestamp dirs under {base}")
    p = subs[-1] / fname
    if not p.exists():
        _abort(f"{fname} missing in {subs[-1]}")
    return p


def main() -> None:
    print("Campello replication — STEP 4  DiD timeline / POST window\n")

    s1 = _latest(STEP1_BASE, "sample.parquet", "step1_sample.py")
    s3 = _latest(STEP3_BASE, "treatment.parquet", "step3_treatment.py")
    samp = pq.read_table(
        s1, columns=["gvkey", "datadate", "cal_yr_qtr"]).to_pandas()
    trt = pq.read_table(
        s3, columns=["gvkey", "HIGH_BETA_UK"]).to_pandas()
    print(f"Step-1 sample : {s1}\n  firm-quarters: {len(samp):,}")
    print(f"Step-3 treat  : {s3}\n  firms: {len(trt):,}")

    # join key: same Compustat lineage; normalise dtype, do not assume zfill.
    samp["gvkey"] = samp["gvkey"].astype(str)
    trt["gvkey"] = trt["gvkey"].astype(str)
    samp["datadate"] = pd.to_datetime(samp["datadate"], errors="coerce")
    samp["cal_yr_qtr"] = samp["cal_yr_qtr"].astype(int)

    # ---- PROBE / GUARD ---------------------------------------------------
    print("\nPROBE / GUARD")
    # cal_yr_qtr encoding sanity: recompute from datadate, must match Step-1's
    # year*10+q. Catches a year*100 vs year*10 mismatch (silent window bug).
    q = ((samp["datadate"].dt.month - 1) // 3 + 1).astype(int)
    recomputed = samp["datadate"].dt.year * 10 + q
    n_bad = int((recomputed != samp["cal_yr_qtr"]).sum())
    print(f"  cal_yr_qtr vs datadate-recompute mismatches: {n_bad}")
    if n_bad != 0:
        _abort(f"{n_bad} rows where cal_yr_qtr != year*10+q — encoding "
               f"mismatch vs Step-1; window filter would be wrong.")
    n3_treated = int((trt["HIGH_BETA_UK"] == 1).sum())
    n3_control = int((trt["HIGH_BETA_UK"] == 0).sum())
    print(f"  Step-3 treated={n3_treated:,}  control={n3_control:,}")
    if n3_treated == 0 or n3_control == 0:
        _abort("Step-3 has an empty treated or control group.")
    print("  GUARD PASSED\n")

    # ---- BUILD -----------------------------------------------------------
    win = samp.copy()  # eq-14 = FULL 2010Q1-2016Q4 panel (no 4-qtr subset)
    # keep only Step-3 treated/control firms (HIGH in {0,1}); NaN excluded.
    trt_bin = trt[trt["HIGH_BETA_UK"].isin([0.0, 1.0])][["gvkey", "HIGH_BETA_UK"]]
    panel = win.merge(trt_bin, on="gvkey", how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_QTRS).astype(int)
    panel = (panel[["gvkey", "datadate", "cal_yr_qtr", "HIGH_BETA_UK", "POST"]]
             .sort_values(["gvkey", "cal_yr_qtr"]).reset_index(drop=True))

    # ---- POST-BUILD ASSERTIONS ------------------------------------------
    # full eq-14 panel: every quarter must lie in Step-1's 2010Q1-2016Q4.
    out_of_span = sorted(q for q in panel["cal_yr_qtr"].unique()
                         if not (PANEL_LO <= q <= PANEL_HI))
    if out_of_span:
        _abort(f"quarters outside 2010Q1-2016Q4 panel: {out_of_span}")
    # POST dummy must agree with the verbatim definition exactly.
    bad_post = int((panel["POST"] !=
                    panel["cal_yr_qtr"].isin(POST_QTRS).astype(int)).sum())
    if bad_post != 0:
        _abort(f"{bad_post} rows with POST != (qtr in 2016Q3-Q4).")
    # full-panel DiD needs BOTH regimes present (pre and 2016Q3-Q4 post).
    if panel["POST"].nunique() < 2:
        _abort("POST is constant — full panel must contain both pre and "
               "2016Q3-Q4 post quarters (check Step-1 window / Step-3 "
               "firm overlap).")

    n_obs = len(panel)
    n_treated_f = int(panel.loc[panel["HIGH_BETA_UK"] == 1, "gvkey"].nunique())
    n_control_f = int(panel.loc[panel["HIGH_BETA_UK"] == 0, "gvkey"].nunique())
    post_frac = float(panel["POST"].mean())
    high_frac = float((panel["HIGH_BETA_UK"] == 1).mean())

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = OUT_BASE / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(out_dir / "panel.parquet", index=False)

    metadata = {
        "step": "4 — DiD timeline / POST window (Campello 2022 JFQA "
                "§IV.C.2 + §IV.C.3)",
        "step1_input": str(s1),
        "step3_input": str(s3),
        "spec_verbatim": {
            "pre_post": "Differences over the 2016:Q3-Q4 period are taken "
                        "relative to the same two quarters in the previous "
                        "year (2015:Q3-Q4) in order to minimize the impact "
                        "of seasonal effects.",
            "post_dummy": "POST_t equals 1 if the time period is in the "
                          "2016:Q3-Q4 window.",
            "short_window_cap": "relatively short window ... Bloom (2009) "
                                "... limit our analysis to the end of 2016 "
                                "due to the start of the Trump "
                                "administration in Jan. 2017.",
        },
        "window": {
            "panel_span": [PANEL_LO, PANEL_HI],
            "panel_qtrs_present": sorted(int(q) for q in
                                         panel["cal_yr_qtr"].unique()),
            "POST_qtrs": sorted(POST_QTRS),
            "encoding": "cal_yr_qtr = year*10 + quarter (Step-1 convention)",
            "design": "eq-14 FULL 2010Q1-2016Q4 panel + POST dummy; NO "
                      "calendar-quarter subsetting (A4 correction 2026-05-16)",
        },
        "counts": {
            "panel_firm_quarters": n_obs,
            "treated_firms_in_panel": n_treated_f,
            "control_firms_in_panel": n_control_f,
            "step3_treated_firms": n3_treated,
            "step3_control_firms": n3_control,
            "post_fraction": round(post_frac, 4),
            "high_fraction": round(high_frac, 4),
        },
        "self_checks": {
            "cal_yr_qtr_encoding_verified": True,
            "all_quarters_within_2010Q1_2016Q4_panel": True,
            "post_dummy_matches_verbatim": True,
            "both_post_regimes_present": True,
            "note": "treated/control firms in panel may be < Step-3 totals "
                    "if a firm has no Step-1 firm-quarters in 2010Q1-2016Q4 "
                    "(legitimate data condition, not a bug — NOT aborted).",
        },
        "deferred_metadata_flags": {
            "eq14_full_panel": "A4 audit correction 2026-05-16: eq-14 is a "
                "FULL 2010Q1-2016Q4 panel + POST dummy (verified vs §IV.C.3 "
                "verbatim, §IV.C.1 firm counts, and the eq-14-faithful F1D "
                "production runner whose N matches Campello 17,170). The "
                "prior 4-quarter restriction was a bug, now removed.",
            "step6_will_lag_from_step1": "eq-14 CONTROLS_{i,t-1} are NOT in "
                "this panel. Step 6 pulls lagged values directly from raw "
                "Compustat (lag of t = previous calendar quarter; YoY lag "
                "for sales growth). Lag lookups span beyond the panel by "
                "design (lookup scope != regression scope).",
        },
        "out_of_scope": "eq-14 interaction + controls + FE + clustered SE = "
                        "Step 5; cash DV = Step 7; continuous-beta^UK = "
                        "different spec. NONE built here (strict-sequential).",
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print("RESULT — DiD timeline / POST window")
    print(f"  panel firm-quarters : {n_obs:,}")
    print(f"  treated firms (panel): {n_treated_f:,}  "
          f"(Step-3: {n3_treated:,})")
    print(f"  control firms (panel): {n_control_f:,}  "
          f"(Step-3: {n3_control:,})")
    print(f"  POST fraction        : {post_frac:.3f}  "
          f"(2016Q3-Q4 of full 2010Q1-2016Q4 panel; ~2/28 ~ 0.07 balanced)")
    print(f"  HIGH fraction        : {high_frac:.3f}  "
          f"(treated share; expect ~0.50)")
    qspan = sorted(int(q) for q in panel['cal_yr_qtr'].unique())
    print(f"  panel quarters       : {len(qspan)}  "
          f"[{qspan[0]}..{qspan[-1]}]")
    print(f"  -> {out_dir / 'panel.parquet'}")
    print(f"  -> {out_dir / 'metadata.json'}")
    print("\n  Timeline built. eq-14 DiD = STEP 5 (NOT built here).")


if __name__ == "__main__":
    main()
