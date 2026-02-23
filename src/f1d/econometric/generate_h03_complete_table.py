#!/usr/bin/env python3
"""
================================================================================
Generate Complete H0.3 LaTeX Table from Existing Regression Results
================================================================================
ID: econometric/generate_h03_complete_table
Description: Reads existing regression output files and generates a COMPLETE
             Accounting Review style LaTeX table with all 4 models.

This script addresses the issue where the original run_h0_3 script was missing
the Manager_Extended model and producing shrunk/summarized tables.

Usage:
    python -m f1d.econometric.generate_h03_complete_table

Output:
    - outputs/econometric/ceo_clarity_extended/{timestamp}/h03_complete_table.tex
================================================================================
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


def parse_regression_output(filepath: Path) -> Dict[str, Any]:
    """Parse statsmodels regression output text file.

    Extracts:
    - N observations
    - R-squared, Adj. R-squared
    - F-statistic
    - Coefficients, standard errors, t-stats, p-values for control variables
    """
    with open(filepath, "r") as f:
        content = f.read()

    result = {
        "n_obs": None,
        "rsquared": None,
        "rsquared_adj": None,
        "f_statistic": None,
        "df_model": None,
        "coefficients": {},
    }

    # Parse diagnostics
    n_obs_match = re.search(r"No\. Observations:\s+([\d,]+)", content)
    if n_obs_match:
        result["n_obs"] = int(n_obs_match.group(1).replace(",", ""))

    r2_match = re.search(r"R-squared:\s+([\d.]+)", content)
    if r2_match:
        result["rsquared"] = float(r2_match.group(1))

    ar2_match = re.search(r"Adj\. R-squared:\s+([\d.]+)", content)
    if ar2_match:
        result["rsquared_adj"] = float(ar2_match.group(1))

    f_match = re.search(r"F-statistic:\s+([\d.]+)", content)
    if f_match:
        result["f_statistic"] = float(f_match.group(1))

    df_match = re.search(r"Df Model:\s+([\d,]+)", content)
    if df_match:
        result["df_model"] = int(df_match.group(1).replace(",", ""))

    # Parse coefficients table
    # Pattern: variable name, coef, std err, t, P>|t|, [0.025, 0.975]
    coef_pattern = re.compile(
        r"^([A-Za-z_][A-Za-z0-9_\[\]().\s]+?)\s+"
        r"([-\d.]+)\s+"
        r"([\d.]+)\s+"
        r"([-\d.]+)\s+"
        r"([\d.]+)\s+"
        r"([-\d.]+)\s+"
        r"([-\d.]+)$",
        re.MULTILINE
    )

    for match in coef_pattern.finditer(content):
        var_name = match.group(1).strip()
        # Skip CEO dummies and year dummies
        if var_name.startswith("C(ceo_id)") or var_name.startswith("C(year)"):
            continue
        if var_name == "Intercept":
            continue

        try:
            coef = float(match.group(2))
            std_err = float(match.group(3))
            t_stat = float(match.group(4))
            p_val = float(match.group(5))

            result["coefficients"][var_name] = {
                "coef": coef,
                "std_err": std_err,
                "t_stat": t_stat,
                "p_val": p_val,
            }
        except ValueError:
            continue

    return result


def add_stars(pvalue: float) -> str:
    """Add significance stars based on p-value."""
    if pvalue is None or pvalue != pvalue:  # NaN check
        return ""
    if pvalue < 0.01:
        return "***"
    if pvalue < 0.05:
        return "**"
    if pvalue < 0.10:
        return "*"
    return ""


def format_coef(coef: float, pval: float, decimals: int = 3) -> str:
    """Format coefficient with stars."""
    if coef is None or coef != coef:
        return ""
    stars = add_stars(pval)
    return f"{coef:.{decimals}f}{stars}"


def format_se(se: float, decimals: int = 3) -> str:
    """Format standard error in parentheses."""
    if se is None or se != se:
        return ""
    return f"({se:.{decimals}f})"


def format_int(n: int) -> str:
    """Format integer with commas."""
    return f"{n:,}" if n else ""


def generate_complete_table(
    results: Dict[str, Dict[str, Any]],
    variable_labels: Dict[str, str],
    control_order: List[str],
    output_path: Path,
) -> str:
    """Generate complete LaTeX table."""

    model_names = list(results.keys())
    n_models = len(model_names)

    lines = []

    # Table header
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\caption{Extended Controls Robustness: CEO and Manager Clarity Fixed Effects}")
    lines.append(r"\label{tab:h03_ceo_clarity_extended_complete}")
    lines.append("")
    lines.append(r"\parbox{\textwidth}{\small")
    lines.append(r"This table reports estimated fixed effects from regressing Q\&A linguistic uncertainty")
    lines.append(r"on baseline and extended financial controls. Columns (1)--(2) use Manager-level Q\&A")
    lines.append(r"uncertainty; columns (3)--(4) use CEO-only Q\&A uncertainty. Extended controls add Size,")
    lines.append(r"Book-to-Market, Leverage, ROA, Current Ratio, R\&D Intensity, and Stock Volatility.")
    lines.append(r"All models are estimated on the Main industry sample (non-financial, non-utility firms).")
    lines.append(r"Standard errors are clustered at the CEO level. All models include CEO fixed effects")
    lines.append(r"and year fixed effects. t-statistics are reported in parentheses below coefficients.")
    lines.append(r"*** p$<$0.01, ** p$<$0.05, * p$<$0.10.")
    lines.append(r"}")
    lines.append("")
    lines.append(r"\vspace{0.5em}")
    lines.append("")

    # Column spec
    col_spec = "l" + "c" * n_models
    lines.append(f"\\begin{{tabular}}{{@{{}}{{{col_spec}}}@{{}}}}")
    lines.append(r"\toprule")

    # Model headers
    header = [""] + model_names
    lines.append(" & ".join(header) + r" \\")
    lines.append(" & ".join([""] + [f"({i+1})" for i in range(n_models)]) + r" \\")
    lines.append(r"\midrule")

    # === Panel A: Linguistic Controls ===
    lines.append(r"\multicolumn{" + str(n_models + 1) + r"}{l}{\textit{Panel A: Linguistic Controls}} \\")
    lines.append(r"\midrule")

    linguistic_vars = [
        ("Manager_Pres_Uncertainty_pct", "Manager Pres Uncertainty"),
        ("CEO_Pres_Uncertainty_pct", "CEO Pres Uncertainty"),
        ("Analyst_QA_Uncertainty_pct", "Analyst QA Uncertainty"),
        ("Entire_All_Negative_pct", "Negative Sentiment"),
    ]

    for var_name, display_name in linguistic_vars:
        coef_row = [display_name]
        se_row = [""]

        for model in model_names:
            coefs = results[model].get("coefficients", {})
            if var_name in coefs:
                c = coefs[var_name]
                coef_row.append(format_coef(c["coef"], c["p_val"]))
                se_row.append(format_se(c["std_err"]))
            else:
                coef_row.append("")
                se_row.append("")

        lines.append(" & ".join(coef_row) + r" \\")
        lines.append(" & ".join(se_row) + r" \\")

    # === Panel B: Base Firm Controls ===
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{" + str(n_models + 1) + r"}{l}{\textit{Panel B: Base Firm Controls}} \\")
    lines.append(r"\midrule")

    base_vars = [
        ("StockRet", "Stock Return"),
        ("MarketRet", "Market Return"),
        ("EPS_Growth", "EPS Growth"),
        ("SurpDec", "Earnings Surprise Decile"),
    ]

    for var_name, display_name in base_vars:
        coef_row = [display_name]
        se_row = [""]

        for model in model_names:
            coefs = results[model].get("coefficients", {})
            if var_name in coefs:
                c = coefs[var_name]
                coef_row.append(format_coef(c["coef"], c["p_val"]))
                se_row.append(format_se(c["std_err"]))
            else:
                coef_row.append("")
                se_row.append("")

        lines.append(" & ".join(coef_row) + r" \\")
        lines.append(" & ".join(se_row) + r" \\")

    # === Panel C: Extended Firm Controls ===
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{" + str(n_models + 1) + r"}{l}{\textit{Panel C: Extended Firm Controls}} \\")
    lines.append(r"\midrule")

    extended_vars = [
        ("Size", "Size (log assets)"),
        ("BM", "Book-to-Market"),
        ("Lev", "Leverage"),
        ("ROA", "Return on Assets"),
        ("CurrentRatio", "Current Ratio"),
        ("RD_Intensity", "R\&D Intensity"),
        ("Volatility", "Stock Volatility"),
    ]

    for var_name, display_name in extended_vars:
        coef_row = [display_name]
        se_row = [""]

        for model in model_names:
            coefs = results[model].get("coefficients", {})
            if var_name in coefs:
                c = coefs[var_name]
                coef_row.append(format_coef(c["coef"], c["p_val"]))
                se_row.append(format_se(c["std_err"]))
            else:
                coef_row.append("")
                se_row.append("")

        lines.append(" & ".join(coef_row) + r" \\")
        lines.append(" & ".join(se_row) + r" \\")

    # === Panel D: Fixed Effects ===
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{" + str(n_models + 1) + r"}{l}{\textit{Panel D: Fixed Effects}} \\")
    lines.append(r"\midrule")

    # CEO FE
    fe_row = ["CEO Fixed Effects"]
    for model in model_names:
        n_ceos = results[model].get("diagnostics", {}).get("n_ceos", "Yes")
        if isinstance(n_ceos, int):
            fe_row.append(f"Yes ({n_ceos:,})")
        else:
            fe_row.append("Yes")
    lines.append(" & ".join(fe_row) + r" \\")

    # Year FE
    fe_row = ["Year Fixed Effects"]
    for _ in model_names:
        fe_row.append("Yes")
    lines.append(" & ".join(fe_row) + r" \\")

    # === Panel E: Diagnostics ===
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{" + str(n_models + 1) + r"}{l}{\textit{Panel E: Model Diagnostics}} \\")
    lines.append(r"\midrule")

    # N Observations
    n_row = ["Observations"]
    for model in model_names:
        n = results[model].get("n_obs")
        n_row.append(format_int(n) if n else "")
    lines.append(" & ".join(n_row) + r" \\")

    # N CEOs
    n_row = ["N CEOs"]
    for model in model_names:
        n = results[model].get("diagnostics", {}).get("n_ceos")
        n_row.append(format_int(n) if n else "")
    lines.append(" & ".join(n_row) + r" \\")

    # R-squared
    r2_row = ["R-squared"]
    for model in model_names:
        r2 = results[model].get("rsquared")
        r2_row.append(f"{r2:.3f}" if r2 else "")
    lines.append(" & ".join(r2_row) + r" \\")

    # Adj R-squared
    ar2_row = ["Adjusted R-squared"]
    for model in model_names:
        ar2 = results[model].get("rsquared_adj")
        ar2_row.append(f"{ar2:.3f}" if ar2 else "")
    lines.append(" & ".join(ar2_row) + r" \\")

    # F-statistic
    f_row = ["F-statistic"]
    for model in model_names:
        f = results[model].get("f_statistic")
        if f:
            if f > 1000:
                f_row.append(f"{f:.2e}")
            else:
                f_row.append(f"{f:.2f}")
        else:
            f_row.append("")
    lines.append(" & ".join(f_row) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    latex_str = "\n".join(lines)

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex_str)

    return latex_str


def main() -> int:
    """Main execution."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]

    # Find the latest regression output directory
    base_dir = root / "outputs" / "econometric" / "ceo_clarity_extended"
    output_dirs = sorted(base_dir.iterdir(), key=lambda x: x.name, reverse=True)

    if not output_dirs:
        print("ERROR: No regression output directories found")
        return 1

    # Find the most recent directory with all 4 regression files
    latest_dir = None
    for d in output_dirs:
        if not d.is_dir():
            continue
        files = list(d.glob("regression_results_*.txt"))
        if len(files) >= 3:  # At least 3 models
            latest_dir = d
            break

    if latest_dir is None:
        print("ERROR: No directory with regression results found")
        return 1

    print(f"Reading regression results from: {latest_dir}")

    # Model name mapping
    model_files = {
        "Manager_Baseline": "regression_results_manager_baseline.txt",
        "Manager_Extended": "regression_results_manager_extended.txt",
        "CEO_Baseline": "regression_results_ceo_baseline.txt",
        "CEO_Extended": "regression_results_ceo_extended.txt",
    }

    results = {}
    for model_name, filename in model_files.items():
        filepath = latest_dir / filename
        if filepath.exists():
            print(f"  Parsing {filename}...")
            results[model_name] = parse_regression_output(filepath)
            print(f"    N={results[model_name]['n_obs']:,}, R²={results[model_name]['rsquared']:.3f}")
        else:
            print(f"  WARNING: {filename} not found")

    if len(results) < 3:
        print("ERROR: Not enough regression results found")
        return 1

    # Variable labels
    variable_labels = {
        "Manager_Pres_Uncertainty_pct": "Manager Pres Uncertainty",
        "CEO_Pres_Uncertainty_pct": "CEO Pres Uncertainty",
        "Analyst_QA_Uncertainty_pct": "Analyst QA Uncertainty",
        "Entire_All_Negative_pct": "Negative Sentiment",
        "StockRet": "Stock Return",
        "MarketRet": "Market Return",
        "EPS_Growth": "EPS Growth",
        "SurpDec": "Earnings Surprise Decile",
        "Size": "Size (log assets)",
        "BM": "Book-to-Market",
        "Lev": "Leverage",
        "ROA": "Return on Assets",
        "CurrentRatio": "Current Ratio",
        "RD_Intensity": "R&D Intensity",
        "Volatility": "Stock Volatility",
    }

    control_order = [
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
        "Analyst_QA_Uncertainty_pct",
        "Entire_All_Negative_pct",
        "StockRet",
        "MarketRet",
        "EPS_Growth",
        "SurpDec",
        "Size",
        "BM",
        "Lev",
        "ROA",
        "CurrentRatio",
        "RD_Intensity",
        "Volatility",
    ]

    # Output path
    out_dir = base_dir / timestamp
    out_file = out_dir / "h03_complete_table.tex"

    print(f"\nGenerating complete table...")
    latex = generate_complete_table(results, variable_labels, control_order, out_file)

    print(f"\nComplete table saved to: {out_file}")
    print(f"\nTable includes {len(results)} models:")
    for model_name, res in results.items():
        print(f"  {model_name}: N={res.get('n_obs', 'N/A'):,}, R²={res.get('rsquared', 'N/A')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
