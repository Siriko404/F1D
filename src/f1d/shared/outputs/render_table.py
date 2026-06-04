"""Pure-transform renderer: SuiteSpec → LaTeX table chunk.

Single rendering entry point for all 37 suites. Consumes a validated
SuiteSpec (loaded from suite_spec_<id>.json) and emits a LaTeX chunk
that gets concatenated into all_tables.tex.

Every formatting decision traces back to the spec — no hardcoded state,
no config lookups, no estimator-aware branches. The renderer is a pure
transformation from spec to string.
"""

from __future__ import annotations

import math
from typing import Optional

from .suite_spec_schema import Coef, Column, SuiteSpec


# ---------------------------------------------------------------------------
# Coefficient / significance formatting
# ---------------------------------------------------------------------------


def _stars_for_var(
    var_name: str, coef: Coef, iv_tails: dict[str, str]
) -> str:
    """Significance stars with β-sign gating for one-tailed IVs.

    Rule: for IVs declared `one_pos` / `one_neg`, stars are suppressed
    when the coefficient sign disagrees with the hypothesis direction.
    Controls and two-tailed IVs use `p_two` without gating.
    """
    tail = iv_tails.get(var_name)
    if tail in ("one_pos", "one_neg"):
        if tail == "one_pos" and coef.beta <= 0:
            return ""
        if tail == "one_neg" and coef.beta >= 0:
            return ""
        p = coef.p_one
    else:
        p = coef.p_two

    if p is None or (isinstance(p, float) and math.isnan(p)):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def _fmt_coef(
    coef: Optional[Coef],
    var_name: str,
    iv_tails: dict[str, str],
    decimal_places: int,
) -> str:
    if coef is None:
        return ""
    beta_str = f"{coef.beta:.{decimal_places}f}"
    stars = _stars_for_var(var_name, coef, iv_tails)
    if stars:
        return f"\\textbf{{{beta_str}}}$^{{{stars}}}$"
    return beta_str


def _fmt_se(coef: Optional[Coef], decimal_places: int) -> str:
    if coef is None:
        return ""
    return f"({coef.se:.{decimal_places}f})"


def _esc(name: str) -> str:
    """Escape a raw pipeline variable name for LaTeX text mode (underscores).

    Used by the ``names_only`` render path so a literal pipeline identifier
    (e.g. ``US_EPU_log``, ``UncResCEO_c_x_Unrated``) compiles instead of
    aborting on the bare ``_``. Pipeline names are Python identifiers, so the
    underscore is the only LaTeX-special character that can appear.
    """
    return name.replace("_", r"\_")


# ---------------------------------------------------------------------------
# Header row emission (top col-numbers + multi-row group headers)
# ---------------------------------------------------------------------------


def _emit_header_rows(spec: SuiteSpec) -> list[str]:
    """Col-number row + each `header_rows` entry with cmidrules where needed."""
    n_cols = len(spec.columns)
    lines: list[str] = []

    # Col numbers always first
    col_nums = " & ".join(f"({c.col})" for c in spec.columns)
    lines.append(f" & {col_nums} \\\\")

    for header_row in spec.header_rows:
        cells: list[str] = []
        for cell in header_row:
            if cell.span == 1:
                cells.append(cell.label)
            else:
                cells.append(f"\\multicolumn{{{cell.span}}}{{c}}{{{cell.label}}}")
        lines.append(" & " + " & ".join(cells) + r" \\")

        # cmidrule below rows that contain multi-span groups
        if any(c.span > 1 for c in header_row):
            rules: list[str] = []
            col_pos = 2  # col 1 is the row-label column; first data col is 2
            for cell in header_row:
                if cell.span > 1:
                    start = col_pos
                    end = col_pos + cell.span - 1
                    rules.append(f"\\cmidrule(lr){{{start}-{end}}}")
                col_pos += cell.span
            lines.append(" ".join(rules))

    # Sanity: last header row must span n_cols
    total_span = sum(c.span for c in spec.header_rows[-1])
    if total_span != n_cols:
        raise ValueError(
            f"render_suite[{spec.suite_id}]: last header row spans {total_span} "
            f"but suite has {n_cols} columns"
        )

    return lines


# ---------------------------------------------------------------------------
# Variable rows (IVs + controls)
# ---------------------------------------------------------------------------


def _emit_var_rows(
    var_names: list[str],
    labels: dict[str, str],
    columns: list[Column],
    iv_tails: dict[str, str],
    decimal_places: int,
    mask_by_control_vars: bool,
    names_only: bool = False,
) -> list[str]:
    """Emit `var_name & beta & ... \\` + `& (se) & ... \\` pair per variable.

    If `mask_by_control_vars` is True, variables not in a given column's
    `control_vars` list render as empty cells (used for control rows where
    different cols have different control sets — H11 PRES_CONTROL_MAP,
    H1 base-vs-extended).
    """
    lines: list[str] = []
    for var in var_names:
        coef_cells: list[str] = []
        se_cells: list[str] = []
        for col in columns:
            if mask_by_control_vars and var not in col.control_vars:
                coef_cells.append("")
                se_cells.append("")
                continue
            coef = col.coefs.get(var)
            coef_cells.append(_fmt_coef(coef, var, iv_tails, decimal_places))
            se_cells.append(_fmt_se(coef, decimal_places))

        label = _esc(var) if names_only else labels.get(var, var)
        lines.append(f"{label} & " + " & ".join(coef_cells) + r" \\")
        lines.append(" & " + " & ".join(se_cells) + r" \\")
    return lines


# ---------------------------------------------------------------------------
# Indicator rows / summary rows / footnote
# ---------------------------------------------------------------------------


def _emit_indicator_rows(columns: list[Column]) -> list[str]:
    """Emit indicator rows (Extended Controls, Industry FE, ..., Year-Quarter FE).

    Rows where every column is empty are suppressed (has_firm / has_ind
    guard pattern from this session's 2026-04-13 H18b fix).
    """
    lines: list[str] = []
    if not columns:
        return lines

    # Use the first column's key set as the canonical order. All columns
    # must have the same keys (the helper guarantees this).
    ordered_keys = list(columns[0].indicator_rows.keys())

    for key in ordered_keys:
        cells = [col.indicator_rows.get(key, "") for col in columns]
        if not any(cell for cell in cells):
            continue  # all empty — suppress entire row
        lines.append(f"{key} & " + " & ".join(cells) + r" \\")
    return lines


def _emit_summary_rows(spec: SuiteSpec) -> list[str]:
    lines: list[str] = []
    n_cells = [f"{int(c.n_obs):,}" for c in spec.columns]
    lines.append("N & " + " & ".join(n_cells) + r" \\")

    # R² label: wrap in $...$ only if the label is bare math (no $).
    # Labels that already contain $ (e.g. "Pseudo~$R^2$") are emitted verbatim.
    r2_label = spec.render_hints.r2_label
    r2_rendered = r2_label if "$" in r2_label else f"${r2_label}$"
    r2_cells = [f"{c.r2:.3f}" for c in spec.columns]
    lines.append(f"{r2_rendered} & " + " & ".join(r2_cells) + r" \\")

    if not spec.render_hints.skip_adj_r2:
        adj_cells: list[str] = []
        for c in spec.columns:
            if c.adj_r2 is None:
                adj_cells.append("")
            else:
                adj_cells.append(f"{c.adj_r2:.3f}")
        lines.append(r"Adj.~$R^2$ & " + " & ".join(adj_cells) + r" \\")
    return lines


def _emit_footnote(spec: SuiteSpec) -> list[str]:
    lines = [
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        f"\\textit{{Notes:}} {spec.tail.footer_note}",
        r" Significant coefficients in \textbf{bold}.",
        f" {spec.clustering.footer_note}",
        f" {spec.sample_label}",
        r" $R^2$ includes absorbed fixed effects (not within-$R^2$).",
    ]

    if spec.render_hints.scaling_note:
        lines.append(f" {spec.render_hints.scaling_note}")

    fallback_cols = [c.col for c in spec.columns if c.cluster_fallback]
    if fallback_cols:
        cols_str = ", ".join(f"({c})" for c in fallback_cols)
        lines.append(
            f" Columns {cols_str} fall back to firm-only clustering "
            r"(two-way clustered VCV rank-deficient; coefficients unchanged)."
        )

    lines.append(r"\end{minipage}")
    return lines


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def render_suite(spec: SuiteSpec, names_only: bool = False) -> str:
    """Render a SuiteSpec as a complete LaTeX table chunk.

    Output matches the academic-convention format currently in
    outputs/all_tables.tex: landscape scriptsize tabular with booktabs
    rules, multicolumn group headers, IV + control rows with bold-and-
    starred significance, FE indicator rows, summary stats, and a
    Notes minipage footer.

    When ``names_only`` is True, IV and control rows render the raw pipeline
    variable name (underscore-escaped) instead of the spec's display label —
    used for the thesis_tables.tex pass so every variable shows its literal
    pipeline identifier. Headers and footnotes are unaffected.
    """
    iv_tails = {iv.name: iv.tail for iv in spec.ivs}
    iv_labels = {iv.name: iv.label for iv in spec.ivs}
    iv_names = [iv.name for iv in spec.ivs]

    control_labels = dict(spec.controls.labels)
    control_order = list(spec.controls.base) + list(spec.controls.extended_only)

    decimal_places = spec.render_hints.decimal_places
    n_cols = len(spec.columns)

    lines: list[str] = [
        r"\begin{table}[htbp]",
        r"\centering",
        f"\\caption{{{spec.caption}}}",
        f"\\label{{{spec.label}}}",
        r"\scriptsize",
        r"\begin{tabular}{l" + "c" * n_cols + "}",
        r"\toprule",
    ]

    lines.extend(_emit_header_rows(spec))
    lines.append(r"\midrule")

    lines.extend(
        _emit_var_rows(
            var_names=iv_names,
            labels=iv_labels,
            columns=spec.columns,
            iv_tails=iv_tails,
            decimal_places=decimal_places,
            mask_by_control_vars=False,  # IVs are always in every column
            names_only=names_only,
        )
    )
    lines.append(r"\midrule")

    lines.extend(
        _emit_var_rows(
            var_names=control_order,
            labels=control_labels,
            columns=spec.columns,
            iv_tails=iv_tails,  # used only to skip p_one gating for controls
            decimal_places=decimal_places,
            mask_by_control_vars=True,
            names_only=names_only,
        )
    )
    lines.append(r"\midrule")

    indicator_lines = _emit_indicator_rows(spec.columns)
    if indicator_lines:
        lines.extend(indicator_lines)
        lines.append(r"\midrule")

    lines.extend(_emit_summary_rows(spec))
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    lines.extend(_emit_footnote(spec))
    lines.append(r"\end{table}")

    return "\n".join(lines)


__all__ = ["render_suite"]
