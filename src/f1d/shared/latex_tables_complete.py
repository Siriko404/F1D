#!/usr/bin/env python3
"""Complete Accounting Review Style LaTeX Table Generator.

This module generates COMPLETE publication-ready LaTeX tables in Accounting Review style:
- Coefficient with standard error in parentheses below
- Significance stars (* p<0.10, ** p<0.05, *** p<0.01)
- Each column = separate model specification
- Full diagnostics (N, R², Adj R², F-stat, etc.)
- Fixed effects indicators
- Complete audit trail

Reference: The Accounting Review, Journal of Finance, Review of Accounting Studies

Example:
    from f1d.shared.latex_tables_complete import make_complete_table

    results = {
        "Main": {
            "model": model1,
            "diagnostics": {"n_obs": 45000, "rsquared": 0.45, "n_ceos": 2500}
        },
        "Finance": {...},
        "Utility": {...}
    }

    latex = make_complete_table(
        results=results,
        caption="Table 1: CEO Clarity Fixed Effects",
        variable_labels=var_labels,
        control_variables=control_vars,
        output_path=Path("outputs/table.tex")
    )
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


def add_stars(pvalue: float) -> str:
    """Add significance stars based on p-value.

    Args:
        pvalue: p-value from regression

    Returns:
        Star string (*, **, or ***)
    """
    if pvalue is None or np.isnan(pvalue):
        return ""
    if pvalue < 0.01:
        return "***"
    if pvalue < 0.05:
        return "**"
    if pvalue < 0.10:
        return "*"
    return ""


def format_coef_with_stars(value: float, pvalue: float, decimals: int = 3) -> str:
    """Format coefficient with significance stars.

    Args:
        value: Coefficient value
        pvalue: p-value for stars
        decimals: Number of decimal places

    Returns:
        Formatted string with stars
    """
    if np.isnan(value) or value is None:
        return ""
    stars = add_stars(pvalue)
    return f"{value:.{decimals}f}{stars}"


def format_se(value: float, decimals: int = 3) -> str:
    """Format standard error in parentheses.

    Args:
        value: Standard error value
        decimals: Number of decimal places

    Returns:
        Formatted string in parentheses
    """
    if np.isnan(value) or value is None:
        return ""
    return f"({value:.{decimals}f})"


def format_integer(value: int) -> str:
    """Format integer with comma separators."""
    if value is None:
        return ""
    return f"{int(value):,}"


def make_complete_table(
    results: Dict[str, Dict[str, Any]],
    caption: str = "",
    label: str = "",
    note: str = "",
    variable_labels: Optional[Dict[str, str]] = None,
    control_variables: Optional[List[str]] = None,
    output_path: Optional[Path] = None,
    coef_decimals: int = 3,
    se_decimals: int = 3,
    include_fixed_effects: bool = True,
    fixed_effects_labels: Optional[Dict[str, str]] = None,
    include_f_stat: bool = True,
    include_adj_r2: bool = True,
    entity_label: str = "N CEOs",
    table_width: str = "textwidth",
    font_size: str = "small",
) -> str:
    """Generate COMPLETE Accounting Review style LaTeX table.

    Creates a publication-ready table with:
    - Coefficients in main row
    - Standard errors in parentheses below
    - Significance stars
    - Full diagnostics
    - Fixed effects indicators

    Args:
        results: Dict mapping sample names to result dicts containing:
            - 'model': Fitted statsmodels OLS model (with .params, .bse, .pvalues)
            - 'diagnostics': Dict with 'n_obs', 'rsquared', 'n_ceos', etc.
        caption: Table caption
        label: LaTeX label for cross-referencing
        note: Explanatory note (table footnote)
        variable_labels: Dict mapping variable names to display names
        control_variables: List of control variable names to include (in order)
        output_path: If provided, write LaTeX to this file
        coef_decimals: Decimal places for coefficients
        se_decimals: Decimal places for standard errors
        include_fixed_effects: Whether to include FE indicator rows
        fixed_effects_labels: Dict mapping FE names to display names
        include_f_stat: Include F-statistic row
        include_adj_r2: Include Adjusted R² row
        entity_label: Label for entity count (e.g., "N CEOs", "N Firms")
        table_width: LaTeX width spec ("textwidth", "linewidth", or custom)
        font_size: Font size ("small", "footnotesize", "scriptsize")

    Returns:
        LaTeX string ready for .tex file
    """
    if variable_labels is None:
        variable_labels = {}
    if control_variables is None:
        control_variables = []
    if fixed_effects_labels is None:
        fixed_effects_labels = {"ceo_fe": "CEO Fixed Effects", "year_fe": "Year Fixed Effects"}

    sample_names = list(results.keys())
    n_samples = len(sample_names)

    # Column spec: left-aligned for variable, centered for each sample
    col_spec = "l" + "c" * n_samples

    lines = []

    # Table environment with optional sizing
    if table_width == "textwidth":
        lines.append(r"\begin{table}[htbp]")
    else:
        lines.append(r"\begin{table}[htbp]")

    lines.append(r"\centering")

    # Caption
    if caption:
        lines.append(f"\\caption{{{caption}}}")
    if label:
        lines.append(f"\\label{{{label}}}")
    lines.append("")

    # Font size
    if font_size != "normalsize":
        lines.append(f"\\{font_size}")

    # Begin tabular
    lines.append(f"\\begin{{tabular}}{{@{{}}{{{col_spec}}}@{{}}}}")

    # Top rule
    lines.append(r"\toprule")

    # Sample headers
    header_parts = [""] + sample_names
    lines.append(" & ".join(header_parts) + r" \\")

    # cmidrule under each sample column
    if n_samples > 1:
        cmidrules = []
        for i in range(n_samples):
            start_col = 2 + i
            end_col = start_col
            cmidrules.append(f"\\cmidrule(lr){{{start_col}-{end_col}}}")
        lines.append(" ".join(cmidrules))

    lines.append(r"\midrule")

    # === Control Variables Section ===
    for var in control_variables:
        display_name = variable_labels.get(var, var)

        # Coefficient row
        coef_parts = [display_name]
        for sample in sample_names:
            model = results[sample].get("model")
            if model is not None and hasattr(model, "params") and var in model.params:
                coef = model.params[var]
                pval = model.pvalues[var] if hasattr(model, "pvalues") and var in model.pvalues else np.nan
                coef_parts.append(format_coef_with_stars(coef, pval, coef_decimals))
            else:
                coef_parts.append("")
        lines.append(" & ".join(coef_parts) + r" \\")

        # Standard error row
        se_parts = [""]
        for sample in sample_names:
            model = results[sample].get("model")
            if model is not None and hasattr(model, "bse") and var in model.bse:
                se = model.bse[var]
                se_parts.append(format_se(se, se_decimals))
            else:
                se_parts.append("")
        lines.append(" & ".join(se_parts) + r" \\")

    # === Fixed Effects Section ===
    if include_fixed_effects:
        lines.append(r"\midrule")

        # CEO Fixed Effects
        fe_parts = [fixed_effects_labels.get("ceo_fe", "CEO Fixed Effects")]
        for sample in sample_names:
            diag = results[sample].get("diagnostics", {})
            n_ceos = diag.get("n_ceos") or diag.get("n_entities") or diag.get("n_managers")
            if n_ceos:
                fe_parts.append("Yes")
            else:
                fe_parts.append("No")
        lines.append(" & ".join(fe_parts) + r" \\")

        # Year Fixed Effects
        fe_parts = [fixed_effects_labels.get("year_fe", "Year Fixed Effects")]
        for sample in sample_names:
            diag = results[sample].get("diagnostics", {})
            has_year_fe = diag.get("year_fe", True)
            fe_parts.append("Yes" if has_year_fe else "No")
        lines.append(" & ".join(fe_parts) + r" \\")

    # === Diagnostics Section ===
    lines.append(r"\midrule")

    # N Observations
    n_obs_parts = ["Observations"]
    for sample in sample_names:
        diag = results[sample].get("diagnostics", {})
        n_obs = diag.get("n_obs") or diag.get("nobs") or diag.get("n_observations")
        n_obs_parts.append(format_integer(n_obs) if n_obs else "")
    lines.append(" & ".join(n_obs_parts) + r" \\")

    # N Entities
    n_ent_parts = [entity_label]
    for sample in sample_names:
        diag = results[sample].get("diagnostics", {})
        n_ent = diag.get("n_ceos") or diag.get("n_entities") or diag.get("n_managers")
        n_ent_parts.append(format_integer(n_ent) if n_ent else "")
    lines.append(" & ".join(n_ent_parts) + r" \\")

    # R-squared
    r2_parts = ["R-squared"]
    for sample in sample_names:
        diag = results[sample].get("diagnostics", {})
        rsq = diag.get("rsquared") or diag.get("r_squared")
        r2_parts.append(f"{rsq:.3f}" if rsq is not None else "")
    lines.append(" & ".join(r2_parts) + r" \\")

    # Adjusted R-squared
    if include_adj_r2:
        ar2_parts = ["Adjusted R-squared"]
        for sample in sample_names:
            diag = results[sample].get("diagnostics", {})
            arsq = diag.get("rsquared_adj") or diag.get("r_squared_adj") or diag.get("adj_rsquared")
            ar2_parts.append(f"{arsq:.3f}" if arsq is not None else "")
        lines.append(" & ".join(ar2_parts) + r" \\")

    # F-statistic
    if include_f_stat:
        f_parts = ["F-statistic"]
        for sample in sample_names:
            diag = results[sample].get("diagnostics", {})
            f_stat = diag.get("f_statistic") or diag.get("f_stat")
            if f_stat is not None:
                if f_stat > 1000:
                    f_parts.append(f"{f_stat:.2e}")
                else:
                    f_parts.append(f"{f_stat:.2f}")
            else:
                f_parts.append("")
        lines.append(" & ".join(f_parts) + r" \\")

    # Bottom rule
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    # Table note
    if note:
        lines.append("")
        lines.append(r"\begin{tablenotes}[flushleft]\footnotesize")
        lines.append(r"\item " + note)
        lines.append(r"\end{tablenotes}")

    # End table
    lines.append(r"\end{table}")

    # Star legend (if any stars in table)
    lines.append("")
    lines.append(r"% Significance levels: * p<0.10, ** p<0.05, *** p<0.01")

    latex_str = "\n".join(lines)

    # Write to file if path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(latex_str)

    return latex_str


def make_panel_table(
    results: Dict[str, Dict[str, Any]],
    caption: str = "",
    label: str = "",
    note: str = "",
    variable_labels: Optional[Dict[str, str]] = None,
    control_variables: Optional[List[str]] = None,
    output_path: Optional[Path] = None,
    coef_decimals: int = 3,
    entity_label: str = "N CEOs",
) -> str:
    """Generate multi-panel Accounting Review style LaTeX table.

    Creates a table with separate panels for:
    - Panel A: Model Diagnostics
    - Panel B: Control Variables
    - Panel C: Fixed Effects (optional)

    This format is commonly used in The Accounting Review for complex tables.

    Args:
        results: Dict mapping sample names to result dicts
        caption: Table caption
        label: LaTeX label
        note: Table footnote
        variable_labels: Variable name mappings
        control_variables: List of control variables
        output_path: Output file path
        coef_decimals: Decimal places for coefficients
        entity_label: Label for entity count

    Returns:
        LaTeX string
    """
    if variable_labels is None:
        variable_labels = {}
    if control_variables is None:
        control_variables = []

    sample_names = list(results.keys())
    n_samples = len(sample_names)
    n_cols = 1 + 2 * n_samples  # Variable + (Est, t-val) per sample

    lines = []

    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    if caption:
        lines.append(f"\\caption{{{caption}}}")
    if label:
        lines.append(f"\\label{{{label}}}")

    if note:
        lines.append("")
        lines.append(r"\vspace{0.5em}")
        lines.append(f"\\parbox{{\\textwidth}}{{\\small {note}}}")
        lines.append("")

    col_spec = "l" + "cc" * n_samples
    lines.append(f"\\begin{{tabular}}{{@{{}}{{{col_spec}}}@{{}}}}")
    lines.append(r"\toprule")

    # Sample headers
    if n_samples > 1:
        header_parts = [""]
        for sample in sample_names:
            header_parts.append(f"\\multicolumn{{2}}{{c}}{{{sample}}}")
        lines.append(" & ".join(header_parts) + r" \\")

        cmidrules = []
        for i in range(n_samples):
            start_col = 2 + i * 2
            end_col = start_col + 1
            cmidrules.append(f"\\cmidrule(lr){{{start_col}-{end_col}}}")
        lines.append(" ".join(cmidrules))

    subheader_parts = [""]
    for _ in sample_names:
        subheader_parts.extend(["Est.", "t-stat"])
    lines.append(" & ".join(subheader_parts) + r" \\")

    # === Panel A: Model Diagnostics ===
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{" + str(n_cols) + r"}{l}{\textit{Panel A: Model Diagnostics}} \\")
    lines.append(r"\midrule")

    # N Observations
    n_obs_parts = ["N Observations"]
    for sample in sample_names:
        diag = results[sample].get("diagnostics", {})
        n_obs = diag.get("n_obs") or diag.get("nobs")
        n_obs_parts.append(format_integer(n_obs) if n_obs else "")
        n_obs_parts.append("")
    lines.append(" & ".join(n_obs_parts) + r" \\")

    # R-squared
    r2_parts = ["R-squared"]
    for sample in sample_names:
        diag = results[sample].get("diagnostics", {})
        rsq = diag.get("rsquared")
        r2_parts.append(f"{rsq:.3f}" if rsq is not None else "")
        r2_parts.append("")
    lines.append(" & ".join(r2_parts) + r" \\")

    # Adj R-squared
    ar2_parts = ["Adjusted R-squared"]
    for sample in sample_names:
        diag = results[sample].get("diagnostics", {})
        arsq = diag.get("rsquared_adj")
        ar2_parts.append(f"{arsq:.3f}" if arsq is not None else "")
        ar2_parts.append("")
    lines.append(" & ".join(ar2_parts) + r" \\")

    # N Entities
    n_ent_parts = [entity_label]
    for sample in sample_names:
        diag = results[sample].get("diagnostics", {})
        n_ent = diag.get("n_ceos") or diag.get("n_entities")
        n_ent_parts.append(format_integer(n_ent) if n_ent else "")
        n_ent_parts.append("")
    lines.append(" & ".join(n_ent_parts) + r" \\")

    # === Panel B: Control Variables ===
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{" + str(n_cols) + r"}{l}{\textit{Panel B: Control Variables}} \\")
    lines.append(r"\midrule")

    for var in control_variables:
        display_name = variable_labels.get(var, var)

        # Coefficient row
        coef_parts = [display_name]
        tval_parts = [""]

        for sample in sample_names:
            model = results[sample].get("model")
            if model is not None and hasattr(model, "params") and var in model.params:
                coef = model.params[var]
                tval = model.tvalues[var] if hasattr(model, "tvalues") and var in model.tvalues else np.nan
                pval = model.pvalues[var] if hasattr(model, "pvalues") and var in model.pvalues else np.nan

                stars = add_stars(pval)
                coef_parts.append(f"{coef:.{coef_decimals}f}{stars}")
                coef_parts.append("")
                tval_parts.append(f"{tval:.2f}" if not np.isnan(tval) else "")
                tval_parts.append("")
            else:
                coef_parts.extend(["", ""])
                tval_parts.extend(["", ""])

        lines.append(" & ".join(coef_parts) + r" \\")
        lines.append(" & ".join(tval_parts) + r" \\")

    # === Panel C: Fixed Effects ===
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{" + str(n_cols) + r"}{l}{\textit{Panel C: Fixed Effects}} \\")
    lines.append(r"\midrule")

    # CEO FE
    fe_parts = ["CEO Fixed Effects"]
    for sample in sample_names:
        fe_parts.append("Yes")
        fe_parts.append("")
    lines.append(" & ".join(fe_parts) + r" \\")

    # Year FE
    fe_parts = ["Year Fixed Effects"]
    for sample in sample_names:
        fe_parts.append("Yes")
        fe_parts.append("")
    lines.append(" & ".join(fe_parts) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    lines.append("")
    lines.append(r"% Significance levels: * p<0.10, ** p<0.05, *** p<0.01")

    latex_str = "\n".join(lines)

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(latex_str)

    return latex_str


__all__ = [
    "make_complete_table",
    "make_panel_table",
    "add_stars",
    "format_coef_with_stars",
    "format_se",
]
