"""Campello et al. (2022 JFQA) replication — STEP 5: eq-14 DiD estimator.

From-scratch rebuild. Builds ONLY the eq-14 estimating machinery and PROVES
it on a planted-delta synthetic outcome. NO cash DV (Step 7), NO real
controls list (Step 6), NO industry DEFINITION (Step 6 — caller-injected),
NO clustered SE (Step 6). NO comparison to any prior F1D output. Produces no
new data — just a verified estimator + a synthetic-validation proof.

Authoritative spec — §IV.C.3 "Empirical Model" (PDF p.19 / journal p.3196),
verbatim from the curated extraction tmp/campello_v2/main_p19.txt:

  "This is equivalent to estimating the following model:
   (14) Y = alpha + delta*[POST . HIGH_UK_EXPOSURE]
            + theta*CONTROLS_{i,t-1}
            + SUM FIRM_i + SUM (INDUSTRY_j x QUARTER_t) + eps_{i,t}
   ... HIGH_UK_EXPOSURE is a dummy ... equals 1 if firm i is U.K.-exposed
   ... POST equals 1 if the time period is in the 2016:Q3-Q4 window."

Operationalization (primary-source-pinned, NOT a judgment call)
---------------------------------------------------------------
* The ONLY estimated treatment term is the product POST*HIGH (delta). There
  is NO standalone POST and NO standalone HIGH regressor: FIRM_i fixed
  effects absorb the firm-constant HIGH; INDUSTRY_jxQUARTER_t fixed effects
  absorb the time-only POST. Adding either lone term is mechanically
  collinear with the fixed effects -> fit_did REFUSES such a design.
* Firm FE        = PanelOLS entity_effects (entity = gvkey).
* IND_jxQTR_t FE = PanelOLS other_effects (one grouping = industry x qtr).
* SE             = plain OLS ('unadjusted') when cluster_cols=(); the
  double-clustered SE is wired in Step 6, not here.
* Industry DEFINITION is caller-injected (Step 5 does not pick FIC100 / FF /
  SIC — that is Step 6). The synthetic test uses a throwaway fake industry.

Step-5 verification = a STRONG synthetic test (advisor-specified): plant
delta PLUS the exact nuisance the FE must absorb (firm intercepts
correlated with HIGH, and ind x qtr shocks). The estimator passes only if it
recovers delta WITH the FE and is visibly biased WITHOUT firm FE.

Output
------
outputs/campello_rebuild/step5_did/<timestamp>/
    synthetic_validation.json   planted vs recovered delta, ablation, guards
    metadata.json               spec verbatim, scope, deferred, library

Run:  python scripts/campello_rebuild/step5_did.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from linearmodels.panel import PanelOLS

ROOT = Path(__file__).resolve().parents[2]
STEP4_BASE = ROOT / "outputs" / "campello_rebuild" / "step4_timeline"
OUT_BASE = ROOT / "outputs" / "campello_rebuild" / "step5_did"

# lone treatment/time names that must NEVER enter as standalone regressors
# (eq-14 is interaction-only; these are absorbed by the fixed effects).
_LONE_FORBIDDEN = {"post", "high", "high_beta_uk", "high_uk_exposure"}

DELTA_TRUE = 0.50  # planted DiD effect for the synthetic proof


def _abort(msg: str) -> None:
    print(f"\nABORT — {msg}")
    print("Step 5 estimator NOT verified. Resolve before proceeding.")
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


def fit_did(
    panel: pd.DataFrame,
    y_col: str,
    industry_col: str,
    *,
    high_col: str = "HIGH",
    post_col: str = "POST",
    entity_col: str = "gvkey",
    time_col: str = "cal_yr_qtr",
    control_cols: tuple[str, ...] = (),
    cluster_cols: tuple[str, ...] = (),
    use_firm_fe: bool = True,
) -> dict:
    """Estimate eq-14:  Y = a + d*[POST x HIGH] + th*CONTROLS
    + SUM FIRM + SUM (IND x QTR) + e.

    Returns {delta_hat, se, tstat, pvalue, n_obs, n_firms, n_indqtr_cells,
    library, cov}. `use_firm_fe=False` is the Step-5 ablation only.
    """
    # ---- interaction-only guard (documents the spec; not defensive bloat) -
    for c in control_cols:
        if c.strip().lower() in _LONE_FORBIDDEN:
            raise ValueError(
                f"eq-14 is interaction-only: lone '{c}' is mechanically "
                f"collinear with the fixed effects and must NOT be a "
                f"standalone regressor. Pass only the interaction + genuine "
                f"controls."
            )
    need = {entity_col, time_col, high_col, post_col, y_col, industry_col}
    missing = need - set(panel.columns)
    if missing:
        raise ValueError(f"panel missing required columns: {sorted(missing)}")

    df = panel.copy()
    df["_interaction"] = (df[post_col].astype(int)
                          * df[high_col].astype(int))
    # ind x qtr single grouping (absorbed as one effect, per spec).
    df["_indqtr"] = (df[industry_col].astype(str) + "|"
                     + df[time_col].astype(str)).astype("category").cat.codes

    df = df.set_index([entity_col, time_col])
    y = df[[y_col]]
    xcols = ["_interaction", *control_cols]
    X = df[xcols]

    mod = PanelOLS(
        y, X,
        entity_effects=bool(use_firm_fe),
        other_effects=df["_indqtr"],
    )
    if cluster_cols:
        res = mod.fit(cov_type="clustered",
                      cluster_entity=("gvkey" in cluster_cols),
                      cluster_time=(time_col in cluster_cols))
        cov = f"clustered{sorted(cluster_cols)}"
    else:
        res = mod.fit(cov_type="unadjusted")
        cov = "unadjusted (Step-6 wires clustered SE)"

    def _r2(attr: str) -> float:
        try:
            return float(getattr(res, attr))
        except Exception:
            return float("nan")

    return {
        "delta_hat": float(res.params["_interaction"]),
        "se": float(res.std_errors["_interaction"]),
        "tstat": float(res.tstats["_interaction"]),
        "pvalue": float(res.pvalues["_interaction"]),
        "n_obs": int(res.nobs),
        "n_firms": int(df.index.get_level_values(0).nunique()),
        "n_indqtr_cells": int(df["_indqtr"].nunique()),
        "r2": {
            "within": _r2("rsquared_within"),
            "between": _r2("rsquared_between"),
            "overall": _r2("rsquared_overall"),
            "inclusive": _r2("rsquared_inclusive"),
            "rsquared": _r2("rsquared"),
        },
        "firm_fe": bool(use_firm_fe),
        "library": "linearmodels.PanelOLS",
        "cov": cov,
    }


def _synthetic_proof() -> dict:
    """Advisor-specified STRONG test: plant delta + the nuisance the FE must
    absorb, on the real Step-4 panel skeleton."""
    s4 = _latest(STEP4_BASE, "panel.parquet", "step4_timeline.py")
    p = pq.read_table(
        s4, columns=["gvkey", "cal_yr_qtr", "HIGH_BETA_UK", "POST"]
    ).to_pandas()
    p["gvkey"] = p["gvkey"].astype(str)
    p["HIGH"] = p["HIGH_BETA_UK"].astype(int)
    p["POST"] = p["POST"].astype(int)

    rng = np.random.default_rng(0)
    firms = p["gvkey"].drop_duplicates()
    # fake_industry — THROWAWAY test fixture; NOT FIC100, NOT persisted.
    fake_ind = pd.Series(rng.integers(0, 12, len(firms)),
                         index=firms.values)
    p["fake_industry"] = p["gvkey"].map(fake_ind)

    # firm FE correlated with HIGH (the nuisance FE must soak up).
    high_by_firm = p.groupby("gvkey")["HIGH"].first()
    a_firm = 0.5 * high_by_firm + rng.normal(0, 0.5, len(high_by_firm))
    p["_a"] = p["gvkey"].map(a_firm)

    cell = p["fake_industry"].astype(str) + "|" + p["cal_yr_qtr"].astype(str)
    g_cell = pd.Series(rng.normal(0, 1.0, cell.nunique()),
                       index=cell.drop_duplicates().values)
    p["_g"] = cell.map(g_cell)
    p["_e"] = rng.normal(0, 1.0, len(p))

    p["Y"] = (DELTA_TRUE * p["POST"] * p["HIGH"]
              + p["_a"] + p["_g"] + p["_e"])

    with_fe = fit_did(p, "Y", "fake_industry", use_firm_fe=True)
    no_firm_fe = fit_did(p, "Y", "fake_industry", use_firm_fe=False)

    # (c) interaction-only guard must reject a lone-term design.
    try:
        fit_did(p, "Y", "fake_industry", control_cols=("POST",))
        guard_ok = False
    except ValueError:
        guard_ok = True

    err_fe = abs(with_fe["delta_hat"] - DELTA_TRUE)
    err_nofe = abs(no_firm_fe["delta_hat"] - DELTA_TRUE)
    rec_ok = err_fe < 0.15                       # (a) recovers with FE
    bias_ok = (err_nofe > 0.10) and (err_nofe > err_fe + 0.05)  # (b) ablation

    return {
        "delta_true": DELTA_TRUE,
        "with_FE": with_fe,
        "no_firm_FE_ablation": no_firm_fe,
        "err_with_FE": round(err_fe, 4),
        "err_no_firm_FE": round(err_nofe, 4),
        "test_a_recovers_with_FE": bool(rec_ok),
        "test_b_biased_without_firm_FE": bool(bias_ok),
        "test_c_lone_term_guard_rejects": bool(guard_ok),
        "all_pass": bool(rec_ok and bias_ok and guard_ok),
    }


def main() -> None:
    print("Campello replication — STEP 5  eq-14 DiD estimator\n")
    proof = _synthetic_proof()

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = OUT_BASE / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "synthetic_validation.json").write_text(
        json.dumps(proof, indent=2))

    metadata = {
        "step": "5 — eq-14 DiD estimator (Campello 2022 JFQA §IV.C.3)",
        "spec_verbatim": "Y = a + d*[POST.HIGH_UK_EXPOSURE] "
                         "+ th*CONTROLS_{i,t-1} + SUM FIRM_i "
                         "+ SUM (INDUSTRY_j x QUARTER_t) + eps  (eq.14)",
        "design": {
            "treatment_term": "ONLY the product POST*HIGH (delta). NO lone "
                              "POST, NO lone HIGH (absorbed by FE; fit_did "
                              "raises ValueError if a lone term is passed).",
            "firm_FE": "PanelOLS entity_effects (entity=gvkey)",
            "indqtr_FE": "PanelOLS other_effects (industry x cal_yr_qtr, "
                         "one absorbed grouping)",
            "SE": "unadjusted OLS when cluster_cols=(); clustered path "
                  "exists but is wired by Step 6, not exercised here",
        },
        "scope_deferred": {
            "industry_definition": "caller-injected; FIC100/FF/SIC choice "
                                   "= Step 6 (synthetic uses throwaway "
                                   "fake_industry, NOT persisted)",
            "controls_list": "Step 6 (5 macro + 5 firm lagged + 1Q-ahead "
                             "consensus EPS)",
            "clustered_SE": "Step 6 (double-cluster firm + cal-qtr)",
            "cash_DV": "Step 7 (CHE/lag(AT-CHE))",
        },
        "verification": "STRONG synthetic proof (advisor-specified): planted "
                        f"delta={DELTA_TRUE} + firm FE correlated with HIGH "
                        "+ ind x qtr shocks + noise; pass iff recovered WITH "
                        "FE and biased WITHOUT firm FE and lone-term guard "
                        "fires.",
        "library": "linearmodels.PanelOLS 7.0",
        "produces_no_new_data": True,
        "out_of_scope": "no real-Y regression, no cash, no controls, no "
                        "industry definition, no clustered SE — each a "
                        "future step (strict-sequential).",
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    a = proof["with_FE"]
    b = proof["no_firm_FE_ablation"]
    print("SYNTHETIC PROOF  (planted delta = 0.50)")
    print(f"  (a) WITH FE        delta_hat={a['delta_hat']:+.4f}  "
          f"se={a['se']:.4f}  err={proof['err_with_FE']}  "
          f"-> recovers: {proof['test_a_recovers_with_FE']}")
    print(f"  (b) NO firm FE     delta_hat={b['delta_hat']:+.4f}  "
          f"err={proof['err_no_firm_FE']}  "
          f"-> biased: {proof['test_b_biased_without_firm_FE']}")
    print(f"  (c) lone-term guard rejects design: "
          f"{proof['test_c_lone_term_guard_rejects']}")
    print(f"  n_obs={a['n_obs']:,}  n_firms={a['n_firms']:,}  "
          f"indxqtr cells={a['n_indqtr_cells']}")
    print(f"\n  ALL PASS: {proof['all_pass']}")
    print(f"  -> {out_dir / 'synthetic_validation.json'}")
    print(f"  -> {out_dir / 'metadata.json'}")
    if not proof["all_pass"]:
        _abort("synthetic proof FAILED — estimator not trustworthy.")
    print("\n  eq-14 estimator verified. Controls/SE = STEP 6, cash DV = "
          "STEP 7 (NOT built here).")


if __name__ == "__main__":
    main()
