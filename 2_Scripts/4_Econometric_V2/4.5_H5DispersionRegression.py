#!/usr/bin/env python3
"""
==============================================================================
STEP 4.5: H5 Analyst Dispersion Regression
==============================================================================
ID: 4.5_H5DispersionRegression
Description: Panel OLS regressions for H5 (Speech Uncertainty & Analyst Dispersion).
             Tests whether hedging language (weak modal verbs) predicts analyst
             forecast dispersion beyond what general uncertainty words predict.

Model Specification (Primary - H5-A):
    Dispersion_{t+1} = beta1*Weak_Modal_t + beta2*Uncertainty_t
                     + beta3*Prior_Dispersion_t
                     + gamma*Controls + Firm FE + Year FE + epsilon

Model Specification (Secondary - H5-B Gap):
    Dispersion_{t+1} = beta1*Uncertainty_Gap_t + beta2*Pres_Uncertainty_t
                     + beta3*Prior_Dispersion_t
                     + gamma*Controls + Firm FE + Year FE + epsilon

Hypothesis Tests:
    H5-A: beta1 > 0 (Weak Modal predicts higher dispersion, controlling for Uncertainty)
    H5-B: beta1 > 0 (Gap predicts dispersion - spontaneous reveals hidden uncertainty)

Inputs:
    - 4_Outputs/3_Financial_V2/3.5_H5Variables/latest/H5_AnalystDispersion.parquet
      (dispersion_lead, prior_dispersion, earnings_surprise, loss_dummy,
       analyst_coverage, firm controls, speech measures, uncertainty_gap)

Outputs:
    - 4_Outputs/4_Econometric_V2/4.5_H5DispersionRegression/{timestamp}/H5_Regression_Results.parquet
    - 4_Outputs/4_Econometric_V2/4.5_H5DispersionRegression/{timestamp}/H5_RESULTS.md
    - 4_Outputs/4_Econometric_V2/4.5_H5DispersionRegression/{timestamp}/stats.json
    - 3_Logs/4_Econometric_V2/4.5_H5DispersionRegression/{timestamp}_H5.log

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
from shared.diagnostics import (
    check_multicollinearity,
)
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


# Uncertainty measures available in H5 data
# Note: CEO_Pres_* not available (not loaded in 3.5_H5Variables.py)
UNCERTAINTY_MEASURES = [
    "Manager_QA_Weak_Modal_pct",  # PRIMARY - Novel contribution
    "Manager_QA_Uncertainty_pct",  # Established - comparison
    "Manager_Pres_Weak_Modal_pct",  # Scripted hedging (weaker expected)
    "Manager_Pres_Uncertainty_pct",  # Scripted uncertainty (weaker expected)
    "CEO_QA_Weak_Modal_pct",  # CEO-specific hedging
    "CEO_QA_Uncertainty_pct",  # CEO-specific uncertainty
]

# Primary control variables
CONTROL_VARS = [
    "firm_size",
    "leverage",
    "earnings_volatility",
    "tobins_q",
]

# All controls including lagged DV and analyst coverage
FULL_CONTROLS = [
    "prior_dispersion",  # Lagged DV - essential for persistence
    "earnings_surprise",  # Confounding control (determined before speech)
    "analyst_coverage",  # NUMEST (log) - standard control
    "loss_dummy",  # NI < 0 dummy
    "firm_size",
    "leverage",
    "earnings_volatility",
    "tobins_q",
]

# Specification variants
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

# Robustness variants
ROBUSTNESS_SPECS = {
    "no_lagged_dv": "Exclude prior_dispersion (addresses Nickell bias)",
    "no_numest": "Exclude analyst_coverage (addresses bad control concern)",
    "ceo_only": "Use CEO-specific measures instead of Manager aggregates",
}


# ==============================================================================
# Path Setup
# ==============================================================================


def setup_paths(config, timestamp):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    # Resolve H5 variables directory
    h5_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2" / "3.5_H5Variables",
        required_file="H5_AnalystDispersion.parquet",
    )

    paths = {
        "root": root,
        "h5_dir": h5_dir,
    }

    # Output directory
    output_base = root / "4_Outputs" / "4_Econometric_V2" / "4.5_H5DispersionRegression"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "4_Econometric_V2" / "4.5_H5DispersionRegression"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H5.log"

    return paths


# ==============================================================================
# Data Loading
# ==============================================================================


def load_h5_variables(h5_dir, dw=None):
    """
    Load H5 Analyst Dispersion variables.

    Expects H5_AnalystDispersion.parquet with columns:
    - gvkey, fiscal_year, fiscal_quarter
    - dispersion_lead (DV), prior_dispersion
    - earnings_surprise, loss_dummy, analyst_coverage
    - firm_size, leverage, earnings_volatility, tobins_q
    - Speech measures: Manager_QA_Weak_Modal_pct, Manager_QA_Uncertainty_pct, etc.
    - uncertainty_gap (for H5-B)
    """
    h5_file = h5_dir / "H5_AnalystDispersion.parquet"
    if not h5_file.exists():
        raise FileNotFoundError(f"H5_AnalystDispersion.parquet not found in {h5_dir}")

    validate_input_file(h5_file, must_exist=True)
    df = pd.read_parquet(h5_file)

    if dw:
        dw.write(f"  Loaded H5 variables: {len(df):,} rows\n")
        dw.write(f"    Columns: {df.columns.tolist()}\n")

    # Ensure gvkey is string and zero-padded
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    return df


# ==============================================================================
# Data Preparation
# ==============================================================================


def prepare_regression_data(df, uncertainty_cols, dw=None):
    """
    Prepare regression data by selecting complete cases for key variables.

    For each regression, we need:
    - dispersion_lead (DV) - not null
    - All control variables - not null
    - Uncertainty measures - at least one not null
    """
    # Define columns that must be non-null for all regressions
    required_cols = ["dispersion_lead", "gvkey", "fiscal_year", "fiscal_quarter"]

    # Define control columns needed
    control_cols = [
        "prior_dispersion",
        "earnings_surprise",
        "analyst_coverage",
        "loss_dummy",
        "firm_size",
        "leverage",
        "earnings_volatility",
        "tobins_q",
    ]

    # Check which controls are available
    available_controls = [c for c in control_cols if c in df.columns]

    if dw:
        dw.write(f"  Available controls: {available_controls}\n")

    # For complete case analysis, we'll use progressively looser filters
    # Strictest: All controls present
    strict_controls = available_controls

    # Create dataset with strict controls
    strict_df = df[required_cols + strict_controls].dropna()

    if dw:
        dw.write(f"  Strict complete cases: {len(strict_df):,} obs\n")

    # Add uncertainty measures back (with NAs allowed for some)
    for col in uncertainty_cols:
        if col in df.columns:
            strict_df[col] = df[col]

    # Also add uncertainty_gap for gap model (H5-B)
    if "uncertainty_gap" in df.columns:
        strict_df["uncertainty_gap"] = df["uncertainty_gap"]

    # Count unique firms and time periods
    n_firms = strict_df["gvkey"].nunique()
    years = sorted(strict_df["fiscal_year"].unique())
    n_quarters = strict_df["fiscal_quarter"].nunique()

    if dw:
        dw.write(f"  Unique firms: {n_firms:,}\n")
        dw.write(f"  Years: {min(years)}-{max(years)} ({len(years)} years)\n")
        dw.write(f"  Quarters: {n_quarters}\n")

    # Check data quality for each uncertainty measure
    if dw:
        dw.write("\n  Uncertainty measure coverage:\n")
        for col in uncertainty_cols:
            if col in strict_df.columns:
                n_obs = strict_df[col].notna().sum()
                pct = n_obs / len(strict_df) * 100
                dw.write(f"    {col}: {n_obs:,} ({pct:.1f}%)\n")

    return strict_df, available_controls


# ==============================================================================
# Single Regression
# ==============================================================================


def run_single_h5_regression(
    df,
    uncertainty_var,
    model_type,
    spec_name,
    spec_config,
    control_vars,
    vif_threshold=5.0,
    dw=None,
):
    """
    Run a single H5 regression.

    Model Types:
    - 'primary': Tests uncertainty_var with Uncertainty as control
    - 'gap': Tests uncertainty_gap with Pres_Uncertainty as control
    - 'solo': Tests uncertainty_var alone (no uncertainty control)

    Hypothesis tests:
    - H5-A: beta1 > 0 (uncertainty_var coefficient)
      p_one_tail = p_two_tail / 2 if beta > 0, else 1 - p_two_tail/2
    """
    df_work = df.copy()

    # Determine control variable based on model type
    if model_type == "primary":
        # Primary: Test Weak_Modal controlling for Uncertainty
        if uncertainty_var == "Manager_QA_Weak_Modal_pct":
            control_var = "Manager_QA_Uncertainty_pct"
        elif uncertainty_var == "CEO_QA_Weak_Modal_pct":
            control_var = "CEO_QA_Uncertainty_pct"
        elif uncertainty_var == "Manager_Pres_Weak_Modal_pct":
            control_var = "Manager_Pres_Uncertainty_pct"
        else:
            # For Uncertainty measures, no control needed
            control_var = None
    elif model_type == "gap":
        # Gap model: uncertainty_gap is the IV
        uncertainty_var = "uncertainty_gap"
        control_var = "Manager_Pres_Uncertainty_pct"
    else:  # solo
        control_var = None

    # Build exog list
    # Start with controls
    exog = [c for c in control_vars if c in df_work.columns]

    # Add uncertainty measure (IV)
    if uncertainty_var in df_work.columns:
        exog.append(uncertainty_var)

    # Add control variable (for incremental contribution test)
    if control_var and control_var in df_work.columns:
        exog.append(control_var)

    # Remove lagged DV if specified (for robustness)
    if "no_lagged_dv" in spec_name and "prior_dispersion" in exog:
        exog.remove("prior_dispersion")

    # Remove analyst_coverage if specified (for robustness)
    if "no_numest" in spec_name and "analyst_coverage" in exog:
        exog.remove("analyst_coverage")

    # Check we have enough variables
    if len(exog) < 2:
        if dw:
            dw.write("  ERROR: Insufficient variables for regression\n")
        return None

    # Drop rows where any exog or DV is missing
    # Include gvkey and fiscal_year for panel structure
    complete_cols = exog + ["dispersion_lead", "gvkey", "fiscal_year"]
    df_reg = df_work[complete_cols].dropna()

    if len(df_reg) < 100:
        if dw:
            dw.write(f"  ERROR: Insufficient observations ({len(df_reg)})\n")
        return None

    # Pre-flight VIF check (only on continuous controls, not dummy variables)
    continuous_controls = [c for c in exog if c not in ["loss_dummy"]]
    if len(continuous_controls) >= 2:
        try:
            vif_result = check_multicollinearity(
                df_reg,
                continuous_controls,
                vif_threshold=vif_threshold,
                condition_threshold=1000.0,  # Relaxed
                fail_on_violation=False,  # Warn but don't fail
            )
            if vif_result["vif_violations"]:
                if dw:
                    dw.write(f"  WARNING: High VIF: {vif_result['vif_violations']}\n")
        except Exception as e:
            if dw:
                dw.write(f"  VIF check skipped: {e}\n")

    # Run panel OLS
    cluster_cols = (
        ["gvkey", "fiscal_year"] if spec_config.get("double_cluster") else ["gvkey"]
    )

    try:
        result = run_panel_ols(
            df=df_reg,
            dependent="dispersion_lead",
            exog=exog,
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=spec_config.get("entity_effects", True),
            time_effects=spec_config.get("time_effects", True),
            cov_type="clustered",
            cluster_cols=cluster_cols,
            check_collinearity=False,  # Already checked above
            vif_threshold=vif_threshold,
        )
    except Exception as e:
        if dw:
            dw.write(f"  ERROR: Regression failed: {e}\n")
        return None

    # Extract results
    coeffs_df = result["coefficients"]
    summary = result["summary"]

    # Get coefficients of interest
    beta1_name = uncertainty_var
    beta1 = (
        coeffs_df.loc[beta1_name, "Coefficient"]
        if beta1_name in coeffs_df.index
        else np.nan
    )

    # Get p-values
    pvalues = result["model"].pvalues
    p1_two = pvalues.get(beta1_name, np.nan)

    # One-tailed hypothesis test (H5: beta1 > 0)
    if not np.isnan(p1_two) and not np.isnan(beta1):
        if beta1 > 0:
            p1_one = p1_two / 2
        else:
            p1_one = 1 - p1_two / 2
    else:
        p1_one = np.nan

    # Hypothesis test outcome
    h5_supported = (not np.isnan(p1_one)) and (p1_one < 0.05) and (beta1 > 0)

    # Get beta2 if control_var exists
    beta2 = np.nan
    beta2_se = np.nan
    beta2_p_two = np.nan
    beta2_signif = False
    if control_var and control_var in coeffs_df.index:
        beta2 = coeffs_df.loc[control_var, "Coefficient"]
        beta2_se = coeffs_df.loc[control_var, "Std. Error"]
        beta2_p_two = pvalues.get(control_var, np.nan)
        # For control variable, we also expect positive (established effect)
        if not np.isnan(beta2_p_two) and not np.isnan(beta2):
            if beta2 > 0:
                beta2_p_one = beta2_p_two / 2
            else:
                beta2_p_one = 1 - beta2_p_two / 2
            beta2_signif = beta2_p_one < 0.05 and beta2 > 0

    return {
        "spec": spec_name,
        "model_type": model_type,
        "uncertainty_var": uncertainty_var,
        "control_var": control_var,
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
        "beta1_signif": h5_supported,
        "beta2": beta2,
        "beta2_se": beta2_se,
        "beta2_p_two": beta2_p_two,
        "beta2_signif": beta2_signif,
        "warnings": result.get("warnings", []),
    }


# ==============================================================================
# Main Regression Loop
# ==============================================================================


def run_all_h5_regressions(
    reg_df, uncertainty_measures, specs, control_vars, vif_threshold=5.0, dw=None
):
    """
    Run all H5 regressions.

    Primary Model (H5-A):
    - 6 uncertainty measures x 4 specs = 24 regressions
    - Key: Manager_QA_Weak_Modal_pct controlling for Manager_QA_Uncertainty_pct

    Gap Model (H5-B):
    - 1 gap measure x 4 specs = 4 regressions

    Robustness:
    - 3 variants x 4 specs = 12 additional regressions per primary measure
    """
    results = []

    # Primary model tests
    if dw:
        dw.write("\n=== Primary Model (H5-A) ===\n")
        dw.write("Testing whether hedging predicts dispersion beyond uncertainty\n")

    for uncertainty_var in uncertainty_measures:
        # Determine model type
        if "Weak_Modal" in uncertainty_var:
            model_type = "primary"  # Tests hedging controlling for uncertainty
        elif "Uncertainty_pct" in uncertainty_var and "Pres" not in uncertainty_var:
            model_type = "solo"  # Established effect - no control needed
        else:
            model_type = "solo"

        for spec_name, spec_config in specs.items():
            if dw:
                dw.write(f"\nRunning: {uncertainty_var} x {spec_name} ({model_type})\n")

            result = run_single_h5_regression(
                reg_df,
                uncertainty_var,
                model_type,
                spec_name,
                spec_config,
                control_vars,
                vif_threshold,
                dw,
            )

            if result:
                results.append(result)

                if dw:
                    dw.write(
                        f"  N={result['n_obs']}, R2={result['r_squared']:.4f}, "
                        f"beta1={result['beta1']:.4f} (p1={result['beta1_p_one']:.4f})"
                    )
                    if result["control_var"]:
                        dw.write(
                            f", beta2({result['control_var']})={result['beta2']:.4f} (sig={result['beta2_signif']})\n"
                        )
                    else:
                        dw.write("\n")

    # Gap model tests
    if dw:
        dw.write("\n=== Gap Model (H5-B) ===\n")
        dw.write("Testing whether spontaneous-scripted gap predicts dispersion\n")

    for spec_name, spec_config in specs.items():
        if dw:
            dw.write(f"\nRunning: uncertainty_gap x {spec_name}\n")

        result = run_single_h5_regression(
            reg_df,
            "uncertainty_gap",
            "gap",
            spec_name,
            spec_config,
            control_vars,
            vif_threshold,
            dw,
        )

        if result:
            results.append(result)

            if dw:
                dw.write(
                    f"  N={result['n_obs']}, R2={result['r_squared']:.4f}, "
                    f"beta1={result['beta1']:.4f} (p1={result['beta1_p_one']:.4f})\n"
                )

    return results


# ==============================================================================
# Output Functions
# ==============================================================================


def save_regression_results(results, output_dir, dw=None):
    """Save regression results to parquet file"""
    rows = []

    for r in results:
        base_info = {
            "spec": r["spec"],
            "model_type": r["model_type"],
            "uncertainty_var": r["uncertainty_var"],
            "control_var": r.get("control_var"),
            "n_obs": r["n_obs"],
            "r_squared": r["r_squared"],
            "r_squared_within": r["r_squared_within"],
            "f_stat": r["f_stat"],
            "f_pvalue": r["f_pvalue"],
        }

        # Add key coefficients
        rows.append(
            {
                **base_info,
                "variable": "beta1",
                "var_name": r["uncertainty_var"],
                "coefficient": r["beta1"],
                "se": r["beta1_se"],
                "t_stat": r["beta1_t"],
                "p_value": r["beta1_p_two"],
                "p_value_one_tail": r["beta1_p_one"],
                "hypothesis_supported": r["beta1_signif"],
            }
        )

        # Add control variable coefficient
        if r.get("control_var") and not np.isnan(r["beta2"]):
            rows.append(
                {
                    **base_info,
                    "variable": "beta2",
                    "var_name": r["control_var"],
                    "coefficient": r["beta2"],
                    "se": r["beta2_se"],
                    "p_value": r["beta2_p_two"],
                    "p_value_one_tail": np.nan,
                    "hypothesis_supported": r["beta2_signif"],
                }
            )

    results_df = pd.DataFrame(rows)
    output_path = output_dir / "H5_Regression_Results.parquet"
    results_df.to_parquet(output_path, index=False)

    if dw:
        dw.write(f"\nSaved: {output_path.name} ({len(results_df)} coefficient rows)\n")

    return results_df


def generate_results_markdown(results, output_dir, dw=None):
    """Generate human-readable markdown summary of H5 regression results"""
    lines = []
    lines.append("# H5 Analyst Dispersion Regression Results")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Hypothesis description
    lines.append("## Hypothesis")
    lines.append("")
    lines.append(
        "- **H5-A:** Hedging language (weak modal verbs) predicts higher analyst forecast dispersion,"
    )
    lines.append(
        "          even after controlling for general uncertainty words (beta1 > 0)"
    )
    lines.append(
        "- **H5-B:** Spontaneous-scripted uncertainty gap predicts dispersion (beta1 > 0)"
    )
    lines.append("")

    # Primary specification results
    lines.append("## Primary Specification Results")
    lines.append("")
    lines.append("Firm + Year FE, clustered SE at firm level")
    lines.append("")

    # Table header
    lines.append("| Uncertainty Measure | N | R2 | beta1 (SE) | p1 (one-tail) | H5-A |")
    lines.append("|---|---|---|---|---|---|")

    for r in results:
        if r["spec"] == "primary" and r["model_type"] in ["primary", "solo"]:
            uncertainty = r["uncertainty_var"]
            n = r["n_obs"]
            r2 = r["r_squared"]
            beta1 = r["beta1"]
            beta1_se = r["beta1_se"]
            p1 = r["beta1_p_one"]
            h5a = "Yes" if r["beta1_signif"] else "No"

            # Add control var note if applicable
            control_note = (
                f" (ctrl: {r['control_var']})" if r.get("control_var") else ""
            )

            lines.append(
                f"| {uncertainty}{control_note} | {n:,} | {r2:.4f} | "
                f"{beta1:.4f} ({beta1_se:.4f}) | {p1:.4f} | {h5a} |"
            )

    lines.append("")
    lines.append(
        "*Significance: p < 0.05 (one-tailed). `ctrl` indicates control variable included.*"
    )
    lines.append("")

    # Hypothesis test outcomes summary
    lines.append("## Hypothesis Test Outcomes")
    lines.append("")

    # Count significant results for primary spec
    primary_weak_modal = [
        r
        for r in results
        if r["spec"] == "primary"
        and "Weak_Modal" in r["uncertainty_var"]
        and r["beta1_signif"]
    ]
    primary_uncertainty = [
        r
        for r in results
        if r["spec"] == "primary"
        and "Uncertainty_pct" in r["uncertainty_var"]
        and "Weak_Modal" not in r["uncertainty_var"]
        and r["beta1_signif"]
    ]

    lines.append("**Primary Specification (Firm + Year FE):**")
    lines.append(f"- Weak Modal measures: {len(primary_weak_modal)}/3 significant")
    lines.append(
        f"- Uncertainty measures: {len(primary_uncertainty)}/2 significant (QA only)"
    )
    lines.append("")

    # List significant measures
    if primary_weak_modal:
        lines.append("**Supporting H5-A (Weak Modal sig):**")
        for r in primary_weak_modal:
            control_str = (
                f" (controlling for {r['control_var']})" if r.get("control_var") else ""
            )
            lines.append(
                f"- {r['uncertainty_var']}: beta1={r['beta1']:.4f}, p={r['beta1_p_one']:.4f}{control_str}"
            )
    else:
        lines.append("**No Weak Modal measures support H5-A**")

    lines.append("")

    # Incremental contribution test
    lines.append("## Incremental Contribution Test")
    lines.append("")
    lines.append("Does hedging add predictive power beyond general uncertainty?")
    lines.append("")

    # Check Manager_QA_Weak_Modal with Manager_QA_Uncertainty control
    weak_modal_ctrl = [
        r
        for r in results
        if r["spec"] == "primary"
        and r["uncertainty_var"] == "Manager_QA_Weak_Modal_pct"
        and r["control_var"] == "Manager_QA_Uncertainty_pct"
    ]

    if weak_modal_ctrl:
        r = weak_modal_ctrl[0]
        sig = "YES" if r["beta1_signif"] else "NO"
        beta1_sig = "YES" if r.get("beta2_signif") else "NO"  # beta2 is control var
        lines.append("| Metric | Result |")
        lines.append("|---|---|")
        lines.append(
            f"| Weak Modal (beta1) | {r['beta1']:.4f} (p={r['beta1_p_one']:.4f}) |"
        )
        lines.append(
            f"| Uncertainty control (beta2) | {r['beta2']:.4f} (sig={beta1_sig}) |"
        )
        lines.append(f"| Weak Modal sig after controlling | **{sig}** |")
        lines.append("")

        if r["beta1_signif"]:
            lines.append(
                "**Conclusion:** Hedging language ADDS incremental predictive power beyond uncertainty."
            )
        elif r.get("beta2_signif"):
            lines.append(
                "**Conclusion:** Uncertainty predicts dispersion, but hedging does NOT add incremental power."
            )
        else:
            lines.append(
                "**Conclusion:** Neither hedging nor uncertainty significantly predict dispersion in this specification."
            )
    else:
        lines.append(
            "**No incremental contribution test available (Weak_Modal with Uncertainty control not found)**"
        )

    lines.append("")

    # Gap model results
    gap_results = [
        r for r in results if r["model_type"] == "gap" and r["spec"] == "primary"
    ]
    if gap_results:
        lines.append("## Gap Model Results (H5-B)")
        lines.append("")
        r = gap_results[0]
        sig = "YES" if r["beta1_signif"] else "NO"
        lines.append("| Metric | Result |")
        lines.append("|---|---|")
        lines.append(
            f"| Uncertainty Gap (beta1) | {r['beta1']:.4f} (p={r['beta1_p_one']:.4f}) |"
        )
        lines.append(f"| Gap significant | **{sig}** |")
        lines.append("")

        if r["beta1_signif"]:
            if r["beta1"] > 0:
                lines.append(
                    "**Interpretation:** Spontaneous (Q&A) uncertainty HIGHER than scripted (Pres)"
                )
                lines.append(
                    "reveals hidden information that increases analyst disagreement."
                )
            else:
                lines.append(
                    "**Interpretation:** Gap effect is significant but negative."
                )
        else:
            lines.append(
                "**Interpretation:** Gap does not significantly predict dispersion."
            )
    else:
        lines.append("## Gap Model Results (H5-B)")
        lines.append("")
        lines.append("No gap model results available.")
        lines.append("")

    lines.append("")

    # Robustness summary
    lines.append("## Robustness Checks")
    lines.append("")
    lines.append(
        "Robustness variants: Without lagged DV, without NUMEST, CEO-only measures"
    )
    lines.append("")
    lines.append("| Specification | Entity FE | Time FE | Cluster |")
    lines.append("|---|---|---|---|")
    lines.append("| primary | Yes | Yes | firm |")
    lines.append("| pooled | No | No | firm |")
    lines.append("| year_only | No | Yes | firm |")
    lines.append("| double_cluster | Yes | Yes | firm+year |")
    lines.append("")

    output_path = output_dir / "H5_RESULTS.md"
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
        description="H5 Analyst Dispersion Regression - Panel OLS testing hedging and uncertainty"
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
    dw.write("STEP 4.5: H5 Analyst Dispersion Regression\n")
    dw.write("=" * 80 + "\n")
    dw.write(f"Timestamp: {timestamp}\n")
    dw.write(f"Git SHA: {get_git_sha()}\n")
    dw.write(f"Config: {config.get('step_id', '4.5_H5DispersionRegression')}\n")
    dw.write("")

    # Stats tracking
    stats = {
        "step_id": "4.5_H5DispersionRegression",
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
        # Load H5 variables
        dw.write("\n[1] Loading H5 variables...\n")
        h5_df = load_h5_variables(paths["h5_dir"], dw)

        stats["input"]["h5_variables"] = {
            "rows": int(len(h5_df)),
            "source": str(paths["h5_dir"]),
        }

        # Prepare regression data
        dw.write("\n[2] Preparing regression data...\n")
        reg_df, available_controls = prepare_regression_data(
            h5_df, UNCERTAINTY_MEASURES, dw
        )

        stats["processing"]["regression_prep"] = {
            "final_obs": int(len(reg_df)),
            "unique_firms": int(reg_df["gvkey"].nunique()),
            "years": [int(y) for y in sorted(reg_df["fiscal_year"].unique())],
            "controls": available_controls,
        }

        if args.dry_run:
            dw.write("\n[Dry run] Validation complete. Exiting.\n")
            return 0

        # Run all regressions
        dw.write("\n[3] Running H5 regressions...\n")
        dw.write(
            f"  {len(UNCERTAINTY_MEASURES)} uncertainty measures x {len(SPECS)} specifications + gap model\n"
        )
        dw.write(
            f"  Estimated {len(UNCERTAINTY_MEASURES) * len(SPECS) + len(SPECS)} regressions\n"
        )

        results = run_all_h5_regressions(
            reg_df,
            UNCERTAINTY_MEASURES,
            SPECS,
            available_controls,
            vif_threshold=5.0,
            dw=dw,
        )

        # Filter out None results
        results = [r for r in results if r is not None]

        stats["regressions"] = [
            {
                "spec": r["spec"],
                "model_type": r["model_type"],
                "uncertainty_var": r["uncertainty_var"],
                "n_obs": r["n_obs"],
                "r_squared": r["r_squared"],
                "beta1": r["beta1"],
                "beta1_p_one": r["beta1_p_one"],
                "beta1_signif": r["beta1_signif"],
            }
            for r in results
        ]

        # Save outputs
        dw.write("\n[4] Saving outputs...\n")
        results_df = save_regression_results(results, paths["output_dir"], dw)
        generate_results_markdown(results, paths["output_dir"], dw)

        # Compute hypothesis summary
        weak_modal_sig = any(
            r["beta1_signif"]
            for r in results
            if "Weak_Modal" in r["uncertainty_var"] and r["spec"] == "primary"
        )
        gap_sig = any(
            r["beta1_signif"]
            for r in results
            if r["model_type"] == "gap" and r["spec"] == "primary"
        )

        stats["hypothesis_summary"] = {
            "H5A_weak_modal_significant": weak_modal_sig,
            "H5B_gap_significant": gap_sig,
            "total_regressions": len(results),
        }

        # Set interpretation
        weak_modal_ctrl = [
            r
            for r in results
            if r["spec"] == "primary"
            and r["uncertainty_var"] == "Manager_QA_Weak_Modal_pct"
            and r["control_var"] == "Manager_QA_Uncertainty_pct"
        ]
        if weak_modal_ctrl:
            r = weak_modal_ctrl[0]
            if r["beta1_signif"]:
                stats["hypothesis_summary"]["interpretation"] = (
                    "Hedging adds incremental power beyond uncertainty"
                )
            elif r.get("beta2_signif"):
                stats["hypothesis_summary"]["interpretation"] = (
                    "Uncertainty predicts dispersion, hedging does not add power"
                )
            else:
                stats["hypothesis_summary"]["interpretation"] = (
                    "Neither hedging nor uncertainty significant"
                )
        else:
            stats["hypothesis_summary"]["interpretation"] = (
                "Unable to determine (test not run)"
            )

        stats["output"]["regression_results"] = {
            "file": "H5_Regression_Results.parquet",
            "rows": int(len(results_df)),
            "regressions": len(results),
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

        dw.write(f"\n  Primary spec - Weak Modal significant: {weak_modal_sig}\n")
        dw.write(f"  Primary spec - Gap significant: {gap_sig}\n")
        dw.write(f"  Interpretation: {stats['hypothesis_summary']['interpretation']}\n")
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
