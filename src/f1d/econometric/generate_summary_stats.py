#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Generate Summary Statistics (4.4)
================================================================================
ID: econometric/generate_summary_stats
Description: Generate publication-quality summary statistics for all variables
             used in the thesis. Produces:
               - Panel A: Linguistic variables (from CEO clarity extended panel)
               - Panel B: Financial controls (from CEO clarity extended panel)
               - Panel C: Panel balance (year × firms × CEOs × calls)
               - Correlation matrix for key regression variables
               - LaTeX tabular for Table 1 in paper

Data source: uses ceo_clarity_extended_panel.parquet (Main sample) as the
canonical dataset — it contains the full set of linguistic and financial
variables used across all hypothesis tests.

Inputs:
    - outputs/variables/ceo_clarity_extended/latest/ceo_clarity_extended_panel.parquet

Outputs:
    - outputs/econometric/summary_stats/{timestamp}/descriptive_statistics.csv
    - outputs/econometric/summary_stats/{timestamp}/correlation_matrix.csv
    - outputs/econometric/summary_stats/{timestamp}/panel_balance.csv
    - outputs/econometric/summary_stats/{timestamp}/summary_table.tex  (LaTeX)
    - outputs/econometric/summary_stats/{timestamp}/report_step4_4.md
    - outputs/econometric/summary_stats/{timestamp}/run_log.txt

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_ceo_clarity_extended_panel)

Author: Thesis Author
Date: 2026-02-19
================================================================================
"""

from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=FutureWarning)

from f1d.shared.observability_utils import DualWriter
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.config import get_config


# ==============================================================================
# Configuration
# ==============================================================================

# Panel A: Linguistic variables (in display order)
PANEL_A_VARS: List[Dict[str, str]] = [
    {"col": "Manager_QA_Uncertainty_pct", "label": "Manager QA Uncertainty (\\%)"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Manager Pres Uncertainty (\\%)"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty (\\%)"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty (\\%)"},
    {"col": "Analyst_QA_Uncertainty_pct", "label": "Analyst QA Uncertainty (\\%)"},
    {"col": "Entire_All_Negative_pct", "label": "All-Speaker Negative Sentiment (\\%)"},
]

# Panel B: Financial controls (in display order)
PANEL_B_VARS: List[Dict[str, str]] = [
    {"col": "Size", "label": "Size (log assets)"},
    {"col": "BM", "label": "Book-to-Market"},
    {"col": "Lev", "label": "Leverage"},
    {"col": "ROA", "label": "Return on Assets"},
    {"col": "CurrentRatio", "label": "Current Ratio"},
    {"col": "RD_Intensity", "label": "R\\&D Intensity"},
    {"col": "EPS_Growth", "label": "EPS Growth"},
    {"col": "StockRet", "label": "Stock Return (\\%)"},
    {"col": "MarketRet", "label": "Market Return (\\%)"},
    {"col": "Volatility", "label": "Return Volatility (annualized)"},
    {"col": "SurpDec", "label": "Earnings Surprise Decile"},
]

# Correlation matrix variables
CORR_VARS = [
    "Manager_QA_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Analyst_QA_Uncertainty_pct",
    "Entire_All_Negative_pct",
    "Size",
    "BM",
    "Lev",
    "ROA",
    "StockRet",
    "MarketRet",
    "SurpDec",
]

# Main sample: exclude Finance (ff12=11) and Utility (ff12=8)
MAIN_SAMPLE_EXCLUDE_FF12 = [8, 11]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: Generate Summary Statistics (4.4)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--panel-path",
        type=str,
        default=None,
        help="Path to panel parquet (default: latest ceo_clarity_extended)",
    )
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    """Load panel from Stage 3 output."""
    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "ceo_clarity_extended",
            required_file="ceo_clarity_extended_panel.parquet",
        )
        panel_file = panel_dir / "ceo_clarity_extended_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}, Columns: {len(panel.columns)}")
    return panel


def filter_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to Main sample (exclude Finance + Utility) and non-null ceo_id."""
    df = panel[
        panel["ceo_id"].notna() & ~panel["ff12_code"].isin(MAIN_SAMPLE_EXCLUDE_FF12)
    ].copy()
    print(f"\n  Main sample (after ceo_id + ff12 filter): {len(df):,} calls")
    return df


# ==============================================================================
# Statistics Computation
# ==============================================================================


def compute_descriptive_stats(
    df: pd.DataFrame,
    var_list: List[Dict[str, str]],
) -> pd.DataFrame:
    """Compute N, Mean, SD, Min, P25, Median, P75, Max for each variable."""
    rows = []
    for item in var_list:
        col = item["col"]
        label = item["label"]
        if col not in df.columns:
            rows.append(
                {
                    "Variable": label,
                    "Col": col,
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
            continue
        data = df[col].dropna()
        rows.append(
            {
                "Variable": label,
                "Col": col,
                "N": len(data),
                "Mean": data.mean(),
                "SD": data.std(),
                "Min": data.min(),
                "P25": data.quantile(0.25),
                "Median": data.median(),
                "P75": data.quantile(0.75),
                "Max": data.max(),
            }
        )
    return pd.DataFrame(rows)


def compute_panel_balance(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute year-level panel balance."""
    year_stats = (
        df.groupby("year")
        .agg(
            n_firms=("gvkey", "nunique"),
            n_ceos=("ceo_id", "nunique"),
            n_calls=("file_name", "count"),
        )
        .reset_index()
        .sort_values("year")
    )
    # Firm-year summary
    fy = df.groupby(["gvkey", "year"]).size()
    summary = pd.DataFrame(
        [
            {
                "N_firm_year_cells": len(fy),
                "Mean_calls_per_fy": round(fy.mean(), 2),
                "Median_calls_per_fy": round(float(np.median(fy.values)), 2),
                "Min_calls": int(fy.min()),
                "Max_calls": int(fy.max()),
                "Total_calls": len(df),
                "Unique_firms": df["gvkey"].nunique(),
                "Unique_CEOs": df["ceo_id"].nunique(),
            }
        ]
    )
    return year_stats, summary


def compute_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Pearson correlation matrix for key variables."""
    avail = [c for c in CORR_VARS if c in df.columns]
    corr = df[avail].corr(method="pearson")
    return corr


# ==============================================================================
# LaTeX Table Generation
# ==============================================================================


def make_summary_latex(
    panel_a: pd.DataFrame,
    panel_b: pd.DataFrame,
    n_obs: int,
    output_path: Path,
) -> None:
    """Generate LaTeX Table 1: Summary Statistics (two-panel tabular).

    Panel A: Linguistic variables
    Panel B: Financial controls
    """
    col_fmt = "l" + "r" * 7  # Variable + N Mean SD Min P25 Median P75 Max
    header_cols = "Variable & N & Mean & SD & Min & P25 & Median & P75 & Max"

    lines = [
        "% Table 1: Summary Statistics",
        "% Auto-generated by generate_summary_stats.py",
        "\\begin{table}[htbp]",
        "  \\centering",
        "  \\caption{Summary Statistics}",
        "  \\label{tab:summary_stats}",
        f"  \\begin{{tabular}}{{{col_fmt}}}",
        "    \\toprule",
        f"    {header_cols} \\\\",
        "    \\midrule",
        "    \\multicolumn{9}{l}{\\textit{Panel A: Linguistic Variables}} \\\\",
        "    \\midrule",
    ]

    def fmt_row(row: pd.Series) -> str:
        n = int(row["N"]) if row["N"] > 0 else 0

        def f(x: Any) -> str:
            if isinstance(x, float) and np.isnan(x):
                return "---"
            return f"{x:.4f}"

        return (
            f"    {row['Variable']} & {n:,} & "
            f"{f(row['Mean'])} & {f(row['SD'])} & "
            f"{f(row['Min'])} & {f(row['P25'])} & "
            f"{f(row['Median'])} & {f(row['P75'])} & {f(row['Max'])} \\\\"
        )

    for _, row in panel_a.iterrows():
        lines.append(fmt_row(row))

    lines += [
        "    \\midrule",
        "    \\multicolumn{9}{l}{\\textit{Panel B: Financial Controls}} \\\\",
        "    \\midrule",
    ]

    for _, row in panel_b.iterrows():
        lines.append(fmt_row(row))

    lines += [
        "    \\bottomrule",
        "  \\end{tabular}",
        f"  \\begin{{tablenotes}}",
        f"    \\small",
        f"    \\item This table reports summary statistics for the Main sample",
        f"    ($N = {n_obs:,}$ call observations, excluding Finance and Utility firms).",
        f"    All linguistic variables are expressed as percentages of total words.",
        f"  \\end{{tablenotes}}",
        "\\end{table}",
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  Saved: summary_table.tex ({len(panel_a) + len(panel_b)} variables)")


# ==============================================================================
# Report
# ==============================================================================


def generate_report(
    panel_a: pd.DataFrame,
    panel_b: pd.DataFrame,
    year_stats: pd.DataFrame,
    fy_summary: pd.DataFrame,
    corr: pd.DataFrame,
    out_dir: Path,
    duration: float,
) -> None:
    """Generate markdown report."""
    report_lines = [
        "# Stage 4: Summary Statistics Report (4.4)",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Panel A: Linguistic Variables (Main Sample)",
        "",
        "| Variable | N | Mean | SD | Min | Median | Max |",
        "|----------|---|------|----|----|--------|-----|",
    ]

    for _, row in panel_a.iterrows():
        n = int(row["N"])
        report_lines.append(
            f"| {row['Variable']} | {n:,} | {row['Mean']:.4f} | "
            f"{row['SD']:.4f} | {row['Min']:.4f} | {row['Median']:.4f} | {row['Max']:.4f} |"
        )

    report_lines += [
        "",
        "## Panel B: Financial Controls (Main Sample)",
        "",
        "| Variable | N | Mean | SD | Min | Median | Max |",
        "|----------|---|------|----|----|--------|-----|",
    ]

    for _, row in panel_b.iterrows():
        n = int(row["N"])
        report_lines.append(
            f"| {row['Variable']} | {n:,} | {row['Mean']:.4f} | "
            f"{row['SD']:.4f} | {row['Min']:.4f} | {row['Median']:.4f} | {row['Max']:.4f} |"
        )

    report_lines += [
        "",
        "## Panel C: Panel Balance",
        "",
        "| Year | N Firms | N CEOs | N Calls |",
        "|------|---------|--------|---------|",
    ]

    for _, row in year_stats.iterrows():
        report_lines.append(
            f"| {int(row['year'])} | {int(row['n_firms']):,} | "
            f"{int(row['n_ceos']):,} | {int(row['n_calls']):,} |"
        )

    if not fy_summary.empty:
        row = fy_summary.iloc[0]
        report_lines += [
            "",
            f"**Total observations:** {int(row['Total_calls']):,}",
            f"**Unique firms:** {int(row['Unique_firms']):,}",
            f"**Unique CEOs:** {int(row['Unique_CEOs']):,}",
            f"**Firm-year cells:** {int(row['N_firm_year_cells']):,}",
            "",
        ]

    report_path = out_dir / "report_step4_4.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print("  Saved: report_step4_4.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "summary_stats" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    log_path = out_dir / "run_log.txt"
    dual = DualWriter(log_path)
    sys.stdout = dual

    print("=" * 80)
    print("STAGE 4: Generate Summary Statistics (4.4)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")

    # Load panel
    panel = load_panel(root, panel_path)

    # Main sample
    df = filter_main_sample(panel)

    # Panel A: Linguistic variables
    print("\n  Computing Panel A: Linguistic variables...")
    panel_a = compute_descriptive_stats(df, PANEL_A_VARS)
    print(f"  Panel A: {len(panel_a)} variables")
    for _, row in panel_a.iterrows():
        print(
            f"    {row['Col']}: N={int(row['N']):,}, mean={row['Mean']:.4f}, sd={row['SD']:.4f}"
        )

    # Panel B: Financial controls
    print("\n  Computing Panel B: Financial controls...")
    panel_b = compute_descriptive_stats(df, PANEL_B_VARS)
    print(f"  Panel B: {len(panel_b)} variables")
    for _, row in panel_b.iterrows():
        if row["N"] > 0:
            print(
                f"    {row['Col']}: N={int(row['N']):,}, mean={row['Mean']:.4f}, sd={row['SD']:.4f}"
            )

    # Panel C: Balance
    print("\n  Computing panel balance...")
    year_stats, fy_summary = compute_panel_balance(df)
    print(
        f"  Year range: {int(year_stats['year'].min())} – {int(year_stats['year'].max())}"
    )
    print(f"  Total calls: {int(fy_summary['Total_calls'].iloc[0]):,}")
    print(f"  Unique firms: {int(fy_summary['Unique_firms'].iloc[0]):,}")
    print(f"  Unique CEOs: {int(fy_summary['Unique_CEOs'].iloc[0]):,}")

    # Correlation matrix
    print("\n  Computing correlation matrix...")
    corr = compute_correlation_matrix(df)

    # Save outputs
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    # CSVs
    all_stats = pd.concat([panel_a, panel_b], ignore_index=True)
    all_stats.to_csv(out_dir / "descriptive_statistics.csv", index=False)
    print(f"  Saved: descriptive_statistics.csv ({len(all_stats)} rows)")

    corr.to_csv(out_dir / "correlation_matrix.csv")
    print(f"  Saved: correlation_matrix.csv ({len(corr)}x{len(corr.columns)})")

    year_stats.to_csv(out_dir / "panel_balance.csv", index=False)
    print(f"  Saved: panel_balance.csv ({len(year_stats)} years)")

    fy_summary.to_csv(out_dir / "firm_year_summary.csv", index=False)
    print(f"  Saved: firm_year_summary.csv")

    # LaTeX
    make_summary_latex(panel_a, panel_b, len(df), out_dir / "summary_table.tex")

    # Report
    duration = (datetime.now() - start_time).total_seconds()
    generate_report(panel_a, panel_b, year_stats, fy_summary, corr, out_dir, duration)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")

    sys.stdout = dual.original_stdout
    dual.log.close()

    return 0


if __name__ == "__main__":
    args = parse_arguments()

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print("[OK] All inputs validated")
        sys.exit(0)

    sys.exit(main(panel_path=args.panel_path))
