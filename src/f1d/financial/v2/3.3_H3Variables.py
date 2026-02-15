#!/usr/bin/env python3
"""
==============================================================================
STEP 3.3: H3 Payout Policy Variables
==============================================================================
ID: 3.3_H3Variables
Description: Constructs H3 dependent variables (Dividend Policy Stability,
             Payout Flexibility) and controls for payout policy hypothesis.

Variables Computed:
    - Dividend Policy Stability: -StdDev(Delta DPS) / Mean(DPS) over trailing 5 years
    - Payout Flexibility: % years with |Delta DPS| > 5% of prior DPS
    - Earnings Volatility: StdDev(annual EPS) over trailing 5 years
    - FCF Growth: Year-over-year growth in (OANCF - CAPX) / AT
    - Firm Maturity: RE / TE ratio (DeAngelo et al. proxy)
    - Standard controls: firm_size, roa, tobins_q, cash_holdings

Inputs:
    - 4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - 1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet
    - 4_Outputs/3_Financial_V2/latest/H1_CashHoldings.parquet (for standard controls)

Outputs:
    - 4_Outputs/3_Financial_V2/{timestamp}/H3_PayoutPolicy.parquet
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
from typing import Any, Dict, List, cast

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


def load_config():
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    if config_path.exists():
        validate_input_file(config_path, must_exist=True)
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


def setup_paths(config, timestamp):
    """Set up all required paths"""
    # Go up from src/f1d/financial/v2/ to project root (5 levels)
    root = Path(__file__).parent.parent.parent.parent.parent

    # Resolve manifest directory using timestamp-based resolution
    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.4_AssembleManifest",
        required_file="master_sample_manifest.parquet",
    )

    # Resolve H1 output directory for standard controls
    h1_output_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H1_CashHoldings.parquet",
    )

    paths = {
        "root": root,
        "manifest_dir": manifest_dir,
        "h1_output_dir": h1_output_dir,
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
    paths["log_file"] = log_base / f"{timestamp}_H3.log"

    return paths


# ==============================================================================
# Data Loading
# ==============================================================================


def load_manifest(manifest_dir):
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


def load_compustat_h3(compustat_file, sample_gvkeys=None):
    """
    Load Compustat data with only required columns for H3 variables.

    Required columns (verified AVAILABLE):
    - gvkey, datadate, fyearq (identifiers)
    - dvpspq (Dividends per Share - Quarterly) for stability/flexibility
    - epspxq (EPS Basic - Excl Extra Items - Quarterly) for earnings volatility
    - req (Retained Earnings - Quarterly) for firm maturity
    - seqq (Stockholders Equity - Quarterly) for firm maturity
    - oancfy (Operating Cash Flow - Annual) for FCF growth
    - capxy (Capital Expenditures - Annual) for FCF growth
    - atq (Total Assets - Quarterly) for ratios

    Args:
        compustat_file: Path to Compustat parquet file
        sample_gvkeys: Optional list of gvkeys to filter to (for memory optimization)

    Returns:
        DataFrame with H3-required columns
    """
    print("  Loading Compustat data...")

    # Required columns for H3 variables
    required_cols = [
        "gvkey",
        "datadate",
        "fyearq",
        # Dividend data (quarterly)
        "dvpspq",  # Dividends per Share - Quarterly
        # Earnings data (quarterly)
        "epspxq",  # EPS Basic - Excl Extra Items - Quarterly
        # Retained earnings and equity (quarterly)
        "req",  # Retained Earnings - Quarterly
        "seqq",  # Stockholders Equity - Quarterly
        # Cash flow data (annual)
        "oancfy",  # Operating Cash Flow - Annual
        "capxy",  # Capital Expenditures - Annual
        # Assets (quarterly)
        "atq",  # Total Assets - Quarterly
    ]

    # Check which columns actually exist using PyArrow schema inspection
    import pyarrow.parquet as pq

    pf = pq.ParquetFile(compustat_file)
    available_cols = set(pf.schema_arrow.names)

    # Filter to only columns that exist
    cols_to_read = [c for c in required_cols if c in available_cols]

    if len(cols_to_read) < len(required_cols):
        missing = set(required_cols) - set(cols_to_read)
        print(f"  Warning: Missing columns: {missing}")

    # Read Compustat data
    df = pd.read_parquet(compustat_file, columns=cols_to_read)

    # Filter to sample gvkeys BEFORE heavy computation (memory optimization)
    if sample_gvkeys is not None:
        sample_gvkeys = set(sample_gvkeys)
        before_rows = len(df)
        df = df.loc[df["gvkey"].astype(str).str.zfill(6).isin(sample_gvkeys), :]
        after_rows = len(df)
        print(f"  Filtered to sample: {after_rows:,} rows (from {before_rows:,})")

    print(f"  Loaded Compustat: {len(df):,} observations")

    # Normalize gvkey to 6-digit zero-padded string
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


def load_h1_standard_controls(h1_output_dir):
    """
    Load standard controls from H1 output (firm_size, roa, tobins_q, cash_holdings).

    H1 output has multiple observations per gvkey-fiscal_year (from different files).
    This function aggregates to one row per gvkey-fiscal_year by taking the mean.

    Args:
        h1_output_dir: Path to H1 output directory

    Returns:
        DataFrame with standard controls (one row per gvkey-fiscal_year)
    """
    h1_file = h1_output_dir / "H1_CashHoldings.parquet"
    if not h1_file.exists():
        print(f"  Warning: H1 output not found at {h1_file}")
        return None

    df = pd.read_parquet(h1_file)

    # Extract standard control columns
    controls = df[
        ["gvkey", "fiscal_year", "firm_size", "roa", "tobins_q", "cash_holdings"]
    ].copy()

    # Ensure gvkey is zero-padded
    controls["gvkey"] = controls["gvkey"].astype(str).str.zfill(6)

    # Aggregate to one row per gvkey-fiscal_year (take mean)
    before_agg = len(controls)
    controls = controls.groupby(["gvkey", "fiscal_year"], as_index=False).mean()
    after_agg = len(controls)
    print(
        f"  Loaded H1 standard controls: {after_agg:,} unique firm-years (aggregated from {before_agg:,} obs)"
    )

    return controls


# ==============================================================================
# Variable Computation Functions
# ==============================================================================


def annualize_quarterly_data(
    compustat_df: pd.DataFrame, value_col: str
) -> pd.DataFrame:
    """
    Aggregate quarterly data to fiscal year level.

    For DPS (dvpspq): SUM quarters to get annual dividend per share
    For EPS (epspxq): SUM quarters to get annual EPS

    Args:
        compustat_df: Compustat data with gvkey, fiscal_year, value_col
        value_col: Column name to aggregate

    Returns:
        DataFrame with gvkey, fiscal_year, annual_value
    """
    # Group by gvkey and fiscal year, sum the quarterly values
    annual = (
        compustat_df.groupby(["gvkey", "fiscal_year"], as_index=False)[value_col]
        .sum()
    )
    annual = cast(pd.DataFrame, annual).rename(columns={value_col: "annual_value"})

    return cast(pd.DataFrame, annual)


def compute_div_stability(
    compustat_df: pd.DataFrame, min_years: int = 2, window: int = 5
) -> pd.DataFrame:
    """
    Compute Dividend Policy Stability = -StdDev(Delta DPS) / Mean(DPS) over trailing 5 years.

    H3-01: Dependent variable measuring dividend stability.
    Formula: -StdDev(Delta DPS) / |Mean(DPS)|

    Higher values = MORE stable (negative CV makes higher = more stable).
    The negative sign flips the coefficient of variation so that higher
    values indicate greater stability.

    Args:
        compustat_df: Compustat data with dvpspq column
        min_years: Minimum observations required in window (default: 2)
        window: Rolling window in years (default: 5)

    Returns:
        DataFrame with gvkey, fiscal_year, div_stability
    """
    print("\nComputing Dividend Policy Stability...")

    # Annualize quarterly DPS (sum quarters)
    annual_dps = annualize_quarterly_data(compustat_df, "dvpspq")
    annual_dps = annual_dps.rename(columns={"annual_value": "dps"})

    # Sort by gvkey and fiscal_year for rolling calculation
    annual_dps = annual_dps.sort_values(["gvkey", "fiscal_year"])

    results = []

    for gvkey, group in annual_dps.groupby("gvkey"):
        group = group.sort_values("fiscal_year")

        # Compute rolling stability for each year
        for _idx, row in group.iterrows():
            fy = row["fiscal_year"]

            # Get trailing window (inclusive of current year)
            window_data = group[
                (group["fiscal_year"] > fy - window - 1) & (group["fiscal_year"] <= fy)
            ]["dps"]

            # Require minimum observations
            if window_data.notna().sum() >= min_years:
                mean_dps = window_data.mean()

                # Guard against division by zero
                if abs(mean_dps) > 0.001:
                    # Compute delta DPS (year-over-year changes)
                    delta_dps = window_data.diff().dropna()

                    if len(delta_dps) >= 1:
                        std_dev_delta = delta_dps.std()
                        # Stability = -StdDev(Delta DPS) / |Mean(DPS)|
                        div_stability = -std_dev_delta / abs(mean_dps)
                        results.append(
                            {
                                "gvkey": gvkey,
                                "fiscal_year": fy,
                                "div_stability": div_stability,
                            }
                        )

    result = pd.DataFrame(results)

    if not result.empty:
        n_computed = result["div_stability"].notna().sum()
        print(f"  Computed div_stability for {n_computed:,} observations")
    else:
        print("  Warning: No dividend stability computed (insufficient data)")

    return result


def compute_payout_flexibility(
    compustat_df: pd.DataFrame,
    min_years: int = 2,
    window: int = 5,
    threshold: float = 0.05,
) -> pd.DataFrame:
    """
    Compute Payout Flexibility = % of years with |Delta DPS| > threshold% of prior DPS over 5-year window.

    H3-02: Dependent variable measuring payout flexibility.
    Higher values indicate MORE frequent changes (less stability).

    Args:
        compustat_df: Compustat data with dvpspq column
        min_years: Minimum observations required in window (default: 2)
        window: Rolling window in years (default: 5)
        threshold: Threshold for significant change (default: 0.05 = 5%)

    Returns:
        DataFrame with gvkey, fiscal_year, payout_flexibility
    """
    print("\nComputing Payout Flexibility...")

    # Annualize quarterly DPS (sum quarters)
    annual_dps = annualize_quarterly_data(compustat_df, "dvpspq")
    annual_dps = annual_dps.rename(columns={"annual_value": "dps"})

    # Sort by gvkey and fiscal_year for rolling calculation
    annual_dps = annual_dps.sort_values(["gvkey", "fiscal_year"])

    results = []

    for gvkey, group in annual_dps.groupby("gvkey"):
        group = group.sort_values("fiscal_year").reset_index(drop=True)

        # Compute year-over-year changes
        group["dps_prior"] = group["dps"].shift(1)
        group["abs_delta_dps"] = (group["dps"] - group["dps_prior"]).abs()

        # Compute relative change (guard against division by zero)
        group["relative_change"] = np.where(
            group["dps_prior"].abs() > 0.001,
            group["abs_delta_dps"] / group["dps_prior"].abs(),
            np.nan,
        )

        # Flag significant changes
        group["is_significant_change"] = group["relative_change"] > threshold

        # Compute rolling flexibility
        for _idx, row in group.iterrows():
            fy = row["fiscal_year"]

            # Get trailing window (inclusive of current year)
            window_data = group[
                (group["fiscal_year"] > fy - window - 1) & (group["fiscal_year"] <= fy)
            ]

            # Count valid observations and significant changes
            valid_obs = window_data["is_significant_change"].notna().sum()
            n_changes = window_data["is_significant_change"].sum()

            # Require minimum observations
            if valid_obs >= min_years:
                payout_flex = n_changes / valid_obs
                results.append(
                    {
                        "gvkey": gvkey,
                        "fiscal_year": fy,
                        "payout_flexibility": payout_flex,
                    }
                )

    result = pd.DataFrame(results)

    if not result.empty:
        n_computed = result["payout_flexibility"].notna().sum()
        print(f"  Computed payout_flexibility for {n_computed:,} observations")
    else:
        print("  Warning: No payout flexibility computed (insufficient data)")

    return result


def compute_earnings_volatility(
    compustat_df: pd.DataFrame, min_years: int = 2, window: int = 5
) -> pd.DataFrame:
    """
    Compute Earnings Volatility = StdDev(annual EPS) over trailing 5 years.

    H3-03: Control variable for earnings stability.
    Higher values indicate MORE volatile earnings.

    Args:
        compustat_df: Compustat data with epspxq column
        min_years: Minimum observations required in window (default: 2)
        window: Rolling window in years (default: 5)

    Returns:
        DataFrame with gvkey, fiscal_year, earnings_volatility
    """
    print("\nComputing Earnings Volatility...")

    # Annualize quarterly EPS (sum quarters)
    annual_eps = annualize_quarterly_data(compustat_df, "epspxq")
    annual_eps = annual_eps.rename(columns={"annual_value": "eps"})

    # Sort by gvkey and fiscal_year for rolling calculation
    annual_eps = annual_eps.sort_values(["gvkey", "fiscal_year"])

    results = []

    for gvkey, group in annual_eps.groupby("gvkey"):
        group = group.sort_values("fiscal_year")

        # Compute rolling StdDev for each year
        for _idx, row in group.iterrows():
            fy = row["fiscal_year"]

            # Get trailing window (inclusive of current year)
            window_data = group[
                (group["fiscal_year"] > fy - window - 1) & (group["fiscal_year"] <= fy)
            ]["eps"]

            # Require minimum observations
            if window_data.notna().sum() >= min_years:
                eps_vol = window_data.std()
                results.append(
                    {
                        "gvkey": gvkey,
                        "fiscal_year": fy,
                        "earnings_volatility": eps_vol,
                    }
                )

    result = pd.DataFrame(results)

    if not result.empty:
        n_computed = result["earnings_volatility"].notna().sum()
        print(f"  Computed earnings_volatility for {n_computed:,} observations")
    else:
        print("  Warning: No earnings volatility computed (insufficient data)")

    return result


def compute_fcf_growth(compustat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute FCF Growth = (FCF_t - FCF_{t-1}) / |FCF_{t-1}|.

    H3-03: Control variable for cash flow dynamics.
    Where FCF = (OANCF - CAPX) / AT (Free Cash Flow to Assets)

    Uses absolute value in denominator to handle negative FCF.

    Args:
        compustat_df: Compustat data with oancfy, capxy, atq columns

    Returns:
        DataFrame with gvkey, fiscal_year, fcf_growth
    """
    print("\nComputing FCF Growth...")

    # Filter to rows with valid data
    df = compustat_df.loc[
        (compustat_df["atq"] > 0)
        & (compustat_df["oancfy"].notna())
        & (compustat_df["capxy"].notna()),
        :
    ].copy()

    # Compute FCF = (OANCF - CAPX) / AT
    # Note: oancfy and capxy are annual, atq is quarterly
    # We use atq as the denominator (it's the most recent asset value)
    df["fcf"] = (df["oancfy"] - df["capxy"].fillna(0)) / df["atq"]

    # Aggregate to fiscal year level (take mean for each firm-year)
    fcf_annual = df.groupby(["gvkey", "fiscal_year"], as_index=False)["fcf"].mean()

    # Sort by gvkey and fiscal_year - use .loc to ensure DataFrame type
    fcf_annual = fcf_annual.loc[:, ["gvkey", "fiscal_year", "fcf"]].sort_values(["gvkey", "fiscal_year"])

    results = []

    for gvkey, group in fcf_annual.groupby("gvkey"):
        group = cast(pd.DataFrame, group).sort_values("fiscal_year").reset_index(drop=True)

        # Compute year-over-year growth
        group["fcf_prior"] = group["fcf"].shift(1)

        # Compute growth rate (use abs in denominator for negative FCF)
        group["fcf_growth"] = np.where(
            group["fcf_prior"].abs() > 0.001,
            (group["fcf"] - group["fcf_prior"]) / group["fcf_prior"].abs(),
            np.nan,
        )

        # Collect results
        for _, row in group.iterrows():
            if pd.notna(row["fcf_growth"]):
                results.append(
                    {
                        "gvkey": gvkey,
                        "fiscal_year": row["fiscal_year"],
                        "fcf_growth": row["fcf_growth"],
                    }
                )

    result = pd.DataFrame(results)

    if not result.empty:
        n_computed = result["fcf_growth"].notna().sum()
        print(f"  Computed fcf_growth for {n_computed:,} observations")
    else:
        print("  Warning: No FCF growth computed (insufficient data)")

    return result


def compute_firm_maturity(compustat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Firm Maturity = RE / TE (Retained Earnings / Total Equity).

    H3-03: Control variable following DeAngelo et al.
    Higher values indicate MORE mature firms (more accumulated retained earnings).

    Uses quarterly req and seqq, taking end-of-year value per fiscal year.
    Allows negative RE (valid immaturity signal).

    Args:
        compustat_df: Compustat data with req, seqq columns

    Returns:
        DataFrame with gvkey, fiscal_year, firm_maturity
    """
    print("\nComputing Firm Maturity (RE/TE)...")

    # Filter to rows with valid equity > 0
    df = compustat_df.loc[
        (compustat_df["seqq"].notna()) & (compustat_df["seqq"] > 0),
        :
    ].copy()

    # Compute firm maturity = RE / TE
    df["firm_maturity"] = df["req"] / df["seqq"]

    # Aggregate to fiscal year level (take last/most recent value)
    # Sort by datadate to get end-of-year value
    df = cast(pd.DataFrame, df).sort_values(["gvkey", "fiscal_year", "datadate"])
    maturity_annual = df.groupby(["gvkey", "fiscal_year"]).last().reset_index()

    result = maturity_annual.loc[:, ["gvkey", "fiscal_year", "firm_maturity"]].copy()

    if not result.empty:
        n_computed = result["firm_maturity"].notna().sum()
        print(f"  Computed firm_maturity for {n_computed:,} observations")
    else:
        print("  Warning: No firm maturity computed (insufficient data)")

    return cast(pd.DataFrame, result)


def flag_dividend_payers(compustat_df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """
    Flag firms that paid dividends in at least one year of the 5-year window.

    This is required because stability/flexibility are undefined for never-payers.

    Args:
        compustat_df: Compustat data with dvpspq column
        window: Window in years to check for dividend payments (default: 5)

    Returns:
        DataFrame with gvkey, fiscal_year, is_div_payer (bool)
    """
    print("\nFlagging dividend payers...")

    # Annualize quarterly DPS
    annual_dps = annualize_quarterly_data(compustat_df, "dvpspq")
    annual_dps = annual_dps.rename(columns={"annual_value": "dps"})
    annual_dps = annual_dps.sort_values(["gvkey", "fiscal_year"])

    results = []

    for gvkey, group in annual_dps.groupby("gvkey"):
        group = group.sort_values("fiscal_year")

        # Flag if DPS > 0 in the window
        for _, row in group.iterrows():
            fy = row["fiscal_year"]

            # Check if any DPS > 0 in trailing window
            window_data = group[
                (group["fiscal_year"] > fy - window - 1) & (group["fiscal_year"] <= fy)
            ]["dps"]

            is_payer = (window_data > 0).any()
            results.append(
                {
                    "gvkey": gvkey,
                    "fiscal_year": fy,
                    "is_div_payer": is_payer,
                }
            )

    result = pd.DataFrame(results)

    n_payers = result["is_div_payer"].sum()
    print(f"  Flagged {n_payers:,} dividend-paying firm-years")

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


def parse_arguments():
    """Parse command-line arguments for 3.3_H3Variables.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 3.3: H3 Payout Policy Variables

Constructs dependent variables (Dividend Policy Stability, Payout Flexibility)
and control variables for H3 payout policy hypothesis testing.
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


def check_prerequisites(paths, args):
    """Validate all required inputs and prerequisite steps exist."""
    print("\nChecking prerequisites...")

    required_files = {
        "Manifest": paths["manifest_dir"] / "master_sample_manifest.parquet",
        "Compustat": paths["compustat_file"],
        "H1 Output": paths["h1_output_dir"] / "H1_CashHoldings.parquet",
    }

    all_ok = True
    for name, path in required_files.items():
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024) if path.is_file() else 0
            print(
                f"  [OK] {name}: {path} ({size_mb:.1f} MB)"
                if size_mb > 0
                else f"  [OK] {name}: {path}"
            )
        else:
            print(f"  [MISSING] {name}: {path}")
            all_ok = False

    return all_ok


# ==============================================================================
# Main
# ==============================================================================


def main() -> None:
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
        print("STEP 3.3: H3 Payout Policy Variables - DRY RUN")
        print(f"Timestamp: {timestamp}")
        print("=" * 60)

        prereq_ok = check_prerequisites(paths, args)
        if prereq_ok:
            print("\n[OK] All prerequisites validated")
            print("\nWould compute:")
            print(
                "  - Dividend Policy Stability (H3-01): -StdDev(Delta DPS) / |Mean(DPS)|"
            )
            print("  - Payout Flexibility (H3-02): % years with |Delta DPS| > 5%")
            print("  - Earnings Volatility (H3-03): StdDev(annual EPS)")
            print("  - FCF Growth (H3-03): YoY growth in (OANCF-CAPX)/AT")
            print("  - Firm Maturity (H3-03): RE / TE ratio")
            print(
                "  - Standard controls from H1: firm_size, roa, tobins_q, cash_holdings"
            )
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
    print("STEP 3.3: H3 Payout Policy Variables")
    print(f"Timestamp: {timestamp}")
    print("=" * 60)

    # Initialize statistics
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    mem_start = get_process_memory_mb()
    memory_readings = [mem_start["rss_mb"]]

    stats: Dict[str, Any] = {
        "step_id": "3.3_H3Variables",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0},
        "processing": {
            "variables_computed": [],
            "winsorization": {},
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

    # Extract sample gvkeys for memory optimization
    sample_gvkeys = manifest["gvkey"].unique().tolist()
    print(f"  Sample contains {len(sample_gvkeys):,} unique firms")

    # Load Compustat (filtered to sample first)
    print("\nCompustat:")
    stats["input"]["files"].append(str(paths["compustat_file"]))
    stats["input"]["checksums"][paths["compustat_file"].name] = compute_file_checksum(
        paths["compustat_file"]
    )
    compustat = load_compustat_h3(paths["compustat_file"], sample_gvkeys=sample_gvkeys)
    print_stat("Compustat rows (filtered)", value=len(compustat))

    # Load H1 standard controls
    print("\nH1 Standard Controls:")
    h1_controls = load_h1_standard_controls(paths["h1_output_dir"])

    # ========================================================================
    # Compute H3 Variables
    # ========================================================================

    print("\n" + "=" * 60)
    print("Computing H3 Variables")
    print("=" * 60)

    # Compute dependent variables
    div_stability_df = compute_div_stability(compustat)
    payout_flexibility_df = compute_payout_flexibility(compustat)

    # Compute H3-specific controls
    earnings_volatility_df = compute_earnings_volatility(compustat)
    fcf_growth_df = compute_fcf_growth(compustat)
    firm_maturity_df = compute_firm_maturity(compustat)

    # Flag dividend payers
    div_payer_df = flag_dividend_payers(compustat)

    stats["processing"]["variables_computed"] = [
        "div_stability",
        "payout_flexibility",
        "earnings_volatility",
        "fcf_growth",
        "firm_maturity",
        "is_div_payer",
    ]

    # ========================================================================
    # Merge Variables
    # ========================================================================

    print("\n" + "=" * 60)
    print("Merging Variables")
    print("=" * 60)

    # Start with manifest as base
    manifest_for_merge = manifest[["gvkey", "year"]].drop_duplicates()
    h3_data = manifest_for_merge.rename(columns={"year": "fiscal_year"}).copy()

    print(f"  Base firm-years from manifest: {len(h3_data):,}")

    # Merge each computed variable
    for var_name, var_df in [
        ("div_stability", div_stability_df),
        ("payout_flexibility", payout_flexibility_df),
        ("earnings_volatility", earnings_volatility_df),
        ("fcf_growth", fcf_growth_df),
        ("firm_maturity", firm_maturity_df),
        ("is_div_payer", div_payer_df),
    ]:
        h3_data = h3_data.merge(
            var_df[["gvkey", "fiscal_year", var_name]],
            on=["gvkey", "fiscal_year"],
            how="left",
        )
        n_valid = h3_data[var_name].notna().sum()
        print(f"  {var_name}: {n_valid:,} valid")

    # Merge H1 standard controls
    if h1_controls is not None:
        print("\nMerging H1 standard controls...")
        h3_data = h3_data.merge(
            h1_controls[
                [
                    "gvkey",
                    "fiscal_year",
                    "firm_size",
                    "roa",
                    "tobins_q",
                    "cash_holdings",
                ]
            ],
            on=["gvkey", "fiscal_year"],
            how="left",
        )
        for col in ["firm_size", "roa", "tobins_q", "cash_holdings"]:
            n_valid = h3_data[col].notna().sum()
            print(f"  {col}: {n_valid:,} valid")

    # Add file_name column from manifest
    # Note: Multiple files (speeches) can exist per gvkey-year.
    # We take one file_name as a reference (not unique identifier).
    file_ref = manifest[["gvkey", "year", "file_name"]].drop_duplicates(
        subset=["gvkey", "year"], keep="first"
    )
    h3_data = h3_data.merge(
        file_ref,
        left_on=["gvkey", "fiscal_year"],
        right_on=["gvkey", "year"],
        how="left",
    )

    print(f"  Final merged data: {len(h3_data):,} observations")

    # ========================================================================
    # Filter to Dividend Payers
    # ========================================================================

    print("\n" + "=" * 60)
    print("Filtering to Dividend Payers")
    print("=" * 60)

    before_count = len(h3_data)
    h3_data_filtered = h3_data[h3_data["is_div_payer"]].copy()
    after_count = len(h3_data_filtered)

    print(f"  Before filter: {before_count:,} observations")
    print(f"  After filter: {after_count:,} observations")
    print(f"  Filtered out: {before_count - after_count:,} non-dividend-payers")

    # Update h3_data reference
    h3_data = h3_data_filtered

    # ========================================================================
    # Apply Winsorization
    # ========================================================================

    print("\n" + "=" * 60)
    print("Applying Winsorization (1%/99%)")
    print("=" * 60)

    continuous_vars = [
        "div_stability",
        "payout_flexibility",
        "earnings_volatility",
        "fcf_growth",
        "firm_maturity",
    ]

    for var in continuous_vars:
        if var in h3_data.columns and h3_data[var].notna().sum() > 0:
            before_mean = h3_data[var].mean()
            h3_data[var] = winsorize_series(h3_data[var], lower=0.01, upper=0.99)
            after_mean = h3_data[var].mean()
            stats["processing"]["winsorization"][var] = {
                "before_mean": round(float(before_mean), 4)
                if pd.notna(before_mean)
                else None,
                "after_mean": round(float(after_mean), 4)
                if pd.notna(after_mean)
                else None,
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
        "div_stability",
        "payout_flexibility",
        "earnings_volatility",
        "fcf_growth",
        "firm_maturity",
        "firm_size",
        "roa",
        "tobins_q",
        "cash_holdings",
        "is_div_payer",
    ]

    for var in output_columns[3:]:  # Skip file_name, gvkey, fiscal_year
        if var in h3_data.columns:
            var_data = h3_data[var]
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
    final_output = h3_data[output_columns].copy()

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
    output_file = paths["output_dir"] / "H3_PayoutPolicy.parquet"
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
        "div_stability",
        "payout_flexibility",
        "earnings_volatility",
        "fcf_growth",
        "firm_maturity",
    ]
    anomalies = detect_anomalies_zscore(final_output, numeric_cols, threshold=3.0)
    total_anomalies = sum(a["count"] for a in anomalies.values())
    print(f"  Anomalies detected (z>3): {total_anomalies}")

    # Print summary
    print_stats_summary(stats)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"H3 Variables computed: {len(final_output):,} observations")
    print("  Dependent variables: div_stability, payout_flexibility")
    print("  H3-specific controls: earnings_volatility, fcf_growth, firm_maturity")
    print("  Standard controls: firm_size, roa, tobins_q, cash_holdings")
    print(f"\nOutputs saved to: {paths['output_dir']}")
    print(f"Log saved to: {paths['log_file']}")

    dual_writer.close()
    sys.stdout = dual_writer.terminal


if __name__ == "__main__":
    main()
