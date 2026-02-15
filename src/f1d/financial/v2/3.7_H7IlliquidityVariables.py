#!/usr/bin/env python3
"""
==============================================================================
STEP 3.7: H7 Illiquidity Variables
==============================================================================
ID: 3.7_H7IlliquidityVariables
Description: Construct illiquidity dependent variables for H7 (Speech
             Uncertainty -> Stock Illiquidity). Implements Amihud (2002)
             as primary measure, Roll (1984) as robustness.

Model Specification (H7):
    Illiquidity_{t+1} = beta0 + beta1*Uncertainty_t + gamma*Controls + FE

Hypothesis:
    H7a: beta1 > 0 (Higher uncertainty -> Higher illiquidity)

Variables Computed:
    - Amihud Illiquidity: Primary DV per Amihud (2002) formula
    - Roll Spread: Robustness DV per Roll (1984)
    - Forward-looking DV: Illiquidity at t+1
    - IVs: V2 speech uncertainty measures (4 measures)
    - Controls: Size, Leverage, ROA, MTB, Volatility, Returns, Current Ratio

Inputs:
    - CRSP Daily Stock File (DSF): RET, VOL, PRC for illiquidity calculation
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/: Speech uncertainty measures
    - 4_Outputs/3_Financial_Features/latest/: Firm controls (market_variables)
    - 4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet: Sample base

Outputs:
    - 4_Outputs/3_Financial_V2/{timestamp}/H7_Illiquidity.parquet
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
import gc
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

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


# Default configuration
DEFAULT_CONFIG: Dict[str, Any] = {
    "year_range": (2002, 2018),
    "min_trading_days": 50,
    "min_years_per_firm": 3,
    "winsorize_lower": 0.01,
    "winsorize_upper": 0.99,
    "amihud_scale": 1e6,
    "sic_financial": (6000, 6999),
    "sic_utilities": (4900, 4999),
}


def setup_paths(config, timestamp):
    """Set up all required paths"""
    # Go up from src/f1d/financial/v2/ to project root (5 levels)
    root = Path(__file__).parent.parent.parent.parent.parent

    # Resolve manifest directory
    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.4_AssembleManifest",
        required_file="master_sample_manifest.parquet",
    )

    # Resolve linguistic variables directory
    linguistic_dir = get_latest_output_dir(
        root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
        required_file="linguistic_variables_2002.parquet",
    )

    # Resolve market variables directory (for additional controls)
    market_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_Features",
        required_file="market_variables_2002.parquet",
    )

    paths = {
        "root": root,
        "manifest_dir": manifest_dir,
        "linguistic_dir": linguistic_dir,
        "market_dir": market_dir,
        "crsp_dir": root / "1_Inputs" / "CRSP_DSF",
        "ccm_file": root
        / "1_Inputs"
        / "CRSPCompustat_CCM"
        / "CRSPCompustat_CCM.parquet",
    }

    # Output directory
    output_base = root / "4_Outputs" / "3_Financial_V2"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "3_Financial_V2"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H7.log"

    return paths


# ==============================================================================
# Data Loading Functions
# ==============================================================================


def load_manifest(manifest_dir):
    """Load master sample manifest"""
    manifest_file = manifest_dir / "master_sample_manifest.parquet"
    validate_input_file(manifest_file, must_exist=True)

    df = pd.read_parquet(manifest_file)
    print(f"  Loaded manifest: {len(df):,} calls")

    # Ensure gvkey is string and zero-padded
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    if "start_date" in df.columns:
        df["start_date"] = pd.to_datetime(df["start_date"])
        df["year"] = df["start_date"].dt.year
    elif "year" not in df.columns:
        raise ValueError("Manifest must have start_date or year column")

    return df


def load_ccm(ccm_file):
    """Load CRSP-Compustat link file"""
    if not ccm_file.exists():
        print(f"  WARNING: CCM file not found: {ccm_file}")
        return None

    validate_input_file(ccm_file, must_exist=True)
    ccm = pd.read_parquet(ccm_file)

    # Normalize gvkey
    ccm["gvkey_clean"] = ccm["gvkey"].astype(str).str.zfill(6)

    # Filter for primary links
    ccm = ccm.loc[ccm["LINKPRIM"].isin(["P", "C", "L"]), :]

    print(f"  Loaded CCM: {len(ccm):,} links")
    return ccm


def load_crsp_for_years(crsp_dir, years):
    """Load CRSP daily data for specified years"""
    all_data = []

    for year in years:
        for q in range(1, 5):
            fp = crsp_dir / f"CRSP_DSF_{year}_Q{q}.parquet"
            if fp.exists():
                try:
                    df = pd.read_parquet(
                        fp,
                        columns=[
                            "PERMNO",
                            "date",
                            "RET",
                            "VOL",
                            "PRC",
                            "ASKHI",
                            "BIDLO",
                        ],
                    )
                    all_data.append(df)
                except Exception as e:
                    print(f"    Warning reading {fp.name}: {e}")

    if not all_data:
        return None

    crsp = pd.concat(all_data, ignore_index=True)

    # Normalize
    crsp["date"] = pd.to_datetime(crsp["date"])
    for col in ["RET", "VOL", "PRC", "ASKHI", "BIDLO"]:
        if col in crsp.columns:
            crsp[col] = pd.to_numeric(crsp[col], errors="coerce")

    # Use absolute value of price (CRSP codes negative prices)
    if "PRC" in crsp.columns:
        crsp["PRC"] = crsp["PRC"].abs()

    print(f"  Loaded CRSP: {len(crsp):,} observations")
    return crsp


def load_linguistic_variables(linguistic_dir, years):
    """Load and merge linguistic variables across years"""
    dfs = []

    for year in years:
        fp = linguistic_dir / f"linguistic_variables_{year}.parquet"
        if fp.exists():
            try:
                df = pd.read_parquet(fp)
                dfs.append(df)
            except Exception as e:
                print(f"    Warning reading {fp.name}: {e}")

    if not dfs:
        raise FileNotFoundError(f"No linguistic variables found for years {years}")

    combined = pd.concat(dfs, ignore_index=True)

    # Ensure gvkey is standardized
    combined["gvkey"] = combined["gvkey"].astype(str).str.zfill(6)

    # Select uncertainty measures
    uncertainty_cols = [
        "file_name",
        "gvkey",
        "start_date",
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
    ]

    # Keep only columns that exist
    uncertainty_cols = [c for c in uncertainty_cols if c in combined.columns]

    result = combined[uncertainty_cols].copy()

    # Create year if not present
    if "start_date" in result.columns:
        result["start_date"] = pd.to_datetime(result["start_date"])
        result["year"] = result["start_date"].dt.year

    print(f"  Loaded linguistic variables: {len(result):,} rows")
    return result


def load_market_variables(market_dir, years):
    """Load market variables for additional controls"""
    dfs = []

    for year in years:
        fp = market_dir / f"market_variables_{year}.parquet"
        if fp.exists():
            try:
                df = pd.read_parquet(fp)
                dfs.append(df)
            except Exception as e:
                print(f"    Warning reading {fp.name}: {e}")

    if not dfs:
        return None

    combined = pd.concat(dfs, ignore_index=True)

    # Ensure gvkey is standardized
    combined["gvkey"] = combined["gvkey"].astype(str).str.zfill(6)

    # Select useful variables
    market_cols = [
        c
        for c in ["file_name", "gvkey", "year", "StockRet", "Volatility"]
        if c in combined.columns
    ]

    result = combined[market_cols].copy() if market_cols else None

    if result is not None:
        print(f"  Loaded market variables: {len(result):,} rows")

    return result


# ==============================================================================
# Illiquidity Calculation Functions
# ==============================================================================


def calculate_amihud_illiquidity(crsp_df, permno_list=None, min_days=50):
    """
    Calculate Amihud (2002) illiquidity measure at firm-year level.

    ILLIQ_{i,y} = (1/D_{i,y}) * sum(|r_{i,y,d}| / VOLD_{i,y,d})

    Where:
        D = number of valid trading days in year
        r = daily return (decimal)
        VOLD = daily dollar volume = |PRC| * VOL

    Args:
        crsp_df: CRSP daily data with PERMNO, date, RET, VOL, PRC
        permno_list: Optional list of PERMNOs to filter for
        min_days: Minimum trading days required (default: 50)

    Returns:
        DataFrame with permno, year, amihud_illiquidity, trading_days
    """
    print("\nCalculating Amihud illiquidity...")

    # Filter to sample permnos if provided
    if permno_list is not None:
        crsp_df = crsp_df[crsp_df["PERMNO"].isin(permno_list)].copy()

    # Add year
    crsp_df["year"] = crsp_df["date"].dt.year

    # Filter valid observations
    valid = crsp_df[
        (crsp_df["RET"].notna())
        & (crsp_df["RET"].between(-0.66, 0.66))  # Exclude extreme returns
        & (crsp_df["VOL"] > 0)
        & (crsp_df["PRC"] > 0)
    ].copy()

    # Calculate dollar volume (CRSP: VOL * PRC)
    valid["dollar_volume"] = valid["VOL"] * valid["PRC"]

    # Daily Amihud ratio: |RET| / dollar_volume
    valid["daily_illiq"] = valid["RET"].abs() / valid["dollar_volume"]

    # Aggregate to firm-year level
    illiq = (
        valid.groupby(["PERMNO", "year"])
        .agg(
            amihud_illiquity=("daily_illiq", "mean"),
            trading_days=("daily_illiq", "count"),
        )
        .reset_index()
    )

    # Require minimum trading days
    illiq = illiq[illiq["trading_days"] >= min_days].copy()

    # Scale by 1e6 for interpretability
    illiq["amihud_illiquidity"] = illiq["amihud_illiquity"] * 1e6

    # Add log-transformed version
    illiq["log_amihud"] = np.log1p(illiq["amihud_illiquity"])

    print(f"  Computed Amihud for {len(illiq):,} firm-years")
    print(f"    Mean: {illiq['amihud_illiquidity'].mean():.4f}")
    print(f"    Median: {illiq['amihud_illiquidity'].median():.4f}")

    return illiq[["PERMNO", "year", "amihud_illiquidity", "log_amihud", "trading_days"]]


def calculate_roll_spread(crsp_df, permno_list=None, min_days=50):
    """
    Calculate Roll (1984) implicit spread from price autocovariance.

    SPRD = 2 * sqrt(-cov(r_t, r_{t-1}))

    Args:
        crsp_df: CRSP daily data with PERMNO, date, RET
        permno_list: Optional list of PERMNOs to filter for
        min_days: Minimum observations required (default: 50)

    Returns:
        DataFrame with permno, year, roll_spread
    """
    print("\nCalculating Roll spread...")

    # Filter to sample permnos if provided
    if permno_list is not None:
        crsp_df = crsp_df[crsp_df["PERMNO"].isin(permno_list)].copy()

    # Add year
    crsp_df["year"] = crsp_df["date"].dt.year

    # Filter valid returns
    valid = crsp_df[
        (crsp_df["RET"].notna()) & (crsp_df["RET"].between(-0.66, 0.66))
    ].copy()

    def roll_for_group(group):
        if len(group) < min_days:
            return pd.Series(
                {"roll_spread": np.nan, "autocov": np.nan, "n_obs": len(group)}
            )

        # Calculate first-order autocovariance
        # autocov = E[(X_t - mu) * (X_{t-1} - mu)]
        rets = group["RET"].values
        if len(rets) < 2:
            return pd.Series(
                {"roll_spread": np.nan, "autocov": np.nan, "n_obs": len(group)}
            )

        # Manual autocovariance calculation at lag 1
        mean_ret = np.mean(rets)
        deviations = rets - mean_ret
        # Lag 1 autocovariance
        autocov = np.mean(deviations[1:] * deviations[:-1])

        if autocov >= 0:
            return pd.Series(
                {"roll_spread": np.nan, "autocov": autocov, "n_obs": len(group)}
            )

        return pd.Series(
            {
                "roll_spread": 2 * np.sqrt(-autocov),
                "autocov": autocov,
                "n_obs": len(group),
            }
        )

    roll = (
        valid.groupby(["PERMNO", "year"])
        .apply(roll_for_group, include_groups=False)
        .reset_index()
    )

    # Count valid spreads
    n_valid = roll["roll_spread"].notna().sum()
    print(f"  Computed Roll spread for {len(roll):,} firm-years ({n_valid} valid)")

    return roll[["PERMNO", "year", "roll_spread", "autocov", "n_obs"]]


def calculate_stock_volatility_and_returns(crsp_df, permno_list=None, min_days=50):
    """
    Calculate annualized stock return volatility and annual stock returns from CRSP daily data.

    Volatility = Annualized standard deviation of daily returns * 100
    StockRet = Cumulative annual return * 100

    Args:
        crsp_df: CRSP daily data with PERMNO, date, RET
        permno_list: Optional list of PERMNOs to filter for
        min_days: Minimum trading days required (default: 50)

    Returns:
        DataFrame with PERMNO, year, Volatility, StockRet
    """
    print("Calculating stock volatility and returns from CRSP...")

    # Filter to sample permnos if provided
    if permno_list is not None:
        crsp_df = crsp_df[crsp_df["PERMNO"].isin(permno_list)].copy()

    # Add year
    crsp_df["year"] = crsp_df["date"].dt.year

    # Filter valid returns
    valid = crsp_df[
        (crsp_df["RET"].notna()) & (crsp_df["RET"].between(-0.66, 0.66))
    ].copy()

    # Calculate annual metrics for each firm-year
    def calc_metrics(group):
        rets = group["RET"].dropna()
        n = len(rets)
        if n < min_days:
            return pd.Series({"Volatility": np.nan, "StockRet": np.nan, "n_obs": n})
        # Daily volatility (std dev), annualized by sqrt(252) and convert to percent
        vol = rets.std() * 100 * (252**0.5)
        # Annual stock return: (1 + r1*r2*...*rn) - 1, * 100
        stock_ret = ((1 + rets).prod() - 1) * 100
        return pd.Series({"Volatility": vol, "StockRet": stock_ret, "n_obs": n})

    metrics_df = (
        valid.groupby(["PERMNO", "year"])
        .apply(calc_metrics, include_groups=False)
        .reset_index()
    )

    # Require minimum trading days
    metrics_df = metrics_df[metrics_df["n_obs"] >= min_days].copy()

    print(f"  Computed metrics for {len(metrics_df):,} firm-years")
    if len(metrics_df) > 0:
        if metrics_df["Volatility"].notna().any():
            print(
                f"    Volatility - Mean: {metrics_df['Volatility'].mean():.2f}%, Median: {metrics_df['Volatility'].median():.2f}%"
            )
        if metrics_df["StockRet"].notna().any():
            print(
                f"    StockRet - Mean: {metrics_df['StockRet'].mean():.2f}%, Median: {metrics_df['StockRet'].median():.2f}%"
            )

    return metrics_df[["PERMNO", "year", "Volatility", "StockRet"]]


# ==============================================================================
# Sample Construction Functions
# ==============================================================================


def winsorize_series(series, lower=0.01, upper=0.99):
    """Winsorize a series at specified percentiles"""
    if series.notna().sum() == 0:
        return series

    lower_bound = series.quantile(lower)
    upper_bound = series.quantile(upper)
    return series.clip(lower=lower_bound, upper=upper_bound)


def apply_sample_restrictions(df, config):
    """Apply sample restrictions per methodology"""
    print("\nApplying sample restrictions...")

    initial_rows = len(df)

    # Exclude financial firms (SIC 6000-6999)
    if "sic" in df.columns:
        df = df[
            ~df["sic"].between(config["sic_financial"][0], config["sic_financial"][1])
        ].copy()
        print(f"  After financial exclusion: {len(df):,} rows")

    # Exclude utilities (SIC 4900-4999)
    if "sic" in df.columns:
        df = df[
            ~df["sic"].between(config["sic_utilities"][0], config["sic_utilities"][1])
        ].copy()
        print(f"  After utilities exclusion: {len(df):,} rows")

    # Require minimum years per firm
    firm_year_counts = df.groupby("gvkey")["year"].transform("count")
    df = df[firm_year_counts >= config["min_years_per_firm"]].copy()
    print(f"  After min years per firm: {len(df):,} rows")

    excluded = initial_rows - len(df)
    print(f"  Total excluded: {excluded:,} ({excluded / initial_rows * 100:.1f}%)")

    return df


# ==============================================================================
# CLI and Prerequisites
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="""
STEP 3.7: H7 Illiquidity Variables

Constructs illiquidity dependent variables for H7 hypothesis testing.
Implements Amihud (2002) as primary measure, Roll (1984) as robustness.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    return parser.parse_args()


def check_prerequisites(paths):
    """Validate all required inputs exist"""
    print("\nChecking prerequisites...")

    all_ok = True

    # Check manifest
    manifest_file = paths["manifest_dir"] / "master_sample_manifest.parquet"
    if manifest_file.exists():
        print(f"  [OK] Manifest: {paths['manifest_dir']}")
    else:
        print(f"  [MISSING] Manifest: {manifest_file}")
        all_ok = False

    # Check linguistic variables
    ling_file = paths["linguistic_dir"] / "linguistic_variables_2002.parquet"
    if ling_file.exists():
        print(f"  [OK] Linguistic variables: {paths['linguistic_dir']}")
    else:
        print(f"  [MISSING] Linguistic variables: {ling_file}")
        all_ok = False

    # Check CRSP directory
    if paths["crsp_dir"].exists():
        crsp_files = list(paths["crsp_dir"].glob("CRSP_DSF_*.parquet"))
        print(f"  [OK] CRSP directory: {paths['crsp_dir']} ({len(crsp_files)} files)")
    else:
        print(f"  [MISSING] CRSP directory: {paths['crsp_dir']}")
        all_ok = False

    # Check CCM (optional)
    if paths["ccm_file"].exists():
        print(f"  [OK] CCM link file: {paths['ccm_file']}")
    else:
        print(f"  [WARNING] CCM link file not found: {paths['ccm_file']}")

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

    # Handle dry-run mode
    if args.dry_run:
        print("=" * 60)
        print("STEP 3.7: H7 Illiquidity Variables - DRY RUN")
        print(f"Timestamp: {timestamp}")
        print("=" * 60)

        prereq_ok = check_prerequisites(paths)
        if prereq_ok:
            print("\n[OK] All prerequisites validated")
            print("\nWould compute:")
            print("  - Amihud (2002) illiquidity at firm-year level")
            print("  - Roll (1984) spread as robustness")
            print("  - Merge with V2 speech uncertainty measures")
            print("  - Merge with firm controls")
            print("  - Create forward-looking DV (Illiquidity_{t+1})")
            print(f"\nOutput would be written to: {paths['output_dir']}")
            sys.exit(0)
        else:
            print("\n[ERROR] Prerequisites not met")
            sys.exit(1)

    # Check prerequisites
    prereq_ok = check_prerequisites(paths)
    if not prereq_ok:
        print("\n[ERROR] Prerequisites not met. Exiting.")
        sys.exit(1)

    # Setup logging
    dual_writer = DualWriter(paths["log_file"])
    sys.stdout = dual_writer

    print("=" * 60)
    print("STEP 3.7: H7 Illiquidity Variables")
    print(f"Timestamp: {timestamp}")
    print("=" * 60)

    # Initialize statistics
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    mem_start = get_process_memory_mb()
    memory_readings = [mem_start["rss_mb"]]

    stats: Dict[str, Any] = {
        "step_id": "3.7_H7IlliquidityVariables",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0},
        "processing": {
            "variables_computed": [],
            "winsorization": {},
            "sample_restrictions": {},
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

    print("\n" + "=" * 60)
    print("Loading Data")
    print("=" * 60)

    # Load config defaults
    cfg = DEFAULT_CONFIG.copy()
    year_range = cfg["year_range"]
    years = list(range(year_range[0], year_range[1] + 1))

    # Load manifest
    print("\nManifest:")
    manifest = load_manifest(paths["manifest_dir"])
    stats["input"]["total_rows"] += len(manifest)

    # Load CCM link
    print("\nCCM Link:")
    ccm = load_ccm(paths["ccm_file"])

    # Get list of PERMNOs from manifest (if available)
    permno_list = None
    if "permno" in manifest.columns:
        permno_list = manifest["permno"].dropna().unique().tolist()
        print(f"  Sample PERMNOs: {len(permno_list):,}")

    # Load CRSP data
    print("\nCRSP Daily Stock Data:")
    crsp = load_crsp_for_years(
        paths["crsp_dir"], list(range(year_range[0] - 1, year_range[1] + 2))
    )
    if crsp is None:
        print("[ERROR] Failed to load CRSP data")
        sys.exit(1)

    # Load linguistic variables
    print("\nLinguistic Variables:")
    linguistic = load_linguistic_variables(paths["linguistic_dir"], years)

    # Load market variables (for additional controls)
    print("\nMarket Variables:")
    market = load_market_variables(paths["market_dir"], years)

    # ========================================================================
    # Calculate Illiquidity Measures
    # ========================================================================

    print("\n" + "=" * 60)
    print("Calculating Illiquidity Measures")
    print("=" * 60)

    # Calculate Amihud illiquidity
    amihud_df = calculate_amihud_illiquidity(crsp, permno_list, cfg["min_trading_days"])
    stats["processing"]["variables_computed"].append("amihud_illiquidity")

    # Calculate Roll spread
    roll_df = calculate_roll_spread(crsp, permno_list, cfg["min_trading_days"])
    stats["processing"]["variables_computed"].append("roll_spread")

    # Calculate stock volatility and returns from CRSP daily data
    volatility_df = calculate_stock_volatility_and_returns(
        crsp, permno_list, cfg["min_trading_days"]
    )
    stats["processing"]["variables_computed"].append("stock_volatility_returns")

    # Free CRSP memory
    del crsp
    gc.collect()

    # ========================================================================
    # Merge Datasets
    # ========================================================================

    print("\n" + "=" * 60)
    print("Merging Datasets")
    print("=" * 60)

    # Start with linguistic variables (at call level)
    df = linguistic.copy()

    # Aggregate linguistic variables to firm-year level
    print("\nAggregating linguistic variables to firm-year...")
    linguistic_agg = (
        df.groupby(["gvkey", "year"])
        .agg(
            {
                "Manager_QA_Uncertainty_pct": "mean",
                "CEO_QA_Uncertainty_pct": "mean",
                "Manager_Pres_Uncertainty_pct": "mean",
                "CEO_Pres_Uncertainty_pct": "mean",
            }
        )
        .reset_index()
    )

    print(f"  Linguistic firm-year observations: {len(linguistic_agg):,}")

    # Create permno crosswalk from manifest
    print("\nCreating permno crosswalk...")
    if "permno" in manifest.columns and manifest["permno"].notna().any():
        crosswalk = manifest[["gvkey", "permno"]].drop_duplicates()
        crosswalk["permno"] = pd.to_numeric(crosswalk["permno"], errors="coerce")
        crosswalk = crosswalk[crosswalk["permno"].notna()].copy()
        print(f"  Direct permno links: {len(crosswalk):,}")
    elif ccm is not None:
        crosswalk = ccm[["gvkey_clean", "LPERMNO"]].drop_duplicates()
        crosswalk["gvkey"] = crosswalk["gvkey_clean"]
        crosswalk["permno"] = pd.to_numeric(crosswalk["LPERMNO"], errors="coerce")
        crosswalk = crosswalk[["gvkey", "permno"]].drop_duplicates()
        crosswalk = crosswalk[crosswalk["permno"].notna()].copy()
        print(f"  CCM permno links: {len(crosswalk):,}")
    else:
        print("  WARNING: No permno crosswalk available")
        crosswalk = None

    # Merge illiquidity measures
    if crosswalk is not None:
        amihud_df = amihud_df.merge(
            crosswalk, left_on="PERMNO", right_on="permno", how="left"
        )
        roll_df = roll_df.merge(
            crosswalk, left_on="PERMNO", right_on="permno", how="left"
        )

        # Merge to linguistic data
        df = linguistic_agg.merge(
            amihud_df[
                ["gvkey", "year", "amihud_illiquidity", "log_amihud", "trading_days"]
            ],
            on=["gvkey", "year"],
            how="left",
        )

        df = df.merge(
            roll_df[["gvkey", "year", "roll_spread"]], on=["gvkey", "year"], how="left"
        )

        # Merge volatility/returns via permno crosswalk
        volatility_df = volatility_df.merge(
            crosswalk, left_on="PERMNO", right_on="permno", how="left"
        )

        # Merge volatility/returns to linguistic data
        df = df.merge(
            volatility_df[["gvkey", "year", "Volatility", "StockRet"]],
            on=["gvkey", "year"],
            how="left",
        )

        print(f"  After merging illiquidity: {len(df):,} observations")
        print(f"    Amihud valid: {df['amihud_illiquidity'].notna().sum():,}")
        print(f"    Roll spread valid: {df['roll_spread'].notna().sum():,}")
        print(f"    Volatility valid: {df['Volatility'].notna().sum():,}")
        print(f"    StockRet valid: {df['StockRet'].notna().sum():,}")

    # Merge market variables (for additional controls)
    # Note: This is now a fallback since Volatility/StockRet are calculated directly from CRSP
    if market is not None:
        df = df.merge(
            market[["gvkey", "year", "StockRet", "Volatility"]],
            on=["gvkey", "year"],
            how="left",
        )
        print(f"  After merging market variables: {len(df):,} observations")

    # ========================================================================
    # Create Forward-Looking Dependent Variable
    # ========================================================================

    print("\n" + "=" * 60)
    print("Creating Forward-Looking DV")
    print("=" * 60)

    # Sort by firm and year
    df = df.sort_values(["gvkey", "year"]).reset_index(drop=True)

    # Create lagged illiquidity (Illiquidity_{t+1})
    df["amihud_lag1"] = df.groupby("gvkey")["amihud_illiquidity"].shift(-1)
    df["log_amihud_lag1"] = df.groupby("gvkey")["log_amihud"].shift(-1)
    df["roll_spread_lag1"] = df.groupby("gvkey")["roll_spread"].shift(-1)

    print(f"  Amihud t+1 valid: {df['amihud_lag1'].notna().sum():,}")
    print(f"  Roll spread t+1 valid: {df['roll_spread_lag1'].notna().sum():,}")

    # Require valid DV for regression sample
    regression_sample = df[df["amihud_lag1"].notna()].copy()
    print(f"  Regression sample: {len(regression_sample):,} observations")

    # ========================================================================
    # Apply Sample Restrictions and Winsorization
    # ========================================================================

    print("\n" + "=" * 60)
    print("Sample Construction")
    print("=" * 60)

    len(regression_sample)
    regression_sample = apply_sample_restrictions(regression_sample, cfg)

    # Winsorize continuous variables
    print("\nApplying winsorization (1%/99%)...")

    continuous_vars = [
        "amihud_lag1",
        "log_amihud_lag1",
        "roll_spread_lag1",
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
    ]

    if "Volatility" in regression_sample.columns:
        continuous_vars.append("Volatility")
    if "StockRet" in regression_sample.columns:
        continuous_vars.append("StockRet")

    for var in continuous_vars:
        if (
            var in regression_sample.columns
            and regression_sample[var].notna().sum() > 0
        ):
            before_mean = regression_sample[var].mean()
            regression_sample[var] = winsorize_series(
                regression_sample[var],
                lower=cfg["winsorize_lower"],
                upper=cfg["winsorize_upper"],
            )
            after_mean = regression_sample[var].mean()
            stats["processing"]["winsorization"][var] = {
                "before_mean": round(float(before_mean), 4)
                if not pd.isna(before_mean)
                else None,
                "after_mean": round(float(after_mean), 4)
                if not pd.isna(after_mean)
                else None,
            }
            print(f"  {var}: winsorized")

    final_sample = regression_sample
    print(f"\nFinal sample: {len(final_sample):,} observations")
    print(f"  Unique firms: {final_sample['gvkey'].nunique():,}")
    print(f"  Years: {final_sample['year'].min()} - {final_sample['year'].max()}")

    # ========================================================================
    # Compute Variable Statistics
    # ========================================================================

    print("\n" + "=" * 60)
    print("Computing Variable Statistics")
    print("=" * 60)

    output_columns = [
        "gvkey",
        "year",
        "amihud_lag1",
        "log_amihud_lag1",
        "roll_spread_lag1",
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
    ]

    if "Volatility" in final_sample.columns:
        output_columns.append("Volatility")
    if "StockRet" in final_sample.columns:
        output_columns.append("StockRet")
    if "trading_days" in final_sample.columns:
        output_columns.append("trading_days")

    for var in output_columns[2:]:  # Skip gvkey, year
        if var in final_sample.columns:
            var_data = final_sample[var]
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
                f"  {var}: mean={stats['variables'][var]['mean']}, n={stats['variables'][var]['n']}"
            )

    # ========================================================================
    # Prepare Final Output
    # ========================================================================

    print("\n" + "=" * 60)
    print("Preparing Output")
    print("=" * 60)

    # Select output columns
    final_output = final_sample[output_columns].copy()
    final_output = final_output.sort_values(["gvkey", "year"]).reset_index(drop=True)

    print(f"  Final output rows: {len(final_output):,}")

    # ========================================================================
    # Write Outputs
    # ========================================================================

    print("\n" + "=" * 60)
    print("Writing Outputs")
    print("=" * 60)

    # Write parquet file
    output_file = paths["output_dir"] / "H7_Illiquidity.parquet"
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
        "amihud_lag1",
        "log_amihud_lag1",
        "roll_spread_lag1",
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
    ]
    anomalies = detect_anomalies_zscore(final_output, numeric_cols, threshold=3.0)
    total_anomalies = sum(a["count"] for a in anomalies.values())
    print(f"  Anomalies detected (z>3): {total_anomalies}")

    # Print summary
    print_stats_summary(stats)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"H7 Variables computed: {len(final_output):,} observations")
    print("  Primary DV: Amihud illiquidity (t+1)")
    print("  Robustness DV: Roll spread (t+1)")
    print("  IVs: 4 speech uncertainty measures")
    print(f"\nOutputs saved to: {paths['output_dir']}")
    print(f"Log saved to: {paths['log_file']}")

    dual_writer.close()
    sys.stdout = dual_writer.terminal


if __name__ == "__main__":
    main()
