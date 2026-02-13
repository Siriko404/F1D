#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Reporting Utilities
================================================================================
ID: shared/reporting_utils
Description: Provides markdown report generation and diagnostic saving for
             regression results. Creates human-readable reports and machine-
             readable CSV outputs.

Inputs:
    - Fitted statsmodels model
    - Sample name for report title
    - Output directory path (pathlib.Path)
    - Regression formula (optional)

Outputs:
    - Markdown report with regression summary and coefficient table
    - CSV file with model diagnostics
    - CSV file with variable reference table

Deterministic: true
Main Functions:
    - generate_report(): Generate markdown report from results

Dependencies:
    - Utility module for reporting
    - Uses: pandas, pathlib

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

from pathlib import Path

import pandas as pd


def generate_regression_report(
    model, sample_name: str, output_dir: Path, formula: str = None
) -> Path:
    """
    Generate markdown report for regression results.

    Args:
        model: Fitted statsmodels model
        sample_name: Name of sample for report title
        output_dir: Directory to save report
        formula: Regression formula (optional)

    Returns:
        Path to generated markdown report
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / f"regression_results_{sample_name}.md"

    with open(report_path, "w") as f:
        f.write(f"# Regression Results: {sample_name}\n\n")

        if formula:
            f.write(f"**Formula:** `{formula}`\n\n")

        f.write("## Model Summary\n\n")
        f.write("```\n")
        f.write(str(model.summary()))
        f.write("\n```\n\n")

        f.write("## Coefficient Table\n\n")
        f.write("| Variable | Coef | Std Err | t | P>|t| | [0.025 | 0.975] |\n")
        f.write("|----------|------|---------|---|--------|----------|\n")

        for idx, row in model.summary2().tables[1].iterrows():
            f.write(f"| {idx} | {row['Coef.']:.4f} | {row['Std.Err.']:.4f} | ")
            f.write(f"{row['t']:.4f} | {row['P>|z|']:.4f} | ")
            f.write(f"{row['[0.025']:.4f} | {row['0.975']:.4f} |\n")

    return report_path


def save_model_diagnostics(model, sample_name: str, output_dir: Path) -> Path:
    """
    Save regression diagnostics to CSV.

    Args:
        model: Fitted statsmodels model
        sample_name: Name of sample
        output_dir: Directory to save CSV

    Returns:
        Path to saved diagnostics CSV
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    diag_path = output_dir / "model_diagnostics.csv"

    import numpy as np

    diagnostics = {
        "sample": sample_name,
        "n_obs": int(model.nobs),
        "rsquared": float(model.rsquared),
        "rsquared_adj": float(model.rsquared_adj),
        "aic": float(model.aic),
        "bic": float(model.bic),
        "f_statistic": float(model.fvalue) if hasattr(model, "fvalue") else np.nan,
        "condno": float(model.condition_number),
    }

    diag_df = pd.DataFrame([diagnostics])
    diag_df.to_csv(diag_path, index=False)

    return diag_path


def save_variable_reference(
    df: pd.DataFrame, sample_name: str, output_dir: Path
) -> Path:
    """
    Save variable reference table (name, dtype, non_null_count).

    Args:
        df: DataFrame with regression data
        sample_name: Name of sample
        output_dir: Directory to save CSV

    Returns:
        Path to saved variable reference CSV
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ref_path = output_dir / "variable_reference.csv"

    ref_df = pd.DataFrame(
        {
            "variable": df.columns,
            "dtype": df.dtypes.astype(str),
            "non_null_count": df.count(),
            "null_count": df.isnull().sum(),
        }
    )

    ref_df.to_csv(ref_path, index=False)

    return ref_path
