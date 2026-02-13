#!/usr/bin/env python3
"""
==============================================================================
STEP 4.10: H2 PRisk x Uncertainty -> Investment Efficiency Regression
==============================================================================
ID: 4.10_H2_PRiskUncertainty_Investment
Description: Panel OLS regressions for H2 (PRisk x Uncertainty -> Investment Efficiency).
             Tests whether compound uncertainty (PRisk x Uncertainty interaction) predicts
             decreased investment efficiency.

Model Specification:
    InvestmentResidual = beta0 + beta1*PRisk_x_Uncertainty + beta2*PRisk_std
                        + beta3*Uncertainty_std + gamma*Controls + Firm FE + Year FE + epsilon

Hypothesis Test:
    H2: beta1 < 0 (Compound uncertainty decreases investment efficiency)
    One-tailed test: p_one_tailed = p_two_tailed / 2 if coefficient < 0

Inputs:
    - 4_Outputs/3_Financial_V2/3.10_H2_PRiskUncertaintyMerge/latest/H2_PRiskUncertainty_Analysis.parquet
      (complete regression dataset from Plan 53-02)

Outputs:
    - 4_Outputs/4_Econometric_V2/4.10_H2_PRiskUncertainty_Investment/{timestamp}/H2_Regression_Results.parquet
      (all regression coefficients, SEs, p-values, diagnostics)
    - 4_Outputs/4_Econometric_V2/4.10_H2_PRiskUncertainty_Investment/{timestamp}/stats.json
      (regression summaries, hypothesis tests, execution metadata)
    - 4_Outputs/4_Econometric_V2/4.10_H2_PRiskUncertainty_Investment/{timestamp}/H2_RESULTS.md
      (human-readable summary of key findings)
    - 3_Logs/4_Econometric_V2/4.10_H2_PRiskUncertainty_Investment/{timestamp}_H2.log
      (execution log with dual-writer output)

Deterministic: true
Dependencies:
    - Requires: Step 3.10_H2_PRiskUncertaintyMerge
    - Uses: shared.regression_utils, shared.panel_ols, linearmodels

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# Add parent directory to sys.path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Import shared utilities
from f1d.shared.dual_writer import DualWriter
from f1d.shared.observability_utils import (
    get_process_memory_mb,
)
from f1d.shared.panel_ols import run_panel_ols
from f1d.shared.path_utils import (
    ensure_output_dir,
    get_latest_output_dir,
    validate_input_file,
)

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


# Regression specifications
PRIMARY_SPEC = {
    "dependent": "InvestmentResidual",
    "exog": [
        "PRisk_x_Uncertainty",
        "PRisk_std",
        "Manager_QA_Uncertainty_pct_std",
        "CashFlow",
        "Size",
        "Leverage",
        "TobinQ",
        "SalesGrowth",
    ],
    "entity_effects": True,
    "time_effects": True,
    "cluster_cols": ["gvkey", "year"],  # Double-clustering per Petersen (2009)
}

ROBUSTNESS_SPECS = {
    "industry_fe": {
        "dependent": "InvestmentResidual",
        "exog": PRIMARY_SPEC["exog"],
        "entity_effects": False,
        "time_effects": True,
        "industry_effects": True,
        "cluster_cols": ["gvkey", "year"],
        "description": "Industry (FF48) + Year FE instead of Firm FE",
    },
    "abs_residual": {
        "dependent": "InvestmentResidual_Abs",
        "exog": PRIMARY_SPEC["exog"],
        "entity_effects": True,
        "time_effects": True,
        "cluster_cols": ["gvkey", "year"],
        "description": "Absolute residual as DV (inefficiency magnitude)",
    },
    "lagged_iv": {
        "dependent": "InvestmentResidual",
        "exog": [
            "PRisk_x_Uncertainty_lag",
            "PRisk_std_lag",
            "Manager_QA_Uncertainty_pct_std_lag",
            "CashFlow",
            "Size",
            "Leverage",
            "TobinQ",
            "SalesGrowth",
        ],
        "entity_effects": True,
        "time_effects": True,
        "cluster_cols": ["gvkey", "year"],
        "description": "Lagged IVs (t-1) to address reverse causality",
    },
    "subsample_2006": {
        "dependent": "InvestmentResidual",
        "exog": PRIMARY_SPEC["exog"],
        "entity_effects": True,
        "time_effects": True,
        "cluster_cols": ["gvkey", "year"],
        "sample_filter": "year >= 2006",
        "description": "Subsample 2006-2018 (exclude sparse early years)",
    },
}

# ==============================================================================
# Path Setup
# ==============================================================================


def setup_paths(config, timestamp):
    """Set up all required paths using get_latest_output_dir"""
    root = Path(__file__).parent.parent.parent

    # Resolve Plan 53-02 output directory
    analysis_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2" / "3.10_H2_PRiskUncertaintyMerge",
        required_file="H2_PRiskUncertainty_Analysis.parquet",
    )

    paths = {
        "root": root,
        "analysis_dir": analysis_dir,
    }

    # Output directory
    output_base = (
        root / "4_Outputs" / "4_Econometric_V2" / "4.10_H2_PRiskUncertainty_Investment"
    )
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = (
        root / "3_Logs" / "4_Econometric_V2" / "4.10_H2_PRiskUncertainty_Investment"
    )
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H2.log"

    return paths


# ==============================================================================
# Data Loading
# ==============================================================================


def load_analysis_dataset(analysis_dir, dw=None):
    """
    Load the merged PRisk x Uncertainty dataset from Plan 53-02.

    Expects H2_PRiskUncertainty_Analysis.parquet with columns:
    - Identifiers: gvkey, year, ff48_code
    - DV: InvestmentResidual
    - IV: PRisk_x_Uncertainty (standardized interaction)
    - Main effects: PRisk_std, Manager_QA_Uncertainty_pct_std
    - Controls: CashFlow, Size, Leverage, TobinQ, SalesGrowth
    - Alternative measures: CEO_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct,
      CEO_Pres_Uncertainty_pct, NPRisk, PRiskT_*

    Returns DataFrame ready for regression.
    """
    analysis_file = analysis_dir / "H2_PRiskUncertainty_Analysis.parquet"
    if not analysis_file.exists():
        raise FileNotFoundError(
            f"H2_PRiskUncertainty_Analysis.parquet not found in {analysis_dir}"
        )

    validate_input_file(analysis_file, must_exist=True)
    df = pd.read_parquet(analysis_file)

    if dw:
        dw.write(f"  Loaded analysis dataset: {len(df):,} rows\n")
        dw.write(f"    Columns: {len(df.columns)}\n")
        dw.write(f"    Year range: {df['year'].min()} - {df['year'].max()}\n")
        dw.write(f"    Firms: {df['gvkey'].nunique():,}\n")

    # Ensure gvkey is string
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    return df


def prepare_regression_datasets(df, dw=None):
    """
    Prepare regression datasets for primary and robustness specifications.

    Creates:
    1. Primary dataset - all columns for primary specification
    2. Absolute residual - InvestmentResidual_Abs = |InvestmentResidual|
    3. Lagged IVs - t-1 values of interaction and main effects
    4. Subsample 2006-2018 - filtered to year >= 2006

    Returns dict of prepared datasets.
    """
    datasets = {}

    # Primary dataset
    primary_cols = [
        "gvkey",
        "year",
        "ff48_code",
        "InvestmentResidual",
        "PRisk_x_Uncertainty",
        "PRisk_std",
        "Manager_QA_Uncertainty_pct_std",
        "CashFlow",
        "Size",
        "Leverage",
        "TobinQ",
        "SalesGrowth",
    ]

    primary_df = df[primary_cols].copy()

    # Check for missing values in regression variables
    regression_vars = [
        "InvestmentResidual",
        "PRisk_x_Uncertainty",
        "PRisk_std",
        "Manager_QA_Uncertainty_pct_std",
        "CashFlow",
        "Size",
        "Leverage",
        "TobinQ",
        "SalesGrowth",
    ]

    missing_counts = primary_df[regression_vars].isna().sum()
    if missing_counts.sum() > 0:
        if dw:
            dw.write("  Warning: Missing values in regression variables:\n")
            for var, count in missing_counts[missing_counts > 0].items():
                dw.write(f"    {var}: {count:,} missing\n")
        # Drop rows with missing values
        primary_df = primary_df.dropna(subset=regression_vars)

    datasets["primary"] = primary_df

    if dw:
        dw.write(f"  Primary dataset: {len(primary_df):,} observations\n")

    # Absolute residual dataset
    abs_df = primary_df.copy()
    abs_df["InvestmentResidual_Abs"] = abs_df["InvestmentResidual"].abs()
    datasets["abs_residual"] = abs_df

    if dw:
        dw.write(f"  Absolute residual dataset: {len(abs_df):,} observations\n")

    # Lagged IVs dataset
    lagged_df = df[
        ["gvkey", "year", "ff48_code", "InvestmentResidual"]
        + [
            "PRisk_x_Uncertainty",
            "PRisk_std",
            "Manager_QA_Uncertainty_pct_std",
            "CashFlow",
            "Size",
            "Leverage",
            "TobinQ",
            "SalesGrowth",
        ]
    ].copy()

    # Create lagged IVs by firm
    iv_cols = ["PRisk_x_Uncertainty", "PRisk_std", "Manager_QA_Uncertainty_pct_std"]
    lagged_df = lagged_df.sort_values(["gvkey", "year"])

    for col in iv_cols:
        lagged_df[f"{col}_lag"] = lagged_df.groupby("gvkey")[col].shift(1)

    # Drop rows with missing lagged values (first year per firm)
    lagged_df = lagged_df.dropna(subset=[f"{c}_lag" for c in iv_cols])

    datasets["lagged_iv"] = lagged_df

    if dw:
        dw.write(f"  Lagged IV dataset: {len(lagged_df):,} observations\n")

    # Subsample 2006-2018
    subsample_df = primary_df[primary_df["year"] >= 2006].copy()

    if dw:
        dw.write(f"  Subsample 2006-2018: {len(subsample_df):,} observations\n")

    datasets["subsample_2006"] = subsample_df

    return datasets


# ==============================================================================
# Regression Execution
# ==============================================================================


def run_single_regression(
    df, spec_name, spec_config, industry_col="ff48_code", vif_threshold=5.0, dw=None
):
    """
    Run a single regression specification.

    Returns dict with regression results.
    """
    dependent = spec_config["dependent"]
    exog = spec_config["exog"]

    # Apply sample filter if specified
    df_work = df.copy()
    if "sample_filter" in spec_config:
        filter_expr = spec_config["sample_filter"]
        df_work = df_work.query(filter_expr).copy()
        if dw and spec_name == "subsample_2006":
            dw.write(f"    Applied filter: {filter_expr}, N={len(df_work):,}\n")

    # Verify columns exist
    missing_cols = [c for c in [dependent] + exog if c not in df_work.columns]
    if missing_cols:
        raise ValueError(f"Missing columns for {spec_name}: {missing_cols}")

    # Drop rows with missing values
    regression_cols = [dependent] + exog
    before_drop = len(df_work)
    df_work = df_work.dropna(subset=regression_cols)
    after_drop = len(df_work)

    if dw and spec_name == "primary":
        dw.write(f"    Dropped {before_drop - after_drop:,} obs with missing values\n")
        dw.write(f"    Final sample: {after_drop:,} observations\n")

    # Determine fixed effects
    entity_effects = spec_config.get("entity_effects", True)
    time_effects = spec_config.get("time_effects", True)
    industry_effects = spec_config.get("industry_effects", False)
    cluster_cols = spec_config.get("cluster_cols", ["gvkey", "year"])

    # Run regression
    if dw:
        dw.write(f"    Running: {dependent} ~ {', '.join(exog[:3])}... + controls\n")
        dw.write(
            f"      Entity FE: {entity_effects}, Time FE: {time_effects}, Industry FE: {industry_effects}\n"
        )
        dw.write(f"      Clustering: {cluster_cols}\n")

    result = run_panel_ols(
        df=df_work,
        dependent=dependent,
        exog=exog,
        entity_col="gvkey",
        time_col="year",
        industry_col=industry_col,
        entity_effects=entity_effects,
        time_effects=time_effects,
        industry_effects=industry_effects,
        cov_type="clustered",
        cluster_cols=cluster_cols,
        check_collinearity=True,
        vif_threshold=vif_threshold,
    )

    # Extract key results
    coeffs_df = result["coefficients"]
    summary = result["summary"]

    # Get coefficient on interaction term
    interaction_var = "PRisk_x_Uncertainty"
    if interaction_var not in coeffs_df.index:
        # Try lagged version
        interaction_var = "PRisk_x_Uncertainty_lag"

    if interaction_var in coeffs_df.index:
        beta1 = float(coeffs_df.loc[interaction_var, "Coefficient"])
        beta1_se = float(coeffs_df.loc[interaction_var, "Std. Error"])
        beta1_t = float(coeffs_df.loc[interaction_var, "t-stat"])

        # Get p-value
        pvalues = result["model"].pvalues
        p_two = float(pvalues.get(interaction_var, np.nan))

        # One-tailed test: H2: beta1 < 0
        if beta1 < 0:
            p_one = p_two / 2
        else:
            p_one = 1 - p_two / 2

        hypothesis_supported = (beta1 < 0) and (p_one < 0.05)
    else:
        beta1 = beta1_se = beta1_t = p_two = p_one = np.nan
        hypothesis_supported = False

    return {
        "specification": spec_name,
        "description": spec_config.get("description", ""),
        "dependent": dependent,
        "n_obs": int(summary["nobs"]),
        "n_firms": df_work["gvkey"].nunique(),
        "r_squared": float(summary["rsquared"]),
        "r_squared_within": float(summary.get("rsquared_within", np.nan)),
        "f_statistic": float(summary.get("f_statistic", np.nan)),
        "f_pvalue": float(summary.get("f_pvalue", np.nan)),
        "beta1": beta1,
        "beta1_se": beta1_se,
        "beta1_t": beta1_t,
        "p_two_tailed": p_two,
        "p_one_tailed": p_one,
        "hypothesis_supported": hypothesis_supported,
        "coefficients": coeffs_df,
        "pvalues": pvalues,
        "warnings": result.get("warnings", []),
        "interaction_var": interaction_var,
    }


def test_hypothesis(beta1, p_one_tailed, alpha=0.05):
    """
    Test H2: beta1 < 0 (PRisk_x_Uncertainty decreases investment efficiency).

    Returns dict with test results.
    """
    if np.isnan(beta1) or np.isnan(p_one_tailed):
        return {
            "hypothesis": "H2: PRisk_x_Uncertainty -> Decreased Investment Efficiency",
            "prediction": "beta1 < 0",
            "supported": False,
            "p_one_tailed": np.nan,
            "interpretation": "Unable to test - missing coefficient or p-value",
        }

    if beta1 < 0 and p_one_tailed < alpha:
        interpretation = (
            "SUPPORTED: Compound uncertainty from political risk and managerial "
            "speech creates amplified real effects on capital allocation. "
            "Firms facing both high political risk AND high managerial uncertainty "
            "invest less efficiently."
        )
        supported = True
    elif beta1 >= 0:
        interpretation = (
            "NOT SUPPORTED (wrong direction): The coefficient is positive, "
            "suggesting compound uncertainty may increase rather than decrease "
            "investment efficiency. Political and managerial uncertainty may affect "
            "investment through independent channels rather than multiplicatively."
        )
        supported = False
    else:
        interpretation = (
            "NOT SUPPORTED (not significant): The negative coefficient is in the "
            "predicted direction but not statistically significant at the "
            f"{alpha} level. Compound uncertainty does not have a detectable "
            "effect on investment efficiency in this sample."
        )
        supported = False

    return {
        "hypothesis": "H2: PRisk_x_Uncertainty -> Decreased Investment Efficiency",
        "prediction": "beta1 < 0",
        "supported": supported,
        "p_one_tailed": p_one_tailed,
        "interpretation": interpretation,
    }


def run_robustness_checks(datasets, vif_threshold=5.0, dw=None):
    """
    Run all robustness check regressions.

    Returns dict of results.
    """
    robustness_results = {}

    if dw:
        dw.write("\n[4] Running robustness checks...\n")

    # Industry + Year FE (instead of Firm FE)
    if "primary" in datasets:
        if dw:
            dw.write("\n  Robustness 1: Industry + Year FE\n")
        result = run_single_regression(
            datasets["primary"],
            "industry_fe",
            ROBUSTNESS_SPECS["industry_fe"],
            vif_threshold=vif_threshold,
            dw=dw,
        )
        robustness_results["industry_fe"] = result

    # Absolute residual DV
    if "abs_residual" in datasets:
        if dw:
            dw.write("\n  Robustness 2: Absolute Residual DV\n")
        result = run_single_regression(
            datasets["abs_residual"],
            "abs_residual",
            ROBUSTNESS_SPECS["abs_residual"],
            vif_threshold=vif_threshold,
            dw=dw,
        )
        robustness_results["abs_residual"] = result

    # Lagged IVs
    if "lagged_iv" in datasets:
        if dw:
            dw.write("\n  Robustness 3: Lagged IVs (t-1)\n")
        result = run_single_regression(
            datasets["lagged_iv"],
            "lagged_iv",
            ROBUSTNESS_SPECS["lagged_iv"],
            vif_threshold=vif_threshold,
            dw=dw,
        )
        robustness_results["lagged_iv"] = result

    # Subsample 2006-2018
    if "subsample_2006" in datasets:
        if dw:
            dw.write("\n  Robustness 4: Subsample 2006-2018\n")
        result = run_single_regression(
            datasets["subsample_2006"],
            "subsample_2006",
            ROBUSTNESS_SPECS["subsample_2006"],
            vif_threshold=vif_threshold,
            dw=dw,
        )
        robustness_results["subsample_2006"] = result

    return robustness_results


# ==============================================================================
# Output Functions
# ==============================================================================


def save_regression_results(primary_result, robustness_results, output_dir, dw=None):
    """
    Save regression results to parquet file.

    Creates long-format DataFrame with columns:
    - specification, variable, coefficient, std_error, t_stat, p_value, p_one_tailed
    """
    rows = []

    # Add primary result
    for var in primary_result["coefficients"].index:
        row = {
            "specification": "primary",
            "variable": var,
            "coefficient": float(
                primary_result["coefficients"].loc[var, "Coefficient"]
            ),
            "std_error": float(primary_result["coefficients"].loc[var, "Std. Error"]),
            "t_stat": float(primary_result["coefficients"].loc[var, "t-stat"]),
            "p_value": float(primary_result["pvalues"].get(var, np.nan)),
            "n_obs": primary_result["n_obs"],
            "r_squared": primary_result["r_squared"],
        }

        # Add one-tailed p-value for interaction term
        if var == primary_result["interaction_var"]:
            row["p_one_tailed"] = primary_result["p_one_tailed"]
            row["hypothesis_test"] = "H2_beta1"
            row["hypothesis_supported"] = primary_result["hypothesis_supported"]
        else:
            row["p_one_tailed"] = np.nan
            row["hypothesis_test"] = None
            row["hypothesis_supported"] = None

        rows.append(row)

    # Add robustness results
    for spec_name, result in robustness_results.items():
        for var in result["coefficients"].index:
            row = {
                "specification": spec_name,
                "variable": var,
                "coefficient": float(result["coefficients"].loc[var, "Coefficient"]),
                "std_error": float(result["coefficients"].loc[var, "Std. Error"]),
                "t_stat": float(result["coefficients"].loc[var, "t-stat"]),
                "p_value": float(result["pvalues"].get(var, np.nan)),
                "n_obs": result["n_obs"],
                "r_squared": result["r_squared"],
            }

            if var == result["interaction_var"]:
                row["p_one_tailed"] = result["p_one_tailed"]
                row["hypothesis_test"] = "H2_beta1"
                row["hypothesis_supported"] = result["hypothesis_supported"]
            else:
                row["p_one_tailed"] = np.nan
                row["hypothesis_test"] = None
                row["hypothesis_supported"] = None

            rows.append(row)

    results_df = pd.DataFrame(rows)
    output_path = output_dir / "H2_Regression_Results.parquet"
    results_df.to_parquet(output_path, index=False)

    if dw:
        dw.write(
            f"\n  Saved: {output_path.name} ({len(results_df)} coefficient rows)\n"
        )

    return results_df


def save_stats_json(
    primary_result,
    robustness_results,
    hypothesis_test,
    timestamp,
    git_sha,
    execution_time,
    output_dir,
    dw=None,
):
    """Save statistics dictionary to JSON file"""
    stats = {
        "primary_results": {
            "PRisk_x_Uncertainty": {
                "coefficient": primary_result["beta1"],
                "se": primary_result["beta1_se"],
                "t_stat": primary_result["beta1_t"],
                "p_two_tailed": primary_result["p_two_tailed"],
                "p_one_tailed": primary_result["p_one_tailed"],
            },
            "model_stats": {
                "n_obs": primary_result["n_obs"],
                "n_firms": primary_result["n_firms"],
                "r2": primary_result["r_squared"],
                "r2_within": primary_result["r_squared_within"],
                "f_stat": primary_result["f_statistic"],
            },
        },
        "hypothesis_test": hypothesis_test,
        "robustness_results": {},
        "execution_metadata": {
            "timestamp": timestamp,
            "git_sha": git_sha,
            "execution_time_sec": execution_time,
        },
    }

    for spec_name, result in robustness_results.items():
        stats["robustness_results"][spec_name] = {
            "PRisk_x_Uncertainty": {
                "coefficient": result["beta1"],
                "se": result["beta1_se"],
                "t_stat": result["beta1_t"],
                "p_two_tailed": result["p_two_tailed"],
                "p_one_tailed": result["p_one_tailed"],
                "hypothesis_supported": result["hypothesis_supported"],
            },
            "model_stats": {
                "n_obs": result["n_obs"],
                "n_firms": result["n_firms"],
                "r2": result["r_squared"],
                "r2_within": result["r_squared_within"],
            },
            "description": result["description"],
        }

    stats_path = output_dir / "stats.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2, default=str)

    if dw:
        dw.write(f"  Saved: {stats_path.name}\n")

    return stats


def generate_results_markdown(
    primary_result, robustness_results, hypothesis_test, timestamp, output_dir, dw=None
):
    """
    Generate human-readable markdown summary of H2 regression results.
    """
    lines = []
    lines.append("# H2 PRisk x Uncertainty -> Investment Efficiency Results")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Hypothesis section
    lines.append("## Hypothesis")
    lines.append("")
    lines.append(f"**{hypothesis_test['hypothesis']}**")
    lines.append("")
    lines.append(f"**Prediction:** {hypothesis_test['prediction']}")
    lines.append("")
    lines.append(
        f"**Result:** {'SUPPORTED' if hypothesis_test['supported'] else 'NOT SUPPORTED'}"
    )
    lines.append("")

    if not np.isnan(hypothesis_test["p_one_tailed"]):
        lines.append(f"**One-tailed p-value:** {hypothesis_test['p_one_tailed']:.4f}")
    else:
        lines.append("**One-tailed p-value:** N/A")
    lines.append("")

    # Primary results
    lines.append("## Primary Results")
    lines.append("")
    lines.append(
        "Specification: InvestmentResidual ~ PRisk_x_Uncertainty + PRisk_std + Uncertainty_std + Controls + Firm FE + Year FE"
    )
    lines.append(
        "Standard errors: Double-clustered at (firm, year) per Petersen (2009)"
    )
    lines.append("")

    # Coefficient table
    lines.append("### Key Coefficient: PRisk_x_Uncertainty")
    lines.append("")
    beta1 = primary_result["beta1"]
    beta1_se = primary_result["beta1_se"]
    beta1_t = primary_result["beta1_t"]
    p_one = primary_result["p_one_tailed"]

    if not np.isnan(beta1):
        lines.append("| Statistic | Value |")
        lines.append("|-----------|-------|")
        lines.append(f"| Coefficient (beta1) | {beta1:.4f} |")
        lines.append(f"| Std. Error | {beta1_se:.4f} |")
        lines.append(f"| t-stat | {beta1_t:.2f} |")

        if not np.isnan(p_one):
            sig_marker = "**" if p_one < 0.05 else ""
            lines.append(f"| One-tailed p-value | {p_one:.4f} {sig_marker} |")

        lines.append("")
        lines.append("Significance: ** p < 0.05 (one-tailed)")
        lines.append("")
    else:
        lines.append("*Coefficient not available*")
        lines.append("")

    # Model stats
    lines.append("### Model Statistics")
    lines.append("")
    lines.append("| Statistic | Value |")
    lines.append("|-----------|-------|")
    lines.append(f"| N (observations) | {primary_result['n_obs']:,} |")
    lines.append(f"| N (firms) | {primary_result['n_firms']:,} |")
    lines.append(f"| R-squared | {primary_result['r_squared']:.4f} |")
    if not np.isnan(primary_result["r_squared_within"]):
        lines.append(
            f"| R-squared (within) | {primary_result['r_squared_within']:.4f} |"
        )
    if not np.isnan(primary_result["f_statistic"]):
        lines.append(f"| F-statistic | {primary_result['f_statistic']:.2f} |")
    lines.append("")

    # Interpretation
    lines.append("## Interpretation")
    lines.append("")
    lines.append(hypothesis_test["interpretation"])
    lines.append("")

    # Robustness
    lines.append("## Robustness Checks")
    lines.append("")
    lines.append("| Specification | N | R2 | beta1 | SE | p_one_tailed | Supported |")
    lines.append("|---------------|---|----|------|----|-------------|-----------|")

    for _spec_name, result in robustness_results.items():
        n = result["n_obs"]
        r2 = result["r_squared"]
        b1 = result["beta1"]
        se = result["beta1_se"]
        p1 = result["p_one_tailed"]
        supp = "Yes" if result["hypothesis_supported"] else "No"

        b1_str = f"{b1:.4f}" if not np.isnan(b1) else "N/A"
        se_str = f"{se:.4f}" if not np.isnan(se) else "N/A"
        p1_str = f"{p1:.4f}" if not np.isnan(p1) else "N/A"

        lines.append(
            f"| {result['description']} | {n:,} | {r2:.4f} | {b1_str} | {se_str} | {p1_str} | {supp} |"
        )

    lines.append("")
    lines.append("Significance threshold: p < 0.05 (one-tailed)")
    lines.append("")

    # Conclusion
    lines.append("## Conclusion")
    lines.append("")

    # Count supporting specs
    n_supporting = sum(
        1 for r in robustness_results.values() if r["hypothesis_supported"]
    )
    n_total = len(robustness_results) + 1  # +1 for primary

    if hypothesis_test["supported"]:
        lines.append(
            f"H2 is SUPPORTED in the primary specification ({n_supporting}/{n_total - 1} robustness checks also support)."
        )
        lines.append("")
        lines.append(
            "Compound uncertainty from political risk and managerial speech uncertainty"
        )
        lines.append(
            "significantly decreases investment efficiency. Firms facing both high political"
        )
        lines.append(
            "risk AND high managerial uncertainty invest less efficiently than predicted by"
        )
        lines.append("fundamental factors alone.")
    else:
        lines.append(
            f"H2 is NOT SUPPORTED in the primary specification (0/{n_total - 1} robustness checks support)."
        )
        lines.append("")
        lines.append(
            "Compound uncertainty does not have a statistically detectable effect on"
        )
        lines.append(
            "investment efficiency. Political risk and managerial uncertainty may affect"
        )
        lines.append(
            "investment through independent channels rather than multiplicatively."
        )

    lines.append("")

    output_path = output_dir / "H2_RESULTS.md"
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    if dw:
        dw.write(f"  Saved: {output_path.name}\n")

    return output_path


# ==============================================================================
# CLI and Main
# ==============================================================================


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="H2 PRisk x Uncertainty -> Investment Efficiency Regression"
    )
    parser.add_argument(
        "--specifications",
        choices=["primary", "robustness", "all"],
        default="all",
        help="Which specifications to run (default: all)",
    )
    parser.add_argument("--output-dir", type=Path, help="Override output directory")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and setup without running regressions",
    )
    return parser.parse_args()


def main():
    """Main execution function"""
    args = parse_args()

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # Load config
    config = load_config()

    # Setup paths
    paths = setup_paths(config, timestamp)

    # Override output directory if specified
    if args.output_dir:
        paths["output_dir"] = Path(args.output_dir)
        ensure_output_dir(paths["output_dir"])

    # Initialize DualWriter for logging
    dw = DualWriter(paths["log_file"])

    # Script header
    dw.write("=" * 80 + "\n")
    dw.write("STEP 4.10: H2 PRisk x Uncertainty -> Investment Efficiency Regression\n")
    dw.write("=" * 80 + "\n")
    dw.write(f"Timestamp: {timestamp}\n")
    dw.write(f"Git SHA: {get_git_sha()}\n")
    dw.write(f"Config: {config.get('step_id', '4.10_H2_PRiskUncertainty_Investment')}\n")
    dw.write("")

    start_time = time.time()
    start_mem = get_process_memory_mb()

    try:
        # Load analysis dataset
        dw.write("\n[1] Loading analysis dataset from Plan 53-02...\n")
        df = load_analysis_dataset(paths["analysis_dir"], dw)

        if args.dry_run:
            dw.write("\n[Dry run] Validation complete. Exiting.\n")
            dw.write(f"  Analysis dataset: {len(df):,} rows\n")
            dw.write(f"  Output directory: {paths['output_dir']}\n")
            return

        # Prepare regression datasets
        dw.write("\n[2] Preparing regression datasets...\n")
        datasets = prepare_regression_datasets(df, dw)

        # Run primary regression
        dw.write("\n[3] Running primary regression...\n")
        primary_result = run_single_regression(
            datasets["primary"], "primary", PRIMARY_SPEC, vif_threshold=5.0, dw=dw
        )

        # Test hypothesis
        hypothesis_test = test_hypothesis(
            primary_result["beta1"], primary_result["p_one_tailed"], alpha=0.05
        )

        dw.write("\n  Hypothesis Test Results:\n")
        dw.write(f"    H2: {hypothesis_test['hypothesis']}\n")
        dw.write(f"    Prediction: {hypothesis_test['prediction']}\n")
        dw.write(f"    Supported: {hypothesis_test['supported']}\n")
        if not np.isnan(hypothesis_test["p_one_tailed"]):
            dw.write(f"    One-tailed p-value: {hypothesis_test['p_one_tailed']:.4f}\n")
        dw.write(f"    Interpretation: {hypothesis_test['interpretation']}\n")

        # Run robustness checks if requested
        robustness_results = {}
        if args.specifications in ["robustness", "all"]:
            robustness_results = run_robustness_checks(
                datasets, vif_threshold=5.0, dw=dw
            )

        # Calculate execution time
        end_time = time.time()
        execution_time = end_time - start_time

        # Save outputs
        dw.write("\n[5] Saving outputs...\n")
        save_regression_results(
            primary_result, robustness_results, paths["output_dir"], dw
        )

        save_stats_json(
            primary_result,
            robustness_results,
            hypothesis_test,
            timestamp,
            get_git_sha(),
            execution_time,
            paths["output_dir"],
            dw,
        )

        generate_results_markdown(
            primary_result,
            robustness_results,
            hypothesis_test,
            timestamp,
            paths["output_dir"],
            dw,
        )

        # Summary
        end_mem = get_process_memory_mb()

        dw.write("\n" + "=" * 80 + "\n")
        dw.write("EXECUTION SUMMARY\n")
        dw.write("=" * 80 + "\n")
        dw.write(f"  Duration: {execution_time:.2f} seconds\n")
        dw.write(
            f"  Memory (RSS): {start_mem['rss_mb']:.1f} MB -> {end_mem['rss_mb']:.1f} MB\n"
        )
        dw.write(f"  Output directory: {paths['output_dir']}\n")
        dw.write(f"  Log file: {paths['log_file']}\n")
        dw.write("")
        dw.write("  Primary Specification:\n")
        dw.write(f"    N: {primary_result['n_obs']:,}\n")
        dw.write(f"    R2: {primary_result['r_squared']:.4f}\n")
        dw.write(f"    beta1 (PRisk_x_Uncertainty): {primary_result['beta1']:.4f}\n")
        dw.write(f"    One-tailed p-value: {primary_result['p_one_tailed']:.4f}\n")
        dw.write(f"    Hypothesis Supported: {hypothesis_test['supported']}\n")

        if robustness_results:
            n_supporting = sum(
                1 for r in robustness_results.values() if r["hypothesis_supported"]
            )
            dw.write(
                f"\n  Robustness: {n_supporting}/{len(robustness_results)} specs support H2\n"
            )

        dw.write("=" * 80 + "\n")
        dw.write("COMPLETE\n")

    except Exception as e:
        dw.write(f"\nERROR: {e}\n")
        import traceback

        dw.write(traceback.format_exc())
        raise
    finally:
        dw.close()


if __name__ == "__main__":
    main()
