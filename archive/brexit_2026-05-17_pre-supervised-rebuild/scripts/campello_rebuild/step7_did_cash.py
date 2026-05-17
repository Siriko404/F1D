"""Campello et al. (2022 JFQA) replication — STEP 7: real cash DiD (eq-14).

FINAL step. Runs the real eq-14 regression on the Step-6 panel with the
cash dependent variable. NO synthetic data. NO comparison to any prior F1D
output. NO NWC / profits / continuous-beta^UK (each a separate request).

Authoritative spec: Table 8 col 1 (main_p31.txt) — DV = CASH =
cheq_t / (atq_{t-1} - cheq_{t-1}); treatment = top tercile beta^UK;
eq-14 with firm FE + FIC-100 x calendar-quarter FE; SE double-clustered
firm + calendar quarter.

PRIMARY SPEC = EX-EPS (10 controls), advisor-ratified:
  The IBES->gvkey CUSIP8 link misses 36.1% of treated vs 14.2% of control
  firms (21.9pp gap; `step6.../eps_missing_integrity.json`). Listwise
  inclusion of the EPS control therefore imposes a TREATMENT-CORRELATED
  sample selection on delta-hat — an artifact of THIS extract's link, not
  a condition Campello faced. Faithful execution => primary drops EPS;
  with-EPS retained as a caveated sensitivity (paper §IV.C.3 text spec).
  Same discipline already accepted for vol() / vendor gap / PhillyFed-LEI.

Three fits (advisor-specified; full 2010Q1-2016Q4 panel after A4):
  primary             ex-EPS  (5 firm ctrl, macro in FE)   <- HEADLINE
  sens_with_eps       with-EPS (6 firm ctrl)               paper-text spec
  diag_sample_effect  ex-EPS ctrl ON the with-EPS sample   isolates
                                                           selection vs control
  N is reported from the fit, NOT asserted. Full-panel N ~17k expected
  (the prior ~2,598 / ~1,985 were 4-qtr-bug artifacts; A4 correction).

Output
------
outputs/campello_rebuild/step7_did_cash/<timestamp>/
    cash_did.json   4 fits + paper anchor + interpretation rules
    metadata.json   spec, deviations, cluster/R2 conventions

Run:  python scripts/campello_rebuild/step7_did_cash.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import step5_did as s5  # noqa: E402  (verified estimator; in-rebuild reuse)

ROOT = HERE.parents[1]
S6_BASE = ROOT / "outputs" / "campello_rebuild" / "step6_controls"
OUT_BASE = ROOT / "outputs" / "campello_rebuild" / "step7_did_cash"

# Macro (fx/vix/umcsent/livingston/ads) is TIME-ONLY: constant within each
# calendar quarter, so perfectly absorbed by the FIC100 x cal_yr_qtr FE on
# ANY number of quarters (Stata reghdfe absorbs silently; linearmodels
# rank-fails). Campello-faithful => macro lives IN the FE, NOT as explicit
# regressors (Table 8: "Controls: Yes" + "Industry x time FE: Yes" + zero
# macro coefficients). Root cause: _diag_s7_rank.py. Holds identically on
# the full 2010Q1-2016Q4 panel (A4 correction). Explicit ctrls = FIRM-level.
FIRM5 = ("tobinq_lag", "cf_lag", "logassets_lag", "salesgrowth_lag",
         "stockret_lag")
FIRM5_EPS = FIRM5 + ("eps_fpi6_lag",)

PAPER_ANCHOR = {"delta": 0.231, "se": 0.059, "n": 17170,
                "source": "Table 8 col 1, POST x HIGH_betaUK; verified "
                          "tmp/campello_v2/campello_paper_FULL.md "
                          "L3785-3786 & L3844-3846 (0.231***, SE 0.059), "
                          "n L3794/L3858 (17,170)",
                "note": "CORRECTED 2026-05-16: prior 0.0539 was an "
                        "extraction corruption (coef + SE garbled); true "
                        "Table 8 col-1 = +0.231*** SE 0.059. Validation "
                        "reference ONLY — locked process forbids changing "
                        "the recipe to chase it"}

# Independent eq-14-faithful cross-anchor: the F1D production runner
# (src/f1d/econometric/run_h1_5_brexit_did.py, DiD_BetaUK / cash_brexit_dv /
# campello_exact FE) on the SAME full 2010Q1-2016Q4 panel design. Verified
# from the primary output file (not memory):
# outputs/econometric/h1_5_brexit_did/2026-05-14_204900/model_diagnostics.csv
# This corrected rebuild's delta_hat should land in the same neighbourhood.
F1D_CROSS_ANCHOR = {"delta": 0.13206, "se": 0.12279, "p_one": 0.141,
                    "n": 17176, "r2_within": 0.0162,
                    "source": "F1D run_h1_5_brexit_did.py eq-14-faithful; "
                              "model_diagnostics.csv 2026-05-14_204900 "
                              "(DiD_BetaUK, cash_brexit_dv, campello_exact)",
                    "note": "sign-correct, ~57% of +0.231, NOT significant "
                            "(p_one 0.141). Independent eq-14 cross-check "
                            "anchor, NOT a target to chase."}


def _abort(m: str) -> None:
    print(f"\nABORT — {m}")
    sys.exit(1)


def _latest() -> Path:
    if not S6_BASE.exists():
        _abort("step6_controls dir missing (run step6_controls.py)")
    subs = sorted(d for d in S6_BASE.iterdir() if d.is_dir())
    p = subs[-1] / "controls.parquet"
    if not p.exists():
        _abort(f"controls.parquet missing in {subs[-1]}")
    return p


def _fit(df: pd.DataFrame, ctrls: tuple[str, ...], sample_rows) -> dict:
    """Complete-case on `sample_rows`' control list, fit eq-14 with `ctrls`."""
    sub = df.dropna(subset=list(sample_rows) + ["CASH_DV", "fic100"]).copy()
    r = s5.fit_did(
        sub, y_col="CASH_DV", industry_col="fic100",
        high_col="HIGH_BETA_UK", post_col="POST",
        entity_col="gvkey", time_col="cal_yr_qtr",
        control_cols=ctrls, cluster_cols=("gvkey", "cal_yr_qtr"),
    )
    r["controls_used"] = list(ctrls)
    r["n_controls"] = len(ctrls)
    return r


def main() -> None:
    print("Campello replication — STEP 7  real cash DiD (eq-14)\n")
    s6 = _latest()
    df = pq.read_table(s6).to_pandas()
    df["gvkey"] = df["gvkey"].astype(str).str.split(".").str[0].str.zfill(6)
    df["cal_yr_qtr"] = df["cal_yr_qtr"].astype(int)
    print(f"Step-6 controls: {s6}\n  rows {len(df):,}  firms "
          f"{df['gvkey'].nunique():,}")

    # PRIMARY — firm controls only (macro absorbed by FE), ex-EPS sample
    primary = _fit(df, FIRM5, FIRM5)                       # full panel ~17k
    # SENS — + EPS (paper-text spec; treatment-selected subsample)
    sens_with_eps = _fit(df, FIRM5_EPS, FIRM5_EPS)         # < primary (EPS link)
    # DIAG — FIRM5 controls but ON the with-EPS sample:
    #        isolates sample-selection effect from the EPS-control effect.
    diag_sample_effect = _fit(df, FIRM5, FIRM5_EPS)        # = sens_with_eps N

    cash = df["CASH_DV"].dropna()
    out = {
        "primary": primary,
        "sens_with_eps": sens_with_eps,
        "diag_sample_effect": diag_sample_effect,
        "paper_anchor": PAPER_ANCHOR,
        "f1d_cross_anchor": F1D_CROSS_ANCHOR,
        "macro_absorbed_by_FE": (
            "5 macro controls (fx/vix/umcsent/livingston/ads) are time-only "
            "(constant within each calendar quarter) -> perfectly absorbed "
            "by the FIC100 x cal_yr_qtr FE on the full 2010Q1-2016Q4 panel, "
            "for ANY number of quarters (root cause _diag_s7_rank.py). They "
            "are IN the model via the FE, NOT explicit regressors — "
            "Campello-faithful (Table 8: 'Controls: Yes' + 'Industry x time "
            "FE: Yes', no macro coefs). The PhillyFed-LEI->ADS deviation "
            "lives in the FE; a drop-ADS sensitivity is NOT applicable at "
            "this FE structure (would require removing time FE = a different "
            "spec)."),
        "selection_bias_note": (
            "EPS missingness was treatment-correlated on the prior 4-qtr "
            "run (36.1% treated vs 14.2% control, 21.9pp gap — figures from "
            "the 4-qtr era; RECOMPUTE on the full panel, A6/A7). Listwise "
            "EPS => treatment-correlated selection => PRIMARY = ex-EPS "
            "firm-controls; with-EPS demoted to a caveated sensitivity."),
        "interpretation_rules": [
            "primary ~ sens_with_eps  -> EPS attrition benign; headline robust",
            "primary != sens_with_eps AND diag_sample_effect ~ sens_with_eps "
            "-> the SELECTION (lost treated firms) drives the gap, not the "
            "EPS control itself",
            "primary != sens_with_eps AND diag_sample_effect ~ primary "
            "-> the EPS CONTROL itself moves delta-hat (not selection)",
            "compare delta_hat to TWO anchors: paper +0.231*** (Table 8) "
            "and the independent eq-14-faithful F1D cross-anchor +0.1321 "
            "(NS, ~57%, N 17,176). The full-panel rebuild delta_hat is the "
            "OBSERVED replication result, reported honestly: a sign-correct "
            "but attenuated and likely-insignificant effect is a genuine "
            "non-replication finding (admittedly-imperfect beta^UK proxy "
            "fn13 + vendor constraint), NOT a defect to 'fix' by changing "
            "the recipe, and NOT 'structurally expected — do not chase' "
            "(that prior framing was a 4-qtr-bug artifact, A4/A8). State "
            "the gap; do not rationalize it away or chase significance.",
        ],
        "cash_dv_distribution_winsorized_1pct": {
            "n": int(cash.size),
            "min": float(cash.min()), "p1": float(cash.quantile(.01)),
            "p50": float(cash.quantile(.50)), "p99": float(cash.quantile(.99)),
            "max": float(cash.max()),
            "note": "Winsorized 1/99 in Step 6 per Campello Table 1 note "
                    "VERBATIM ('All variables are winsorized at the 1% "
                    "level.', paper L2527-2528). The prior 'NOT winsorized "
                    "(paper Table 8 does not)' claim was FALSE and was the "
                    "cash-DiD non-replication root cause (A6/A7, "
                    "systematic-debugging).",
        },
    }

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = OUT_BASE / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "cash_did.json").write_text(json.dumps(out, indent=2,
                                                      default=str))
    (out_dir / "metadata.json").write_text(json.dumps({
        "step": "7 — real cash DiD eq-14 (Campello 2022 JFQA Table 8 col 1)",
        "step6_input": str(s6),
        "primary_spec": "FIRM-controls-only (tobinq/cf/logassets/"
                        "salesgrowth/stockret, all t-1) on the full "
                        "2010Q1-2016Q4 eq-14 panel (A4 correction; N from "
                        "fit, not asserted). Macro absorbed by "
                        "FIC100xcal_yr_qtr FE (not regressors). EPS excluded "
                        "from primary (treatment-correlated IBES-link gap, "
                        "4-qtr-era 21.9pp — recompute on full panel A6/A7); "
                        "with-EPS = sensitivity.",
        "deviations_logged": [
            "macro (5) absorbed by industry x time FE, NOT explicit "
            "regressors — Campello-faithful per Table 8; root cause "
            "_diag_s7_rank.py (time-only vars collinear with the "
            "FIC100 x cal_yr_qtr FE on the full 2010Q1-2016Q4 panel)",
            "EPS dropped from primary (treatment-correlated link selection); "
            "with-EPS = sensitivity per paper §IV.C.3 text",
            "PhillyFed national LEI does not exist -> ADS substitute, now "
            "inside the FE; drop-ADS sensitivity NOT applicable at this FE "
            "structure (flagged for future work if ever needed)",
            "A4 correction (2026-05-16): the prior 4-quarter restriction "
            "was a bug; eq-14 is the full 2010Q1-2016Q4 panel + POST dummy. "
            "Any residual attenuation vs +0.231*** (cross-checked vs the "
            "F1D eq-14 anchor +0.1321, NS, N 17,176) is the OBSERVED "
            "non-replication, reported honestly — NOT 'structurally "
            "expected, do not chase' (that was the 4-qtr-bug artifact, "
            "A8) and NOT a license to change the recipe.",
        ],
        "fit_did_cluster_wiring_caveat": "fit_did cluster flags assume "
            "default entity_col='gvkey'/time_col='cal_yr_qtr'; Step 7 uses "
            "defaults so double-cluster fires correctly. Verify 'cov' "
            "string reads clustered in cash_did.json.",
        "cluster": "double-clustered firm + cal_yr_qtr (PanelOLS clustered)",
        "r2_convention": "paper Table 8 R2=0.21; compare to r2.within "
                         "(absorbed-FE comparand); all flavors reported",
        "integrity_check": str(s6.parent / "eps_missing_integrity.json"),
        "out_of_scope": "NWC, profits, continuous-beta^UK, commit — separate "
                        "requests (strict-sequential HARD-STOP).",
    }, indent=2, default=str))

    def row(tag, r):
        rr = r["r2"]
        print(f"  {tag:<20s} d={r['delta_hat']:+.4f}  se={r['se']:.4f}  "
              f"t={r['tstat']:+.2f}  p={r['pvalue']:.3f}  "
              f"N={r['n_obs']:,} f={r['n_firms']}  "
              f"R2w={rr['within']:.3f}  [{r['cov']}]")

    print("\nRESULT — eq-14 cash DiD")
    print("  paper anchor : delta=+0.231***  SE=0.059  N=17,170  R2=0.21")
    print("  F1D x-anchor : delta=+0.1321 (NS p_one .141)  SE=0.123  "
          "N=17,176  (eq-14-faithful cross-check, ~57%)")
    row("PRIMARY firm5", primary)
    row("sens_with_eps", sens_with_eps)
    row("diag_sample_eff", diag_sample_effect)
    print(f"\n  CASH_DV (winsorized 1/99 @ Step 6) "
          f"p1={cash.quantile(.01):+.3f} "
          f"p50={cash.quantile(.5):+.3f} p99={cash.quantile(.99):+.3f} "
          f"min={cash.min():+.3f} max={cash.max():+.3f}")
    print(f"\n  -> {out_dir / 'cash_did.json'}")
    print(f"  -> {out_dir / 'metadata.json'}")
    print("\n  REBUILD COMPLETE. HARD-STOP: NWC/profits/continuous-beta^UK "
          "+ commit = separate requests.")


if __name__ == "__main__":
    main()
