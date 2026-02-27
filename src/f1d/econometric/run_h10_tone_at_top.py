#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Tone-at-the-Top Econometrics (H_TT)
================================================================================
ID: econometric/run_h10_tone_at_top
Description: Executes regressions for the Tone-at-the-Top transmission hypothesis.
             H_TT1: Call-level, real-time CEO style predicts CFO uncertainty.
             H_TT2: Speaker-turn level, prior CEO QA turns predict NonCEO manager uncertainty.
             Model 3: Robustness using full-sample ClarityCEO instead of real-time style.

Model Specifications:
    M1 (Call-level): IHS(CFO_QA_Unc) ~ ClarityStyle_Realtime + Controls + FirmFE + QuarterFE
    M2 (Turn-level): IHS(NonCEO_Turn_Unc) ~ IHS(CEO_Prior_QA_Unc_j) + CallFE + SpeakerFE

    ClarityStyle_Realtime = 4-call rolling window, min 4 prior calls, EB-shrunk.

Hypothesis Tests:
    H_TT1: beta(ClarityStyle_Realtime) > 0 (CEO style transmits to CFO uncertainty)
    H_TT2: beta(CEO_Prior_QA_Unc) > 0 (prior CEO turns predict NonCEO manager uncertainty)

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    CEOs must have >= 4 prior calls for real-time style estimation.
    Turn-level analysis requires speaker identification.

Clustering: Two-way (Firm × CEO) for call-level models.

Inputs:
    - outputs/variables/tone_at_top/latest/tone_at_top_panel.parquet
    - outputs/variables/tone_at_top/latest/tone_at_top_turns_panel.parquet

Outputs:
    - outputs/econometric/tone_at_top/{timestamp}/coefficients_{sample}_{model}.csv
    - outputs/econometric/tone_at_top/{timestamp}/tone_at_top_full.tex (Accounting Review style)
    - outputs/econometric/tone_at_top/{timestamp}/tone_at_top_summary.tex (summary table)
    - outputs/econometric/tone_at_top/{timestamp}/model_diagnostics.csv
    - outputs/econometric/tone_at_top/{timestamp}/summary_stats.csv
    - outputs/econometric/tone_at_top/{timestamp}/summary_stats.tex
    - outputs/econometric/tone_at_top/{timestamp}/report.md

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h10_tone_at_top_panel)
    - Uses: linearmodels, f1d.shared.latex_tables_accounting

Author: Thesis Author
Date: 2026-02-26
================================================================================
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS
from linearmodels.iv.absorbing import AbsorbingLS

from f1d.shared.latex_tables_accounting import make_summary_stats_table
from f1d.shared.path_utils import get_latest_output_dir, ensure_output_dir


def parse_arguments():
    parser = argparse.ArgumentParser(description="H_TT Econometrics")
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate without executing"
    )
    return parser.parse_args()


# ==============================================================================
# Summary Statistics Variables (Call-level panel)
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Transformed dependent variables
    {"col": "IHS_CFO_QA_Unc", "label": "CFO Q\\&A Uncertainty (IHS)"},
    {"col": "IHS_CEO_QA_Unc", "label": "CEO Q\\&A Uncertainty (IHS)"},
    {"col": "IHS_CEO_Pres_Unc", "label": "CEO Pres. Uncertainty (IHS)"},
    # Main independent variable
    {"col": "ClarityStyle_Realtime", "label": "CEO Style (Realtime Clarity)"},
    # Financial controls
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "BM", "label": "Book-to-Market"},
    {"col": "Lev", "label": "Leverage"},
    {"col": "ROA", "label": "ROA"},
    {"col": "StockRet", "label": "Stock Return"},
    {"col": "MarketRet", "label": "Market Return"},
    {"col": "EPS_Growth", "label": "EPS Growth"},
    {"col": "SurpDec", "label": "Earnings Surprise Decile"},
]


def asinh(series: pd.Series) -> pd.Series:
    """Inverse hyperbolic sine transformation for percentage variables."""
    return pd.Series(np.arcsinh(series.to_numpy()), index=series.index)


def run_call_level_model_full(
    df: pd.DataFrame, dv: str, iv: str, controls: list
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Run Model 1 (Call-level) with two-way clustering and FEs.
    Returns full coefficient table and diagnostics.
    """
    reg_df = df.copy()
    reg_df["year_qtr"] = (
        reg_df["year"].astype(str) + "Q" + reg_df["quarter"].astype(str)
    )
    reg_df["yq_id"] = reg_df["year_qtr"].astype("category").cat.codes

    # Drop NAs
    keep_cols = ["file_name", "gvkey", "ceo_id", "yq_id", dv, iv] + controls
    reg_df = reg_df.dropna(subset=keep_cols)

    if len(reg_df) < 50:
        return pd.DataFrame(), {"N": len(reg_df), "Error": "Too few obs"}

    reg_df["const"] = 1

    # Set multi-index for panel
    reg_df = reg_df.set_index(["gvkey", "yq_id"])

    exog = ["const", iv] + controls

    try:
        mod = PanelOLS(
            dependent=reg_df[dv],
            exog=reg_df[exog],
            entity_effects=True,
            time_effects=True,
            drop_absorbed=True,
        )
        # Cluster by firm (gvkey) and CEO
        clusters = pd.DataFrame(
            {
                "gvkey": pd.Categorical(reg_df.index.get_level_values("gvkey")).codes,
                "ceo_id": reg_df["ceo_id"].astype("category").cat.codes,
            },
            index=reg_df.index,
        )
        res = mod.fit(cov_type="clustered", clusters=clusters)

        # Build full coefficient table
        params = res.params.copy()
        std_errs = res.std_errors.copy()
        tstats = res.tstats.copy()
        pvalues = res.pvalues.copy()

        coef_df = pd.DataFrame({
            "variable": params.index,
            "coef": params.values,
            "se": std_errs.values,
            "tstat": tstats.values,
            "pval": pvalues.values,
        })
        coef_df = coef_df.reset_index(drop=True)

        # Rename const to Intercept
        coef_df.loc[coef_df["variable"] == "const", "variable"] = "Intercept"

        diagnostics = {
            "N": int(res.nobs),
            "n_entities": int(res.entity_info["total"]),
            "n_time": int(res.time_info["total"]),
            "r2_within": round(res.rsquared_within, 4) if res.rsquared_within is not None else np.nan,
            "r2_between": round(res.rsquared_between, 4) if res.rsquared_between is not None else np.nan,
            "r2_overall": round(res.rsquared, 4) if res.rsquared is not None else np.nan,
        }

        return coef_df, diagnostics

    except Exception as e:
        return pd.DataFrame(), {"N": len(reg_df), "Error": str(e)}


def run_turn_level_model_full(
    df: pd.DataFrame, dv: str, iv: str, controls: Optional[List[str]] = None,
    cluster_by_call: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Run Model 2 (Speaker-turn level) with Call FE + Speaker FE absorbed.
    Now supports additional controls beyond the main IV.

    Args:
        df: DataFrame with turn-level data
        dv: Dependent variable column name
        iv: Independent variable column name
        controls: Optional list of additional control variables
        cluster_by_call: If True, cluster by (Firm, Call); if False, cluster by (Firm, CEO)
                        Per Addendum C, the default is Firm+Call for M2.

    Returns full coefficient table and diagnostics.
    """
    if controls is None:
        controls = []

    reg_df = df.copy()

    # Use speaker_id (composite key) for Speaker FE - per Addendum A
    speaker_col = "speaker_id" if "speaker_id" in reg_df.columns else "speaker_name"

    keep_cols = [
        "file_name",
        speaker_col,
        "gvkey",
        "ceo_id",
        dv,
        iv,
    ] + controls
    keep_cols = list(set(keep_cols))  # Remove duplicates
    reg_df = reg_df.dropna(subset=keep_cols)

    if len(reg_df) < 50:
        return pd.DataFrame(), {"N": len(reg_df), "Error": "Too few obs"}

    reg_df["const"] = 1.0
    for col in [dv, iv] + controls:
        reg_df[col] = reg_df[col].astype(float)

    exog = ["const", iv] + controls

    try:
        # Use speaker_id (composite key) for Speaker FE - per Addendum A
        absorb_df = reg_df[[speaker_col, "file_name"]].copy()
        absorb_df[speaker_col] = (
            absorb_df[speaker_col].astype("category").cat.codes
        )
        absorb_df["file_name"] = absorb_df["file_name"].astype("category").cat.codes

        mod = AbsorbingLS(
            dependent=reg_df[dv],
            exog=reg_df[exog],
            absorb=absorb_df,
            drop_absorbed=True,
        )

        # CORRECTED clustering per Addendum C: M2 clusters by (Firm, Call), not (Firm, CEO)
        if cluster_by_call:
            clusters = reg_df[["gvkey", "file_name"]].copy()
            clusters["gvkey"] = clusters["gvkey"].astype("category").cat.codes
            clusters["file_name"] = clusters["file_name"].astype("category").cat.codes
        else:
            # Original: cluster by firm + CEO (for robustness comparison)
            clusters = reg_df[["gvkey", "ceo_id"]].copy()
            clusters["gvkey"] = clusters["gvkey"].astype("category").cat.codes
            clusters["ceo_id"] = clusters["ceo_id"].astype("category").cat.codes
        res = mod.fit(cov_type="clustered", clusters=clusters)

        # Build full coefficient table
        params = res.params.copy()
        std_errs = res.std_errors.copy()
        tstats = res.tstats.copy()
        pvalues = res.pvalues.copy()

        coef_df = pd.DataFrame({
            "variable": params.index,
            "coef": params.values,
            "se": std_errs.values,
            "tstat": tstats.values,
            "pval": pvalues.values,
        })
        coef_df = coef_df.reset_index(drop=True)

        # Rename const to Intercept
        coef_df.loc[coef_df["variable"] == "const", "variable"] = "Intercept"

        diagnostics = {
            "N": int(res.nobs),
            "n_calls": int(reg_df["file_name"].nunique()),
            "n_speakers": int(reg_df[speaker_col].nunique()),
            "r2": round(res.rsquared, 4) if res.rsquared is not None else np.nan,
            "cluster_type": "Firm+Call" if cluster_by_call else "Firm+CEO",
        }

        return coef_df, diagnostics

    except Exception as e:
        return pd.DataFrame(), {"N": len(reg_df), "Error": str(e)}


def add_stars(pval: float) -> str:
    """Add significance stars based on p-value."""
    if pd.isna(pval):
        return ""
    if pval < 0.01:
        return "$^{***}$"
    elif pval < 0.05:
        return "$^{**}$"
    elif pval < 0.10:
        return "$^{*}$"
    return ""


def format_coef_se(coef: float, se: float, pval: float) -> Tuple[str, str]:
    """Format coefficient with stars and standard error in parentheses."""
    if pd.isna(coef) or pd.isna(se):
        return "", ""

    stars = add_stars(pval)
    # Coefficient: 4 decimal places with stars
    coef_str = f"{coef:.4f}{stars}"
    # Standard error: 4 decimal places in parentheses
    se_str = f"({se:.4f})"

    return coef_str, se_str


def generate_accounting_review_latex(
    results: Dict[str, Dict[str, Any]],
    model_order: List[str],
    variable_order: List[str],
    variable_labels: Dict[str, str],
    out_path: Path,
    caption: str = "Tone-at-the-Top Transmission (H\\_TT)",
    label: str = "tab:tone_at_top_full",
):
    """
    Generate Accounting Review style LaTeX table with full regression results.

    Each column is a model, each row is a variable.
    Coefficients are shown with significance stars.
    Standard errors are shown in parentheses below coefficients.
    """
    lines = []

    # Determine number of columns
    n_models = len(model_order)

    # Create clean model labels for columns
    model_labels = []
    sample_labels = []
    for model_key in model_order:
        parts = model_key.split("_", 1)
        sample = parts[0]
        model = parts[1] if len(parts) > 1 else model_key
        # Clean up model name
        model_clean = model.replace(" (H_TT1 Realtime)", "").replace(" (H_TT2 Turns)", "")
        model_labels.append(model_clean)
        sample_labels.append(sample)

    # Table header
    lines.append("\\begin{table}[htbp]")
    lines.append("\\centering")
    lines.append("\\caption{" + caption + "}")
    lines.append("\\label{" + label + "}")
    lines.append("\\footnotesize")
    lines.append("\\setlength{\\tabcolsep}{4pt}")  # Tighter column spacing
    lines.append("\\begin{tabular}{l" + "c" * n_models + "}")
    lines.append("\\toprule")

    # Sample row (grouped header) with cmidrule
    # We have 3 samples × 2 models = 6 columns
    sample_row = " & \\multicolumn{2}{c}{Main} & \\multicolumn{2}{c}{Finance} & \\multicolumn{2}{c}{Utility} \\\\"
    lines.append(sample_row)
    # Add cmidrule under each sample group
    lines.append("\\cmidrule(lr){2-3} \\cmidrule(lr){4-5} \\cmidrule(lr){6-7}")

    # Model row
    model_row = " & M1 & M2 & M1 & M2 & M1 & M2 \\\\"
    lines.append(model_row)
    lines.append("\\midrule")

    # Variable rows
    for var in variable_order:
        var_label = variable_labels.get(var, var)
        row_vals = []

        for model_key in model_order:
            if model_key not in results:
                row_vals.append("")
                continue

            model_res = results[model_key]
            coef_df = model_res.get("coefficients", pd.DataFrame())

            if coef_df.empty:
                row_vals.append("")
                continue

            # Find the variable in coefficients
            match = coef_df[coef_df["variable"] == var]
            if len(match) == 0:
                row_vals.append("")
                continue

            coef = match.iloc[0]["coef"]
            se = match.iloc[0]["se"]
            pval = match.iloc[0]["pval"]

            coef_str, se_str = format_coef_se(coef, se, pval)
            row_vals.append(coef_str)

        # Coefficient row
        lines.append(f"{var_label} & " + " & ".join(row_vals) + " \\\\")

        # Standard error row
        se_vals = []
        for model_key in model_order:
            if model_key not in results:
                se_vals.append("")
                continue

            model_res = results[model_key]
            coef_df = model_res.get("coefficients", pd.DataFrame())

            if coef_df.empty:
                se_vals.append("")
                continue

            match = coef_df[coef_df["variable"] == var]
            if len(match) == 0:
                se_vals.append("")
                continue

            se = match.iloc[0]["se"]
            if pd.isna(se):
                se_vals.append("")
            else:
                se_vals.append(f"({se:.4f})")

        lines.append(" & " + " & ".join(se_vals) + " \\\\")

    # Separator
    lines.append("\\midrule")

    # Diagnostics rows
    diag_labels = {
        "N": "Observations",
        "n_entities": "N Firms",
        "n_time": "N Quarters",
        "n_calls": "N Calls",
        "n_speakers": "N Speakers",
        "r2_within": "Within R$^2$",
        "r2": "R$^2$",
    }

    diag_keys = ["N", "n_entities", "n_time", "n_calls", "n_speakers", "r2_within", "r2"]

    for diag_key in diag_keys:
        diag_label = diag_labels.get(diag_key, diag_key)

        vals = []
        has_any = False
        for model_key in model_order:
            if model_key not in results:
                vals.append("")
                continue

            diag = results[model_key].get("diagnostics", {})
            val = diag.get(diag_key)

            if val is None or (isinstance(val, float) and np.isnan(val)):
                vals.append("")
            else:
                has_any = True
                if isinstance(val, int):
                    vals.append(f"{val:,}")
                else:
                    vals.append(f"{val:.4f}")

        if has_any:
            lines.append(f"{diag_label} & " + " & ".join(vals) + " \\\\")

    # Fixed effects rows - determine which FEs each model has
    lines.append("\\midrule")

    # Build FE rows dynamically
    firm_fe = []
    yq_fe = []
    call_fe = []
    speaker_fe = []

    for model_key in model_order:
        if model_key not in results:
            firm_fe.append("")
            yq_fe.append("")
            call_fe.append("")
            speaker_fe.append("")
            continue

        model_res = results[model_key]
        coef_df = model_res.get("coefficients", pd.DataFrame())

        if coef_df.empty:
            firm_fe.append("")
            yq_fe.append("")
            call_fe.append("")
            speaker_fe.append("")
            continue

        # Model 1 (call-level) has Firm FE + Year-Quarter FE
        # Model 2 (turn-level) has Call FE + Speaker FE
        if "M1" in model_key:
            firm_fe.append("Yes")
            yq_fe.append("Yes")
            call_fe.append("No")
            speaker_fe.append("No")
        else:
            firm_fe.append("Yes")  # Clustering still uses firm
            yq_fe.append("No")
            call_fe.append("Yes")
            speaker_fe.append("Yes")

    lines.append("Firm FE & " + " & ".join(firm_fe) + " \\\\")
    lines.append("Year-Quarter FE & " + " & ".join(yq_fe) + " \\\\")
    lines.append("Call FE & " + " & ".join(call_fe) + " \\\\")
    lines.append("Speaker FE & " + " & ".join(speaker_fe) + " \\\\")

    # Notes
    lines.append("\\bottomrule")
    lines.append(f"\\multicolumn{{{n_models + 1}}}{{l}}{{\\parbox{{\\linewidth}}{{\\footnotesize \\textit{{Notes:}} Standard errors (two-way clustered by Firm $\\times$ CEO) in parentheses.}}}} \\\\")
    lines.append(f"\\multicolumn{{{n_models + 1}}}{{l}}{{\\parbox{{\\linewidth}}{{\\footnotesize $^{{***}}$ p$<$0.01, $^{{**}}$ p$<$0.05, $^{{*}}$ p$<$0.10.}}}} \\\\")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"  Generated Accounting Review style table: {out_path}")


def generate_summary_latex(
    results: Dict[str, Dict[str, Any]],
    model_order: List[str],
    iv_variable: str,
    out_path: Path,
    caption: str = "Tone-at-the-Top Transmission (H\\_TT) - Summary",
    label: str = "tab:tone_at_top",
):
    """Generate summary LaTeX table with only the main IV coefficient."""
    latex = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{" + caption + "}",
        "\\label{" + label + "}",
        "\\begin{tabular}{llrrrrr}",
        "\\toprule",
        "Sample & Model & Coef & t-stat & p-value & N & Adj R$^2$ \\\\",
        "\\midrule",
    ]

    for model_key in model_order:
        if model_key not in results:
            continue

        model_res = results[model_key]
        coef_df = model_res.get("coefficients", pd.DataFrame())
        diag = model_res.get("diagnostics", {})

        if coef_df.empty:
            continue

        # Find the main IV
        match = coef_df[coef_df["variable"] == iv_variable]
        if len(match) == 0:
            continue

        coef = match.iloc[0]["coef"]
        tstat = match.iloc[0]["tstat"]
        pval = match.iloc[0]["pval"]
        n = diag.get("N", 0)

        # R2 - use r2_within for Model 1, r2 for Model 2
        r2 = diag.get("r2_within", diag.get("r2", np.nan))

        # Format numbers
        coef_str = f"{coef:.4f}" if pd.notna(coef) else ""
        tstat_str = f"{tstat:.2f}" if pd.notna(tstat) else ""
        pval_str = f"{pval:.4f}" if pd.notna(pval) else ""
        n_str = f"{int(n):,}" if pd.notna(n) else ""
        r2_str = f"{r2:.4f}" if pd.notna(r2) else ""

        # Add significance stars
        stars = ""
        if pd.notna(pval):
            p = float(pval)
            if p < 0.01:
                stars = "$^{***}$"
            elif p < 0.05:
                stars = "$^{**}$"
            elif p < 0.10:
                stars = "$^{*}$"

        # Parse sample and model from key
        parts = model_key.split("_", 1)
        sample = parts[0]
        model = parts[1] if len(parts) > 1 else model_key

        latex.append(
            f"{sample} & {model} & {coef_str}{stars} & {tstat_str} & {pval_str} & {n_str} & {r2_str} \\\\"
        )

    latex.extend(
        [
            "\\bottomrule",
            "\\multicolumn{7}{l}{\\footnotesize \\textit{Notes:} $^{***}$ p$<$0.01, $^{**}$ p$<$0.05, $^{*}$ p$<$0.10.} \\\\",
            "\\end{tabular}",
            "\\end{table}",
        ]
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(latex) + "\n")

    print(f"  Generated summary table: {out_path}")


def generate_report_md(
    results: Dict[str, Dict[str, Any]],
    model_order: List[str],
    out_path: Path,
):
    """Generate Markdown report with full results."""
    lines = []
    lines.append("# H_TT: Tone-at-the-Top Transmission Results\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    for model_key in model_order:
        if model_key not in results:
            continue

        model_res = results[model_key]
        coef_df = model_res.get("coefficients", pd.DataFrame())
        diag = model_res.get("diagnostics", {})

        lines.append(f"\n## {model_key}\n")

        if coef_df.empty:
            lines.append("*Error: No results*\n")
            continue

        # Coefficient table
        lines.append("### Coefficients\n")
        lines.append("| Variable | Coef | SE | t-stat | p-value |")
        lines.append("|----------|------|-----|--------|---------|")

        for _, row in coef_df.iterrows():
            var = row["variable"]
            coef = f"{row['coef']:.4f}" if pd.notna(row["coef"]) else ""
            se = f"{row['se']:.4f}" if pd.notna(row["se"]) else ""
            tstat = f"{row['tstat']:.2f}" if pd.notna(row["tstat"]) else ""
            pval = f"{row['pval']:.4f}" if pd.notna(row["pval"]) else ""
            lines.append(f"| {var} | {coef} | {se} | {tstat} | {pval} |")

        # Diagnostics
        lines.append("\n### Diagnostics\n")
        for k, v in diag.items():
            if isinstance(v, int):
                lines.append(f"- **{k}:** {v:,}")
            elif isinstance(v, float) and not np.isnan(v):
                lines.append(f"- **{k}:** {v:.4f}")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  Generated report: {out_path}")


# =============================================================================
# NEW FUNCTIONS FOR ROBUSTNESS TESTS (per revision plan)
# =============================================================================

def wild_cluster_bootstrap(
    df: pd.DataFrame,
    dv: str,
    iv: str,
    cluster_col: str,
    controls: Optional[List[str]] = None,
    n_bootstrap: int = 9999,
    seed: int = 42,
) -> Dict[str, float]:
    """
    Wild cluster bootstrap for small samples (Utility, Finance).
    Uses Rademacher weights (±1) for residuals.
    Returns bootstrap p-value and confidence interval.
    Reference: Cameron, Gelbach, & Miller (2008)
    """
    if controls is None:
        controls = []

    np.random.seed(seed)

    # Prepare data
    df = df.dropna(subset=[dv, iv, cluster_col] + controls).copy()
    df["const"] = 1.0

    # Get unique clusters
    clusters = df[cluster_col].unique()
    n_clusters = len(clusters)

    if n_clusters < 10:
        print(f"  WARNING: Only {n_clusters} clusters, bootstrap may be unreliable")

    # Run baseline regression (OLS, no FE for simplicity)
    X = df[["const", iv] + controls].values
    y = df[dv].values

    try:
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        resid = y - X @ beta
        baseline_coef = beta[1]  # Index 1 is the IV coefficient
    except Exception:
        return {"p_value": np.nan, "ci_lower": np.nan, "ci_upper": np.nan, "error": "Baseline regression failed"}

    # Bootstrap
    boot_coefs = []
    for _ in range(n_bootstrap):
        # Draw Rademacher weights (±1) for each cluster
        weights = np.random.choice([-1, 1], size=n_clusters)
        weight_map = dict(zip(clusters, weights))

        # Create wild residuals
        wild_resid = np.array([weight_map[c] * r for c, r in zip(df[cluster_col], resid)])

        # Create bootstrap outcome
        y_boot = X @ beta + wild_resid

        # Re-estimate
        try:
            beta_boot = np.linalg.lstsq(X, y_boot, rcond=None)[0]
            boot_coefs.append(beta_boot[1])
        except Exception:
            continue

    if len(boot_coefs) < n_bootstrap * 0.9:
        return {"p_value": np.nan, "ci_lower": np.nan, "ci_upper": np.nan, "error": "Too many bootstrap failures"}

    boot_coefs = np.array(boot_coefs)

    # Two-sided p-value
    p_value = np.mean(np.abs(boot_coefs) >= np.abs(baseline_coef))

    # Confidence interval (percentile method)
    ci_lower = np.percentile(boot_coefs, 2.5)
    ci_upper = np.percentile(boot_coefs, 97.5)

    return {
        "p_value": p_value,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "n_bootstrap": len(boot_coefs),
        "baseline_coef": baseline_coef,
    }


def permutation_test_optimized(
    df: pd.DataFrame,
    dv: str,
    iv: str,
    group_col: str,
    controls: Optional[List[str]] = None,
    n_permutations: int = 500,
    seed: int = 42,
) -> Dict[str, float]:
    """
    Permutation test: shuffle IV within groups (calls).
    Optimized to avoid full dataframe copies.
    Returns empirical p-value.
    """
    if controls is None:
        controls = []

    np.random.seed(seed)

    df = df.dropna(subset=[dv, iv, group_col] + controls).copy()
    df["const"] = 1.0

    # Pre-compute baseline
    X = df[["const", iv] + controls].values
    y = df[dv].values
    baseline_coef = np.linalg.lstsq(X, y, rcond=None)[0][1]

    # Pre-extract values
    iv_values = df[iv].values
    groups = df[group_col].values
    unique_groups = np.unique(groups)

    # Get indices for each group
    group_indices = {g: np.where(groups == g)[0] for g in unique_groups}

    perm_coefs = []
    for _ in range(n_permutations):
        # Shuffle within groups (in-place on a copy of iv_values)
        iv_shuffled = iv_values.copy()
        for g in unique_groups:
            idx = group_indices[g]
            iv_shuffled[idx] = np.random.permutation(iv_shuffled[idx])

        # Re-estimate
        X_perm = np.column_stack([np.ones(len(df)), iv_shuffled] + [df[c].values for c in controls])
        try:
            coef = np.linalg.lstsq(X_perm, y, rcond=None)[0][1]
            perm_coefs.append(coef)
        except Exception:
            continue

    perm_coefs = np.array(perm_coefs)

    # Two-sided empirical p-value
    p_value = np.mean(np.abs(perm_coefs) >= np.abs(baseline_coef))

    return {
        "p_value": p_value,
        "baseline_coef": baseline_coef,
        "perm_mean": np.mean(perm_coefs) if len(perm_coefs) > 0 else np.nan,
        "perm_std": np.std(perm_coefs) if len(perm_coefs) > 0 else np.nan,
        "n_permutations": len(perm_coefs),
    }


def compute_economic_significance(
    turns_panel: pd.DataFrame,
    coef: float,
    iv: str = "IHS_CEO_Prior_QA_Unc",
    dv: str = "IHS_NonCEO_Turn_Unc",
) -> Dict[str, float]:
    """
    Translate IHS coefficient to interpretable economic magnitude.
    """
    df = turns_panel.dropna(subset=[iv, dv])

    iv_sd = df[iv].std()
    iv_p25 = df[iv].quantile(0.25)
    iv_p75 = df[iv].quantile(0.75)
    dv_sd = df[dv].std()
    dv_mean = df[dv].mean()

    # One SD change in IV
    delta_1sd = coef * iv_sd

    # 25th to 75th percentile change
    delta_iqr = coef * (iv_p75 - iv_p25)

    # As % of DV SD
    pct_of_sd = (delta_1sd / dv_sd) * 100

    # Approximate basis points (IHS ≈ log for small values)
    bps_1sd = delta_1sd * 100  # IHS units to approximate bps

    return {
        "iv_sd": iv_sd,
        "dv_sd": dv_sd,
        "delta_1sd": delta_1sd,
        "delta_iqr": delta_iqr,
        "pct_of_dv_sd": pct_of_sd,
        "approx_bps_1sd": bps_1sd,
        "iv_p25": iv_p25,
        "iv_p75": iv_p75,
        "dv_mean": dv_mean,
    }


def run_m2_specifications(
    df: pd.DataFrame, sample_name: str = ""
) -> Dict[str, Dict[str, Any]]:
    """Run all M2 specifications for robustness testing."""
    results = {}

    specs = {
        # Baseline (current)
        "baseline": {
            "iv": "IHS_CEO_Prior_QA_Unc",
            "controls": [],
            "description": "Expanding mean (baseline)",
        },
        # Local lags (address time trend concern)
        "lag1": {
            "iv": "IHS_CEO_Unc_Lag1",
            "controls": [],
            "description": "Last CEO turn only",
        },
        "roll2": {
            "iv": "IHS_CEO_Unc_Roll2",
            "controls": [],
            "description": "Rolling 2 CEO turns",
        },
        "roll3": {
            "iv": "IHS_CEO_Unc_Roll3",
            "controls": [],
            "description": "Rolling 3 CEO turns",
        },
        "exp_decay": {
            "iv": "IHS_CEO_Unc_ExpDecay",
            "controls": [],
            "description": "Exp. weighted (alpha=0.5)",
        },
        # With time controls
        "with_turn_linear": {
            "iv": "IHS_CEO_Prior_QA_Unc",
            "controls": ["turn_index"],
            "description": "Baseline + turn index",
        },
        "with_turn_quad": {
            "iv": "IHS_CEO_Prior_QA_Unc",
            "controls": ["turn_index", "turn_index_sq"],
            "description": "Baseline + quadratic time",
        },
        # With analyst controls
        "with_analyst": {
            "iv": "IHS_CEO_Prior_QA_Unc",
            "controls": ["IHS_Analyst_Unc"],
            "description": "Baseline + analyst uncertainty",
        },
        "full_controls": {
            "iv": "IHS_CEO_Prior_QA_Unc",
            "controls": ["turn_index", "turn_index_sq", "IHS_Analyst_Unc"],
            "description": "Baseline + all controls",
        },
        # Placebo: future CEO uncertainty should NOT predict
        "placebo_lead": {
            "iv": "IHS_CEO_Unc_Lead1",
            "controls": [],
            "description": "Placebo: FUTURE CEO uncertainty",
        },
    }

    for spec_name, spec in specs.items():
        # Check if IV column exists
        if spec["iv"] not in df.columns:
            print(f"  Skipping {spec_name}: {spec['iv']} not in data")
            continue

        # For specs with controls, check if controls exist
        missing_controls = [c for c in spec["controls"] if c not in df.columns]
        if missing_controls:
            print(f"  Skipping {spec_name}: missing controls {missing_controls}")
            continue

        coef_df, diag = run_turn_level_model_full(
            df, "IHS_NonCEO_Turn_Unc", spec["iv"], spec["controls"]
        )
        results[spec_name] = {
            "coefficients": coef_df,
            "diagnostics": diag,
            "description": spec["description"],
        }

    return results


def main():
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent.parent

    if args.dry_run:
        print("Dry run OK")
        return

    # Load panels
    panel_dir = get_latest_output_dir(
        root / "outputs" / "variables" / "tone_at_top",
        required_file="tone_at_top_panel.parquet",
    )
    call_panel = pd.read_parquet(panel_dir / "tone_at_top_panel.parquet")
    turns_panel = pd.read_parquet(panel_dir / "tone_at_top_turns_panel.parquet")

    # Add start_date to turns_panel if missing
    if "start_date" not in turns_panel.columns:
        turns_panel = turns_panel.merge(
            call_panel[["file_name", "start_date"]].drop_duplicates(),
            on="file_name",
            how="left",
        )

    # Prep variables - Call panel
    call_panel["IHS_CFO_QA_Unc"] = asinh(call_panel["CFO_QA_Uncertainty_pct"])
    call_panel["IHS_CEO_QA_Unc"] = asinh(call_panel["CEO_QA_Uncertainty_pct"])
    call_panel["IHS_CEO_Pres_Unc"] = asinh(call_panel["CEO_Pres_Uncertainty_pct"])

    # Prep variables - Turns panel
    turns_panel["IHS_NonCEO_Turn_Unc"] = asinh(turns_panel["Turn_Uncertainty_pct"])
    turns_panel["IHS_CEO_Prior_QA_Unc"] = asinh(turns_panel["CEO_Prior_QA_Unc"])
    turns_panel["IHS_CEO_Pres_Unc"] = asinh(turns_panel["CEO_Pres_Uncertainty_pct"])

    # NEW: IHS transforms for CEO lag variables (robustness tests)
    for col in ["CEO_Unc_Lag1", "CEO_Unc_Roll2", "CEO_Unc_Roll3", "CEO_Unc_ExpDecay", "CEO_Unc_Lead1"]:
        if col in turns_panel.columns:
            turns_panel[f"IHS_{col}"] = asinh(turns_panel[col])

    # NEW: IHS transform for analyst uncertainty
    if "Preceding_Analyst_Unc" in turns_panel.columns:
        turns_panel["IHS_Analyst_Unc"] = asinh(turns_panel["Preceding_Analyst_Unc"])

    # Control specifications per Addendum D
    # Primary controls (NO CEO same-call uncertainty - for causal interpretation)
    call_controls_primary = [
        "Size", "BM", "Lev", "ROA", "StockRet", "MarketRet", "EPS_Growth", "SurpDec",
    ]

    # Full controls (WITH CEO same-call - for "holding constant" interpretation)
    call_controls_full = [
        "Size", "BM", "Lev", "ROA", "StockRet", "MarketRet", "EPS_Growth", "SurpDec",
        "IHS_CEO_QA_Unc", "IHS_CEO_Pres_Unc",  # CEO same-call controls (bad controls?)
    ]

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = root / "outputs" / "econometric" / "tone_at_top" / timestamp
    ensure_output_dir(out_dir)

    # ------------------------------------------------------------------
    # Summary Statistics (call-level, Main/Finance/Utility)
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Generating summary statistics (call-level panel)")
    print("=" * 60)
    summary_vars = [
        {"col": v["col"], "label": v["label"]}
        for v in SUMMARY_STATS_VARS
        if v["col"] in call_panel.columns
    ]
    make_summary_stats_table(
        df=call_panel,
        variables=summary_vars,
        sample_names=["Main", "Finance", "Utility"],
        sample_col="sample",
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics — Tone-at-the-Top",
        label="tab:summary_stats_h10",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    # Store all results
    all_results = {}

    # Model order for tables
    model_order = [
        "Main_M1 (H_TT1 Realtime)",
        "Main_M2 (H_TT2 Turns)",
        "Finance_M1 (H_TT1 Realtime)",
        "Finance_M2 (H_TT2 Turns)",
        "Utility_M1 (H_TT1 Realtime)",
        "Utility_M2 (H_TT2 Turns)",
    ]

    # Variable order for full table (Model 1 controls)
    variable_order_m1 = [
        "ClarityStyle_Realtime",
        "Size",
        "BM",
        "Lev",
        "ROA",
        "StockRet",
        "MarketRet",
        "EPS_Growth",
        "SurpDec",
        "IHS_CEO_QA_Unc",
        "IHS_CEO_Pres_Unc",
        "Intercept",
    ]

    variable_labels = {
        "ClarityStyle_Realtime": "CEO Style (Realtime)",
        "IHS_CEO_Prior_QA_Unc": "CEO Prior Q\\&A Unc.",
        "Size": "Size",
        "BM": "Book-to-Market",
        "Lev": "Leverage",
        "ROA": "ROA",
        "StockRet": "Stock Return",
        "MarketRet": "Market Return",
        "EPS_Growth": "EPS Growth",
        "SurpDec": "Earnings Surprise",
        "IHS_CEO_QA_Unc": "CEO Q\\&A Unc.",
        "IHS_CEO_Pres_Unc": "CEO Pres. Unc.",
        "Intercept": "Intercept",
    }

    for sample in ["Main", "Finance", "Utility"]:
        print(f"\nProcessing {sample} Sample...")

        call_sub = (
            call_panel
            if sample == "Main"
            else call_panel[call_panel["sample"] == sample]
        )
        turns_sub = (
            turns_panel
            if sample == "Main"
            else turns_panel[turns_panel["sample"] == sample]
        )

        # M1: H_TT1 (Real-time style, 4-call rolling window, min=4)
        # PRIMARY SPECIFICATION: Without CEO same-call controls (per Addendum D)
        print(f"  Running M1 (H_TT1 Realtime) - Primary (no CEO controls)...")
        m1_coef, m1_diag = run_call_level_model_full(
            call_sub, "IHS_CFO_QA_Unc", "ClarityStyle_Realtime", call_controls_primary
        )

        m1_key = f"{sample}_M1 (H_TT1 Realtime)"
        all_results[m1_key] = {
            "coefficients": m1_coef,
            "diagnostics": m1_diag,
        }

        if not m1_coef.empty:
            print(f"    N={m1_diag.get('N', 0):,}, R²={m1_diag.get('r2_within', 'N/A')}")

        # M2: H_TT2 (Speaker turns) - with corrected clustering (Firm+Call)
        print(f"  Running M2 (H_TT2 Turns)...")
        m2_coef, m2_diag = run_turn_level_model_full(
            turns_sub, "IHS_NonCEO_Turn_Unc", "IHS_CEO_Prior_QA_Unc"
        )

        m2_key = f"{sample}_M2 (H_TT2 Turns)"
        all_results[m2_key] = {
            "coefficients": m2_coef,
            "diagnostics": m2_diag,
        }

        if not m2_coef.empty:
            print(f"    N={m2_diag.get('N', 0):,}, R²={m2_diag.get('r2', 'N/A')}")
            # Economic significance
            iv_coef = m2_coef[m2_coef["variable"] == "IHS_CEO_Prior_QA_Unc"]["coef"].values
            if len(iv_coef) > 0:
                econ_sig = compute_economic_significance(
                    turns_sub, iv_coef[0], "IHS_CEO_Prior_QA_Unc", "IHS_NonCEO_Turn_Unc"
                )
                all_results[m2_key]["economic_significance"] = econ_sig

        # M2 Robustness: Run all specifications for this sample
        print(f"  Running M2 robustness specifications...")
        m2_robust = run_m2_specifications(turns_sub, sample)
        for spec_name, spec_result in m2_robust.items():
            robust_key = f"{sample}_M2_{spec_name}"
            all_results[robust_key] = spec_result

        # Wild bootstrap for small samples (Utility, Finance) - per Addendum E
        if sample in ["Utility", "Finance"] and len(turns_sub) >= 50:
            print(f"  Running wild cluster bootstrap for {sample}...")
            n_firms = turns_sub["gvkey"].nunique()
            if n_firms < 100:  # Only for small samples
                boot_result = wild_cluster_bootstrap(
                    turns_sub,
                    "IHS_NonCEO_Turn_Unc",
                    "IHS_CEO_Prior_QA_Unc",
                    "gvkey",
                    n_bootstrap=9999,
                )
                all_results[f"{sample}_M2_bootstrap"] = {
                    "bootstrap": boot_result,
                    "description": "Wild cluster bootstrap (Rademacher)",
                }
                print(f"    Bootstrap p-value: {boot_result.get('p_value', 'N/A'):.4f}")


    # Generate outputs
    print("\nGenerating outputs...")

    # Generate full Accounting Review style table
    # Combined variable order for both models
    full_var_order = [
        "ClarityStyle_Realtime",
        "IHS_CEO_Prior_QA_Unc",
        "Size",
        "BM",
        "Lev",
        "ROA",
        "StockRet",
        "MarketRet",
        "EPS_Growth",
        "SurpDec",
        "IHS_CEO_QA_Unc",
        "IHS_CEO_Pres_Unc",
        "Intercept",
    ]

    generate_accounting_review_latex(
        all_results,
        model_order,
        full_var_order,
        variable_labels,
        out_dir / "tone_at_top_full.tex",
    )

    # Generate summary table (backward compatible)
    generate_summary_latex(
        all_results,
        model_order,
        "ClarityStyle_Realtime",  # Will find appropriate IV per model
        out_dir / "tone_at_top_table.tex",
    )

    # Generate markdown report
    generate_report_md(all_results, model_order, out_dir / "report.md")

    # Save model diagnostics CSV (linearmodels-specific)
    diag_rows = []
    for model_key in model_order:
        if model_key not in all_results:
            continue
        model_res = all_results[model_key]
        diag = model_res.get("diagnostics", {})
        coef_df = model_res.get("coefficients", pd.DataFrame())
        if not coef_df.empty:
            # M1 has n_entities, M2 has n_calls/n_speakers
            n_entities = diag.get("n_entities") or diag.get("n_calls") or diag.get("n_speakers")
            r2 = diag.get("r2_within") or diag.get("r2")
            diag_rows.append({
                "model": model_key,
                "n_obs": diag.get("N"),
                "n_entities": n_entities,
                "rsquared": r2,
                "rsquared_adj": None,  # linearmodels does not provide
                "fvalue": None,
                "f_pvalue": None,
                "aic": None,
                "bic": None,
            })
    if diag_rows:
        diag_df = pd.DataFrame(diag_rows)
        diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False)
        print(f"  Saved: model_diagnostics.csv ({len(diag_df)} rows)")

    # Save individual CSV files (backward compatible format)
    for sample in ["Main", "Finance", "Utility"]:
        sample_results = []
        for model_key in model_order:
            if not model_key.startswith(sample):
                continue
            if model_key not in all_results:
                continue

            model_res = all_results[model_key]
            coef_df = model_res.get("coefficients", pd.DataFrame())
            diag = model_res.get("diagnostics", {})

            if coef_df.empty:
                continue

            # Get main IV coefficient
            iv = "ClarityStyle_Realtime" if "M1" in model_key else "IHS_CEO_Prior_QA_Unc"
            match = coef_df[coef_df["variable"] == iv]

            if len(match) == 0:
                continue

            parts = model_key.split("_", 1)
            sample_name = parts[0]
            model_name = parts[1] if len(parts) > 1 else model_key

            row = {
                "Sample": sample_name,
                "Model": model_name,
                "Coef": round(match.iloc[0]["coef"], 4),
                "t-stat": round(match.iloc[0]["tstat"], 2),
                "p-value": round(match.iloc[0]["pval"], 4),
                "N": diag.get("N", 0),
                "Adj_R2": diag.get("r2_within", diag.get("r2", np.nan)),
                "Error": diag.get("Error", ""),
            }
            sample_results.append(row)

        if sample_results:
            df = pd.DataFrame(sample_results)
            df.to_csv(out_dir / f"results_{sample.lower()}.csv", index=False)

    # Save full coefficient tables
    for model_key, model_res in all_results.items():
        coef_df = model_res.get("coefficients", pd.DataFrame())
        if not coef_df.empty:
            safe_key = model_key.replace(" ", "_").replace("(", "").replace(")", "")
            coef_df.to_csv(out_dir / f"coefficients_{safe_key}.csv", index=False)

    print(f"\nOutputs saved to {out_dir}")


if __name__ == "__main__":
    main()
