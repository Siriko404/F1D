#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H1.2 Financing-Constraint-Moderated Cash Holdings Hypothesis
================================================================================
ID: econometric/run_h1_2_cash_constraint
Description: Test whether the UncAnsMgr → CashRatio relationship
             is stronger for financially constrained firms, distinguishing
             below-investment-grade rated firms from unrated firms.

Channel: CH1 — Precautionary liquidity under external-finance frictions
    Literature: Almeida, Campello & Weisbach (2004); Acharya, Almeida & Campello
    (2007); Bates, Kahle & Stulz (2009).

Model Specification (three-category moderator):
    CashRatio = b1*Unc_c + b2*BelowIG + b3*Unrated
              + b4*(Unc_c x BelowIG) + b5*(Unc_c x Unrated)
              + controls + IndustryFE + CalendarYearFE + e

    Reference group: Investment-grade firms (BBB- and above).
    b4 = clean CH1 test: does the uncertainty→cash link strengthen for junk-rated firms?
    b5 = does it strengthen for unrated firms? (noisier, heterogeneous population)
    b1 = effect for IG firms alone (reference group)
    b2, b3 = level shifts at mean uncertainty

    L1 fix: separates below-IG (genuine credit-constrained, ~23% of Main sample)
    from unrated (heterogeneous, ~52%) which were previously conflated in a single
    binary moderator. Below-IG firms hold LESS cash than IG (0.102 vs 0.106);
    unrated firms hold far more (0.237). The binary moderator was mixing opposite signals.

Parent suite: H1 (Cash Holdings)

2 Models:
    Col 1: DV = CashRatio_t, Industry + Calendar Year FE, Extended controls
    Col 2: DV = CashRatio_t, Industry + Calendar Year-Quarter FE, Extended controls

Moderator: Three-category from S&P splticrm (Compustat Daily Ratings)
    IG (reference): BBB- and above (both dummies = 0)
    BelowIG: BB+ through SD (rated junk)
    Unrated: no splticrm match (no S&P rating)
    Merge: merge_asof on (gvkey, start_date) to avoid look-ahead bias.

Sample: Main only (FF12 not in {8, 11}). Fiscal years 2002-2016 (ratings end 2017-02).
Hypothesis: All 6 top-of-table IVs one-tailed positive (per user directive
    2026-04-14). Financial constraint + uncertainty predicts more cash
    holding: main IV, BelowIG/Unrated level shifts, IG-slope, and both
    differential interactions are all β > 0. β-sign-gated stars suppress
    any empirical coefficient whose sign contradicts the hypothesis.
Unit: Call-level. Panel index: ["gvkey", "cal_yr"] or ["gvkey", "cal_yr_qtr"]. SEs: Firm-clustered.

Inputs:
    - outputs/variables/h13_capex/latest/h13_capex_panel.parquet
    - inputs/compustat_daily_ratings/compustat_daily_ratings.csv

Outputs:
    - outputs/econometric/h1_2_cash_constraint/{timestamp}/...

Deterministic: true
Author: Thesis Author
Date: 2026-03-19
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

IV = "UncAnsCEO"
IV_CENTERED = "UncAnsCEO_c"  # mean-centered on Main sample
IV_CENTERED_IG = "UncAnsCEO_c_x_IG"  # same variable, renamed in interaction specs

CONTROLS = [
    "lnAssets", "TobinsQ", "ROA", "Leverage", "CashRatio",
    "DivDummy", "sCFO",
    "SalesGrowth", "RDSales", "CashFlowAt", "DailyVola",
    "Lagged_DV",  # Unified lagged DV
]

# Three-category moderator (reference = IG)
MOD_BELOW_IG = "BelowIG"
MOD_UNRATED = "Unrated"
INT_BELOW_IG = "UncAnsCEO_c_x_BelowIG"
INT_UNRATED = "UncAnsCEO_c_x_Unrated"

# Investment-grade rating codes (BBB- and above)
IG_RATINGS = {"AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-"}

MIN_CALLS_PER_FIRM = 5
YEAR_MIN = 2002
YEAR_MAX = 2016

# ------------------------------------------------------------------
# Suite metadata for suite_spec.json emission.
# H1.2 displays cols 5-8 (interaction specs). The top IV row
# (UncAnsMgr_c) pulls from cols 1-4 (unconditional specs) — the
# spec builder merges both sources into each column's coefs dict so the
# renderer sees 6 top-of-table variables.
# ------------------------------------------------------------------
SUITE_ID = "H13.3"
SUITE_DIR_NAME = "h13_3_capex_constraint"
SUITE_TITLE = (
    "Financial Constraint-Moderated Speech Uncertainty and Capital Expenditure "
    "(Three-Category, CEO Q&A)"
)
SUITE_CAPTION = (
    "H13.3: Financial Constraint--Moderated Speech Uncertainty and Capital Expenditure "
    "(Three-Category, CEO Q\\&A)"
)
SUITE_LABEL = "tab:h13_3"
SAMPLE_LABEL = "Main sample (excludes financial and utility firms). Fiscal years 2002-2016."
HYP_DIR = "positive"  # main IV expected beta > 0
CLUSTERING = {"entity": True, "time": False}
TAIL = {"direction": HYP_DIR, "applies_to": "ivs_only"}
EXTENDED_ONLY_CONTROLS: List[str] = []

MODEL_SPECS = [
    # Block 1: CashRatio_t
    # Unconditional specs (no interactions): cols 1-4, full FE ladder
    {"col": 1, "dv": "Capex",      "fe": "industry",    "extra_controls": [], "interactions": False},
    {"col": 2, "dv": "Capex",      "fe": "firm",        "extra_controls": [], "interactions": False},
    {"col": 3, "dv": "Capex",      "fe": "industry_yq", "extra_controls": [], "interactions": False},
    {"col": 4, "dv": "Capex",      "fe": "firm_yq",     "extra_controls": [], "interactions": False},
    # Interaction specs (IG-reference conditional effect): cols 5-8, full FE ladder
    {"col": 5, "dv": "Capex",      "fe": "industry",    "extra_controls": [], "interactions": True},
    {"col": 6, "dv": "Capex",      "fe": "firm",        "extra_controls": [], "interactions": True},
    {"col": 7, "dv": "Capex",      "fe": "industry_yq", "extra_controls": [], "interactions": True},
    {"col": 8, "dv": "Capex",      "fe": "firm_yq",     "extra_controls": [], "interactions": True},
    # Block 2: Capex_lead (one-quarter-ahead)
    # Unconditional specs: cols 9-12
    {"col":  9, "dv": "Capex_lead", "fe": "industry",    "extra_controls": [], "interactions": False},
    {"col": 10, "dv": "Capex_lead", "fe": "firm",        "extra_controls": [], "interactions": False},
    {"col": 11, "dv": "Capex_lead", "fe": "industry_yq", "extra_controls": [], "interactions": False},
    {"col": 12, "dv": "Capex_lead", "fe": "firm_yq",     "extra_controls": [], "interactions": False},
    # Interaction specs: cols 13-16
    {"col": 13, "dv": "Capex_lead", "fe": "industry",    "extra_controls": [], "interactions": True},
    {"col": 14, "dv": "Capex_lead", "fe": "firm",        "extra_controls": [], "interactions": True},
    {"col": 15, "dv": "Capex_lead", "fe": "industry_yq", "extra_controls": [], "interactions": True},
    {"col": 16, "dv": "Capex_lead", "fe": "firm_yq",     "extra_controls": [], "interactions": True},
]

DV_TEX = {
    "Capex": r"CapEx/AT$_t$",
    "Capex_lead": r"CapEx/AT$_{t+1}$",
}

SUMMARY_STATS_VARS = [
    {"col": "Capex", "label": "CapEx / Assets$_t$"},
    {"col": "Capex_lead", "label": "CapEx / Assets$_{t+1}$"},
    {"col": IV, "label": "CEO QA Uncertainty (raw)"},
    {"col": IV_CENTERED, "label": "CEO QA Uncertainty (centered)"},
    {"col": MOD_BELOW_IG, "label": "Below-IG (dummy)"},
    {"col": MOD_UNRATED, "label": "Unrated (dummy)"},
    {"col": "Leverage", "label": "Leverage"},
    {"col": "lnAssets", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "CashRatio", "label": "Cash Holdings"},
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
    """Load call-level H13 capex panel from Stage 3 output."""
    print("\n" + "=" * 60)
    print("Loading H13 panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h13_capex",
            required_file="h13_capex_panel.parquet",
        )
        panel_file = panel_dir / "h13_capex_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    columns = [
        "gvkey", "year", "fyearq_int", "ff12_code", "start_date",
        "Capex", "Capex_lag", "Capex_lead",
        IV,
        *[c for c in CONTROLS if c != "Lagged_DV"],  # lagged created dynamically
    ]
    # Deduplicate (CONTROLS may reference vars already in the explicit list)
    columns = list(dict.fromkeys(columns))

    panel = pd.read_parquet(panel_file, columns=columns)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")

    # Build calendar year-quarter index for FE specs
    panel = build_cal_yr_qtr_index(panel)
    n_yr_qtr = panel["cal_yr_qtr"].notna().sum()
    print(f"  cal_yr_qtr coverage: {n_yr_qtr:,}/{len(panel):,} ({100*n_yr_qtr/len(panel):.1f}%)")

    return panel, panel_file


def load_and_merge_ratings(panel: pd.DataFrame, root_path: Path) -> pd.DataFrame:
    """Load S&P credit ratings and merge to panel via merge_asof.

    Three-category classification (L1 fix):
        - BBB- and above → IG (reference group: BelowIG=0, Unrated=0)
        - Below BBB- (BB+ through SD) → BelowIG=1, Unrated=0
        - No splticrm match → BelowIG=0, Unrated=1

    Data: Monthly Compustat Daily Ratings (2000-01 to 2017-02).
    22 rating codes: AAA, AA+, AA, AA-, A+, A, A-, BBB+, BBB, BBB-,
    BB+, BB, BB-, B+, B, B-, CCC+, CCC, CCC-, CC, D, SD.
    """
    print("\n" + "=" * 60)
    print("Merging S&P Credit Ratings (merge_asof, 3-category)")
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

    # Three-category classification
    is_ig = panel["splticrm"].isin(IG_RATINGS)
    has_rating = panel["splticrm"].notna()

    panel[MOD_BELOW_IG] = (has_rating & ~is_ig).astype(float)  # rated but below IG
    panel[MOD_UNRATED] = (~has_rating).astype(float)             # no rating at all
    # IG = reference: both dummies = 0 when splticrm is in IG_RATINGS

    # Diagnostics
    n_ig = is_ig.sum()
    n_below_ig = panel[MOD_BELOW_IG].sum()
    n_unrated = panel[MOD_UNRATED].sum()
    n_total = len(panel)

    print(f"  IG (reference):     {int(n_ig):,} ({100*n_ig/n_total:.1f}%)")
    print(f"  Below-IG (rated):   {int(n_below_ig):,} ({100*n_below_ig/n_total:.1f}%)")
    print(f"  Unrated:            {int(n_unrated):,} ({100*n_unrated/n_total:.1f}%)")

    # Rating distribution for below-IG
    below_ig_mask = has_rating & ~is_ig
    if below_ig_mask.any():
        print(f"  Below-IG rating distribution (top 10):")
        for rating, count in panel.loc[below_ig_mask, "splticrm"].value_counts().head(10).items():
            print(f"    {rating:6s}: {count:,}")

    # Clean up temp columns
    panel = panel.drop(columns=["_start_dt", "_rating_date", "splticrm"], errors="ignore")

    return panel


def center_iv(panel: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
    """Mean-center the IV on Main sample (after FF12 filter, before complete-case)."""
    print("\n" + "=" * 60)
    print("Centering IV on Main sample")
    print("=" * 60)

    main_mask = ~panel["ff12_code"].isin([8, 11])
    iv_main = panel.loc[main_mask, IV].dropna()
    iv_mu = iv_main.mean()

    panel[IV_CENTERED] = panel[IV] - iv_mu

    print(f"  Main sample IV obs: {len(iv_main):,}")
    print(f"  IV mean (Main): {iv_mu:.4f}")
    print(f"  IV centered mean (Main): {panel.loc[main_mask, IV_CENTERED].dropna().mean():.6f}")

    return panel, iv_mu


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

    required = ([dv, IV, IV_CENTERED, MOD_BELOW_IG, MOD_UNRATED]
                + all_controls + ["gvkey", time_col, "ff12_code"])

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    # Create interaction terms only for interaction specs
    if use_interactions:
        df[IV_CENTERED_IG] = df[IV_CENTERED]  # rename: IG-conditional effect
        df[INT_BELOW_IG] = df[IV_CENTERED] * df[MOD_BELOW_IG]
        df[INT_UNRATED] = df[IV_CENTERED] * df[MOD_UNRATED]

    # Drop NaN in DV
    before = len(df)
    df = df[df[dv].notna()].copy()
    print(f"  After DV ({dv}) filter: {len(df):,} / {before:,}")

    # Complete cases
    all_required = required + ([INT_BELOW_IG, INT_UNRATED] if use_interactions else [])
    complete_mask = df[all_required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases: {len(df):,}")

    # Min calls per firm
    firm_counts = df["gvkey"].value_counts()
    valid_firms = set(firm_counts[firm_counts >= MIN_CALLS_PER_FIRM].index)
    df = df[df["gvkey"].isin(valid_firms)].copy()

    n_firms = df["gvkey"].nunique()
    n_time_periods = df.groupby(["gvkey", time_col]).ngroups
    n_ig = int(((df[MOD_BELOW_IG] == 0) & (df[MOD_UNRATED] == 0)).sum())
    n_below_ig = int(df[MOD_BELOW_IG].sum())
    n_unrated = int(df[MOD_UNRATED].sum())
    print(f"  After >={MIN_CALLS_PER_FIRM} calls/firm: "
          f"{len(df):,} calls, {n_firms:,} firms, {n_time_periods:,} firm-time-periods")
    print(f"  Three-category split: {n_ig:,} IG ({100*n_ig/len(df):.1f}%) / "
          f"{n_below_ig:,} Below-IG ({100*n_below_ig/len(df):.1f}%) / "
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
    if use_interactions:
        exog = [IV_CENTERED_IG, MOD_BELOW_IG, MOD_UNRATED,
                INT_BELOW_IG, INT_UNRATED] + all_controls
    else:
        exog = [IV_CENTERED, MOD_BELOW_IG, MOD_UNRATED] + all_controls

    n_firms = df_prepared["gvkey"].nunique()
    n_time_periods = df_prepared.groupby(["gvkey", time_col]).ngroups
    print(f"  N={len(df_prepared):,}, firms={n_firms:,}, firm-time-periods={n_time_periods:,}")
    if extra_controls:
        print(f"  Extra controls: {extra_controls}")

    # VIF
    vif = compute_vif(df_prepared, exog)
    if vif and use_interactions:
        print(f"  VIF({INT_BELOW_IG}): {vif.get(INT_BELOW_IG, np.nan):.2f}")
        print(f"  VIF({INT_UNRATED}): {vif.get(INT_UNRATED, np.nan):.2f}")
        print(f"  VIF({MOD_BELOW_IG}): {vif.get(MOD_BELOW_IG, np.nan):.2f}")
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

    # Extract key coefficients
    iv_name = IV_CENTERED_IG if use_interactions else IV_CENTERED
    beta_iv, se_iv, p_two_iv = _extract_coef(model, iv_name)
    beta_big, se_big, p_two_big = _extract_coef(model, MOD_BELOW_IG)
    beta_unr, se_unr, p_two_unr = _extract_coef(model, MOD_UNRATED)

    if use_interactions:
        beta_int_big, se_int_big, p_two_int_big = _extract_coef(model, INT_BELOW_IG)
        beta_int_unr, se_int_unr, p_two_int_unr = _extract_coef(model, INT_UNRATED)
    else:
        beta_int_big, se_int_big, p_two_int_big = np.nan, np.nan, np.nan
        beta_int_unr, se_int_unr, p_two_int_unr = np.nan, np.nan, np.nan

    # One-tailed p for main IV (expected positive)
    if not np.isnan(p_two_iv) and not np.isnan(beta_iv):
        p_one_iv = p_two_iv / 2 if beta_iv > 0 else 1 - p_two_iv / 2
    else:
        p_one_iv = np.nan

    # Lagged DV control if present
    beta_lag_dv, se_lag_dv, p_two_lag_dv = np.nan, np.nan, np.nan
    if "CashRatio" in extra_controls:
        beta_lag_dv, se_lag_dv, p_two_lag_dv = _extract_coef(model, "CashRatio")

    stars_iv = _sig_stars_one(p_one_iv)

    print(f"  [OK] {elapsed:.1f}s | R2={model.rsquared:.4f}  Adj R2={1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid:.4f}")
    print(f"  {IV_CENTERED}: b={beta_iv:.4f} p1={p_one_iv:.4f} {stars_iv}")
    print(f"  {MOD_BELOW_IG}: b={beta_big:.4f} p2={p_two_big:.4f}")
    print(f"  {MOD_UNRATED}: b={beta_unr:.4f} p2={p_two_unr:.4f}")
    if use_interactions:
        stars_int_big = _sig_stars_two(p_two_int_big)
        stars_int_unr = _sig_stars_two(p_two_int_unr)
        print(f"  {INT_BELOW_IG}: b={beta_int_big:.4f} p2={p_two_int_big:.4f} {stars_int_big}")
        print(f"  {INT_UNRATED}: b={beta_int_unr:.4f} p2={p_two_int_unr:.4f} {stars_int_unr}")

    n_ig = int(((df_prepared[MOD_BELOW_IG] == 0) & (df_prepared[MOD_UNRATED] == 0)).sum())
    n_below_ig = int(df_prepared[MOD_BELOW_IG].sum())
    n_unrated = int(df_prepared[MOD_UNRATED].sum())

    meta = {
        "col": col_num, "dv": dv, "fe": fe,
        "interactions": use_interactions,
        "n_obs": int(model.nobs), "n_firms": n_firms, "n_time_periods": n_time_periods,
        "r2": float(model.rsquared),
        "adj_r2": 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid,
        "dv_mean": float(model.model.dependent.dataframe.mean().iloc[0]),
        # Main IV
        "beta_iv": beta_iv, "se_iv": se_iv, "p_one_iv": p_one_iv, "p_two_iv": p_two_iv,
        # Below-IG level
        "beta_below_ig": beta_big, "se_below_ig": se_big, "p_two_below_ig": p_two_big,
        # Unrated level
        "beta_unrated": beta_unr, "se_unrated": se_unr, "p_two_unrated": p_two_unr,
        # Interaction: Below-IG
        "beta_int_below_ig": beta_int_big, "se_int_below_ig": se_int_big, "p_two_int_below_ig": p_two_int_big,
        # Interaction: Unrated
        "beta_int_unrated": beta_int_unr, "se_int_unrated": se_int_unr, "p_two_int_unrated": p_two_int_unr,
        # Lagged DV
        "beta_lag_dv": beta_lag_dv, "se_lag_dv": se_lag_dv, "p_two_lag_dv": p_two_lag_dv,
        "extra_controls": ",".join(extra_controls) if extra_controls else "",
        # VIF
        "vif_int_below_ig": vif.get(INT_BELOW_IG, np.nan) if (vif and use_interactions) else np.nan,
        "vif_int_unrated": vif.get(INT_UNRATED, np.nan) if (vif and use_interactions) else np.nan,
        # Counts
        "n_ig": n_ig, "n_below_ig": n_below_ig, "n_unrated": n_unrated,
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
    """Write 4-column LaTeX table: 2 base + 2 interaction specs."""
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

    m1 = results_by_col.get(1, {})
    m2 = results_by_col.get(2, {})
    m3 = results_by_col.get(3, {})
    m4 = results_by_col.get(4, {})

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Financial Constraint--Moderated Speech Uncertainty and Cash Holdings (Three-Category)}",
        r"\label{tab:h1_2_cash_constraint}",
        r"\small",
        r"\begin{tabular}{lcccc}",
        r"\toprule",
        r" & (1) & (2) & (3) & (4) \\",
        r" & \multicolumn{2}{c}{Base} & \multicolumn{2}{c}{Interaction} \\",
        r"\cmidrule(lr){2-3} \cmidrule(lr){4-5}",
        r" & \multicolumn{4}{c}{Cash Holdings$_t$} \\",
        r"\midrule",
    ]

    def _row(label, key_b, key_se, key_p, stars_fn, cols):
        """Write one coefficient row across specified column metas."""
        parts_b = []
        parts_se = []
        for m in cols:
            parts_b.append(fmt_coef(m.get(key_b, np.nan), stars_fn(m.get(key_p, np.nan))))
            parts_se.append(fmt_se(m.get(key_se, np.nan)))
        lines.append(f"{label} & {' & '.join(parts_b)} \\\\")
        lines.append(f" & {' & '.join(parts_se)} \\\\")

    all_cols = [m1, m2, m3, m4]

    # Main IV — unconditional in cols 1-2, IG-conditional in cols 3-4
    _row(r"Manager\_QA\_Unc\_c", "beta_iv", "se_iv", "p_one_iv", _sig_stars_one, [m1, m2])
    # blank cells for interaction cols on this row — write manually
    # Actually, we need a combined row. Let me do it differently.

    # Redo: write full 4-col rows
    lines.pop()  # remove last two lines we just added
    lines.pop()

    def _row4(label, key_b, key_se, key_p, stars_fn):
        parts_b = []
        parts_se = []
        for m in all_cols:
            parts_b.append(fmt_coef(m.get(key_b, np.nan), stars_fn(m.get(key_p, np.nan))))
            parts_se.append(fmt_se(m.get(key_se, np.nan)))
        lines.append(f"{label} & {' & '.join(parts_b)} \\\\")
        lines.append(f" & {' & '.join(parts_se)} \\\\")

    # Main IV
    _row4(r"Manager\_QA\_Unc\_c", "beta_iv", "se_iv", "p_one_iv", _sig_stars_one)
    # Below-IG level
    _row4("BelowIG", "beta_below_ig", "se_below_ig", "p_two_below_ig", _sig_stars_two)
    # Unrated level
    _row4("Unrated", "beta_unrated", "se_unrated", "p_two_unrated", _sig_stars_two)
    # Interaction: Below-IG (only cols 3-4)
    _row4(r"UncAnsCEO\_c\_x\_BelowIG", "beta_int_below_ig", "se_int_below_ig", "p_two_int_below_ig", _sig_stars_two)
    # Interaction: Unrated (only cols 3-4)
    _row4(r"UncAnsCEO\_c\_x\_Unrated", "beta_int_unrated", "se_int_unrated", "p_two_int_unrated", _sig_stars_two)

    lines.append(r"\midrule")
    lines.append(r"Controls & Ext & Ext & Ext & Ext \\")
    lines.append(r"Industry FE & Yes & Yes & Yes & Yes \\")
    lines.append(r"Calendar Year FE & Yes &  & Yes &  \\")
    lines.append(r"Calendar Year-Quarter FE &  & Yes &  & Yes \\")
    lines.append(r"\midrule")

    n_row = " & ".join(f"{m.get('n_obs', 0):,}" for m in all_cols)
    lines.append(f"N (calls) & {n_row} \\\\")
    ntp_row = " & ".join(f"{m.get('n_time_periods', 0):,}" for m in all_cols)
    lines.append(f"N (firm-time-periods) & {ntp_row} \\\\")
    r2_row = " & ".join(fmt_r2(m.get("r2", np.nan)) for m in all_cols)
    lines.append(f"$R^2$ & {r2_row} \\\\")
    ar2_row = " & ".join(fmt_r2(m.get("adj_r2", np.nan)) for m in all_cols)
    lines.append(f"Adj.~$R^2$ & {ar2_row} \\\\")
    lines.append(f"Sample years & {YEAR_MIN}--{YEAR_MAX} & {YEAR_MIN}--{YEAR_MAX} & {YEAR_MIN}--{YEAR_MAX} & {YEAR_MIN}--{YEAR_MAX} \\\\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$. ",
        r"Main IV (Manager\_QA\_Unc\_c) mean-centered; one-tailed ($\beta > 0$). ",
        r"Interactions and moderator levels: two-tailed. ",
        r"Cols~(1)--(2): base model (unconditional Manager\_QA\_Unc\_c). ",
        r"Cols~(3)--(4): interaction model (Manager\_QA\_Unc\_c = IG-reference conditional effect). ",
        r"Reference group: investment-grade firms (S\&P long-term issuer rating BBB$-$ or above). ",
        r"Below-IG: firms rated BB$+$ through SD. ",
        r"Unrated: firms with no S\&P long-term issuer credit rating. ",
        r"Rating matched via merge\_asof to most recent rating before call date. ",
        r"Standard errors (in parentheses) firm-level clustered. ",
        r"Main sample (excludes financial and utility firms). ",
        r"Sample restricted to fiscal years 2002--2016 (ratings coverage). ",
        r"Cols~(1),(3): Calendar Year FE. Cols~(2),(4): Calendar Year-Quarter FE. ",
        r"Unit of observation: individual earnings call.",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h1_2_cash_constraint_table.tex"
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
            f.write(f"H1.2 Financing-Constraint-Moderated Cash Holdings (3-category) [{spec_type}]\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"IV: {IV} (centered)\n")
            f.write(f"Moderators: BelowIG (dummy), Unrated (dummy). Reference: IG\n")
            if has_int:
                f.write(f"Interactions: {INT_BELOW_IG}, {INT_UNRATED}\n")
            else:
                f.write(f"Interactions: none (base model)\n")
            f.write(f"FE: {meta['fe']}\n")
            f.write(f"Sample years: {YEAR_MIN}-{YEAR_MAX}\n")
            f.write(f"Extra controls: {meta.get('extra_controls', '')}\n")
            if has_int:
                f.write(f"VIF(int_below_ig): {meta.get('vif_int_below_ig', 'N/A')}\n")
                f.write(f"VIF(int_unrated): {meta.get('vif_int_unrated', 'N/A')}\n")
            f.write(f"N: IG={meta['n_ig']}, Below-IG={meta['n_below_ig']}, Unrated={meta['n_unrated']}\n")
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
    duration: float, iv_mu: float,
) -> None:
    """Generate markdown report."""
    lines = [
        "# H1.2 Financing-Constraint-Moderated Cash Holdings Report (3-Category)",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        f"**Design:** UncAnsMgr × BelowIG / Unrated (two interactions)",
        f"**Channel:** CH1 — Precautionary liquidity under external-finance frictions",
        f"**Moderator:** Three-category: IG (ref) / Below-IG / Unrated",
        f"**IV centering mean:** {iv_mu:.4f}",
        f"**FE:** Col 1: Industry + CalYear; Col 2: Industry + CalYrQtr",
        f"**Sample years:** {YEAR_MIN}-{YEAR_MAX}",
        f"**Parent suite:** H1 (Cash Holdings)",
        "",
        "## Results",
        "",
        "| Col | DV | b_iv (p1) | b_int_belowIG (p2) | b_int_unrated (p2) | N | R2 |",
        "|-----|----|-----------|--------------------|--------------------|---|-----|",
    ]

    for r in all_results:
        m = r.get("meta", {})
        if not m:
            continue
        s_iv = _sig_stars_one(m["p_one_iv"])
        s_big = _sig_stars_two(m["p_two_int_below_ig"])
        s_unr = _sig_stars_two(m["p_two_int_unrated"])
        lines.append(
            f"| ({m['col']}) | {m['dv']} | "
            f"{m['beta_iv']:.4f}{s_iv} ({m['p_one_iv']:.3f}) | "
            f"{m['beta_int_below_ig']:.4f}{s_big} ({m['p_two_int_below_ig']:.3f}) | "
            f"{m['beta_int_unrated']:.4f}{s_unr} ({m['p_two_int_unrated']:.3f}) | "
            f"{m['n_obs']:,} | {m['r2']:.4f} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "- b1 (main IV): uncertainty→cash effect for IG firms (reference group)",
        "- b4 (Unc × BelowIG): clean CH1 test — junk-rated firms' differential sensitivity",
        "- b5 (Unc × Unrated): unrated firms' differential sensitivity (noisier)",
        "- If b4 > 0 and significant: CH1 channel supported for genuinely constrained firms",
        "- If both b4 and b5 null: CH1 channel not operative regardless of moderator definition",
    ]

    with open(out_dir / "report_step4_H1_2.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: report_step4_H1_2.md")


def _write_suite_spec_json(
    all_results: List[Dict[str, Any]],
    out_dir: Path,
) -> None:
    """Emit canonical suite_spec_H1.2.json from moderation runner state.

    H1.2 has 16 underlying regressions (after 2026-04-20 lead-DV upgrade):
      - Cols 1-4: unconditional specs, DV=CashRatio_t
      - Cols 5-8: interaction specs, DV=CashRatio_t
      - Cols 9-12: unconditional specs, DV=Capex_lead
      - Cols 13-16: interaction specs, DV=Capex_lead

    The displayed table shows 8 columns corresponding to runner interaction
    cols 5-8 (CashRatio_t) + 13-16 (Capex_lead). For each displayed col:
      1. Uses interaction-model metadata (n_obs, r2, fe, etc.)
      2. Merges BOTH sets of coefs into the col's coefs dict:
         - `UncAnsMgr_c` from the matching unconditional spec (interaction
           col - 4 = unconditional col)
         - All other top-of-table vars + controls from the interaction spec
    """
    results_by_col = {
        r["meta"]["col"]: r for r in all_results if r.get("meta")
    }

    col_metadata: List[Dict[str, Any]] = []
    coefs_per_col: List[Dict[str, Dict[str, Any]]] = []

    # Display interaction cols (CashRatio_t: 5-8; Capex_lead: 13-16),
    # renumber to 1..8 in the spec.
    display_cols = [5, 6, 7, 8, 13, 14, 15, 16]
    for interaction_col in display_cols:
        if interaction_col not in results_by_col:
            raise RuntimeError(
                f"H1.2 spec build: missing interaction result for col {interaction_col}"
            )
        unconditional_col = interaction_col - 4
        if unconditional_col not in results_by_col:
            raise RuntimeError(
                f"H1.2 spec build: missing unconditional result for col {unconditional_col}"
            )

        int_entry = results_by_col[interaction_col]
        int_model = int_entry["model"]
        int_meta = int_entry["meta"]
        uncond_entry = results_by_col[unconditional_col]
        uncond_model = uncond_entry["model"]

        # Locate the MODEL_SPECS row corresponding to the interaction col.
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
                "col": len(col_metadata) + 1,  # renumber to 1..4
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

        # Interaction-model coefs: all vars except the main IV (which comes
        # from the unconditional model instead).
        interaction_vars = [
            MOD_BELOW_IG,
            MOD_UNRATED,
            IV_CENTERED_IG,
            "UncAnsCEO_c_x_BelowIG",
            "UncAnsCEO_c_x_Unrated",
        ]
        # All 5 interaction-block IVs are one-tailed positive per user
        # directive (2026-04-14). Controls (`control_vars`) are filtered
        # out of the directional p_one computation inside the helper.
        interaction_coefs = extract_coefs_panelols(
            model=int_model,
            key_ivs=interaction_vars,
            all_vars=interaction_vars + control_vars,
            hyp_dir="positive",
        )

        # Unconditional-model coef for UncAnsMgr_c (one-tailed positive).
        uncond_coefs = extract_coefs_panelols(
            model=uncond_model,
            key_ivs=[IV_CENTERED],
            all_vars=[IV_CENTERED],
            hyp_dir="positive",
        )

        merged = {}
        if IV_CENTERED in uncond_coefs:
            merged[IV_CENTERED] = uncond_coefs[IV_CENTERED]
        merged.update(interaction_coefs)
        coefs_per_col.append(merged)

    # Display-only suppression (2026-04-18, T53): user requested keeping ONLY
    # the unconditional main IV (UncAnsMgr_c, from cols 1-4) plus the Unrated
    # moderator + Unrated×UncAnsMgr interaction (from cols 5-8). BelowIG main,
    # IG-conditional UncAnsCEO_c_x_IG, and UncAnsCEO_c_x_BelowIG are still
    # ESTIMATED in the underlying regressions (necessary for unbiased
    # coefficients on retained terms) but not shown in the displayed table.
    # All retained IVs one-tailed positive per user directive (2026-04-14).
    ivs = [
        {
            "name": IV_CENTERED,
            "label": r"UncAnsCEO\_c",
            "tail": "one_pos",
        },
        {"name": MOD_UNRATED, "label": "Unrated", "tail": "one_pos"},
        {
            "name": "UncAnsCEO_c_x_Unrated",
            "label": r"UncAnsCEO\_c\_x\_Unrated",
            "tail": "one_pos",
        },
    ]

    # 8 display cols: 4 CashRatio_t + 4 Capex_lead
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
    out_dir = root / "outputs" / "econometric" / "h13_3_capex_constraint" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H13_3_CapexConstraint",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H13.3 Financing-Constraint-Moderated Capital Expenditure (3-Category)")
    print("=" * 80)
    print(f"Timestamp:  {timestamp}")
    print(f"Output:     {out_dir}")
    print(f"Design:     1 IV × 2 DVs × (base + interaction) × 4 FE types = 16 models (8 displayed)")
    print(f"Channel:    CH1 — Precautionary liquidity under external-finance frictions")
    print(f"Moderator:  Three-category: IG (ref) / Below-IG / Unrated")
    print(f"IV:         {IV}")
    print(f"Sample:     {YEAR_MIN}-{YEAR_MAX}")

    # Load panel
    panel, panel_file = load_panel(root, panel_path)

    # Merge S&P credit ratings via merge_asof (three-category)
    panel = load_and_merge_ratings(panel, root)

    # Filter to sample years
    before_year = len(panel)
    panel = panel[panel["fyearq_int"].between(YEAR_MIN, YEAR_MAX)].copy()
    print(f"\n  Year filter ({YEAR_MIN}-{YEAR_MAX}): {len(panel):,} / {before_year:,} "
          f"(dropped {before_year - len(panel):,})")

    # Center IV on Main sample
    panel, iv_mu = center_iv(panel)

    # Filter to Main sample
    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)

    n_ig = int(((panel[MOD_BELOW_IG] == 0) & (panel[MOD_UNRATED] == 0)).sum())
    n_below_ig = int(panel[MOD_BELOW_IG].sum())
    n_unrated = int(panel[MOD_UNRATED].sum())

    print(f"\n  Main sample: {main_n:,} calls, {panel['gvkey'].nunique():,} firms")
    print(f"  Three-category (Main): {n_ig:,} IG ({100*n_ig/main_n:.1f}%) / "
          f"{n_below_ig:,} Below-IG ({100*n_below_ig/main_n:.1f}%) / "
          f"{n_unrated:,} Unrated ({100*n_unrated/main_n:.1f}%)")

    # Summary stats
    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics --- H13.3 Capital Expenditure (3-Category Constraint, Main Sample, 2002--2016)",
        label="tab:summary_stats_h13_3",
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
            ("IG firms (reference)", n_ig),
            ("Below-IG firms", n_below_ig),
            ("Unrated firms", n_unrated),
            ("After complete-case + min-calls (col 1)", first["n_obs"]),
        ]
        generate_attrition_table(
            attrition_stages, out_dir,
            "H13.3 Financing-Constraint-Moderated Capital Expenditure (3-Category)",
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
    generate_report(all_results, out_dir, duration, iv_mu)

    # Summary
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f}s")
    print(f"Regressions: {len(all_results)}/{len(MODEL_SPECS)}")

    for r in all_results:
        m = r["meta"]
        s_iv = _sig_stars_one(m["p_one_iv"])
        if m.get("interactions"):
            s_big = _sig_stars_two(m["p_two_int_below_ig"])
            s_unr = _sig_stars_two(m["p_two_int_unrated"])
            print(f"  Col ({m['col']}) {m['dv']} [interaction]: "
                  f"IV(IG ref) b={m['beta_iv']:.4f}{s_iv} | "
                  f"Int(BelowIG) b={m['beta_int_below_ig']:.4f}{s_big} | "
                  f"Int(Unrated) b={m['beta_int_unrated']:.4f}{s_unr}")
        else:
            print(f"  Col ({m['col']}) {m['dv']} [base]: "
                  f"IV b={m['beta_iv']:.4f}{s_iv}")

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("Dry-run: validating...")
        print(f"  IV: {IV}")
        print(f"  Specs: {len(MODEL_SPECS)}")
        print(f"  Controls: {len(CONTROLS)}")
        print(f"  Moderators: {MOD_BELOW_IG}, {MOD_UNRATED}")
        print(f"  Interactions: {INT_BELOW_IG}, {INT_UNRATED}")
        print(f"  Sample years: {YEAR_MIN}-{YEAR_MAX}")
        print("[OK]")
        sys.exit(0)
    sys.exit(main(panel_path=args.panel_path))
