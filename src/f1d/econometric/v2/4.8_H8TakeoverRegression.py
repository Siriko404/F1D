#!/usr/bin/env python3
"""
==============================================================================
STEP 4.8: H8 Takeover Regression
==============================================================================
ID: 4.8_H8TakeoverRegression
Description: Logistic regressions for H8 (Speech Uncertainty -> Takeover
             Target Probability). Tests whether vague managers face higher
             takeover likelihood.

Model Specification:
    logit(P(Takeover_{t+1}=1)) = beta0 + beta1*Uncertainty_t + gamma*Controls
                                  + Firm FE + Year FE

Hypothesis Tests:
    H8a: beta1 > 0 (Higher uncertainty -> Higher takeover probability)

Econometric Standards:
    - Model: Logistic regression with firm and year FE
    - SE: Clustered at firm level
    - DV: Forward-looking (t+1) for causal interpretation
    - Alternative: Cox proportional hazards (if feasible)

Inputs:
    - 4_Outputs/3_Financial_V2/latest/H8_Takeover.parquet

Outputs:
    - 4_Outputs/4_Econometric_V2/{timestamp}/H8_Regression_Results.parquet
    - 4_Outputs/4_Econometric_V2/{timestamp}/H8_RESULTS.md
    - 4_Outputs/4_Econometric_V2/{timestamp}/stats.json

Deterministic: true
Dependencies:
    - Requires: Step 3.8_H8TakeoverVariables
    - Uses: shared.regression_utils, shared.panel_ols, shared.diagnostics, linearmodels

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

import argparse
import subprocess
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
import yaml

# Import shared utilities
from f1d.shared.latex_tables import make_regression_table
from f1d.shared.observability_utils import (
    DualWriter,
    compute_file_checksum,
    get_process_memory_mb,
    print_stats_summary,
    save_stats,
)
from f1d.shared.path_utils import (
    ensure_output_dir,
    get_latest_output_dir,
    validate_input_file,
)

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# ==============================================================================
# Configuration
# ==============================================================================


def load_config():
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    if config_path.exists():
        validate_input_file(config_path, must_exist=True)
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


def get_git_sha():
    """Get current git commit SHA for reproducibility"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


# Uncertainty measures (4 total available in H8_Takeover.parquet)
UNCERTAINTY_MEASURES = [
    "Manager_QA_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
]

# Control variables (available in H8_Takeover.parquet)
CONTROL_VARS = ["Volatility", "StockRet"]

# Regression specifications
SPECS = {
    "primary": {"include_fe": True, "cluster": "firm"},
    "pooled": {"include_fe": False, "cluster": "firm"},
}

# H8 Robustness configuration
H8_ROBUSTNESS_CONFIG: Dict[str, Any] = {
    "alternative_dvs": {
        "takeover_announced": "Announced deals (all)",
        "takeover_hostile": "Hostile/unsolicited deals",
    },
    "alternative_specs": {
        "pooled": {"include_fe": False, "cluster": "firm"},
    },
    "alternative_ivs": {
        "ceo_only": ["CEO_QA_Uncertainty_pct", "CEO_Pres_Uncertainty_pct"],
        "presentation_only": [
            "Manager_Pres_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
        ],
        "qa_only": ["Manager_QA_Uncertainty_pct", "CEO_QA_Uncertainty_pct"],
    },
    "timing_tests": {
        "concurrent": 0,  # Uncertainty_t -> Takeover_t
        "forward": -1,  # Uncertainty_t -> Takeover_{t+1} (primary)
        "lead": -2,  # Uncertainty_t -> Takeover_{t+2}
    },
    "alternative_models": {
        "cox_ph": True  # Cox proportional hazards if lifelines available
    },
}

# ==============================================================================
# Path Setup
# ==============================================================================


def setup_paths(timestamp):
    """Set up all required paths"""
    root = Path(__file__).resolve().parents[4]

    # Resolve H8 output directory
    h8_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H8_Takeover.parquet",
    )

    paths = {
        "root": root,
        "h8_file": h8_dir / "H8_Takeover.parquet",
    }

    # Output directory
    output_base = root / "4_Outputs" / "4_Econometric_V2"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "4_Econometric_V2"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H8.log"

    return paths


# ==============================================================================
# Data Loading
# ==============================================================================


def load_h8_data(h8_path):
    """
    Load H8 takeover data.

    Args:
        h8_path: Path to H8_Takeover.parquet

    Returns:
        DataFrame with takeover variables, uncertainty measures, and controls
    """
    print("\nLoading H8 takeover data...")

    df = pd.read_parquet(h8_path)
    print(f"  Loaded H8: {len(df):,} observations")

    # Ensure gvkey is string
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    # Set MultiIndex for panel data
    df = df.set_index(["gvkey", "year"])

    print(f"  Firms: {df.index.get_level_values('gvkey').nunique():,}")
    print(
        f"  Years: {df.index.get_level_values('year').min()}-{df.index.get_level_values('year').max()}"
    )

    # Check takeover variation
    takeover_rate = df["takeover_fwd"].mean()
    takeover_events = df["takeover_fwd"].sum()
    print(f"  Takeover events (t+1): {takeover_events:,}")
    print(f"  Takeover rate: {takeover_rate:.2%}")

    if takeover_events == 0:
        print("  WARNING: No takeover events in sample!")
        print("  Logistic regression requires variation in dependent variable")

    return df


# ==============================================================================
# Logit Regression
# ==============================================================================


def run_h8_logit(
    df,
    uncertainty_var,
    dv_col="takeover_fwd",
    controls=None,
    include_fe=True,
    spec="primary",
):
    """
    Run single H8 logistic regression.

    Specification:
        logit(P(Takeover_{t+1}=1)) = beta0 + beta1*Uncertainty + Controls + FE

    Args:
        df: Dataset with gvkey, year, DV, IV, controls (MultiIndex)
        uncertainty_var: Name of uncertainty IV
        dv_col: Name of dependent variable (binary)
        controls: List of control variable names
        include_fe: Whether to include firm and year FE
        spec: Specification name ('primary' or 'pooled')

    Returns:
        dict with coefficients, SEs, p-values, diagnostics
    """
    import statsmodels.api as sm

    # Prepare data
    iv_vars = [uncertainty_var]
    if controls:
        iv_vars.extend([c for c in controls if c in df.columns])

    # Drop rows with missing IV or controls
    model_df = df[[dv_col] + iv_vars].dropna()
    model_df = model_df.copy()

    # Reset index to access gvkey and year for clustering and FE
    model_df = model_df.reset_index()

    # Add intercept
    X = model_df[iv_vars].copy()
    X = sm.add_constant(X)
    y = model_df[dv_col]

    # Add firm and year FE if requested
    if include_fe:
        # Use firm dummies and year dummies
        firm_dummies = pd.get_dummies(model_df["gvkey"], prefix="firm", drop_first=True)
        year_dummies = pd.get_dummies(model_df["year"], prefix="year", drop_first=True)
        X = pd.concat([X, firm_dummies, year_dummies], axis=1)

    # Check for variation in DV
    if y.sum() == 0 or y.sum() == len(y):
        return {
            "spec": spec,
            "uncertainty_var": uncertainty_var,
            "coefficient": np.nan,
            "se": np.nan,
            "p_two_sided": np.nan,
            "p_one_sided": np.nan,
            "odds_ratio": np.nan,
            "or_ci_lower": np.nan,
            "or_ci_upper": np.nan,
            "n": len(model_df),
            "n_firms": model_df["gvkey"].nunique(),
            "n_takeovers": int(y.sum()),
            "pseudo_r2": np.nan,
            "converged": False,
            "error": "No variation in dependent variable",
        }

    # Fit logit with clustered SE
    try:
        logit_model = sm.Logit(y, X)
        results = logit_model.fit(
            cov_type="cluster",
            cov_kwds={"groups": model_df["gvkey"]},
            disp=False,
            maxiter=100,
        )

        # Extract uncertainty coefficient
        if uncertainty_var not in results.params:
            return {
                "spec": spec,
                "uncertainty_var": uncertainty_var,
                "coefficient": np.nan,
                "se": np.nan,
                "p_two_sided": np.nan,
                "p_one_sided": np.nan,
                "odds_ratio": np.nan,
                "or_ci_lower": np.nan,
                "or_ci_upper": np.nan,
                "n": len(model_df),
                "n_firms": model_df["gvkey"].nunique(),
                "n_takeovers": int(y.sum()),
                "pseudo_r2": np.nan,
                "converged": False,
                "error": f"{uncertainty_var} not in results.params",
            }

        coef = results.params[uncertainty_var]
        se = results.bse[uncertainty_var]
        p_two = results.pvalues[uncertainty_var]
        p_one = p_two / 2 if coef > 0 else 1 - p_two / 2  # H8a: beta > 0

        # Calculate odds ratio
        odds_ratio = np.exp(coef)
        or_ci_lower = np.exp(coef - 1.96 * se)
        or_ci_upper = np.exp(coef + 1.96 * se)

        return {
            "spec": spec,
            "uncertainty_var": uncertainty_var,
            "coefficient": coef,
            "se": se,
            "p_two_sided": p_two,
            "p_one_sided": p_one,
            "odds_ratio": odds_ratio,
            "or_ci_lower": or_ci_lower,
            "or_ci_upper": or_ci_upper,
            "n": len(model_df),
            "n_firms": model_df["gvkey"].nunique(),
            "n_takeovers": int(y.sum()),
            "pseudo_r2": results.prsquared,
            "converged": True,
            "error": None,
        }
    except Exception as e:
        return {
            "spec": spec,
            "uncertainty_var": uncertainty_var,
            "coefficient": np.nan,
            "se": np.nan,
            "p_two_sided": np.nan,
            "p_one_sided": np.nan,
            "odds_ratio": np.nan,
            "or_ci_lower": np.nan,
            "or_ci_upper": np.nan,
            "n": len(model_df),
            "n_firms": model_df["gvkey"].nunique(),
            "n_takeovers": int(y.sum()) if "y" in locals() else 0,
            "pseudo_r2": np.nan,
            "converged": False,
            "error": str(e),
        }


def run_all_regressions(df, uncertainty_measures, control_vars, specs):
    """
    Run all H8 regressions.

    Args:
        df: Dataset with MultiIndex (gvkey, year)
        uncertainty_measures: List of uncertainty IV names
        control_vars: List of control variable names
        specs: Dict of specification configurations

    Returns:
        List of regression result dicts
    """
    results = []

    for spec_name, spec_config in specs.items():
        print(f"\nRunning specification: {spec_name}")

        for iv in uncertainty_measures:
            print(f"  IV: {iv}...")

            result = run_h8_logit(
                df,
                iv,
                dv_col="takeover_fwd",
                controls=control_vars,
                include_fe=spec_config["include_fe"],
                spec=spec_name,
            )

            results.append(result)

            if result["converged"]:
                print(
                    f"    Coef: {result['coefficient']:.4f}, SE: {result['se']:.4f}, "
                    f"p (one-tailed): {result['p_one_sided']:.4f}, OR: {result['odds_ratio']:.2f}"
                )
            else:
                print(f"    ERROR: {result['error']}")

    return results


def apply_fdr_correction(results_list):
    """
    Apply FDR correction to primary specification results.

    Args:
        results_list: List of regression result dicts

    Returns:
        Modified results_list with p_fdr added
    """
    from statsmodels.stats.multitest import multipletests

    # Filter to primary spec results
    primary_results = [
        r for r in results_list if r["spec"] == "primary" and r["converged"]
    ]

    if not primary_results:
        print("\nWARNING: No converged primary results for FDR correction")
        return results_list

    # Extract p-values
    p_values = [r["p_one_sided"] for r in primary_results]

    # Apply FDR correction (Benjamini-Hochberg)
    reject, pvals_corrected, _, _ = multipletests(p_values, alpha=0.05, method="fdr_bh")

    # Add FDR-corrected p-values to results
    primary_idx = 0
    for i, result in enumerate(results_list):
        if result["spec"] == "primary" and result["converged"]:
            results_list[i]["p_fdr"] = pvals_corrected[primary_idx]
            results_list[i]["fdr_reject"] = reject[primary_idx]
            primary_idx += 1

    return results_list


# ==============================================================================
# Robustness Functions
# ==============================================================================


def create_takeover_timing_variants(df, dv_base="takeover_completed", lags=None):
    """
    Create DV variants for different timing assumptions (binary).

    For takeover prediction, we test whether uncertainty predicts
    takeover in same year (t), next year (t+1), or two years ahead (t+2).

    Args:
        df: DataFrame with MultiIndex (gvkey, year)
        dv_base: Base column name for takeover indicator
        lags: List of lag values (0=concurrent, -1=forward, -2=lead)

    Returns:
        Dict of {timing_name: (df_with_timing_variant, dv_col_name)}
    """
    if lags is None:
        lags = [0, -1, -2]
    timing_variants = {}
    timing_names = {0: "concurrent", -1: "forward", -2: "lead"}

    # Handle takeover_fwd (already forward-looking) mapping
    dv_col_map = {"takeover_completed": "takeover_fwd", "takeover_fwd": "takeover_fwd"}

    actual_dv_base = dv_col_map.get(dv_base, dv_base)

    for lag in lags:
        df_work = df.reset_index() if isinstance(df.index, pd.MultiIndex) else df.copy()

        if lag == 0:
            # Concurrent: use current year takeover
            # For takeover_fwd which is already forward, concurrent means shift(+1) to get current
            if actual_dv_base == "takeover_fwd":
                df_work["takeover_timing"] = df_work.groupby("gvkey")[
                    actual_dv_base
                ].shift(1)
            else:
                df_work["takeover_timing"] = df_work[actual_dv_base]
        elif lag == -1:
            # Forward (primary): takeover_fwd is already forward-looking
            df_work["takeover_timing"] = df_work[actual_dv_base]
        else:  # lag == -2
            # Lead (t+2): shift forward by one more year
            df_work["takeover_timing"] = df_work.groupby("gvkey")[actual_dv_base].shift(
                -abs(lag) + 1
            )

        df_work["takeover_timing"] = df_work["takeover_timing"].fillna(0).astype(int)
        df_work = df_work.set_index(["gvkey", "year"])
        timing_variants[timing_names[lag]] = (df_work, "takeover_timing")

    return timing_variants


def run_h8_cox_ph(df, uncertainty_var, dv_col="time_to_takeover", controls=None):
    """
    Run Cox proportional hazards model for takeover prediction.

    Uses survival analysis framework: time until takeover event.
    Censoring: firms not acquired by end of sample.

    Args:
        df: Dataset with MultiIndex (gvkey, year)
        uncertainty_var: Name of uncertainty IV
        dv_col: Duration/time column name
        controls: List of control variable names

    Returns:
        dict with hazard ratios and statistics, or None if lifelines unavailable
    """
    try:
        from lifelines import CoxPHFitter  # type: ignore[import-untyped]
    except ImportError:
        print("    Note: lifelines not available, skipping Cox PH")
        return None

    # Prepare data - need to create survival analysis format
    # For each firm, calculate time to takeover or censoring
    df_work = df.reset_index() if isinstance(df.index, pd.MultiIndex) else df.copy()

    # Check if takeover_fwd exists
    if "takeover_fwd" not in df_work.columns:
        return None

    # Create survival dataset: one row per firm
    # For each firm, find first takeover year or censor at end
    firm_survival = []
    for gvkey in df_work["gvkey"].unique():
        firm_df = df_work[df_work["gvkey"] == gvkey].sort_values("year")

        # Find first takeover
        takeover_idx = firm_df[firm_df["takeover_fwd"] == 1].index

        if len(takeover_idx) > 0:
            # Firm gets taken over - use first observation with takeover_fwd=1
            first_takeover_row = firm_df.loc[takeover_idx[0]]
            firm_survival.append(
                {
                    "gvkey": gvkey,
                    "duration": 1,  # Binary: 1 if taken over
                    "event": 1,
                    uncertainty_var: first_takeover_row[uncertainty_var],
                }
            )
        else:
            # Censored - use last observation
            last_row = firm_df.iloc[-1]
            firm_survival.append(
                {
                    "gvkey": gvkey,
                    "duration": 0,  # Binary: 0 if censored
                    "event": 0,
                    uncertainty_var: last_row[uncertainty_var],
                }
            )

    survival_df = pd.DataFrame(firm_survival)

    # Cox PH requires variation in duration (can't be all 0 or 1)
    if survival_df["duration"].nunique() < 2:
        return None

    # Drop rows with missing IV
    survival_df = survival_df.dropna(subset=[uncertainty_var])

    if len(survival_df) < 50:
        return None  # Too few observations

    # Fit Cox model
    try:
        cph = CoxPHFitter()
        cph.fit(survival_df, duration_col="duration", event_col="event")

        # Extract results for uncertainty variable
        if uncertainty_var not in cph.summary.index:
            return None

        summary = cph.summary.loc[uncertainty_var]

        return {
            "model_type": "cox_ph",
            "uncertainty_var": uncertainty_var,
            "coefficient": summary["coef"],
            "se": summary["se(coef)"],
            "p_two_sided": summary["p"],
            "p_one_sided": summary["p"] / 2
            if summary["coef"] > 0
            else 1 - summary["p"] / 2,
            "hazard_ratio": summary["exp(coef)"],
            "ci_lower": summary["exp(coef) lower 95%"],
            "ci_upper": summary["exp(coef) upper 95%"],
            "n": len(survival_df),
            "n_firms": survival_df["gvkey"].nunique(),
            "n_takeovers": int(survival_df["event"].sum()),
            "converged": True,
            "error": None,
        }
    except Exception as e:
        return {
            "model_type": "cox_ph",
            "uncertainty_var": uncertainty_var,
            "coefficient": np.nan,
            "se": np.nan,
            "p_two_sided": np.nan,
            "p_one_sided": np.nan,
            "hazard_ratio": np.nan,
            "ci_lower": np.nan,
            "ci_upper": np.nan,
            "n": len(survival_df) if "survival_df" in locals() else 0,
            "n_firms": survival_df["gvkey"].nunique()
            if "survival_df" in locals()
            else 0,
            "n_takeovers": 0,
            "converged": False,
            "error": str(e),
        }


def run_h8_robustness_suite(df, uncertainty_measures, control_vars):
    """
    Run full robustness suite for H8.

    Dimensions:
    1. Alternative DVs (announced, hostile)
    2. Alternative specs (pooled)
    3. Alternative IVs (CEO-only, Presentation-only)
    4. Timing variants (concurrent, forward, lead)
    5. Alternative models (Cox PH if available)

    Args:
        df: Dataset with MultiIndex (gvkey, year)
        uncertainty_measures: List of primary uncertainty IV names
        control_vars: List of control variable names

    Returns:
        List of robustness result dicts
    """
    results = []

    print("\n" + "=" * 60)
    print("Running H8 Robustness Suite")
    print("=" * 60)

    # Dimension 1: Alternative DVs
    print("\n[Dimension 1] Alternative Dependent Variables")
    for dv_col, dv_label in H8_ROBUSTNESS_CONFIG["alternative_dvs"].items():
        if dv_col not in df.columns:
            print(f"  Skipping {dv_col}: not in data")
            continue

        print(f"  Testing DV: {dv_col} ({dv_label})")

        for uv in uncertainty_measures:
            if uv not in df.columns:
                continue

            result = run_h8_logit(
                df, uv, dv_col, control_vars, include_fe=True, spec="primary"
            )

            if result:
                result["dv_type"] = dv_label
                result["robustness_dim"] = "alt_dv"
                results.append(result)

                if result["converged"]:
                    print(
                        f"    {uv}: p={result['p_one_sided']:.4f}, OR={result['odds_ratio']:.2f}"
                    )
                else:
                    print(f"    {uv}: FAILED - {result['error']}")

    # Dimension 2: Alternative specs (pooled already done in main loop)
    # Skip to avoid duplication - pooled is already in SPECS

    # Dimension 3: Alternative IVs
    print("\n[Dimension 2] Alternative Independent Variables")
    for iv_type, ivs in H8_ROBUSTNESS_CONFIG["alternative_ivs"].items():
        print(f"  Testing IV set: {iv_type}")

        for uv in ivs:
            if uv not in df.columns:
                continue

            result = run_h8_logit(
                df, uv, "takeover_fwd", control_vars, include_fe=True, spec="primary"
            )

            if result:
                result["iv_type"] = iv_type
                result["robustness_dim"] = "alt_iv"
                results.append(result)

                if result["converged"]:
                    print(
                        f"    {uv}: p={result['p_one_sided']:.4f}, OR={result['odds_ratio']:.2f}"
                    )
                else:
                    print(f"    {uv}: FAILED - {result['error']}")

    # Dimension 4: Timing variants
    print("\n[Dimension 3] Timing Tests")
    timing_variants = create_takeover_timing_variants(
        df, "takeover_completed", [0, -1, -2]
    )

    for timing_name, (df_t, dv_col) in timing_variants.items():
        print(f"  Testing timing: {timing_name}")

        for uv in uncertainty_measures:
            if uv not in df_t.columns:
                continue

            result = run_h8_logit(
                df_t, uv, dv_col, control_vars, include_fe=True, spec="primary"
            )

            if result:
                result["timing"] = timing_name
                result["robustness_dim"] = "timing"
                results.append(result)

                if result["converged"]:
                    print(
                        f"    {uv}: p={result['p_one_sided']:.4f}, OR={result['odds_ratio']:.2f}"
                    )
                else:
                    print(f"    {uv}: FAILED - {result['error']}")

    # Dimension 5: Cox PH (if available)
    if H8_ROBUSTNESS_CONFIG["alternative_models"]["cox_ph"]:
        print("\n[Dimension 4] Cox Proportional Hazards Model")

        # Try to run Cox PH for primary IVs
        for uv in uncertainty_measures:
            if uv not in df.columns:
                continue

            cox_result = run_h8_cox_ph(df, uv, "time_to_takeover", control_vars)

            if cox_result:
                cox_result["robustness_dim"] = "alt_model"
                results.append(cox_result)

                if cox_result["converged"]:
                    print(
                        f"  {uv}: HR={cox_result['hazard_ratio']:.2f}, p={cox_result['p_one_sided']:.4f}"
                    )
                elif cox_result.get("error"):
                    print(f"  {uv}: FAILED - {cox_result['error']}")
                else:
                    print(
                        f"  {uv}: Skipped (lifelines unavailable or insufficient data)"
                    )

    print(f"\nRobustness suite complete: {len(results)} tests")

    return results


# ==============================================================================
# Output Functions
# ==============================================================================


def save_regression_results(results_list, output_dir):
    """
    Save regression results to parquet.

    Args:
        results_list: List of regression result dicts
        output_dir: Output directory path

    Returns:
        Path to saved parquet file
    """
    output_file = output_dir / "H8_Regression_Results.parquet"

    df_results = pd.DataFrame(results_list)

    # Reorder columns - include robustness columns
    col_order = [
        "spec",
        "uncertainty_var",
        "coefficient",
        "se",
        "p_two_sided",
        "p_one_sided",
        "p_fdr",
        "fdr_reject",
        "odds_ratio",
        "or_ci_lower",
        "or_ci_upper",
        "hazard_ratio",
        "ci_lower",
        "ci_upper",  # Cox PH columns
        "dv_type",
        "iv_type",
        "timing",
        "model_type",
        "robustness_dim",  # Robustness columns
        "n",
        "n_firms",
        "n_takeovers",
        "pseudo_r2",
        "converged",
        "error",
    ]

    # Only include columns that exist
    col_order = [c for c in col_order if c in df_results.columns]
    df_results = df_results[col_order]  # type: ignore[assignment]

    df_results.to_parquet(output_file, index=False)
    print(f"\nSaved regression results to: {output_file}")

    return output_file


def generate_h8_results_report(results_list, sample_stats, timestamp):
    """
    Generate H8 results report in markdown with robustness sections.

    Special focus on odds ratios for interpretation.

    Args:
        results_list: List of regression result dicts
        sample_stats: Dict with sample statistics
        timestamp: Execution timestamp

    Returns:
        Markdown report string
    """
    report = (
        "# H8 Regression Results: Speech Uncertainty -> Takeover Target Probability\n\n"
    )

    # Executive summary
    primary_results = [
        r
        for r in results_list
        if r.get("spec") == "primary"
        and r.get("converged", False)
        and r.get("robustness_dim") is None
    ]
    n_sig = sum(1 for r in primary_results if r.get("p_one_sided", 1) < 0.05)
    n_fdr = sum(1 for r in primary_results if r.get("p_fdr", 1) < 0.05)

    # Count robustness results
    robustness_results = [
        r for r in results_list if r.get("robustness_dim") is not None
    ]
    n_rob = len(robustness_results)
    n_rob_sig = sum(
        1
        for r in robustness_results
        if r.get("p_one_sided", 1) < 0.05 and r.get("converged", False)
    )

    report += f"**Date:** {timestamp}\n"
    report += f"**Sample:** {sample_stats['n_obs']:,} firm-years, {sample_stats['n_firms']:,} firms\n"
    report += f"**Years:** {sample_stats['year_range']}\n"
    report += f"**Takeover events:** {sample_stats['n_takeovers']}\n"
    report += f"**Takeover rate:** {sample_stats['takeover_rate']:.2%}\n\n"

    report += "## Executive Summary\n\n"
    report += "**Hypothesis H8a:** Higher speech uncertainty predicts HIGHER takeover probability (beta > 0)\n\n"
    report += "**Conclusion:** "
    if n_fdr >= 4:
        report += "SUPPORTED - Strong evidence\n"
    elif n_fdr >= 2:
        report += "WEAKLY SUPPORTED - Moderate evidence\n"
    elif n_fdr >= 1:
        report += "MIXED - Limited evidence\n"
    else:
        report += "NOT SUPPORTED - No consistent evidence\n"

    report += f"\n**Primary specification significant measures (p < 0.05, one-tailed):** {n_sig}/{len(primary_results)}\n"
    report += f"**After FDR correction:** {n_fdr}/{len(primary_results)}\n"
    report += f"**Robustness tests:** {n_rob_sig}/{n_rob} significant\n\n"

    # Primary spec results table
    report += "## Primary Specification Results\n\n"
    if primary_results:
        report += "| Uncertainty Measure | Beta | SE | Odds Ratio | 95% CI OR | p (one-tailed) | FDR | Significant? |\n"
        report += "|---------------------|------|----|------------|-----------|----------------|-----|--------------|\n"

        for r in primary_results:
            sig = "Yes" if r.get("p_one_sided", 1) < 0.05 else "No"
            fdr_sig = "Yes" if r.get("p_fdr", 1) < 0.05 else "No"
            or_ci = f"[{r.get('or_ci_lower', 0):.2f}, {r.get('or_ci_upper', 0):.2f}]"
            report += f"| {r.get('uncertainty_var', 'N/A')} | {r.get('coefficient', 0):.4f} | {r.get('se', 0):.4f} | {r.get('odds_ratio', 0):.2f} | {or_ci} | {r.get('p_one_sided', 1):.4f} | {fdr_sig} | {sig} |\n"
    else:
        report += "No primary specification results (all failed to converge).\n"

    # Pooled spec results (if available)
    pooled_results = [
        r
        for r in results_list
        if r.get("spec") == "pooled" and r.get("converged", False)
    ]
    if pooled_results:
        report += "\n## Pooled Specification Results (No Fixed Effects)\n\n"
        report += "| Uncertainty Measure | Beta | SE | Odds Ratio | 95% CI OR | p (one-tailed) | Significant? |\n"
        report += "|---------------------|------|----|------------|-----------|----------------|--------------|\n"

        for r in pooled_results:
            sig = "Yes" if r.get("p_one_sided", 1) < 0.05 else "No"
            or_ci = f"[{r.get('or_ci_lower', 0):.2f}, {r.get('or_ci_upper', 0):.2f}]"
            report += f"| {r.get('uncertainty_var', 'N/A')} | {r.get('coefficient', 0):.4f} | {r.get('se', 0):.4f} | {r.get('odds_ratio', 0):.2f} | {or_ci} | {r.get('p_one_sided', 1):.4f} | {sig} |\n"

    # ========================================================================
    # Robustness Suite Results
    # ========================================================================

    if robustness_results:
        report += "\n## Robustness Suite Results\n\n"

        # Alternative DVs
        alt_dv_results = [
            r for r in robustness_results if r.get("robustness_dim") == "alt_dv"
        ]
        if alt_dv_results:
            report += "### Alternative Dependent Variables\n\n"
            report += "| DV | UV | Beta | Odds Ratio | 95% CI OR | p (one-tailed) | Significant? |\n"
            report += "|----|----|------|------------|-----------|----------------|--------------|\n"
            for r in alt_dv_results:
                if r.get("converged", False):
                    sig = "Yes" if r.get("p_one_sided", 1) < 0.05 else "No"
                    or_ci = f"[{r.get('or_ci_lower', 0):.2f}, {r.get('or_ci_upper', 0):.2f}]"
                    dv_type = r.get("dv_type", "Unknown")
                    report += f"| {dv_type} | {r.get('uncertainty_var', 'N/A')} | {r.get('coefficient', 0):.4f} | {r.get('odds_ratio', 0):.2f} | {or_ci} | {r.get('p_one_sided', 1):.4f} | {sig} |\n"

            n_sig = sum(
                1
                for r in alt_dv_results
                if r.get("p_one_sided", 1) < 0.05 and r.get("converged", False)
            )
            report += f"\n**Summary:** {n_sig}/{len(alt_dv_results)} significant\n"

        # Alternative IVs
        alt_iv_results = [
            r for r in robustness_results if r.get("robustness_dim") == "alt_iv"
        ]
        if alt_iv_results:
            report += "\n### Alternative Independent Variables\n\n"
            for iv_type in ["ceo_only", "presentation_only", "qa_only"]:
                iv_results = [r for r in alt_iv_results if r.get("iv_type") == iv_type]
                if iv_results:
                    n_sig = sum(
                        1
                        for r in iv_results
                        if r.get("p_one_sided", 1) < 0.05 and r.get("converged", False)
                    )
                    report += (
                        f"- **{iv_type}**: {n_sig}/{len(iv_results)} significant\n"
                    )
                    for r in iv_results:
                        if r.get("converged", False):
                            sig = "Yes" if r.get("p_one_sided", 1) < 0.05 else "No"
                            report += f"  - {r.get('uncertainty_var', 'N/A')}: OR={r.get('odds_ratio', 0):.2f}, p={r.get('p_one_sided', 1):.4f}, {sig}\n"

        # Timing tests
        timing_results = [
            r for r in robustness_results if r.get("robustness_dim") == "timing"
        ]
        if timing_results:
            report += "\n### Timing Tests\n\n"
            report += (
                "| Timing | UV | Beta | Odds Ratio | p (one-tailed) | Significant? |\n"
            )
            report += (
                "|--------|----|------|------------|----------------|--------------|\n"
            )
            for r in timing_results:
                if r.get("converged", False):
                    sig = "Yes" if r.get("p_one_sided", 1) < 0.05 else "No"
                    timing = r.get("timing", "Unknown")
                    report += f"| {timing} | {r.get('uncertainty_var', 'N/A')} | {r.get('coefficient', 0):.4f} | {r.get('odds_ratio', 0):.2f} | {r.get('p_one_sided', 1):.4f} | {sig} |\n"

            for timing in ["concurrent", "forward", "lead"]:
                timing_tests = [r for r in timing_results if r.get("timing") == timing]
                if timing_tests:
                    n_sig = sum(
                        1
                        for r in timing_tests
                        if r.get("p_one_sided", 1) < 0.05 and r.get("converged", False)
                    )
                    report += (
                        f"- **{timing}**: {n_sig}/{len(timing_tests)} significant\n"
                    )

        # Cox PH results
        cox_results = [r for r in robustness_results if r.get("model_type") == "cox_ph"]
        if cox_results:
            report += "\n### Cox Proportional Hazards Model\n\n"
            report += "Survival analysis results (hazard ratios):\n\n"
            report += (
                "| UV | Hazard Ratio | 95% CI HR | p (one-tailed) | Significant? |\n"
            )
            report += (
                "|----|--------------|-----------|----------------|--------------|\n"
            )
            for r in cox_results:
                if r.get("converged", False):
                    sig = "Yes" if r.get("p_one_sided", 1) < 0.05 else "No"
                    ci = f"[{r.get('ci_lower', 0):.2f}, {r.get('ci_upper', 0):.2f}]"
                    report += f"| {r.get('uncertainty_var', 'N/A')} | {r.get('hazard_ratio', 0):.2f} | {ci} | {r.get('p_one_sided', 1):.4f} | {sig} |\n"

        # Robustness conclusion
        report += "\n### Robustness Conclusion\n\n"
        rob_converged = [r for r in robustness_results if r.get("converged", False)]
        if rob_converged:
            n_sig = sum(1 for r in rob_converged if r.get("p_one_sided", 1) < 0.05)
            rob_total = len(rob_converged)
            report += f"Across {rob_total} robustness tests, {n_sig} ({n_sig / rob_total * 100:.1f}%) show significant effects.\n\n"

            if n_sig / rob_total > 0.5:
                report += "**Robustness Assessment:** Results are ROBUST - majority of tests significant.\n"
            elif n_sig / rob_total > 0.2:
                report += "**Robustness Assessment:** Results are MIXED - some specifications significant.\n"
            else:
                report += "**Robustness Assessment:** Results are NOT ROBUST - few specifications significant.\n"
        else:
            report += "**Robustness Assessment:** No robustness tests converged (likely due to low event count).\n"

    # Interpretation guide
    report += "\n### Interpretation\n\n"
    report += "Odds ratios > 1.0 indicate higher takeover probability per unit increase in uncertainty.\n"
    report += "For example, OR = 1.05 means 5% higher odds of takeover for each 1% increase in uncertainty.\n\n"

    # Warnings
    if sample_stats["n_takeovers"] < 100:
        report += "\n## Warnings\n\n"
        report += f"- **Low takeover events:** Only {sample_stats['n_takeovers']} takeover events in sample "
        report += "(expected minimum: 100)\n"
        report += (
            "- This limits statistical power and may affect reliability of estimates\n"
        )

    if sample_stats["takeover_rate"] < 0.005:
        if "## Warnings\n\n" not in report:
            report += "\n## Warnings\n\n"
        report += f"- **Low takeover rate:** {sample_stats['takeover_rate']:.2%} is below expected range (0.5%-5%)\n"
        report += (
            "- H7 sample period (2002-2004) is very short, limiting takeover events\n"
        )

    return report


def save_results_report(report, output_dir):
    """
    Save results report to markdown.

    Args:
        report: Markdown report string
        output_dir: Output directory path

    Returns:
        Path to saved markdown file
    """
    output_file = output_dir / "H8_RESULTS.md"

    with open(output_file, "w") as f:
        f.write(report)

    print(f"Saved results report to: {output_file}")
    return output_file


def generate_latex_table(results, output_dir):
    """
    Generate publication-ready LaTeX regression table for H8 logistic results.

    Shows odds ratios (exp(beta)) with 95% CI and significance stars.
    Designed for logit regression results.

    Args:
        results: List of regression result dicts from run_h8_logit
        output_dir: Output directory path

    Returns:
        Path to saved LaTeX file
    """
    # Variable labels for display
    var_labels = {
        "Manager_QA_Uncertainty_pct": "QA Unc. (Mgr)",
        "CEO_QA_Uncertainty_pct": "QA Unc. (CEO)",
        "Manager_QA_Weak_Modal_pct": "Weak Modal (Mgr)",
        "CEO_QA_Weak_Modal_pct": "Weak Modal (CEO)",
        "Manager_Pres_Uncertainty_pct": "Pres. Unc. (Mgr)",
        "CEO_Pres_Uncertainty_pct": "Pres. Unc. (CEO)",
        "uncertainty_gap": "Uncertainty Gap",
    }

    # Filter to primary specification and converged results
    primary_results = [
        r for r in results
        if r.get("spec") == "primary" and r.get("converged", False)
    ]

    if not primary_results:
        print("No converged primary results for LaTeX table")
        return None

    lines = []

    # Table header
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\caption{H8 Results: Speech Uncertainty and Takeover Probability}")
    lines.append(r"\label{tab:h8_takeover}")
    lines.append(r"\begin{tabular}{lcccccc}")

    # Header
    lines.append(r"\toprule")
    dvs = [r["uncertainty_var"] for r in primary_results]
    n_models = len(dvs)

    lines.append(" & " + " & ".join([f"({i + 1})" for i in range(n_models)]) + r" \\")
    lines.append(" & " + " & ".join([var_labels.get(dv, dv) for dv in dvs]) + r" \\")
    lines.append(r"\midrule")

    # Odds ratio row (H8 uses logit, so show ORs)
    or_row = ["Odds Ratio"]
    ci_row = [r"[95\% CI]"]

    for r in primary_results:
        or_val = r.get("odds_ratio", np.nan)
        ci_lo = r.get("or_ci_lower", np.nan)
        ci_hi = r.get("or_ci_upper", np.nan)
        p_one = r.get("p_one_sided", np.nan)

        if np.isnan(or_val):
            or_row.append("")
            ci_row.append("")
            continue

        # Add stars based on one-sided p-value (H8a: beta > 0)
        if p_one < 0.01:
            stars = "***"
        elif p_one < 0.05:
            stars = "**"
        elif p_one < 0.10:
            stars = "*"
        else:
            stars = ""

        or_row.append(f"{or_val:.3f}{stars}")
        ci_row.append(f"[{ci_lo:.3f}, {ci_hi:.3f}]")

    lines.append(" & ".join(or_row) + r" \\")
    lines.append(" & ".join(ci_row) + r" \\")

    # Statistics rows
    lines.append(r"\midrule")

    # N row
    n_row = ["N"]
    for r in primary_results:
        n_row.append(f"{r.get('n', 0):,}")
    lines.append(" & ".join(n_row) + r" \\")

    # Pseudo R2 row
    r2_row = ["Pseudo R$^2$"]
    for r in primary_results:
        r2_row.append(f"{r.get('pseudo_r2', 0):.3f}")
    lines.append(" & ".join(r2_row) + r" \\")

    # Takeovers row
    tk_row = ["Takeovers"]
    for r in primary_results:
        tk_row.append(f"{r.get('n_takeovers', 0):,}")
    lines.append(" & ".join(tk_row) + r" \\")

    # Fixed effects row
    lines.append(r"\midrule")
    lines.append("Firm FE & " + " & ".join(["Yes"] * n_models) + r" \\")
    lines.append("Year FE & " + " & ".join(["Yes"] * n_models) + r" \\")

    # Footer
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\begin{tablenotes}[flushleft]")
    lines.append(r"\small")
    lines.append(r"\item Odds ratios from logit regression. 95\% confidence intervals in brackets.")
    lines.append(r"\item *** p<0.01, ** p<0.05, * p<0.10 (one-tailed for H8a: OR > 1).")
    lines.append(r"\end{tablenotes}")
    lines.append(r"\end{table}")

    latex_str = "\n".join(lines)

    latex_path = output_dir / "H8_Regression_Table.tex"
    with open(latex_path, "w", encoding="utf-8") as f:
        f.write(latex_str)

    print(f"Saved LaTeX table: {latex_path}")
    return latex_path


# ==============================================================================
# Main Execution
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="H8 Takeover Regression - Test whether speech uncertainty predicts takeover likelihood"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate prerequisites and exit without processing",
    )
    return parser.parse_args()


def check_prerequisites(paths):
    """Check that required inputs exist"""
    print("Checking prerequisites...")

    ok = True
    if not paths["h8_file"].exists():
        print(f"  [ERROR] H8 data not found: {paths['h8_file']}")
        ok = False
    else:
        print(f"  [OK] H8 data: {paths['h8_file']}")

    return ok


def main():
    """Main execution"""
    args = parse_arguments()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    paths = setup_paths(timestamp)

    # Handle dry-run mode
    if args.dry_run:
        print("=" * 60)
        print("STEP 4.8: H8 Takeover Regression - DRY RUN")
        print(f"Timestamp: {timestamp}")
        print("=" * 60)

        prereq_ok = check_prerequisites(paths)
        if prereq_ok:
            print("\n[OK] All prerequisites validated")
            print("\nWould compute:")
            print("  - Logistic regressions (4 uncertainty measures x 2 specs)")
            print("  - Firm and year fixed effects")
            print("  - Firm-clustered standard errors")
            print("  - FDR correction across measures")
            print("  - Robustness suite (alt DVs, alt IVs, timing tests, Cox PH)")
            print(f"\nOutput would be written to: {paths['output_dir']}")
            sys.exit(0)
        else:
            print("\n[ERROR] Prerequisites not met")
            sys.exit(1)

    # Check prerequisites before processing
    prereq_ok = check_prerequisites(paths)
    if not prereq_ok:
        print("\n[ERROR] Prerequisites not met. Exiting.")
        sys.exit(1)

    # Setup logging
    dual_writer = DualWriter(paths["log_file"])
    sys.stdout = dual_writer

    print("=" * 60)
    print("STEP 4.8: H8 Takeover Regression")
    print(f"Timestamp: {timestamp}")
    print("=" * 60)

    # Initialize statistics
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    mem_start = get_process_memory_mb()
    memory_readings = [mem_start["rss_mb"]]

    stats = {
        "step_id": "4.8_H8TakeoverRegression",
        "timestamp": timestamp,
        "git_sha": get_git_sha(),
        "input": {"files": [], "checksums": {}, "total_rows": 0},
        "processing": {
            "n_regressions": 0,
            "n_converged": 0,
            "n_significant": 0,
            "n_robustness": 0,
            "n_robustness_converged": 0,
            "n_robustness_sig": 0,
        },
        "output": {"files": [], "checksums": {}, "final_rows": 0},
        "sample_stats": {},
        "results": [],
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
        "memory": {
            "start_mb": mem_start["rss_mb"],
            "end_mb": 0.0,
            "peak_mb": 0.0,
            "delta_mb": 0.0,
        },
    }

    # ========================================================================
    # Load Data
    # ========================================================================

    print("\nLoading data...")

    print("\nH8 Takeover Data:")
    stats["input"]["files"].append(str(paths["h8_file"]))
    stats["input"]["checksums"][paths["h8_file"].name] = compute_file_checksum(
        paths["h8_file"]
    )
    h8_df = load_h8_data(paths["h8_file"])
    stats["input"]["total_rows"] = len(h8_df)

    # Sample statistics
    sample_stats = {
        "n_obs": len(h8_df),
        "n_firms": h8_df.index.get_level_values("gvkey").nunique(),
        "year_range": f"{h8_df.index.get_level_values('year').min()}-{h8_df.index.get_level_values('year').max()}",
        "n_takeovers": int(h8_df["takeover_fwd"].sum()),
        "takeover_rate": float(h8_df["takeover_fwd"].mean()),
    }
    stats["sample_stats"] = sample_stats

    # ========================================================================
    # Run Regressions
    # ========================================================================

    print("\n" + "=" * 60)
    print("Running H8 Logistic Regressions")
    print("=" * 60)

    results = run_all_regressions(h8_df, UNCERTAINTY_MEASURES, CONTROL_VARS, SPECS)

    stats["processing"]["n_regressions"] = len(results)
    stats["processing"]["n_converged"] = sum(1 for r in results if r["converged"])
    stats["processing"]["n_significant"] = sum(
        1 for r in results if r["converged"] and r["p_one_sided"] < 0.05
    )

    print(f"\nRegressions completed: {len(results)}")
    print(f"  Converged: {stats['processing']['n_converged']}")
    print(
        f"  Significant (p < 0.05, one-tailed): {stats['processing']['n_significant']}"
    )

    # ========================================================================
    # Apply FDR Correction
    # ========================================================================

    print("\n" + "=" * 60)
    print("Applying FDR Correction (Benjamini-Hochberg)")
    print("=" * 60)

    results = apply_fdr_correction(results)

    n_fdr_sig = sum(
        1 for r in results if r["spec"] == "primary" and r.get("p_fdr", 1) < 0.05
    )
    print(
        f"Primary spec significant after FDR: {n_fdr_sig}/{len(UNCERTAINTY_MEASURES)}"
    )

    # ========================================================================
    # Run Robustness Suite
    # ========================================================================

    print("\n" + "=" * 60)
    print("Running Robustness Suite")
    print("=" * 60)

    robustness_results = run_h8_robustness_suite(
        h8_df, UNCERTAINTY_MEASURES, CONTROL_VARS
    )

    # Combine primary and robustness results
    all_results = results + robustness_results

    stats["processing"]["n_robustness"] = len(robustness_results)
    stats["processing"]["n_robustness_converged"] = sum(
        1 for r in robustness_results if r.get("converged", False)
    )
    stats["processing"]["n_robustness_sig"] = sum(
        1
        for r in robustness_results
        if r.get("converged", False) and r.get("p_one_sided", 1) < 0.05
    )

    print(f"\nRobustness tests completed: {len(robustness_results)}")
    print(f"  Converged: {stats['processing']['n_robustness_converged']}")
    print(
        f"  Significant (p < 0.05, one-tailed): {stats['processing']['n_robustness_sig']}"
    )

    # Use combined results for reporting
    results = all_results

    # ========================================================================
    # Prepare Output
    # ========================================================================

    print("\n" + "=" * 60)
    print("Preparing Output")
    print("=" * 60)

    # Save regression results
    results_file = save_regression_results(results, paths["output_dir"])
    stats["output"]["files"].append(results_file.name)
    stats["output"]["checksums"][results_file.name] = compute_file_checksum(
        results_file
    )

    # Generate and save report
    report = generate_h8_results_report(results, sample_stats, timestamp)
    report_file = save_results_report(report, paths["output_dir"])
    stats["output"]["files"].append(report_file.name)
    stats["output"]["checksums"][report_file.name] = compute_file_checksum(report_file)

    # Generate LaTeX table
    latex_file = generate_latex_table(results, paths["output_dir"])
    if latex_file:
        stats["output"]["files"].append(latex_file.name)
        stats["output"]["checksums"][latex_file.name] = compute_file_checksum(latex_file)

    # Print report to console
    print("\n" + report)

    # ========================================================================
    # Finalize Statistics
    # ========================================================================

    end_time = time.perf_counter()
    end_iso = datetime.now().isoformat()
    mem_end = get_process_memory_mb()

    stats["timing"]["end_iso"] = end_iso
    stats["timing"]["duration_seconds"] = end_time - start_time
    stats["memory"]["end_mb"] = mem_end["rss_mb"]
    stats["memory"]["peak_mb"] = max(memory_readings)
    stats["memory"]["delta_mb"] = mem_end["rss_mb"] - mem_start["rss_mb"]
    stats["output"]["final_rows"] = len(results)  # Number of regression results

    # Store detailed results
    stats["results"] = results

    # ========================================================================
    # Write Stats
    # ========================================================================

    save_stats(stats, paths["output_dir"])
    print("\nSaved: stats.json")

    # ========================================================================
    # Summary
    # ========================================================================

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print("H8 Takeover Regression completed")
    print(f"  Sample: {sample_stats['n_obs']:,} obs, {sample_stats['n_firms']:,} firms")
    print(f"  Takeover events: {sample_stats['n_takeovers']}")
    print(f"  Takeover rate: {sample_stats['takeover_rate']:.2%}")
    print(
        f"  Primary regressions: {stats['processing']['n_converged']}/{stats['processing']['n_regressions']} converged"
    )
    print(f"  Primary significant (p < 0.05): {stats['processing']['n_significant']}")
    print(f"  Primary after FDR: {n_fdr_sig}")
    print(
        f"  Robustness tests: {stats['processing']['n_robustness_converged']}/{stats['processing']['n_robustness']} converged"
    )
    print(
        f"  Robustness significant (p < 0.05): {stats['processing']['n_robustness_sig']}"
    )

    print(f"\nOutputs saved to: {paths['output_dir']}")
    print(f"Log saved to: {paths['log_file']}")

    print_stats_summary(stats)

    print("\n" + "=" * 60)
    print("STEP 4.8 COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
