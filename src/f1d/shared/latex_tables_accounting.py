#!/usr/bin/env python3
"""Accounting Review Style LaTeX Table Generator.

This module generates publication-ready LaTeX tables in Accounting Review style:
- No vertical lines
- Sparse horizontal rules (toprule, midrule, cmidrule, bottomrule)
- Two columns per model: Estimate and t-value (NOT coefficient with SE in parentheses)
- NO significance stars
- Multi-panel tables with panel headers

Reference: The Accounting Review Author Guidelines

Example:
    from f1d.shared.latex_tables_accounting import make_accounting_table

    results = {
        "Main": {
            "model": model1,
            "diagnostics": {"n_obs": 45000, "rsquared": 0.45, "n_managers": 2500}
        },
        "Finance": {...},
        "Utility": {...}
    }

    latex = make_accounting_table(
        results=results,
        caption="Table 1: Manager Clarity Fixed Effects",
        note="This table reports manager fixed effects..."
    )
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def format_estimate(value: float, decimals: int = 3) -> str:
    """Format coefficient estimate for display.

    Args:
        value: Coefficient value
        decimals: Number of decimal places

    Returns:
        Formatted string (no stars)
    """
    if np.isnan(value) or value is None:
        return ""
    return f"{value:.{decimals}f}"


def format_tvalue(value: float, decimals: int = 2) -> str:
    """Format t-statistic for display.

    Args:
        value: t-statistic value
        decimals: Number of decimal places

    Returns:
        Formatted string
    """
    if np.isnan(value) or value is None:
        return ""
    return f"{value:.{decimals}f}"


def format_integer(value: int) -> str:
    """Format integer with comma separators.

    Args:
        value: Integer value

    Returns:
        Formatted string with commas
    """
    if value is None:
        return ""
    return f"{int(value):,}"


def make_accounting_table(
    results: Dict[str, Dict[str, Any]],
    caption: str = "",
    label: str = "",
    note: str = "",
    variable_labels: Optional[Dict[str, str]] = None,
    control_variables: Optional[List[str]] = None,
    output_path: Optional[Path] = None,
    decimals: int = 3,
    entity_label: str = "N Managers",
) -> str:
    """Generate Accounting Review style LaTeX table.

    Creates a multi-panel table with two columns per model (Estimate, t-value),
    no significance stars, and sparse booktabs formatting.

    Args:
        results: Dict mapping sample names to result dicts containing:
            - 'model': Fitted statsmodels OLS model
            - 'diagnostics': Dict with 'n_obs', 'rsquared', 'n_managers' (or 'n_entities')
        caption: Table caption
        label: LaTeX label for cross-referencing
        note: Explanatory note to appear below caption
        variable_labels: Dict mapping variable names to display names
        control_variables: List of control variable names to include (in order)
        output_path: If provided, write LaTeX to this file
        decimals: Number of decimal places for coefficients

    Returns:
        LaTeX string ready for .tex file

    Example:
        >>> latex = make_accounting_table(
        ...     results={
        ...         "Main": {"model": model1, "diagnostics": {...}},
        ...         "Finance": {"model": model2, "diagnostics": {...}},
        ...     },
        ...     caption="Table 1: Manager Clarity Fixed Effects",
        ...     note="This table reports manager fixed effects..."
        ... )
    """
    if variable_labels is None:
        variable_labels = {}
    if control_variables is None:
        control_variables = []

    sample_names = list(results.keys())
    n_samples = len(sample_names)

    # Calculate total columns: 1 for variable name + 2 per sample (Est, t-val)
    n_cols = 1 + 2 * n_samples

    lines = []

    # Table environment
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")

    # Caption
    if caption:
        lines.append(f"\\caption{{{caption}}}")
    if label:
        lines.append(f"\\label{{{label}}}")

    # Note paragraph
    if note:
        lines.append("")
        lines.append(r"\vspace{0.5em}")
        lines.append(f"\\parbox{{\\textwidth}}{{\\small {note}}}")
        lines.append("")

    # Begin tabular
    # Column spec: left-aligned for variable, then c pairs for each sample
    col_spec = "l" + "cc" * n_samples
    lines.append(f"\\begin{{tabular}}{{@{{}}{{{col_spec}}}@{{}}}}")

    # Top rule
    lines.append(r"\toprule")

    # Sample headers
    if n_samples > 1:
        # First row: sample names spanning 2 columns each
        header_parts = [""]  # Empty first cell
        for sample in sample_names:
            header_parts.append(f"\\multicolumn{{2}}{{c}}{{{sample}}}")
        lines.append(" & ".join(header_parts) + r" \\")

        # cmidrule under each sample
        cmidrules = []
        for i, _ in enumerate(sample_names):
            start_col = 2 + i * 2
            end_col = start_col + 1
            cmidrules.append(f"\\cmidrule(lr){{{start_col}-{end_col}}}")
        lines.append(" ".join(cmidrules))

    # Second row: Est. and t-value for each sample
    subheader_parts = [""]  # Empty first cell
    for _ in sample_names:
        subheader_parts.extend(["Est.", "t-value"])
    lines.append(" & ".join(subheader_parts) + r" \\")

    # Midrule before data
    lines.append(r"\midrule")

    # Panel A: Model Diagnostics
    lines.append(
        r"\multicolumn{" + str(n_cols) + r"}{l}{\textit{Panel A: Model Diagnostics}} \\"
    )
    lines.append(r"\midrule")

    # N Observations row
    n_obs_parts = ["N Observations"]
    for sample in sample_names:
        diag = results[sample].get("diagnostics", {})
        n_obs = diag.get("n_obs") or diag.get("nobs") or diag.get("n_observations")
        n_obs_parts.append(format_integer(n_obs) if n_obs else "")
        n_obs_parts.append("")  # Empty t-value cell
    lines.append(" & ".join(n_obs_parts) + r" \\")

    # R-squared row
    r2_parts = ["R-squared"]
    for sample in sample_names:
        diag = results[sample].get("diagnostics", {})
        rsq = diag.get("rsquared") or diag.get("r_squared")
        r2_parts.append(f"{rsq:.3f}" if rsq is not None else "")
        r2_parts.append("")  # Empty t-value cell
    lines.append(" & ".join(r2_parts) + r" \\")

    # N entities row — label is caller-supplied (e.g., "N CEOs" vs "N Managers")
    n_mgr_parts = [entity_label]
    for sample in sample_names:
        diag = results[sample].get("diagnostics", {})
        n_mgr = diag.get("n_managers") or diag.get("n_entities") or diag.get("n_ceos")
        n_mgr_parts.append(format_integer(n_mgr) if n_mgr else "")
        n_mgr_parts.append("")  # Empty t-value cell
    lines.append(" & ".join(n_mgr_parts) + r" \\")

    # Midrule before Panel B
    lines.append(r"\midrule")

    # Panel B: Control Variables
    lines.append(
        r"\multicolumn{" + str(n_cols) + r"}{l}{\textit{Panel B: Control Variables}} \\"
    )
    lines.append(r"\midrule")

    # Get models to extract coefficients
    for var in control_variables:
        display_name = variable_labels.get(var, var)

        row_parts = [display_name]
        tval_parts = [""]  # t-value row starts with empty cell

        for sample in sample_names:
            model = results[sample].get("model")
            if model is not None and hasattr(model, "params") and var in model.params:
                coef = model.params[var]
                tval = (
                    model.tvalues[var]
                    if hasattr(model, "tvalues") and var in model.tvalues
                    else np.nan
                )

                row_parts.append(format_estimate(coef, decimals))
                row_parts.append("")  # Empty cell for t-value column
                tval_parts.append(format_tvalue(tval))
                tval_parts.append("")  # Empty cell for spacing
            else:
                row_parts.append("")
                row_parts.append("")
                tval_parts.append("")
                tval_parts.append("")

        # Do NOT remove trailing empty cells - need consistent column count
        lines.append(" & ".join(row_parts) + r" \\")
        lines.append(" & ".join(tval_parts) + r" \\")

    # Bottom rule
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

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


def make_diagnostics_table(
    diagnostics: Dict[str, Dict[str, Any]],
    caption: str = "Model Diagnostics",
    output_path: Optional[Path] = None,
) -> str:
    """Generate simple diagnostics table without coefficients.

    Args:
        diagnostics: Dict mapping sample names to diagnostic dicts
        caption: Table caption
        output_path: If provided, write to file

    Returns:
        LaTeX string
    """
    sample_names = list(diagnostics.keys())
    n_samples = len(sample_names)

    lines = []

    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(f"\\caption{{{caption}}}")

    col_spec = "l" + "c" * n_samples
    lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
    lines.append(r"\toprule")

    # Header
    header = [""] + sample_names
    lines.append(" & ".join(header) + r" \\")
    lines.append(r"\midrule")

    # Rows
    rows = [
        ("N Observations", "n_obs"),
        (
            "N Entities",
            "n_managers",
        ),  # generic label; callers may override via results dict
        ("R-squared", "rsquared"),
        ("Adj. R-squared", "rsquared_adj"),
        ("F-statistic", "f_statistic"),
    ]

    for label, key in rows:
        row_parts = [label]
        for sample in sample_names:
            value = diagnostics[sample].get(key)
            if value is None:
                row_parts.append("")
            elif key in ["n_obs", "n_managers"]:
                row_parts.append(format_integer(int(value)))
            else:
                row_parts.append(f"{value:.3f}")
        lines.append(" & ".join(row_parts) + r" \\")

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


__all__ = [
    "make_accounting_table",
    "make_diagnostics_table",
    "format_estimate",
    "format_tvalue",
]
