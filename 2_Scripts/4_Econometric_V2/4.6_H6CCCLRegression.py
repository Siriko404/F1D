#!/usr/bin/env python3
"""
==============================================================================
STEP 4.6: H6 CCCL Speech Uncertainty Regression
==============================================================================
ID: 4.6_H6CCCLRegression
Description: Panel OLS regressions for H6 (SEC Scrutiny Effects on Speech
             Uncertainty). Tests whether CCCL exposure (SEC scrutiny via
             comment letter intensity) reduces managerial speech uncertainty.

Model Specification (Primary - H6-A):
    Uncertainty_{i,t} = beta0 + beta1*CCCL_{i,t-1} + gamma*Controls_{i,t}
                      + Firm_FE + Year_FE + epsilon_{i,t}

Hypothesis Tests:
    H6-A: beta1 < 0 (CCCL exposure reduces speech uncertainty - PRIMARY)
    H6-B: |beta1_QA| > |beta1_Pres| (stronger effect in spontaneous Q&A)
    H6-C: beta1 < 0 for Uncertainty_Gap (CCCL reduces Q&A-Pres gap)

Identification:
    - FDR Correction: Benjamini-Hochberg across 6 uncertainty measures
    - Pre-trends: Test CCCL_{t-2}, CCCL_{t-1} leads (should be insignificant)
    - Primary Instrument: shift_intensity_mkvalt_ff48_lag

Inputs:
    - 4_Outputs/3_Financial_V2/3.6_H6Variables/latest/H6_CCCL_Speech.parquet
      (CCCL instrument variants, lagged exposure, speech uncertainty measures)

Outputs:
    - 4_Outputs/4_Econometric_V2/4.6_H6CCCLRegression/{timestamp}/H6_Regression_Results.parquet
    - 4_Outputs/4_Econometric_V2/4.6_H6CCCLRegression/{timestamp}/H6_RESULTS.md
    - 4_Outputs/4_Econometric_V2/4.6_H6CCCLRegression/{timestamp}/stats.json
    - 3_Logs/4_Econometric_V2/4.6_H6CCCLRegression/{timestamp}_H6.log

Deterministic: true
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
from shared.diagnostics import check_multicollinearity
from shared.observability_utils import (
    DualWriter,
    get_process_memory_mb,
    save_stats,
)
from shared.panel_ols import run_panel_ols
from shared.path_utils import (
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


# Uncertainty measures for H6 testing
UNCERTAINTY_MEASURES = [
    "Manager_QA_Uncertainty_pct",  # PRIMARY - Manager spontaneous uncertainty
    "Manager_QA_Weak_Modal_pct",  # Manager hedging in Q&A
    "Manager_Pres_Uncertainty_pct",  # Manager prepared uncertainty
    "CEO_QA_Uncertainty_pct",  # CEO spontaneous uncertainty
    "CEO_QA_Weak_Modal_pct",  # CEO hedging in Q&A
    "CEO_Pres_Uncertainty_pct",  # CEO prepared uncertainty
]

# CCCL instrument variants (for robustness)
CCCL_VARIANTS = [
    "shift_intensity_mkvalt_ff48_lag",  # PRIMARY - FF48 x market value
    "shift_intensity_sale_ff48_lag",  # FF48 x sales
    "shift_intensity_mkvalt_ff12_lag",  # FF12 x market value
    "shift_intensity_sale_ff12_lag",  # FF12 x sales
    "shift_intensity_mkvalt_sic2_lag",  # SIC2 x market value
    "shift_intensity_sale_sic2_lag",  # SIC2 x sales
]

# Specification variants
SPECS = {
    "primary": {"entity_effects": True, "time_effects": True, "cluster_cols": None},
    "firm_only": {"entity_effects": True, "time_effects": False, "cluster_cols": None},
    "pooled": {"entity_effects": False, "time_effects": False, "cluster_cols": None},
    "double_cluster": {
        "entity_effects": True,
        "time_effects": True,
        "cluster_cols": ["gvkey", "fiscal_year"],
    },
}

# ==============================================================================
# Path Setup
# ==============================================================================


def setup_paths(config, timestamp):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    # Resolve H6 variables directory
    h6_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2" / "3.6_H6Variables",
        required_file="H6_CCCL_Speech.parquet",
    )

    paths = {
        "root": root,
        "h6_dir": h6_dir,
    }

    # Output directory
    output_base = root / "4_Outputs" / "4_Econometric_V2" / "4.6_H6CCCLRegression"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "4_Econometric_V2" / "4.6_H6CCCLRegression"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H6.log"

    return paths


# ==============================================================================
# Data Loading
# ==============================================================================


def load_h6_variables(h6_dir, dw=None):
    """
    Load H6 CCCL Speech variables.

    Expects H6_CCCL_Speech.parquet with columns:
    - gvkey, fiscal_year (panel identifiers)
    - CCCL variants (6 variants + 6 lagged variants)
    - Speech uncertainty measures (6 measures)
    - uncertainty_gap (for H6-C)
    """
    h6_file = h6_dir / "H6_CCCL_Speech.parquet"
    if not h6_file.exists():
        raise FileNotFoundError(f"H6_CCCL_Speech.parquet not found in {h6_dir}")

    validate_input_file(h6_file, must_exist=True)
    df = pd.read_parquet(h6_file)

    if dw:
        dw.write(f"  Loaded H6 data: {len(df):,} observations\n")
        dw.write(f"    Columns: {df.columns.tolist()}\n")
        dw.write(
            f"    Year range: {df['fiscal_year'].min()}-{df['fiscal_year'].max()}\n"
        )
        dw.write(f"    Unique firms: {df['gvkey'].nunique():,}\n")

    # Ensure gvkey is string and zero-padded
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    return df


# ==============================================================================
# Data Preparation
# ==============================================================================


def prepare_regression_data(df, uncertainty_cols, cccl_col, dw=None):
    """
    Prepare regression data for H6 analysis.

    For each uncertainty measure, we need:
    - Uncertainty measure (DV) - not null
    - CCCL exposure (IV) - not null
    - Panel identifiers (gvkey, fiscal_year) - not null
    """
    # Define required columns
    required_cols = ["gvkey", "fiscal_year", cccl_col]

    # Check which uncertainty measures are available
    available_measures = [c for c in uncertainty_cols if c in df.columns]

    # Include uncertainty_gap if present
    if "uncertainty_gap" in df.columns:
        available_measures.append("uncertainty_gap")

    if dw:
        dw.write(f"  Available uncertainty measures: {available_measures}\n")

    # Build regression dataset with all uncertainty measures
    reg_df = df[required_cols + available_measures].copy()

    # Drop rows where CCCL or identifiers are missing
    reg_df = reg_df.dropna(subset=required_cols)

    if dw:
        dw.write(f"  After dropping missing CCCL/IDs: {len(reg_df):,} obs\n")

    # Count unique firms and time periods
    n_firms = reg_df["gvkey"].nunique()
    years = sorted(reg_df["fiscal_year"].unique())

    if dw:
        dw.write(f"  Unique firms: {n_firms:,}\n")
        dw.write(f"  Years: {min(years)}-{max(years)} ({len(years)} years)\n")

    # Check data quality for each uncertainty measure
    if dw:
        dw.write("\n  Uncertainty measure coverage:\n")
        for col in available_measures:
            if col in reg_df.columns:
                n_obs = reg_df[col].notna().sum()
                pct = n_obs / len(reg_df) * 100
                dw.write(f"    {col}: {n_obs:,} ({pct:.1f}%)\n")

    return reg_df, available_measures


# ==============================================================================
# Single Regression
# ==============================================================================


def run_single_h6_regression(
    df, uncertainty_var, cccl_var, spec_name, spec_config, vif_threshold=5.0, dw=None
):
    """
    Run a single H6 regression.

    Model:
        Uncertainty_{i,t} = beta0 + beta1*CCCL_{i,t-1} + Firm_FE + Year_FE + epsilon

    Hypothesis test:
        H6-A: beta1 < 0 (CCCL reduces uncertainty - one-tailed)
        p_one_tail = p_two_tail / 2 if beta < 0, else 1 - p_two_tail/2
    """
    df_work = df.copy()

    # Build exog list (just CCCL for minimal specification)
    # Note: Controls would be added here if available (firm_size, leverage, roa)
    exog = [cccl_var]

    # Add controls if available (e.g., for Q&A specs add Pres_Uncertainty)
    # This is optional as Firm FE absorbs time-invariant firm characteristics

    # Drop rows where any exog or DV is missing
    complete_cols = exog + [uncertainty_var, "gvkey", "fiscal_year"]
    df_reg = df_work[complete_cols].dropna()

    if len(df_reg) < 100:
        if dw:
            dw.write(f"  ERROR: Insufficient observations ({len(df_reg)})\n")
        return None

    # Pre-flight VIF check (trivial for single IV, but good practice)
    if len(exog) >= 2:
        try:
            vif_result = check_multicollinearity(
                df_reg,
                exog,
                vif_threshold=vif_threshold,
                condition_threshold=1000.0,
                fail_on_violation=False,
            )
            if vif_result["vif_violations"]:
                if dw:
                    dw.write(f"  WARNING: High VIF: {vif_result['vif_violations']}\n")
        except Exception as e:
            if dw:
                dw.write(f"  VIF check skipped: {e}\n")

    # Determine cluster columns
    cluster_cols = spec_config.get("cluster_cols")

    try:
        result = run_panel_ols(
            df=df_reg,
            dependent=uncertainty_var,
            exog=exog,
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=spec_config.get("entity_effects", True),
            time_effects=spec_config.get("time_effects", True),
            cov_type="clustered",
            cluster_cols=cluster_cols,
            check_collinearity=False,
            vif_threshold=vif_threshold,
        )
    except Exception as e:
        if dw:
            dw.write(f"  ERROR: Regression failed: {e}\n")
        return None

    # Extract results
    coeffs_df = result["coefficients"]
    summary = result["summary"]

    # Get CCCL coefficient
    beta_cccl = (
        coeffs_df.loc[cccl_var, "Coefficient"]
        if cccl_var in coeffs_df.index
        else np.nan
    )
    se_cccl = (
        coeffs_df.loc[cccl_var, "Std. Error"] if cccl_var in coeffs_df.index else np.nan
    )
    t_cccl = (
        coeffs_df.loc[cccl_var, "t-stat"] if cccl_var in coeffs_df.index else np.nan
    )

    # Get p-value
    pvalues = result["model"].pvalues
    p_two = pvalues.get(cccl_var, np.nan)

    # One-tailed hypothesis test (H6: beta_CCCL < 0)
    if not np.isnan(p_two) and not np.isnan(beta_cccl):
        if beta_cccl < 0:
            p_one = p_two / 2
        else:
            p_one = 1 - p_two / 2
    else:
        p_one = np.nan

    # Hypothesis test outcome (H6-A: CCCL reduces uncertainty)
    h6a_supported = (not np.isnan(p_one)) and (p_one < 0.05) and (beta_cccl < 0)

    return {
        "spec": spec_name,
        "uncertainty_var": uncertainty_var,
        "cccl_var": cccl_var,
        "n_obs": summary["nobs"],
        "n_firms": df_reg["gvkey"].nunique(),
        "n_years": df_reg["fiscal_year"].nunique(),
        "r_squared": summary["rsquared"],
        "r_squared_within": summary.get("rsquared_within", None),
        "f_stat": summary.get("f_statistic", None),
        "f_pvalue": summary.get("f_pvalue", None),
        "beta_cccl": beta_cccl,
        "se_cccl": se_cccl,
        "t_cccl": t_cccl,
        "p_value_two_tail": p_two,
        "p_value_one_tail": p_one,
        "h6a_supported": h6a_supported,
        "entity_effects": summary["entity_effects"],
        "time_effects": summary["time_effects"],
        "warnings": result.get("warnings", []),
    }


# ==============================================================================
# Pre-trends Test
# ==============================================================================


def run_pre_trends_test(df, uncertainty_var, cccl_lag_var, dw=None):
    """
    Run pre-trends test (falsification check).

    Model:
        Uncertainty_t = beta_{-2}*CCCL_{t-2} + beta_{-1}*CCCL_{t-1}
                       + beta_0*CCCL_t + Controls + FE

    Identification: Leads (t-2, t-1) should be insignificant (no anticipatory effects).
    Current (t) should be negative and significant.

    Note: We use lagged CCCL (t-1) to create leads by shifting:
        CCCL_lead2 = CCCL_lag shifted forward by 2
        CCCL_lead1 = CCCL_lag shifted forward by 1
        CCCL_current = CCCL_lag
    """
    df_work = df.copy()

    # Sort by firm and year
    df_work = df_work.sort_values(["gvkey", "fiscal_year"]).copy()

    # Create forward shifts (leads) from the lagged variable
    # If CCCL_lag is CCCL_{t-1}, then:
    #   shift(-2, groupby) on CCCL_lag gives CCCL_{t+1} relative to current row
    #   We need to be careful about what we're measuring

    # For pre-trends, we want to test if FUTURE CCCL predicts CURRENT uncertainty
    # CCCL_{t+1} and CCCL_{t+2} should not predict Uncertainty_t

    # CCCL_lag in the data is CCCL_{year-1}
    # So CCCL_lag shifted forward by 1 is CCCL_{year} (contemporaneous)
    # And CCCL_lag shifted forward by 2 is CCCL_{year+1} (future)

    df_work["cccl_future1"] = df_work.groupby("gvkey")[cccl_lag_var].shift(-1)
    df_work["cccl_future2"] = df_work.groupby("gvkey")[cccl_lag_var].shift(-2)
    df_work["cccl_contemp"] = df_work[cccl_lag_var]

    # Build regression with future leads and contemporaneous
    exog_vars = ["cccl_future2", "cccl_future1", "cccl_contemp"]

    # Drop missing
    complete_cols = exog_vars + [uncertainty_var, "gvkey", "fiscal_year"]
    df_reg = df_work[complete_cols].dropna()

    if len(df_reg) < 100:
        if dw:
            dw.write(
                f"  WARNING: Pre-trends test - insufficient observations ({len(df_reg)})\n"
            )
        return {
            "uncertainty_var": uncertainty_var,
            "note": "insufficient_obs",
        }

    # Check for variation in CCCL variables
    has_variation = False
    for var in exog_vars:
        if df_reg[var].std() > 0:
            has_variation = True
            break

    if not has_variation:
        if dw:
            dw.write("  WARNING: Pre-trends test - no variation in CCCL variables\n")
            dw.write("    CCCL is sparse (many zeros). Cannot run pre-trends test.\n")
        return {
            "uncertainty_var": uncertainty_var,
            "note": "no_variation",
        }

    try:
        result = run_panel_ols(
            df=df_reg,
            dependent=uncertainty_var,
            exog=exog_vars,
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            cov_type="clustered",
            cluster_cols=None,
            check_collinearity=False,
        )
    except Exception as e:
        if dw:
            dw.write(f"  WARNING: Pre-trends test failed: {e}\n")
        return {
            "uncertainty_var": uncertainty_var,
            "note": "regression_failed",
        }

    # Extract coefficients
    coeffs_df = result["coefficients"]
    pvalues = result["model"].pvalues

    results = {}
    for var in exog_vars:
        if var in coeffs_df.index:
            beta = coeffs_df.loc[var, "Coefficient"]
            p_val = pvalues.get(var, np.nan)
            results[var] = {"beta": beta, "p_value": p_val}

    if dw:
        dw.write("\n  Pre-trends test results:\n")
        for var, res in results.items():
            sig = (
                "***"
                if res["p_value"] < 0.01
                else "**"
                if res["p_value"] < 0.05
                else "*"
                if res["p_value"] < 0.1
                else ""
            )
            dw.write(
                f"    {var}: beta={res['beta']:.4f}, p={res['p_value']:.4f} {sig}\n"
            )

    # Check if future leads are insignificant (p > 0.05)
    future1_insig = results.get("cccl_future1", {}).get("p_value", 1) > 0.05
    future2_insig = results.get("cccl_future2", {}).get("p_value", 1) > 0.05
    contemp_sig_neg = (
        results.get("cccl_contemp", {}).get("p_value", 1) < 0.05
        and results.get("cccl_contemp", {}).get("beta", 0) < 0
    )

    pre_trends_pass = future1_insig and future2_insig

    return {
        "uncertainty_var": uncertainty_var,
        "future2_beta": results.get("cccl_future2", {}).get("beta"),
        "future2_p": results.get("cccl_future2", {}).get("p_value"),
        "future1_beta": results.get("cccl_future1", {}).get("beta"),
        "future1_p": results.get("cccl_future1", {}).get("p_value"),
        "contemp_beta": results.get("cccl_contemp", {}).get("beta"),
        "contemp_p": results.get("cccl_contemp", {}).get("p_value"),
        "pre_trends_pass": pre_trends_pass,
        "contemp_significant_negative": contemp_sig_neg,
        "note": "success" if all(k in results for k in exog_vars) else "missing_coeffs",
    }


# ==============================================================================
# Main Regression Loop
# ==============================================================================


def run_primary_regressions(
    reg_df, uncertainty_measures, cccl_var, specs, vif_threshold=5.0, dw=None
):
    """
    Run primary H6 regressions for all uncertainty measures.

    Primary Model (H6-A):
    - 6 uncertainty measures x 4 specs = 24 regressions
    - Key test: CCCL coefficient < 0 (one-tailed)
    """
    results = []

    if dw:
        dw.write("\n=== Primary Regressions (H6-A) ===\n")
        dw.write("Testing whether CCCL reduces speech uncertainty\n")
        dw.write(f"CCCL variable: {cccl_var}\n")

    for uncertainty_var in uncertainty_measures:
        if uncertainty_var not in reg_df.columns:
            continue

        for spec_name, spec_config in specs.items():
            if dw:
                dw.write(f"\nRunning: {uncertainty_var} x {spec_name}\n")

            result = run_single_h6_regression(
                reg_df,
                uncertainty_var,
                cccl_var,
                spec_name,
                spec_config,
                vif_threshold,
                dw,
            )

            if result:
                results.append(result)

                if dw:
                    dw.write(f"  N={result['n_obs']:,}, R2={result['r_squared']:.4f}, ")
                    dw.write(
                        f"beta_CCCL={result['beta_cccl']:.4f} (p1={result['p_value_one_tail']:.4f})\n"
                    )

    return results


def run_mechanism_test(reg_df, cccl_var, vif_threshold=5.0, dw=None):
    """
    Run mechanism test (H6-B): Compare QA vs Presentation effects.

    Tests whether |beta_QA| > |beta_Pres|, indicating stronger effect
    in spontaneous speech.
    """
    if dw:
        dw.write("\n=== Mechanism Test (H6-B) ===\n")
        dw.write("Comparing QA vs Presentation effects\n")

    qa_measures = ["Manager_QA_Uncertainty_pct", "CEO_QA_Uncertainty_pct"]
    pres_measures = ["Manager_Pres_Uncertainty_pct", "CEO_Pres_Uncertainty_pct"]

    results = []

    # Run QA regressions
    qa_results = {}
    for measure in qa_measures:
        if measure in reg_df.columns:
            result = run_single_h6_regression(
                reg_df,
                measure,
                cccl_var,
                "primary",
                {"entity_effects": True, "time_effects": True, "cluster_cols": None},
                vif_threshold,
                dw=None,
            )
            if result:
                qa_results[measure] = result
                results.append(result)

    # Run Presentation regressions
    pres_results = {}
    for measure in pres_measures:
        if measure in reg_df.columns:
            result = run_single_h6_regression(
                reg_df,
                measure,
                cccl_var,
                "primary",
                {"entity_effects": True, "time_effects": True, "cluster_cols": None},
                vif_threshold,
                dw=None,
            )
            if result:
                pres_results[measure] = result
                results.append(result)

    # Compare effects
    comparison = []
    for qa_key, qa_res in qa_results.items():
        pres_key = qa_key.replace("QA", "Pres")
        if pres_key in pres_results:
            pres_res = pres_results[pres_key]
            qa_beta = abs(qa_res["beta_cccl"])
            pres_beta = abs(pres_res["beta_cccl"])
            qa_larger = qa_beta > pres_beta

            comparison.append(
                {
                    "qa_measure": qa_key,
                    "pres_measure": pres_key,
                    "qa_beta": qa_res["beta_cccl"],
                    "pres_beta": pres_res["beta_cccl"],
                    "qa_abs": qa_beta,
                    "pres_abs": pres_beta,
                    "qa_larger": qa_larger,
                }
            )

    if dw:
        dw.write("\n  QA vs Presentation comparison:\n")
        for comp in comparison:
            dw.write(f"    {comp['qa_measure']}: |{comp['qa_beta']:.4f}| vs ")
            dw.write(f"{comp['pres_measure']}: |{comp['pres_beta']:.4f}|")
            dw.write(f" - QA larger: {comp['qa_larger']}\n")

    # H6-B supported if QA effects are consistently larger
    h6b_supported = (
        len(comparison) > 0
        and sum(c["qa_larger"] for c in comparison) > len(comparison) / 2
    )

    return results, comparison, h6b_supported


def run_gap_analysis(reg_df, cccl_var, vif_threshold=5.0, dw=None):
    """
    Run gap analysis (H6-C): Test whether CCCL reduces uncertainty gap.

    Model:
        Uncertainty_Gap ~ CCCL_lag + Controls + FE

    Hypothesis: beta_CCCL < 0 (CCCL reduces Q&A-Pres uncertainty gap)
    """
    if dw:
        dw.write("\n=== Gap Analysis (H6-C) ===\n")
        dw.write("Testing whether CCCL reduces Q&A-Presentation uncertainty gap\n")

    if "uncertainty_gap" not in reg_df.columns:
        if dw:
            dw.write("  WARNING: uncertainty_gap not found\n")
        return None

    result = run_single_h6_regression(
        reg_df,
        "uncertainty_gap",
        cccl_var,
        "primary",
        {"entity_effects": True, "time_effects": True, "cluster_cols": None},
        vif_threshold,
        dw=dw,
    )

    if result:
        # H6-C: CCCL reduces gap (beta < 0)
        h6c_supported = result["p_value_one_tail"] < 0.05 and result["beta_cccl"] < 0
        result["h6c_supported"] = h6c_supported

        if dw:
            dw.write(
                f"\n  Gap regression: beta={result['beta_cccl']:.4f}, p={result['p_value_one_tail']:.4f}\n"
            )
            dw.write(f"  H6-C supported: {h6c_supported}\n")

    return result


def run_instrument_robustness(
    df, uncertainty_var, cccl_variants, specs, vif_threshold=5.0, dw=None
):
    """
    Run robustness checks with alternative CCCL instruments.
    Tests all 6 CCCL variants against the primary uncertainty measure.
    """
    results = []

    if dw:
        dw.write("\n=== Instrument Robustness ===\n")
        dw.write("Testing alternative CCCL instruments\n")

    primary_spec = specs["primary"]

    for cccl_var in cccl_variants:
        if cccl_var not in df.columns:
            if dw:
                dw.write(f"  Skipping {cccl_var}: not in data\n")
            continue

        if dw:
            dw.write(f"\n  Instrument: {cccl_var}\n")

        # Prepare data with this specific CCCL variant
        # Need to drop missing for this specific CCCL variable
        complete_cols = [cccl_var, uncertainty_var, "gvkey", "fiscal_year"]
        df_reg = df[complete_cols].dropna()

        if len(df_reg) < 100:
            if dw:
                dw.write(f"    Insufficient observations: {len(df_reg)}\n")
            continue

        result = run_single_h6_regression(
            df_reg,
            uncertainty_var,
            cccl_var,
            "robustness_instrument",
            primary_spec,
            vif_threshold,
            dw=None,  # Suppress verbose output
        )

        if result:
            results.append(result)
            if dw:
                sig = (
                    "***"
                    if result["p_value_one_tail"] < 0.01
                    else "**"
                    if result["p_value_one_tail"] < 0.05
                    else "*"
                    if result["p_value_one_tail"] < 0.1
                    else ""
                )
                dw.write(
                    f"    beta={result['beta_cccl']:.4f}, p={result['p_value_one_tail']:.4f} {sig}\n"
                )

    if dw:
        dw.write(
            f"\n  Summary: {len(results)}/{len(cccl_variants)} instruments tested\n"
        )

    return results


# ==============================================================================
# FDR Correction
# ==============================================================================


def apply_fdr_correction(results, alpha=0.05, dw=None):
    """
    Apply Benjamini-Hochberg FDR correction across primary regressions.

    Collects p-values from all primary spec regressions and adjusts
    for multiple testing using FDR (q=0.05).
    """
    # Filter to primary spec results
    primary_results = [r for r in results if r["spec"] == "primary"]

    if not primary_results:
        if dw:
            dw.write("\n  WARNING: No primary results for FDR correction\n")
        return results, {}

    # Extract p-values
    p_values = [
        r["p_value_one_tail"]
        for r in primary_results
        if not np.isnan(r["p_value_one_tail"])
    ]

    if len(p_values) == 0:
        if dw:
            dw.write("\n  WARNING: No valid p-values for FDR correction\n")
        return results, {}

    # Apply FDR correction
    from statsmodels.stats.multitest import multipletests

    reject, p_corrected, _, _ = multipletests(p_values, alpha=alpha, method="fdr_bh")

    if dw:
        dw.write("\n=== FDR Correction (Benjamini-Hochberg) ===\n")
        dw.write(f"  Tests: {len(p_values)}\n")
        dw.write(f"  Alpha: {alpha}\n")
        dw.write(f"  Significant after FDR: {sum(reject)}/{len(reject)}\n")

    # Update results with FDR-corrected p-values
    fdr_map = {}
    idx = 0
    for r in primary_results:
        if not np.isnan(r["p_value_one_tail"]):
            r["fdr_p_value"] = float(p_corrected[idx])
            r["fdr_significant"] = bool(reject[idx])
            fdr_map[r["uncertainty_var"]] = {
                "p_original": float(r["p_value_one_tail"]),
                "p_fdr": float(p_corrected[idx]),
                "significant": bool(reject[idx]),
            }
            idx += 1
        else:
            r["fdr_p_value"] = np.nan
            r["fdr_significant"] = False

    return results, fdr_map


# ==============================================================================
# Output Functions
# ==============================================================================


def save_regression_results(results, output_dir, dw=None):
    """Save regression results to parquet file"""
    rows = []

    for r in results:
        rows.append(
            {
                "spec": r["spec"],
                "uncertainty_var": r["uncertainty_var"],
                "cccl_var": r["cccl_var"],
                "n_obs": r["n_obs"],
                "n_firms": r.get("n_firms"),
                "n_years": r.get("n_years"),
                "r_squared": r["r_squared"],
                "r_squared_within": r.get("r_squared_within"),
                "f_stat": r.get("f_stat"),
                "f_pvalue": r.get("f_pvalue"),
                "beta_cccl": r["beta_cccl"],
                "se_cccl": r.get("se_cccl"),
                "t_cccl": r.get("t_cccl"),
                "p_value_two_tail": r.get("p_value_two_tail"),
                "p_value_one_tail": r.get("p_value_one_tail"),
                "fdr_p_value": r.get("fdr_p_value"),
                "fdr_significant": r.get("fdr_significant", False),
                "h6a_supported": r.get("h6a_supported", False),
                "entity_effects": r.get("entity_effects"),
                "time_effects": r.get("time_effects"),
            }
        )

    results_df = pd.DataFrame(rows)
    output_path = output_dir / "H6_Regression_Results.parquet"
    results_df.to_parquet(output_path, index=False)

    if dw:
        dw.write(f"\nSaved: {output_path.name} ({len(results_df)} regression rows)\n")

    return results_df


def generate_results_markdown(
    results, fdr_map, pre_trends, mechanism_comp, gap_result, output_dir, dw=None
):
    """Generate human-readable markdown summary of H6 regression results"""
    lines = []
    lines.append("# H6 CCCL Speech Uncertainty Regression Results")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Hypothesis description
    lines.append("## Hypothesis")
    lines.append("")
    lines.append(
        "- **H6-A (Primary):** SEC scrutiny (CCCL exposure) reduces speech uncertainty (beta_CCCL < 0)"
    )
    lines.append(
        "- **H6-B (Mechanism):** CCCL effect is stronger in spontaneous Q&A than prepared Presentation"
    )
    lines.append("- **H6-C (Gap):** CCCL reduces the Q&A-Presentation uncertainty gap")
    lines.append("")

    # Primary specification results
    lines.append("## Primary Specification Results (H6-A)")
    lines.append("")
    lines.append("Firm + Year FE, clustered SE at firm level")
    lines.append("")

    # Table header
    lines.append(
        "| Uncertainty Measure | N | Firms | Years | R2 | beta_CCCL (SE) | p1 (one-tail) | FDR q | H6-A |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")

    # Only include actual primary results (not duplicates from mechanism test)
    primary_measures = [
        "Manager_QA_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "CEO_QA_Weak_Modal_pct",
        "CEO_Pres_Uncertainty_pct",
    ]

    for measure in primary_measures:
        matching = [
            r
            for r in results
            if r["spec"] == "primary" and r["uncertainty_var"] == measure
        ]
        if matching:
            r = matching[0]
            uncertainty = r["uncertainty_var"]
            n = r["n_obs"]
            n_firms = r.get("n_firms", "-")
            n_years = r.get("n_years", "-")
            r2 = r["r_squared"]
            beta = r["beta_cccl"]
            se = r.get("se_cccl", 0)
            p1 = r["p_value_one_tail"]
            fdr_q = r.get("fdr_p_value")
            h6a = "Yes" if r.get("h6a_supported") else "No"

            # FDR significance indicator
            fdr_sig = "*" if r.get("fdr_significant") else ""

            lines.append(
                f"| {uncertainty} | {n:,} | {n_firms} | {n_years} | {r2:.4f} | "
                f"{beta:.4f} ({se:.4f}) | {p1:.4f} | {fdr_q:.4f}{fdr_sig} | {h6a} |"
            )

    lines.append("")
    lines.append(
        "*Significance: p < 0.05 (one-tailed). FDR q is Benjamini-Hochberg corrected p-value. * indicates FDR-significant at q=0.05.*"
    )
    lines.append("")

    # FDR summary
    if fdr_map:
        lines.append("## FDR Correction Results")
        lines.append("")
        fdr_sig_count = sum(1 for v in fdr_map.values() if v["significant"])
        lines.append(
            f"Benjamini-Hochberg FDR correction across {len(fdr_map)} primary tests:"
        )
        lines.append("")
        lines.append(f"- **Significant after FDR:** {fdr_sig_count}/{len(fdr_map)}")
        lines.append("")
        lines.append("| Measure | p (original) | p (FDR) | FDR Sig |")
        lines.append("|---|---|---|---|")
        for measure, vals in fdr_map.items():
            sig_str = "*" if vals["significant"] else ""
            lines.append(
                f"| {measure} | {vals['p_original']:.4f} | {vals['p_fdr']:.4f} | {sig_str} |"
            )
        lines.append("")

    # Hypothesis test outcomes summary
    lines.append("## Hypothesis Test Outcomes")
    lines.append("")

    # Count significant results for primary spec
    primary_sig = [
        r
        for r in results
        if r["spec"] == "primary"
        and r.get("h6a_supported")
        and r["uncertainty_var"] in primary_measures
    ]
    fdr_sig = [
        r
        for r in results
        if r["spec"] == "primary"
        and r.get("fdr_significant")
        and r["uncertainty_var"] in primary_measures
    ]

    lines.append("**H6-A (CCCL reduces uncertainty):**")
    lines.append(f"- Uncorrected (p < 0.05): {len(primary_sig)}/6 measures significant")
    lines.append(f"- FDR-corrected (q < 0.05): {len(fdr_sig)}/6 measures significant")
    lines.append("")

    # List significant measures
    if fdr_sig:
        lines.append("**FDR-significant measures:**")
        for r in fdr_sig:
            lines.append(
                f"- {r['uncertainty_var']}: beta_CCCL={r['beta_cccl']:.4f}, p_FDR={r['fdr_p_value']:.4f}"
            )
    elif primary_sig:
        lines.append("**Significant before FDR (not after):**")
        for r in primary_sig:
            lines.append(
                f"- {r['uncertainty_var']}: beta_CCCL={r['beta_cccl']:.4f}, p={r['p_value_one_tail']:.4f}"
            )
    else:
        lines.append("**No measures support H6-A**")
    lines.append("")

    # Pre-trends test
    if pre_trends:
        lines.append("## Pre-trends Test (Falsification)")
        lines.append("")
        note = pre_trends.get("note", "")
        if note == "no_variation":
            lines.append("Tests for anticipatory effects using future CCCL exposure.")
            lines.append("")
            lines.append(
                "**Pre-trends test: SKIPPED** - CCCL instrument has insufficient variation (sparse)."
            )
            lines.append(
                "The CCCL shift-share instrument is highly sparse with most observations at zero."
            )
            lines.append(
                "This makes pre-trends testing infeasible as leads would have no variation."
            )
        elif note and note != "success":
            lines.append(f"**Pre-trends test: SKIPPED** - {note}")
        else:
            lines.append("Tests for anticipatory effects using future CCCL exposure.")
            lines.append(
                "Identification assumption: Future CCCL should not predict current uncertainty."
            )
            lines.append("")

            lines.append("| Variable | Beta | p-value | Significant (p<0.05) |")
            lines.append("|---|---|---|---|")

            var_labels = {
                "future2_beta": "CCCL_{t+2}",
                "future1_beta": "CCCL_{t+1}",
                "contemp_beta": "CCCL_t",
            }
            var_p = {
                "future2_beta": "future2_p",
                "future1_beta": "future1_p",
                "contemp_beta": "contemp_p",
            }

            has_coeffs = False
            for var_key in ["future2_beta", "future1_beta", "contemp_beta"]:
                beta = pre_trends.get(var_key)
                p_key = var_p[var_key]
                p = pre_trends.get(p_key)
                if beta is not None and not np.isnan(beta):
                    has_coeffs = True
                    sig = "Yes" if p < 0.05 else "No"
                    label = var_labels[var_key]
                    lines.append(f"| {label} | {beta:.4f} | {p:.4f} | {sig} |")

            if has_coeffs:
                lines.append("")
                if pre_trends.get("pre_trends_pass"):
                    lines.append(
                        "**Pre-trends test: PASSED** - Future CCCL effects are insignificant, no anticipatory effects detected."
                    )
                else:
                    lines.append(
                        "**Pre-trends test: FAILED** - Future CCCL effects are significant, suggesting potential"
                    )
                    lines.append(
                        "anticipatory effects or pre-trends violation. This weakens the causal interpretation."
                    )

                if pre_trends.get("contemp_significant_negative"):
                    lines.append(
                        " Contemporaneous period (CCCL_t) is significant and negative as expected."
                    )
                else:
                    lines.append(" Contemporaneous period (CCCL_t) is not significant.")
            lines.append("")

    # Mechanism test
    if mechanism_comp:
        lines.append("## Mechanism Test (H6-B)")
        lines.append("")
        lines.append(
            "Tests whether CCCL effect is stronger in spontaneous Q&A than prepared Presentation."
        )
        lines.append("")

        lines.append(
            "| QA Measure | QA beta | Pres Measure | Pres beta | |QA| > |Pres| |"
        )
        lines.append("|---|---|---|---|---|")

        qa_larger_count = 0
        for comp in mechanism_comp:
            qa_larger_str = "Yes" if comp["qa_larger"] else "No"
            if comp["qa_larger"]:
                qa_larger_count += 1
            lines.append(
                f"| {comp['qa_measure']} | {comp['qa_beta']:.4f} | "
                f"{comp['pres_measure']} | {comp['pres_beta']:.4f} | {qa_larger_str} |"
            )

        lines.append("")
        h6b_supported = qa_larger_count > len(mechanism_comp) / 2
        if h6b_supported:
            lines.append(
                f"**H6-B: SUPPORTED** - {qa_larger_count}/{len(mechanism_comp)} QA effects larger than Pres."
            )
        else:
            lines.append(
                f"**H6-B: NOT SUPPORTED** - Only {qa_larger_count}/{len(mechanism_comp)} QA effects larger."
            )
        lines.append("")

    # Gap analysis
    if gap_result:
        lines.append("## Gap Analysis (H6-C)")
        lines.append("")
        lines.append("Tests whether CCCL reduces the Q&A-Presentation uncertainty gap.")
        lines.append("")
        lines.append("| Metric | Result |")
        lines.append("|---|---|")
        lines.append(
            f"| beta_CCCL | {gap_result['beta_cccl']:.4f} (SE: {gap_result.get('se_cccl', 0):.4f}) |"
        )
        lines.append(f"| p-value (one-tail) | {gap_result['p_value_one_tail']:.4f} |")
        lines.append(
            f"| H6-C supported | {'Yes' if gap_result.get('h6c_supported') else 'No'} |"
        )
        lines.append("")

        if gap_result.get("h6c_supported"):
            lines.append(
                "**Interpretation:** CCCL significantly reduces the uncertainty gap, suggesting"
            )
            lines.append(
                "managers become more consistent across spontaneous and prepared speech under scrutiny."
            )
        else:
            lines.append(
                "**Interpretation:** CCCL does not significantly reduce the uncertainty gap."
            )
        lines.append("")
    else:
        lines.append("## Gap Analysis (H6-C)")
        lines.append("")
        lines.append("Gap analysis results not available.")
        lines.append("")

    # Robustness summary
    lines.append("## Robustness Checks")
    lines.append("")
    lines.append("Alternative specifications and instruments:")
    lines.append("")

    # Count by spec type
    spec_counts = {}
    for r in results:
        spec = r["spec"]
        if spec not in spec_counts:
            spec_counts[spec] = 0
        spec_counts[spec] += 1

    lines.append("| Specification | Regressions |")
    lines.append("|---|---|")
    for spec, count in sorted(spec_counts.items()):
        lines.append(f"| {spec} | {count} |")
    lines.append("")

    lines.append("Instrument variants tested:")
    for variant in CCCL_VARIANTS:
        tested = any(r["cccl_var"] == variant for r in results)
        status = "Yes" if tested else "No"
        primary = " (PRIMARY)" if "_ff48_lag" in variant and "mkvalt" in variant else ""
        lines.append(f"- {variant}: {status}{primary}")
    lines.append("")

    lines.append("---")
    lines.append("*Phase: 42-h6-sec-scrutiny-cccl-reduces-manager-speech-uncertainty*")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    output_path = output_dir / "H6_RESULTS.md"
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    if dw:
        dw.write(f"Saved: {output_path.name}\n")

    return output_path


def save_stats(stats, output_dir, dw=None):
    """Save statistics dictionary to JSON file with numpy encoder"""
    stats_path = output_dir / "stats.json"

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (bool, np.bool_)):
                return bool(obj)
            return super().default(obj)

    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2, cls=NumpyEncoder)

    if dw:
        dw.write(f"Saved: {stats_path.name}\n")

    return stats_path


# ==============================================================================
# CLI and Main
# ==============================================================================


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="H6 CCCL Speech Uncertainty Regression - Panel OLS testing SEC scrutiny effects"
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
    dw.write("STEP 4.6: H6 CCCL Speech Uncertainty Regression\n")
    dw.write("=" * 80 + "\n")
    dw.write(f"Timestamp: {timestamp}\n")
    dw.write(f"Git SHA: {get_git_sha()}\n")
    dw.write(f"Config: {config.get('step_id', '4.6_H6CCCLRegression')}\n")
    dw.write("")

    # Stats tracking
    stats = {
        "step_id": "4.6_H6CCCLRegression",
        "timestamp": timestamp,
        "git_sha": get_git_sha(),
        "input": {},
        "processing": {},
        "output": {},
        "regressions": [],
        "fdr_results": {},
        "pre_trends": {},
        "mechanism_test": {},
        "gap_analysis": {},
        "timing": {},
        "memory": {},
    }

    start_time = time.time()
    start_mem = get_process_memory_mb()

    try:
        # Load H6 variables
        dw.write("\n[1] Loading H6 variables...\n")
        h6_df = load_h6_variables(paths["h6_dir"], dw)

        stats["input"]["h6_variables"] = {
            "rows": int(len(h6_df)),
            "source": str(paths["h6_dir"]),
        }

        # Primary CCCL variable
        primary_cccl = "shift_intensity_mkvalt_ff48_lag"

        # Prepare regression data
        dw.write("\n[2] Preparing regression data...\n")
        reg_df, available_measures = prepare_regression_data(
            h6_df, UNCERTAINTY_MEASURES, primary_cccl, dw
        )

        stats["processing"]["regression_prep"] = {
            "final_obs": int(len(reg_df)),
            "unique_firms": int(reg_df["gvkey"].nunique()),
            "years": [int(y) for y in sorted(reg_df["fiscal_year"].unique())],
            "measures": available_measures,
        }

        if args.dry_run:
            dw.write("\n[Dry run] Validation complete. Exiting.\n")
            return 0

        # Run primary regressions
        dw.write("\n[3] Running primary H6 regressions...\n")
        dw.write(
            f"  {len(available_measures)} uncertainty measures x {len(SPECS)} specifications\n"
        )
        dw.write(f"  Estimated {len(available_measures) * len(SPECS)} regressions\n")

        all_results = []
        primary_results = run_primary_regressions(
            reg_df, available_measures, primary_cccl, SPECS, vif_threshold=5.0, dw=dw
        )
        all_results.extend(primary_results)

        # Run mechanism test (H6-B)
        dw.write("\n[4] Running mechanism test (H6-B)...\n")
        mechanism_results, mechanism_comp, h6b_supported = run_mechanism_test(
            reg_df, primary_cccl, vif_threshold=5.0, dw=dw
        )
        all_results.extend(mechanism_results)

        stats["mechanism_test"] = {
            "comparison": mechanism_comp,
            "h6b_supported": h6b_supported,
        }

        # Run gap analysis (H6-C)
        dw.write("\n[5] Running gap analysis (H6-C)...\n")
        gap_result = run_gap_analysis(reg_df, primary_cccl, vif_threshold=5.0, dw=dw)
        if gap_result:
            all_results.append(gap_result)
            stats["gap_analysis"] = {
                "beta_cccl": gap_result["beta_cccl"],
                "p_value": gap_result["p_value_one_tail"],
                "h6c_supported": gap_result.get("h6c_supported", False),
            }

        # Run pre-trends test
        dw.write("\n[6] Running pre-trends test...\n")
        pre_trends = run_pre_trends_test(
            h6_df, "Manager_QA_Uncertainty_pct", primary_cccl, dw=dw
        )
        if pre_trends:
            stats["pre_trends"] = pre_trends

        # Run instrument robustness
        dw.write("\n[7] Running instrument robustness checks...\n")
        robustness_results = run_instrument_robustness(
            h6_df,
            "Manager_QA_Uncertainty_pct",
            CCCL_VARIANTS,
            SPECS,
            vif_threshold=5.0,
            dw=dw,
        )
        all_results.extend(robustness_results)

        # Apply FDR correction
        dw.write("\n[8] Applying FDR correction...\n")
        all_results, fdr_map = apply_fdr_correction(all_results, alpha=0.05, dw=dw)
        stats["fdr_results"] = fdr_map

        # Count FDR significant results
        fdr_sig_count = sum(1 for r in all_results if r.get("fdr_significant"))
        stats["hypothesis_summary"] = {
            "h6a_primary_measures": len(available_measures),
            "h6a_fdr_significant": fdr_sig_count,
            "h6b_supported": h6b_supported,
            "h6c_supported": gap_result.get("h6c_supported", False)
            if gap_result
            else False,
            "pre_trends_pass": pre_trends.get("pre_trends_pass", False)
            if pre_trends
            else None,
        }

        # Save outputs
        dw.write("\n[9] Saving outputs...\n")
        results_df = save_regression_results(all_results, paths["output_dir"], dw)
        generate_results_markdown(
            all_results,
            fdr_map,
            pre_trends,
            mechanism_comp,
            gap_result,
            paths["output_dir"],
            dw,
        )

        stats["output"]["regression_results"] = {
            "file": "H6_Regression_Results.parquet",
            "rows": int(len(results_df)),
            "regressions": len(all_results),
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
        dw.write(f"  Regressions: {len(all_results)}\n")
        dw.write(f"  Output directory: {paths['output_dir']}\n")

        dw.write("\n  Hypothesis Summary:\n")
        dw.write(
            f"    H6-A (FDR sig): {stats['hypothesis_summary']['h6a_fdr_significant']}/{stats['hypothesis_summary']['h6a_primary_measures']}\n"
        )
        dw.write(
            f"    H6-B (QA > Pres): {stats['hypothesis_summary']['h6b_supported']}\n"
        )
        dw.write(f"    H6-C (Gap): {stats['hypothesis_summary']['h6c_supported']}\n")
        if pre_trends:
            dw.write(
                f"    Pre-trends: {'PASS' if stats['hypothesis_summary']['pre_trends_pass'] else 'FAIL'}\n"
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

    return 0


if __name__ == "__main__":
    sys.exit(main())
