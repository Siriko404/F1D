#!/usr/bin/env python3
"""latex_tables_accounting - Accounting Review style tables (Est + t-value format).

Purpose:
    Generates publication-ready LaTeX tables in strict Accounting Review style
    with two columns per model (Estimate and t-value), no significance stars,
    and sparse booktabs formatting.

Key Classes/Functions:
    - make_accounting_table: Generate Accounting Review style table
    - make_diagnostics_table: Generate simple diagnostics table
    - make_summary_stats_table: Generate summary statistics table
    - make_cox_hazard_table: Generate Cox hazard model table

Usage:
    from f1d.shared.latex_tables_accounting import make_accounting_table

    latex = make_accounting_table(
        results={
            "Main": {"model": model1, "diagnostics": {...}},
            "Finance": {"model": model2, "diagnostics": {...}},
        },
        caption="Table 1: Manager Clarity Fixed Effects",
        note="This table reports manager fixed effects..."
    )

Table Format (TAR Style):
    - No vertical lines
    - Sparse horizontal rules (toprule, midrule, cmidrule, bottomrule)
    - Two columns per model: Estimate and t-value (NOT SE in parentheses)
    - NO significance stars
    - Multi-panel tables with panel headers

Reference: The Accounting Review Author Guidelines
"""

from __future__ import annotations

import re
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


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

    # Note paragraph — escape bare & that would break LaTeX column parsing.
    # Only replace & not already preceded by \ (i.e., not already escaped).
    if note:
        safe_note = re.sub(r"(?<!\\)&", r"\\&", note)
        lines.append("")
        lines.append(r"\vspace{0.5em}")
        lines.append(f"\\parbox{{\\textwidth}}{{\\small {safe_note}}}")
        lines.append("")

    # Begin tabular
    # Column spec: left-aligned for variable, then right-aligned pairs for each sample
    # TAR style: numeric columns are right-aligned (r), not centered (c)
    col_spec = "l" + "rr" * n_samples
    lines.append(f"\\begin{{tabular}}{{@{{}}{col_spec}@{{}}}}")

    # Top rule
    lines.append(r"\toprule")

    # Sample headers
    if n_samples > 1:
        # First row: sample names spanning 2 columns each
        # Replace underscores with spaces for valid LaTeX (underscores cause subscript errors)
        header_parts = [""]  # Empty first cell for variable name column
        for sample in sample_names:
            display_sample = sample.replace("_", " ")
            header_parts.append(f"\\multicolumn{{2}}{{c}}{{{display_sample}}}")
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

    # Control variable rows: TAR style = one row per variable with Est. and t-value
    # side-by-side in their respective columns (NOT stacked across two rows).
    for var in control_variables:
        display_name = variable_labels.get(var, var)

        # Single row: varname & coef & tval & coef & tval & ...
        row_parts = [display_name]

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
                row_parts.append(format_tvalue(tval))
            else:
                # Variable not in this model — both cells blank
                row_parts.append("")
                row_parts.append("")

        lines.append(" & ".join(row_parts) + r" \\")

    # Midrule before bottomrule to close the last panel (TAR style)
    lines.append(r"\midrule")

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


def make_summary_stats_table(
    df: pd.DataFrame,
    variables: List[Dict[str, str]],
    sample_names: Optional[List[str]] = None,
    sample_col: str = "sample",
    output_csv: Optional[Path] = None,
    output_tex: Optional[Path] = None,
    caption: str = "Summary Statistics",
    label: str = "tab:summary_stats",
    decimals: int = 4,
) -> pd.DataFrame:
    """Generate summary statistics table for regression variables.

    Computes N, Mean, SD, Min, P25, Median, P75, Max for each variable.
    Generates both CSV (machine-readable) and LaTeX (publication-ready) outputs.

    Args:
        df: DataFrame with regression data (must be the COMPLETE-CASE filtered data
            used in the actual regression, NOT raw panel data)
        variables: List of dicts with 'col' (column name) and 'label' (display name) keys.
                   Columns not in df are skipped with a warning.
        sample_names: If provided, compute per-sample breakdown (e.g., ["Main", "Finance", "Utility"]).
                      If None, compute single aggregate table.
        sample_col: Column name for sample filtering (default: "sample"). Ignored if sample_names is None.
        output_csv: Path to save CSV output. If None, no CSV is saved.
        output_tex: Path to save LaTeX output. If None, no LaTeX is saved.
        caption: LaTeX table caption.
        label: LaTeX label for cross-referencing.
        decimals: Number of decimal places for statistics (default: 4).

    Returns:
        DataFrame with columns: Sample, Variable, Col, N, Mean, SD, Min, P25, Median, P75, Max

    Edge Cases:
        - Variable not in df: skip with warning, continue with others
        - Variable all-NaN: report N=0, stats as NaN
        - Zero SD (constant variable): report SD=0.0000, continue normally
        - Empty df: return empty DataFrame with correct columns
    """
    # Define result columns
    result_columns = [
        "Sample",
        "Variable",
        "Col",
        "N",
        "Mean",
        "SD",
        "Min",
        "P25",
        "Median",
        "P75",
        "Max",
    ]
    rows = []

    # Handle empty DataFrame
    if df.empty:
        result_df = pd.DataFrame(columns=result_columns)
    else:
        # Filter to valid variables (those that exist in df)
        valid_vars = []
        for var_spec in variables:
            col_name = var_spec.get("col")
            if col_name not in df.columns:
                warnings.warn(
                    f"Variable '{col_name}' not found in DataFrame. Skipping.",
                    UserWarning,
                )
            else:
                valid_vars.append(var_spec)

        # Determine samples to process
        if sample_names is None:
            # Single aggregate table
            samples_to_process = [(None, df)]
        else:
            # Per-sample breakdown
            samples_to_process = []
            for sample_name in sample_names:
                if sample_col in df.columns:
                    sample_df = df[df[sample_col] == sample_name]
                    if not sample_df.empty:
                        samples_to_process.append((sample_name, sample_df))
                    else:
                        # Still include empty sample with empty df for consistency
                        samples_to_process.append(
                            (sample_name, pd.DataFrame(columns=df.columns))
                        )
                else:
                    warnings.warn(
                        f"Sample column '{sample_col}' not found in DataFrame. "
                        "Computing aggregate statistics instead.",
                        UserWarning,
                    )
                    samples_to_process = [(None, df)]
                    break

        # Compute statistics for each sample × variable
        for sample_name, sample_df in samples_to_process:
            for var_spec in valid_vars:
                col_name = var_spec["col"]
                display_label = var_spec.get("label", col_name)

                if sample_df.empty or col_name not in sample_df.columns:
                    # Empty sample or missing column - report N=0, stats as NaN
                    rows.append(
                        {
                            "Sample": sample_name if sample_name else "All",
                            "Variable": display_label,
                            "Col": col_name,
                            "N": 0,
                            "Mean": np.nan,
                            "SD": np.nan,
                            "Min": np.nan,
                            "P25": np.nan,
                            "Median": np.nan,
                            "P75": np.nan,
                            "Max": np.nan,
                        }
                    )
                else:
                    # Get non-null values
                    values = sample_df[col_name].dropna()
                    n = len(values)

                    if n == 0:
                        # All NaN values
                        rows.append(
                            {
                                "Sample": sample_name if sample_name else "All",
                                "Variable": display_label,
                                "Col": col_name,
                                "N": 0,
                                "Mean": np.nan,
                                "SD": np.nan,
                                "Min": np.nan,
                                "P25": np.nan,
                                "Median": np.nan,
                                "P75": np.nan,
                                "Max": np.nan,
                            }
                        )
                    else:
                        rows.append(
                            {
                                "Sample": sample_name if sample_name else "All",
                                "Variable": display_label,
                                "Col": col_name,
                                "N": n,
                                "Mean": values.mean(),
                                "SD": values.std(ddof=1),
                                "Min": values.min(),
                                "P25": values.quantile(0.25),
                                "Median": values.median(),
                                "P75": values.quantile(0.75),
                                "Max": values.max(),
                            }
                        )

        result_df = pd.DataFrame(rows)

    # Save CSV if requested
    if output_csv is not None:
        output_csv = Path(output_csv)
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        # Format N with comma separators, stats with decimals
        csv_df = result_df.copy()
        csv_df["N"] = csv_df["N"].apply(
            lambda x: f"{int(x):,}"
            if pd.notna(x) and x > 0
            else str(int(x))
            if pd.notna(x)
            else ""
        )
        for col in ["Mean", "SD", "Min", "P25", "Median", "P75", "Max"]:
            csv_df[col] = csv_df[col].apply(
                lambda x: f"{x:.{decimals}f}" if pd.notna(x) else ""
            )
        csv_df.to_csv(output_csv, index=False)

    # Save LaTeX if requested
    if output_tex is not None:
        output_tex = Path(output_tex)
        output_tex.parent.mkdir(parents=True, exist_ok=True)
        latex_content = _generate_summary_stats_latex(
            result_df, caption, label, decimals, sample_names
        )
        with open(output_tex, "w", encoding="utf-8") as f:
            f.write(latex_content)

    return result_df


def _generate_summary_stats_latex(
    df: pd.DataFrame,
    caption: str,
    label: str,
    decimals: int,
    sample_names: Optional[List[str]],
) -> str:
    """Generate LaTeX table for summary statistics.

    Args:
        df: DataFrame with summary statistics
        caption: Table caption
        label: LaTeX label
        decimals: Number of decimal places
        sample_names: List of sample names for panel structure, or None for single table

    Returns:
        LaTeX string
    """
    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(f"\\caption{{{caption}}}")
    lines.append(f"\\label{{{label}}}")

    # Column spec: Variable + 8 statistics columns
    col_spec = "lrrrrrrrr"
    lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
    lines.append(r"\toprule")

    # Header row
    header = "Variable & N & Mean & SD & Min & P25 & Median & P75 & Max"
    lines.append(header + r" \\")
    lines.append(r"\midrule")

    def format_row(row: pd.Series) -> str:
        """Format a single data row."""
        # Escape bare & in variable labels (e.g. "R&D Intensity" → "R\&D Intensity")
        var = re.sub(r"(?<!\\)&", r"\\&", str(row["Variable"]))
        n = f"{int(row['N']):,}" if pd.notna(row["N"]) and row["N"] > 0 else "0"
        stats = []
        for col in ["Mean", "SD", "Min", "P25", "Median", "P75", "Max"]:
            val = row[col]
            if pd.isna(val):
                stats.append("---")
            else:
                stats.append(f"{val:.{decimals}f}")
        return f"{var} & {n} & " + " & ".join(stats) + r" \\"

    if sample_names is None or len(sample_names) == 0:
        # Single panel (no sample breakdown)
        for _, row in df.iterrows():
            lines.append(format_row(row))
    else:
        # Multi-panel by sample
        for i, sample_name in enumerate(sample_names):
            sample_df = df[df["Sample"] == sample_name]
            if sample_df.empty:
                continue

            # Panel header (skip before first panel)
            if i > 0:
                lines.append(r"\midrule")
            lines.append(
                r"\multicolumn{9}{l}{\textit{Panel "
                + chr(65 + i)
                + f": {sample_name} Sample"
                + r"}} \\"
            )
            lines.append(r"\midrule")

            for _, row in sample_df.iterrows():
                lines.append(format_row(row))

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    # Table notes
    lines.append(r"\begin{tablenotes}")
    lines.append(r"\small")
    lines.append(
        r"\item This table reports summary statistics for all three industry samples. "
        r"Regressions use Main sample only."
    )
    lines.append(r"All variables are measured at the call level.")
    lines.append(r"\end{tablenotes}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def make_cox_hazard_table(
    results: List[Dict[str, Any]],
    variable_labels: Dict[str, str],
    caption: str = "",
    label: str = "",
    note: str = "",
    output_path: Optional[Path] = None,
) -> str:
    """Generate Accounting Review style LaTeX table for Cox hazard models.

    Creates a table with:
    - Panel A: Model Diagnostics (N Events, Concordance)
    - Panel B: Hazard Ratios (HR, SE in parentheses below)

    Args:
        results: List of dicts from extract_results() where each dict is ONE
                 coefficient row with model-level diagnostics included.
        variable_labels: Dict mapping variable names to display names.
        caption, label, note: Standard LaTeX table elements.
        output_path: If provided, write to file.

    Returns:
        LaTeX string
    """
    if not results:
        return ""

    # Column structure: 3 models x 2 variants = 6 data columns
    model_order = ["Cox PH All", "Cox CS Uninvited", "Cox CS Friendly"]
    variant_order = ["Regime", "CEO"]

    col_keys = []
    for model in model_order:
        for variant in variant_order:
            col_keys.append((model, variant))

    n_cols = 1 + len(col_keys)

    # Get unique variables
    all_vars = []
    seen = set()
    for row in results:
        var = row.get("variable")
        if var and var not in seen:
            all_vars.append(var)
            seen.add(var)

    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    if caption:
        lines.append(f"\\caption{{{caption}}}")
    if label:
        lines.append(f"\\label{{{label}}}")
    if note:
        safe_note = re.sub(r"(?<!\\)&", r"\\&", note)
        lines.append(f"\\parbox{{\\textwidth}}{{\\small {safe_note}}}")

    col_spec = "l" + "c" * len(col_keys)
    lines.append(f"\\begin{{tabular}}{{@{{}}{col_spec}@{{}}}}")
    lines.append(r"\toprule")

    # Header row 1: Model names
    header1 = [""]
    for model in model_order:
        header1.append(f"\\multicolumn{{2}}{{c}}{{{model}}}")
    lines.append(" & ".join(header1) + r" \\")

    # cmidrule
    cmidrules = []
    for i in range(len(model_order)):
        start = 2 + i * 2
        end = start + 1
        cmidrules.append(f"\\cmidrule(lr){{{start}-{end}}}")
    lines.append(" ".join(cmidrules))

    # Header row 2: Variants
    header2 = [""]
    for _ in model_order:
        header2.extend(["Regime", "CEO"])
    lines.append(" & ".join(header2) + r" \\")
    lines.append(r"\midrule")

    # Panel A: Model Diagnostics
    lines.append(f"\\multicolumn{{{n_cols}}}{{l}}{{\\textit{{Panel A: Model Diagnostics}}}} \\\\")
    lines.append(r"\midrule")

    # N Events row
    n_events_parts = ["N Events"]
    for model, variant in col_keys:
        match_row = next((r for r in results if r.get("model") == model and r.get("variant") == variant), None)
        if match_row and match_row.get("n_events") is not None:
            n_events_parts.append(str(int(match_row["n_events"])))
        else:
            n_events_parts.append("")
    lines.append(" & ".join(n_events_parts) + r" \\")

    # Concordance row
    conc_parts = ["Concordance"]
    for model, variant in col_keys:
        match_row = next((r for r in results if r.get("model") == model and r.get("variant") == variant), None)
        if match_row and match_row.get("concordance") is not None and not pd.isna(match_row["concordance"]):
            conc_parts.append(f"{match_row['concordance']:.4f}")
        else:
            conc_parts.append("")
    lines.append(" & ".join(conc_parts) + r" \\")

    lines.append(r"\midrule")

    # Panel B: Hazard Ratios
    lines.append(f"\\multicolumn{{{n_cols}}}{{l}}{{\\textit{{Panel B: Hazard Ratios}}}} \\\\")
    lines.append(r"\midrule")

    # Variable rows
    for var in all_vars:
        display_name = variable_labels.get(var, var)
        display_name = re.sub(r"(?<!\\)&", r"\\&", display_name)
        row_parts = [display_name]

        for model, variant in col_keys:
            match_row = next((r for r in results if r.get("model") == model and r.get("variant") == variant and r.get("variable") == var), None)
            if match_row and match_row.get("exp_coef") is not None:
                row_parts.append(f"{match_row['exp_coef']:.4f}")
            else:
                row_parts.append("")
        lines.append(" & ".join(row_parts) + r" \\")

    # SE rows
    for var in all_vars:
        se_parts = [""]
        for model, variant in col_keys:
            match_row = next((r for r in results if r.get("model") == model and r.get("variant") == variant and r.get("variable") == var), None)
            if match_row and match_row.get("se_coef") is not None:
                se_parts.append(f"({match_row['se_coef']:.4f})")
            else:
                se_parts.append("")
        lines.append(" & ".join(se_parts) + r" \\")

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


__all__ = [
    "make_accounting_table",
    "make_diagnostics_table",
    "make_summary_stats_table",
    "make_cox_hazard_table",
    "format_estimate",
    "format_tvalue",
]
