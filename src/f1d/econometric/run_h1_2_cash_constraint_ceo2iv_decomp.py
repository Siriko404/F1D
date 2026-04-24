#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H1.2 HFC Channel — CEO 2-IV DECOMPOSED (DWZ Eq.5 × Unrated)
================================================================================
ID: econometric/run_h1_2_cash_constraint_ceo2iv_decomp
Description: DWZ-decomposition variant of H1.2.ceo2. Replaces the main
             speech-uncertainty IV stack (UncAnsCEO_c + UncPreCEO_c) with the
             DWZ Eq.5 decomposition: ClarityCEO_QtrExp_c (persistent CEO trait,
             = -CEO FE) + UncResCEO_QtrExp_c (call-level state residual).
             Both decomp components computed via strict no-look-ahead
             quarterly-expanding fit of DWZ Eq.4 — see
             run_h0_3_ceo_clarity_expanding.py. Both decomp IVs mean-centered
             on Main sample. Two Unrated interaction terms estimated:
             ClarityCEO × Unrated and UncResCEO × Unrated. Moderator is BINARY
             Unrated vs Rated (FP 2006 verbatim spec) — BelowIG level dummy
             AND BelowIG interactions DROPPED entirely. Reference group =
             Rated firms (IG ∪ BelowIG).

Tail directions (asymmetric per design lock 2026-04-23):
    Main ClarityCEO_QtrExp_c: one-tail NEG
        (high persistent clarity → less precautionary cash; HC at trait level)
    Main UncResCEO_QtrExp_c: one-tail POS
        (positive within-quarter uncertainty surprise → more cash; HC at state level)
    Interaction UncResCEO × Unrated: one-tail POS
        (HFC amplification — constrained firms more reactive to state uncertainty)
    Interaction ClarityCEO × Unrated: TWO-TAIL
        (no theory prior: trait-level moderation by constraint status has no
         clean monotone mechanism — null does not read as theory failure)
    Unrated level dummy: two-tailed (no directional prior on level shift).

Channel: CH1 — Precautionary liquidity under external-finance frictions.

Parent suite: H1.2.ceo2 (Cash × Constraint, CEO 2-IV UncAns/UncPre)
DWZ source: Demerjian, Wang & Zarowin (2021), Eq.4 + Eq.5.

Model Specification:
    CashRatio = b1*ClarityCEO_c + b2*UncResCEO_c
              + b3*Unrated
              + b4*(ClarityCEO_c x Unrated) + b5*(UncResCEO_c x Unrated)
              + controls + IndustryFE + CalendarYearFE + e

16 Models (8 displayed: cols 5-8 + 13-16 = interaction specs only):
    Block 1 (cols 1-8):  DV = CashRatio_t
    Block 2 (cols 9-16): DV = CashRatio_lead

Moderator: BINARY Unrated dummy from S&P splticrm (Compustat Daily Ratings).
    Rated (reference): any splticrm match (IG and BelowIG combined per FP 2006)
    Unrated: no splticrm match
    Merge: merge_asof on (gvkey, start_date) — no look-ahead.

Sample: Main only (FF12 not in {8, 11}). Fiscal years 2002-2016. Decomp parquet
    merge drops rows with NaN Clarity/UncRes (Q1 of each year unestimable under
    strict-expanding spec). Final sample size strictly smaller than parent
    H1.2.ceo2 due to decomp coverage cost.

Unit: Call-level. Panel index: ["gvkey", "cal_yr"] or ["gvkey", "cal_yr_qtr"].
SEs: Firm-clustered.

Inputs:
    - outputs/variables/h1_cash_holdings/latest/h1_cash_holdings_panel.parquet
    - outputs/econometric/ceo_clarity_expanding/<latest>/ceo_clarity_qtrexp_residuals.parquet
    - inputs/compustat_daily_ratings/compustat_daily_ratings.csv

Outputs:
    - outputs/econometric/h1_2_cash_constraint_ceo2iv_decomp/{timestamp}/...

Deterministic: true
Author: Thesis Author
Date: 2026-04-23
================================================================================
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.shared.latex_tables_accounting import make_summary_stats_table
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import (
    extract_coefs_panelols,
    generate_attrition_table,
    generate_manifest,
    write_suite_spec,
)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index


# ==============================================================================
# Configuration
# ==============================================================================

# CEO 2-IV DECOMPOSED stack (DWZ Eq.5; both mean-centered on Main sample)
IVS_RAW = ["ClarityCEO_QtrExp", "UncResCEO_QtrExp"]
IVS_CENTERED = ["ClarityCEO_QtrExp_c", "UncResCEO_QtrExp_c"]
IV_RAW_TO_CENTERED = dict(zip(IVS_RAW, IVS_CENTERED))

CONTROLS = [
    "Leverage", "lnAssets", "TobinsQ", "ROA", "Capex",
    "DivDummy", "sCFO",
    "SalesGrowth", "RDSales", "CashFlowAt", "DailyVola",
    "Lagged_DV",  # Unified lagged DV
]

# Binary moderator (Unrated vs Rated reference) per FP 2006 verbatim.
# BelowIG dropped entirely: no level dummy, no interactions. Reference group =
# Rated firms (IG ∪ BelowIG) — the FP 2006 binary specification.
MOD_UNRATED = "Unrated"
# Per-IV interaction term names (Unrated only; binary moderator)
INT_UNRATED_CLARITY = "ClarityCEO_QtrExp_c_x_Unrated"
INT_UNRATED_UNCRES = "UncResCEO_QtrExp_c_x_Unrated"
INT_UNRATED_TERMS = [INT_UNRATED_CLARITY, INT_UNRATED_UNCRES]

# Per-IV tail directions (asymmetric; locked 2026-04-23).
# Why: state-channel interaction (UncRes×Unrated) has clean HFC amplification
#      mechanism; trait-channel interaction (Clarity×Unrated) does not. Two-tail
#      preserves null-as-non-failure for the trait interaction.
IV_TAIL_DIRECTION: Dict[str, str] = {
    "ClarityCEO_QtrExp_c": "negative",
    "UncResCEO_QtrExp_c": "positive",
    INT_UNRATED_CLARITY: "none",        # two-tailed
    INT_UNRATED_UNCRES: "positive",
}

# Investment-grade rating codes (BBB- and above)
IG_RATINGS = {"AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-"}

MIN_CALLS_PER_FIRM = 5
YEAR_MIN = 2002
YEAR_MAX = 2016

# ------------------------------------------------------------------
# Suite metadata for suite_spec.json emission.
# Display layout mirrors parent H1.2.ceo2: 16 underlying regressions,
# 8 interaction specs displayed (cols 5-8 + 13-16 renumbered 1-8).
# Top main-IV rows pull from the matching unconditional spec
# (interaction_col - 4); moderator levels + Unrated interactions
# come from the interaction spec.
# ------------------------------------------------------------------
SUITE_ID = "H1.2.ceo2.decomp"
SUITE_DIR_NAME = "h1_2_cash_constraint_ceo2iv_decomp"
SUITE_TITLE = (
    "Financial Constraint-Moderated CEO Speech Uncertainty and Cash Holdings "
    "(CEO 2-IV Decomposed: DWZ Clarity + UncRes, qtr-exp)"
)
SUITE_CAPTION = (
    r"H1.2 CEO 2-IV Decomp: Financial Constraint--Moderated DWZ CEO Speech "
    r"Decomposition and Cash Holdings"
)
SUITE_LABEL = "tab:h1_2_ceo2_decomp"
SAMPLE_LABEL = (
    "Main sample (excludes financial and utility firms). Fiscal years 2002-2016. "
    "DWZ quarterly-expanding decomposition: Clarity = -CEO FE; UncRes = call-level residual."
)
HYP_DIR = "positive"  # Suite-level Pydantic placeholder; per-IV via IV_TAIL_DIRECTION + spec stitching.
CLUSTERING = {"entity": True, "time": False}
TAIL = {"direction": HYP_DIR, "applies_to": "ivs_only"}
EXTENDED_ONLY_CONTROLS: List[str] = []

MODEL_SPECS = [
    # Block 1: CashRatio_t
    # Unconditional specs (no interactions): cols 1-4, full FE ladder
    {"col": 1, "dv": "CashRatio",      "fe": "industry",    "extra_controls": [], "interactions": False},
    {"col": 2, "dv": "CashRatio",      "fe": "firm",        "extra_controls": [], "interactions": False},
    {"col": 3, "dv": "CashRatio",      "fe": "industry_yq", "extra_controls": [], "interactions": False},
    {"col": 4, "dv": "CashRatio",      "fe": "firm_yq",     "extra_controls": [], "interactions": False},
    # Interaction specs (IG-reference conditional effect): cols 5-8, full FE ladder
    {"col": 5, "dv": "CashRatio",      "fe": "industry",    "extra_controls": [], "interactions": True},
    {"col": 6, "dv": "CashRatio",      "fe": "firm",        "extra_controls": [], "interactions": True},
    {"col": 7, "dv": "CashRatio",      "fe": "industry_yq", "extra_controls": [], "interactions": True},
    {"col": 8, "dv": "CashRatio",      "fe": "firm_yq",     "extra_controls": [], "interactions": True},
    # Block 2: CashRatio_lead (one-quarter-ahead)
    # Unconditional specs: cols 9-12
    {"col":  9, "dv": "CashRatio_lead", "fe": "industry",    "extra_controls": [], "interactions": False},
    {"col": 10, "dv": "CashRatio_lead", "fe": "firm",        "extra_controls": [], "interactions": False},
    {"col": 11, "dv": "CashRatio_lead", "fe": "industry_yq", "extra_controls": [], "interactions": False},
    {"col": 12, "dv": "CashRatio_lead", "fe": "firm_yq",     "extra_controls": [], "interactions": False},
    # Interaction specs: cols 13-16
    {"col": 13, "dv": "CashRatio_lead", "fe": "industry",    "extra_controls": [], "interactions": True},
    {"col": 14, "dv": "CashRatio_lead", "fe": "firm",        "extra_controls": [], "interactions": True},
    {"col": 15, "dv": "CashRatio_lead", "fe": "industry_yq", "extra_controls": [], "interactions": True},
    {"col": 16, "dv": "CashRatio_lead", "fe": "firm_yq",     "extra_controls": [], "interactions": True},
]

DV_TEX = {
    "CashRatio": r"Cash$_t$",
    "CashRatio_lead": r"Cash$_{t+1}$",
}

SUMMARY_STATS_VARS = [
    {"col": "CashRatio", "label": "Cash Holdings$_t$"},
    {"col": "CashRatio_lead", "label": "Cash Holdings$_{t+1}$"},
    {"col": "ClarityCEO_QtrExp", "label": "CEO Clarity (DWZ qtr-exp, raw)"},
    {"col": "ClarityCEO_QtrExp_c", "label": "CEO Clarity (DWZ qtr-exp, centered)"},
    {"col": "UncResCEO_QtrExp", "label": "CEO UncRes (DWZ qtr-exp, raw)"},
    {"col": "UncResCEO_QtrExp_c", "label": "CEO UncRes (DWZ qtr-exp, centered)"},
    {"col": MOD_UNRATED, "label": "Unrated (dummy)"},
    {"col": "Leverage", "label": "Leverage"},
    {"col": "lnAssets", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "Capex", "label": "CapEx / Assets"},
    {"col": "DivDummy", "label": "Dividend Payer"},
    {"col": "sCFO", "label": "OCF Volatility"},
    {"col": "SalesGrowth", "label": "Sales Growth"},
    {"col": "RDSales", "label": "R\\&D Intensity"},
    {"col": "CashFlowAt", "label": "Cash Flow"},
    {"col": "DailyVola", "label": "Stock Volatility"},
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H1.2 Financing-Constraint-Moderated Cash Holdings (3-category)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> Tuple[pd.DataFrame, Path]:
    """Load H1 panel + merge DWZ-decomp parquet on file_name.

    Decomp IVs (ClarityCEO_QtrExp + UncResCEO_QtrExp) are NOT in the H1
    parquet — they come from the latest H0.3 expanding-window output.
    """
    print("\n" + "=" * 60)
    print("Loading H1 panel + merging DWZ-decomp parquet")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h1_cash_holdings",
            required_file="h1_cash_holdings_panel.parquet",
        )
        panel_file = panel_dir / "h1_cash_holdings_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    # H1 panel: DV + controls + identifiers (decomp IVs come from merge below)
    columns = [
        "file_name",
        "gvkey", "year", "fyearq_int", "ff12_code", "start_date",
        "CashRatio", "CashRatio_lag", "CashRatio_lead",
        *[c for c in CONTROLS if c != "Lagged_DV"],  # lagged created dynamically
    ]

    panel = pd.read_parquet(panel_file, columns=columns)
    print(f"  H1 panel:   {panel_file}")
    print(f"  H1 rows:    {len(panel):,}")

    # Merge DWZ decomp parquet (strict no-look-ahead quarterly expanding)
    decomp_dir = get_latest_output_dir(
        root_path / "outputs" / "econometric" / "ceo_clarity_expanding",
        required_file="ceo_clarity_qtrexp_residuals.parquet",
    )
    decomp_file = decomp_dir / "ceo_clarity_qtrexp_residuals.parquet"
    decomp = pd.read_parquet(
        decomp_file,
        columns=["file_name", *IVS_RAW],
    )
    print(f"  Decomp:     {decomp_file}")
    print(f"  Decomp rows: {len(decomp):,}  "
          f"non-NaN Clarity: {decomp[IVS_RAW[0]].notna().sum():,}")

    before = len(panel)
    panel = panel.merge(decomp, on="file_name", how="left", validate="one_to_one")
    matched = panel[IVS_RAW[0]].notna().sum()
    print(f"  After merge: {len(panel):,} rows ({matched:,} with non-NaN Clarity; "
          f"{before - matched:,} dropped downstream by complete-case)")

    # Build calendar year-quarter index for FE specs
    panel = build_cal_yr_qtr_index(panel)
    n_yr_qtr = panel["cal_yr_qtr"].notna().sum()
    print(f"  cal_yr_qtr coverage: {n_yr_qtr:,}/{len(panel):,} ({100*n_yr_qtr/len(panel):.1f}%)")

    return panel, panel_file


def load_and_merge_ratings(panel: pd.DataFrame, root_path: Path) -> pd.DataFrame:
    """Load S&P credit ratings and merge via merge_asof. Binary Unrated dummy only.

    Binary classification per FP 2006:
        - Any splticrm match (IG or BelowIG) → Unrated=0 (reference: Rated)
        - No splticrm match                  → Unrated=1

    Data: Monthly Compustat Daily Ratings (2000-01 to 2017-02).
    22 rating codes: AAA, AA+, AA, AA-, A+, A, A-, BBB+, BBB, BBB-,
    BB+, BB, BB-, B+, B, B-, CCC+, CCC, CCC-, CC, D, SD.
    """
    print("\n" + "=" * 60)
    print("Merging S&P Credit Ratings (merge_asof, binary Unrated)")
    print("=" * 60)

    ratings_path = root_path / "inputs" / "compustat_daily_ratings" / "compustat_daily_ratings.csv"
    if not ratings_path.exists():
        raise FileNotFoundError(f"Ratings data not found: {ratings_path}")

    ratings = pd.read_csv(
        ratings_path, usecols=["gvkey", "datadate", "splticrm"], low_memory=False,
    )
    print(f"  Loaded ratings: {len(ratings):,} rows")

    # Parse dates, format gvkey to match panel (zero-padded 6-char string)
    ratings["datadate"] = pd.to_datetime(ratings["datadate"])
    ratings["gvkey"] = ratings["gvkey"].astype(str).str.zfill(6)
    ratings = ratings.dropna(subset=["datadate"])
    ratings = ratings.sort_values("datadate").reset_index(drop=True)

    # Ensure panel has datetime start_date for merge_asof
    panel["_start_dt"] = pd.to_datetime(panel["start_date"])
    panel = panel.sort_values("_start_dt").reset_index(drop=True)

    before = len(panel)

    # merge_asof: for each call, find the most recent rating on or before call date
    panel = pd.merge_asof(
        panel,
        ratings[["gvkey", "datadate", "splticrm"]].rename(
            columns={"datadate": "_rating_date"}
        ),
        left_on="_start_dt",
        right_on="_rating_date",
        by="gvkey",
        direction="backward",
    )

    assert len(panel) == before, f"merge_asof changed row count: {before} -> {len(panel)}"

    # Binary classification: Rated (splticrm not null) vs Unrated
    has_rating = panel["splticrm"].notna()
    panel[MOD_UNRATED] = (~has_rating).astype(float)

    # Diagnostics
    n_rated = int(has_rating.sum())
    n_unrated = int(panel[MOD_UNRATED].sum())
    n_total = len(panel)

    print(f"  Rated (reference): {n_rated:,} ({100*n_rated/n_total:.1f}%)")
    print(f"  Unrated:           {n_unrated:,} ({100*n_unrated/n_total:.1f}%)")

    # Clean up temp columns
    panel = panel.drop(columns=["_start_dt", "_rating_date", "splticrm"], errors="ignore")

    return panel


def center_iv(panel: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Mean-center each CEO IV on Main sample (after FF12 filter, before complete-case)."""
    print("\n" + "=" * 60)
    print("Centering CEO IVs on Main sample")
    print("=" * 60)

    main_mask = ~panel["ff12_code"].isin([8, 11])
    iv_means: Dict[str, float] = {}

    for raw, centered in zip(IVS_RAW, IVS_CENTERED):
        iv_main = panel.loc[main_mask, raw].dropna()
        mu = float(iv_main.mean())
        panel[centered] = panel[raw] - mu
        iv_means[raw] = mu
        print(f"  {raw}: Main obs={len(iv_main):,}  mean={mu:.4f}  "
              f"centered mean={panel.loc[main_mask, centered].dropna().mean():.6f}")

    return panel, iv_means


# ==============================================================================
# Regression
# ==============================================================================


def filter_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to Main sample only (exclude Finance ff12=8, Utility ff12=11)."""
    before = len(panel)
    main = panel[~panel["ff12_code"].isin([8, 11])].copy()
    print(f"  Main sample: {len(main):,} / {before:,} "
          f"(dropped {before - len(main):,} Finance/Utility)")
    return main


def prepare_regression_data(
    panel: pd.DataFrame, spec: Dict[str, Any]
) -> pd.DataFrame:
    """Prepare data for one regression spec with two interaction terms."""
    dv = spec["dv"]
    fe = spec["fe"]
    extra_controls = spec["extra_controls"]
    all_controls = CONTROLS + extra_controls

    # Determine time column based on FE type
    time_col = "cal_yr_qtr" if fe.endswith("_yq") else "cal_yr"

    # Create Lagged_DV: always lag of the base DV (t-1), regardless of t/t+1
    base_dv = dv.replace("_lead", "")
    lag_col = f"{base_dv}_lag"
    panel = panel.copy()
    panel["Lagged_DV"] = panel[lag_col]

    use_interactions = spec.get("interactions", True)

    required = ([dv] + IVS_RAW + IVS_CENTERED + [MOD_UNRATED]
                + all_controls + ["gvkey", time_col, "ff12_code"])

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    # Create Unrated interaction terms only for interaction specs
    if use_interactions:
        df[INT_UNRATED_CLARITY] = df["ClarityCEO_QtrExp_c"] * df[MOD_UNRATED]
        df[INT_UNRATED_UNCRES] = df["UncResCEO_QtrExp_c"] * df[MOD_UNRATED]

    # Drop NaN in DV
    before = len(df)
    df = df[df[dv].notna()].copy()
    print(f"  After DV ({dv}) filter: {len(df):,} / {before:,}")

    # Complete cases (includes decomp IVs — drops Q1 rows with NaN Clarity/UncRes)
    all_required = required + (INT_UNRATED_TERMS if use_interactions else [])
    complete_mask = df[all_required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases: {len(df):,}")

    # Min calls per firm
    firm_counts = df["gvkey"].value_counts()
    valid_firms = set(firm_counts[firm_counts >= MIN_CALLS_PER_FIRM].index)
    df = df[df["gvkey"].isin(valid_firms)].copy()

    n_firms = df["gvkey"].nunique()
    n_time_periods = df.groupby(["gvkey", time_col]).ngroups
    n_unrated = int(df[MOD_UNRATED].sum())
    n_rated = int((df[MOD_UNRATED] == 0).sum())
    print(f"  After >={MIN_CALLS_PER_FIRM} calls/firm: "
          f"{len(df):,} calls, {n_firms:,} firms, {n_time_periods:,} firm-time-periods")
    print(f"  Binary split: {n_rated:,} Rated ({100*n_rated/len(df):.1f}%) / "
          f"{n_unrated:,} Unrated ({100*n_unrated/len(df):.1f}%)")

    return df


def compute_vif(df: pd.DataFrame, exog_cols: List[str]) -> Dict[str, float]:
    """Compute VIF for each regressor."""
    from numpy.linalg import LinAlgError

    X = df[exog_cols].dropna()
    if len(X) < len(exog_cols) + 1:
        return {}

    X = X.copy()
    X["_const"] = 1.0
    cols_with_const = exog_cols + ["_const"]

    vif_dict = {}
    try:
        X_arr = X[cols_with_const].values.astype(float)
        for i, col in enumerate(exog_cols):
            from statsmodels.stats.outliers_influence import variance_inflation_factor
            vif_dict[col] = variance_inflation_factor(X_arr, i)
    except (LinAlgError, ValueError):
        pass

    return vif_dict


def _extract_coef(model, name: str) -> Tuple[float, float, float]:
    """Extract (beta, se, p_two) for a named coefficient."""
    beta = float(model.params.get(name, np.nan))
    se = float(model.std_errors.get(name, np.nan))
    p = float(model.pvalues.get(name, np.nan))
    return beta, se, p


def run_regression(
    df_prepared: pd.DataFrame, spec: Dict[str, Any]
) -> Tuple[Any, Dict[str, Any]]:
    """Run PanelOLS with Industry FE + Calendar Year or Year-Quarter FE."""
    dv = spec["dv"]
    col_num = spec["col"]
    fe = spec["fe"]
    extra_controls = spec["extra_controls"]
    all_controls = CONTROLS + extra_controls

    # Determine time column and FE label
    time_col = "cal_yr_qtr" if fe.endswith("_yq") else "cal_yr"
    base_fe = fe.replace("_yq", "")
    fe_label = f"{'Firm' if base_fe == 'firm' else 'Industry(FF12)'} + {'CalYrQtr' if fe.endswith('_yq') else 'CalYear'}"

    print(f"\n{'=' * 60}")
    print(f"Col ({col_num}) | DV={dv} | FE={fe_label}")
    print(f"{'=' * 60}")

    if len(df_prepared) < 100:
        print(f"  Too few obs ({len(df_prepared)}), skipping")
        return None, {}

    use_interactions = spec.get("interactions", True)
    # Always include both centered decomp IVs + Unrated level dummy (binary moderator).
    base_exog = list(IVS_CENTERED) + [MOD_UNRATED]
    if use_interactions:
        exog = base_exog + INT_UNRATED_TERMS + all_controls
    else:
        exog = base_exog + all_controls

    n_firms = df_prepared["gvkey"].nunique()
    n_time_periods = df_prepared.groupby(["gvkey", time_col]).ngroups
    print(f"  N={len(df_prepared):,}, firms={n_firms:,}, firm-time-periods={n_time_periods:,}")
    if extra_controls:
        print(f"  Extra controls: {extra_controls}")

    # VIF
    vif = compute_vif(df_prepared, exog)
    if vif and use_interactions:
        for t in INT_UNRATED_TERMS:
            print(f"  VIF({t}): {vif.get(t, np.nan):.2f}")
        print(f"  VIF({MOD_UNRATED}): {vif.get(MOD_UNRATED, np.nan):.2f}")

    t0 = datetime.now()
    df_panel = df_prepared.set_index(["gvkey", time_col])

    try:
        if base_fe == "industry":
            model_obj = PanelOLS(
                dependent=df_panel[dv],
                exog=df_panel[exog],
                entity_effects=False,
                time_effects=True,
                other_effects=df_panel["ff12_code"],
                drop_absorbed=True,
                check_rank=False,
            )
        else:  # firm
            exog_str = " + ".join(exog)
            formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
            model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
        model = model_obj.fit(cov_type="clustered", cluster_entity=True, cluster_time=False)
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return None, {}

    elapsed = (datetime.now() - t0).total_seconds()

    # Extract main decomposed IV coefficients (per-IV asymmetric directions)
    beta_clarity, se_clarity, p_two_clarity = _extract_coef(model, "ClarityCEO_QtrExp_c")
    beta_uncres, se_uncres, p_two_uncres = _extract_coef(model, "UncResCEO_QtrExp_c")
    # Unrated level (two-tailed)
    beta_unr, se_unr, p_two_unr = _extract_coef(model, MOD_UNRATED)

    if use_interactions:
        beta_int_clarity, se_int_clarity, p_two_int_clarity = _extract_coef(model, INT_UNRATED_CLARITY)
        beta_int_uncres, se_int_uncres, p_two_int_uncres = _extract_coef(model, INT_UNRATED_UNCRES)
    else:
        beta_int_clarity, se_int_clarity, p_two_int_clarity = np.nan, np.nan, np.nan
        beta_int_uncres, se_int_uncres, p_two_int_uncres = np.nan, np.nan, np.nan

    # Per-IV directional p (asymmetric per IV_TAIL_DIRECTION)
    def _p_by_dir(b: float, p2: float, direction: str) -> float:
        if np.isnan(p2) or np.isnan(b):
            return float("nan")
        if direction == "positive":
            return p2 / 2 if b > 0 else 1 - p2 / 2
        if direction == "negative":
            return p2 / 2 if b < 0 else 1 - p2 / 2
        return p2  # "none" → two-tailed

    p_clarity = _p_by_dir(beta_clarity, p_two_clarity, IV_TAIL_DIRECTION["ClarityCEO_QtrExp_c"])
    p_uncres = _p_by_dir(beta_uncres, p_two_uncres, IV_TAIL_DIRECTION["UncResCEO_QtrExp_c"])
    p_int_clarity = _p_by_dir(beta_int_clarity, p_two_int_clarity, IV_TAIL_DIRECTION[INT_UNRATED_CLARITY])
    p_int_uncres = _p_by_dir(beta_int_uncres, p_two_int_uncres, IV_TAIL_DIRECTION[INT_UNRATED_UNCRES])

    print(f"  [OK] {elapsed:.1f}s | R2={model.rsquared:.4f}  Adj R2={1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid:.4f}")
    print(f"  ClarityCEO_QtrExp_c: b={beta_clarity:.4f} p(neg-tail)={p_clarity:.4f} {_sig_stars_one(p_clarity)}")
    print(f"  UncResCEO_QtrExp_c:  b={beta_uncres:.4f} p(pos-tail)={p_uncres:.4f} {_sig_stars_one(p_uncres)}")
    print(f"  {MOD_UNRATED}: b={beta_unr:.4f} p2={p_two_unr:.4f}")
    if use_interactions:
        print(f"  {INT_UNRATED_CLARITY}: b={beta_int_clarity:.4f} p2={p_int_clarity:.4f} "
              f"{_sig_stars_one(p_int_clarity)}  [two-tail]")
        print(f"  {INT_UNRATED_UNCRES}: b={beta_int_uncres:.4f} p1(pos)={p_int_uncres:.4f} "
              f"{_sig_stars_one(p_int_uncres)}")

    n_unrated = int(df_prepared[MOD_UNRATED].sum())
    n_rated = int((df_prepared[MOD_UNRATED] == 0).sum())

    meta = {
        "col": col_num, "dv": dv, "fe": fe,
        "interactions": use_interactions,
        "n_obs": int(model.nobs), "n_firms": n_firms, "n_time_periods": n_time_periods,
        "r2": float(model.rsquared),
        "adj_r2": 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid,
        "dv_mean": float(model.model.dependent.dataframe.mean().iloc[0]),
        # Main Clarity (one-tail NEG)
        "beta_iv_clarity": beta_clarity, "se_iv_clarity": se_clarity,
        "p_iv_clarity": p_clarity, "p_two_iv_clarity": p_two_clarity,
        # Main UncRes (one-tail POS)
        "beta_iv_uncres": beta_uncres, "se_iv_uncres": se_uncres,
        "p_iv_uncres": p_uncres, "p_two_iv_uncres": p_two_uncres,
        # Unrated level (two-tailed)
        "beta_unrated": beta_unr, "se_unrated": se_unr, "p_two_unrated": p_two_unr,
        # Interaction Clarity x Unrated (TWO-TAIL)
        "beta_int_clarity_unrated": beta_int_clarity, "se_int_clarity_unrated": se_int_clarity,
        "p_int_clarity_unrated": p_int_clarity, "p_two_int_clarity_unrated": p_two_int_clarity,
        # Interaction UncRes x Unrated (one-tail POS)
        "beta_int_uncres_unrated": beta_int_uncres, "se_int_uncres_unrated": se_int_uncres,
        "p_int_uncres_unrated": p_int_uncres, "p_two_int_uncres_unrated": p_two_int_uncres,
        "extra_controls": ",".join(extra_controls) if extra_controls else "",
        # VIF
        "vif_int_clarity_unrated": vif.get(INT_UNRATED_CLARITY, np.nan) if (vif and use_interactions) else np.nan,
        "vif_int_uncres_unrated": vif.get(INT_UNRATED_UNCRES, np.nan) if (vif and use_interactions) else np.nan,
        # Counts (binary)
        "n_rated": n_rated, "n_unrated": n_unrated,
        "sample_years": f"{YEAR_MIN}-{YEAR_MAX}",
    }

    return model, meta


def _sig_stars_one(p: float) -> str:
    if np.isnan(p): return ""
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


def _sig_stars_two(p: float) -> str:
    if np.isnan(p): return ""
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


# ==============================================================================
# Output
# ==============================================================================


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Write 8-column LaTeX table: 4 interaction CashRatio_t + 4 interaction CashRatio_lead.

    Mirrors parent display intent: shows interaction cols (5-8 + 13-16) only.
    """
    results_by_col = {}
    for r in all_results:
        meta = r.get("meta", {})
        if meta:
            results_by_col[meta["col"]] = meta

    def fmt_coef(val: float, stars: str) -> str:
        if np.isnan(val): return ""
        return f"{val:.4f}{stars}"

    def fmt_se(val: float) -> str:
        if np.isnan(val): return ""
        return f"({val:.4f})"

    def fmt_r2(val: float) -> str:
        if np.isnan(val): return ""
        if abs(val) < 0.001: return f"{val:.2e}"
        return f"{val:.3f}"

    display_cols = [5, 6, 7, 8, 13, 14, 15, 16]
    metas = [results_by_col.get(c, {}) for c in display_cols]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{" + SUITE_CAPTION + r"}",
        r"\label{" + SUITE_LABEL + r"}",
        r"\small",
        r"\begin{tabular}{l" + "c" * 8 + "}",
        r"\toprule",
        " & " + " & ".join(f"({i})" for i in range(1, 9)) + r" \\",
        r" & \multicolumn{4}{c}{Cash Holdings$_t$} & \multicolumn{4}{c}{Cash Holdings$_{t+1}$} \\",
        r"\cmidrule(lr){2-5} \cmidrule(lr){6-9}",
        r"\midrule",
    ]

    def _row(label, key_b, key_se, key_p, stars_fn):
        parts_b = []
        parts_se = []
        for m in metas:
            parts_b.append(fmt_coef(m.get(key_b, np.nan), stars_fn(m.get(key_p, np.nan))))
            parts_se.append(fmt_se(m.get(key_se, np.nan)))
        lines.append(f"{label} & {' & '.join(parts_b)} \\\\")
        lines.append(f" & {' & '.join(parts_se)} \\\\")

    # Main ClarityCEO_c (one-tail NEG)
    _row(r"ClarityCEO\_QtrExp\_c", "beta_iv_clarity", "se_iv_clarity",
         "p_iv_clarity", _sig_stars_one)
    # Main UncResCEO_c (one-tail POS)
    _row(r"UncResCEO\_QtrExp\_c", "beta_iv_uncres", "se_iv_uncres",
         "p_iv_uncres", _sig_stars_one)
    # Unrated level (two-tailed)
    _row("Unrated", "beta_unrated", "se_unrated", "p_two_unrated", _sig_stars_two)
    # Interaction: ClarityCEO x Unrated (TWO-TAIL)
    _row(r"ClarityCEO\_c $\times$ Unrated", "beta_int_clarity_unrated",
         "se_int_clarity_unrated", "p_int_clarity_unrated", _sig_stars_two)
    # Interaction: UncResCEO x Unrated (one-tail POS)
    _row(r"UncResCEO\_c $\times$ Unrated", "beta_int_uncres_unrated",
         "se_int_uncres_unrated", "p_int_uncres_unrated", _sig_stars_one)

    lines.append(r"\midrule")
    lines.append(r"Controls & " + " & ".join(["Ext"] * 8) + r" \\")
    # FE row: Industry / Firm
    ind_cells = ["Yes" if results_by_col.get(c, {}).get("fe", "").startswith("industry") else ""
                 for c in display_cols]
    firm_cells = ["Yes" if results_by_col.get(c, {}).get("fe", "").startswith("firm") else ""
                  for c in display_cols]
    yr_cells = ["Yes" if not results_by_col.get(c, {}).get("fe", "").endswith("_yq") else ""
                for c in display_cols]
    yq_cells = ["Yes" if results_by_col.get(c, {}).get("fe", "").endswith("_yq") else ""
                for c in display_cols]
    lines.append(r"Industry FE & " + " & ".join(ind_cells) + r" \\")
    lines.append(r"Firm FE & " + " & ".join(firm_cells) + r" \\")
    lines.append(r"Calendar Year FE & " + " & ".join(yr_cells) + r" \\")
    lines.append(r"Calendar Year-Quarter FE & " + " & ".join(yq_cells) + r" \\")
    lines.append(r"\midrule")

    n_row = " & ".join(f"{m.get('n_obs', 0):,}" for m in metas)
    lines.append(f"N (calls) & {n_row} \\\\")
    r2_row = " & ".join(fmt_r2(m.get("r2", np.nan)) for m in metas)
    lines.append(f"$R^2$ & {r2_row} \\\\")
    ar2_row = " & ".join(fmt_r2(m.get("adj_r2", np.nan)) for m in metas)
    lines.append(f"Adj.~$R^2$ & {ar2_row} \\\\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$. ",
        r"DWZ Eq.5 decomposition variant of H1.2.ceo2: replaces (UncAnsCEO\_c, UncPreCEO\_c) ",
        r"with the persistent CEO-trait component \textit{ClarityCEO\_c} (= negated CEO ",
        r"fixed effect from DWZ Eq.4) and the call-level state residual \textit{UncResCEO\_c}, ",
        r"both estimated under strict no-look-ahead quarterly-expanding window, then mean-centered ",
        r"on the Main sample. ",
        r"\textit{ClarityCEO\_c}: one-tailed NEG ($\beta < 0$; high persistent clarity $\Rightarrow$ less cash). ",
        r"\textit{UncResCEO\_c}: one-tailed POS ($\beta > 0$; positive within-quarter uncertainty $\Rightarrow$ more cash). ",
        r"\textit{UncResCEO} $\times$ Unrated: one-tailed POS (HFC amplification at state level). ",
        r"\textit{ClarityCEO} $\times$ Unrated: two-tailed (no theoretical prior for trait-level moderation). ",
        r"Unrated level dummy: two-tailed. ",
        r"Moderator is BINARY: Unrated vs Rated reference group (FP 2006 specification; ",
        r"Rated $=$ any S\&P long-term issuer rating). ",
        r"Rating matched via merge\_asof to most recent rating before call date. ",
        r"Standard errors (in parentheses) firm-level clustered. ",
        r"Main sample (excludes financial and utility firms). ",
        r"Sample restricted to fiscal years 2002--2016 (ratings coverage). ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h1_2_cash_constraint_ceo2iv_decomp_table.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: {tex_path.name}")


def save_outputs(all_results: List[Dict[str, Any]], out_dir: Path) -> pd.DataFrame:
    """Save all outputs."""
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    for r in all_results:
        model = r.get("model")
        meta = r.get("meta", {})
        if model is None or not meta:
            continue
        col_num = meta["col"]
        has_int = meta.get("interactions", True)
        fname = f"regression_results_col{col_num}.txt"
        with open(out_dir / fname, "w", encoding="utf-8") as f:
            spec_type = "Interaction" if has_int else "Base"
            f.write(f"H1.2 CEO 2-IV Decomposed Financing-Constraint-Moderated Cash Holdings [{spec_type}]\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"IVs: {', '.join(IVS_RAW)} (DWZ Eq.5 qtr-exp; mean-centered)\n")
            f.write(f"Moderator: Unrated only (binary; FP 2006)\n")
            if has_int:
                f.write(f"Interactions: {', '.join(INT_UNRATED_TERMS)}\n")
                f.write(f"Tail: ClarityxUnrated TWO-TAIL; UncResxUnrated one-tail POS\n")
            else:
                f.write(f"Interactions: none (base model)\n")
            f.write(f"FE: {meta['fe']}\n")
            f.write(f"Sample years: {YEAR_MIN}-{YEAR_MAX}\n")
            f.write(f"Extra controls: {meta.get('extra_controls', '')}\n")
            if has_int:
                f.write(f"VIF(int_clarity_unrated): {meta.get('vif_int_clarity_unrated', 'N/A')}\n")
                f.write(f"VIF(int_uncres_unrated): {meta.get('vif_int_uncres_unrated', 'N/A')}\n")
            f.write(f"N: Rated={meta['n_rated']}, Unrated={meta['n_unrated']}\n")
            f.write(f"Adj_R2: {meta['adj_r2']:.10f}\n")
            f.write("=" * 60 + "\n\n")
            f.write(str(model.summary))
        print(f"  Saved: {fname}")

    diag_rows = [r["meta"] for r in all_results if r.get("meta")]
    diag_df = pd.DataFrame(diag_rows)
    diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False, float_format="%.10f")
    print(f"  Saved: model_diagnostics.csv ({len(diag_df)} models)")

    _save_latex_table(all_results, out_dir)

    return diag_df


def generate_report(
    all_results: List[Dict[str, Any]], out_dir: Path,
    duration: float, iv_means: Dict[str, float],
) -> None:
    """Generate markdown report for CEO 2-IV decomposed variant."""
    iv_means_str = ", ".join(f"{k}={v:.4f}" for k, v in iv_means.items())
    lines = [
        "# H1.2 CEO 2-IV DECOMP Financing-Constraint-Moderated Cash Holdings Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        f"**Design:** ClarityCEO_c (NEG), UncResCEO_c (POS) × Unrated interactions",
        f"          (DWZ Eq.5 qtr-expanding decomposition; binary Unrated moderator per FP 2006)",
        f"**Tails:** Clarity NEG, UncRes POS (mains); UncRes×Unrated POS, Clarity×Unrated TWO-TAIL",
        f"**Channel:** CH1 — Precautionary liquidity under external-finance frictions",
        f"**IV centering means:** {iv_means_str}",
        f"**Sample years:** {YEAR_MIN}-{YEAR_MAX}",
        f"**Parent suite:** H1.2.ceo2 (Cash × Constraint, UncAns/UncPre)",
        "",
        "## Results",
        "",
        "| Col | DV | Spec | b_clarity (p) | b_uncres (p) | b_int_clarity (p2) | b_int_uncres (p1) | N | R2 |",
        "|-----|----|------|---------------|--------------|---------------------|--------------------|---|-----|",
    ]

    for r in all_results:
        m = r.get("meta", {})
        if not m:
            continue
        s_cl = _sig_stars_one(m["p_iv_clarity"])
        s_un = _sig_stars_one(m["p_iv_uncres"])
        if m.get("interactions"):
            s_int_cl = _sig_stars_two(m["p_int_clarity_unrated"])
            s_int_un = _sig_stars_one(m["p_int_uncres_unrated"])
            int_cl_str = f"{m['beta_int_clarity_unrated']:.4f}{s_int_cl} ({m['p_int_clarity_unrated']:.3f})"
            int_un_str = f"{m['beta_int_uncres_unrated']:.4f}{s_int_un} ({m['p_int_uncres_unrated']:.3f})"
        else:
            int_cl_str = "—"
            int_un_str = "—"
        spec_label = "Int" if m.get("interactions") else "Base"
        lines.append(
            f"| ({m['col']}) | {m['dv']} | {spec_label} | "
            f"{m['beta_iv_clarity']:.4f}{s_cl} ({m['p_iv_clarity']:.3f}) | "
            f"{m['beta_iv_uncres']:.4f}{s_un} ({m['p_iv_uncres']:.3f}) | "
            f"{int_cl_str} | {int_un_str} | "
            f"{m['n_obs']:,} | {m['r2']:.4f} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "- b_clarity (NEG): persistent CEO clarity → less precautionary cash (rated firms baseline)",
        "- b_uncres (POS): within-quarter uncertainty surprise → more cash (rated firms baseline)",
        "- b_int_uncres (POS): HFC amplification at state level for unrated firms",
        "- b_int_clarity (two-tail): no theory prior on trait-level moderation by constraint status",
        "- Reference group: Rated (IG ∪ BelowIG) firms; binary moderator per FP 2006",
    ]

    with open(out_dir / "report_step4_H1_2_ceo2iv_decomp.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: report_step4_H1_2_ceo2iv_decomp.md")


def _write_suite_spec_json(
    all_results: List[Dict[str, Any]],
    out_dir: Path,
) -> None:
    """Emit canonical suite_spec_H1.2.ceo2.decomp.json from runner state.

    16 underlying regressions:
      - Cols 1-4:  unconditional, DV=CashRatio_t
      - Cols 5-8:  interaction,   DV=CashRatio_t
      - Cols 9-12: unconditional, DV=CashRatio_lead
      - Cols 13-16: interaction,  DV=CashRatio_lead

    Display table = 8 cols: interaction cols 5-8 + 13-16. Main decomp IV slopes
    (ClarityCEO_c, UncResCEO_c) come from matched UNCONDITIONAL spec
    (interaction_col - 4); moderator level + Unrated interactions from
    interaction spec. Per-IV directional p stitched across 3 directions
    (positive/negative/none) per IV_TAIL_DIRECTION.
    """
    results_by_col = {
        r["meta"]["col"]: r for r in all_results if r.get("meta")
    }

    col_metadata: List[Dict[str, Any]] = []
    coefs_per_col: List[Dict[str, Dict[str, Any]]] = []

    display_cols = [5, 6, 7, 8, 13, 14, 15, 16]
    for interaction_col in display_cols:
        if interaction_col not in results_by_col:
            raise RuntimeError(
                f"H1.2.ceo2 spec build: missing interaction result for col {interaction_col}"
            )
        unconditional_col = interaction_col - 4
        if unconditional_col not in results_by_col:
            raise RuntimeError(
                f"H1.2.ceo2 spec build: missing unconditional result for col {unconditional_col}"
            )

        int_entry = results_by_col[interaction_col]
        int_model = int_entry["model"]
        int_meta = int_entry["meta"]
        uncond_entry = results_by_col[unconditional_col]
        uncond_model = uncond_entry["model"]

        spec = next(s for s in MODEL_SPECS if s["col"] == interaction_col)
        fe = spec["fe"]
        base_fe = fe.replace("_yq", "")
        fe_entity = "industry" if base_fe == "industry" else "firm"
        fe_time = (
            "calendar_year_quarter" if fe.endswith("_yq") else "calendar_year"
        )

        extra_controls = spec.get("extra_controls", [])
        control_vars = list(CONTROLS) + list(extra_controls)

        try:
            dv_mean: Optional[float] = float(
                int_model.model.dependent.dataframe.mean().iloc[0]
            )
        except Exception:
            dv_mean = None

        col_metadata.append(
            {
                "col": len(col_metadata) + 1,
                "dv": spec["dv"],
                "fe_entity": fe_entity,
                "fe_time": fe_time,
                "control_vars": control_vars,
                "n_obs": int(int_meta["n_obs"]),
                "n_firms": int(int_meta.get("n_firms", 0)) or None,
                "r2": float(int_meta["r2"]),
                "adj_r2": float(int_meta.get("adj_r2", float("nan"))),
                "dv_mean": dv_mean,
                "cluster_fallback": False,
            }
        )

        # Interaction-model coefs: Unrated level + 2 Unrated interactions.
        # MOD_UNRATED level treated as two-tailed (no directional prior on level shift).
        interaction_vars = [
            MOD_UNRATED,
            INT_UNRATED_CLARITY,
            INT_UNRATED_UNCRES,
        ]

        # Per-IV directional stitching across 3 directions
        merged_int: Dict[str, Dict[str, Any]] = {}
        for direction in ("positive", "negative", "none"):
            ivs_for_dir = [
                v for v in interaction_vars
                if (IV_TAIL_DIRECTION.get(v, "none") == direction)
                or (v == MOD_UNRATED and direction == "none")
            ]
            if not ivs_for_dir:
                continue
            coefs = extract_coefs_panelols(
                model=int_model,
                key_ivs=ivs_for_dir,
                all_vars=interaction_vars + control_vars,
                hyp_dir=direction,
            )
            for v in ivs_for_dir:
                if v in coefs:
                    merged_int[v] = coefs[v]

        # Main decomp IV slopes from unconditional spec (per-IV direction).
        merged_main: Dict[str, Dict[str, Any]] = {}
        for direction in ("positive", "negative"):
            ivs_for_dir = [
                ivc for ivc in IVS_CENTERED
                if IV_TAIL_DIRECTION.get(ivc) == direction
            ]
            if not ivs_for_dir:
                continue
            coefs = extract_coefs_panelols(
                model=uncond_model,
                key_ivs=ivs_for_dir,
                all_vars=list(IVS_CENTERED),
                hyp_dir=direction,
            )
            for ivc in ivs_for_dir:
                if ivc in coefs:
                    merged_main[ivc] = coefs[ivc]

        merged: Dict[str, Dict[str, Any]] = dict(merged_main)
        merged.update(merged_int)
        coefs_per_col.append(merged)

    # Display IVs (decomp): 2 main + Unrated level + 2 Unrated interactions.
    # Tail values per IV_TAIL_DIRECTION (asymmetric).
    ivs = [
        {"name": "ClarityCEO_QtrExp_c",
         "label": r"ClarityCEO\_QtrExp\_c", "tail": "one_neg"},
        {"name": "UncResCEO_QtrExp_c",
         "label": r"UncResCEO\_QtrExp\_c", "tail": "one_pos"},
        {"name": MOD_UNRATED, "label": "Unrated", "tail": "two"},
        {"name": INT_UNRATED_CLARITY,
         "label": r"ClarityCEO\_c $\times$ Unrated", "tail": "two"},
        {"name": INT_UNRATED_UNCRES,
         "label": r"UncResCEO\_c $\times$ Unrated", "tail": "one_pos"},
    ]

    # 8 display cols: 4 CashRatio_t + 4 CashRatio_lead
    header_rows = [
        [
            {"label": "CashRatio", "span": 4},
            {"label": r"CashRatio\_lead", "span": 4},
        ]
    ]

    paths = write_suite_spec(
        output_dir=out_dir,
        runner_id=SUITE_DIR_NAME,
        sub_tables=[
            {
                "suite_id": SUITE_ID,
                "dir_name": SUITE_DIR_NAME,
                "title": SUITE_TITLE,
                "caption": SUITE_CAPTION,
                "label": SUITE_LABEL,
                "col_range": list(range(1, len(col_metadata) + 1)),
                "header_rows": header_rows,
                "suite_type": "moderation",
            }
        ],
        coefs_per_col=coefs_per_col,
        col_metadata=col_metadata,
        sample_label=SAMPLE_LABEL,
        clustering=CLUSTERING,
        tail=TAIL,
        ivs=ivs,
        controls={
            "base": list(CONTROLS),
            "extended_only": list(EXTENDED_ONLY_CONTROLS),
        },
        model_family="PanelOLS",
    )
    for path in paths:
        print(f"  Saved: {path.name}")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / SUITE_DIR_NAME / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H1_2_CashConstraint_ceo2iv_decomp",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H1.2 CEO 2-IV DECOMP Financing-Constraint-Moderated Cash Holdings")
    print("=" * 80)
    print(f"Timestamp:  {timestamp}")
    print(f"Output:     {out_dir}")
    print(f"Design:     2 decomp IVs × 2 DVs × (base + interaction) × 4 FE types = 16 models (8 displayed)")
    print(f"Channel:    CH1 — Precautionary liquidity under external-finance frictions")
    print(f"Moderator:  Binary Unrated vs Rated (FP 2006)")
    print(f"IVs:        {', '.join(IVS_RAW)}  (DWZ Eq.5 qtr-expanding)")
    print(f"Tails:      Clarity NEG / UncRes POS / UncRes×Unrated POS / Clarity×Unrated TWO-TAIL")
    print(f"Sample:     {YEAR_MIN}-{YEAR_MAX}")

    # Load panel + merge decomp parquet
    panel, panel_file = load_panel(root, panel_path)

    # Merge S&P credit ratings via merge_asof (binary Unrated only)
    panel = load_and_merge_ratings(panel, root)

    # Filter to sample years
    before_year = len(panel)
    panel = panel[panel["fyearq_int"].between(YEAR_MIN, YEAR_MAX)].copy()
    print(f"\n  Year filter ({YEAR_MIN}-{YEAR_MAX}): {len(panel):,} / {before_year:,} "
          f"(dropped {before_year - len(panel):,})")

    # Center both decomp IVs on Main sample
    panel, iv_means = center_iv(panel)

    # Filter to Main sample
    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)

    n_unrated = int(panel[MOD_UNRATED].sum())
    n_rated = int((panel[MOD_UNRATED] == 0).sum())

    print(f"\n  Main sample: {main_n:,} calls, {panel['gvkey'].nunique():,} firms")
    print(f"  Binary (Main): {n_rated:,} Rated ({100*n_rated/main_n:.1f}%) / "
          f"{n_unrated:,} Unrated ({100*n_unrated/main_n:.1f}%)")

    # Summary stats
    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics --- H1.2 CEO 2-IV Decomp Cash Holdings (Main Sample, 2002--2016)",
        label="tab:summary_stats_h1_2_ceo2_decomp",
    )
    print("  Saved: summary_stats.csv/.tex")

    # Run 2 regressions
    all_results: List[Dict[str, Any]] = []

    for spec in MODEL_SPECS:
        print(f"\n--- Model ({spec['col']}): DV={spec['dv']} ---")
        try:
            df_prep = prepare_regression_data(panel, spec)
        except ValueError as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            continue
        if len(df_prep) < 100:
            print(f"  Skipping: too few obs")
            continue

        model, meta = run_regression(df_prep, spec)
        if model is not None and meta:
            all_results.append({"model": model, "meta": meta})

    # Save outputs
    diag_df = save_outputs(all_results, out_dir)
    _write_suite_spec_json(all_results, out_dir)

    # Attrition
    if all_results:
        first = all_results[0]["meta"]
        attrition_stages = [
            ("Full panel (H1)", full_n + (before_year - len(panel.index))),
            (f"Year filter ({YEAR_MIN}-{YEAR_MAX})", full_n),
            ("Main sample (excl Finance/Utility)", main_n),
            ("Rated firms (reference)", n_rated),
            ("Unrated firms", n_unrated),
            ("After complete-case + min-calls (col 1)", first["n_obs"]),
        ]
        generate_attrition_table(
            attrition_stages, out_dir,
            "H1.2 CEO 2-IV DECOMP Financing-Constraint-Moderated Cash Holdings",
        )
        print("  Saved: sample_attrition.csv/.tex")

    # Manifest
    generate_manifest(
        output_dir=out_dir, stage="stage4", timestamp=timestamp,
        input_paths={
            "panel": panel_file,
            "ratings": root / "inputs" / "compustat_daily_ratings" / "compustat_daily_ratings.csv",
        },
        output_files={"diagnostics": out_dir / "model_diagnostics.csv"},
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    # Report
    duration = (datetime.now() - start_time).total_seconds()
    generate_report(all_results, out_dir, duration, iv_means)

    # Summary
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f}s")
    print(f"Regressions: {len(all_results)}/{len(MODEL_SPECS)}")

    for r in all_results:
        m = r["meta"]
        s_cl = _sig_stars_one(m["p_iv_clarity"])
        s_un = _sig_stars_one(m["p_iv_uncres"])
        if m.get("interactions"):
            s_int_cl = _sig_stars_two(m["p_int_clarity_unrated"])
            s_int_un = _sig_stars_one(m["p_int_uncres_unrated"])
            print(f"  Col ({m['col']}) {m['dv']} [int]: "
                  f"Clarity b={m['beta_iv_clarity']:.4f}{s_cl} | "
                  f"UncRes b={m['beta_iv_uncres']:.4f}{s_un} | "
                  f"Int(Cl×Unr,2t) b={m['beta_int_clarity_unrated']:.4f}{s_int_cl} | "
                  f"Int(Un×Unr,1t+) b={m['beta_int_uncres_unrated']:.4f}{s_int_un}")
        else:
            print(f"  Col ({m['col']}) {m['dv']} [base]: "
                  f"Clarity b={m['beta_iv_clarity']:.4f}{s_cl} | "
                  f"UncRes b={m['beta_iv_uncres']:.4f}{s_un}")

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("Dry-run: validating...")
        print(f"  IVs: {', '.join(IVS_RAW)}")
        print(f"  Centered: {', '.join(IVS_CENTERED)}")
        print(f"  Specs: {len(MODEL_SPECS)}")
        print(f"  Controls: {len(CONTROLS)}")
        print(f"  Moderator: {MOD_UNRATED} (binary)")
        print(f"  Interactions: {', '.join(INT_UNRATED_TERMS)}")
        print(f"  IV_TAIL_DIRECTION: {IV_TAIL_DIRECTION}")
        print(f"  Sample years: {YEAR_MIN}-{YEAR_MAX}")
        print("[OK]")
        sys.exit(0)
    sys.exit(main(panel_path=args.panel_path))
