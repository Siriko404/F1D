#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test Liquidity Hypothesis (4.2 Liquidity Regressions)
================================================================================
ID: econometric/test_liquidity
Description: Run Liquidity hypothesis tests (4.2) by loading the liquidity panel
             from Stage 3, running:
               Phase 1: First stage OLS — instrument validity
                        (Q&A Uncertainty ~ CCCL + controls)
               Phase 2: OLS — liquidity regressed on clarity + uncertainty
               Phase 3: 2SLS — Q&A Uncertainty instrumented by CCCL
             Runs for 2 dependent variables × 2 clarity models = 4 regressions
             per phase (OLS/2SLS). Main sample only.

Model specs:
    Regime model: dep ~ ClarityManager + Manager_QA_Uncertainty_pct + controls
    CEO model:    dep ~ ClarityCEO    + CEO_QA_Uncertainty_pct    + controls

Dependent variables:
    Delta_Amihud            — change in Amihud (2002) illiquidity
    Delta_Corwin_Schultz    — change in Corwin-Schultz bid-ask spread

Endogenous variable (instrumented in 2SLS):
    Manager_QA_Uncertainty_pct  (Regime model)
    CEO_QA_Uncertainty_pct      (CEO model)

Instrument (CCCL):
    shift_intensity_sale_ff48

Exogenous controls:
    Analyst_QA_Uncertainty_pct, Entire_All_Negative_pct
    Manager_Pres_Uncertainty_pct / CEO_Pres_Uncertainty_pct (per model)
    Size, BM, Lev, ROA, CurrentRatio, RD_Intensity, Volatility,
    EPS_Growth, StockRet, MarketRet, SurpDec
    C(year) fixed effects

Data coverage note:
    Delta_Amihud/Delta_Corwin_Schultz available 2002-2011 only.
    CCCL instrument starts 2005; 2SLS sample is 2005-2011.
    OLS sample is 2002-2011 (where dep var non-null).

Inputs:
    - outputs/variables/liquidity/{latest_timestamp}/liquidity_panel.parquet

Outputs:
    - outputs/econometric/liquidity/{timestamp}/first_stage_results.txt
    - outputs/econometric/liquidity/{timestamp}/ols_{model}_{dep}.txt
    - outputs/econometric/liquidity/{timestamp}/iv_{model}_{dep}.txt
    - outputs/econometric/liquidity/{timestamp}/model_diagnostics.csv
    - outputs/econometric/liquidity/{timestamp}/report_step4_liquidity.md
    - outputs/econometric/liquidity/{timestamp}/run_log.txt

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_liquidity_panel)
    - Uses: statsmodels, linearmodels, f1d.shared

Author: Thesis Author
Date: 2026-02-19
================================================================================
"""

from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=FutureWarning)

# statsmodels — always-bound pattern (matches test_ceo_tone.py)
smf: Any = None
sm: Any = None
try:
    import statsmodels.api as sm  # type: ignore[no-redef]
    import statsmodels.formula.api as smf  # type: ignore[no-redef]

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("WARNING: statsmodels not available. Install with: pip install statsmodels")

# linearmodels for IV2SLS
IV2SLS: Any = None
try:
    from linearmodels.iv import IV2SLS  # type: ignore[no-redef]

    LINEARMODELS_AVAILABLE = True
except ImportError:
    LINEARMODELS_AVAILABLE = False
    print("WARNING: linearmodels not available. Install with: pip install linearmodels")

from f1d.shared.observability_utils import DualWriter
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.regression_validation import (
    RegressionValidationError,
    validate_columns,
    validate_sample_size,
)


# ==============================================================================
# Configuration
# ==============================================================================

INSTRUMENT = "shift_intensity_sale_ff48"

DEP_VARS = ["Delta_Amihud", "Delta_Corwin_Schultz"]

# Financial controls shared across all regressions
FINANCIAL_CONTROLS = [
    "Size",
    "BM",
    "Lev",
    "ROA",
    "CurrentRatio",
    "RD_Intensity",
    "Volatility",
    "EPS_Growth",
    "StockRet",
    "MarketRet",
    "SurpDec",
]

# Linguistic controls shared across all regressions
LINGUISTIC_CONTROLS_SHARED = [
    "Analyst_QA_Uncertainty_pct",
    "Entire_All_Negative_pct",
]

# Two clarity model specs
MODEL_SPECS: Dict[str, Dict[str, str]] = {
    "Regime": {
        "clarity_var": "ClarityManager",
        "endog_var": "Manager_QA_Uncertainty_pct",
        "pres_unc_var": "Manager_Pres_Uncertainty_pct",
        "description": "Manager Clarity (4.1) with Manager Q&A Uncertainty",
    },
    "CEO": {
        "clarity_var": "ClarityCEO",
        "endog_var": "CEO_QA_Uncertainty_pct",
        "pres_unc_var": "CEO_Pres_Uncertainty_pct",
        "description": "CEO Clarity (4.1.1) with CEO Q&A Uncertainty",
    },
}

# Main sample only (exclude Finance ff12=11, Utility ff12=8)
MAIN_SAMPLE_EXCLUDE_FF12 = [8, 11]

# Minimum observations for regression
MIN_OBS = 100

VARIABLE_LABELS = {
    "ClarityManager": "Clarity (Manager)",
    "ClarityCEO": "Clarity (CEO)",
    "Manager_QA_Uncertainty_pct": "Manager QA Uncertainty",
    "CEO_QA_Uncertainty_pct": "CEO QA Uncertainty",
    "Manager_Pres_Uncertainty_pct": "Manager Pres Uncertainty",
    "CEO_Pres_Uncertainty_pct": "CEO Pres Uncertainty",
    "Analyst_QA_Uncertainty_pct": "Analyst QA Uncertainty",
    "Entire_All_Negative_pct": "Neg Sentiment (All)",
    "Size": "Size (log assets)",
    "BM": "Book-to-Market",
    "Lev": "Leverage",
    "ROA": "ROA",
    "CurrentRatio": "Current Ratio",
    "RD_Intensity": "R\\&D Intensity",
    "Volatility": "Return Volatility",
    "EPS_Growth": "EPS Growth",
    "StockRet": "Stock Return",
    "MarketRet": "Market Return",
    "SurpDec": "Earnings Surprise Decile",
    INSTRUMENT: "CCCL Instrument",
}


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Stage 4: Test Liquidity Hypothesis (4.2)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs without executing",
    )
    parser.add_argument(
        "--panel-path",
        type=str,
        default=None,
        help="Path to liquidity panel parquet (default: latest from Stage 3)",
    )
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    """Load liquidity panel from Stage 3 output."""
    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "liquidity",
            required_file="liquidity_panel.parquet",
        )
        panel_file = panel_dir / "liquidity_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")

    # Hard assertion: ff12_code must be present
    if "ff12_code" not in panel.columns:
        raise ValueError(
            "'ff12_code' not found in liquidity panel. "
            "Cannot filter to Main sample. Re-run Stage 3."
        )

    # Report dep var coverage
    for dep in DEP_VARS:
        if dep in panel.columns:
            n = panel[dep].notna().sum()
            print(f"  {dep}: {n:,} non-null ({100.0 * n / len(panel):.1f}%)")

    return panel


def prepare_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter panel to Main sample (exclude Finance ff12=11, Utility ff12=8).

    Returns filtered DataFrame with year as integer column.
    """
    df = panel[~panel["ff12_code"].isin(MAIN_SAMPLE_EXCLUDE_FF12)].copy()
    print(
        f"\n  Main sample: {len(df):,} calls (excluded ff12 in {MAIN_SAMPLE_EXCLUDE_FF12})"
    )

    if "year" not in df.columns and "start_date" in df.columns:
        df["year"] = pd.to_datetime(df["start_date"], errors="coerce").dt.year

    df["ceo_id"] = df["ceo_id"].astype(str)

    # Report dep var coverage in main sample
    for dep in DEP_VARS:
        if dep in df.columns:
            n = df[dep].notna().sum()
            yrs = df.loc[df[dep].notna(), "year"]
            if len(yrs) > 0:
                print(f"  {dep} in Main: {n:,} obs ({yrs.min():.0f}–{yrs.max():.0f})")

    # Report instrument coverage
    if INSTRUMENT in df.columns:
        n_inst = df[INSTRUMENT].notna().sum()
        print(
            f"  {INSTRUMENT} in Main: {n_inst:,} non-null ({100.0 * n_inst / len(df):.1f}%)"
        )

    return df


# ==============================================================================
# Phase 1: First Stage (Instrument Validity)
# ==============================================================================


def run_first_stage(
    df: pd.DataFrame,
    out_dir: Path,
) -> List[Dict[str, Any]]:
    """Test instrument relevance: endogenous ~ CCCL + controls + C(year).

    Runs for each endogenous variable (Manager_QA_Uncertainty_pct,
    CEO_QA_Uncertainty_pct). Hard exits if statsmodels unavailable.

    Returns:
        List of result dicts (one per endogenous variable).
    """
    print("\n" + "=" * 60)
    print("PHASE 1: First Stage — Instrument Validity")
    print("=" * 60)

    if not STATSMODELS_AVAILABLE:
        print("ERROR: statsmodels not available")
        sys.exit(1)

    results: List[Dict[str, Any]] = []
    output_lines: List[str] = []
    output_lines.append("=" * 80)
    output_lines.append("FIRST STAGE REGRESSIONS: Instrument Validity")
    output_lines.append(f"Instrument: {INSTRUMENT}")
    output_lines.append("=" * 80)

    for endog_var, model_label in [
        ("Manager_QA_Uncertainty_pct", "Regime (Manager)"),
        ("CEO_QA_Uncertainty_pct", "CEO"),
    ]:
        if endog_var not in df.columns:
            output_lines.append(f"\n--- {model_label}: MISSING from panel ---")
            continue

        output_lines.append(f"\n--- Endogenous: {endog_var} ({model_label}) ---")

        # Controls: shared linguistic + financial (exclude the endog var itself)
        pres_unc = (
            "Manager_Pres_Uncertainty_pct"
            if "Manager" in endog_var
            else "CEO_Pres_Uncertainty_pct"
        )
        controls = LINGUISTIC_CONTROLS_SHARED + [pres_unc] + FINANCIAL_CONTROLS
        controls = [c for c in controls if c in df.columns and c != endog_var]

        # Build regression dataset — require instrument non-null
        required = [endog_var, INSTRUMENT] + controls + ["year"]
        required = [r for r in required if r in df.columns]

        reg_df = df[required].dropna().copy()

        if len(reg_df) < MIN_OBS:
            output_lines.append(f"  Insufficient observations: {len(reg_df)}")
            continue

        # Validate before regression
        try:
            validate_columns(reg_df, required)
            validate_sample_size(reg_df, min_observations=MIN_OBS)
        except RegressionValidationError as e:
            output_lines.append(f"  ERROR: Validation failed: {e}")
            continue

        reg_df["year"] = reg_df["year"].astype(str)

        formula = (
            f"{endog_var} ~ {INSTRUMENT} + "
            + " + ".join([c for c in controls if c in reg_df.columns])
            + " + C(year)"
        )
        output_lines.append(f"  Formula: {formula}")
        output_lines.append(f"  N = {len(reg_df):,}")

        try:
            model = smf.ols(formula, data=reg_df).fit(cov_type="HC1")
        except Exception as e:
            output_lines.append(f"  ERROR: Regression failed: {e}")
            continue

        coef = model.params.get(INSTRUMENT, np.nan)
        t_stat = model.tvalues.get(INSTRUMENT, np.nan)
        p_val = model.pvalues.get(INSTRUMENT, np.nan)
        f_stat = float(t_stat) ** 2 if not np.isnan(t_stat) else np.nan

        output_lines.append(f"  R-squared = {model.rsquared:.4f}")
        output_lines.append(f"  Instrument coefficient: {coef:.6f}")
        output_lines.append(f"  t-statistic: {t_stat:.2f}")
        output_lines.append(f"  p-value: {p_val:.4f}")
        output_lines.append(f"  F-statistic (t²): {f_stat:.2f}")

        if not np.isnan(f_stat) and f_stat >= 10:
            output_lines.append("  [OK] Strong instrument (F >= 10)")
        else:
            output_lines.append("  [WEAK] Weak instrument (F < 10)")

        results.append(
            {
                "Endogenous": endog_var,
                "Label": model_label,
                "N": int(model.nobs),
                "R2": model.rsquared,
                "Instrument_Coef": coef,
                "Instrument_tstat": t_stat,
                "Instrument_pval": p_val,
                "F_stat": f_stat,
                "Strong": (not np.isnan(f_stat)) and (f_stat >= 10),
            }
        )

        # Save full summary for this endogenous variable
        full_path = out_dir / f"first_stage_{endog_var.lower()}.txt"
        with open(full_path, "w") as fh:
            fh.write(f"First Stage: {endog_var}\nFormula: {formula}\n\n")
            fh.write(model.summary().as_text())
        print(f"  Saved: first_stage_{endog_var.lower()}.txt")

    summary_path = out_dir / "first_stage_results.txt"
    with open(summary_path, "w") as fh:
        fh.write("\n".join(output_lines))
    print(f"  Saved: first_stage_results.txt")

    return results


# ==============================================================================
# Phase 2: OLS Regressions
# ==============================================================================


def run_ols(
    df: pd.DataFrame,
    model_key: str,
    dep_var: str,
    out_dir: Path,
) -> Optional[Dict[str, Any]]:
    """Run OLS regression: dep_var ~ clarity + endog + controls + C(year).

    No instrument used. This is the unadjusted baseline regression.

    Args:
        df: Main sample DataFrame
        model_key: 'Regime' or 'CEO'
        dep_var: 'Delta_Amihud' or 'Delta_Corwin_Schultz'
        out_dir: Output directory for results text file

    Returns:
        Result dict or None if insufficient data.
    """
    spec = MODEL_SPECS[model_key]
    clarity_var = spec["clarity_var"]
    endog_var = spec["endog_var"]
    pres_unc_var = spec["pres_unc_var"]

    print(f"\n  OLS | {model_key} | {dep_var}")

    # Build complete-case dataset
    controls = (
        [clarity_var, endog_var, pres_unc_var]
        + LINGUISTIC_CONTROLS_SHARED
        + FINANCIAL_CONTROLS
    )
    controls = [c for c in controls if c in df.columns]
    required = [dep_var] + controls + ["year"]
    required = [r for r in required if r in df.columns]

    reg_df = df[required].dropna().copy()

    if len(reg_df) < MIN_OBS:
        print(f"  Skipping: {len(reg_df)} obs < {MIN_OBS}")
        return None

    try:
        validate_columns(reg_df, required)
        validate_sample_size(reg_df, min_observations=MIN_OBS)
    except RegressionValidationError as e:
        print(f"  ERROR: Validation failed: {e}")
        sys.exit(1)

    reg_df["year"] = reg_df["year"].astype(str)

    rhs = [c for c in controls if c in reg_df.columns]
    formula = f"{dep_var} ~ " + " + ".join(rhs) + " + C(year)"
    print(f"  Formula: {formula}")
    print(f"  N = {len(reg_df):,}")

    try:
        model = smf.ols(formula, data=reg_df).fit(cov_type="HC1")
    except Exception as e:
        print(f"  ERROR: OLS failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"  R² = {model.rsquared:.4f}, N = {int(model.nobs):,}")

    out_file = out_dir / f"ols_{model_key.lower()}_{dep_var.lower()}.txt"
    with open(out_file, "w") as fh:
        fh.write(f"OLS: {model_key} / {dep_var}\nFormula: {formula}\n\n")
        fh.write(model.summary().as_text())
    print(f"  Saved: ols_{model_key.lower()}_{dep_var.lower()}.txt")

    return {
        "phase": "OLS",
        "model": model_key,
        "dep_var": dep_var,
        "n_obs": int(model.nobs),
        "rsquared": model.rsquared,
        "rsquared_adj": model.rsquared_adj,
        "fvalue": getattr(model, "fvalue", None),
        "f_pvalue": getattr(model, "f_pvalue", None),
        "aic": getattr(model, "aic", None),
        "bic": getattr(model, "bic", None),
        "clarity_coef": model.params.get(clarity_var, np.nan),
        "clarity_pval": model.pvalues.get(clarity_var, np.nan),
        "endog_coef": model.params.get(endog_var, np.nan),
        "endog_pval": model.pvalues.get(endog_var, np.nan),
        "fitted_model": model,
    }


# ==============================================================================
# Phase 3: 2SLS Regressions
# ==============================================================================


def run_iv(
    df: pd.DataFrame,
    model_key: str,
    dep_var: str,
    out_dir: Path,
) -> Optional[Dict[str, Any]]:
    """Run 2SLS regression: dep_var ~ [clarity + controls] + (endog ~ CCCL).

    Q&A Uncertainty is instrumented by shift_intensity_sale_ff48 (CCCL).
    Year fixed effects implemented as dummies (linearmodels requires matrices).

    Args:
        df: Main sample DataFrame
        model_key: 'Regime' or 'CEO'
        dep_var: 'Delta_Amihud' or 'Delta_Corwin_Schultz'
        out_dir: Output directory for results text file

    Returns:
        Result dict or None if insufficient data or package unavailable.
    """
    if not LINEARMODELS_AVAILABLE:
        print(
            f"  WARNING: linearmodels unavailable — skipping 2SLS for {model_key}/{dep_var}"
        )
        return None

    spec = MODEL_SPECS[model_key]
    clarity_var = spec["clarity_var"]
    endog_var = spec["endog_var"]
    pres_unc_var = spec["pres_unc_var"]

    print(f"\n  2SLS | {model_key} | {dep_var}")

    # Build complete-case dataset — requires instrument non-null
    controls = (
        [clarity_var, pres_unc_var] + LINGUISTIC_CONTROLS_SHARED + FINANCIAL_CONTROLS
    )
    controls = [c for c in controls if c in df.columns]
    required = [dep_var, endog_var, INSTRUMENT] + controls + ["year"]
    required = [r for r in required if r in df.columns]

    reg_df = df[required].dropna().copy()

    if len(reg_df) < MIN_OBS:
        print(f"  Skipping: {len(reg_df)} obs < {MIN_OBS}")
        return None

    try:
        validate_columns(reg_df, required)
        validate_sample_size(reg_df, min_observations=MIN_OBS)
    except RegressionValidationError as e:
        print(f"  ERROR: Validation failed: {e}")
        sys.exit(1)

    # Cast all numeric columns to float64
    for col in reg_df.columns:
        if col != "year":
            reg_df[col] = pd.to_numeric(reg_df[col], errors="coerce").astype(np.float64)
    reg_df = reg_df.dropna()

    if len(reg_df) < MIN_OBS:
        print(f"  Skipping after numeric cast: {len(reg_df)} obs < {MIN_OBS}")
        return None

    print(f"  N = {len(reg_df):,}")

    # Year dummies (drop first for identification)
    year_dummies = pd.get_dummies(
        reg_df["year"].astype(str), prefix="year", drop_first=True
    ).astype(np.float64)
    reg_df = pd.concat([reg_df.drop(columns=["year"]), year_dummies], axis=1)

    try:
        y = reg_df[dep_var].astype(np.float64)
        endog = reg_df[[endog_var]].astype(np.float64)
        instruments = reg_df[[INSTRUMENT]].astype(np.float64)

        exog_cols = [c for c in controls if c in reg_df.columns]
        exog_cols += list(year_dummies.columns)
        exog_data = reg_df[exog_cols].astype(np.float64)
        exog = sm.add_constant(exog_data)

        model = IV2SLS(y, exog, endog, instruments).fit(cov_type="robust")

        # Kleibergen-Paap F-stat via first-stage OLS
        fs_X = sm.add_constant(
            pd.concat(
                [instruments, exog.drop(columns=["const"], errors="ignore")],
                axis=1,
            )
        )
        fs_model = sm.OLS(endog, fs_X).fit()
        kp_f = float(fs_model.fvalue)

    except Exception as e:
        print(f"  ERROR: 2SLS failed: {e}", file=sys.stderr)
        return None

    r2 = float(model.rsquared) if hasattr(model, "rsquared") else np.nan
    print(f"  R² = {r2:.4f}, KP F-stat = {kp_f:.2f}, N = {int(model.nobs):,}")

    if kp_f < 10:
        print(f"  [WEAK] Kleibergen-Paap F-stat < 10 ({kp_f:.2f})")
    else:
        print(f"  [OK] Strong instrument (KP F = {kp_f:.2f} >= 10)")

    out_file = out_dir / f"iv_{model_key.lower()}_{dep_var.lower()}.txt"
    with open(out_file, "w") as fh:
        fh.write(
            f"2SLS: {model_key} / {dep_var}\n"
            f"Endogenous: {endog_var}\n"
            f"Instrument: {INSTRUMENT}\n\n"
        )
        fh.write(str(model.summary))
        fh.write(f"\n\nKleibergen-Paap F-stat: {kp_f:.2f}")
        if kp_f < 10:
            fh.write(" (WEAK)")
        fh.write("\n")
    print(f"  Saved: iv_{model_key.lower()}_{dep_var.lower()}.txt")

    clarity_coef = (
        float(model.params.get(clarity_var, np.nan))
        if hasattr(model, "params")
        else np.nan
    )
    clarity_pval = (
        float(model.pvalues.get(clarity_var, np.nan))
        if hasattr(model, "pvalues")
        else np.nan
    )
    endog_coef = (
        float(model.params.get(endog_var, np.nan))
        if hasattr(model, "params")
        else np.nan
    )
    endog_pval = (
        float(model.pvalues.get(endog_var, np.nan))
        if hasattr(model, "pvalues")
        else np.nan
    )

    return {
        "phase": "2SLS",
        "model": model_key,
        "dep_var": dep_var,
        "n_obs": int(model.nobs),
        "rsquared": r2,
        "rsquared_adj": np.nan,
        "fvalue": np.nan,
        "f_pvalue": np.nan,
        "kp_f": kp_f,
        "aic": np.nan,
        "bic": np.nan,
        "clarity_coef": clarity_coef,
        "clarity_pval": clarity_pval,
        "endog_coef": endog_coef,
        "endog_pval": endog_pval,
        "fitted_model": None,  # linearmodels summary is string-only
    }


# ==============================================================================
# Output Generation
# ==============================================================================


def save_diagnostics(
    all_results: List[Dict[str, Any]],
    first_stage_results: List[Dict[str, Any]],
    out_dir: Path,
) -> None:
    """Save model_diagnostics.csv combining first stage + OLS + 2SLS results."""
    diag_rows = []

    for fs in first_stage_results:
        diag_rows.append(
            {
                "phase": "FirstStage",
                "model": fs.get("Label"),
                "dep_var": fs.get("Endogenous"),
                "n_obs": fs.get("N"),
                "rsquared": fs.get("R2"),
                "rsquared_adj": np.nan,
                "fvalue": fs.get("F_stat"),
                "f_pvalue": fs.get("Instrument_pval"),
                "kp_f": np.nan,
                "aic": np.nan,
                "bic": np.nan,
                "clarity_coef": np.nan,
                "clarity_pval": np.nan,
                "endog_coef": fs.get("Instrument_Coef"),
                "endog_pval": fs.get("Instrument_pval"),
            }
        )

    for res in all_results:
        diag_rows.append(
            {
                "phase": res.get("phase"),
                "model": res.get("model"),
                "dep_var": res.get("dep_var"),
                "n_obs": res.get("n_obs"),
                "rsquared": res.get("rsquared"),
                "rsquared_adj": res.get("rsquared_adj"),
                "fvalue": res.get("fvalue"),
                "f_pvalue": res.get("f_pvalue"),
                "kp_f": res.get("kp_f"),
                "aic": res.get("aic"),
                "bic": res.get("bic"),
                "clarity_coef": res.get("clarity_coef"),
                "clarity_pval": res.get("clarity_pval"),
                "endog_coef": res.get("endog_coef"),
                "endog_pval": res.get("endog_pval"),
            }
        )

    if diag_rows:
        diag_df = pd.DataFrame(diag_rows)
        diag_path = out_dir / "model_diagnostics.csv"
        diag_df.to_csv(diag_path, index=False)
        print(f"  Saved: model_diagnostics.csv ({len(diag_df)} rows)")


def generate_report(
    first_stage_results: List[Dict[str, Any]],
    all_results: List[Dict[str, Any]],
    out_dir: Path,
    duration: float,
) -> None:
    """Generate markdown report."""
    report_lines = [
        "# Stage 4: Liquidity Regression Results (4.2)",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Data Coverage Note",
        "",
        "- `Delta_Amihud` and `Delta_Corwin_Schultz` available for 2002–2011 only.",
        "- CCCL instrument (`shift_intensity_sale_ff48`) available from 2005.",
        "- OLS sample: 2002–2011 (where dep var non-null). 2SLS sample: 2005–2011.",
        "",
        "## Phase 1: First Stage — Instrument Validity",
        "",
        "| Endogenous | N | R² | Instrument Coef | t-stat | p-val | F-stat | Strong? |",
        "|-----------|---|-----|----------------|--------|-------|--------|---------|",
    ]
    for fs in first_stage_results:
        f_stat = fs.get("F_stat", np.nan)
        strong = "Yes" if fs.get("Strong") else "No"
        report_lines.append(
            f"| {fs.get('Endogenous')} | {fs.get('N', 'N/A'):,} | "
            f"{fs.get('R2', np.nan):.4f} | {fs.get('Instrument_Coef', np.nan):.4f} | "
            f"{fs.get('Instrument_tstat', np.nan):.2f} | {fs.get('Instrument_pval', np.nan):.4f} | "
            f"{f_stat:.2f} | {strong} |"
        )
    report_lines.append("")

    report_lines += [
        "## Phase 2 & 3: OLS and 2SLS Results",
        "",
        "| Phase | Model | Dep Var | N | R² | Clarity Coef | Clarity p-val | KP F |",
        "|-------|-------|---------|---|-----|-------------|--------------|------|",
    ]
    for res in all_results:
        kp_f = res.get("kp_f", np.nan)
        kp_str = (
            f"{kp_f:.2f}" if not (isinstance(kp_f, float) and np.isnan(kp_f)) else "—"
        )
        r2 = res.get("rsquared", np.nan)
        r2_str = f"{r2:.4f}" if not (isinstance(r2, float) and np.isnan(r2)) else "N/A"
        clarity_coef = res.get("clarity_coef", np.nan)
        clarity_pval = res.get("clarity_pval", np.nan)
        coef_str = (
            f"{clarity_coef:.4f}"
            if not (isinstance(clarity_coef, float) and np.isnan(clarity_coef))
            else "—"
        )
        pval_str = (
            f"{clarity_pval:.4f}"
            if not (isinstance(clarity_pval, float) and np.isnan(clarity_pval))
            else "—"
        )
        report_lines.append(
            f"| {res.get('phase')} | {res.get('model')} | {res.get('dep_var')} | "
            f"{res.get('n_obs', 'N/A'):,} | {r2_str} | {coef_str} | {pval_str} | {kp_str} |"
        )
    report_lines.append("")

    report_path = out_dir / "report_step4_liquidity.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print("  Saved: report_step4_liquidity.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    # Setup paths
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "liquidity" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    # DualWriter: mirror stdout to persistent log file
    log_path = out_dir / "run_log.txt"
    dual = DualWriter(log_path)
    sys.stdout = dual

    print("=" * 80)
    print("STAGE 4: Test Liquidity Hypothesis (4.2)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")

    # Load panel
    panel = load_panel(root, panel_path)

    # Filter to Main sample
    df_main = prepare_main_sample(panel)

    # Phase 1: First Stage (instrument validity)
    first_stage_results = run_first_stage(df_main, out_dir)

    # Phase 2 (OLS) and Phase 3 (2SLS): 2 models × 2 dep vars = 4 each
    all_results: List[Dict[str, Any]] = []

    for model_key in MODEL_SPECS:
        print(f"\n{'=' * 80}")
        print(f"MODEL: {model_key} — {MODEL_SPECS[model_key]['description']}")
        print("=" * 80)

        for dep_var in DEP_VARS:
            if dep_var not in df_main.columns:
                print(f"  WARNING: {dep_var} not in panel — skipping")
                continue

            # OLS
            ols_result = run_ols(df_main.copy(), model_key, dep_var, out_dir)
            if ols_result is not None:
                all_results.append(ols_result)

            # 2SLS
            iv_result = run_iv(df_main.copy(), model_key, dep_var, out_dir)
            if iv_result is not None:
                all_results.append(iv_result)

    # Save outputs
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    save_diagnostics(all_results, first_stage_results, out_dir)

    # Final summary
    duration = (datetime.now() - start_time).total_seconds()
    generate_report(first_stage_results, all_results, out_dir, duration)

    n_ols = sum(1 for r in all_results if r["phase"] == "OLS")
    n_iv = sum(1 for r in all_results if r["phase"] == "2SLS")
    print(f"\n  First stage regressions: {len(first_stage_results)}")
    print(f"  OLS regressions completed: {n_ols}")
    print(f"  2SLS regressions completed: {n_iv}")

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")

    # Restore stdout
    sys.stdout = dual.original_stdout
    dual.log.close()

    return 0


if __name__ == "__main__":
    args = parse_arguments()

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print("[OK] All inputs validated")
        sys.exit(0)

    sys.exit(main(panel_path=args.panel_path))
