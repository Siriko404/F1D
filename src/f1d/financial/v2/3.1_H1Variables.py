#!/usr/bin/env python3
"""
==============================================================================
STEP 3.1: H1 Cash Holdings Variables
==============================================================================
ID: 3.1_H1Variables
Description: Constructs H1 dependent variable (Cash Holdings), moderator
             (Leverage), and controls for cash holdings hypothesis testing.

Variables Computed:
    - Cash Holdings: CHE / AT (Dependent Variable)
    - Leverage: (DLTT + DLC) / AT (Moderator)
    - OCF Volatility: StdDev(OANCF/AT) over trailing 5 years (Control)
    - Current Ratio: ACT / LCT (Control)
    - Tobin's Q: (AT + Market Equity - CEQ) / AT (Control)
    - ROA: IB / AT (Control)
    - Capex/AT: CAPX / AT (Control)
    - Dividend Payer: Indicator(DVC > 0) (Control)
    - Firm Size: ln(AT) (Control)

Inputs:
    - 4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - 4_Outputs/3_Financial_Features/latest/firm_controls_*.parquet
    - 1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet (Compustat raw data)

Outputs:
    - 4_Outputs/3_Financial_V2/{timestamp}/H1_CashHoldings.parquet
    - 4_Outputs/3_Financial_V2/{timestamp}/stats.json

Deterministic: true
Dependencies:
    - Requires: Step 2.2
    - Uses: shared.financial_utils, pandas, numpy

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import numpy as np
import pandas as pd
import yaml

# Configure logger for this module
logger = logging.getLogger(__name__)

# Import shared path validation utilities
# Import DualWriter from f1d.shared.observability_utils
from f1d.shared.observability_utils import (
    DualWriter,
    calculate_throughput,
    compute_file_checksum,
    detect_anomalies_zscore,
    get_process_memory_mb,
    print_stat,
    print_stats_summary,
    save_stats,
)
from f1d.shared.path_utils import (
    ensure_output_dir,
    get_latest_output_dir,
    validate_input_file,
)

# ==============================================================================
# Configuration
# ==============================================================================


def load_config() -> Dict[str, Any]:
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    if config_path.exists():
        validate_input_file(config_path, must_exist=True)
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


def setup_paths(config: Dict[str, Any], timestamp: str) -> Dict[str, Path]:
    """Set up all required paths"""
    # Go up from src/f1d/financial/v2/ to project root (5 levels)
    root = Path(__file__).parent.parent.parent.parent.parent

    # Resolve manifest directory using timestamp-based resolution
    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.4_AssembleManifest",
        required_file="master_sample_manifest.parquet",
    )

    # Resolve firm controls directory
    firm_controls_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_Features",
        required_file="firm_controls_2002.parquet",  # At least one year must exist
    )

    paths = {
        "root": root,
        "manifest_dir": manifest_dir,
        "firm_controls_dir": firm_controls_dir,
        "compustat_file": root
        / "1_Inputs"
        / "comp_na_daily_all"
        / "comp_na_daily_all.parquet",
    }

    # Output directory
    output_base = root / "4_Outputs" / "3_Financial_V2"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "3_Financial_V2"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H1.log"

    return paths


# ==============================================================================
# Data Loading
# ==============================================================================


def load_manifest(manifest_dir: Path) -> pd.DataFrame:
    """Load manifest data - the universe of firm-years in sample"""
    manifest_file = manifest_dir / "master_sample_manifest.parquet"
    if not manifest_file.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_file}")

    validate_input_file(manifest_file, must_exist=True)
    df = pd.read_parquet(manifest_file)
    print(f"  Loaded manifest: {len(df):,} calls")

    # Ensure gvkey is string and zero-padded
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["year"] = df["start_date"].dt.year

    return df


def load_firm_controls(firm_controls_dir: Path) -> pd.DataFrame:
    """Load and combine all yearly firm controls files"""
    print(f"  Loading firm controls from: {firm_controls_dir}")

    # Find all firm_controls_*.parquet files
    control_files = sorted(firm_controls_dir.glob("firm_controls_*.parquet"))

    if not control_files:
        raise FileNotFoundError(f"No firm_controls files found in {firm_controls_dir}")

    dfs = []
    for f in control_files:
        df = pd.read_parquet(f)
        dfs.append(df)
        print(f"    Loaded {f.name}: {len(df):,} rows")

    combined = pd.concat(dfs, ignore_index=True)
    print(f"  Combined firm controls: {len(combined):,} rows")

    # Ensure gvkey is string and zero-padded
    combined["gvkey"] = combined["gvkey"].astype(str).str.zfill(6)

    return combined


def load_compustat(compustat_file: Path) -> pd.DataFrame:
    """Load Compustat data with only required columns for H1 variables"""
    print("  Loading Compustat data...")

    # Required columns for H1 variables
    # Quarterly fields (q suffix): at, che, dltt, dlc, act, lct, ceq
    # Annual fields (y suffix): oancf, ib, capx, dv
    # Price and shares: csho, prcc
    # Date fields: datadate, fyearq (fiscal year quarterly)
    required_cols = [
        "gvkey",
        "datadate",
        "fyearq",
        # Assets and cash (quarterly)
        "atq",
        "cheq",
        # Debt (quarterly)
        "dlttq",
        "dlcq",
        # Current assets/liabilities (quarterly)
        "actq",
        "lctq",
        # Equity (quarterly)
        "ceqq",
        "cshoq",  # Common Shares Outstanding Quarterly
        "prccq",  # Price Close Quarterly
        # Annual fields for some variables
        "oancfy",  # Operating Cash Flow Annual
        "iby",  # Income Before Extra Items Annual
        "capxy",  # Capital Expenditures Annual
        "dvy",  # Dividends Annual (not dvcy)
    ]

    # Check which columns actually exist
    import pyarrow.parquet as pq

    pf = pq.ParquetFile(compustat_file)
    available_cols = set(pf.schema_arrow.names)

    # Filter to only columns that exist
    cols_to_read = [c for c in required_cols if c in available_cols]

    if len(cols_to_read) < len(required_cols):
        missing = set(required_cols) - set(cols_to_read)
        print(f"  Warning: Missing columns will be unavailable: {missing}")

    df = pd.read_parquet(compustat_file, columns=cols_to_read)

    print(f"  Loaded Compustat: {len(df):,} observations")

    # Normalize
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["datadate"] = pd.to_datetime(df["datadate"])

    # Convert Decimal types to float64 for numpy compatibility
    for col in df.columns:
        if col not in ["gvkey", "datadate"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

    # Add fiscal year field from fyearq
    if "fyearq" in df.columns:
        df["fiscal_year"] = df["fyearq"].astype("Int64")
    else:
        # Extract fiscal year from datadate
        df["fiscal_year"] = df["datadate"].dt.year

    return df


# ==============================================================================
# Variable Computation Functions
# ==============================================================================


def compute_cash_holdings(compustat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Cash Holdings = CHE / AT

    Args:
        compustat_df: Compustat data with atq, cheq columns

    Returns:
        DataFrame with gvkey, fiscal_year, cash_holdings
    """
    print("\nComputing Cash Holdings (CHE/AT)...")

    # Require positive AT
    df = compustat_df[(compustat_df["atq"] > 0)].copy()

    # Compute cash holdings
    df["cash_holdings"] = df["cheq"] / df["atq"]

    result = df[["gvkey", "fiscal_year", "datadate", "cash_holdings"]].copy()

    n_computed = result["cash_holdings"].notna().sum()
    print(f"  Computed cash_holdings for {n_computed:,} observations")

    return result


def compute_leverage(compustat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Leverage = (DLTT + DLC) / AT

    Handles missing DLTT or DLC as 0 (debt can be zero).

    Args:
        compustat_df: Compustat data with atq, dlttq, dlcq columns

    Returns:
        DataFrame with gvkey, fiscal_year, leverage
    """
    print("\nComputing Leverage ((DLTT+DLC)/AT)...")

    # Require positive AT
    df = compustat_df[(compustat_df["atq"] > 0)].copy()

    # Fill missing debt with 0
    df["dlttq"] = df["dlttq"].fillna(0)
    df["dlcq"] = df["dlcq"].fillna(0)

    # Compute leverage
    df["leverage"] = (df["dlttq"] + df["dlcq"]) / df["atq"]

    result = df[["gvkey", "fiscal_year", "datadate", "leverage"]].copy()

    n_computed = result["leverage"].notna().sum()
    print(f"  Computed leverage for {n_computed:,} observations")

    return result


def compute_ocf_volatility(
    compustat_df: pd.DataFrame, min_years: int = 3, window: int = 5
) -> pd.DataFrame:
    """
    Compute Operating Cash Flow Volatility = StdDev(OANCF/AT) over trailing 5 years

    Requires minimum 3 years of data in the 5-year window.
    Computed per firm using fiscal year ordering.

    Args:
        compustat_df: Compustat data with oancfy, atq, fiscal_year columns
        min_years: Minimum observations required (default: 3)
        window: Rolling window in years (default: 5)

    Returns:
        DataFrame with gvkey, fiscal_year, ocf_volatility
    """
    print("\nComputing OCF Volatility (5-year rolling StdDev of OANCF/AT)...")

    # Require positive AT and valid OCF
    df = compustat_df.loc[
        (compustat_df["atq"] > 0) & (compustat_df["oancfy"].notna()),
        :,
    ].copy()

    # Compute OCF/AT ratio
    df["ocf_at"] = df["oancfy"] / df["atq"]

    # Sort by gvkey and fiscal_year for rolling calculation
    df = cast(pd.DataFrame, df).sort_values(["gvkey", "fiscal_year"])

    # Vectorized two-pointer approach: for each (gvkey, fiscal_year),
    # find rows with fiscal_year in (fy - window, fy] and compute std
    results = []
    for gvkey, group in df.groupby("gvkey", sort=False):
        group = group.sort_values("fiscal_year").reset_index(drop=True)
        years = group["fiscal_year"].values
        ocf_vals = group["ocf_at"].values
        n = len(years)
        left = 0

        for right in range(n):
            fy = years[right]
            # Move left pointer to first year > fy - window - 1
            lower_bound = fy - window - 1
            while left < n and years[left] <= lower_bound:
                left += 1
            # Window is [left, right] inclusive
            window_data = ocf_vals[left : right + 1]
            valid_mask = ~np.isnan(window_data)
            if valid_mask.sum() >= min_years:
                ocf_vol = np.nanstd(window_data)
                results.append(
                    {"gvkey": gvkey, "fiscal_year": fy, "ocf_volatility": ocf_vol}
                )

    result = pd.DataFrame(results)

    if not result.empty:
        n_computed = result["ocf_volatility"].notna().sum()
        print(f"  Computed ocf_volatility for {n_computed:,} observations")
    else:
        print("  Warning: No OCF volatility computed (insufficient data)")

    return result


def compute_current_ratio(compustat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Current Ratio = ACT / LCT

    Args:
        compustat_df: Compustat data with actq, lctq columns

    Returns:
        DataFrame with gvkey, fiscal_year, current_ratio
    """
    print("\nComputing Current Ratio (ACT/LCT)...")

    # Require positive LCT
    df = compustat_df[(compustat_df["lctq"] > 0)].copy()

    # Compute current ratio
    df["current_ratio"] = df["actq"] / df["lctq"]

    result = df[["gvkey", "fiscal_year", "datadate", "current_ratio"]].copy()

    n_computed = result["current_ratio"].notna().sum()
    print(f"  Computed current_ratio for {n_computed:,} observations")

    return result


def compute_tobins_q(compustat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Tobin's Q = (AT + Market Equity - CEQ) / AT

    Market Equity = cshoq * prccq (shares outstanding * price)

    Args:
        compustat_df: Compustat data with atq, ceqq, cshoq, prccq columns

    Returns:
        DataFrame with gvkey, fiscal_year, tobins_q
    """
    print("\nComputing Tobin's Q...")

    # Check if required columns exist
    if "cshoq" not in compustat_df.columns or "prccq" not in compustat_df.columns:
        print("  Warning: cshoq or prccq not available, returning empty")
        return pd.DataFrame(columns=["gvkey", "fiscal_year", "datadate", "tobins_q"])

    # Require positive AT
    df = compustat_df[(compustat_df["atq"] > 0)].copy()

    # Compute market equity (handle missing as NaN)
    df["market_equity"] = df["cshoq"] * df["prccq"]

    # Compute Tobin's Q
    # (AT + ME - CEQ) / AT
    df["tobins_q"] = (df["atq"] + df["market_equity"] - df["ceqq"]) / df["atq"]

    result = df[["gvkey", "fiscal_year", "datadate", "tobins_q"]].copy()

    n_computed = result["tobins_q"].notna().sum()
    print(f"  Computed tobins_q for {n_computed:,} observations")

    return result


def compute_roa(compustat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute ROA = IB / AT

    Uses annual IB (net income) from Compustat.

    Args:
        compustat_df: Compustat data with atq, iby columns

    Returns:
        DataFrame with gvkey, fiscal_year, roa
    """
    print("\nComputing ROA (IB/AT)...")

    # Require positive AT
    df = compustat_df[(compustat_df["atq"] > 0)].copy()

    # Compute ROA
    df["roa"] = df["iby"] / df["atq"]

    result = df[["gvkey", "fiscal_year", "datadate", "roa"]].copy()

    n_computed = result["roa"].notna().sum()
    print(f"  Computed roa for {n_computed:,} observations")

    return result


def compute_capex_at(compustat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Capex/AT = CAPX / AT

    Args:
        compustat_df: Compustat data with atq, capxy columns

    Returns:
        DataFrame with gvkey, fiscal_year, capex_at
    """
    print("\nComputing Capex/AT...")

    # Require positive AT
    df = compustat_df[(compustat_df["atq"] > 0)].copy()

    # Compute capex/AT (treat missing CAPX as 0)
    df["capex_at"] = df["capxy"].fillna(0) / df["atq"]

    result = df[["gvkey", "fiscal_year", "datadate", "capex_at"]].copy()

    n_computed = result["capex_at"].notna().sum()
    print(f"  Computed capex_at for {n_computed:,} observations")

    return result


def compute_dividend_payer(compustat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Dividend Payer = Indicator(DV > 0)

    Args:
        compustat_df: Compustat data with dvy column (Dividends Annual)

    Returns:
        DataFrame with gvkey, fiscal_year, dividend_payer
    """
    print("\nComputing Dividend Payer indicator...")

    # Check if dvy column exists
    if "dvy" not in compustat_df.columns:
        print("  Warning: dvy not available, returning empty")
        return pd.DataFrame(
            columns=["gvkey", "fiscal_year", "datadate", "dividend_payer"]
        )

    df = compustat_df.copy()

    # Compute dividend payer indicator
    df["dividend_payer"] = (df["dvy"].fillna(0) > 0).astype(int)

    result = df[["gvkey", "fiscal_year", "datadate", "dividend_payer"]].copy()

    n_payers = result["dividend_payer"].sum()
    print(f"  Computed dividend_payer: {n_payers:,} dividend payers")

    return result


def compute_firm_size(compustat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Firm Size = ln(AT)

    Args:
        compustat_df: Compustat data with atq column

    Returns:
        DataFrame with gvkey, fiscal_year, firm_size
    """
    print("\nComputing Firm Size (ln(AT))...")

    # Require positive AT
    df = compustat_df[(compustat_df["atq"] > 0)].copy()

    # Compute firm size
    df["firm_size"] = np.log(df["atq"])

    result = df[["gvkey", "fiscal_year", "datadate", "firm_size"]].copy()

    n_computed = result["firm_size"].notna().sum()
    print(f"  Computed firm_size for {n_computed:,} observations")

    return result


def winsorize_series(
    s: pd.Series, lower: float = 0.01, upper: float = 0.99
) -> pd.Series:
    """
    Winsorize a series at specified percentiles.

    Args:
        s: Series to winsorize
        lower: Lower percentile (default: 0.01)
        upper: Upper percentile (default: 0.99)

    Returns:
        Winsorized series
    """
    if s.notna().sum() == 0:
        return s

    lower_bound = s.quantile(lower)
    upper_bound = s.quantile(upper)
    return s.clip(lower=lower_bound, upper=upper_bound)


# ==============================================================================
# CLI and Prerequisites
# ==============================================================================


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for 3.1_H1Variables.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 3.1: H1 Cash Holdings Variables

Constructs dependent variable (Cash Holdings), moderator (Leverage),
and control variables for H1 cash holdings hypothesis testing.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config/project.yaml",
        help="Path to project.yaml config file",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Override output directory",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    return parser.parse_args()


def check_prerequisites(paths: Dict[str, Path], args: argparse.Namespace) -> bool:
    """Validate all required inputs and prerequisite steps exist."""
    print("\nChecking prerequisites...")

    required_files = {
        "Manifest": paths["manifest_dir"] / "master_sample_manifest.parquet",
        "Compustat": paths["compustat_file"],
    }

    required_dirs = {
        "Firm Controls": paths["firm_controls_dir"],
    }

    all_ok = True
    for name, path in required_files.items():
        if path.exists():
            print(f"  [OK] {name}: {path}")
        else:
            print(f"  [MISSING] {name}: {path}")
            all_ok = False

    for name, path in required_dirs.items():
        if path.exists():
            # Check for at least one firm_controls file
            controls = list(path.glob("firm_controls_*.parquet"))
            if controls:
                print(f"  [OK] {name}: {path} ({len(controls)} files)")
            else:
                print(f"  [EMPTY] {name}: {path} (no firm_controls files)")
                all_ok = False
        else:
            print(f"  [MISSING] {name}: {path}")
            all_ok = False

    return all_ok


# ==============================================================================
# Main
# ==============================================================================


def main() -> int:
    """Main execution"""
    args = parse_arguments()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    config = load_config()
    paths = setup_paths(config, timestamp)

    # Handle output-dir override
    if args.output_dir:
        paths["output_dir"] = Path(args.output_dir)
        ensure_output_dir(paths["output_dir"])

    # Handle dry-run mode
    if args.dry_run:
        print("=" * 60)
        print("STEP 3.1: H1 Cash Holdings Variables - DRY RUN")
        print(f"Timestamp: {timestamp}")
        print("=" * 60)

        prereq_ok = check_prerequisites(paths, args)
        if prereq_ok:
            print("\n[OK] All prerequisites validated")
            print("\nWould compute:")
            print("  - Cash Holdings (CHE/AT)")
            print("  - Leverage ((DLTT+DLC)/AT)")
            print("  - OCF Volatility (5-year StdDev)")
            print("  - Current Ratio (ACT/LCT)")
            print("  - Tobin's Q, ROA, Capex/AT")
            print("  - Dividend Payer, Firm Size")
            print(f"\nOutput would be written to: {paths['output_dir']}")
            sys.exit(0)
        else:
            print("\n[ERROR] Prerequisites not met")
            sys.exit(1)

    # Check prerequisites before processing
    prereq_ok = check_prerequisites(paths, args)
    if not prereq_ok:
        print("\n[ERROR] Prerequisites not met. Exiting.")
        sys.exit(1)

    # Setup logging
    dual_writer = DualWriter(paths["log_file"])
    sys.stdout = dual_writer

    print("=" * 60)
    print("STEP 3.1: H1 Cash Holdings Variables")
    print(f"Timestamp: {timestamp}")
    print("=" * 60)

    # Initialize statistics
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    mem_start = get_process_memory_mb()
    memory_readings = [mem_start["rss_mb"]]

    stats: Dict[str, Any] = {
        "step_id": "3.1_H1Variables",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0},
        "processing": {
            "variables_computed": [],
            "winsorization": {},
            "missing_dropped": 0,
        },
        "output": {"final_rows": 0, "files": [], "checksums": {}},
        "variables": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
        "memory": {
            "start_mb": mem_start["rss_mb"],
            "end_mb": 0.0,
            "peak_mb": 0.0,
            "delta_mb": 0.0,
        },
    }

    # ========================================================================
    # Load Data
    # ========================================================================

    print("\nLoading data...")

    # Load manifest
    print("\nManifest:")
    manifest_file = paths["manifest_dir"] / "master_sample_manifest.parquet"
    stats["input"]["files"].append(str(manifest_file))
    stats["input"]["checksums"][manifest_file.name] = compute_file_checksum(
        manifest_file
    )
    manifest = load_manifest(paths["manifest_dir"])
    print_stat("Manifest rows", value=len(manifest))
    stats["input"]["total_rows"] += len(manifest)

    # Load firm controls
    print("\nFirm Controls:")
    firm_controls = load_firm_controls(paths["firm_controls_dir"])
    print_stat("Firm controls rows", value=len(firm_controls))

    # Load Compustat
    print("\nCompustat:")
    stats["input"]["files"].append(str(paths["compustat_file"]))
    stats["input"]["checksums"][paths["compustat_file"].name] = compute_file_checksum(
        paths["compustat_file"]
    )
    compustat = load_compustat(paths["compustat_file"])
    print_stat("Compustat rows", value=len(compustat))

    # ========================================================================
    # Compute H1 Variables
    # ========================================================================

    print("\n" + "=" * 60)
    print("Computing H1 Variables")
    print("=" * 60)

    # Compute all H1 variables
    cash_holdings_df = compute_cash_holdings(compustat)
    leverage_df = compute_leverage(compustat)
    ocf_volatility_df = compute_ocf_volatility(compustat)
    current_ratio_df = compute_current_ratio(compustat)
    tobins_q_df = compute_tobins_q(compustat)
    roa_df = compute_roa(compustat)
    capex_at_df = compute_capex_at(compustat)
    dividend_payer_df = compute_dividend_payer(compustat)
    firm_size_df = compute_firm_size(compustat)

    stats["processing"]["variables_computed"] = [
        "cash_holdings",
        "leverage",
        "ocf_volatility",
        "current_ratio",
        "tobins_q",
        "roa",
        "capex_at",
        "dividend_payer",
        "firm_size",
    ]

    # ========================================================================
    # Merge Variables
    # ========================================================================

    print("\n" + "=" * 60)
    print("Merging Variables")
    print("=" * 60)

    # Start with a base of unique firm-years from Compustat
    # Use the most recent datadate for each gvkey-fiscal_year combination
    compustat_vars = compustat.loc[:, ["gvkey", "fiscal_year", "datadate"]].copy()

    # For each gvkey-fiscal_year, keep the most recent datadate
    compustat_vars = (
        cast(pd.DataFrame, compustat_vars)
        .sort_values(
            ["gvkey", "fiscal_year", "datadate"], ascending=[True, True, False]
        )
        .drop_duplicates(subset=["gvkey", "fiscal_year"], keep="first")
    )

    print(f"  Base firm-years: {len(compustat_vars):,}")

    # Merge each computed variable
    for var_name, var_df in [
        ("cash_holdings", cash_holdings_df),
        ("leverage", leverage_df),
        ("current_ratio", current_ratio_df),
        ("tobins_q", tobins_q_df),
        ("roa", roa_df),
        ("capex_at", capex_at_df),
        ("dividend_payer", dividend_payer_df),
        ("firm_size", firm_size_df),
    ]:
        # Keep the most recent datadate for each gvkey-fiscal_year
        var_df_sorted = var_df.sort_values(
            ["gvkey", "fiscal_year", "datadate"], ascending=[True, True, False]
        ).drop_duplicates(subset=["gvkey", "fiscal_year"], keep="first")

        compustat_vars = compustat_vars.merge(
            var_df_sorted[["gvkey", "fiscal_year", var_name]],
            on=["gvkey", "fiscal_year"],
            how="left",
        )
        n_valid = compustat_vars[var_name].notna().sum()
        print(f"  {var_name}: {n_valid:,} valid")

    # Merge OCF volatility (already at gvkey-fiscal_year level)
    compustat_vars = compustat_vars.merge(
        ocf_volatility_df[["gvkey", "fiscal_year", "ocf_volatility"]],
        on=["gvkey", "fiscal_year"],
        how="left",
    )
    n_valid = compustat_vars["ocf_volatility"].notna().sum()
    print(f"  ocf_volatility: {n_valid:,} valid")

    # Merge with existing firm controls for additional variables
    print("\nMerging with existing firm controls...")
    h1_data = compustat_vars.merge(
        firm_controls[
            [
                "file_name",
                "gvkey",
                "year",
                "Size",
                "BM",
                "Lev",
                "ROA",
                "CurrentRatio",
                "RD_Intensity",
            ]
        ],
        left_on=["gvkey", "fiscal_year"],
        right_on=["gvkey", "year"],
        how="left",
    )

    print(f"  After merging firm controls: {len(h1_data):,} observations")

    # Filter to sample manifest firm-years
    # Match based on gvkey and year
    manifest_for_merge = manifest[["gvkey", "year"]].drop_duplicates()
    h1_data = h1_data.merge(manifest_for_merge, on=["gvkey", "year"], how="inner")

    print(f"  After filtering to sample: {len(h1_data):,} observations")

    # ========================================================================
    # Apply Winsorization
    # ========================================================================

    print("\n" + "=" * 60)
    print("Applying Winsorization (1%/99%)")
    print("=" * 60)

    continuous_vars = [
        "cash_holdings",
        "leverage",
        "ocf_volatility",
        "current_ratio",
        "tobins_q",
        "roa",
        "capex_at",
        "firm_size",
    ]

    for var in continuous_vars:
        if var in h1_data.columns and h1_data[var].notna().sum() > 0:
            before_mean = h1_data[var].mean()
            h1_data[var] = winsorize_series(h1_data[var], lower=0.01, upper=0.99)
            after_mean = h1_data[var].mean()
            stats["processing"]["winsorization"][var] = {
                "before_mean": round(float(before_mean), 4),
                "after_mean": round(float(after_mean), 4),
            }
            print(f"  {var}: winsorized")

    # ========================================================================
    # Compute Variable Statistics
    # ========================================================================

    print("\n" + "=" * 60)
    print("Computing Variable Statistics")
    print("=" * 60)

    output_columns = [
        "file_name",
        "gvkey",
        "fiscal_year",
        "cash_holdings",
        "leverage",
        "ocf_volatility",
        "current_ratio",
        "tobins_q",
        "roa",
        "capex_at",
        "dividend_payer",
        "firm_size",
    ]

    for var in output_columns[3:]:  # Skip file_name, gvkey, fiscal_year
        if var in h1_data.columns:
            var_data = h1_data[var]
            stats["variables"][var] = {
                "mean": round(float(var_data.mean()), 4)
                if var_data.notna().sum() > 0
                else None,
                "std": round(float(var_data.std()), 4)
                if var_data.notna().sum() > 1
                else None,
                "min": round(float(var_data.min()), 4)
                if var_data.notna().sum() > 0
                else None,
                "max": round(float(var_data.max()), 4)
                if var_data.notna().sum() > 0
                else None,
                "n": int(var_data.notna().sum()),
                "missing_count": int(var_data.isna().sum()),
            }
            print(
                f"  {var}: mean={stats['variables'][var]['mean']}, "
                f"n={stats['variables'][var]['n']}"
            )

    # ========================================================================
    # Prepare Final Output
    # ========================================================================

    print("\n" + "=" * 60)
    print("Preparing Output")
    print("=" * 60)

    # Select and rename columns for output
    final_output = h1_data[output_columns].copy()

    # Sort by gvkey, fiscal_year for determinism
    final_output = final_output.sort_values(["gvkey", "fiscal_year"]).reset_index(
        drop=True
    )

    print(f"  Final output rows: {len(final_output):,}")

    # ========================================================================
    # Write Outputs
    # ========================================================================

    print("\n" + "=" * 60)
    print("Writing Outputs")
    print("=" * 60)

    # Write parquet file
    output_file = paths["output_dir"] / "H1_CashHoldings.parquet"
    final_output.to_parquet(output_file, index=False)
    print(f"  Wrote: {output_file.name}")
    stats["output"]["files"].append(output_file.name)
    stats["output"]["checksums"][output_file.name] = compute_file_checksum(output_file)

    # Write stats.json
    stats["output"]["final_rows"] = len(final_output)
    save_stats(stats, paths["output_dir"])

    # ========================================================================
    # Final Summary
    # ========================================================================

    # Timing
    end_time = time.perf_counter()
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(end_time - start_time, 2)

    # Memory tracking
    mem_end = get_process_memory_mb()
    memory_readings.append(mem_end["rss_mb"])
    stats["memory"]["end_mb"] = mem_end["rss_mb"]
    stats["memory"]["peak_mb"] = round(max(memory_readings), 2)
    stats["memory"]["delta_mb"] = round(mem_end["rss_mb"] - mem_start["rss_mb"], 2)

    # Throughput
    duration_seconds = end_time - start_time
    try:
        throughput = calculate_throughput(len(final_output), duration_seconds)
        stats["throughput"] = {
            "rows_per_second": throughput,
            "total_rows": len(final_output),
            "duration_seconds": round(duration_seconds, 3),
        }
    except ValueError as e:
        # Log but don't fail - throughput is not critical
        logger.warning(f"Could not calculate throughput: {e}")
        stats["throughput"] = {
            "error": str(e),
            "total_rows": len(final_output),
            "duration_seconds": round(duration_seconds, 3),
        }

    # Detect anomalies
    print("\nDetecting anomalies...")
    numeric_cols = [
        "cash_holdings",
        "leverage",
        "ocf_volatility",
        "current_ratio",
        "tobins_q",
        "roa",
        "capex_at",
        "firm_size",
    ]
    anomalies = detect_anomalies_zscore(final_output, numeric_cols, threshold=3.0)
    total_anomalies = sum(a["count"] for a in anomalies.values())
    print(f"  Anomalies detected (z>3): {total_anomalies}")

    # Print summary
    print_stats_summary(stats)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"H1 Variables computed: {len(final_output):,} observations")
    print(f"\nOutputs saved to: {paths['output_dir']}")
    print(f"Log saved to: {paths['log_file']}")

    dual_writer.close()
    sys.stdout = dual_writer.terminal

    return 0


if __name__ == "__main__":
    main()
