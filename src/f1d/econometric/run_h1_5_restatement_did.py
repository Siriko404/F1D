#!/usr/bin/env python3
"""
================================================================================
STAGE 4: H1.5 Chen Restatement DiD on Cash + Speech (Chen 2017 JAAF verbatim)
================================================================================
ID: econometric/run_h1_5_restatement_did
Description: PSM-matched DiD design exploiting firm-event idiosyncratic
             restatements 1997-Jun2006 as plausibly-exogenous precautionary-cash
             shocks per Chen-Cheng-Lin-Tang 2017 JAAF Vol 32(2) pp.286-326.
             Tests:

             1. Cash response: matched IRREG firm vs control × POST → cash UP
                per spec C2 verbatim with firm FE + matched-pair × year double-cluster SE
                (Gow-Ormazabal-Taylor 2010).
             2. Speech response: same matched-pair × POST on UncResCEO_c
                (F1D speech-extension novelty per Sina Q3 lock).
             3. PS_DEMAND HIGH/LOW partitions: Cash + Speech × HIGH/LOW
                — Story B precautionary-savings demand mechanism per spec C7
                (Duchin 2010 framework; F1D adds speech).

POST = (fyear > event_year) for matched (gvkey, fyear) rows in window
[event-3, event-1] ∪ [event+1, event+3]. Year 0 (event_year) EXCLUDED per spec C2.

18 cells per variant × 3 variants (A/B/C) = 54 cells total.
Block layout per variant (per audit M1 — per-cell + Wald-difference, NOT interaction-term):
    Block 1 (cols 1-3): DV=Cash — restatement-only POST + control-only POST + Wald-diff
    Block 2 (cols 4-6): DV=Speech — same per-cell+Wald structure
    Block 3 (cols 7-9): DV=Cash × PS_DEMAND HIGH partition
    Block 4 (cols 10-12): DV=Cash × PS_DEMAND LOW partition
    Block 5 (cols 13-15): DV=Speech × PS_DEMAND HIGH partition
    Block 6 (cols 16-18): DV=Speech × PS_DEMAND LOW partition

Tail directions:
    Restatement on Cash:                       one-tail POS (precautionary cash)
    Restatement on UncResCEO_c:                one-tail POS (uncertainty speech)
    PS_DEMAND HIGH × Restatement (Cash+Speech): one-tail POS (precaution channel)
    PS_DEMAND LOW × Restatement (Cash+Speech):  one-tail POS but expected ~0

Anchor: Chen-Cheng-Lin-Tang (2017) JAAF verbatim. Spec-locked at
    tmp/3did_replication_v2_2026_05_08.md Section C (lines 1450-1700).
Plan: ~/.claude/plans/staggered-firm-cascade.md (v2 2026-05-09 ratified).
Audit: tmp/boasiako_chen_plan_audit_findings_2026_05_09.md (af9bcfb73742b167c).

CRITICAL DESIGN POINTS:
1. matched_pair_year cluster SE per spec C4 verbatim "we cluster standard errors
   at both the matched pair (of the restatement and control firms) and year levels
   (Gow, Ormazabal, & Taylor, 2010)". Implementation: clusters_col="matched_pair_year"
   baked DIRECTLY into Brexit-cloned _fit_one() per audit M0a (Trump _fit_one
   refactor was DROPPED v2; new clones each bake clusters_col).
2. v2 audit M1: per-cell+Wald-diff structure (NOT interaction-term DiD).
   For each block, run 3 regressions:
     (1) Restatement-only subsample: DV ~ POST + controls + firm FE
     (2) Control-only subsample:     DV ~ POST + controls + firm FE
     (3) Combined sample:            DV ~ Treated + POST + Treated×POST + controls + firm FE
                                      Treated×POST coef = Wald-diff
3. v2 audit M5: M5 pre-flight for Variant B post-PSM yielded:
     CASH coverage [event-3,-1] AND [+1,+3]: 80 firms (BELOW 150 threshold)
     SPEECH coverage:                         17 firms (severely BELOW threshold)
     Sina ratified PROCEED 2026-05-09: ship 18-cell runner with low-power caveat.
4. v2 audit M0a: clusters_col baked into _fit_one() clone-time (NOT cross-cutting refactor).
5. Cash DV = CHE/AT (Chen verbatim — distinct from Boasiako's BoY-scaled CHE/AT_lag).
6. UncResCEO_c quarterly → annualized via groupby(['gvkey','fyear']).mean()
   BEFORE matched-pair merge (advisor 2026-05-09 nit).

Inputs:
    - 5 Chen Phase 1C builders: chen_psm_matching, chen_baseline_controls,
      chen_industry_cf_vol_ff48, chen_ps_demand, chen_restatement_treatment
    - inputs/Compustat_Annual/compustat_annual.csv via _compustat_annual_reader
    - outputs/econometric/ceo_clarity_extended/<latest>/ceo_clarity_residual.parquet
    - outputs/variables/h1_cash_holdings/<latest>/h1_cash_holdings_panel.parquet
      (for ff12_code only; UncResCEO comes from ceo_clarity_residual + start_date→fyear)

Outputs:
    - outputs/econometric/h1_5_restatement_did/<timestamp>/
================================================================================
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared._compustat_annual_reader import read_compustat_annual
from f1d.shared.variables.chen_baseline_controls import ChenBaselineControlsBuilder
from f1d.shared.variables.chen_industry_cf_vol_ff48 import ChenIndustryCFVolFF48Builder
from f1d.shared.variables.chen_ps_demand import ChenPSDemandBuilder
from f1d.shared.variables.chen_psm_matching import ChenPSMMatchingBuilder


# ==============================================================================
# Configuration
# ==============================================================================

POST_VAR = "POST"
TREATED_VAR = "Treated"
INTERACTION_VAR = "Treated_x_POST"

# 8 baseline controls per Chen spec C3 (firm FE absorbs some)
FIRM_CONTROLS: List[str] = ["q", "size", "cf", "nwc", "lev", "nseg", "age"]
INDUSTRY_CONTROL = "sigma_chen"
ALL_CONTROLS = FIRM_CONTROLS + [INDUSTRY_CONTROL]

# Window per spec C2: [event-3, event-1] ∪ [event+1, event+3]
PRE_WINDOW = (-3, -1)
POST_WINDOW = (1, 3)

# Loading window (covers earliest 1997 event - 3 = 1994; latest 2006 event + 3 = 2009)
LOAD_FYEAR_MIN = 1994
LOAD_FYEAR_MAX = 2009

# v2 audit M0a: bake clusters_col into NEW runner _fit_one() clone (NOT Trump refactor)
CLUSTERING: Dict[str, Any] = {"clusters_col": "matched_pair_year"}

# Classifier variants per Sina Q1 lock (3-variant sensitivity)
VARIANTS = ["A", "B", "C"]

SUITE_ID = "H1.5.restatement_did"
SUITE_DIR_NAME = "h1_5_restatement_did"
SUITE_TITLE = (
    "Chen Restatement DiD: PSM-Matched Firm-Event Cash Holdings + "
    "CEO Speech Uncertainty (Chen-Cheng-Lin-Tang 2017 JAAF verbatim, 3-variant sensitivity)"
)
SUITE_LABEL = "tab:h1_5_restatement_did"


# ==============================================================================
# Data Loading — UncResCEO_c annualized per advisor nit
# ==============================================================================

def load_uncres_ceo_annual(root: Path) -> pd.DataFrame:
    """Load UncResCEO from ceo_clarity_residual; aggregate to (gvkey, fyear)."""
    rdir = get_latest_output_dir(
        root / "outputs" / "econometric" / "ceo_clarity_extended",
        required_file="ceo_clarity_residual.parquet",
    )
    res = pd.read_parquet(rdir / "ceo_clarity_residual.parquet",
                          columns=["gvkey", "start_date", "UncResCEO"])
    res["start_date"] = pd.to_datetime(res["start_date"])
    res["fyear"] = res["start_date"].dt.year.astype(int)
    res["gvkey"] = res["gvkey"].astype(str).str.zfill(6)

    # Center UncResCEO over Chen window (1997-2009 covering events 1997-2006 ± 3)
    win = res[res["fyear"].between(LOAD_FYEAR_MIN, LOAD_FYEAR_MAX)]
    mu = win["UncResCEO"].mean(skipna=True)
    res["UncResCEO_c"] = res["UncResCEO"] - mu

    annual = (
        res.groupby(["gvkey", "fyear"])["UncResCEO_c"]
        .mean()
        .reset_index()
    )
    return annual


# ==============================================================================
# Pair-firm-year panel assembly
# ==============================================================================

def assemble_pair_panel(root: Path, classifier_variant: str) -> pd.DataFrame:
    """Build (gvkey, fyear) pair-firm-year panel for given classifier variant.

    Steps:
        1. Load PSM matched pairs (variant-specific).
        2. For each pair-firm: expand to fyears [event-3,-1] ∪ [event+1,+3].
        3. Merge Compustat (CHE/AT for cash DV).
        4. Merge controls + SIGMA + PS_DEMAND.
        5. Merge UncResCEO_c (annualized).
        6. Construct POST = (fyear > event_year) and matched_pair_year cluster ID.
    """
    print(f"\n  --- Variant {classifier_variant}: Pair-firm-year panel ---")
    years = range(LOAD_FYEAR_MIN, LOAD_FYEAR_MAX + 1)

    # 1. PSM matched pairs
    psm = ChenPSMMatchingBuilder(
        {"classifier_variant": classifier_variant}
    ).build(years=range(1997, 2007), root_path=root).data
    matched = psm[psm["in_psm_sample"] == 1].copy()
    matched["gvkey"] = matched["gvkey"].astype(str).str.zfill(6)
    matched["match_partner_gvkey"] = matched["match_partner_gvkey"].astype(str).str.zfill(6)

    # Build pair_id: shared key per (treated, control, event_year) pair.
    # Convention: pair_id = treated_gvkey + "_" + event_year (treated rows define the pair).
    treated_only = matched[matched["treated"] == 1].copy()
    pair_lookup: Dict[Tuple[str, int], str] = {}
    for _, t in treated_only.iterrows():
        gv_t = t["gvkey"]
        gv_c = t["match_partner_gvkey"]
        ey = int(t["event_year"])
        pid = f"{gv_t}_{ey}"
        pair_lookup[(gv_t, ey)] = pid
        pair_lookup[(gv_c, ey)] = pid

    matched["pair_id"] = matched.apply(
        lambda r: pair_lookup.get((r["gvkey"], int(r["event_year"]))),
        axis=1,
    )
    matched = matched.dropna(subset=["pair_id"])
    print(f"  PSM matched pairs: {len(matched)} rows ({(matched.treated==1).sum()} treated)")

    # 2. Expand each pair-firm to fyears in [event-3,-1] ∪ [event+1,+3]
    rows = []
    for _, m in matched.iterrows():
        gv = m["gvkey"]
        ey = int(m["event_year"])
        pid = m["pair_id"]
        t_flag = int(m["treated"])
        # Pre-window
        for off in range(PRE_WINDOW[0], PRE_WINDOW[1] + 1):
            rows.append({"gvkey": gv, "fyear": ey + off, "event_year": ey,
                         "pair_id": pid, "Treated": t_flag, "POST": 0})
        # Post-window (year 0 excluded per spec)
        for off in range(POST_WINDOW[0], POST_WINDOW[1] + 1):
            rows.append({"gvkey": gv, "fyear": ey + off, "event_year": ey,
                         "pair_id": pid, "Treated": t_flag, "POST": 1})

    pair_panel = pd.DataFrame(rows)
    print(f"  Pair-firm-year expanded: {len(pair_panel)} rows ({pair_panel.gvkey.nunique()} gvkeys × ~6 fyears)")

    # 3. Merge Compustat for Cash DV (CHE/AT) per Chen verbatim
    comp = read_compustat_annual(
        path=root / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
        cols=["gvkey", "datadate", "sic", "loc", "at", "che"],
        years=years,
        us_only=True,
    )
    comp = comp.dropna(subset=["at"]).copy()
    comp = comp[comp["at"] > 0]
    comp["cash"] = comp["che"].fillna(0) / comp["at"]
    comp = comp.sort_values(["gvkey", "fyear", "datadate"]).drop_duplicates(
        ["gvkey", "fyear"], keep="last"
    )
    pair_panel = pair_panel.merge(comp[["gvkey", "fyear", "cash"]], on=["gvkey", "fyear"], how="left")
    print(f"  After Cash DV merge: {pair_panel['cash'].notna().sum()} rows with cash")

    # 4. Merge 7 baseline firm-controls (Chen C3) + SIGMA (Chen C4 via FF48)
    ctrl = ChenBaselineControlsBuilder().build(years=range(1997, 2007), root_path=root).data
    pair_panel = pair_panel.merge(
        ctrl[["gvkey", "fyear"] + FIRM_CONTROLS],
        on=["gvkey", "fyear"], how="left",
    )

    # SIGMA via FF48
    from f1d.shared.variables.ff48_industry_classifier import FF48IndustryClassifierBuilder
    ff48 = FF48IndustryClassifierBuilder().build(years=years, root_path=root).data
    pair_panel = pair_panel.merge(ff48[["gvkey", "fyear", "ff48_code"]],
                                   on=["gvkey", "fyear"], how="left")
    sigma = ChenIndustryCFVolFF48Builder().build(years=range(1997, 2007), root_path=root).data
    pair_panel = pair_panel.merge(sigma[["ff48_code", "fyear", "sigma_chen"]],
                                   on=["ff48_code", "fyear"], how="left")

    # 5. Merge PS_DEMAND for HIGH/LOW partition (assigned at event_year of treated firm)
    # Convention: each pair takes treated firm's PS_DEMAND at event_year as the pair-level value.
    ps_demand = ChenPSDemandBuilder().build(years=range(1997, 2007), root_path=root).data
    # Per pair: treated firm's PS_DEMAND at event_year
    treated_ps = pair_panel[pair_panel["Treated"] == 1].drop_duplicates(["pair_id"])[
        ["pair_id", "ff48_code", "event_year"]
    ].copy()
    treated_ps = treated_ps.rename(columns={"event_year": "fyear"})
    treated_ps = treated_ps.merge(
        ps_demand[["ff48_code", "fyear", "ps_demand"]],
        on=["ff48_code", "fyear"], how="left",
    )[["pair_id", "ps_demand"]].rename(columns={"ps_demand": "pair_ps_demand"})
    pair_panel = pair_panel.merge(treated_ps, on="pair_id", how="left")
    # HIGH = top half by median; LOW = bottom half
    median_ps = pair_panel["pair_ps_demand"].median()
    pair_panel["ps_demand_high"] = (pair_panel["pair_ps_demand"] >= median_ps).astype(int)
    print(f"  PS_DEMAND median: {median_ps:.3f}; HIGH pairs: "
          f"{pair_panel.loc[pair_panel.Treated==1, 'ps_demand_high'].sum()}, "
          f"LOW pairs: {(pair_panel.loc[pair_panel.Treated==1, 'ps_demand_high'] == 0).sum()}")

    # 6. Merge UncResCEO_c (annualized)
    uc = load_uncres_ceo_annual(root)
    pair_panel = pair_panel.merge(uc, on=["gvkey", "fyear"], how="left")
    print(f"  After UncResCEO_c merge: {pair_panel['UncResCEO_c'].notna().sum()} rows with speech")

    # 7. matched_pair_year cluster
    pair_panel["matched_pair_year"] = (
        pair_panel["pair_id"].astype(str) + "_" + pair_panel["fyear"].astype(str)
    )

    # Drop rows missing fyear info (e.g., out-of-window)
    pair_panel = pair_panel.dropna(subset=["fyear"]).copy()
    pair_panel["fyear"] = pair_panel["fyear"].astype(int)

    # Winsorize cash + UncResCEO_c at 1% pooled per Chen convention
    for col in ["cash", "UncResCEO_c"]:
        if col in pair_panel.columns:
            v = pair_panel[col]
            if v.notna().sum() >= 10:
                p1, p99 = v.quantile(0.01), v.quantile(0.99)
                pair_panel[col] = pair_panel[col].clip(lower=p1, upper=p99)

    return pair_panel.reset_index(drop=True)


# ==============================================================================
# Regression — _fit_one with clusters_col baked in (audit M0a)
# ==============================================================================

def _fit_one(
    df: pd.DataFrame,
    dv: str,
    headline_term: str,
    extra_terms: List[str],
    extra_controls: List[str],
) -> Tuple[Optional[Any], Dict[str, Any]]:
    """Fit one Chen regression spec. Firm FE only (per spec C4); matched_pair_year cluster.

    Args:
        df: panel DataFrame with required columns + 'matched_pair_year'.
        dv: dependent variable column.
        headline_term: variable for which we report β/SE/t/p (e.g., POST or Treated_x_POST).
        extra_terms: additional regressors (e.g., [Treated, POST] for Wald-diff regression).
        extra_controls: control vars to include in exog.

    Returns:
        (PanelResults or None, meta dict)
    """
    needed = [dv, headline_term] + extra_terms + extra_controls + ["gvkey", "fyear", "matched_pair_year"]
    df = df.dropna(subset=needed).copy()
    if len(df) < 30:
        return None, {"n_obs": int(len(df)), "skipped": "too few obs"}

    # Pre-extract cluster column BEFORE set_index
    cluster_series = df["matched_pair_year"].astype(str).copy()

    # Pandas index: (gvkey, fyear)
    df = df.sort_values(["gvkey", "fyear"]).reset_index(drop=True)
    cluster_series = cluster_series.reset_index(drop=True)
    df_idx = df.set_index(["gvkey", "fyear"])
    cluster_series.index = df_idx.index

    exog_cols = [headline_term] + extra_terms + extra_controls
    exog = df_idx[exog_cols].astype(float)

    # Build fit_kwargs with clusters baked in (audit M0a)
    fit_kwargs: Dict[str, Any] = {"cov_type": "clustered"}
    if CLUSTERING.get("clusters_col") == "matched_pair_year":
        fit_kwargs["clusters"] = pd.DataFrame(
            {"matched_pair_year": cluster_series.values}, index=df_idx.index
        )

    # Firm FE only per spec C4 ("we include firm fixed effects (a_i)")
    try:
        model = PanelOLS(
            dependent=df_idx[dv],
            exog=exog,
            entity_effects=True,   # firm FE
            drop_absorbed=True,
            check_rank=False,
        )
        result = model.fit(**fit_kwargs)
    except Exception as e:
        return None, {"n_obs": int(len(df)), "skipped": f"fit failed: {e}"}

    meta: Dict[str, Any] = {
        "dv": dv,
        "headline": headline_term,
        "n_obs": int(result.nobs),
        "r2": float(result.rsquared),
        "n_pairs": int(df["matched_pair_year"].nunique()),
    }
    if headline_term in result.params.index:
        beta = float(result.params[headline_term])
        se = float(result.std_errors[headline_term])
        t = float(result.tstats[headline_term])
        p_two = float(result.pvalues[headline_term])
        meta.update({
            "beta": beta, "se": se, "t": t,
            "p_two": p_two,
            "p_one": (p_two / 2) if beta >= 0 else 1 - (p_two / 2),
        })
    else:
        meta.update({"beta": np.nan, "se": np.nan, "t": np.nan, "p_two": np.nan, "p_one": np.nan,
                     "skipped": "headline absorbed by FE"})
    return result, meta


# ==============================================================================
# Per-cell + Wald-diff block runner (audit M1)
# ==============================================================================

def _run_block(
    panel: pd.DataFrame,
    dv: str,
    block_label: str,
    col_offset: int,
    sample_filter: Optional[Dict[str, int]] = None,
) -> List[Dict[str, Any]]:
    """Run 3-cell per-block: restatement-only POST + control-only POST + combined Wald-diff.

    Args:
        panel: full pair-firm-year panel.
        dv: 'cash' or 'UncResCEO_c'.
        block_label: name for diagnostics.
        col_offset: starting col number (e.g., 1, 4, 7, ...).
        sample_filter: optional pre-filter, e.g., {"ps_demand_high": 1}.
    """
    results: List[Dict[str, Any]] = []
    sub = panel.copy()
    if sample_filter:
        for k, v in sample_filter.items():
            sub = sub[sub[k] == v]

    if len(sub) < 30:
        for i, label in enumerate(["restatement_only", "control_only", "wald_diff"], start=col_offset):
            results.append({
                "model": None,
                "meta": {"col": i, "block": block_label, "subblock": label,
                         "dv": dv, "n_obs": int(len(sub)),
                         "skipped": "block sample <30",
                         "beta": np.nan, "se": np.nan, "t": np.nan, "p_two": np.nan, "p_one": np.nan},
            })
        return results

    # Cell 1: Restatement-only subsample, POST coef
    treated_sub = sub[sub["Treated"] == 1].copy()
    model_t, meta_t = _fit_one(
        treated_sub, dv=dv, headline_term=POST_VAR,
        extra_terms=[], extra_controls=ALL_CONTROLS,
    )
    meta_t.update({"col": col_offset, "block": block_label, "subblock": "restatement_only"})
    results.append({"model": model_t, "meta": meta_t})
    _print_cell(meta_t)

    # Cell 2: Control-only subsample, POST coef
    control_sub = sub[sub["Treated"] == 0].copy()
    model_c, meta_c = _fit_one(
        control_sub, dv=dv, headline_term=POST_VAR,
        extra_terms=[], extra_controls=ALL_CONTROLS,
    )
    meta_c.update({"col": col_offset + 1, "block": block_label, "subblock": "control_only"})
    results.append({"model": model_c, "meta": meta_c})
    _print_cell(meta_c)

    # Cell 3: Combined Wald-diff (Treated×POST interaction)
    sub["Treated_x_POST"] = sub["Treated"].astype(int) * sub["POST"].astype(int)
    model_w, meta_w = _fit_one(
        sub, dv=dv, headline_term=INTERACTION_VAR,
        extra_terms=[POST_VAR],  # Treated absorbed by firm FE
        extra_controls=ALL_CONTROLS,
    )
    meta_w.update({"col": col_offset + 2, "block": block_label, "subblock": "wald_diff"})
    results.append({"model": model_w, "meta": meta_w})
    _print_cell(meta_w)

    return results


def run_18_cells_for_variant(panel: pd.DataFrame, variant: str) -> List[Dict[str, Any]]:
    """18 cells per variant = 6 blocks × 3 sub-cells (per-cell + Wald-diff)."""
    print(f"\n  --- Variant {variant}: 6 blocks × 3 sub-cells = 18 cells ---")
    out: List[Dict[str, Any]] = []
    out.extend(_run_block(panel, dv="cash", block_label="cash_baseline", col_offset=1))
    out.extend(_run_block(panel, dv="UncResCEO_c", block_label="speech_baseline", col_offset=4))
    out.extend(_run_block(panel, dv="cash", block_label="cash_ps_high",
                          col_offset=7, sample_filter={"ps_demand_high": 1}))
    out.extend(_run_block(panel, dv="cash", block_label="cash_ps_low",
                          col_offset=10, sample_filter={"ps_demand_high": 0}))
    out.extend(_run_block(panel, dv="UncResCEO_c", block_label="speech_ps_high",
                          col_offset=13, sample_filter={"ps_demand_high": 1}))
    out.extend(_run_block(panel, dv="UncResCEO_c", block_label="speech_ps_low",
                          col_offset=16, sample_filter={"ps_demand_high": 0}))
    for r in out:
        r["meta"]["variant"] = variant
    return out


# ==============================================================================
# Reporting
# ==============================================================================

def _print_cell(meta: Dict[str, Any]) -> None:
    msg = (
        f"  Col ({meta.get('col', '?'):>2}) "
        f"DV={meta.get('dv', '?'):14s} "
        f"head={meta.get('headline', '?'):20s} "
        f"sub={meta.get('subblock', '?'):20s} "
        f"n={meta.get('n_obs', 0):>5,} "
        f"beta={meta.get('beta', np.nan):+.4f} "
        f"p_one={meta.get('p_one', np.nan):.3f}"
    )
    if meta.get("skipped"):
        msg += f"  SKIPPED({meta['skipped']})"
    print(msg)


def _sig_stars(p: float, beta: float) -> str:
    """One-tailed POS sig stars (only fire if beta >= 0)."""
    if np.isnan(p) or np.isnan(beta) or beta < 0:
        return ""
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


def write_outputs(results: List[Dict[str, Any]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = [r["meta"] for r in results]
    diag = pd.DataFrame(rows)
    diag.to_csv(out_dir / "model_diagnostics.csv", index=False)
    print(f"  Saved: model_diagnostics.csv ({len(diag)} rows)")

    # Markdown summary
    lines = [f"# H1.5 Chen Restatement DiD — 54 Cells (18 per variant × 3)", ""]
    lines.append(f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("**Sina decisions ratified 2026-05-09 (plan v2):**")
    lines.append("- Q1 Chen classifier: 3-variant sensitivity (A/B/C) — this runner ships all 3")
    lines.append("- Q3 Speech channel: INCLUDED on UncResCEO_c (Story B novelty)")
    lines.append("- M5 pre-flight Variant B: Cash n=80, Speech n=17 — BELOW 150 threshold; Sina ratified PROCEED with low-power caveat")
    lines.append("")
    lines.append("**Per-cell + Wald-diff structure (audit M1):**")
    lines.append("- Sub-cell 1: restatement-only subsample, POST coef")
    lines.append("- Sub-cell 2: control-only subsample, POST coef")
    lines.append("- Sub-cell 3: combined sample, Treated×POST coef (this IS the Wald-diff)")
    lines.append("")
    lines.append("| variant | col | block | subblock | dv | n_obs | n_pairs | beta | p_one | sig |")
    lines.append("|---------|-----|-------|----------|----|-------|---------|------|-------|-----|")
    for r in results:
        m = r["meta"]
        sig = _sig_stars(m.get("p_one", np.nan), m.get("beta", 0))
        lines.append(
            f"| {m.get('variant', '?')} | {m.get('col', '?')} | {m.get('block', '?')} | "
            f"{m.get('subblock', '?')} | {m.get('dv', '?')} | "
            f"{m.get('n_obs', 0):,} | {m.get('n_pairs', 0):,} | "
            f"{m.get('beta', np.nan):+.4f} | {m.get('p_one', np.nan):.3f} | {sig} |"
        )
    (out_dir / "report_step4_H1_5_restatement_did.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print(f"  Saved: report_step4_H1_5_restatement_did.md")

    suite_spec = {
        "suite_id": SUITE_ID,
        "dir_name": SUITE_DIR_NAME,
        "title": SUITE_TITLE,
        "label": SUITE_LABEL,
        "n_cells": len(results),
        "n_variants": len(VARIANTS),
        "n_cells_per_variant": 18,
        "clustering": CLUSTERING,
        "fe": "firm-only (entity_effects=True)",
        "audit_M1_structure": "per-cell + Wald-diff (NOT interaction-term DiD)",
        "audit_M5_preflight": "Variant B post-PSM Cash n=80, Speech n=17 (BELOW 150 threshold; Sina ratified PROCEED with low-power caveat)",
        "blocks_per_variant": {
            "block_1_cash_baseline": "cols 1-3",
            "block_2_speech_baseline": "cols 4-6",
            "block_3_cash_ps_high": "cols 7-9",
            "block_4_cash_ps_low": "cols 10-12",
            "block_5_speech_ps_high": "cols 13-15",
            "block_6_speech_ps_low": "cols 16-18",
        },
    }
    (out_dir / f"suite_spec_{SUITE_ID}.json").write_text(json.dumps(suite_spec, indent=2))
    print(f"  Saved: suite_spec_{SUITE_ID}.json")


# ==============================================================================
# Main
# ==============================================================================

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H1.5 Chen Restatement DiD (Cash + Speech + PS_DEMAND HIGH/LOW)"
    )
    parser.add_argument("--variant", choices=["A", "B", "C", "all"], default="all",
                        help="Classifier variant (default: all 3)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Build panel + check counts; skip regressions")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_arguments()
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / SUITE_DIR_NAME / timestamp

    variants_to_run = [args.variant] if args.variant != "all" else VARIANTS

    print("=" * 80)
    print("STAGE 4: H1.5 CHEN RESTATEMENT DiD ON CASH + SPEECH (PSM-MATCHED)")
    print("=" * 80)
    print(f"Timestamp:  {timestamp}")
    print(f"Output:     {out_dir}")
    print(f"Variants:   {variants_to_run}")
    print(f"Cells:      18 per variant × {len(variants_to_run)} = {18 * len(variants_to_run)}")
    print(f"FE:         firm-only (entity_effects=True)")
    print(f"Clustering: {CLUSTERING}  (matched_pair_year per Gow 2010)")
    print(f"Audit M1:   per-cell + Wald-diff (NOT interaction-term)")
    print(f"Audit M5:   Variant B pre-flight Cash n=80 / Speech n=17 (BELOW 150 — Sina PROCEED)")
    print()

    all_results: List[Dict[str, Any]] = []
    for variant in variants_to_run:
        panel = assemble_pair_panel(root, variant)
        if args.dry_run:
            print(f"  Variant {variant}: panel built ({len(panel)} rows); dry-run skip regressions.")
            continue
        results = run_18_cells_for_variant(panel, variant)
        all_results.extend(results)

    if args.dry_run:
        return 0

    print(f"\n  --- Writing outputs to {out_dir} ---")
    write_outputs(all_results, out_dir)

    elapsed = (datetime.now() - t0).total_seconds()
    print(f"\n=== DONE in {elapsed:.1f}s ({len(all_results)} cells) ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
