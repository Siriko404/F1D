#!/usr/bin/env python3
"""
==============================================================================
STEP 4.2: H2 Investment Efficiency Regression
==============================================================================
ID: 4.2_H2InvestmentEfficiencyRegression
Description: Panel OLS regressions for H2 (Speech Uncertainty & Investment Efficiency).
             Tests whether vague managers exhibit lower investment efficiency
             (more over/under-investment) and whether leverage moderates this effect.

Model Specification:
    Efficiency_{t+1} = beta0 + beta1*Uncertainty_t + beta2*Leverage_t
                       + beta3*(Uncertainty_t * Leverage_t)
                       + gamma*Controls + Firm FE + Year FE + epsilon

Hypothesis Tests:
    H2a: beta1 < 0 (Higher uncertainty leads to LOWER investment efficiency)
    H2b: beta3 > 0 (Leverage attenuates the negative uncertainty-efficiency relationship)

Inputs:
    - 4_Outputs/3_Financial_V2/latest/H2_InvestmentEfficiency.parquet
      (efficiency_score, roa_residual, controls at firm-year level)
    - 4_Outputs/3_Financial_V2/latest/H1_CashHoldings.parquet
      (leverage variable merged in)
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_*.parquet
      (speech uncertainty measures at call level)

Outputs:
    - 4_Outputs/4_Econometric_V2/4.2_H2InvestmentEfficiencyRegression/{timestamp}/H2_Regression_Results.parquet
      (all regression coefficients, SEs, p-values, diagnostics)
    - 4_Outputs/4_Econometric_V2/4.2_H2InvestmentEfficiencyRegression/{timestamp}/stats.json
      (regression summaries, hypothesis tests, execution metadata)
    - 4_Outputs/4_Econometric_V2/4.2_H2InvestmentEfficiencyRegression/{timestamp}/H2_RESULTS.md
      (human-readable summary of key findings)
    - 3_Logs/4_Econometric_V2/4.2_H2InvestmentEfficiencyRegression/{timestamp}_H2.log
      (execution log with dual-writer output)

Deterministic: true
Dependencies:
    - Requires: Step 3.2_H2Variables
    - Uses: shared.regression_utils, shared.panel_ols, shared.diagnostics, linearmodels

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
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import yaml

# Import shared utilities
from f1d.shared.centering import center_continuous
from f1d.shared.diagnostics import MulticollinearityError, check_multicollinearity
from f1d.shared.observability_utils import (
    DualWriter,
    get_process_memory_mb,
    save_stats as shared_save_stats,  # type: ignore[attr-defined]
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


UNCERTAINTY_MEASURES = [
    "Manager_QA_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Manager_QA_Weak_Modal_pct",
    "CEO_QA_Weak_Modal_pct",
    "Manager_Pres_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
]

CONTROL_VARS = [
    "tobins_q",
    "cf_volatility",
    "industry_capex_intensity",
    "analyst_dispersion",
    "firm_size",
    "roa",
    "fcf",
    "earnings_volatility",
]

DV_VARS = ["efficiency_score", "roa_residual"]

SPECS = {
    "primary": {"entity_effects": True, "time_effects": True, "double_cluster": False},
    "pooled": {"entity_effects": False, "time_effects": False, "double_cluster": False},
    "year_only": {
        "entity_effects": False,
        "time_effects": True,
        "double_cluster": False,
    },
    "double_cluster": {
        "entity_effects": True,
        "time_effects": True,
        "double_cluster": True,
    },
}


# ==============================================================================
# Path Setup
# ==============================================================================


def setup_paths(config, timestamp):
    """Set up all required paths using get_latest_output_dir"""
    root = Path(__file__).parent.parent.parent

    # Resolve H2 variables directory
    h2_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H2_InvestmentEfficiency.parquet",
    )

    # Resolve H1 variables directory (for leverage)
    h1_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H1_CashHoldings.parquet",
    )

    # Resolve speech uncertainty directory
    speech_dir = get_latest_output_dir(
        root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
        required_file="linguistic_variables_2002.parquet",  # At least one year must exist
    )

    paths = {
        "root": root,
        "h2_dir": h2_dir,
        "h1_dir": h1_dir,
        "speech_dir": speech_dir,
    }

    # Output directory - organize by script name
    output_base = (
        root / "4_Outputs" / "4_Econometric_V2" / "4.2_H2InvestmentEfficiencyRegression"
    )
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory - organize by script name
    log_base = (
        root / "3_Logs" / "4_Econometric_V2" / "4.2_H2InvestmentEfficiencyRegression"
    )
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H2.log"

    return paths


# ==============================================================================
# Data Loading
# ==============================================================================


def load_h2_variables(h2_dir, dw=None):
    """
    Load H2 Investment Efficiency variables.

    Expects H2_InvestmentEfficiency.parquet with columns:
    - gvkey, fiscal_year
    - DVs: efficiency_score, roa_residual
    - Controls: tobins_q, cf_volatility, industry_capex_intensity, analyst_dispersion,
                firm_size, roa, fcf, earnings_volatility

    Note: leverage is NOT in H2 data - must be merged from H1 data.
    """
    h2_file = h2_dir / "H2_InvestmentEfficiency.parquet"
    if not h2_file.exists():
        raise FileNotFoundError(
            f"H2_InvestmentEfficiency.parquet not found in {h2_dir}"
        )

    validate_input_file(h2_file, must_exist=True)
    df = pd.read_parquet(h2_file)

    if dw:
        dw.write(f"  Loaded H2 variables: {len(df):,} rows\n")
        dw.write(f"    Columns: {df.columns.tolist()}\n")

    # Ensure gvkey is string and zero-padded
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    return df


def load_h1_leverage(h1_dir, dw=None):
    """
    Load leverage from H1 Cash Holdings data.

    H1_CashHoldings.parquet has the leverage variable needed for H2 regressions.
    """
    h1_file = h1_dir / "H1_CashHoldings.parquet"
    if not h1_file.exists():
        raise FileNotFoundError(f"H1_CashHoldings.parquet not found in {h1_dir}")

    validate_input_file(h1_file, must_exist=True)
    df = pd.read_parquet(h1_file)

    if dw:
        dw.write(f"  Loaded H1 leverage: {len(df):,} rows\n")

    # Ensure gvkey is string and zero-padded
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    # Select only gvkey, fiscal_year, leverage
    df = df[["gvkey", "fiscal_year", "leverage"]].copy()  # type: ignore[assignment]

    return df


def load_speech_uncertainty(speech_dir, uncertainty_cols, dw=None):
    """
    Load all linguistic_variables_*.parquet files and concatenate.

    Returns DataFrame with columns:
    - file_name, gvkey, start_date
    - uncertainty_cols (6 measures)
    """
    speech_files = sorted(speech_dir.glob("linguistic_variables_*.parquet"))

    if not speech_files:
        raise FileNotFoundError(f"No linguistic_variables files found in {speech_dir}")

    dfs = []
    total_rows = 0
    for f in speech_files:
        df = pd.read_parquet(f)
        dfs.append(df)
        total_rows += len(df)

    if dw:
        dw.write(
            f"  Loaded speech uncertainty: {total_rows:,} calls across {len(speech_files)} years\n"
        )

    combined = pd.concat(dfs, ignore_index=True)

    # Select only needed columns
    required_cols = ["file_name", "gvkey", "start_date"] + uncertainty_cols
    available_cols = [c for c in required_cols if c in combined.columns]
    missing_cols = set(required_cols) - set(available_cols)

    if missing_cols:
        raise ValueError(f"Missing columns in speech data: {missing_cols}")

    combined = combined[available_cols].copy()

    # Ensure gvkey is string and zero-padded
    combined["gvkey"] = combined["gvkey"].astype(str).str.zfill(6)
    combined["start_date"] = pd.to_datetime(combined["start_date"])

    return combined


# ==============================================================================
# Aggregation
# ==============================================================================


def aggregate_speech_to_firmyear(speech_df, uncertainty_cols, dw=None):
    """
    Aggregate call-level speech data to firm-year level.

    Extracts fiscal_year from start_date and computes mean of uncertainty
    measures within each firm-year. Counts number of calls per firm-year.
    """
    df = speech_df.copy()

    # Extract year from start_date as fiscal_year
    df["fiscal_year"] = df["start_date"].dt.year

    # Group by gvkey and fiscal_year
    group_cols = ["gvkey", "fiscal_year"]

    # Compute mean of uncertainty columns, count of file_name
    agg_dict = {col: "mean" for col in uncertainty_cols}
    agg_dict["file_name"] = "count"

    agg_df = df.groupby(group_cols, as_index=False).agg(agg_dict)
    agg_df = agg_df.rename(columns={"file_name": "n_calls"})

    if dw:
        mean_calls = agg_df["n_calls"].mean()
        dw.write(
            f"  Aggregated to {len(agg_df):,} firm-years, mean {mean_calls:.2f} calls per firm-year\n"
        )

    return agg_df


# ==============================================================================
# Data Preparation
# ==============================================================================


def prepare_regression_data(
    h2_df, h1_leverage_df, speech_agg_df, uncertainty_cols, dv_var, dw=None
):
    """
    Merge H2 variables with speech data and leverage, create lead dependent variable.

    Steps:
    1. Merge H2 with H1 leverage on gvkey and fiscal_year (inner join)
    2. Merge with speech data on gvkey and fiscal_year (inner join)
    3. Sort by gvkey and fiscal_year
    4. Create lead dependent variable via groupby shift(-1)
    5. Drop rows where lead is NaN (last year per firm)

    Args:
        h2_df: H2 variables with DVs and controls
        h1_leverage_df: H1 data with leverage
        speech_agg_df: Aggregated speech uncertainty by firm-year
        uncertainty_cols: List of uncertainty measure columns
        dv_var: Dependent variable name (efficiency_score or roa_residual)
    """
    # Merge H2 with H1 leverage
    merge_cols = ["gvkey", "fiscal_year"]
    reg_df = h2_df.merge(h1_leverage_df, on=merge_cols, how="inner")

    if dw:
        dw.write(f"  After H1 leverage merge: {len(reg_df):,} obs\n")

    # Merge with speech data
    reg_df = reg_df.merge(speech_agg_df, on=merge_cols, how="inner")

    if dw:
        merge_rate = len(reg_df) / len(h2_df) * 100
        dw.write(
            f"  After speech merge: {len(reg_df):,} obs ({merge_rate:.1f}% of H2 data)\n"
        )

    # Select columns needed for regression
    core_cols = (
        ["gvkey", "fiscal_year", "leverage", dv_var]
        + CONTROL_VARS
        + uncertainty_cols
        + ["n_calls"]
    )
    reg_df = reg_df[core_cols].copy()

    # Sort and create lead dependent variable
    reg_df = reg_df.sort_values(["gvkey", "fiscal_year"])
    dv_lead = f"{dv_var}_lead"
    reg_df[dv_lead] = reg_df.groupby("gvkey")[dv_var].shift(-1)

    # Drop NaN in lead (last year per firm)
    before_drop = len(reg_df)
    reg_df = reg_df.dropna(subset=[dv_lead])
    after_drop = len(reg_df)
    dropped = before_drop - after_drop

    if dw:
        dw.write(
            f"  Lead variable created, dropped {dropped:,} obs (last year per firm)\n"
        )
        dw.write(f"  Final regression sample ({dv_var}): {len(reg_df):,} obs\n")

    return reg_df


# ==============================================================================
# Single Regression
# ==============================================================================


def run_single_h2_regression(
    df,
    uncertainty_var,
    dv_var,
    spec_name,
    spec_config,
    control_vars,
    vif_threshold=5.0,
    dw=None,
):
    """
    Run a single H2 regression with specified uncertainty measure, DV, and spec.

    Model:
        efficiency_lead ~ uncertainty_c + leverage_c + uncertainty_c:leverage_c
                         + controls

    Steps:
    1. Center uncertainty and leverage variables
    2. Create interaction term
    3. Build exog list
    4. Pre-flight VIF check on controls only (STRICT mode)
    5. Run panel OLS with specified FE config
    6. Extract results and perform one-tailed hypothesis tests

    Hypothesis tests:
    - H2a: beta1 < 0 (uncertainty coefficient - negative effect)
      p_one_tail = p_two_tail / 2 if beta < 0, else 1 - p_two_tail/2
    - H2b: beta3 > 0 (interaction coefficient - positive moderation)
      p_one_tail = p_two_tail / 2 if beta > 0, else 1 - p_two_tail/2
    """
    df_work = df.copy()

    # Center variables
    vars_to_center = [uncertainty_var, "leverage"]
    df_work, means = center_continuous(df_work, vars_to_center, suffix="_c")

    # Create interaction term
    uncertainty_c = f"{uncertainty_var}_c"
    leverage_c = "leverage_c"
    interaction_col = f"{uncertainty_var}_x_leverage"
    df_work[interaction_col] = df_work[uncertainty_c] * df_work[leverage_c]

    # Build exog list
    exog = [uncertainty_c, leverage_c, interaction_col] + control_vars

    # Pre-flight VIF check on control variables only
    controls_only = [c for c in control_vars if c in df_work.columns]
    try:
        check_multicollinearity(
            df_work,
            controls_only,
            vif_threshold=vif_threshold,
            condition_threshold=1000.0,
            fail_on_violation=True,
        )
    except MulticollinearityError as e:
        if dw:
            dw.write(f"  VIF check failed: {e}\n")
        raise

    # Run panel OLS
    cluster_cols = (
        ["gvkey", "fiscal_year"] if spec_config["double_cluster"] else ["gvkey"]
    )

    dv_lead = f"{dv_var}_lead"
    result = run_panel_ols(
        df=df_work,
        dependent=dv_lead,
        exog=exog,
        entity_col="gvkey",
        time_col="fiscal_year",
        entity_effects=spec_config["entity_effects"],
        time_effects=spec_config["time_effects"],
        cov_type="clustered",
        cluster_cols=cluster_cols,
        check_collinearity=False,
        vif_threshold=vif_threshold,
    )

    # Extract results
    coeffs_df = result["coefficients"]
    summary = result["summary"]

    # Get coefficients of interest
    beta1_name = uncertainty_c
    beta3_name = interaction_col

    beta1 = (
        coeffs_df.loc[beta1_name, "Coefficient"]
        if beta1_name in coeffs_df.index
        else np.nan
    )
    beta3 = (
        coeffs_df.loc[beta3_name, "Coefficient"]
        if beta3_name in coeffs_df.index
        else np.nan
    )

    # Get p-values
    pvalues = result["model"].pvalues
    p1_two = pvalues.get(beta1_name, np.nan)
    p3_two = pvalues.get(beta3_name, np.nan)

    # One-tailed hypothesis tests
    # H2a: beta1 < 0 (negative coefficient supports hypothesis - vagueness reduces efficiency)
    if not np.isnan(p1_two) and not np.isnan(beta1):
        if beta1 < 0:
            p1_one = p1_two / 2
        else:
            p1_one = 1 - p1_two / 2
    else:
        p1_one = np.nan

    # H2b: beta3 > 0 (positive coefficient supports hypothesis - leverage attenuates)
    if not np.isnan(p3_two) and not np.isnan(beta3):
        if beta3 > 0:
            p3_one = p3_two / 2
        else:
            p3_one = 1 - p3_two / 2
    else:
        p3_one = np.nan

    # Hypothesis test outcomes
    h2a_supported = (not np.isnan(p1_one)) and (p1_one < 0.05) and (beta1 < 0)
    h2b_supported = (not np.isnan(p3_one)) and (p3_one < 0.05) and (beta3 > 0)

    return {
        "dv_var": dv_var,
        "spec": spec_name,
        "uncertainty_var": uncertainty_var,
        "n_obs": summary["nobs"],
        "r_squared": summary["rsquared"],
        "r_squared_within": summary.get("rsquared_within", None),
        "f_stat": summary.get("f_statistic", None),
        "f_pvalue": summary.get("f_pvalue", None),
        "coefficients": coeffs_df.to_dict("index"),
        "pvalues": pvalues.to_dict(),
        "beta1": beta1,
        "beta1_se": coeffs_df.loc[beta1_name, "Std. Error"]
        if beta1_name in coeffs_df.index
        else np.nan,
        "beta1_t": coeffs_df.loc[beta1_name, "t-stat"]
        if beta1_name in coeffs_df.index
        else np.nan,
        "beta1_p_two": p1_two,
        "beta1_p_one": p1_one,
        "beta1_signif": h2a_supported,
        "beta2": coeffs_df.loc[leverage_c, "Coefficient"]
        if leverage_c in coeffs_df.index
        else np.nan,
        "beta2_se": coeffs_df.loc[leverage_c, "Std. Error"]
        if leverage_c in coeffs_df.index
        else np.nan,
        "beta3": beta3,
        "beta3_se": coeffs_df.loc[beta3_name, "Std. Error"]
        if beta3_name in coeffs_df.index
        else np.nan,
        "beta3_t": coeffs_df.loc[beta3_name, "t-stat"]
        if beta3_name in coeffs_df.index
        else np.nan,
        "beta3_p_two": p3_two,
        "beta3_p_one": p3_one,
        "beta3_signif": h2b_supported,
        "centering_means": means,
        "warnings": result.get("warnings", []),
    }


# ==============================================================================
# Main Regression Loop
# ==============================================================================


def run_all_h2_regressions(
    reg_dfs,
    uncertainty_measures,
    dv_vars,
    specs,
    control_vars,
    vif_threshold=5.0,
    dw=None,
):
    """
    Run all H2 regressions: 2 DVs x 6 uncertainty measures x 4 specifications = 48 total.

    Args:
        reg_dfs: Dict mapping dv_var -> prepared regression DataFrame
        uncertainty_measures: List of 6 uncertainty measures
        dv_vars: List of 2 DVs
        specs: Dict of 4 specifications
        control_vars: List of control variables

    Returns list of regression result dictionaries.
    """
    results = []

    for dv_var in dv_vars:
        reg_df = reg_dfs[dv_var]
        for uncertainty_var in uncertainty_measures:
            for spec_name, spec_config in specs.items():
                if dw:
                    dw.write(f"\nRunning: {dv_var} x {uncertainty_var} x {spec_name}\n")

                result = run_single_h2_regression(
                    reg_df,
                    uncertainty_var,
                    dv_var,
                    spec_name,
                    spec_config,
                    control_vars,
                    vif_threshold,
                    dw,
                )

                results.append(result)

                if dw:
                    dw.write(
                        f"  N={result['n_obs']}, R2={result['r_squared']:.4f}, "
                        f"beta1={result['beta1']:.4f} (p1={result['beta1_p_one']:.4f}), "
                        f"beta3={result['beta3']:.4f} (p3={result['beta3_p_one']:.4f})\n"
                    )

    return results


# ==============================================================================
# Output Functions
# ==============================================================================


def save_regression_results(results, output_dir, dw=None):
    """
    Save regression results to parquet file.

    Creates long-format DataFrame with columns:
    - dv_name, spec, uncertainty_var, variable, coefficient, se, t_stat, p_value
    - n_obs, r_squared, r_squared_within, f_stat, f_pvalue
    - hypothesis_test (for beta1 and beta3)
    """
    rows = []

    for r in results:
        base_info = {
            "dv_name": r["dv_var"],
            "spec": r["spec"],
            "uncertainty_var": r["uncertainty_var"],
            "n_obs": r["n_obs"],
            "r_squared": r["r_squared"],
            "r_squared_within": r["r_squared_within"],
            "f_stat": r["f_stat"],
            "f_pvalue": r["f_pvalue"],
        }

        # Add each coefficient
        for var_name, coeff_dict in r["coefficients"].items():
            row = base_info.copy()
            row["variable"] = var_name
            row["coefficient"] = coeff_dict["Coefficient"]
            row["se"] = coeff_dict["Std. Error"]
            row["t_stat"] = coeff_dict["t-stat"]
            row["p_value"] = r["pvalues"].get(var_name, np.nan)

            # Mark hypothesis test variables
            if var_name.endswith("_c") and "_x_leverage" not in var_name:
                # This is an uncertainty main effect (beta1 equivalent)
                row["hypothesis_test"] = "H2a_beta1"
                row["p_value_one_tail"] = r["beta1_p_one"]
                row["hypothesis_supported"] = r["beta1_signif"]
            elif f"{r['uncertainty_var']}_x_leverage" in var_name:
                # This is the interaction (beta3)
                row["hypothesis_test"] = "H2b_beta3"
                row["p_value_one_tail"] = r["beta3_p_one"]
                row["hypothesis_supported"] = r["beta3_signif"]
            else:
                row["hypothesis_test"] = None
                row["p_value_one_tail"] = np.nan
                row["hypothesis_supported"] = None

            rows.append(row)

    results_df = pd.DataFrame(rows)
    output_path = output_dir / "H2_Regression_Results.parquet"
    results_df.to_parquet(output_path, index=False)

    if dw:
        dw.write(f"\nSaved: {output_path.name} ({len(results_df)} rows)\n")

    return results_df


def generate_results_markdown(results, output_dir, dw=None):
    """
    Generate human-readable markdown summary of H2 regression results.
    """
    lines = []
    lines.append("# H2 Investment Efficiency Regression Results")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Hypothesis")
    lines.append("")
    lines.append(
        "- **H2a:** Higher speech uncertainty leads to LOWER investment efficiency (beta1 < 0)"
    )
    lines.append(
        "- **H2b:** Leverage attenuates the negative uncertainty-efficiency relationship (beta3 > 0)"
    )
    lines.append("")

    # Summary table: Primary specification
    lines.append("## Primary Specification Results")
    lines.append("")
    lines.append("Firm + Year FE, clustered SE at firm level")
    lines.append("")
    lines.append("### Primary DV: efficiency_score")
    lines.append("")
    lines.append(
        "| Uncertainty Measure | N | R2 | beta1 (SE) | p1 | beta3 (SE) | p3 | H2a | H2b |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")

    for r in results:
        if r["spec"] == "primary" and r["dv_var"] == "efficiency_score":
            uncertainty = r["uncertainty_var"]
            n = r["n_obs"]
            r2 = r["r_squared"]
            beta1 = r["beta1"]
            beta1_se = r["beta1_se"]
            p1 = r["beta1_p_one"]
            beta3 = r["beta3"]
            beta3_se = r["beta3_se"]
            p3 = r["beta3_p_one"]
            h2a = "Yes" if r["beta1_signif"] else "No"
            h2b = "Yes" if r["beta3_signif"] else "No"

            lines.append(
                f"| {uncertainty} | {n:,} | {r2:.4f} | "
                f"{beta1:.4f} ({beta1_se:.4f}) | {p1:.4f} | "
                f"{beta3:.4f} ({beta3_se:.4f}) | {p3:.4f} | {h2a} | {h2b} |"
            )

    lines.append("")
    lines.append("### Alternative DV: roa_residual")
    lines.append("")
    lines.append(
        "| Uncertainty Measure | N | R2 | beta1 (SE) | p1 | beta3 (SE) | p3 | H2a | H2b |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")

    for r in results:
        if r["spec"] == "primary" and r["dv_var"] == "roa_residual":
            uncertainty = r["uncertainty_var"]
            n = r["n_obs"]
            r2 = r["r_squared"]
            beta1 = r["beta1"]
            beta1_se = r["beta1_se"]
            p1 = r["beta1_p_one"]
            beta3 = r["beta3"]
            beta3_se = r["beta3_se"]
            p3 = r["beta3_p_one"]
            h2a = "Yes" if r["beta1_signif"] else "No"
            h2b = "Yes" if r["beta3_signif"] else "No"

            lines.append(
                f"| {uncertainty} | {n:,} | {r2:.4f} | "
                f"{beta1:.4f} ({beta1_se:.4f}) | {p1:.4f} | "
                f"{beta3:.4f} ({beta3_se:.4f}) | {p3:.4f} | {h2a} | {h2b} |"
            )

    lines.append("")
    lines.append("*Significance: p < 0.05 (one-tailed)")
    lines.append("")

    # Hypothesis test outcomes summary
    lines.append("## Hypothesis Test Outcomes")
    lines.append("")

    # Count significant results by DV
    for dv in ["efficiency_score", "roa_residual"]:
        h2a_count = sum(
            1
            for r in results
            if r["spec"] == "primary" and r["dv_var"] == dv and r["beta1_signif"]
        )
        h2b_count = sum(
            1
            for r in results
            if r["spec"] == "primary" and r["dv_var"] == dv and r["beta3_signif"]
        )

        lines.append(f"**Primary Specification ({dv}):**")
        lines.append(f"- H2a (beta1 < 0): {h2a_count}/6 measures significant")
        lines.append(f"- H2b (beta3 > 0): {h2b_count}/6 measures significant")
        lines.append("")

    # List significant measures
    for dv in ["efficiency_score", "roa_residual"]:
        h2a_measures = [
            r["uncertainty_var"]
            for r in results
            if r["spec"] == "primary" and r["dv_var"] == dv and r["beta1_signif"]
        ]
        h2b_measures = [
            r["uncertainty_var"]
            for r in results
            if r["spec"] == "primary" and r["dv_var"] == dv and r["beta3_signif"]
        ]

        if h2a_measures:
            lines.append(
                f"**Supporting H2a for {dv} (beta1 < 0):** {', '.join(h2a_measures)}"
            )
        else:
            lines.append(f"**No measures support H2a for {dv}**")

        if h2b_measures:
            lines.append(
                f"**Supporting H2b for {dv} (beta3 > 0):** {', '.join(h2b_measures)}"
            )
        else:
            lines.append(f"**No measures support H2b for {dv}**")

        lines.append("")

    # Key findings
    lines.append("## Key Findings")
    lines.append("")

    # Find strongest effects for each DV
    for dv in ["efficiency_score", "roa_residual"]:
        lines.append(f"### {dv}")
        lines.append("")

        primary_results = [
            r for r in results if r["spec"] == "primary" and r["dv_var"] == dv
        ]

        if primary_results:
            # Sort by beta1 p-value
            sorted_by_h2a = sorted(
                primary_results,
                key=lambda x: x["beta1_p_one"] if not np.isnan(x["beta1_p_one"]) else 1,
            )
            top_h2a = [r for r in sorted_by_h2a if r["beta1_signif"]]

            if top_h2a:
                lines.append("**Strongest support for H2a:**")
                for r in top_h2a[:3]:
                    lines.append(
                        f"- {r['uncertainty_var']}: beta1={r['beta1']:.4f}, p={r['beta1_p_one']:.4f}"
                    )
            else:
                lines.append("**No significant support for H2a**")

            lines.append("")

            # Sort by beta3 p-value
            sorted_by_h2b = sorted(
                primary_results,
                key=lambda x: x["beta3_p_one"] if not np.isnan(x["beta3_p_one"]) else 1,
            )
            top_h2b = [r for r in sorted_by_h2b if r["beta3_signif"]]

            if top_h2b:
                lines.append("**Strongest support for H2b:**")
                for r in top_h2b[:3]:
                    lines.append(
                        f"- {r['uncertainty_var']}: beta3={r['beta3']:.4f}, p={r['beta3_p_one']:.4f}"
                    )
            else:
                lines.append("**No significant support for H2b**")

        lines.append("")

    # Specification comparison
    lines.append("## Specification Comparison")
    lines.append("")
    lines.append("| Spec | Entity FE | Time FE | Cluster |")
    lines.append("|---|---|---|---|")
    lines.append("| primary | Yes | Yes | firm |")
    lines.append("| pooled | No | No | firm |")
    lines.append("| year_only | No | Yes | firm |")
    lines.append("| double_cluster | Yes | Yes | firm+year |")
    lines.append("")

    output_path = output_dir / "H2_RESULTS.md"
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    if dw:
        dw.write(f"Saved: {output_path.name}\n")

    return output_path


def save_stats(stats, output_dir, dw=None):
    """Save statistics dictionary to JSON file"""
    stats_path = output_dir / "stats.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2, default=str)

    if dw:
        dw.write(f"Saved: {stats_path.name}\n")

    return stats_path


# ==============================================================================
# CLI and Main
# ==============================================================================


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="H2 Investment Efficiency Regression - Panel OLS with Uncertainty x Leverage interaction"
    )
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

    # Initialize DualWriter for logging
    dw = DualWriter(paths["log_file"])

    # Script header
    dw.write("=" * 80 + "\n")
    dw.write("STEP 4.2: H2 Investment Efficiency Regression\n")
    dw.write("=" * 80 + "\n")
    dw.write(f"Timestamp: {timestamp}\n")
    dw.write(f"Git SHA: {get_git_sha()}\n")
    dw.write(
        f"Config: {config.get('step_id', '4.2_H2InvestmentEfficiencyRegression')}\n"
    )
    dw.write("")

    # Stats tracking
    stats: Dict[str, Any] = {
        "step_id": "4.2_H2InvestmentEfficiencyRegression",
        "timestamp": timestamp,
        "git_sha": get_git_sha(),
        "input": {},
        "processing": {},
        "output": {},
        "regressions": [],
        "timing": {},
        "memory": {},
    }

    start_time = time.time()
    start_mem = get_process_memory_mb()

    try:
        # Load H2 variables
        dw.write("\n[1] Loading H2 variables...\n")
        h2_df = load_h2_variables(paths["h2_dir"], dw)

        stats["input"]["h2_variables"] = {
            "rows": int(len(h2_df)),
            "source": str(paths["h2_dir"]),
        }

        # Load H1 leverage
        dw.write("\n[2] Loading H1 leverage...\n")
        h1_leverage_df = load_h1_leverage(paths["h1_dir"], dw)

        stats["input"]["h1_leverage"] = {
            "rows": int(len(h1_leverage_df)),
            "source": str(paths["h1_dir"]),
        }

        # Load speech uncertainty
        dw.write("\n[3] Loading speech uncertainty data...\n")
        speech_df = load_speech_uncertainty(
            paths["speech_dir"], UNCERTAINTY_MEASURES, dw
        )

        stats["input"]["speech_uncertainty"] = {
            "calls": int(len(speech_df)),
            "years": int(speech_df["start_date"].dt.year.nunique()),
            "source": str(paths["speech_dir"]),
        }

        if args.dry_run:
            dw.write("\n[Dry run] Validation complete. Exiting.\n")
            return

        # Aggregate speech to firm-year
        dw.write("\n[4] Aggregating speech data to firm-year level...\n")
        speech_agg = aggregate_speech_to_firmyear(speech_df, UNCERTAINTY_MEASURES, dw)

        stats["processing"]["aggregation"] = {
            "firm_years": int(len(speech_agg)),
        }

        # Prepare regression data for each DV
        dw.write("\n[5] Preparing regression data for each DV...\n")
        reg_dfs = {}
        for dv_var in DV_VARS:
            reg_dfs[dv_var] = prepare_regression_data(
                h2_df, h1_leverage_df, speech_agg, UNCERTAINTY_MEASURES, dv_var, dw
            )

        stats["processing"]["regression_prep"] = {
            "dvs": DV_VARS,
            "efficiency_sample": int(len(reg_dfs["efficiency_score"])),
            "roa_residual_sample": int(len(reg_dfs["roa_residual"])),
        }

        # Run all regressions
        dw.write("\n[6] Running H2 regressions...\n")
        n_regressions = len(DV_VARS) * len(UNCERTAINTY_MEASURES) * len(SPECS)
        dw.write(
            f"  {len(DV_VARS)} DVs x {len(UNCERTAINTY_MEASURES)} uncertainty measures x {len(SPECS)} specifications = "
            f"{n_regressions} regressions\n"
        )

        results = run_all_h2_regressions(
            reg_dfs,
            UNCERTAINTY_MEASURES,
            DV_VARS,
            SPECS,
            CONTROL_VARS,
            vif_threshold=5.0,
            dw=dw,
        )

        stats["regressions"] = [
            {
                "dv_var": r["dv_var"],
                "spec": r["spec"],
                "uncertainty_var": r["uncertainty_var"],
                "n_obs": r["n_obs"],
                "r_squared": r["r_squared"],
                "beta1": r["beta1"],
                "beta1_p_one": r["beta1_p_one"],
                "beta1_signif": r["beta1_signif"],
                "beta3": r["beta3"],
                "beta3_p_one": r["beta3_p_one"],
                "beta3_signif": r["beta3_signif"],
            }
            for r in results
        ]

        # Save outputs
        dw.write("\n[7] Saving outputs...\n")
        results_df = save_regression_results(results, paths["output_dir"], dw)
        generate_results_markdown(results, paths["output_dir"], dw)

        # Create hypothesis test summary for stats.json
        h2a_counts = {}
        h2b_counts = {}
        for dv in DV_VARS:
            h2a_counts[dv] = sum(
                1
                for r in results
                if r["spec"] == "primary" and r["dv_var"] == dv and r["beta1_signif"]
            )
            h2b_counts[dv] = sum(
                1
                for r in results
                if r["spec"] == "primary" and r["dv_var"] == dv and r["beta3_signif"]
            )

        stats["output"]["regression_results"] = {
            "file": "H2_Regression_Results.parquet",
            "rows": int(len(results_df)),
            "regressions": len(results),
        }
        stats["output"]["hypothesis_tests"] = {
            "H2a": h2a_counts,
            "H2b": h2b_counts,
            "description": "H2a: beta1 < 0 (vagueness reduces efficiency), H2b: beta3 > 0 (leverage moderates)",
        }

        # Final stats
        end_time = time.time()
        end_mem = get_process_memory_mb()

        stats["timing"]["duration_seconds"] = end_time - start_time
        stats["memory"]["rss_mb_start"] = start_mem["rss_mb"]
        stats["memory"]["rss_mb_end"] = end_mem["rss_mb"]

        save_stats(stats, paths["output_dir"], dw)

        # Summary
        dw.write("\n" + "=" * 80 + "\n")
        dw.write("EXECUTION SUMMARY\n")
        dw.write("=" * 80 + "\n")
        dw.write(f"  Duration: {stats['timing']['duration_seconds']:.2f} seconds\n")
        dw.write(f"  Regressions: {len(results)}\n")
        dw.write(f"  Output directory: {paths['output_dir']}\n")

        for dv in DV_VARS:
            dw.write(
                f"\n  Primary spec ({dv}) - H2a (beta1 < 0): {h2a_counts[dv]}/6 significant\n"
            )
            dw.write(
                f"  Primary spec ({dv}) - H2b (beta3 > 0): {h2b_counts[dv]}/6 significant\n"
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
