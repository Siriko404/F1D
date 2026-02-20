#!/usr/bin/env python3
"""
================================================================================
STAGE 4: H1 Cash Holdings Regression
================================================================================
ID: econometric/test_h1_cash_holdings
Description: Panel OLS regressions for H1 (Speech Uncertainty & Cash Holdings).

    Tests whether vague managers hoard more cash (precautionary motive) and
    whether leverage attenuates this effect (debt discipline hypothesis).

    H1a: beta1 > 0  (Higher uncertainty → more cash holdings)
    H1b: beta3 < 0  (Leverage attenuates uncertainty-cash relationship)

Model:
    CashHoldings_{t+1} = beta0
                        + beta1 * Uncertainty_t_c
                        + beta2 * Lev_t_c
                        + beta3 * (Uncertainty_t_c × Lev_t_c)
                        + gamma * Controls_t
                        + Firm FE + Year FE
                        + epsilon

Uncertainty measures (6):
    1. Manager_QA_Uncertainty_pct   (primary)
    2. CEO_QA_Uncertainty_pct
    3. Manager_QA_Weak_Modal_pct
    4. CEO_QA_Weak_Modal_pct
    5. Manager_Pres_Uncertainty_pct
    6. CEO_Pres_Uncertainty_pct

Specifications (4):
    primary        — Firm FE + Year FE, firm-clustered SE
    pooled         — No FE, firm-clustered SE
    year_only      — Year FE only, firm-clustered SE
    double_cluster — Firm FE + Year FE, double-clustered SE (firm+year)

Samples: Main, Finance, Utility

LaTeX output: Three stacked panels (Main / Finance / Utility).
Each panel has 6 columns (one per uncertainty measure), primary spec only.

Inputs:
    - outputs/variables/h1_cash_holdings/latest/h1_cash_holdings_panel.parquet

Outputs:
    - outputs/econometric/h1_cash_holdings/{timestamp}/
        model_diagnostics.csv
        h1_cash_holdings_table.tex
        regression_results_{sample}_{measure}_{spec}.txt
        report_step4_H1.md
        run_log.txt

Author: Thesis Author
Date: 2026-02-19
================================================================================
"""

from __future__ import annotations

import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.observability_utils import DualWriter
from f1d.shared.regression_validation import validate_columns, validate_sample_size

# ============================================================================
# Configuration
# ============================================================================

UNCERTAINTY_MEASURES = [
    "Manager_QA_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Manager_QA_Weak_Modal_pct",
    "CEO_QA_Weak_Modal_pct",
    "Manager_Pres_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
]

CONTROL_VARS = [
    "Size",
    "TobinsQ",
    "ROA",
    "CapexAt",
    "DividendPayer",
    "OCF_Volatility",
    "CurrentRatio",
]

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

SAMPLES = {
    "Main": lambda df: df["sample"] == "Main",
    "Finance": lambda df: df["sample"] == "Finance",
    "Utility": lambda df: df["sample"] == "Utility",
}

VAR_LABELS = {
    "Manager_QA_Uncertainty_pct": "QA Unc. (Mgr)",
    "CEO_QA_Uncertainty_pct": "QA Unc. (CEO)",
    "Manager_QA_Weak_Modal_pct": "Weak Modal (Mgr QA)",
    "CEO_QA_Weak_Modal_pct": "Weak Modal (CEO QA)",
    "Manager_Pres_Uncertainty_pct": "Pres. Unc. (Mgr)",
    "CEO_Pres_Uncertainty_pct": "Pres. Unc. (CEO)",
    "Lev": "Leverage",
    "Size": "Size (log assets)",
    "TobinsQ": "Tobin's Q",
    "ROA": "ROA",
    "CapexAt": "CapEx/Assets",
    "DividendPayer": "Dividend Payer",
    "OCF_Volatility": "OCF Volatility",
    "CurrentRatio": "Current Ratio",
}

MIN_OBS = 100

# ============================================================================
# Data loading
# ============================================================================


def load_panel(root: Path, dw: DualWriter) -> pd.DataFrame:
    panel_dir = get_latest_output_dir(
        root / "outputs" / "variables" / "h1_cash_holdings",
        required_file="h1_cash_holdings_panel.parquet",
    )
    panel_path = panel_dir / "h1_cash_holdings_panel.parquet"
    dw.write(f"  Loaded: {panel_path}\n")

    df = pd.read_parquet(panel_path)
    dw.write(f"  Rows: {len(df):,}, Columns: {len(df.columns)}\n")

    required = [
        "gvkey",
        "fiscal_year",
        "sample",
        "ff12_code",
        "CashHoldings_lead",
        "CashHoldings",
        "Lev",
    ] + UNCERTAINTY_MEASURES
    validate_columns(df, required)

    dw.write(f"\n  Sample distribution:\n")
    for s in ["Main", "Finance", "Utility"]:
        n = (df["sample"] == s).sum()
        dw.write(f"    {s}: {n:,} firm-years\n")

    return df


# ============================================================================
# Mean-centering
# ============================================================================


def center_vars(
    df: pd.DataFrame, cols: List[str]
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Mean-center columns (complete cases only for mean computation)."""
    df = df.copy()
    means: Dict[str, float] = {}
    for col in cols:
        if col in df.columns:
            m = df[col].mean(skipna=True)
            df[f"{col}_c"] = df[col] - m
            means[col] = float(m)
    return df, means


# ============================================================================
# Single regression
# ============================================================================


def run_single_regression(
    df: pd.DataFrame,
    uncertainty_var: str,
    spec_name: str,
    spec_cfg: Dict[str, bool],
    dw: DualWriter,
) -> Optional[Dict[str, Any]]:
    """Run one H1 regression (one uncertainty measure × one spec).

    Uses linearmodels.PanelOLS for entity/time FE with clustered SE.
    Falls back to statsmodels OLS (with C(gvkey)+C(fiscal_year) dummies)
    for pooled and year_only specs where linearmodels entity absorption
    may not be needed, but we use PanelOLS throughout for consistency.
    """
    try:
        from linearmodels.panel import PanelOLS, PooledOLS
        import warnings
    except ImportError:
        dw.write("  ERROR: linearmodels not installed. Run: pip install linearmodels\n")
        raise

    # Required columns for this regression
    needed = [
        uncertainty_var,
        "Lev",
        "CashHoldings_lead",
        "gvkey",
        "fiscal_year",
    ] + CONTROL_VARS
    available = [c for c in needed if c in df.columns]
    df_work = (
        df[available]
        .dropna(subset=[uncertainty_var, "Lev", "CashHoldings_lead"])
        .copy()
    )

    # Drop controls with missing; keep obs where at least uncertainty+Lev+DV available
    df_work = df_work.dropna(subset=[c for c in CONTROL_VARS if c in df_work.columns])

    if len(df_work) < MIN_OBS:
        dw.write(f"    Skipped ({len(df_work)} obs < {MIN_OBS} minimum)\n")
        return None

    # Mean-center uncertainty and Lev
    df_work, means = center_vars(df_work, [uncertainty_var, "Lev"])
    unc_c = f"{uncertainty_var}_c"
    lev_c = "Lev_c"
    interaction = f"{uncertainty_var}_x_Lev"
    df_work[interaction] = df_work[unc_c] * df_work[lev_c]

    # Build exog list
    controls_avail = [c for c in CONTROL_VARS if c in df_work.columns]
    exog_cols = [unc_c, lev_c, interaction] + controls_avail

    # Set MultiIndex for linearmodels
    df_panel = df_work.set_index(["gvkey", "fiscal_year"])

    y = df_panel["CashHoldings_lead"]
    X = df_panel[exog_cols].copy()
    import statsmodels.api as sm

    X = sm.add_constant(X, has_constant="add")

    formula_str = (
        f"CashHoldings_lead ~ {unc_c} + {lev_c} + {interaction} + "
        + " + ".join(controls_avail)
        + " + Firm FE + Year FE"
    )
    dw.write(f"    Formula: {formula_str}\n")

    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if spec_cfg["entity_effects"] or spec_cfg["time_effects"]:
            model = PanelOLS(
                y,
                X,
                entity_effects=spec_cfg["entity_effects"],
                time_effects=spec_cfg["time_effects"],
            )
        else:
            model = PooledOLS(y, X)

        cluster_col = "gvkey" if not spec_cfg["double_cluster"] else None
        if spec_cfg["double_cluster"]:
            fit = model.fit(
                cov_type="clustered", cluster_entity=True, cluster_time=True
            )
        else:
            fit = model.fit(cov_type="clustered", cluster_entity=True)

    n_obs = int(fit.nobs)
    rsq = float(fit.rsquared) if hasattr(fit, "rsquared") else np.nan

    params = fit.params
    pvalues = fit.pvalues

    beta1 = float(params.get(unc_c, np.nan))
    beta3 = float(params.get(interaction, np.nan))
    p1_two = float(pvalues.get(unc_c, np.nan))
    p3_two = float(pvalues.get(interaction, np.nan))

    # One-tailed tests
    p1_one = p1_two / 2 if beta1 > 0 else (1 - p1_two / 2)  # H1a: beta1 > 0
    p3_one = p3_two / 2 if beta3 < 0 else (1 - p3_two / 2)  # H1b: beta3 < 0

    h1a = (not np.isnan(p1_one)) and (p1_one < 0.05) and (beta1 > 0)
    h1b = (not np.isnan(p3_one)) and (p3_one < 0.05) and (beta3 < 0)

    return {
        "uncertainty_var": uncertainty_var,
        "spec": spec_name,
        "n_obs": n_obs,
        "rsquared": rsq,
        "beta1": beta1,
        "beta1_se": float(fit.std_errors.get(unc_c, np.nan)),
        "beta1_t": float(fit.tstats.get(unc_c, np.nan)),
        "beta1_p_two": p1_two,
        "beta1_p_one": p1_one,
        "beta1_signif": h1a,
        "beta3": beta3,
        "beta3_se": float(fit.std_errors.get(interaction, np.nan)),
        "beta3_t": float(fit.tstats.get(interaction, np.nan)),
        "beta3_p_two": p3_two,
        "beta3_p_one": p3_one,
        "beta3_signif": h1b,
        "centering_means": means,
        "fit": fit,
    }


# ============================================================================
# Run all regressions for one sample
# ============================================================================


def run_sample_regressions(
    df: pd.DataFrame,
    sample_name: str,
    dw: DualWriter,
    out_dir: Path,
) -> List[Dict[str, Any]]:
    """Run all 24 regressions (6 measures × 4 specs) for one sample."""
    results = []

    for uv in UNCERTAINTY_MEASURES:
        for spec_name, spec_cfg in SPECS.items():
            dw.write(f"\n  [{sample_name}] {uv} × {spec_name}:\n")
            result = run_single_regression(df, uv, spec_name, spec_cfg, dw)

            if result is not None:
                result["sample"] = sample_name
                results.append(result)
                dw.write(
                    f"    N={result['n_obs']:,}, R2={result['rsquared']:.4f}, "
                    f"b1={result['beta1']:.4f} (p1={result['beta1_p_one']:.4f}) "
                    f"H1a={'YES' if result['beta1_signif'] else 'NO'}, "
                    f"b3={result['beta3']:.4f} (p3={result['beta3_p_one']:.4f}) "
                    f"H1b={'YES' if result['beta3_signif'] else 'NO'}\n"
                )

                # Save full regression output
                fit = result.pop("fit")
                txt_name = f"regression_results_{sample_name}_{uv}_{spec_name}.txt"
                with open(out_dir / txt_name, "w", encoding="utf-8") as f:
                    f.write(str(fit.summary))
                result["fit"] = fit  # put back for downstream use if needed
            else:
                dw.write(f"    No result.\n")

    return results


# ============================================================================
# LaTeX table — three stacked panels
# ============================================================================


def build_latex_table(
    all_results: Dict[str, List[Dict[str, Any]]],
    out_dir: Path,
    dw: DualWriter,
) -> None:
    """Generate LaTeX table with three stacked panels (Main / Finance / Utility).

    Each panel has 6 columns, one per uncertainty measure, primary spec only.
    Rows: β1 (Uncertainty), β1 SE, β3 (Interaction), β3 SE, N, R².
    """
    lines: List[str] = []

    def star(p: float) -> str:
        if np.isnan(p):
            return ""
        if p < 0.01:
            return "***"
        if p < 0.05:
            return "**"
        if p < 0.10:
            return "*"
        return ""

    ncols = len(UNCERTAINTY_MEASURES)
    col_spec = "l" + "r" * ncols

    lines += [
        "% Table H1: Speech Uncertainty and Cash Holdings",
        "% Auto-generated by test_h1_cash_holdings.py",
        r"\begin{table}[htbp]",
        r"  \centering",
        r"  \caption{H1: Speech Uncertainty and Cash Holdings}",
        r"  \label{tab:h1_cash_holdings}",
        r"  \begin{small}",
        f"  \\begin{{tabular}}{{{col_spec}}}",
        r"    \toprule",
    ]

    # Header row: uncertainty measure labels
    headers = " & ".join(
        f"\\shortstack{{{VAR_LABELS.get(uv, uv)}}}" for uv in UNCERTAINTY_MEASURES
    )
    lines.append(f"    & {headers} \\\\")
    lines.append(r"    \midrule")

    row_defs = [
        ("Uncertainty$_c$ (β₁)", "beta1", "beta1_se", "beta1_p_one"),
        ("Lev$_c$ × Unc$_c$ (β₃)", "beta3", "beta3_se", "beta3_p_one"),
    ]

    for panel_name in ["Main", "Finance", "Utility"]:
        if panel_name not in all_results:
            continue
        primary = [r for r in all_results[panel_name] if r["spec"] == "primary"]
        primary_by_uv = {r["uncertainty_var"]: r for r in primary}

        lines.append(
            f"    \\multicolumn{{{ncols + 1}}}{{l}}"
            f"{{\\textit{{Panel {chr(65 + list(all_results.keys()).index(panel_name))}: {panel_name} sample}}}} \\\\"
        )
        lines.append(r"    \midrule")

        for label, coef_key, se_key, p_key in row_defs:
            vals = []
            for uv in UNCERTAINTY_MEASURES:
                r = primary_by_uv.get(uv)
                if r is None:
                    vals.append("—")
                else:
                    c = r[coef_key]
                    s = star(r[p_key])
                    vals.append(f"{c:.4f}{s}")
            lines.append(f"    {label} & " + " & ".join(vals) + " \\\\")

            # SE row
            se_vals = []
            for uv in UNCERTAINTY_MEASURES:
                r = primary_by_uv.get(uv)
                if r is None:
                    se_vals.append("")
                else:
                    se_vals.append(f"({r[se_key]:.4f})")
            lines.append("    & " + " & ".join(se_vals) + " \\\\")

        # N and R² rows
        n_vals = []
        r2_vals = []
        for uv in UNCERTAINTY_MEASURES:
            r = primary_by_uv.get(uv)
            if r is None:
                n_vals.append("—")
                r2_vals.append("—")
            else:
                n_vals.append(f"{r['n_obs']:,}")
                r2_vals.append(f"{r['rsquared']:.3f}")

        lines.append(r"    \midrule")
        lines.append("    N & " + " & ".join(n_vals) + " \\\\")
        lines.append("    R\\textsuperscript{2} & " + " & ".join(r2_vals) + " \\\\")
        lines.append("    Firm FE & " + " & ".join(["Yes"] * ncols) + " \\\\")
        lines.append("    Year FE & " + " & ".join(["Yes"] * ncols) + " \\\\")
        lines.append(r"    \midrule")

    lines += [
        r"    \bottomrule",
        r"  \end{tabular}",
        r"  \end{small}",
        r"  \begin{tablenotes}",
        r"    \small",
        r"    \item This table reports H1 panel OLS results.",
        r"    \item DV: \textit{CashHoldings}$_{t+1}$ = cash \& equivalents / total assets.",
        r"    \item Uncertainty and Leverage are mean-centered before interaction.",
        r"    \item H1a: $\beta_1 > 0$ (one-tailed). H1b: $\beta_3 < 0$ (one-tailed).",
        r"    \item Standard errors in parentheses, clustered by firm.",
        r"    \item *$p<0.10$, **$p<0.05$, ***$p<0.01$ (two-tailed).",
        r"  \end{tablenotes}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h1_cash_holdings_table.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    dw.write(f"  Saved: h1_cash_holdings_table.tex\n")


# ============================================================================
# Markdown report
# ============================================================================


def write_report(
    all_results: Dict[str, List[Dict[str, Any]]],
    out_dir: Path,
    duration: float,
    dw: DualWriter,
) -> None:
    lines: List[str] = [
        "# H1 Cash Holdings Regression — Results Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f}s",
        "",
        "## Hypothesis",
        "",
        "- **H1a:** β₁ > 0 — Higher uncertainty → more cash holdings (precautionary motive)",
        "- **H1b:** β₃ < 0 — Leverage attenuates uncertainty-cash relationship (debt discipline)",
        "",
        "## Model",
        "",
        "```",
        "CashHoldings_{t+1} = β₀ + β₁·Unc_c + β₂·Lev_c + β₃·(Unc_c × Lev_c)",
        "                   + γ·Controls + Firm FE + Year FE + ε",
        "```",
        "",
    ]

    for sample_name, results in all_results.items():
        primary = [r for r in results if r["spec"] == "primary"]
        lines += [
            f"## {sample_name} Sample — Primary Specification",
            "",
            "| Uncertainty Measure | N | R² | β₁ | p₁ (1-tail) | H1a | β₃ | p₃ (1-tail) | H1b |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for r in primary:
            h1a = "✓" if r["beta1_signif"] else "✗"
            h1b = "✓" if r["beta3_signif"] else "✗"
            lines.append(
                f"| {VAR_LABELS.get(r['uncertainty_var'], r['uncertainty_var'])} "
                f"| {r['n_obs']:,} | {r['rsquared']:.4f} "
                f"| {r['beta1']:.4f} | {r['beta1_p_one']:.4f} | {h1a} "
                f"| {r['beta3']:.4f} | {r['beta3_p_one']:.4f} | {h1b} |"
            )

        h1a_count = sum(1 for r in primary if r["beta1_signif"])
        h1b_count = sum(1 for r in primary if r["beta3_signif"])
        lines += [
            "",
            f"H1a supported: {h1a_count}/6 measures significant",
            f"H1b supported: {h1b_count}/6 measures significant",
            "",
        ]

    report_path = out_dir / "report_step4_H1.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    dw.write(f"  Saved: report_step4_H1.md\n")


# ============================================================================
# Diagnostics CSV
# ============================================================================


def save_diagnostics(
    all_results: Dict[str, List[Dict[str, Any]]],
    out_dir: Path,
    dw: DualWriter,
) -> None:
    rows = []
    for sample_name, results in all_results.items():
        for r in results:
            rows.append(
                {
                    "sample": sample_name,
                    "uncertainty_var": r["uncertainty_var"],
                    "spec": r["spec"],
                    "n_obs": r["n_obs"],
                    "rsquared": r["rsquared"],
                    "beta1": r["beta1"],
                    "beta1_se": r["beta1_se"],
                    "beta1_t": r["beta1_t"],
                    "beta1_p_two": r["beta1_p_two"],
                    "beta1_p_one": r["beta1_p_one"],
                    "beta1_signif": r["beta1_signif"],
                    "beta3": r["beta3"],
                    "beta3_se": r["beta3_se"],
                    "beta3_t": r["beta3_t"],
                    "beta3_p_two": r["beta3_p_two"],
                    "beta3_p_one": r["beta3_p_one"],
                    "beta3_signif": r["beta3_signif"],
                }
            )

    diag_df = pd.DataFrame(rows)
    diag_path = out_dir / "model_diagnostics.csv"
    diag_df.to_csv(diag_path, index=False)
    dw.write(f"  Saved: model_diagnostics.csv ({len(diag_df)} rows)\n")


# ============================================================================
# Main
# ============================================================================


def main() -> int:
    # Ensure stdout can handle unicode on Windows (cp1252 terminal)
    import sys as _sys

    if hasattr(_sys.stdout, "reconfigure"):
        _sys.stdout.reconfigure(encoding="utf-8")

    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h1_cash_holdings" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    log_path = out_dir / "run_log.txt"
    dw = DualWriter(log_path)

    try:
        dw.write("=" * 80 + "\n")
        dw.write("STAGE 4: H1 Cash Holdings Regression\n")
        dw.write("=" * 80 + "\n")
        dw.write(f"Timestamp: {timestamp}\n")
        dw.write(f"Output: {out_dir}\n\n")

        # Load panel
        dw.write("=" * 60 + "\n")
        dw.write("Loading panel\n")
        dw.write("=" * 60 + "\n")
        df = load_panel(root, dw)

        # Validate sample size
        validate_sample_size(df, min_observations=500)

        # Run regressions per sample
        all_results: Dict[str, List[Dict[str, Any]]] = {}

        for sample_name, mask_fn in SAMPLES.items():
            mask = mask_fn(df)
            df_sample = df[mask].copy()

            dw.write("\n" + "=" * 60 + "\n")
            dw.write(f"Sample: {sample_name} ({len(df_sample):,} firm-years)\n")
            dw.write("=" * 60 + "\n")

            if len(df_sample) < MIN_OBS:
                dw.write(
                    f"  Skipped — too few observations ({len(df_sample)} < {MIN_OBS})\n"
                )
                continue

            results = run_sample_regressions(df_sample, sample_name, dw, out_dir)
            all_results[sample_name] = results

        # Save outputs
        dw.write("\n" + "=" * 60 + "\n")
        dw.write("Saving outputs\n")
        dw.write("=" * 60 + "\n")

        save_diagnostics(all_results, out_dir, dw)
        build_latex_table(all_results, out_dir, dw)

        duration = (datetime.now() - start_time).total_seconds()
        write_report(all_results, out_dir, duration, dw)

        # Summary
        dw.write("\n" + "=" * 80 + "\n")
        dw.write("COMPLETE\n")
        dw.write("=" * 80 + "\n")
        dw.write(f"Duration: {duration:.1f} seconds\n")
        dw.write(f"Output:   {out_dir}\n\n")

        for sample_name, results in all_results.items():
            primary = [r for r in results if r["spec"] == "primary"]
            h1a = sum(1 for r in primary if r["beta1_signif"])
            h1b = sum(1 for r in primary if r["beta3_signif"])
            dw.write(
                f"  {sample_name}: H1a {h1a}/6, H1b {h1b}/6 significant (primary spec)\n"
            )

    except Exception as e:
        dw.write(f"\nERROR: {e}\n")
        dw.write(traceback.format_exc())
        sys.stdout = dw.original_stdout
        dw.close()
        sys.exit(1)

    sys.stdout = dw.original_stdout
    dw.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
