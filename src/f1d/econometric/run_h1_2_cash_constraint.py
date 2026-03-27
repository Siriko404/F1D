#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H1.2 Financing-Constraint-Moderated Cash Holdings Hypothesis
================================================================================
ID: econometric/run_h1_2_cash_constraint
Description: Test whether the Manager_QA_Uncertainty → CashHoldings relationship
             is stronger for financially constrained firms, distinguishing
             below-investment-grade rated firms from unrated firms.

Channel: CH1 — Precautionary liquidity under external-finance frictions
    Literature: Almeida, Campello & Weisbach (2004); Acharya, Almeida & Campello
    (2007); Bates, Kahle & Stulz (2009).

Model Specification (three-category moderator):
    CashHoldings = b1*Unc_c + b2*BelowIG + b3*Unrated
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
    Col 1: DV = CashHoldings_t, Industry + Calendar Year FE, Extended controls
    Col 2: DV = CashHoldings_t, Industry + Calendar Year-Quarter FE, Extended controls

Moderator: Three-category from S&P splticrm (Compustat Daily Ratings)
    IG (reference): BBB- and above (both dummies = 0)
    BelowIG: BB+ through SD (rated junk)
    Unrated: no splticrm match (no S&P rating)
    Merge: merge_asof on (gvkey, start_date) to avoid look-ahead bias.

Sample: Main only (FF12 not in {8, 11}). Fiscal years 2002-2016 (ratings end 2017-02).
Hypothesis: Two-tailed on interactions (b4, b5 != 0); one-tailed on main IV (b1 > 0).
Unit: Call-level. Panel index: ["gvkey", "cal_yr"] or ["gvkey", "cal_yr_qtr"]. SEs: Firm-clustered.

Inputs:
    - outputs/variables/h1_cash_holdings/latest/h1_cash_holdings_panel.parquet
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
from f1d.shared.outputs import generate_manifest, generate_attrition_table
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import build_cal_yr_qtr_index


# ==============================================================================
# Configuration
# ==============================================================================

IV = "Manager_QA_Uncertainty_pct"
IV_CENTERED = "Manager_QA_Unc_c"  # mean-centered on Main sample

CONTROLS = [
    "BookLev", "Size", "TobinsQ", "ROA", "CapexAt",
    "DividendPayer", "OCF_Volatility",
    "SalesGrowth", "RD_Intensity", "CashFlow", "Volatility",
    "Lagged_DV",  # Unified lagged DV
]

# Three-category moderator (reference = IG)
MOD_BELOW_IG = "BelowIG"
MOD_UNRATED = "Unrated"
INT_BELOW_IG = "MgrQAUnc_x_BelowIG"
INT_UNRATED = "MgrQAUnc_x_Unrated"

# Investment-grade rating codes (BBB- and above)
IG_RATINGS = {"AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-"}

MIN_CALLS_PER_FIRM = 5
YEAR_MIN = 2002
YEAR_MAX = 2016

MODEL_SPECS = [
    {"col": 1, "dv": "CashHoldings", "fe": "industry",    "extra_controls": []},
    {"col": 2, "dv": "CashHoldings", "fe": "industry_yq", "extra_controls": []},
]

SUMMARY_STATS_VARS = [
    {"col": "CashHoldings", "label": "Cash Holdings$_t$"},
    {"col": IV, "label": "Mgr QA Uncertainty (raw)"},
    {"col": IV_CENTERED, "label": "Mgr QA Uncertainty (centered)"},
    {"col": MOD_BELOW_IG, "label": "Below-IG (dummy)"},
    {"col": MOD_UNRATED, "label": "Unrated (dummy)"},
    {"col": "BookLev", "label": "Leverage"},
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "CapexAt", "label": "CapEx / Assets"},
    {"col": "DividendPayer", "label": "Dividend Payer"},
    {"col": "OCF_Volatility", "label": "OCF Volatility"},
    {"col": "SalesGrowth", "label": "Sales Growth"},
    {"col": "RD_Intensity", "label": "R\\&D Intensity"},
    {"col": "CashFlow", "label": "Cash Flow"},
    {"col": "Volatility", "label": "Stock Volatility"},
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
    """Load call-level H1 panel from Stage 3 output."""
    print("\n" + "=" * 60)
    print("Loading H1 panel")
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

    columns = [
        "gvkey", "year", "fyearq_int", "ff12_code", "start_date",
        "CashHoldings", "CashHoldings_lag",
        IV,
        *[c for c in CONTROLS if c != "Lagged_DV"],  # lagged created dynamically
    ]

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

    # Create Lagged_DV: always lag of the base DV (t-1)
    lag_col = f"{dv}_lag"
    panel = panel.copy()
    panel["Lagged_DV"] = panel[lag_col]

    required = ([dv, IV, IV_CENTERED, MOD_BELOW_IG, MOD_UNRATED]
                + all_controls + ["gvkey", time_col, "ff12_code"])

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    # Create two interaction terms: centered IV × each moderator dummy
    df[INT_BELOW_IG] = df[IV_CENTERED] * df[MOD_BELOW_IG]
    df[INT_UNRATED] = df[IV_CENTERED] * df[MOD_UNRATED]

    # Drop NaN in DV
    before = len(df)
    df = df[df[dv].notna()].copy()
    print(f"  After DV ({dv}) filter: {len(df):,} / {before:,}")

    # Complete cases
    all_required = required + [INT_BELOW_IG, INT_UNRATED]
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
    fe_label = "Industry + CalYrQtr" if fe.endswith("_yq") else "Industry + CalYear"

    print(f"\n{'=' * 60}")
    print(f"Col ({col_num}) | DV={dv} | FE={fe_label}")
    print(f"{'=' * 60}")

    if len(df_prepared) < 100:
        print(f"  Too few obs ({len(df_prepared)}), skipping")
        return None, {}

    exog = [IV_CENTERED, MOD_BELOW_IG, MOD_UNRATED,
            INT_BELOW_IG, INT_UNRATED] + all_controls

    n_firms = df_prepared["gvkey"].nunique()
    n_time_periods = df_prepared.groupby(["gvkey", time_col]).ngroups
    print(f"  N={len(df_prepared):,}, firms={n_firms:,}, firm-time-periods={n_time_periods:,}")
    if extra_controls:
        print(f"  Extra controls: {extra_controls}")

    # VIF
    vif = compute_vif(df_prepared, exog)
    if vif:
        print(f"  VIF({INT_BELOW_IG}): {vif.get(INT_BELOW_IG, np.nan):.2f}")
        print(f"  VIF({INT_UNRATED}): {vif.get(INT_UNRATED, np.nan):.2f}")
        print(f"  VIF({MOD_BELOW_IG}): {vif.get(MOD_BELOW_IG, np.nan):.2f}")
        print(f"  VIF({MOD_UNRATED}): {vif.get(MOD_UNRATED, np.nan):.2f}")

    t0 = datetime.now()
    df_panel = df_prepared.set_index(["gvkey", time_col])

    try:
        model_obj = PanelOLS(
            dependent=df_panel[dv],
            exog=df_panel[exog],
            entity_effects=False,
            time_effects=True,
            other_effects=df_panel["ff12_code"],
            drop_absorbed=True,
            check_rank=False,
        )
        model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return None, {}

    elapsed = (datetime.now() - t0).total_seconds()

    # Extract all 5 key coefficients
    beta_iv, se_iv, p_two_iv = _extract_coef(model, IV_CENTERED)
    beta_big, se_big, p_two_big = _extract_coef(model, MOD_BELOW_IG)
    beta_unr, se_unr, p_two_unr = _extract_coef(model, MOD_UNRATED)
    beta_int_big, se_int_big, p_two_int_big = _extract_coef(model, INT_BELOW_IG)
    beta_int_unr, se_int_unr, p_two_int_unr = _extract_coef(model, INT_UNRATED)

    # One-tailed p for main IV (expected positive)
    if not np.isnan(p_two_iv) and not np.isnan(beta_iv):
        p_one_iv = p_two_iv / 2 if beta_iv > 0 else 1 - p_two_iv / 2
    else:
        p_one_iv = np.nan

    # Lagged DV control if present
    beta_lag_dv, se_lag_dv, p_two_lag_dv = np.nan, np.nan, np.nan
    if "CashHoldings" in extra_controls:
        beta_lag_dv, se_lag_dv, p_two_lag_dv = _extract_coef(model, "CashHoldings")

    stars_iv = _sig_stars_one(p_one_iv)
    stars_int_big = _sig_stars_two(p_two_int_big)
    stars_int_unr = _sig_stars_two(p_two_int_unr)

    print(f"  [OK] {elapsed:.1f}s | R2w={model.rsquared_within:.4f}")
    print(f"  {IV_CENTERED}: b={beta_iv:.4f} p1={p_one_iv:.4f} {stars_iv}")
    print(f"  {MOD_BELOW_IG}: b={beta_big:.4f} p2={p_two_big:.4f}")
    print(f"  {MOD_UNRATED}: b={beta_unr:.4f} p2={p_two_unr:.4f}")
    print(f"  {INT_BELOW_IG}: b={beta_int_big:.4f} p2={p_two_int_big:.4f} {stars_int_big}")
    print(f"  {INT_UNRATED}: b={beta_int_unr:.4f} p2={p_two_int_unr:.4f} {stars_int_unr}")

    n_ig = int(((df_prepared[MOD_BELOW_IG] == 0) & (df_prepared[MOD_UNRATED] == 0)).sum())
    n_below_ig = int(df_prepared[MOD_BELOW_IG].sum())
    n_unrated = int(df_prepared[MOD_UNRATED].sum())

    meta = {
        "col": col_num, "dv": dv, "fe": fe,
        "n_obs": int(model.nobs), "n_firms": n_firms, "n_time_periods": n_time_periods,
        "within_r2": float(model.rsquared_within),
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
        "vif_int_below_ig": vif.get(INT_BELOW_IG, np.nan) if vif else np.nan,
        "vif_int_unrated": vif.get(INT_UNRATED, np.nan) if vif else np.nan,
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
    """Write clean 2-column LaTeX table with three-category moderator."""
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

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Financial Constraint--Moderated Speech Uncertainty and Cash Holdings (Three-Category)}",
        r"\label{tab:h1_2_cash_constraint}",
        r"\small",
        r"\begin{tabular}{lcc}",
        r"\toprule",
        r" & (1) & (2) \\",
        r" & \multicolumn{2}{c}{Cash Holdings$_t$} \\",
        r"\cmidrule(lr){2-3}",
        r" & Cal Year FE & Cal Yr-Qtr FE \\",
        r"\midrule",
    ]

    def _row(label, key_b, key_se, key_p, stars_fn):
        b1 = fmt_coef(m1.get(key_b, np.nan), stars_fn(m1.get(key_p, np.nan)))
        b2 = fmt_coef(m2.get(key_b, np.nan), stars_fn(m2.get(key_p, np.nan)))
        s1 = fmt_se(m1.get(key_se, np.nan))
        s2 = fmt_se(m2.get(key_se, np.nan))
        lines.append(f"{label} & {b1} & {b2} \\\\")
        lines.append(f" & {s1} & {s2} \\\\")

    # Main IV
    _row("Mgr QA Uncertainty", "beta_iv", "se_iv", "p_one_iv", _sig_stars_one)
    # Below-IG level
    _row("Below-IG", "beta_below_ig", "se_below_ig", "p_two_below_ig", _sig_stars_two)
    # Unrated level
    _row("Unrated", "beta_unrated", "se_unrated", "p_two_unrated", _sig_stars_two)
    # Interaction: Below-IG (key)
    _row(r"Mgr QA Unc $\times$ Below-IG", "beta_int_below_ig", "se_int_below_ig", "p_two_int_below_ig", _sig_stars_two)
    # Interaction: Unrated
    _row(r"Mgr QA Unc $\times$ Unrated", "beta_int_unrated", "se_int_unrated", "p_two_int_unrated", _sig_stars_two)

    lines.append(r"\midrule")
    lines.append(r"Controls & Extended & Extended \\")
    lines.append(r"Industry FE & Yes & Yes \\")
    lines.append(r"Calendar Year FE & Yes &  \\")
    lines.append(r"Calendar Year-Quarter FE &  & Yes \\")
    lines.append(r"\midrule")

    lines.append(f"N (calls) & {m1.get('n_obs', 0):,} & {m2.get('n_obs', 0):,} \\\\")
    lines.append(f"N (firm-time-periods) & {m1.get('n_time_periods', 0):,} & {m2.get('n_time_periods', 0):,} \\\\")
    lines.append(
        f"N (IG / Below-IG / Unrated) & "
        f"{m1.get('n_ig', 0):,} / {m1.get('n_below_ig', 0):,} / {m1.get('n_unrated', 0):,} & "
        f"{m2.get('n_ig', 0):,} / {m2.get('n_below_ig', 0):,} / {m2.get('n_unrated', 0):,} \\\\"
    )
    lines.append(
        f"Within-R$^2$ & {fmt_r2(m1.get('within_r2', np.nan))} & "
        f"{fmt_r2(m2.get('within_r2', np.nan))} \\\\"
    )
    lines.append(f"Sample years & {YEAR_MIN}--{YEAR_MAX} & {YEAR_MIN}--{YEAR_MAX} \\\\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$. ",
        r"Main IV (Mgr QA Uncertainty) mean-centered; one-tailed ($\beta > 0$). ",
        r"Interactions and moderator levels: two-tailed. ",
        r"Reference group: investment-grade firms (S\&P long-term issuer rating BBB$-$ or above). ",
        r"Below-IG: firms rated BB$+$ through SD. ",
        r"Unrated: firms with no S\&P long-term issuer credit rating. ",
        r"Rating matched via merge\_asof to most recent rating before call date. ",
        r"$\beta_1$ represents the uncertainty effect for IG firms only. ",
        r"Standard errors (in parentheses) clustered at firm level. ",
        r"Main sample (excludes financial and utility firms). ",
        r"Sample restricted to fiscal years 2002--2016 (ratings coverage). ",
        r"Col~(1): Calendar Year FE. Col~(2): Calendar Year-Quarter FE. ",
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
        fname = f"regression_results_col{col_num}.txt"
        with open(out_dir / fname, "w", encoding="utf-8") as f:
            f.write(f"H1.2 Financing-Constraint-Moderated Cash Holdings (3-category)\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']}\n")
            f.write(f"IV: {IV} (centered)\n")
            f.write(f"Moderators: BelowIG (dummy), Unrated (dummy). Reference: IG\n")
            f.write(f"Interactions: {INT_BELOW_IG}, {INT_UNRATED}\n")
            f.write(f"FE: {meta['fe']}\n")
            f.write(f"Sample years: {YEAR_MIN}-{YEAR_MAX}\n")
            f.write(f"Extra controls: {meta.get('extra_controls', '')}\n")
            f.write(f"VIF(int_below_ig): {meta.get('vif_int_below_ig', 'N/A')}\n")
            f.write(f"VIF(int_unrated): {meta.get('vif_int_unrated', 'N/A')}\n")
            f.write(f"N: IG={meta['n_ig']}, Below-IG={meta['n_below_ig']}, Unrated={meta['n_unrated']}\n")
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
        f"**Design:** Manager_QA_Uncertainty × BelowIG / Unrated (two interactions)",
        f"**Channel:** CH1 — Precautionary liquidity under external-finance frictions",
        f"**Moderator:** Three-category: IG (ref) / Below-IG / Unrated",
        f"**IV centering mean:** {iv_mu:.4f}",
        f"**FE:** Col 1: Industry + CalYear; Col 2: Industry + CalYrQtr",
        f"**Sample years:** {YEAR_MIN}-{YEAR_MAX}",
        f"**Parent suite:** H1 (Cash Holdings)",
        "",
        "## Results",
        "",
        "| Col | DV | b_iv (p1) | b_int_belowIG (p2) | b_int_unrated (p2) | N | R2w |",
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
            f"{m['n_obs']:,} | {m['within_r2']:.4f} |"
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


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h1_2_cash_constraint" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H1_2_CashConstraint",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H1.2 Financing-Constraint-Moderated Cash Holdings (3-Category)")
    print("=" * 80)
    print(f"Timestamp:  {timestamp}")
    print(f"Output:     {out_dir}")
    print(f"Design:     1 IV × 1 DV × 2 interactions × 2 FE types = 2 models")
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
        caption="Summary Statistics --- H1.2 Cash Holdings (3-Category Constraint, Main Sample, 2002--2016)",
        label="tab:summary_stats_h1_2",
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
            "H1.2 Financing-Constraint-Moderated Cash Holdings (3-Category)",
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
        s_big = _sig_stars_two(m["p_two_int_below_ig"])
        s_unr = _sig_stars_two(m["p_two_int_unrated"])
        print(f"  Col ({m['col']}) {m['dv']}: "
              f"IV b={m['beta_iv']:.4f}{s_iv} | "
              f"Int(BelowIG) b={m['beta_int_below_ig']:.4f}{s_big} | "
              f"Int(Unrated) b={m['beta_int_unrated']:.4f}{s_unr}")

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
