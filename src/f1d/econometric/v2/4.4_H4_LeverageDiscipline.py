#!/usr/bin/env python3
"""
==============================================================================
STEP 4.4: H4 Leverage Disciplines Speech (Data Preparation)
==============================================================================
ID: 4.4_H4_LeverageDiscipline
Description: Data preparation for H4 (Leverage Disciplines Speech Uncertainty).
             Tests whether higher leverage disciplines managers and reduces
             speech uncertainty (reverse causal direction from H1-H3).

Model Specification:
    Uncertainty_t = beta0 + beta1*Leverage_{t-1} + beta2*Analyst_Uncertainty_t
                     + beta3*Presentation_Uncertainty_t + gamma*Controls
                     + Firm FE + Year FE + Industry FE + epsilon

Hypothesis Test:
    H4: beta1 < 0 (Higher leverage leads to lower speech uncertainty - one-tailed)

Note: This script prepares the analysis dataset. Regressions will be run
      in a separate execution step.

Inputs:
    - 4_Outputs/3_Financial_V2/latest/H1_CashHoldings.parquet
      (leverage, firm_size, tobins_q, roa, cash_holdings, dividend_payer)
    - 4_Outputs/3_Financial_V2/latest/H3_PayoutPolicy.parquet
      (firm_maturity, earnings_volatility)
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_*.parquet
      (6 uncertainty DVs, analyst uncertainty, presentation uncertainty)

Outputs:
    - 4_Outputs/4_Econometric_V2/4.4_H4_LeverageDiscipline/{timestamp}/H4_Analysis_Dataset.parquet
      (complete analysis dataset with all variables for 6 regressions)
    - 4_Outputs/4_Econometric_V2/4.4_H4_LeverageDiscipline/{timestamp}/stats.json
      (merge stats, VIF diagnostics, variable availability, execution metadata)
    - 4_Outputs/4_Econometric_V2/4.4_H4_LeverageDiscipline/{timestamp}/H4_DATA_SUMMARY.md
      (human-readable summary of data preparation)
    - 3_Logs/4_Econometric_V2/4.4_H4_LeverageDiscipline/{timestamp}_H4.log
      (execution log with dual-writer output)

Deterministic: true
Dependencies:
    - Requires: Step 3.x
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
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import yaml
from scipy import stats

# Import shared utilities
from f1d.shared.diagnostics import check_multicollinearity, format_vif_table
from f1d.shared.observability_utils import (
    DualWriter,
    get_process_memory_mb,
    save_stats,
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


# H4: 6 uncertainty DVs (same as H1-H3)
UNCERTAINTY_MEASURES = [
    "Manager_QA_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Manager_QA_Weak_Modal_pct",
    "CEO_QA_Weak_Modal_pct",
    "Manager_Pres_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
]

# Analyst uncertainty control (from linguistic variables)
ANALYST_UNCERTAINTY_VAR = "Analyst_QA_Uncertainty_pct"

# Presentation controls for QA DVs (to control for presentation uncertainty)
PRESENTATION_CONTROL_MAP = {
    "Manager_QA_Uncertainty_pct": "Manager_Pres_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct": "CEO_Pres_Uncertainty_pct",
    "Manager_QA_Weak_Modal_pct": None,  # No direct presentation equivalent
    "CEO_QA_Weak_Modal_pct": None,
    "Manager_Pres_Uncertainty_pct": None,  # Already a presentation DV
    "CEO_Pres_Uncertainty_pct": None,
}

# Financial controls (from H1 and H3)
FINANCIAL_CONTROLS = [
    "firm_size",
    "tobins_q",
    "roa",
    "cash_holdings",
    "dividend_payer",
    "firm_maturity",
    "earnings_volatility",
]

# Base specification for VIF check (continuous vars only)
VIF_COLUMNS = [
    "leverage_lag1",
    "analyst_qa_uncertainty",
    "firm_size",
    "tobins_q",
    "roa",
    "cash_holdings",
    "firm_maturity",
    "earnings_volatility",
]

# ==============================================================================
# H4 Regression Execution Functions
# ==============================================================================


def one_tailed_pvalue(
    coef: float, se: float, df_resid: int, alternative: str = "less"
) -> float:
    """
    Calculate one-tailed p-value for directional hypothesis.

    H4 tests beta1 < 0 (alternative='less'): Higher leverage reduces speech uncertainty.

    Args:
        coef: Coefficient estimate
        se: Standard error
        df_resid: Residual degrees of freedom
        alternative: 'less' for beta < 0, 'greater' for beta > 0

    Returns:
        One-tailed p-value
    """
    if se <= 0:
        return np.nan

    t_stat = coef / se
    p_two_tailed = 2 * (1 - stats.t.cdf(abs(t_stat), df=df_resid))

    if alternative == "less":
        # Testing beta < 0
        return p_two_tailed / 2 if coef < 0 else 1 - p_two_tailed / 2
    elif alternative == "greater":
        # Testing beta > 0
        return p_two_tailed / 2 if coef > 0 else 1 - p_two_tailed / 2
    else:
        raise ValueError("alternative must be 'less' or 'greater'")


def run_all_h4_regressions(df: pd.DataFrame, dw: Any = None) -> Dict[str, Any]:
    """
    Run H4 regressions for all 6 uncertainty measures.

    Model Specification:
        Uncertainty_t = beta0 + beta1*Leverage_{t-1} + beta2*Analyst_Uncertainty_t
                        + beta3*Presentation_Uncertainty_t + gamma*Controls_t
                        + Firm_FE + Year_FE + epsilon

    H4: beta1 < 0 (Higher leverage reduces speech uncertainty - one-tailed)

    Args:
        df: DataFrame with all required variables
        dw: DualWriter for logging

    Returns:
        Dictionary mapping DV name to regression result dict with keys:
            - result: Full regression result from run_panel_ols
            - coef: Leverage coefficient
            - se: Leverage standard error
            - p_one_tailed: One-tailed p-value (H4: beta1 < 0)
            - significant_05: True if p < 0.05 and coef < 0
            - nobs: Number of observations
            - rsquared: R-squared
            - f_stat: F-statistic
            - f_pvalue: F-test p-value
    """
    dependent_vars = [
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct",
        "CEO_QA_Weak_Modal_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
    ]

    # Presentation control mapping (control for presentation uncertainty in QA regressions)
    pres_control_map = {
        "Manager_QA_Uncertainty_pct": "Manager_Pres_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct": "CEO_Pres_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct": "Manager_Pres_Uncertainty_pct",
        "CEO_QA_Weak_Modal_pct": "CEO_Pres_Uncertainty_pct",
        "Manager_Pres_Uncertainty_pct": None,  # No control for presentation DV
        "CEO_Pres_Uncertainty_pct": None,
    }

    # Base controls (always included)
    base_controls = [
        "analyst_qa_uncertainty",
        "firm_size",
        "tobins_q",
        "roa",
        "cash_holdings",
        "dividend_payer",
        "firm_maturity",
        "earnings_volatility",
    ]

    results: Dict[str, Any] = {}

    for dv in dependent_vars:
        if dw:
            dw.write(f"\n{'=' * 60}\n")
            dw.write(f"Running H4 regression: {dv}\n")
            dw.write(f"{'=' * 60}\n")

        # Build exog vars for this DV
        exog_vars = ["leverage_lag1"] + base_controls
        pres_control = pres_control_map.get(dv)
        if pres_control and pres_control in df.columns:
            exog_vars.append(pres_control)
            if dw:
                dw.write(f"  Including presentation control: {pres_control}\n")

        # Prepare data (drop missing for this specification)
        reg_df: pd.DataFrame = df[[dv] + exog_vars + ["gvkey", "fiscal_year"]].dropna().copy()  # type: ignore[assignment]

        if len(reg_df) == 0:
            if dw:
                dw.write(f"  WARNING: No valid observations for {dv}\n")
            results[dv] = {"error": "No valid observations"}
            continue

        if dw:
            dw.write(f"  N observations: {len(reg_df):,}\n")
            dw.write(f"  N unique firms: {reg_df['gvkey'].nunique():,}\n")

        # Run Panel OLS with Firm + Year FE, firm-clustered SE
        try:
            result = run_panel_ols(
                df=reg_df,
                dependent=dv,
                exog=exog_vars,
                entity_col="gvkey",
                time_col="fiscal_year",
                entity_effects=True,
                time_effects=True,
                cov_type="clustered",
            )

            # Extract leverage coefficient stats
            # run_panel_ols returns coefficients as DataFrame with 'Coefficient', 'Std. Error', 't-stat' columns
            coef_df = result["coefficients"]
            if "leverage_lag1" in coef_df.index:
                coef = coef_df.loc["leverage_lag1", "Coefficient"]
                se = coef_df.loc["leverage_lag1", "Std. Error"]
            else:
                coef = np.nan
                se = np.nan

            # Calculate one-tailed p-value for H4: beta1 < 0
            if not np.isnan(coef) and not np.isnan(se) and se > 0:
                df_resid = (
                    result["summary"].get("nobs", 0) - len(exog_vars) - 2
                )  # Approximate
                p_one_tailed = one_tailed_pvalue(coef, se, df_resid, alternative="less")
            else:
                p_one_tailed = np.nan

            # Store results
            results[dv] = {
                "result": result,
                "coef": float(coef) if not np.isnan(coef) else np.nan,
                "se": float(se) if not np.isnan(se) else np.nan,
                "p_one_tailed": float(p_one_tailed)
                if not np.isnan(p_one_tailed)
                else np.nan,
                "significant_05": (p_one_tailed < 0.05 and coef < 0)
                if not np.isnan(p_one_tailed)
                else False,
                "nobs": int(result["summary"]["nobs"]),
                "rsquared": float(result["summary"]["rsquared"]),
                "f_stat": result["summary"].get("f_statistic", np.nan),
                "f_pvalue": result["summary"].get("f_pvalue", np.nan),
                "exog_vars": exog_vars,
            }

            if dw:
                sig_marker = "***" if results[dv]["significant_05"] else ""
                dw.write(
                    f"  Leverage (lag1): {coef:.4f} (SE={se:.4f}, p={p_one_tailed:.3f}){sig_marker}\n"
                )
                dw.write(
                    f"  N={results[dv]['nobs']:,}, R²={results[dv]['rsquared']:.4f}\n"
                )

        except Exception as e:
            if dw:
                dw.write(f"  ERROR: {str(e)}\n")
            results[dv] = {"error": str(e)}

    return results


def save_regression_results(
    results: Dict[str, Any], output_dir: Path, dw: Any = None
) -> Optional[Path]:
    """
    Save all regression results to parquet and JSON.

    Args:
        results: Dictionary from run_all_h4_regressions
        output_dir: Output directory path
        dw: DualWriter for logging

    Returns:
        Path to saved parquet file
    """
    # Flatten results for DataFrame
    rows = []
    for dv, res in results.items():
        if "error" in res:
            rows.append(
                {
                    "dependent_var": dv,
                    "error": res.get("error"),
                    "leverage_coef": np.nan,
                    "leverage_se": np.nan,
                    "leverage_p_one_tailed": np.nan,
                    "significant_at_05": False,
                    "nobs": 0,
                    "rsquared": np.nan,
                    "f_stat": np.nan,
                    "f_pvalue": np.nan,
                }
            )
            continue

        rows.append(
            {
                "dependent_var": dv,
                "leverage_coef": res["coef"],
                "leverage_se": res["se"],
                "leverage_p_one_tailed": res["p_one_tailed"],
                "significant_at_05": res["significant_05"],
                "nobs": res["nobs"],
                "rsquared": res["rsquared"],
                "f_stat": res["f_stat"],
                "f_pvalue": res["f_pvalue"],
            }
        )

    results_df = pd.DataFrame(rows)
    results_path = output_dir / "H4_Regression_Results.parquet"
    results_df.to_parquet(results_path, index=False)

    if dw:
        dw.write(f"\nSaved regression results: {results_path}\n")

    return results_path


def generate_h4_summary(
    results: Dict[str, Any], output_dir: Path, dw: Any = None
) -> Optional[Path]:
    """
    Generate H4_RESULTS.md summary with hypothesis support table.

    Args:
        results: Dictionary from run_all_h4_regressions
        output_dir: Output directory path
        dw: DualWriter for logging

    Returns:
        Path to saved summary file
    """
    summary_lines = [
        "# H4 Regression Results: Leverage Discipline Hypothesis",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Model Specification",
        "```",
        "Speech Uncertainty_t = beta0 + beta1*Leverage_{t-1} + beta2*Analyst_Uncertainty_t",
        "                       + beta3*Presentation_Uncertainty_t + gamma*Controls_t",
        "                       + Firm_FE + Year_FE + epsilon",
        "```",
        "",
        "## Hypothesis",
        "**H4: beta1 < 0** (Higher leverage -> Lower speech uncertainty / Debt discipline effect)",
        "",
        "Test: One-tailed at alpha = 0.05",
        "",
        "## Results Summary",
        "",
        "| Dependent Variable | Leverage Coef | SE | p-value (1-tailed) | Significant | N | R² |",
        "|-------------------|---------------|-----|-------------------|-------------|-------|------|",
    ]

    sig_count = 0
    neg_count = 0  # Count negative coefficients even if not significant
    for dv, res in sorted(results.items()):
        if "error" in res:
            summary_lines.append(f"| {dv} | ERROR | - | - | - | - | - |")
            continue

        sig = "Yes" if res["significant_05"] else "No"
        if res["significant_05"]:
            sig_count += 1
        if res["coef"] < 0:
            neg_count += 1

        summary_lines.append(
            f"| {dv} | {res['coef']:.4f} | {res['se']:.4f} | {res['p_one_tailed']:.3f} | {sig} | {res['nobs']:,} | {res['rsquared']:.4f} |"
        )

    summary_lines.extend(
        [
            "",
            "## Hypothesis Support",
            "",
            f"- **Significant negative coefficients: {sig_count}/6** (p < 0.05, one-tailed)",
            f"- **Negative coefficients (all): {neg_count}/6**",
            "- H4 supported if beta1 < 0 and p < 0.05 (one-tailed)",
            "",
            "### Interpretation",
            "- If beta1 < 0 and significant: Higher leverage disciplines managers -> less vague speech",
            "- Economic magnitude: A 10pp increase in leverage -> beta1 * 10 change in uncertainty %",
            "",
            "### Economic Significance",
            "- For context, average speech uncertainty ranges from 2-8% across measures",
            "- A coefficient of -0.01 means 10pp more leverage reduces uncertainty by 0.1pp",
            "",
            "## Detailed Results",
            "",
            "See H4_Regression_Results.parquet for full coefficient tables.",
            "",
            "## Regression Diagnostics",
            "",
            "| DV | N | R² | F-stat | F-pvalue |",
            "|---|-------|------|--------|----------|",
        ]
    )

    for dv, res in sorted(results.items()):
        if "error" in res:
            summary_lines.append(f"| {dv} | ERROR | - | - | - |")
        else:
            f_str = f"{res['f_stat']:.2f}" if not np.isnan(res["f_stat"]) else "N/A"
            fp_str = (
                f"{res['f_pvalue']:.4f}" if not np.isnan(res["f_pvalue"]) else "N/A"
            )
            summary_lines.append(
                f"| {dv} | {res['nobs']:,} | {res['rsquared']:.4f} | {f_str} | {fp_str} |"
            )

    summary_path = output_dir / "H4_RESULTS.md"
    with open(summary_path, "w") as f:
        f.write("\n".join(summary_lines))

    if dw:
        dw.write(f"\nSaved summary: {summary_path}\n")

    return summary_path


def generate_latex_table(
    results: Dict[str, Any], output_dir: Path, dw: Any = None
) -> Optional[Path]:
    """
    Generate LaTeX coefficient table with 6 columns (one per DV).

    Args:
        results: Dictionary from run_all_h4_regressions
        output_dir: Output directory path
        dw: DualWriter for logging

    Returns:
        Path to saved LaTeX file
    """
    # Variable labels for display
    var_labels = {
        "leverage_lag1": "Leverage$_{t-1}$",
        "analyst_qa_uncertainty": "Analyst Uncertainty",
        "Manager_Pres_Uncertainty_pct": "Pres. Uncertainty (Mgr)",
        "CEO_Pres_Uncertainty_pct": "Pres. Uncertainty (CEO)",
        "firm_size": "Firm Size",
        "tobins_q": "Tobin's Q",
        "roa": "ROA",
        "cash_holdings": "Cash Holdings",
        "dividend_payer": "Dividend Payer",
        "firm_maturity": "Firm Maturity",
        "earnings_volatility": "Earnings Volatility",
    }

    # DV names for column headers
    dv_names = {
        "Manager_QA_Uncertainty_pct": "QA Unc.",
        "CEO_QA_Uncertainty_pct": "QA Unc.",
        "Manager_QA_Weak_Modal_pct": "Weak Modal",
        "CEO_QA_Weak_Modal_pct": "Weak Modal",
        "Manager_Pres_Uncertainty_pct": "Pres. Unc.",
        "CEO_Pres_Uncertainty_pct": "Pres. Unc.",
    }

    # Order of variables for table
    var_order = [
        "leverage_lag1",
        "analyst_qa_uncertainty",
    ]

    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(
        r"\caption{H4 Results: Leverage Discipline Effect on Speech Uncertainty}"
    )
    lines.append(r"\label{tab:h4_leverage_discipline}")
    lines.append(r"\begin{tabular}{lcccccc}")

    # Header
    lines.append(r"\toprule")
    dvs = [
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct",
        "CEO_QA_Weak_Modal_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
    ]

    lines.append(" & " + " & ".join([f"({i + 1})" for i in range(6)]) + r" \\")
    lines.append(" & " + " & ".join([f"{dv_names.get(dv, dv)}" for dv in dvs]) + r" \\")
    lines.append(r"\midrule")

    # Get all variables from first successful regression
    all_exog_vars = set()
    for res in results.values():
        if "exog_vars" in res:
            all_exog_vars.update(res["exog_vars"])
            break

    # Add presentation control to var_order if used
    presentation_used = any(
        res.get("exog_vars", []).count("Manager_Pres_Uncertainty_pct") > 0
        for res in results.values()
    )
    if presentation_used:
        var_order.append("Manager_Pres_Uncertainty_pct")

    # Then controls
    control_vars = [
        "firm_size",
        "tobins_q",
        "roa",
        "cash_holdings",
        "dividend_payer",
        "firm_maturity",
        "earnings_volatility",
    ]
    for v in control_vars:
        if v in all_exog_vars:
            var_order.append(v)

    # Coefficient rows
    for var in var_order:
        display_name = var_labels.get(var, var)
        coef_row = [display_name]
        se_row = [""]

        for dv in dvs:
            res = results.get(dv, {})
            if "error" in res or "result" not in res:
                coef_row.append("")
                se_row.append("")
                continue

            coef_df = res["result"]["coefficients"]
            if var in coef_df.index:
                beta = float(coef_df.loc[var, "Coefficient"])
                se = float(coef_df.loc[var, "Std. Error"])
                pval = float(
                    coef_df.loc[var, "t-stat"]
                )  # Use t-stat, will convert to p-value

                # Get p-value from result if available
                if (
                    hasattr(res["result"]["model"], "pvalues")
                    and var in res["result"]["model"].pvalues.index
                ):
                    pval = float(res["result"]["model"].pvalues[var])

                # Add stars
                if pval < 0.01:
                    beta_str = f"{beta:.3f}***"
                elif pval < 0.05:
                    beta_str = f"{beta:.3f}**"
                elif pval < 0.10:
                    beta_str = f"{beta:.3f}*"
                else:
                    beta_str = f"{beta:.3f}"

                coef_row.append(beta_str)
                se_row.append(f"({se:.3f})")
            else:
                coef_row.append("")
                se_row.append("")

        lines.append(" & ".join(coef_row) + r" \\")
        lines.append(" & ".join(se_row) + r" \\")

    # Stats rows
    lines.append(r"\midrule")

    # N row
    n_row = ["N"]
    for dv in dvs:
        res = results.get(dv, {})
        if "error" in res:
            n_row.append("")
        else:
            n_row.append(f"{res['nobs']:,}")
    lines.append(" & ".join(n_row) + r" \\")

    # R-squared row
    r2_row = ["R$^2$"]
    for dv in dvs:
        res = results.get(dv, {})
        if "error" in res:
            r2_row.append("")
        else:
            r2_row.append(f"{res['rsquared']:.3f}")
    lines.append(" & ".join(r2_row) + r" \\")

    # Fixed effects row
    lines.append(r"\midrule")
    lines.append("Entity FE & Yes & Yes & Yes & Yes & Yes & Yes \\")
    lines.append("Year FE & Yes & Yes & Yes & Yes & Yes & Yes \\")

    # Footer
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\begin{tablenotes}[flushleft]")
    lines.append(r"\small")
    lines.append(
        r"\item Standard errors in parentheses. *** p<0.01, ** p<0.05, * p<0.10."
    )
    lines.append(
        r"\item H4 tests whether higher leverage reduces speech uncertainty (one-tailed test)."
    )
    lines.append(r"\end{tablenotes}")
    lines.append(r"\end{table}")

    latex_path = output_dir / "H4_Coefficient_Table.tex"
    with open(latex_path, "w") as f:
        f.write("\n".join(lines))

    if dw:
        dw.write(f"\nSaved LaTeX table: {latex_path}\n")

    return latex_path


# ==============================================================================
# Path Setup
# ==============================================================================


def setup_paths(config, timestamp):
    """Set up all required paths using get_latest_output_dir"""
    root = Path(__file__).resolve().parents[4]

    # Resolve H1 variables directory (for leverage and base controls)
    h1_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H1_CashHoldings.parquet",
    )

    # Resolve H3 variables directory (for firm_maturity, earnings_volatility)
    h3_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H3_PayoutPolicy.parquet",
    )

    # Resolve speech uncertainty directory
    speech_dir = get_latest_output_dir(
        root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
        required_file="linguistic_variables_2002.parquet",  # At least one year must exist
    )

    paths = {
        "root": root,
        "h1_dir": h1_dir,
        "h3_dir": h3_dir,
        "speech_dir": speech_dir,
    }

    # Output directory
    output_base = root / "4_Outputs" / "4_Econometric_V2" / "4.4_H4_LeverageDiscipline"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "4_Econometric_V2" / "4.4_H4_LeverageDiscipline"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H4.log"

    return paths


# ==============================================================================
# Data Loading Functions
# ==============================================================================


def load_h1_variables(h1_dir, dw=None):
    """
    Load H1 Cash Holdings variables.

    Expects H1_CashHoldings.parquet with columns:
    - gvkey, fiscal_year
    - leverage (primary IV for H4)
    - Base controls: firm_size, tobins_q, roa, cash_holdings, dividend_payer
    """
    h1_file = h1_dir / "H1_CashHoldings.parquet"
    if not h1_file.exists():
        raise FileNotFoundError(f"H1_CashHoldings.parquet not found in {h1_dir}")

    validate_input_file(h1_file, must_exist=True)
    df = pd.read_parquet(h1_file)

    if dw:
        dw.write(f"  Loaded H1 variables: {len(df):,} rows\n")
        dw.write(f"    Columns: {df.columns.tolist()}\n")

    # Ensure gvkey is string and zero-padded
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    return df


def load_h3_variables(h3_dir, dw=None):
    """
    Load H3 Payout Policy variables.

    Expects H3_PayoutPolicy.parquet with columns:
    - gvkey, fiscal_year
    - Additional controls: firm_maturity, earnings_volatility
    """
    h3_file = h3_dir / "H3_PayoutPolicy.parquet"
    if not h3_file.exists():
        raise FileNotFoundError(f"H3_PayoutPolicy.parquet not found in {h3_dir}")

    validate_input_file(h3_file, must_exist=True)
    df = pd.read_parquet(h3_file)

    if dw:
        dw.write(f"  Loaded H3 variables: {len(df):,} rows\n")
        dw.write(f"    Columns: {df.columns.tolist()}\n")

    # Ensure gvkey is string and zero-padded
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    # Select only gvkey, fiscal_year, and the two H3-specific controls
    df = df[["gvkey", "fiscal_year", "firm_maturity", "earnings_volatility"]].copy()  # type: ignore[assignment]

    return df


def load_speech_uncertainty(speech_dir, uncertainty_cols, dw=None):
    """
    Load all linguistic_variables_*.parquet files and concatenate.

    Returns DataFrame with columns:
    - file_name, gvkey, start_date
    - All uncertainty measures (6 DVs + analyst uncertainty + presentation controls)
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
# Variable Preparation
# ==============================================================================


def create_lagged_leverage(df, leverage_col="leverage", group_col="gvkey", dw=None):
    """
    Create lagged leverage variable (t-1) within firm boundaries.

    Leverage at t-1 is the key independent variable for H4. We group by gvkey
    and shift leverage by 1 year to get the prior year's leverage.

    Args:
        df: DataFrame with gvkey, fiscal_year, leverage
        leverage_col: Name of leverage column
        group_col: Column to group by for lag creation (gvkey)

    Returns:
        DataFrame with new column 'leverage_lag1'
    """
    df_work = df.copy()

    # Sort by gvkey and fiscal_year for proper lagging
    df_work = df_work.sort_values([group_col, "fiscal_year"])

    # Create lagged leverage within each firm
    df_work["leverage_lag1"] = df_work.groupby(group_col)[leverage_col].shift(1)

    # Validate: Check for cross-entity leakage
    # The first observation for each firm should have NaN lag
    first_obs = df_work.groupby(group_col).head(1)
    if not first_obs["leverage_lag1"].isna().all():
        raise ValueError("Cross-entity leakage detected in lagged leverage!")

    # Check for gaps > 1 year
    df_work["year_diff"] = df_work.groupby(group_col)["fiscal_year"].diff()
    large_gaps = df_work[df_work["year_diff"] > 1]
    if not large_gaps.empty and dw:
        n_large_gaps = len(large_gaps)
        dw.write(
            f"  Warning: {n_large_gaps} observations have gaps > 1 year in fiscal_year\n"
        )

    if dw:
        before_count = len(df_work)
        after_count = df_work["leverage_lag1"].notna().sum()
        dropped = before_count - after_count
        dw.write(f"  Lagged leverage created: {after_count:,} obs with valid lag\n")
        dw.write(f"    Dropped: {dropped:,} obs (first year per firm)\n")

    return df_work


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

    # First aggregate numeric columns with mean
    numeric_cols = [c for c in uncertainty_cols if c in df.columns]
    agg_df = df.groupby(group_cols, as_index=False)[numeric_cols].mean()

    # Count calls per firm-year
    call_counts = df.groupby(group_cols, as_index=False)["file_name"].count()
    call_counts = call_counts.rename(columns={"file_name": "n_calls"})

    # Merge the aggregations
    agg_df = agg_df.merge(call_counts, on=group_cols)

    if dw:
        mean_calls = agg_df["n_calls"].mean()
        dw.write(
            f"  Aggregated to {len(agg_df):,} firm-years, mean {mean_calls:.2f} calls per firm-year\n"
        )

    return agg_df


# ==============================================================================
# Data Preparation
# ==============================================================================


def prepare_analysis_dataset(
    h1_df,
    h3_df,
    speech_agg_df,
    uncertainty_measures,
    analyst_uncertainty_var,
    vif_columns,
    vif_threshold=5.0,
    dw=None,
):
    """
    Prepare complete H4 analysis dataset by merging all data sources.

    Steps:
    1. Merge H1 with H3 on (gvkey, fiscal_year)
    2. Merge with speech uncertainty data on (gvkey, fiscal_year)
    3. Create lagged leverage (t-1)
    4. Drop observations without valid lag
    5. Run VIF diagnostics on base specification
    6. Validate variable availability

    Args:
        h1_df: H1 data with leverage and base controls
        h3_df: H3 data with firm_maturity, earnings_volatility
        speech_agg_df: Aggregated speech uncertainty by firm-year
        uncertainty_measures: List of 6 uncertainty DVs
        analyst_uncertainty_var: Name of analyst uncertainty column
        vif_columns: List of continuous variables for VIF check
        vif_threshold: VIF threshold for multicollinearity warning

    Returns:
        DataFrame with all required variables for H4 regressions
    """
    # Step 1: Merge H1 with H3
    merge_cols = ["gvkey", "fiscal_year"]
    # H3 has only firm_maturity and earnings_volatility (select columns in load_h3_variables)
    # But to be safe, handle potential duplicates with suffixes
    merged_df = h1_df.merge(h3_df, on=merge_cols, how="outer", suffixes=("", "_h3"))

    # If there were duplicates, coalesce to prefer H1 values for controls
    # (H1 has the full set of controls, H3 only adds firm_maturity and earnings_volatility)
    for col in ["firm_size", "roa", "tobins_q", "cash_holdings"]:
        if f"{col}_h3" in merged_df.columns:
            merged_df[col] = merged_df[col].fillna(merged_df[f"{col}_h3"])
            merged_df = merged_df.drop(columns=[f"{col}_h3"])

    if dw:
        h1_only = merged_df["firm_maturity"].isna() & merged_df["leverage"].notna()
        h3_only = merged_df["leverage"].isna() & merged_df["firm_maturity"].notna()
        both = merged_df["leverage"].notna() & merged_df["firm_maturity"].notna()
        dw.write(f"  After H1-H3 merge: {len(merged_df):,} obs\n")
        dw.write(
            f"    H1 only: {h1_only.sum():,}, H3 only: {h3_only.sum():,}, Both: {both.sum():,}\n"
        )

    # Step 2: Merge with speech uncertainty
    # Use suffixes to handle any duplicate column names
    before_merge = len(merged_df)
    merged_df = merged_df.merge(
        speech_agg_df, on=merge_cols, how="left", suffixes=("", "_speech")
    )

    # Coalesce any duplicated columns (prefer original values)
    for col in merged_df.columns:
        if col.endswith("_speech"):
            orig_col = col.replace("_speech", "")
            if orig_col in merged_df.columns:
                merged_df[orig_col] = merged_df[orig_col].fillna(merged_df[col])
                merged_df = merged_df.drop(columns=[col])

    if dw:
        missing_speech = merged_df[UNCERTAINTY_MEASURES[0]].isna().sum() if UNCERTAINTY_MEASURES else 0
        dw.write(
            f"  After speech merge: {len(merged_df):,} obs ({missing_speech:,} missing speech data)\n"
        )

    # Step 3: Create lagged leverage
    merged_df = create_lagged_leverage(merged_df, dw=dw)

    # Step 4: Drop observations without valid lag (first year per firm)
    merged_df = merged_df.dropna(subset=["leverage_lag1"])

    if dw:
        dw.write(f"  After dropping missing lags: {len(merged_df):,} obs\n")

    # Step 5: Select and rename variables for analysis
    # Include all uncertainty measures, analyst uncertainty, presentation controls
    core_cols = ["gvkey", "fiscal_year", "leverage", "leverage_lag1"]
    control_cols = FINANCIAL_CONTROLS.copy()

    # Build full column list (preserve order, remove duplicates)
    all_cols = (
        core_cols + control_cols + uncertainty_measures + [analyst_uncertainty_var]
    )

    # Add presentation controls that exist in data (avoid duplicates)
    presentation_cols = [
        c
        for c in PRESENTATION_CONTROL_MAP.values()
        if c is not None and c not in all_cols
    ]
    all_cols.extend(presentation_cols)

    # Add n_calls for reference
    all_cols.append("n_calls")

    # Remove any duplicates while preserving order
    seen = set()
    unique_cols = []
    for col in all_cols:
        if col not in seen:
            seen.add(col)
            unique_cols.append(col)

    # Select available columns only
    available_cols = [c for c in unique_cols if c in merged_df.columns]

    # Also check if merged_df itself has duplicate columns and deduplicate if needed
    if len(merged_df.columns) != len(set(merged_df.columns)):
        # DataFrame has duplicate columns - need to deduplicate
        # Keep first occurrence of each column
        merged_df = merged_df.loc[:, ~merged_df.columns.duplicated(keep="first")]

    analysis_df = merged_df[available_cols].copy()

    # Final check: remove any duplicate columns in analysis_df
    analysis_df = analysis_df.loc[:, ~analysis_df.columns.duplicated(keep="first")]

    # Rename analyst uncertainty to shorter name for regression
    if analyst_uncertainty_var in analysis_df.columns:
        analysis_df = analysis_df.rename(
            columns={analyst_uncertainty_var: "analyst_qa_uncertainty"}
        )

    # Step 6: VIF diagnostics on base specification
    vif_vars = [c for c in vif_columns if c in analysis_df.columns]
    if dw:
        dw.write("\n[4] Running VIF diagnostics on base specification...\n")
        dw.write(f"  Variables: {vif_vars}\n")

    try:
        vif_result = check_multicollinearity(
            analysis_df,
            vif_vars,
            vif_threshold=vif_threshold,
            condition_threshold=1000.0,
            fail_on_violation=False,  # Log warning but continue
        )

        if dw:
            dw.write(
                str(format_vif_table(vif_result["vif_results"], vif_threshold)) + "\n"
            )

            if vif_result["vif_violations"]:
                dw.write(
                    f"  WARNING: VIF violations detected: {vif_result['vif_violations']}\n"
                )
            else:
                dw.write(f"  OK: All VIF values < {vif_threshold}\n")

            if vif_result["condition_number"]:
                dw.write(f"  Condition number: {vif_result['condition_number']:.2f}\n")

    except Exception as e:
        if dw:
            dw.write(f"  VIF check failed: {e}\n")

    # Step 7: Validate variable availability
    if dw:
        dw.write("\n[5] Variable availability...\n")

        for var in uncertainty_measures:
            avail = analysis_df[var].notna().sum()
            # Convert scalar to int (handle pandas 3.x Series behavior)
            try:
                avail = int(avail.iloc[0] if hasattr(avail, "iloc") else avail)
            except (AttributeError, IndexError):
                avail = int(avail)
            total = len(analysis_df)
            pct = avail / total * 100
            dw.write(f"  {var}: {avail:,}/{total:,} ({pct:.1f}%)\n")

        for var in ["analyst_qa_uncertainty"] + FINANCIAL_CONTROLS:
            if var in analysis_df.columns:
                avail = analysis_df[var].notna().sum()
                try:
                    avail = int(avail.iloc[0] if hasattr(avail, "iloc") else avail)
                except (AttributeError, IndexError):
                    avail = int(avail)
                total = len(analysis_df)
                pct = avail / total * 100
                dw.write(f"  {var}: {avail:,}/{total:,} ({pct:.1f}%)\n")

    # Final stats
    if dw:
        dw.write("\n[6] Final analysis dataset...\n")
        dw.write(f"  N observations: {len(analysis_df):,}\n")
        dw.write(f"  N unique firms: {analysis_df['gvkey'].nunique():,}\n")
        dw.write(
            f"  Year range: {analysis_df['fiscal_year'].min()}-{analysis_df['fiscal_year'].max()}\n"
        )

    return analysis_df, vif_result if "vif_result" in locals() else None


# ==============================================================================
# Output Functions
# ==============================================================================


def save_analysis_dataset(df, output_path, dw=None):
    """Save analysis dataset to parquet file"""
    df.to_parquet(output_path, index=False)

    if dw:
        dw.write(
            f"\nSaved: {output_path.name} ({len(df):,} rows, {len(df.columns)} cols)\n"
        )

    return output_path


def save_vif_results(vif_result, output_path, dw=None):
    """Save VIF diagnostics to JSON file"""
    if vif_result is None:
        return None

    # Convert VIF DataFrame to dict for JSON serialization
    vif_dict = {
        "vif_results": vif_result["vif_results"].to_dict("records"),
        "condition_number": vif_result["condition_number"],
        "vif_violations": vif_result["vif_violations"],
        "condition_violation": vif_result["condition_violation"],
        "pass": vif_result["pass"],
    }

    with open(output_path, "w") as f:
        json.dump(vif_dict, f, indent=2, default=str)

    if dw:
        dw.write(f"Saved: {output_path.name}\n")

    return output_path


def generate_data_summary_markdown(df, vif_result, output_dir, dw=None):
    """
    Generate human-readable markdown summary of H4 data preparation.
    """
    lines = []
    lines.append("# H4 Leverage Discipline Analysis Dataset")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Hypothesis
    lines.append("## Hypothesis")
    lines.append("")
    lines.append(
        "**H4: Higher leverage disciplines managers and lowers speech uncertainty**"
    )
    lines.append("")
    lines.append("Model Specification:")
    lines.append("```")
    lines.append(
        "Uncertainty_t = beta0 + beta1*Leverage_{t-1} + beta2*Analyst_Uncertainty_t"
    )
    lines.append("                + beta3*Presentation_Uncertainty_t + gamma*Controls")
    lines.append("                + Firm FE + Year FE + epsilon")
    lines.append("```")
    lines.append("")
    lines.append("- **H4 (one-tailed):** beta1 < 0 (Leverage reduces uncertainty)")
    lines.append("")

    # Data summary
    lines.append("## Dataset Summary")
    lines.append("")
    lines.append(f"- **N observations:** {len(df):,}")
    lines.append(f"- **N unique firms:** {df['gvkey'].nunique():,}")
    lines.append(
        f"- **Year range:** {df['fiscal_year'].min()}-{df['fiscal_year'].max()}"
    )
    lines.append(f"- **Mean calls per firm-year:** {df['n_calls'].mean():.2f}")
    lines.append("")

    # Uncertainty DVs
    lines.append("## Uncertainty Dependent Variables")
    lines.append("")
    lines.append("| Measure | N Valid | % Valid | Mean | Std |")
    lines.append("|---|---|---|---|---|")

    for var in UNCERTAINTY_MEASURES:
        if var in df.columns:
            valid = df[var].notna().sum()
            pct = valid / len(df) * 100
            mean = df[var].mean()
            std = df[var].std()
            lines.append(f"| {var} | {valid:,} | {pct:.1f}% | {mean:.4f} | {std:.4f} |")

    lines.append("")

    # Key variables
    lines.append("## Key Independent Variables")
    lines.append("")
    lines.append("| Variable | N Valid | % Valid | Mean | Std | Min | Max |")
    lines.append("|---|---|---|---|---|---|---|")

    key_vars = ["leverage", "leverage_lag1", "analyst_qa_uncertainty"]
    for var in key_vars:
        if var in df.columns:
            valid = df[var].notna().sum()
            pct = valid / len(df) * 100
            mean = df[var].mean()
            std = df[var].std()
            min_val = df[var].min()
            max_val = df[var].max()
            lines.append(
                f"| {var} | {valid:,} | {pct:.1f}% | {mean:.4f} | {std:.4f} | {min_val:.4f} | {max_val:.4f} |"
            )

    lines.append("")

    # Financial controls
    lines.append("## Financial Controls")
    lines.append("")
    lines.append("| Variable | N Valid | % Valid | Mean | Std |")
    lines.append("|---|---|---|---|---|")

    for var in FINANCIAL_CONTROLS:
        if var in df.columns:
            valid = df[var].notna().sum()
            pct = valid / len(df) * 100
            mean = df[var].mean()
            std = df[var].std()
            lines.append(f"| {var} | {valid:,} | {pct:.1f}% | {mean:.4f} | {std:.4f} |")

    lines.append("")

    # VIF diagnostics
    lines.append("## VIF Diagnostics")
    lines.append("")
    lines.append("VIF thresholds: < 5 (low), 5-10 (moderate), > 10 (high)")
    lines.append("")
    lines.append("| Variable | VIF | Status |")
    lines.append("|---|---|---|")

    if vif_result and "vif_results" in vif_result:
        vif_df = vif_result["vif_results"]
        for _, row in vif_df.iterrows():
            var = row["variable"]
            vif = row["VIF"]
            exceeded = row["threshold_exceeded"]
            status = "*** EXCEEDS" if exceeded else "OK"
            lines.append(f"| {var} | {vif:.2f} | {status} |")

        if vif_result["condition_number"]:
            lines.append("")
            lines.append(f"**Condition number:** {vif_result['condition_number']:.2f}")

    lines.append("")

    # Correlation: leverage_lag1 with uncertainty measures
    lines.append("## Correlation: Lagged Leverage vs Uncertainty Measures")
    lines.append("")
    lines.append("| Uncertainty Measure | Correlation |")
    lines.append("|---|---|")

    for var in UNCERTAINTY_MEASURES:
        if var in df.columns:
            corr = df["leverage_lag1"].corr(df[var])
            lines.append(f"| {var} | {corr:.4f} |")

    lines.append("")
    lines.append("*Pearson correlation coefficients")
    lines.append("")

    # Data ready note
    lines.append("## Next Steps")
    lines.append("")
    lines.append("The analysis dataset is ready for H4 regressions. Run the regression")
    lines.append("script to estimate the following models:")
    lines.append("")
    lines.append("1. Manager_QA_Uncertainty ~ leverage_lag1 + controls + FEs")
    lines.append("2. CEO_QA_Uncertainty ~ leverage_lag1 + controls + FEs")
    lines.append("3. Manager_QA_Weak_Modal ~ leverage_lag1 + controls + FEs")
    lines.append("4. CEO_QA_Weak_Modal ~ leverage_lag1 + controls + FEs")
    lines.append("5. Manager_Pres_Uncertainty ~ leverage_lag1 + controls + FEs")
    lines.append("6. CEO_Pres_Uncertainty ~ leverage_lag1 + controls + FEs")
    lines.append("")

    output_path = output_dir / "H4_DATA_SUMMARY.md"
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    if dw:
        dw.write(f"Saved: {output_path.name}\n")

    return output_path


def save_stats_with_log(
    stats: Dict[str, Any], output_dir: Path, dw: Any = None
) -> None:
    """Save statistics dictionary to JSON file"""
    stats_path = output_dir / "stats.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2, default=str)

    if dw:
        dw.write(f"Saved: {stats_path.name}\n")


def load_existing_analysis_dataset(root, dw=None):
    """
    Load the existing H4 analysis dataset from the latest output directory.

    Args:
        root: Project root path
        dw: DualWriter for logging

    Returns:
        Tuple of (analysis_df, output_dir)
    """
    from f1d.shared.path_utils import get_latest_output_dir

    h4_dir = get_latest_output_dir(
        root / "4_Outputs" / "4_Econometric_V2" / "4.4_H4_LeverageDiscipline",
        required_file="H4_Analysis_Dataset.parquet",
    )

    analysis_file = h4_dir / "H4_Analysis_Dataset.parquet"
    if not analysis_file.exists():
        raise FileNotFoundError(f"H4_Analysis_Dataset.parquet not found in {h4_dir}")

    validate_input_file(analysis_file, must_exist=True)
    analysis_df = pd.read_parquet(analysis_file)

    if dw:
        dw.write(f"  Loaded existing analysis dataset: {len(analysis_df):,} obs\n")
        dw.write(f"    N unique firms: {analysis_df['gvkey'].nunique():,}\n")
        dw.write(f"    Source: {analysis_file}\n")

    return analysis_df, h4_dir


def update_stats_with_regressions(stats, regression_results, dw=None):
    """Update stats dictionary with regression results."""
    stats["regression_results"] = {}

    for dv, res in regression_results.items():
        if "error" in res:
            stats["regression_results"][dv] = {"error": res["error"]}
        else:
            stats["regression_results"][dv] = {
                "leverage_coef": float(res["coef"]),
                "leverage_se": float(res["se"]),
                "leverage_p_one_tailed": float(res["p_one_tailed"]),
                "significant_at_05": bool(res["significant_05"]),
                "nobs": int(res["nobs"]),
                "rsquared": float(res["rsquared"]),
                "f_stat": float(res["f_stat"]) if not np.isnan(res["f_stat"]) else None,
                "f_pvalue": float(res["f_pvalue"])
                if not np.isnan(res["f_pvalue"])
                else None,
            }

    # Count significant results
    sig_count = sum(
        1 for res in regression_results.values() if res.get("significant_05", False)
    )
    stats["hypothesis_support"] = {
        "significant_negative_count": sig_count,
        "total_regressions": len(regression_results),
        "h4_supported": sig_count > 0,
    }

    return stats


# ==============================================================================
# CLI and Main
# ==============================================================================


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="H4 Leverage Discipline - Data preparation and regression execution for reverse causal test"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and setup without running data preparation",
    )
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Run data preparation only (skip regression execution)",
    )
    parser.add_argument(
        "--regressions-only",
        action="store_true",
        help="Skip data preparation, run regressions on existing analysis dataset",
    )
    return parser.parse_args()


def main():
    """Main execution function"""
    args = parse_args()

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # Load config
    config = load_config()

    # Get project root
    root = Path(__file__).resolve().parents[4]

    # Initialize stats
    stats: Dict[str, Any] = {
        "step_id": "4.4_H4_LeverageDiscipline",
        "timestamp": timestamp,
        "git_sha": get_git_sha(),
        "input": {},
        "processing": {},
        "output": {},
        "vif_diagnostics": {},
        "variable_availability": {},
        "timing": {},
        "memory": {},
    }

    # Track if we're doing regressions
    run_regressions = not args.prepare_only

    # --regressions-only mode: load existing dataset
    if args.regressions_only:
        # Setup minimal paths for logging (reuse existing output directory)
        from f1d.shared.path_utils import get_latest_output_dir

        existing_dir = get_latest_output_dir(
            root / "4_Outputs" / "4_Econometric_V2" / "4.4_H4_LeverageDiscipline",
            required_file="H4_Analysis_Dataset.parquet",
        )

        # Use timestamp for new outputs
        output_base = (
            root / "4_Outputs" / "4_Econometric_V2" / "4.4_H4_LeverageDiscipline"
        )
        output_dir = output_base / timestamp
        ensure_output_dir(output_dir)

        # Log directory
        log_base = root / "3_Logs" / "4_Econometric_V2" / "4.4_H4_LeverageDiscipline"
        ensure_output_dir(log_base)
        log_file = log_base / f"{timestamp}_H4.log"

        # Initialize DualWriter
        dw = DualWriter(log_file)

        # Script header
        dw.write("=" * 80 + "\n")
        dw.write("STEP 4.4: H4 Leverage Discipline Regression Execution\n")
        dw.write("=" * 80 + "\n")
        dw.write(f"Timestamp: {timestamp}\n")
        dw.write(f"Git SHA: {get_git_sha()}\n")
        dw.write("Mode: --regressions-only (using existing dataset)\n")
        dw.write("")

        # Load existing analysis dataset
        dw.write("[Loading existing analysis dataset]\n")
        analysis_df, _ = load_existing_analysis_dataset(root, dw)

        vif_result = None  # Will load from existing stats if needed
        stats["processing"]["analysis_dataset"] = {
            "n_obs": int(len(analysis_df)),
            "n_firms": int(analysis_df["gvkey"].nunique()),
            "year_range": [
                int(analysis_df["fiscal_year"].min()),
                int(analysis_df["fiscal_year"].max()),
            ],
        }

        # Initialize timing for regression-only mode
        start_time = time.time()
        start_mem = get_process_memory_mb()

    else:
        # Normal mode: setup paths
        paths = setup_paths(config, timestamp)

        # Initialize DualWriter for logging
        dw = DualWriter(paths["log_file"])

        # Script header
        dw.write("=" * 80 + "\n")
        dw.write("STEP 4.4: H4 Leverage Discipline Data Preparation")
        if run_regressions:
            dw.write(" + Regression Execution\n")
        else:
            dw.write("\n")
        dw.write("=" * 80 + "\n")
        dw.write(f"Timestamp: {timestamp}\n")
        dw.write(f"Git SHA: {get_git_sha()}\n")
        dw.write(f"Config: {config.get('step_id', '4.4_H4_LeverageDiscipline')}\n")
        dw.write("")

        # For normal mode, set output_dir for later use
        output_dir = paths["output_dir"]

        start_time = time.time()
        start_mem = get_process_memory_mb()

        # Data preparation flow
        try:
            # Build list of all speech columns we need
            speech_cols = UNCERTAINTY_MEASURES + [ANALYST_UNCERTAINTY_VAR]
            speech_cols.extend(
                [c for c in PRESENTATION_CONTROL_MAP.values() if c is not None]
            )

            # Load H1 variables
            dw.write("\n[1] Loading H1 variables (leverage + base controls)...\n")
            h1_df = load_h1_variables(paths["h1_dir"], dw)

            stats["input"]["h1_variables"] = {
                "rows": int(len(h1_df)),
                "source": str(paths["h1_dir"]),
            }

            # Load H3 variables
            dw.write(
                "\n[2] Loading H3 variables (firm_maturity, earnings_volatility)...\n"
            )
            h3_df = load_h3_variables(paths["h3_dir"], dw)

            stats["input"]["h3_variables"] = {
                "rows": int(len(h3_df)),
                "source": str(paths["h3_dir"]),
            }

            # Load speech uncertainty
            dw.write("\n[3] Loading speech uncertainty data...\n")
            speech_df = load_speech_uncertainty(paths["speech_dir"], speech_cols, dw)

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
            speech_agg = aggregate_speech_to_firmyear(speech_df, speech_cols, dw)

            stats["processing"]["aggregation"] = {
                "firm_years": int(len(speech_agg)),
            }

            # Prepare analysis dataset
            dw.write("\n[5] Preparing H4 analysis dataset...\n")
            analysis_df, vif_result = prepare_analysis_dataset(
                h1_df,
                h3_df,
                speech_agg,
                UNCERTAINTY_MEASURES,
                ANALYST_UNCERTAINTY_VAR,
                VIF_COLUMNS,
                vif_threshold=5.0,
                dw=dw,
            )

            stats["processing"]["analysis_dataset"] = {
                "n_obs": int(len(analysis_df)),
                "n_firms": int(analysis_df["gvkey"].nunique()),
                "year_range": [
                    int(analysis_df["fiscal_year"].min()),
                    int(analysis_df["fiscal_year"].max()),
                ],
            }

            # VIF diagnostics
            if vif_result:
                stats["vif_diagnostics"] = {
                    "condition_number": vif_result["condition_number"],
                    "vif_violations": vif_result["vif_violations"],
                    "pass": vif_result["pass"],
                    "vif_values": {
                        row["variable"]: row["VIF"]
                        for _, row in vif_result["vif_results"].iterrows()
                    },
                }

            # Variable availability
            for var in (
                UNCERTAINTY_MEASURES + ["analyst_qa_uncertainty"] + FINANCIAL_CONTROLS
            ):
                if var in analysis_df.columns:
                    n_valid = analysis_df[var].notna().sum()
                    # Convert scalar to int (handle pandas 3.x Series behavior)
                    try:
                        n_valid = int(
                            n_valid.iloc[0] if hasattr(n_valid, "iloc") else n_valid
                        )
                    except (AttributeError, IndexError):
                        n_valid = int(n_valid)
                    pct_valid = float(n_valid / len(analysis_df) * 100)
                    stats["variable_availability"][var] = {
                        "n_valid": n_valid,
                        "pct_valid": pct_valid,
                    }

            # Save outputs
            dw.write("\n[6] Saving outputs...\n")
            save_analysis_dataset(
                analysis_df, output_dir / "H4_Analysis_Dataset.parquet", dw
            )
            save_vif_results(vif_result, output_dir / "vif_diagnostics.json", dw)
            generate_data_summary_markdown(analysis_df, vif_result, output_dir, dw)

            stats["output"]["analysis_dataset"] = {
                "file": "H4_Analysis_Dataset.parquet",
                "rows": int(len(analysis_df)),
                "columns": len(analysis_df.columns),
            }

        except Exception as e:
            dw.write(f"\nERROR in data preparation: {e}\n")
            import traceback

            dw.write(traceback.format_exc())
            raise

    # Common: regression execution (unless --prepare-only)
    try:
        if run_regressions:
            if not args.regressions_only:
                # If we just did data prep, update timing stats
                end_prep_time = time.time()
                dw.write(
                    f"\n[Data prep completed in {end_prep_time - start_time:.2f} seconds]\n"
                )

            dw.write("\n" + "=" * 80 + "\n")
            dw.write("H4 REGRESSION EXECUTION\n")
            dw.write("=" * 80 + "\n")

            # Run all 6 H4 regressions
            regression_results = run_all_h4_regressions(analysis_df, dw)

            # Save regression results
            dw.write("\n[Saving regression outputs]\n")
            save_regression_results(regression_results, output_dir, dw)
            generate_h4_summary(regression_results, output_dir, dw)
            generate_latex_table(regression_results, output_dir, dw)

            # Update stats with regression results
            stats = update_stats_with_regressions(stats, regression_results, dw)

            # Summary stats
            sig_count = stats["hypothesis_support"]["significant_negative_count"]
            dw.write("\n[H4 Hypothesis Summary]\n")
            dw.write(f"  Significant negative coefficients: {sig_count}/6\n")
            if sig_count > 0:
                dw.write(
                    "  H4 SUPPORTED: Leverage disciplines managers, reducing speech uncertainty\n"
                )
            else:
                dw.write(
                    "  H4 NOT SUPPORTED: No significant negative relationship found\n"
                )

        # Final stats
        end_time = time.time()
        end_mem = get_process_memory_mb()

        stats["timing"]["duration_seconds"] = end_time - start_time
        stats["memory"]["rss_mb_start"] = start_mem["rss_mb"]
        stats["memory"]["rss_mb_end"] = end_mem["rss_mb"]

        save_stats_with_log(stats, output_dir, dw)

        # Summary
        dw.write("\n" + "=" * 80 + "\n")
        dw.write("EXECUTION SUMMARY\n")
        dw.write("=" * 80 + "\n")
        dw.write(f"  Duration: {stats['timing']['duration_seconds']:.2f} seconds\n")
        dw.write(
            f"  Analysis dataset: {len(analysis_df):,} obs, {analysis_df['gvkey'].nunique():,} firms\n"
        )
        dw.write(f"  Output directory: {output_dir}\n")

        if "hypothesis_support" in stats:
            sig_count = stats["hypothesis_support"]["significant_negative_count"]
            dw.write(f"  H4 support: {sig_count}/6 measures significant at p<0.05\n")

        if "vif_result" in locals() and vif_result:
            vif_pass = "PASS" if vif_result["pass"] else "WARNING"
            dw.write(f"  VIF check: {vif_pass}\n")
            if vif_result["vif_violations"]:
                dw.write(f"    Violations: {vif_result['vif_violations']}\n")

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
