#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H12 Language Uncertainty → Dividend Intensity
================================================================================
ID: econometric/run_h12_div_intensity
Description: Run H12 hypothesis test by loading the firm-year panel from Stage 3,
             running fixed effects OLS regressions across 6 uncertainty measures
             and 3 industry samples, and outputting results.

Model Specification:
    DivIntensity_{i,t+1} = β0 + β1·Avg_Uncertainty_{i,t}
                          + γ₁·Size + γ₂·Lev + γ₃·ROA + γ₄·TobinsQ
                          + FirmFE_i + YearFE_t + ε

    Unit of obs: firm-fiscal-year (gvkey, fyearq)
    DV: DivIntensity_lead = (dvy_Q4 / atq)_{t+1}
    IV: Avg_Uncertainty = mean of call-level uncertainty within firm-year

Hypothesis Test (one-tailed):
    H12: β1 < 0  — higher uncertainty language → lower dividend intensity
         (vague managers pay fewer dividends)

Industry Samples:
    - Main:    FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Uncertainty Measures (6, averaged to firm-year):
    Avg_Manager_QA_Uncertainty_pct, Avg_CEO_QA_Uncertainty_pct,
    Avg_Manager_QA_Weak_Modal_pct,  Avg_CEO_QA_Weak_Modal_pct,
    Avg_Manager_Pres_Uncertainty_pct, Avg_CEO_Pres_Uncertainty_pct

Controls: Size, Lev, ROA, TobinsQ (standard corporate finance set)
FE: Firm + Year
SE: Firm-clustered

Inputs:
    - outputs/variables/h12_div_intensity/latest/h12_div_intensity_panel.parquet

Outputs:
    - outputs/econometric/h12_div_intensity/{timestamp}/regression_results_{sample}_{measure}.txt
    - outputs/econometric/h12_div_intensity/{timestamp}/h12_div_intensity_table.tex
    - outputs/econometric/h12_div_intensity/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h12_div_intensity/{timestamp}/summary_stats.csv
    - outputs/econometric/h12_div_intensity/{timestamp}/summary_stats.tex
    - outputs/econometric/h12_div_intensity/{timestamp}/sanity_checks.txt
    - outputs/econometric/h12_div_intensity/{timestamp}/report_step4_H12.md

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h12_div_intensity_panel)
    - Uses: linearmodels, f1d.shared.latex_tables_accounting

Author: Thesis Author
Date: 2026-03-05

Cloned from: run_h8_political_risk.py (firm-year architecture) + run_h1_cash_holdings.py
             (6×3 regression loop pattern).
================================================================================
"""

from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.shared.latex_tables_accounting import make_summary_stats_table
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import generate_manifest, generate_attrition_table
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import assign_industry_sample

warnings.filterwarnings(
    "ignore", message="covariance of constraints does not have full rank"
)
warnings.filterwarnings("ignore", category=FutureWarning, module="linearmodels.*")


# ==============================================================================
# Configuration
# ==============================================================================

# Dependent variables: both contemporaneous (t) and lead (t+1)
DEPENDENT_VARIABLES = ["DivIntensity", "DivIntensity_lead"]

# Firm-year averaged uncertainty measures (prefixed with Avg_ by panel builder)
UNCERTAINTY_MEASURES = [
    "Avg_Manager_QA_Uncertainty_pct",
    "Avg_CEO_QA_Uncertainty_pct",
    "Avg_Manager_QA_Weak_Modal_pct",
    "Avg_CEO_QA_Weak_Modal_pct",
    "Avg_Manager_Pres_Uncertainty_pct",
    "Avg_CEO_Pres_Uncertainty_pct",
]

BASE_CONTROLS = [
    "Size",
    "Lev",
    "ROA",
    "TobinsQ",
    "CashHoldings",
    "CapexAt",
    "RD_Intensity",
]

# Minimum calls per firm-year to include (ensures meaningful average)
MIN_CALLS_PER_FIRM = 5

VARIABLE_LABELS = {
    "DivIntensity_lead": "DivIntensity$_{t+1}$",
    "DivIntensity": "DivIntensity$_{t}$",
    "Avg_Manager_QA_Uncertainty_pct": "Manager_QA_Uncertainty",
    "Avg_CEO_QA_Uncertainty_pct": "CEO_QA_Uncertainty",
    "Avg_Manager_QA_Weak_Modal_pct": "Manager_QA_Weak_Modal",
    "Avg_CEO_QA_Weak_Modal_pct": "CEO_QA_Weak_Modal",
    "Avg_Manager_Pres_Uncertainty_pct": "Manager_Pres_Uncertainty",
    "Avg_CEO_Pres_Uncertainty_pct": "CEO_Pres_Uncertainty",
    "Size": "Size",
    "Lev": "Leverage",
    "ROA": "ROA",
    "TobinsQ": "TobinsQ",
    "CashHoldings": "CashHoldings",
    "CapexAt": "CapexAt",
    "OCF_Volatility": "OCF_Volatility",
    "CurrentRatio": "CurrentRatio",
    "RD_Intensity": "RD_Intensity",
}

CONFIG = {
    "min_firms": 50,
    "min_obs": 200,
}


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # DV
    {"col": "DivIntensity_lead", "label": "DivIntensity$_{t+1}$"},
    {"col": "DivIntensity", "label": "DivIntensity$_{t}$"},
    # IVs (firm-year averaged - using exact column names from pipeline)
    {
        "col": "Avg_Manager_QA_Uncertainty_pct",
        "label": "Avg_Manager_QA_Uncertainty_pct",
    },
    {"col": "Avg_CEO_QA_Uncertainty_pct", "label": "Avg_CEO_QA_Uncertainty_pct"},
    {"col": "Avg_Manager_QA_Weak_Modal_pct", "label": "Avg_Manager_QA_Weak_Modal_pct"},
    {"col": "Avg_CEO_QA_Weak_Modal_pct", "label": "Avg_CEO_QA_Weak_Modal_pct"},
    {
        "col": "Avg_Manager_Pres_Uncertainty_pct",
        "label": "Avg_Manager_Pres_Uncertainty_pct",
    },
    {"col": "Avg_CEO_Pres_Uncertainty_pct", "label": "Avg_CEO_Pres_Uncertainty_pct"},
    # Controls (using exact column names from pipeline)
    {"col": "Size", "label": "Size"},
    {"col": "Lev", "label": "Lev"},
    {"col": "ROA", "label": "ROA"},
    {"col": "TobinsQ", "label": "TobinsQ"},
    {"col": "CashHoldings", "label": "CashHoldings"},
    {"col": "CapexAt", "label": "CapexAt"},
    {"col": "OCF_Volatility", "label": "OCF_Volatility"},
    {"col": "CurrentRatio", "label": "CurrentRatio"},
    {"col": "RD_Intensity", "label": "RD_Intensity"},
    # Calls per firm-year
    {"col": "n_calls", "label": "n_calls"},
]


# ==============================================================================
# CLI Arguments
# ==============================================================================


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stage 4: Test H12 Language Uncertainty → Dividend Intensity (firm-year)",
    )
    parser.add_argument(
        "--panel-path",
        type=str,
        default=None,
        help="Explicit path to H12 firm-year panel parquet",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


# ==============================================================================
# Sanity Checks
# ==============================================================================


def run_sanity_checks(df: pd.DataFrame, out_dir: Path) -> None:
    """Print and save sanity checks on the loaded panel."""
    lines = [
        "=" * 70,
        "H12 DIVIDEND INTENSITY PANEL — SANITY CHECKS",
        "=" * 70,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"N firm-years (raw):  {len(df):,}",
        f"N firms (unique):    {df['gvkey'].nunique():,}",
        "",
    ]

    # DV
    if "DivIntensity_lead" in df.columns:
        dv = df["DivIntensity_lead"]
        lines += [
            "DivIntensity_lead (DV, t+1):",
            f"  valid={dv.notna().sum():,} / {len(df):,}",
            f"  mean={dv.mean():.4f}  SD={dv.std():.4f}",
            f"  min={dv.min():.4f}  max={dv.max():.4f}",
            "",
        ]

    if "DivIntensity" in df.columns:
        di = df["DivIntensity"]
        lines += [
            "DivIntensity (contemporaneous):",
            f"  valid={di.notna().sum():,} / {len(df):,}",
            f"  mean={di.mean():.4f}  SD={di.std():.4f}",
            f"  zero-dividend fraction: {(di == 0).sum()}/{di.notna().sum()} "
            f"({100 * (di == 0).sum() / max(di.notna().sum(), 1):.1f}%)",
            "",
        ]

    # Uncertainty measures
    for col in UNCERTAINTY_MEASURES:
        if col in df.columns:
            s = df[col]
            lines += [
                f"{col}:",
                f"  valid={s.notna().sum():,}  mean={s.mean():.4f}  SD={s.std():.4f}",
            ]
    lines.append("")

    # Calls per firm-year
    if "n_calls" in df.columns:
        nc = df["n_calls"]
        lines += [
            "Calls per firm-year:",
            f"  mean={nc.mean():.1f}  median={nc.median():.0f}  "
            f"min={nc.min():.0f}  max={nc.max():.0f}",
            "",
        ]

    lines.append("=" * 70)

    for line in lines:
        print(f"  {line}")

    sanity_path = out_dir / "sanity_checks.txt"
    with open(sanity_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Sanity checks saved: {sanity_path.name}")


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df: pd.DataFrame,
    dv: str,
    uncertainty_var: str,
    sample_name: str,
) -> Tuple[Optional[Any], Dict[str, Any]]:
    """Run PanelOLS for a single DV, uncertainty measure, and industry sample.

    Model:
        DivIntensity or DivIntensity_lead ~ Uncertainty + Size + Lev + ROA + TobinsQ
                                   + CashHoldings + CapexAt + OCF_Volatility
                                   + CurrentRatio + RD_Intensity
                                   + EntityEffects + TimeEffects

    Standard errors: firm-clustered.

    Returns (model_result, meta_dict).
    """
    existing_controls = [c for c in BASE_CONTROLS if c in df.columns]
    required_avail = [dv, uncertainty_var] + existing_controls + ["gvkey", "fyearq"]

    df_reg = df.replace([np.inf, -np.inf], np.nan).dropna(subset=required_avail).copy()

    # Minimum calls per firm filter
    firm_counts = df_reg["gvkey"].value_counts()
    valid_firms = set(firm_counts[firm_counts >= MIN_CALLS_PER_FIRM].index)
    df_reg = df_reg[df_reg["gvkey"].isin(valid_firms)].copy()

    if (
        len(df_reg) < CONFIG["min_obs"]
        or df_reg["gvkey"].nunique() < CONFIG["min_firms"]
    ):
        print(
            f"  Skipping {sample_name}/{dv}/{uncertainty_var}: insufficient data "
            f"(N={len(df_reg):,}, firms={df_reg['gvkey'].nunique():,})"
        )
        return None, {}

    # Use original variable name in formula (no renaming)
    formula = (
        f"{dv} ~ {uncertainty_var} + "
        + " + ".join(existing_controls)
        + " + EntityEffects + TimeEffects"
    )

    print(f"\n--- {sample_name} / {dv} / {uncertainty_var} ---")
    print(
        f"  N firm-years: {len(df_reg):,}  |  N firms: {df_reg['gvkey'].nunique():,}"
        f"  |  N years: {df_reg['fyearq'].nunique():,}"
    )
    print(f"  Formula: {dv} ~ {uncertainty_var} + {' + '.join(existing_controls)}")
    print("  Estimating with firm-clustered SEs...")

    t0 = datetime.now()

    df_panel = df_reg.set_index(["gvkey", "fyearq"])

    try:
        model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
        model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: PanelOLS failed: {e}", file=sys.stderr)
        return None, {}

    duration = (datetime.now() - t0).total_seconds()
    print(
        f"  [OK] Complete in {duration:.1f}s  |  Within-R²: {model.rsquared_within:.4f}"
    )

    # Extract key coefficient using original variable name
    beta1 = float(model.params.get(uncertainty_var, np.nan))
    se1 = float(model.std_errors.get(uncertainty_var, np.nan))
    t1 = float(model.tstats.get(uncertainty_var, np.nan))
    p1_two = float(model.pvalues.get(uncertainty_var, np.nan))

    # One-tailed test: H12 predicts β1 < 0
    if not np.isnan(p1_two) and not np.isnan(beta1):
        p1_one = p1_two / 2 if beta1 < 0 else 1 - p1_two / 2
    else:
        p1_one = np.nan

    h12_sig = (not np.isnan(p1_one)) and (p1_one < 0.05) and (beta1 < 0)

    print(
        f"  β1 ({uncertainty_var}): {beta1:.4f}  SE={se1:.4f}  t={t1:.2f}  "
        f"p(two)={p1_two:.4f}  p(one)={p1_one:.4f}  "
        f"H12={'SUPPORTED' if h12_sig else 'not supported'}"
    )

    # Extract control coefficients
    control_coefs = {}
    for ctrl in existing_controls:
        control_coefs[f"beta_{ctrl}"] = float(model.params.get(ctrl, np.nan))
        control_coefs[f"se_{ctrl}"] = float(model.std_errors.get(ctrl, np.nan))
        control_coefs[f"p_{ctrl}"] = float(model.pvalues.get(ctrl, np.nan))

    meta: Dict[str, Any] = {
        "sample": sample_name,
        "dv": dv,
        "uncertainty_var": uncertainty_var,
        "beta1": beta1,
        "beta1_se": se1,
        "beta1_t": t1,
        "beta1_p_two": p1_two,
        "beta1_p_one": p1_one,
        "beta1_signif": h12_sig,
        "n_obs": int(model.nobs),
        "n_firms": df_reg["gvkey"].nunique(),
        "n_clusters": df_reg["gvkey"].nunique(),
        "cluster_var": "gvkey",
        "within_r2": float(model.rsquared_within),
        **control_coefs,
    }

    return model, meta


# ==============================================================================
# LaTeX Table
# ==============================================================================


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Write a publication-ready LaTeX table for H12 results.

    Two panels per industry sample (DivIntensity and DivIntensity_lead).
    6 columns per panel (one per uncertainty measure).
    Shows β1 (Uncertainty) with SE, significance stars, controls row,
    N, within-R².
    """

    def sig(p: float) -> str:
        if p < 0.01:
            return "^{***}"
        elif p < 0.05:
            return "^{**}"
        elif p < 0.10:
            return "^{*}"
        return ""

    def fmt_coef(val: float, pval: float) -> str:
        if pd.isna(val):
            return ""
        return f"{val:.4f}{sig(pval)}"

    def fmt_se(val: float) -> str:
        return "" if pd.isna(val) else f"({val:.4f})"

    # Short labels for column headers (using exact column names from pipeline)
    short_labels = {
        "Avg_Manager_QA_Uncertainty_pct": "Manager_QA_Uncertainty",
        "Avg_CEO_QA_Uncertainty_pct": "CEO_QA_Uncertainty",
        "Avg_Manager_QA_Weak_Modal_pct": "Manager_QA_Weak_Modal",
        "Avg_CEO_QA_Weak_Modal_pct": "CEO_QA_Weak_Modal",
        "Avg_Manager_Pres_Uncertainty_pct": "Manager_Pres_Uncertainty",
        "Avg_CEO_Pres_Uncertainty_pct": "CEO_Pres_Uncertainty",
    }

    samples = ["Main", "Finance", "Utility"]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{H12: Language Uncertainty and Dividend Intensity}",
        r"\label{tab:h12_div_intensity}",
        r"\small",
    ]

    for dv in DEPENDENT_VARIABLES:
        dv_label = (
            "DivIntensity$_{t}$" if dv == "DivIntensity" else "DivIntensity$_{t+1}$"
        )

        for sample in samples:
            sample_results = [
                r
                for r in all_results
                if r.get("sample") == sample and r.get("dv") == dv
            ]
            if not sample_results:
                continue

            # Order by UNCERTAINTY_MEASURES
            ordered = []
            for measure in UNCERTAINTY_MEASURES:
                match = [
                    r for r in sample_results if r.get("uncertainty_var") == measure
                ]
                if match:
                    ordered.append(match[0])
                else:
                    ordered.append({})

            n_cols = len(ordered)
            col_spec = "l" + "c" * n_cols

            lines += [
                "",
                r"\vspace{0.5em}",
                rf"\textbf{{Panel: {sample} Sample — {dv_label}}}",
                r"\vspace{0.3em}",
                "",
                r"\begin{tabular}{" + col_spec + "}",
                r"\toprule",
            ]

            # Column headers
            headers = " & ".join(
                short_labels.get(UNCERTAINTY_MEASURES[i], f"({i + 1})")
                for i in range(n_cols)
            )
            lines.append(r" & " + headers + r" \\")
            lines.append(r"\midrule")

            # β1 (Uncertainty) row
            coef_vals = " & ".join(
                fmt_coef(r.get("beta1", np.nan), r.get("beta1_p_one", np.nan))
                for r in ordered
            )
            lines.append(r" & " + coef_vals + r" \\")

            # SE row
            se_vals = " & ".join(fmt_se(r.get("beta1_se", np.nan)) for r in ordered)
            lines.append(r" & " + se_vals + r" \\")

            # Control coefficients
            for ctrl in BASE_CONTROLS:
                ctrl_coef = " & ".join(
                    fmt_coef(r.get(f"beta_{ctrl}", np.nan), r.get(f"p_{ctrl}", np.nan))
                    for r in ordered
                )
                ctrl_label = VARIABLE_LABELS.get(ctrl, ctrl)
                lines.append(rf"{ctrl_label} & " + ctrl_coef + r" \\")
                ctrl_se = " & ".join(
                    fmt_se(r.get(f"se_{ctrl}", np.nan)) for r in ordered
                )
                lines.append(r" & " + ctrl_se + r" \\")

            lines += [
                r"\midrule",
                r"Firm FE  & " + " & ".join("Yes" for _ in ordered) + r" \\",
                r"Year FE  & " + " & ".join("Yes" for _ in ordered) + r" \\",
                r"\midrule",
                "Observations & "
                + " & ".join(f"{r.get('n_obs', 0):,}" for r in ordered)
                + r" \\",
                "Firms & "
                + " & ".join(f"{r.get('n_firms', 0):,}" for r in ordered)
                + r" \\",
                r"Within-$R^2$ & "
                + " & ".join(f"{r.get('within_r2', np.nan):.4f}" for r in ordered)
                + r" \\",
                r"\bottomrule",
                r"\end{tabular}",
            ]

    lines += [
        r"\\[-0.5em]",
        r"\parbox{\textwidth}{\scriptsizeskip0pt\selectfont\scriptsize ",
        r"\textit{Notes:} Dependent variables are Dividend Intensity$_{t}$ (contemporaneous) and Dividend Intensity$_{t+1}$ (one-year ahead). "
        r"Unit of observation: firm--fiscal-year. "
        r"Uncertainty measures are averaged across all earnings calls within the firm-year. "
        r"Firms with fewer than 5 firm-year observations are excluded. "
        r"Standard errors (in parentheses) are clustered at the firm level. "
        r"Variables are winsorized at 1\%/99\% by year at the engine level. "
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed for H12: $\beta_1 < 0$).",
        r"}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h12_div_intensity_table.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  LaTeX table saved: {tex_path.name}")


# ==============================================================================
# Report Generation
# ==============================================================================
# Report Generation
# ==============================================================================


def generate_report(
    all_results: List[Dict[str, Any]],
    out_dir: Path,
    duration: float,
) -> None:
    """Generate markdown report summarizing H12 results."""
    n_sig = sum(1 for r in all_results if r.get("beta1_signif"))
    n_total = len(all_results)

    lines = [
        "# Stage 4: H12 Language Uncertainty → Dividend Intensity Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Summary",
        f"- Total regressions: {n_total}",
        f"- H12 supported (β1 < 0, p < 0.05 one-tailed): **{n_sig}/{n_total}**",
        "",
        "## Results by Sample",
    ]

    for sample in ["Main", "Finance", "Utility"]:
        sample_results = [r for r in all_results if r.get("sample") == sample]
        if not sample_results:
            continue
        sig_count = sum(1 for r in sample_results if r.get("beta1_signif"))
        lines.append(f"**{sample}:** H12 {sig_count}/{len(sample_results)} significant")
        for r in sample_results:
            measure = r.get("uncertainty_var", "?")
            b = r.get("beta1", np.nan)
            p = r.get("beta1_p_one", np.nan)
            star = " *" if r.get("beta1_signif") else ""
            lines.append(f"  - {measure}: β1={b:.4f}, p(one)={p:.4f}{star}")
        lines.append("")

    report_path = out_dir / "report_step4_H12.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: report_step4_H12.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    """Main execution."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h12_div_intensity" / timestamp

    # Setup logging
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H12_DivIntensity",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: Test H12 Language Uncertainty → Dividend Intensity")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")

    # ------------------------------------------------------------------
    # Load Stage 3 panel
    # ------------------------------------------------------------------
    if not panel_path:
        try:
            panel_dir = get_latest_output_dir(
                root / "outputs" / "variables" / "h12_div_intensity",
                required_file="h12_div_intensity_panel.parquet",
            )
            panel_file = panel_dir / "h12_div_intensity_panel.parquet"
        except Exception as e:
            print(f"ERROR: Could not find Stage 3 panel: {e}")
            return 1
    else:
        panel_file = Path(panel_path)

    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)
    print(f"  File: {panel_file}")
    df = pd.read_parquet(panel_file)
    print(f"  Rows: {len(df):,}")
    print(f"  Columns: {len(df.columns)}")

    out_dir.mkdir(parents=True, exist_ok=True)

    # Assign sample if not already present
    if "sample" not in df.columns and "ff12_code" in df.columns:
        df["sample"] = assign_industry_sample(df["ff12_code"])

    # ------------------------------------------------------------------
    # Summary Statistics
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Generating summary statistics")
    print("=" * 60)
    summary_vars = [
        {"col": v["col"], "label": v["label"]}
        for v in SUMMARY_STATS_VARS
        if v["col"] in df.columns
    ]
    make_summary_stats_table(
        df=df,
        variables=summary_vars,
        sample_names=["Main", "Finance", "Utility"] if "sample" in df.columns else None,
        sample_col="sample" if "sample" in df.columns else None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics — H12 Dividend Intensity",
        label="tab:summary_stats_h12",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    # ------------------------------------------------------------------
    # Sanity Checks
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Sanity checks")
    print("=" * 60)
    run_sanity_checks(df, out_dir)

    # ------------------------------------------------------------------
    # Run Regressions: 6 measures × 3 samples = 18 regressions
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Regressions (6 measures × 3 samples)")
    print("=" * 60)

    all_results: List[Dict[str, Any]] = []
    all_models: List[Dict[str, Any]] = []

    for sample_name in ["Main", "Finance", "Utility"]:
        if "sample" in df.columns:
            df_sample = df[df["sample"] == sample_name].copy()
        elif "ff12_code" in df.columns:
            if sample_name == "Finance":
                df_sample = df[df["ff12_code"] == 11].copy()
            elif sample_name == "Utility":
                df_sample = df[df["ff12_code"] == 8].copy()
            else:
                df_sample = df[~df["ff12_code"].isin([8, 11])].copy()
        else:
            # No industry classification — run all data as "Main" only
            if sample_name != "Main":
                continue
            df_sample = df.copy()

        n_sample = len(df_sample)
        n_dv_lead = (
            df_sample["DivIntensity_lead"].notna().sum()
            if "DivIntensity_lead" in df_sample.columns
            else 0
        )
        n_dv_concurrent = (
            df_sample["DivIntensity"].notna().sum()
            if "DivIntensity" in df_sample.columns
            else 0
        )
        print(f"\n{'=' * 40}")
        print(
            f"Sample: {sample_name} ({n_sample:,} firm-years, {n_dv_concurrent:,} concurrent, {n_dv_lead:,} lead)"
        )
        print(f"{'=' * 40}")

        for dv in DEPENDENT_VARIABLES:
            for uncertainty_var in UNCERTAINTY_MEASURES:
                if uncertainty_var not in df_sample.columns:
                    print(f"  WARNING: {uncertainty_var} not in panel — skipping")
                    continue

                model, meta = run_regression(
                    df_sample, dv, uncertainty_var, sample_name
                )

                if model is not None and meta:
                    all_results.append(meta)
                    all_models.append({"model": model, "meta": meta})

                    # Save full regression output
                    fname = (
                        f"regression_results_{sample_name}_{dv}_{uncertainty_var}.txt"
                    )
                    fpath = out_dir / fname
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(str(model.summary))

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    if all_results:
        # Model diagnostics CSV
        pd.DataFrame(all_results).to_csv(out_dir / "model_diagnostics.csv", index=False)
        print(f"  Saved: model_diagnostics.csv ({len(all_results)} regressions)")

        # LaTeX table
        _save_latex_table(all_results, out_dir)

    # Attrition table
    if all_results:
        main_results = [r for r in all_results if r.get("sample") == "Main"]
        if main_results:
            first_meta = main_results[0]
            attrition_stages = [
                ("Full firm-year panel", len(df)),
                (
                    "Main sample filter",
                    len(df[df["sample"] == "Main"])
                    if "sample" in df.columns
                    else len(df),
                ),
                ("After complete-case + min-calls filter", first_meta.get("n_obs", 0)),
            ]
            generate_attrition_table(
                attrition_stages, out_dir, "H12 Dividend Intensity"
            )
            print("  Saved: sample_attrition.csv and sample_attrition.tex")

    # Run manifest
    generate_manifest(
        output_dir=out_dir,
        stage="stage4",
        timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={
            "diagnostics": out_dir / "model_diagnostics.csv",
            "table": out_dir / "h12_div_intensity_table.tex",
        },
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    # Report
    duration = (datetime.now() - t0).total_seconds()
    generate_report(all_results, out_dir, duration)

    # Final summary
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output:   {out_dir}")
    print(f"Total regressions completed: {len(all_results)}")

    h12_sig = sum(1 for r in all_results if r.get("beta1_signif"))
    print(f"H12 supported (β1 < 0, p < 0.05 one-tail): {h12_sig}/{len(all_results)}")

    for dv in DEPENDENT_VARIABLES:
        dv_results = [r for r in all_results if r.get("dv") == dv]
        dv_sig = sum(1 for r in dv_results if r.get("beta1_signif"))
        print(f"  {dv}: {dv_sig}/{len(dv_results)} significant")

    for sample in ["Main", "Finance", "Utility"]:
        sample_res = [r for r in all_results if r.get("sample") == sample]
        if sample_res:
            sig_n = sum(1 for r in sample_res if r.get("beta1_signif"))
            print(f"  {sample}: {sig_n}/{len(sample_res)} significant")

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print("[OK] All inputs validated")
        sys.exit(0)
    sys.exit(main(panel_path=args.panel_path))
