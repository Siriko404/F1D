#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: LaTeX Table Generation
================================================================================
ID: shared/latex_tables
Description: Publication-ready LaTeX regression table generation using booktabs
             three-line format. Supports multi-model tables with significance
             stars, standard errors, and customizable formatting.

Inputs:
    - List of regression result dictionaries
    - Model names for column headers
    - Optional variable ordering and labels

Outputs:
    - LaTeX string ready for .tex file
    - Optionally writes to file

Deterministic: true
Dependencies:
    - Utility module for LaTeX table generation
    - Uses: pandas

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def format_coefficient(
    beta: float, se: float, pvalue: float, decimals: int = 3, show_stars: bool = True
) -> Tuple[str, str]:
    """Format coefficient with significance stars and standard error.

    Args:
        beta: Coefficient estimate
        se: Standard error
        pvalue: P-value for significance testing
        decimals: Number of decimal places for formatting
        show_stars: If True, add significance stars to coefficient

    Returns:
        Tuple of (formatted beta with stars, formatted SE in parentheses)
        Example: ("0.123***", "(0.045)")

    Significance levels:
        *** p < 0.01
        **  p < 0.05
        *   p < 0.10
    """
    # Format coefficient
    beta_str = f"{beta:.{decimals}f}"

    # Add stars if requested
    if show_stars:
        if pvalue < 0.01:
            beta_str += "***"
        elif pvalue < 0.05:
            beta_str += "**"
        elif pvalue < 0.10:
            beta_str += "*"

    # Format standard error in parentheses
    se_str = f"({se:.{decimals}f})"

    return beta_str, se_str


def _get_significance_note() -> str:
    """Get standard significance note for table footer.

    Returns:
        LaTeX-formatted significance note string
    """
    return (
        r"\item Note: Standard errors in parentheses. *** p<0.01, ** p<0.05, * p<0.10."
    )


def _format_number(value: Any, decimals: int = 2, format_type: str = "decimal") -> str:
    """Format a number for LaTeX table display.

    Args:
        value: Value to format (int, float, or None)
        decimals: Number of decimal places
        format_type: 'decimal' for floats, 'integer' for integers with comma separators

    Returns:
        Formatted string
    """
    if value is None:
        return ""

    if format_type == "integer":
        # Format with comma separators (e.g., 1,234)
        return f"{int(value):,}"
    else:
        return f"{float(value):.{decimals}f}"


def make_regression_table(
    results: List[Dict[str, Any]],
    model_names: List[str],
    variable_order: Optional[List[str]] = None,
    variable_labels: Optional[Dict[str, str]] = None,
    include_stats: List[str] = None,
    caption: str = "",
    label: str = "",
    output_path: Optional[Path] = None,
    decimals: int = 3,
    dep_var_name: str = "",
    include_fe_rows: bool = True,
) -> str:
    """Generate publication-ready LaTeX regression table.

    Creates a booktabs-formatted LaTeX table with multiple model columns.
    Standard errors appear in parentheses below coefficients.

    Args:
        results: List of regression result dictionaries. Each dict should contain:
            - 'coefficients': DataFrame with columns 'coefficient', 'std_error', 'p_value'
            - 'summary': Dict with 'n_obs', 'rsquared', etc.
        model_names: Column headers for each model
        variable_order: Optional list specifying row order. If None, uses coefficient order.
        variable_labels: Optional dict mapping variable names to display names
                        Example: {'vagueness_c': 'Speech Uncertainty', 'leverage_c': 'Leverage'}
        include_stats: List of statistics to include: 'N', 'R2', 'adj_R2', 'F', 'FE_entity', 'FE_time'
        caption: Table caption for LaTeX
        label: Table label for LaTeX cross-referencing
        output_path: If provided, write LaTeX to this file
        decimals: Number of decimal places for coefficients
        dep_var_name: Name of dependent variable for display
        include_fe_rows: If True, include fixed effects rows if data available

    Returns:
        LaTeX string ready for .tex file

    Example:
        >>> latex = make_regression_table(
        ...     results=[result1, result2, result3],
        ...     model_names=['OLS', 'Fixed Effects', '2SLS'],
        ...     variable_labels={'vagueness': 'Speech Uncertainty'},
        ...     caption='Effect of Managerial Vagueness on Cash Holdings',
        ...     label='tab:vagueness_cash'
        ... )
    """
    if include_stats is None:
        include_stats = ["N", "R2", "F"]
    if variable_labels is None:
        variable_labels = {}

    n_models = len(results)

    # Collect all variable names across models
    all_vars = []
    for r in results:
        if "coefficients" in r:
            vars_in_model = r["coefficients"]["variable"].tolist()
            for var in vars_in_model:
                if var not in all_vars:
                    all_vars.append(var)

    # Use specified order or default order
    if variable_order:
        # Put ordered variables first, then others
        ordered_vars = [v for v in variable_order if v in all_vars]
        remaining_vars = [v for v in all_vars if v not in variable_order]
        display_vars = ordered_vars + remaining_vars
    else:
        display_vars = all_vars

    # Filter out constant from display (typically shown separately or not at all)
    display_vars = [v for v in display_vars if v != "const"]

    # Build LaTeX table
    lines = []

    # Table header
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")

    if caption:
        lines.append(f"\\caption{{{caption}}}")
    if label:
        lines.append(f"\\label{{{label}}}")

    # Column specification: left column for variables, then one per model
    col_spec = "l" + "c" * n_models
    lines.append(f"\\begin{{tabular}}{{{col_spec}}}")

    # Top rule
    lines.append(r"\toprule")

    # Model number row
    lines.append("& " + " & ".join([f"({i + 1})" for i in range(n_models)]) + r" \\")
    # Model name row
    lines.append("& " + " & ".join(model_names) + r" \\")
    # Midrule
    lines.append(r"\midrule")

    # Dependent variable row (if specified)
    if dep_var_name:
        lines.append(
            f"\\multicolumn{{{n_models + 1}}}{{l}}{{\\textit{{Dependent variable: {dep_var_name}}}}} \\\\"
        )
        lines.append(r"\midrule")

    # Coefficient rows
    for var in display_vars:
        display_name = variable_labels.get(var, var)
        coef_row = [display_name]
        se_row = [""]

        for _i, r in enumerate(results):
            coef_df = r.get("coefficients")
            if coef_df is not None:
                var_rows = coef_df[coef_df["variable"] == var]
                if len(var_rows) > 0:
                    row = var_rows.iloc[0]
                    beta, se = format_coefficient(
                        row["coefficient"],
                        row["std_error"],
                        row["p_value"],
                        decimals=decimals,
                    )
                    coef_row.append(beta)
                    se_row.append(se)
                else:
                    coef_row.append("")
                    se_row.append("")
            else:
                coef_row.append("")
                se_row.append("")

        lines.append(" & ".join(coef_row) + r" \\")
        lines.append(" & ".join(se_row) + r" \\")

    # Midrule before statistics
    lines.append(r"\midrule")

    # Statistics rows
    for stat in include_stats:
        if stat == "N":
            row = ["Observations"]
            for r in results:
                summary = r.get("summary", {})
                n_obs = summary.get("n_obs") or summary.get("nobs")
                row.append(_format_number(n_obs, decimals=0, format_type="integer"))
            lines.append(" & ".join(row) + r" \\")

        elif stat == "R2":
            row = ["R$^2$"]
            for r in results:
                summary = r.get("summary", {})
                rsq = summary.get("rsquared") or summary.get("rsquared_within")
                row.append(_format_number(rsq, decimals=2))
            lines.append(" & ".join(row) + r" \\")

        elif stat == "adj_R2":
            row = ["Adj. R$^2$"]
            for r in results:
                summary = r.get("summary", {})
                adj_rsq = summary.get("rsquared_adj")
                row.append(_format_number(adj_rsq, decimals=2))
            lines.append(" & ".join(row) + r" \\")

        elif stat == "F":
            row = ["F-statistic"]
            for r in results:
                summary = r.get("summary", {})
                f_stat = summary.get("f_statistic")
                row.append(_format_number(f_stat, decimals=2))
            lines.append(" & ".join(row) + r" \\")

        elif stat == "FE_entity" and include_fe_rows:
            row = ["Entity FE"]
            for r in results:
                summary = r.get("summary", {})
                has_fe = summary.get("entity_effects", False)
                row.append("Yes" if has_fe else "No")
            lines.append(" & ".join(row) + r" \\")

        elif stat == "FE_time" and include_fe_rows:
            row = ["Year FE"]
            for r in results:
                summary = r.get("summary", {})
                has_fe = summary.get("time_effects", False)
                row.append("Yes" if has_fe else "No")
            lines.append(" & ".join(row) + r" \\")

    # Bottom rule
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    # Table notes
    lines.append(r"\begin{tablenotes}[flushleft]")
    lines.append(r"\small")
    lines.append(_get_significance_note())
    lines.append(r"\end{tablenotes}")

    # End table
    lines.append(r"\end{table}")

    latex_str = "\n".join(lines)

    # Write to file if path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(latex_str)

    return latex_str


def make_iv_table(
    results: List[Dict[str, Any]],
    model_names: List[str],
    include_first_stage: bool = True,
    include_hansen_j: bool = True,
    **kwargs,
) -> str:
    """Generate LaTeX table specialized for IV regression results.

    Extends make_regression_table() to include first-stage F-statistics
    and Hansen J overidentification test p-values.

    Args:
        results: List of IV regression result dictionaries from run_iv2sls()
        model_names: Column headers for each model
        include_first_stage: If True, add first-stage F-stat row
        include_hansen_j: If True, add Hansen J p-value row (when available)
        **kwargs: Additional arguments passed to make_regression_table()

    Returns:
        LaTeX string with IV-specific diagnostics

    Example:
        >>> latex = make_iv_table(
        ...     results=[iv_result1, iv_result2],
        ...     model_names=['2SLS (1)', '2SLS (2)'],
        ...     include_first_stage=True
        ... )
    """
    # Get base table
    latex = make_regression_table(results, model_names, **kwargs)

    if not (include_first_stage or include_hansen_j):
        return latex

    # Insert IV-specific statistics before \bottomrule
    lines = latex.split("\n")
    bottomrule_idx = next(i for i, line in enumerate(lines) if r"\bottomrule" in line)

    iv_lines = []

    # First-stage F-stat row
    if include_first_stage:
        f_row = ["First-stage F"]
        for r in results:
            first_stage = r.get("first_stage", {})
            f_stat = first_stage.get("f_stat")
            f_row.append(
                _format_number(f_stat, decimals=2) if f_stat is not None else ""
            )
        iv_lines.append(" & ".join(f_row) + r" \\")

    # Hansen J test row
    if include_hansen_j:
        hansen_row = ["Hansen J p-val"]
        for r in results:
            overid = r.get("overid_test", {})
            pval = overid.get("pval")
            if pval is not None:
                hansen_row.append(f"{pval:.3f}")
            else:
                hansen_row.append("")
        iv_lines.append(" & ".join(hansen_row) + r" \\")

    # Insert IV lines before bottomrule
    lines = (
        lines[:bottomrule_idx]
        + iv_lines
        + [lines[bottomrule_idx]]
        + lines[bottomrule_idx + 1 :]
    )

    return "\n".join(lines)


def make_summary_table(
    data: Dict[str, Any],
    title: str = "Summary Statistics",
    output_path: Optional[Path] = None,
) -> str:
    """Generate LaTeX table for summary statistics.

    Args:
        data: Dictionary with variable names as keys and dicts as values.
              Each value dict should have: 'mean', 'std', 'min', 'max', 'n'
              Example: {'vagueness': {'mean': 0.5, 'std': 0.2, 'min': 0, 'max': 1, 'n': 1000}}
        title: Table title
        output_path: If provided, write to this file

    Returns:
        LaTeX string
    """
    lines = []

    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(f"\\caption{{{title}}}")
    lines.append(r"\begin{tabular}{lccccc}")
    lines.append(r"\toprule")
    lines.append("Variable & N & Mean & Std. Dev. & Min & Max \\\\")
    lines.append(r"\midrule")

    for var, stats in data.items():
        lines.append(
            f"{var} & "
            f"{_format_number(stats.get('n'), decimals=0, format_type='integer')} & "
            f"{_format_number(stats.get('mean'), decimals=3)} & "
            f"{_format_number(stats.get('std'), decimals=3)} & "
            f"{_format_number(stats.get('min'), decimals=3)} & "
            f"{_format_number(stats.get('max'), decimals=3)} \\\\"
        )

    lines.append(r"\midrule")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    latex_str = "\n".join(lines)

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(latex_str)

    return latex_str


def make_correlation_table(
    corr_matrix: Any,
    variable_labels: Optional[Dict[str, str]] = None,
    title: str = "Correlation Matrix",
    output_path: Optional[Path] = None,
) -> str:
    """Generate LaTeX table for correlation matrix.

    Args:
        corr_matrix: pandas DataFrame with correlation values
        variable_labels: Optional dict mapping variable names to display names
        title: Table title
        output_path: If provided, write to this file

    Returns:
        LaTeX string
    """
    if variable_labels is None:
        variable_labels = {}

    lines = []

    n_vars = len(corr_matrix.columns)

    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(f"\\caption{{{title}}}")
    lines.append(r"\begin{tabular}{" + "l" + "c" * n_vars + "}")
    lines.append(r"\toprule")

    # Header row
    header = [""]
    for var in corr_matrix.columns:
        header.append(variable_labels.get(var, var))
    lines.append(" & ".join(header) + r" \\")
    lines.append(r"\midrule")

    # Data rows
    for i, var_row in enumerate(corr_matrix.index):
        row = [variable_labels.get(var_row, var_row)]
        for j, _var_col in enumerate(corr_matrix.columns):
            if i == j:
                row.append("1.00")
            else:
                val = corr_matrix.iloc[i, j]
                row.append(f"{val:.2f}" if not pd.isna(val) else "")
        lines.append(" & ".join(row) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    latex_str = "\n".join(lines)

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(latex_str)

    return latex_str


if __name__ == "__main__":
    # Simple demonstration
    import numpy as np
    import pandas as pd

    # Create sample regression results
    np.random.seed(42)
    sample_results = [
        {
            "coefficients": pd.DataFrame(
                {
                    "variable": ["vagueness", "leverage", "size", "const"],
                    "coefficient": [0.123, -0.456, 0.789, 0.012],
                    "std_error": [0.045, 0.078, 0.089, 0.003],
                    "p_value": [0.001, 0.023, 0.150, 0.001],
                }
            ),
            "summary": {
                "n_obs": 1234,
                "rsquared": 0.45,
                "rsquared_adj": 0.44,
                "f_statistic": 25.3,
                "entity_effects": True,
                "time_effects": True,
            },
        }
    ]

    latex = make_regression_table(
        results=sample_results,
        model_names=["OLS"],
        variable_labels={"vagueness": "Speech Uncertainty", "leverage": "Leverage"},
        caption="Sample Regression Table",
        dep_var_name="Cash Holdings",
    )

    print("LaTeX Tables Module")
    print("=" * 70)
    print("Sample output:")
    print(latex)
