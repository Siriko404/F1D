#!/usr/bin/env python3
"""
==============================================================================
STEP 4.4: Generate Summary Statistics
==============================================================================
ID: 4.4_GenerateSummaryStats
Description: Generate comprehensive summary statistics for analysis dataset.

Purpose:
    Generate comprehensive summary statistics for analysis dataset including
    descriptive statistics, correlation matrix, and panel balance diagnostics.

Inputs:
    - 4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - 4_Outputs/3_Financial_Features/latest/firm_controls_{year}.parquet
    - 4_Outputs/3_Financial_Features/latest/market_variables_{year}.parquet

Outputs:
    - 4_Outputs/4.1_CeoClarity/{timestamp}/descriptive_statistics.csv
    - 4_Outputs/4.1_CeoClarity/{timestamp}/correlation_matrix.csv
    - 4_Outputs/4.1_CeoClarity/{timestamp}/panel_balance.csv
    - 4_Outputs/4.1_CeoClarity/{timestamp}/summary_report.md

Deterministic: true
Dependencies:
    - Requires: Step 3.x
    - Uses: pandas, numpy

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

import argparse
import csv
import json
import sys as _sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

# Add script directory to Python path for shared imports
_script_dir = Path(__file__).parent.parent
_sys.path.insert(0, str(_script_dir))

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Import shared utilities
from f1d.shared.observability_utils import (
    DualWriter,
    analyze_missing_values,
    compute_file_checksum,
)
from f1d.shared.path_utils import (
    get_latest_output_dir,
)


def parse_arguments():
    """Parse command-line arguments for 4.4_GenerateSummaryStats.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 4.4: Generate Summary Statistics

Generates summary statistics and descriptive statistics
for all econometric analyses. Produces tables and plots
for results presentation.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    return parser.parse_args()


def check_prerequisites(root):
    """Validate all required inputs and prerequisite steps exist."""
    from f1d.shared.dependency_checker import validate_prerequisites

    required_files: Dict[str, Any] = {}

    required_steps = {
        "4.1_EstimateCeoClarity": "ceo_clarity_scores.parquet",
        "4.2_LiquidityRegressions": "liquidity_results.parquet",
        "4.3_TakeoverHazards": "takeover_results.parquet",
    }

    validate_prerequisites(required_files, required_steps)


# Data Loading Functions
# ==============================================================================


def load_manifest(manifest_path, stats=None):
    """Load sample manifest."""
    print("\nLoading manifest...")
    try:
        df = pd.read_parquet(manifest_path)
    except FileNotFoundError as e:
        print(f"ERROR: Manifest file not found: {e}", file=_sys.stderr)
        print(f"  File: {manifest_path}", file=_sys.stderr)
        _sys.exit(1)
    except PermissionError as e:
        print(f"ERROR: Permission denied reading manifest: {e}", file=_sys.stderr)
        print(f"  File: {manifest_path}", file=_sys.stderr)
        _sys.exit(1)
    except OSError as e:
        print(f"ERROR: OS error reading manifest: {e}", file=_sys.stderr)
        print(f"  File: {manifest_path}", file=_sys.stderr)
        _sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load manifest: {e}", file=_sys.stderr)
        print(f"  File: {manifest_path}", file=_sys.stderr)
        _sys.exit(1)

    print(f"  Manifest: {len(df):,} calls")

    if stats:
        stats["input"]["files"].append(str(manifest_path))
        stats["input"]["total_rows"] += len(df)
        stats["input"]["checksums"]["manifest"] = compute_file_checksum(manifest_path)

    return df


def load_linguistic_variables(linguistic_dir, year_start, year_end, stats=None):
    """Load and merge linguistic variables across years."""
    print("\nLoading linguistic variables...")

    dfs = []
    for year in range(year_start, year_end + 1):
        path = linguistic_dir / f"linguistic_variables_{year}.parquet"
        if not path.exists():
            print(f"  WARNING: Missing {path.name}")
            continue

        try:
            df = pd.read_parquet(path)
        except FileNotFoundError:
            print(f"  WARNING: File not found: {path.name}")
            continue
        except PermissionError as e:
            print(
                f"ERROR: Permission denied reading {path.name}: {e}", file=_sys.stderr
            )
            _sys.exit(1)
        except OSError as e:
            print(f"ERROR: OS error reading {path.name}: {e}", file=_sys.stderr)
            _sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to load {path.name}: {e}", file=_sys.stderr)
            _sys.exit(1)

        dfs.append(df)
        print(f"  {year}: {len(df):,} calls")

        if stats:
            stats["input"]["files"].append(str(path))
            stats["input"]["total_rows"] += len(df)
            stats["input"]["checksums"][f"linguistic_{year}"] = compute_file_checksum(
                path
            )

    if not dfs:
        print("ERROR: No linguistic variables files found", file=_sys.stderr)
        _sys.exit(1)

    return pd.concat(dfs, ignore_index=True)


def load_financial_controls(financial_dir, year_start, year_end, stats=None):
    """Load and merge financial controls across years."""
    print("\nLoading financial controls...")

    dfs = []
    for year in range(year_start, year_end + 1):
        path = financial_dir / f"firm_controls_{year}.parquet"
        if not path.exists():
            print(f"  WARNING: Missing {path.name}")
            continue

        try:
            df = pd.read_parquet(path)
        except FileNotFoundError:
            print(f"  WARNING: File not found: {path.name}")
            continue
        except PermissionError as e:
            print(
                f"ERROR: Permission denied reading {path.name}: {e}", file=_sys.stderr
            )
            _sys.exit(1)
        except OSError as e:
            print(f"ERROR: OS error reading {path.name}: {e}", file=_sys.stderr)
            _sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to load {path.name}: {e}", file=_sys.stderr)
            _sys.exit(1)

        dfs.append(df)

        if stats:
            stats["input"]["files"].append(str(path))
            stats["input"]["checksums"][f"firm_controls_{year}"] = (
                compute_file_checksum(path)
            )

    if not dfs:
        print("ERROR: No financial controls files found", file=_sys.stderr)
        _sys.exit(1)

    return pd.concat(dfs, ignore_index=True)


def load_market_variables(financial_dir, year_start, year_end, stats=None):
    """Load and merge market variables across years."""
    print("\nLoading market variables...")

    dfs = []
    for year in range(year_start, year_end + 1):
        path = financial_dir / f"market_variables_{year}.parquet"
        if not path.exists():
            print(f"  WARNING: Missing {path.name}")
            continue

        try:
            df = pd.read_parquet(path)
        except FileNotFoundError:
            print(f"  WARNING: File not found: {path.name}")
            continue
        except PermissionError as e:
            print(
                f"ERROR: Permission denied reading {path.name}: {e}", file=_sys.stderr
            )
            _sys.exit(1)
        except OSError as e:
            print(f"ERROR: OS error reading {path.name}: {e}", file=_sys.stderr)
            _sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to load {path.name}: {e}", file=_sys.stderr)
            _sys.exit(1)

        dfs.append(df)

        if stats:
            stats["input"]["files"].append(str(path))
            stats["input"]["checksums"][f"market_vars_{year}"] = compute_file_checksum(
                path
            )

    if not dfs:
        print("ERROR: No market variables files found", file=_sys.stderr)
        _sys.exit(1)

    return pd.concat(dfs, ignore_index=True)


# ==============================================================================
# Data Preparation Functions
# ==============================================================================


def prepare_analysis_data(manifest, linguistic, firm_controls, market_vars, stats=None):
    """Merge and prepare analysis dataset."""
    print("\n" + "=" * 60)
    print("Preparing analysis data")
    print("=" * 60)

    # Start with manifest
    df = manifest.copy()

    # Merge linguistic variables
    df = df.merge(linguistic, on=["file_name", "start_date"], how="inner")
    print(f"  After linguistic merge: {len(df):,}")

    # Merge financial controls
    df = df.merge(firm_controls, on=["file_name", "start_date"], how="inner")
    print(f"  After financial controls merge: {len(df):,}")

    # Merge market variables using left join with suffixes to preserve observations
    df = df.merge(
        market_vars,
        on=["file_name", "start_date", "year"],
        how="left",
        suffixes=("", "_mkt"),
    )
    print(f"  After market variables merge: {len(df):,}")

    print(f"\n  Total: {len(df):,} calls")
    print(f"  Unique CEOs: {df['ceo_id'].nunique():,}")
    print(f"  Unique firms: {df['gvkey'].nunique():,}")

    if stats:
        stats["processing"]["merge_steps"] = {
            "initial_manifest": len(manifest),
            "after_linguistic": len(df),
            "after_firm_controls": len(df),
            "after_market_vars": len(df),
        }
        stats["missing_values"] = analyze_missing_values(df)

    return df


def filter_complete_cases(df, stats=None):
    """Filter to complete cases for analysis."""
    print("\n" + "=" * 60)
    print("Filtering to complete cases")
    print("=" * 60)

    initial_n = len(df)

    # Filter to non-null ceo_id
    df = df[df["ceo_id"].notna()].copy()
    print(f"  After ceo_id filter: {len(df):,} / {initial_n:,}")

    if stats:
        stats["processing"]["ceo_id_filter"] = initial_n - len(df)

    # Define key variables for correlation matrix (these drive complete cases)
    key_vars = [
        "Manager_QA_Uncertainty_pct",
        "Manager_Pres_Uncertainty_pct",
        "Analyst_QA_Uncertainty_pct",
        "Entire_All_Negative_pct",
        "StockRet",
        "MarketRet",
        "EPS_Growth",
        "SurpDec",
    ]

    # Check which variables exist
    existing_vars = [v for v in key_vars if v in df.columns]
    missing_vars = [v for v in key_vars if v not in df.columns]

    if missing_vars:
        print(f"  WARNING: Missing variables: {missing_vars}")

    # Also require ceo_id, year, ff12_code for sample assignment
    required = existing_vars + ["ceo_id", "year", "ff12_code"]

    # Filter to complete cases (only key variables need to be non-NA)
    complete_mask = df[required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases filter: {len(df):,}")

    if stats:
        stats["processing"]["complete_cases_filter"] = initial_n - len(df)

    # Assign industry samples based on FF12
    df["sample"] = "Main"
    if "ff12_code" in df.columns:
        df.loc[df["ff12_code"] == 11, "sample"] = "Finance"
        df.loc[df["ff12_code"] == 8, "sample"] = "Utility"

    print("\n  Sample distribution:")
    for sample in ["Main", "Finance", "Utility"]:
        n = (df["sample"] == sample).sum()
        print(f"    {sample}: {n:,} calls")

    return df


# ==============================================================================
# Summary Statistics Functions
# ==============================================================================


def compute_descriptive_statistics(df, output_path, stats=None):
    """Compute and save descriptive statistics for all numeric columns."""
    print("\n" + "=" * 60)
    print("SUMM-01: Computing Descriptive Statistics")
    print("=" * 60)

    # Get numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Compute statistics for each variable
    stats_rows = []
    for col in numeric_cols:
        data = df[col].dropna()
        stats_rows.append(
            {
                "Variable": col,
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

    # Create DataFrame
    desc_df = pd.DataFrame(stats_rows)

    # Save to CSV
    try:
        desc_df.to_csv(output_path, index=False)
    except PermissionError as e:
        print(
            f"ERROR: Permission denied writing descriptive_statistics.csv: {e}",
            file=_sys.stderr,
        )
        print(f"  Output path: {output_path}", file=_sys.stderr)
        _sys.exit(1)
    except OSError as e:
        print(
            f"ERROR: OS error writing descriptive_statistics.csv: {e}", file=_sys.stderr
        )
        print(f"  Output path: {output_path}", file=_sys.stderr)
        _sys.exit(1)
    except Exception as e:
        print(
            f"ERROR: Failed to save descriptive_statistics.csv: {e}", file=_sys.stderr
        )
        print(f"  Output path: {output_path}", file=_sys.stderr)
        _sys.exit(1)

    print(f"  Saved: descriptive_statistics.csv ({len(numeric_cols)} variables)")

    # Print sample
    print("\n  Sample of descriptive statistics:")
    print(desc_df.head(10).to_string(index=False))

    if stats:
        stats["output"]["descriptive_stats"] = {
            "variables": len(numeric_cols),
            "observations": len(df),
        }

    return desc_df


def compute_correlation_matrix(df, output_path, stats=None):
    """Compute and save correlation matrix for key regression variables."""
    print("\n" + "=" * 60)
    print("SUMM-02: Computing Correlation Matrix")
    print("=" * 60)

    # Define key regression variables
    key_vars = [
        "Manager_QA_Uncertainty_pct",
        "Manager_Pres_Uncertainty_pct",
        "Analyst_QA_Uncertainty_pct",
        "Entire_All_Negative_pct",
        "StockRet",
        "MarketRet",
        "EPS_Growth",
        "SurpDec",
    ]

    # Filter to existing variables
    existing_vars = [v for v in key_vars if v in df.columns]

    if len(existing_vars) < 2:
        print("  WARNING: Not enough variables for correlation matrix")
        return None

    # Compute correlation matrix
    corr_matrix = df[existing_vars].corr(method="pearson")

    # Save to CSV
    try:
        corr_matrix.to_csv(output_path)
    except PermissionError as e:
        print(
            f"ERROR: Permission denied writing correlation_matrix.csv: {e}",
            file=_sys.stderr,
        )
        print(f"  Output path: {output_path}", file=_sys.stderr)
        _sys.exit(1)
    except OSError as e:
        print(f"ERROR: OS error writing correlation_matrix.csv: {e}", file=_sys.stderr)
        print(f"  Output path: {output_path}", file=_sys.stderr)
        _sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to save correlation_matrix.csv: {e}", file=_sys.stderr)
        print(f"  Output path: {output_path}", file=_sys.stderr)
        _sys.exit(1)

    print(
        f"  Saved: correlation_matrix.csv ({len(existing_vars)}x{len(existing_vars)})"
    )

    # Print matrix
    print("\n  Correlation Matrix:")
    print(corr_matrix.to_string(float_format="  %7.4f"))

    if stats:
        stats["output"]["correlation_matrix"] = {"variables": len(existing_vars)}

    return corr_matrix


def compute_panel_balance(df, output_path, stats=None):
    """Compute and save panel balance diagnostics."""
    print("\n" + "=" * 60)
    print("SUMM-03: Computing Panel Balance Diagnostics")
    print("=" * 60)

    # Firm-year coverage
    if "gvkey" in df.columns and "year" in df.columns:
        firm_year = df.groupby(["gvkey", "year"]).size()
        calls_per_firm_year = firm_year.values

        firm_year_summary = {
            "N (firm-year cells)": int(len(firm_year)),
            "Mean calls per firm-year": round(calls_per_firm_year.mean(), 2),
            "Median": round(np.median(calls_per_firm_year), 2),
            "SD": round(calls_per_firm_year.std(), 2),
            "Min": int(calls_per_firm_year.min()),
            "Max": int(calls_per_firm_year.max()),
        }

        print("\n  Firm-Year Coverage Summary:")
        for k, v in firm_year_summary.items():
            if isinstance(v, int):
                print(f"    {k}: {v:,}")
            else:
                print(f"    {k}: {v}")

        # Year-level coverage
        year_stats = pd.DataFrame()
        if "ceo_id" in df.columns:
            year_stats = df.groupby("year").agg(
                {"gvkey": "nunique", "ceo_id": "nunique"}
            )
            year_stats["N Calls"] = df.groupby("year").size()

            print("\n  Year-Level Coverage:")
            print("    Year    Firms     CEOs    Calls")
            print("  ------ -------- -------- --------")
            for year, row in year_stats.iterrows():
                print(
                    f"    {int(year):>6} {row['gvkey']:>8} {row['ceo_id']:>8} {row['N Calls']:>8,}"
                )
    else:
        firm_year_summary = {}
        year_stats = pd.DataFrame()
        print("  WARNING: Missing gvkey or year column for panel balance")

    # Save to CSV
    # Create multi-section CSV with proper formatting
    try:
        f = open(output_path, "w", newline="")
    except FileNotFoundError as e:
        print(f"ERROR: Output directory not found: {e}", file=_sys.stderr)
        print(f"  Output path: {output_path}", file=_sys.stderr)
        _sys.exit(1)
    except PermissionError as e:
        print(
            f"ERROR: Permission denied creating panel_balance.csv: {e}",
            file=_sys.stderr,
        )
        print(f"  Output path: {output_path}", file=_sys.stderr)
        _sys.exit(1)
    except OSError as e:
        print(f"ERROR: OS error creating panel_balance.csv: {e}", file=_sys.stderr)
        print(f"  Output path: {output_path}", file=_sys.stderr)
        _sys.exit(1)

    with f:
        writer = csv.writer(f)
        writer.writerow(["Panel Balance Summary", "", "", "", ""])

        # Firm-year section
        writer.writerow(["Metric", "Value", "", "", ""])
        for k, v in firm_year_summary.items():
            if isinstance(v, int):
                writer.writerow([k, f"{v:,}", "", "", ""])
            else:
                writer.writerow([k, f"{v}", "", "", ""])

        writer.writerow(["", "", "", "", ""])
        writer.writerow(["Year-Level Coverage", "", "", "", ""])
        writer.writerow(["Year", "N Firms", "N CEOs", "N Calls", ""])

        if not year_stats.empty:
            for year, row in year_stats.iterrows():
                calls_str = format(int(row["N Calls"]), ",")
                writer.writerow([int(year), row["gvkey"], row["ceo_id"], calls_str, ""])

    print("\n  Saved: panel_balance.csv")

    if stats:
        stats["output"]["panel_balance"] = {
            "firm_year_cells": firm_year_summary.get("N (firm-year cells)", 0),
            "years": len(year_stats),
        }

    return firm_year_summary, year_stats


def generate_summary_report(
    desc_stats, corr_matrix, firm_year_summary, year_stats, output_path
):
    """Generate markdown summary report."""
    print("\n  Generating summary report...")

    report_lines = [
        "# Summary Statistics Report for Analysis Dataset",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Overview",
        "",
        "This report provides comprehensive summary statistics for the final analysis",
        "dataset used in CEO clarity estimation and liquidity regressions.",
        "",
        "## SUMM-01: Descriptive Statistics",
        "",
        "Descriptive statistics for all numeric variables in the analysis dataset.",
        "",
        "| Variable | N | Mean | SD | Min | P25 | Median | P75 | Max |",
        "|----------|---|------|----|-----|----|--------|----|----|",
    ]

    # Add descriptive statistics table
    for _, row in desc_stats.iterrows():
        report_lines.append(
            f"| {row['Variable']:<35} | {row['N']:>6} | {row['Mean']:>8.4f} | {row['SD']:>8.4f} | "
            f"{row['Min']:>8.4f} | {row['P25']:>8.4f} | {row['Median']:>8.4f} | {row['P75']:>8.4f} | {row['Max']:>8.4f} |"
        )

    # Correlation matrix section
    report_lines.extend(["", "## SUMM-02: Correlation Matrix", ""])
    report_lines.append(
        "Pearson correlation coefficients for key regression variables."
    )
    report_lines.append("")

    if corr_matrix is not None:
        # Build header
        header = "|                                     |"
        for col in corr_matrix.columns:
            header += f" {col:<35} |"
        report_lines.append(header)

        # Separator
        sep = "|"
        for _ in corr_matrix.columns:
            sep += "---|"
        report_lines.append(sep)

        # Data rows
        for idx, row in corr_matrix.iterrows():
            row_str = f"| {idx:<35} |"
            for val in row.values:
                row_str += f" {val:>7.4f} |"
            report_lines.append(row_str)

    # Panel balance section
    report_lines.extend(["", "## SUMM-03: Panel Balance Diagnostics", ""])
    report_lines.append("### Firm-Year Coverage")
    report_lines.append("")

    for k, v in firm_year_summary.items():
        if isinstance(v, int):
            report_lines.append(f"- **{k}**: {v:,}")
        else:
            report_lines.append(f"- **{k}**: {v}")

    report_lines.extend(["", "### Year-Level Coverage", ""])
    report_lines.append("| Year | N Firms | N CEOs | N Calls |")
    report_lines.append("|------|---------|--------|---------|")

    if not year_stats.empty:
        for year, row in year_stats.iterrows():
            report_lines.append(
                f"| {int(year)} | {row['gvkey']:,} | {row['ceo_id']:,} | {row['N Calls']:,} |"
            )

    # Notes section
    report_lines.extend(
        [
            "",
            "## SUMM-04: Notes for Paper Table 1",
            "",
            "- All variables are winsorized at 1% and 99% (see Step 3)",
            "- Correlations use complete cases only",
            "- Panel coverage includes all firms with complete data",
            "",
        ]
    )

    # Write report
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("  Saved: summary_report.md")


# ==============================================================================
# Main
# ==============================================================================


def main():
    """Main execution."""
    start_time = datetime.now()
    start_iso = start_time.isoformat()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    # Load config
    year_start = 2002
    year_end = 2004

    # Setup paths
    root = Path(__file__).resolve().parents[2]
    out_dir = root / "4_Outputs" / "4.1_CeoClarity" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = root / "3_Logs" / "4.4_GenerateSummaryStats" / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)

    # Setup dual logging
    log_path = log_dir / f"step4_4_{timestamp}.log"
    dual_writer = DualWriter(log_path)
    _sys.stdout = dual_writer

    # Initialize stats
    stats: Dict[str, Any] = {
        "step_id": "4.4_GenerateSummaryStats",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {},
        "output": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
    }

    # Set random seed for deterministic execution
    np.random.seed(42)

    print("=" * 80)
    print("STEP 4.4: Generate Summary Statistics for Analysis Dataset")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")
    print(f"Years: {year_start}-{year_end}")

    # ==============================================================================
    # Load and Merge Data
    # ==============================================================================

    print("\n" + "=" * 60)
    print("Loading and merging data")
    print("=" * 60)

    # Resolve manifest path using get_latest_output_dir
    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.4_AssembleManifest",
        required_file="master_sample_manifest.parquet",
    )
    manifest = load_manifest(
        manifest_dir / "master_sample_manifest.parquet",
        stats,
    )

    # Resolve linguistic variables path
    linguistic_dir = get_latest_output_dir(
        root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
    )
    linguistic = load_linguistic_variables(
        linguistic_dir,
        year_start,
        year_end,
        stats,
    )

    # Resolve financial controls path
    financial_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_Features",
    )
    firm_controls = load_financial_controls(
        financial_dir,
        year_start,
        year_end,
        stats,
    )

    market_vars = load_market_variables(
        financial_dir,
        year_start,
        year_end,
        stats,
    )

    # Merge data
    df = prepare_analysis_data(manifest, linguistic, firm_controls, market_vars, stats)

    # ==============================================================================
    # Generate Summary Statistics
    # ==============================================================================

    # Panel balance (compute BEFORE filtering for complete dataset)
    firm_year_summary, year_stats = compute_panel_balance(
        df, out_dir / "panel_balance.csv", stats
    )

    # Filter to complete cases
    df_analysis = filter_complete_cases(df, stats)

    # Descriptive statistics
    desc_stats = compute_descriptive_statistics(
        df_analysis, out_dir / "descriptive_statistics.csv", stats
    )

    # Correlation matrix
    corr_matrix = compute_correlation_matrix(
        df_analysis, out_dir / "correlation_matrix.csv", stats
    )

    # Summary report
    generate_summary_report(
        desc_stats,
        corr_matrix,
        firm_year_summary,
        year_stats,
        out_dir / "summary_report.md",
    )

    # ==============================================================================
    # Finalize
    # ==============================================================================

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    stats["timing"]["end_iso"] = end_time.isoformat()
    stats["timing"]["duration_seconds"] = duration

    # Save stats.json
    stats_path = out_dir / "stats.json"
    try:
        with open(stats_path, "w") as f:
            json.dump(stats, f, indent=2)
    except FileNotFoundError as e:
        print(f"ERROR: Output directory not found: {e}", file=_sys.stderr)
        print(f"  Output path: {stats_path}", file=_sys.stderr)
        _sys.exit(1)
    except PermissionError as e:
        print(f"ERROR: Permission denied writing stats.json: {e}", file=_sys.stderr)
        print(f"  Output path: {stats_path}", file=_sys.stderr)
        _sys.exit(1)
    except OSError as e:
        print(f"ERROR: OS error writing stats.json: {e}", file=_sys.stderr)
        print(f"  Output path: {stats_path}", file=_sys.stderr)
        _sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to save stats.json: {e}", file=_sys.stderr)
        print(f"  Output path: {stats_path}", file=_sys.stderr)
        _sys.exit(1)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")
    print("\nGenerated files:")
    print("  - descriptive_statistics.csv")
    print("  - correlation_matrix.csv")
    print("  - panel_balance.csv")
    print("  - summary_report.md")

    # Restore stdout
    _sys.stdout = dual_writer.original_stdout
    dual_writer.close()

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        # validate_prerequisites already prints "[OK] All prerequisites validated"
        _sys.exit(0)

    check_prerequisites(root)
    _sys.exit(main())
