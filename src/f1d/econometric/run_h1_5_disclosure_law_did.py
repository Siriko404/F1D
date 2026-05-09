#!/usr/bin/env python3
"""
================================================================================
STAGE 4: H1.5 Boasiako Disclosure Law DiD on Cash + Speech (Boasiako 2020 verbatim)
================================================================================
ID: econometric/run_h1_5_disclosure_law_did
Description: Difference-in-differences design exploiting state-staggered passage
             of data-breach disclosure laws 2002-2010 as plausibly-exogenous
             precautionary-cash shocks per Boasiako-O'Connor Keefe (2020) EFM
             Vol 27(3) pp.528-551. Tests:

             1. Cash response: Disclosure_Law(0/1)_{s,t} → cash holdings UP
                per spec §3.2 verbatim Eq (1) with state+year+industry+firm FE
                (varies by spec) and state-cluster SE.
             2. Speech response: same Disclosure_Law treatment on UncResCEO_c
                (F1D speech-extension novelty per Sina Q3 lock).
             3. Speech-channel partitions: Small/Young/Non-Div × Disclosure_Law
                on UncResCEO_c — Story B financial-constraint mechanism per
                spec §4.1 Table 4 (cash partitions; F1D reuses on speech).

POST is encoded INTO Disclosure_Law itself (Y+1 timing per spec §3.2 verbatim:
"Disclosure Law(0/1)_{s,t} is a dummy variable that switches to one the year
after the focal state passed the disclosure law"). No separate Post variable.

14 cells = 8 baseline (cash + speech × 4 FE) + 6 speech-channel (3 partitions × 2 FE).

Tail directions:
    Disclosure_Law on Cash:                  one-tail POS  (precautionary cash)
    Disclosure_Law on UncResCEO_c:           one-tail POS  (uncertainty speech)
    Partition × Disclosure_Law on UncResCEO_c: one-tail POS (constraint channel)

Anchor: Boasiako-O'Connor Keefe (2020) EFM verbatim. Spec-locked at
    tmp/3did_replication_v2_2026_05_08.md Section B (lines 957-1448).
Plan: ~/.claude/plans/staggered-firm-cascade.md (v2 2026-05-09 ratified).
Audit: tmp/boasiako_chen_plan_audit_findings_2026_05_09.md (af9bcfb73742b167c).

CRITICAL DESIGN POINTS:
1. State-cluster SE per spec §3.2 verbatim "We cluster standard errors by
   state, because the treatment is defined at the state level."
   Implementation: clusters_col="state" baked into Brexit-cloned _fit_one()
   per audit M0a (Trump _fit_one refactor was DROPPED v2; new clones each
   bake clusters_col directly).
2. v2 audit M7: us_only=True via _compustat_annual_reader (drops 17.4% non-US)
3. v2 audit P5: 4 never-treated states (AL/KY/NM/SD) encoded Disclosure_Law=0
4. v2 audit V1: Y+1 timing per spec §3.2 (NOT Table A1)
5. v2 audit V3: Industry CF Vol ≥3y obs floor
6. v2 audit M3: CF formula = (OIBDP-XINT-TXT-DVC)/AT (Bates 2009 interpretation)
7. NO $-filter beyond "drop negative/missing AT" (audit P12: Boasiako-spec ≠ Brexit's $10M)

Inputs:
    - outputs/variables/h1_cash_holdings/<latest>/h1_cash_holdings_panel.parquet
    - outputs/econometric/ceo_clarity_extended/<latest>/ceo_clarity_residual.parquet
    - inputs/Compustat_Annual/compustat_annual.csv via _compustat_annual_reader
    - 4 Boasiako Phase 1A builder outputs:
        boasiako_disclosure_law_treatment + boasiako_eq1_controls +
        boasiako_industry_cf_vol + ff49_industry_classifier

Outputs:
    - outputs/econometric/h1_5_disclosure_law_did/<timestamp>/
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
from f1d.shared.variables.boasiako_disclosure_law_treatment import (
    BoasiakoDisclosureLawTreatmentBuilder,
)
from f1d.shared.variables.boasiako_eq1_controls import BoasiakoEq1ControlsBuilder
from f1d.shared.variables.boasiako_industry_cf_vol import BoasiakoIndustryCFVolBuilder
from f1d.shared.variables.ff49_industry_classifier import FF49IndustryClassifierBuilder


# ==============================================================================
# Configuration
# ==============================================================================

KEY_IV = "Disclosure_Law"  # treatment variable (already 0/1 with Y+1 timing baked in)

# 11 controls + IndCFVol per Boasiako spec §3.3 (Eq 1 controls + industry CF vol)
FIRM_CONTROLS: List[str] = [
    "firm_size", "firm_age", "book_leverage", "market_to_book", "cash_flow",
    "capital_expenditure", "acquisition_expenditure", "rd_expenditure", "nwc",
    "dividend_paying",
]
INDUSTRY_CONTROL = "industry_cf_vol"
ALL_CONTROLS = FIRM_CONTROLS + [INDUSTRY_CONTROL]

# Sample window per spec §3.1: 1997-2015 annual
WINDOW_FYEAR_MIN = 1997
WINDOW_FYEAR_MAX = 2015

# Crisis-exclusion window (Boasiako Table 2 col 4 sensitivity)
CRISIS_FYEARS = {2007, 2008, 2009}

# v2 audit M0a: bake clusters_col into NEW runner _fit_one() clone (NOT Trump refactor)
CLUSTERING: Dict[str, Any] = {"clusters_col": "state"}

# FE configurations per Boasiako Table 2:
#   - "industry_state_year" = ind+state+year FE (col 1 BASELINE β=+0.0076**)
#   - "firm_year" = firm+year FE (col 2)
#   - "industry_state_year_excl_ca" = col 1 sensitivity excl California
#   - "industry_state_year_excl_crisis" = col 1 sensitivity excl 2007-2009
FE_LADDER_CASH: List[str] = [
    "industry_state_year",
    "firm_year",
    "industry_state_year_excl_ca",
    "industry_state_year_excl_crisis",
]
# Speech reuses same 4 FE configs
FE_LADDER_SPEECH: List[str] = FE_LADDER_CASH
# Speech-channel partitions (Block 3): only first 2 FE configs (industry+state+year, firm+year)
FE_LADDER_CHANNEL: List[str] = ["industry_state_year", "firm_year"]

PARTITIONS = {
    "Small": "tercile_small",   # bottom tercile firm_size
    "Young": "tercile_young",   # bottom tercile firm_age
    "NonDiv": "non_dividend",   # dividend_paying == 0
}

SUITE_ID = "H1.5.disclosure_law_did"
SUITE_DIR_NAME = "h1_5_disclosure_law_did"
SUITE_TITLE = (
    "Boasiako Disclosure Law Difference-in-Differences: Cash Holdings + "
    "CEO Speech Uncertainty (Boasiako-O'Connor Keefe 2020 EFM verbatim)"
)
SUITE_LABEL = "tab:h1_5_disclosure_law_did"


# ==============================================================================
# Data Loading
# ==============================================================================

def load_h1_panel_to_annual(root: Path) -> pd.DataFrame:
    """Load h1_cash_holdings panel + UncResCEO; aggregate to (gvkey, fyear).

    Boasiako uses ANNUAL data; F1D's H1 panel is QUARTERLY (call-level).
    We aggregate UncResCEO_c per (gvkey, fyear) as MEAN across all calls in that
    fiscal year (proxy: calendar year). Firms with no calls in a given year are
    dropped from speech specs but kept for cash specs (which use Compustat fields
    and don't need the call panel).
    """
    pdir = get_latest_output_dir(
        root / "outputs" / "variables" / "h1_cash_holdings",
        required_file="h1_cash_holdings_panel.parquet",
    )
    panel_file = pdir / "h1_cash_holdings_panel.parquet"
    columns = ["file_name", "gvkey", "ff12_code", "start_date"]
    panel = pd.read_parquet(panel_file, columns=columns)
    panel["gvkey"] = panel["gvkey"].astype(str).str.zfill(6)
    panel["start_date"] = pd.to_datetime(panel["start_date"])
    panel["cal_year"] = panel["start_date"].dt.year

    # Merge UncResCEO residual (call-level)
    rdir = get_latest_output_dir(
        root / "outputs" / "econometric" / "ceo_clarity_extended",
        required_file="ceo_clarity_residual.parquet",
    )
    res = pd.read_parquet(rdir / "ceo_clarity_residual.parquet", columns=["file_name", "UncResCEO"])
    panel = panel.merge(res, on="file_name", how="left")

    # Center UncResCEO within Boasiako window (1997-2015)
    win_panel = panel[panel["cal_year"].between(WINDOW_FYEAR_MIN, WINDOW_FYEAR_MAX)]
    mu_uncres = win_panel["UncResCEO"].mean(skipna=True)
    panel["UncResCEO_c"] = panel["UncResCEO"] - mu_uncres
    print(f"  UncResCEO mean (centering offset): {mu_uncres:.6f}")

    # Aggregate to (gvkey, fyear) — mean of calls within year + firm-fixed ff12
    annual = (
        panel.groupby(["gvkey", "cal_year"], observed=True)
        .agg(UncResCEO_c=("UncResCEO_c", "mean"), ff12_code=("ff12_code", "first"))
        .reset_index()
        .rename(columns={"cal_year": "fyear"})
    )
    print(f"  Annualized H1 panel: {len(annual):,} (gvkey, fyear) cells, "
          f"{annual['gvkey'].nunique():,} gvkeys")
    return annual


# ==============================================================================
# Panel assembly
# ==============================================================================

def _winsorize_within_year(df: pd.DataFrame, col: str, pct: float = 0.01) -> pd.DataFrame:
    """1% winsorize per spec §3.3 line 1054."""
    def _w(s: pd.Series) -> pd.Series:
        if s.notna().sum() < 10:
            return s
        lo = s.quantile(pct)
        hi = s.quantile(1 - pct)
        return s.clip(lower=lo, upper=hi)
    df = df.copy()
    df[col] = df.groupby("fyear", observed=True)[col].transform(_w)
    return df


def assemble_panel(root: Path) -> pd.DataFrame:
    """Build (gvkey, fyear) panel with DV + treatment + controls + FE columns."""
    print("\n  --- Panel assembly ---")
    years = range(WINDOW_FYEAR_MIN, WINDOW_FYEAR_MAX + 1)

    # 1. Load Compustat Annual: che, at, lag(at) for DV; loc, state for treatment
    comp = read_compustat_annual(
        path=root / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
        cols=["gvkey", "datadate", "sic", "state", "loc", "at", "che"],
        years=range(WINDOW_FYEAR_MIN - 1, WINDOW_FYEAR_MAX + 1),  # +1 prior year for at_lag1
        us_only=True,
    )
    comp = comp.dropna(subset=["at", "state"]).copy()
    comp = comp[comp["at"] > 0]
    # Restrict state to 50 US + DC
    valid_us = {
        "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
        "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
        "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
        "VA","WA","WV","WI","WY","DC",
    }
    comp = comp[comp["state"].isin(valid_us)].copy()

    # Sort + lag AT for BoY scaling per spec line 1059 verbatim
    # ("scaled by total book assets at the beginning of the year")
    comp = comp.sort_values(["gvkey", "fyear"], kind="stable").reset_index(drop=True)
    comp["at_lag1"] = comp.groupby("gvkey")["at"].shift(1)
    comp = comp.dropna(subset=["at_lag1"]).copy()
    comp = comp[comp["at_lag1"] > 0]

    # DV: Cash = (cash + marketable securities) / total book assets BoY
    # Compustat CHE = Cash and Short-Term Investments (includes marketable secs)
    comp["cash"] = comp["che"].fillna(0) / comp["at_lag1"]

    # Restrict to plan years
    comp = comp[comp["fyear"].isin(years)].copy()
    # Dedup to (gvkey, fyear)
    comp = comp.sort_values(["gvkey", "fyear", "datadate"], kind="stable")
    comp = comp.drop_duplicates(subset=["gvkey", "fyear"], keep="last")
    print(f"  Compustat (US, AT>0, BoY-lag) base: {len(comp):,} firm-years, "
          f"{comp['gvkey'].nunique():,} gvkeys")

    # 2. Merge Disclosure_Law treatment (Y+1 staggered)
    dl = BoasiakoDisclosureLawTreatmentBuilder().build(years=years, root_path=root).data
    panel = comp.merge(dl[["gvkey", "fyear", "Disclosure_Law"]], on=["gvkey", "fyear"], how="inner")
    print(f"  After Disclosure_Law merge: {len(panel):,} firm-years")

    # 3. Merge 11 controls
    ctrl = BoasiakoEq1ControlsBuilder().build(years=years, root_path=root).data
    panel = panel.merge(
        ctrl[["gvkey", "fyear"] + FIRM_CONTROLS], on=["gvkey", "fyear"], how="inner"
    )
    print(f"  After Eq 1 controls merge: {len(panel):,} firm-years")

    # 4. Merge FF49 industry classifier
    ff49 = FF49IndustryClassifierBuilder().build(years=years, root_path=root).data
    panel = panel.merge(ff49[["gvkey", "fyear", "ff49_code"]], on=["gvkey", "fyear"], how="inner")
    print(f"  After FF49 merge: {len(panel):,} firm-years")

    # 5. Merge industry CF vol
    icv = BoasiakoIndustryCFVolBuilder().build(years=years, root_path=root).data
    panel = panel.merge(icv[["ff49_code", "fyear", "industry_cf_vol"]],
                        on=["ff49_code", "fyear"], how="left")
    print(f"  After industry_cf_vol merge: {len(panel):,} firm-years")

    # 6. Winsorize cash (DV) — 1% within year per spec line 1054
    panel = _winsorize_within_year(panel, "cash", pct=0.01)

    # 7. Build partition dummies for Block 3 speech-channel specs
    # Small = bottom tercile firm_size; Young = bottom tercile firm_age; NonDiv = dividend_paying==0
    def _is_bottom_tercile(s: pd.Series) -> pd.Series:
        valid = s.dropna()
        if len(valid) < 10:
            return pd.Series(np.nan, index=s.index)
        cutoff = valid.quantile(1.0 / 3.0)
        return (s <= cutoff).astype(float)

    panel["tercile_small"] = panel.groupby("fyear")["firm_size"].transform(_is_bottom_tercile)
    panel["tercile_young"] = panel.groupby("fyear")["firm_age"].transform(_is_bottom_tercile)
    panel["non_dividend"] = (panel["dividend_paying"] == 0).astype(float)

    # 8. Merge UncResCEO_c (annualized) — left merge so cash specs work even when speech missing
    h1_annual = load_h1_panel_to_annual(root)
    panel = panel.merge(h1_annual[["gvkey", "fyear", "UncResCEO_c"]],
                        on=["gvkey", "fyear"], how="left")
    print(f"  UncResCEO_c coverage on Boasiako panel: "
          f"{panel['UncResCEO_c'].notna().mean():.1%}")

    return panel.reset_index(drop=True)


# ==============================================================================
# Regression — _fit_one with clusters_col baked in (audit M0a)
# ==============================================================================

def _fit_one(
    df: pd.DataFrame,
    dv: str,
    treatment_terms: List[str],
    extra_controls: List[str],
    fe: str,
) -> Tuple[Optional[Any], Dict[str, Any]]:
    """Fit one regression spec with clusters_col baked in (audit M0a clone-time pattern).

    Args:
        df: panel with index NOT yet set (we set MultiIndex inside)
        dv: dependent variable column
        treatment_terms: list of variables of interest (e.g., ["Disclosure_Law"]
                         or ["Disclosure_Law", "Small_x_DL", "Small"]).
                         The FIRST entry is the headline coefficient for reporting.
        extra_controls: additional control vars to include in exog
        fe: FE config name (see FE_LADDER_CASH)

    Returns:
        (PanelResults or None, meta dict)
    """
    headline = treatment_terms[0]
    needed = [dv] + treatment_terms + extra_controls + ["gvkey", "fyear", "state", "ff49_code"]
    df = df.dropna(subset=needed).copy()
    if len(df) < 100:
        return None, {"n_obs": int(len(df)), "skipped": "too few obs"}

    # Apply FE-specific filters BEFORE set_index
    if fe == "industry_state_year_excl_ca":
        df = df[df["state"] != "CA"].copy()
    elif fe == "industry_state_year_excl_crisis":
        df = df[~df["fyear"].isin(CRISIS_FYEARS)].copy()
    if len(df) < 100:
        return None, {"n_obs": int(len(df)), "skipped": "too few obs after FE filter"}

    # Pre-extract cluster column BEFORE set_index (since it'll move to index)
    state_clusters = df["state"].copy()

    df = df.set_index(["gvkey", "fyear"])
    state_clusters.index = df.index

    exog = df[treatment_terms + extra_controls]

    # Build fit_kwargs with clusters_col=state baked in (audit M0a)
    fit_kwargs: Dict[str, Any] = {"cov_type": "clustered"}
    cluster_col = CLUSTERING.get("clusters_col")
    if cluster_col == "state":
        fit_kwargs["clusters"] = pd.DataFrame({"state": state_clusters.values}, index=df.index)
    elif CLUSTERING.get("entity"):
        fit_kwargs["cluster_entity"] = True
    if CLUSTERING.get("time"):
        fit_kwargs["cluster_time"] = True

    # FE configurations (Boasiako Table 2)
    # linearmodels.PanelOLS supports max 2 effects total (entity + time + other ≤ 2 cols).
    # For industry+state+year (3 dimensions): use time_effects=True (year) +
    # other_effects=ff49 (industry) + STATE DUMMIES added to exog as regressors.
    # drop_absorbed=True handles perfect collinearity from omitted state.
    if fe in ("industry_state_year", "industry_state_year_excl_ca", "industry_state_year_excl_crisis"):
        # State dummies as exog regressors (drop_first to avoid full-rank collinearity with intercept)
        state_dummies = pd.get_dummies(df["state"], prefix="state", drop_first=True, dtype=float)
        # Combine treatment + controls + state dummies
        exog_with_state = pd.concat([exog, state_dummies], axis=1)
        model = PanelOLS(
            dependent=df[dv],
            exog=exog_with_state,
            entity_effects=False,
            time_effects=True,  # year FE
            other_effects=df["ff49_code"].astype("category").cat.codes,  # industry FE
            drop_absorbed=True,
            check_rank=False,
        )
    elif fe == "firm_year":
        # firm + year FE (state absorbed by firm FE since firms don't move)
        model = PanelOLS(
            dependent=df[dv],
            exog=exog,
            entity_effects=True,   # firm FE (gvkey is panel entity)
            time_effects=True,     # year FE
            drop_absorbed=True,
            check_rank=False,
        )
    else:
        raise ValueError(f"Unknown FE config: {fe}")

    try:
        result = model.fit(**fit_kwargs)
    except Exception as e:
        return None, {"n_obs": int(len(df)), "skipped": f"fit failed: {e}"}

    meta: Dict[str, Any] = {
        "dv": dv,
        "treatment_headline": headline,
        "fe": fe,
        "n_obs": int(result.nobs),
        "r2": float(result.rsquared),
    }
    if headline in result.params.index:
        beta = float(result.params[headline])
        se = float(result.std_errors[headline])
        t = float(result.tstats[headline])
        p_two = float(result.pvalues[headline])
        meta.update({
            "beta": beta,
            "se": se,
            "t": t,
            "p_two": p_two,
            "p_one": (p_two / 2) if beta >= 0 else 1 - (p_two / 2),
        })
    else:
        meta.update({"beta": np.nan, "se": np.nan, "t": np.nan, "p_two": np.nan, "p_one": np.nan,
                     "skipped": "headline absorbed by FE"})
    return result, meta


def run_14_cells(panel: pd.DataFrame) -> List[Dict[str, Any]]:
    """14 cells = 8 baseline (4 cash + 4 speech) + 6 channel (3 partitions × 2 FE)."""
    results: List[Dict[str, Any]] = []
    col = 0

    # Block 1: DV=cash, Disclosure_Law, 4 FE
    for fe in FE_LADDER_CASH:
        col += 1
        model, meta = _fit_one(
            panel, dv="cash",
            treatment_terms=[KEY_IV],
            extra_controls=ALL_CONTROLS,
            fe=fe,
        )
        meta["col"] = col
        meta["block"] = "cash_baseline"
        results.append({"model": model, "meta": meta})
        _print_cell(meta)

    # Block 2: DV=UncResCEO_c, Disclosure_Law, 4 FE
    for fe in FE_LADDER_SPEECH:
        col += 1
        model, meta = _fit_one(
            panel, dv="UncResCEO_c",
            treatment_terms=[KEY_IV],
            extra_controls=ALL_CONTROLS,
            fe=fe,
        )
        meta["col"] = col
        meta["block"] = "speech_baseline"
        results.append({"model": model, "meta": meta})
        _print_cell(meta)

    # Block 3: SPEECH × FINANCIAL CONSTRAINT × Disclosure_Law (6 cells)
    for partition_label, partition_col in PARTITIONS.items():
        for fe in FE_LADDER_CHANNEL:
            col += 1
            interaction_col = f"{partition_label}_x_DL"
            panel_w = panel.copy()
            panel_w[interaction_col] = (panel_w[partition_col] * panel_w[KEY_IV])
            model, meta = _fit_one(
                panel_w, dv="UncResCEO_c",
                treatment_terms=[interaction_col, partition_col, KEY_IV],
                extra_controls=ALL_CONTROLS,
                fe=fe,
            )
            meta["col"] = col
            meta["block"] = f"speech_channel_{partition_label}"
            meta["partition"] = partition_label
            results.append({"model": model, "meta": meta})
            _print_cell(meta)

    return results


def _print_cell(meta: Dict[str, Any]) -> None:
    msg = (
        f"  Col ({meta.get('col', '?'):>2}) "
        f"DV={meta.get('dv', '?'):14s} "
        f"head={meta.get('treatment_headline', '?'):20s} "
        f"FE={meta.get('fe', '?'):32s} "
        f"n={meta.get('n_obs', 0):>6,} "
        f"beta={meta.get('beta', np.nan):+.4f} "
        f"p_one={meta.get('p_one', np.nan):.3f}"
    )
    if meta.get("skipped"):
        msg += f"  SKIPPED({meta['skipped']})"
    print(msg)


# ==============================================================================
# Output
# ==============================================================================

def _sig_stars(p: float, beta: float) -> str:
    """One-tailed POS sig stars (only fire if beta >= 0)."""
    if np.isnan(p) or np.isnan(beta) or beta < 0:
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def write_outputs(results: List[Dict[str, Any]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # CSV diagnostics
    rows = [r["meta"] for r in results]
    diag = pd.DataFrame(rows)
    diag.to_csv(out_dir / "model_diagnostics.csv", index=False)
    print(f"  Saved: model_diagnostics.csv ({len(diag)} rows)")

    # Markdown summary
    lines = ["# H1.5 Boasiako Disclosure Law DiD — 14 Cells", ""]
    lines.append(f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("**Sina decisions ratified 2026-05-09 (plan v2):**")
    lines.append("- Q1 Chen classifier: 3-variant sensitivity (handled separately)")
    lines.append("- Q2 Boasiako scope: Eq 1 only (Eq 2 ABORTED post-audit C2)")
    lines.append("- Q3 Speech channel partitions: INCLUDED on UncResCEO_c")
    lines.append("- Q4 Cash robustness ladder: SKIPPED per Brexit pattern")
    lines.append("")
    lines.append("| col | block | dv | treatment | fe | n | beta | p_one | sig |")
    lines.append("|-----|-------|----|-----------|----|---|------|-------|-----|")
    for r in results:
        m = r["meta"]
        sig = _sig_stars(m.get("p_one", np.nan), m.get("beta", 0))
        lines.append(
            f"| {m.get('col', '?')} | {m.get('block', '?')} | {m.get('dv', '?')} | "
            f"{m.get('treatment_headline', '?')} | {m.get('fe', '?')} | "
            f"{m.get('n_obs', 0):,} | {m.get('beta', np.nan):+.4f} | "
            f"{m.get('p_one', np.nan):.3f} | {sig} |"
        )
    (out_dir / "report_step4_H1_5_disclosure_law_did.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print(f"  Saved: report_step4_H1_5_disclosure_law_did.md")

    # Suite spec JSON for thesis-table autogen
    suite_spec = {
        "suite_id": SUITE_ID,
        "dir_name": SUITE_DIR_NAME,
        "title": SUITE_TITLE,
        "label": SUITE_LABEL,
        "n_cells": len(results),
        "clustering": CLUSTERING,
        "treatment": KEY_IV,
        "blocks": {
            "cash_baseline": "cols 1-4 (DV=cash, Disclosure_Law, 4 FE)",
            "speech_baseline": "cols 5-8 (DV=UncResCEO_c, Disclosure_Law, 4 FE)",
            "speech_channel": "cols 9-14 (Small/Young/NonDiv x DL, 2 FE each)",
        },
    }
    (out_dir / f"suite_spec_{SUITE_ID}.json").write_text(json.dumps(suite_spec, indent=2))
    print(f"  Saved: suite_spec_{SUITE_ID}.json")


# ==============================================================================
# Main
# ==============================================================================

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H1.5 Boasiako Disclosure Law DiD (Cash + Speech + Channels)"
    )
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

    print("=" * 80)
    print("STAGE 4: H1.5 BOASIAKO DISCLOSURE LAW DiD ON CASH + SPEECH")
    print("=" * 80)
    print(f"Timestamp:  {timestamp}")
    print(f"Output:     {out_dir}")
    print(f"Window:     {WINDOW_FYEAR_MIN}-{WINDOW_FYEAR_MAX} (annual)")
    print(f"POST:       Disclosure_Law(0/1)_{{s,t}} Y+1 timing per spec §3.2")
    print(f"Clustering: {CLUSTERING}  (state-cluster per spec §3.2 verbatim)")
    print(f"Sina v2 lock: BOTH Eq 1 only (Phase 1B Eq 2 ABORTED audit C2)")
    print()

    panel = assemble_panel(root)

    if args.dry_run:
        print(f"\n  DRY RUN: panel built ({len(panel):,} firm-years); skipping regressions.")
        return 0

    print("\n  --- Running 14 regressions ---")
    results = run_14_cells(panel)

    print(f"\n  --- Writing outputs to {out_dir} ---")
    write_outputs(results, out_dir)

    elapsed = (datetime.now() - t0).total_seconds()
    print(f"\n=== DONE in {elapsed:.1f}s ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
