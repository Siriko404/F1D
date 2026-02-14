#!/usr/bin/env python3
"""
================================================================================
STEP 3.9: H2 Biddle (2009) Investment Residual (V2 - PRisk Interaction)
================================================================================
ID: 3.9_H2_BiddleInvestmentResidual
Description: Constructs the correct Biddle (2009) investment residual as the
             dependent variable for H2 regression (PRisk x Uncertainty -> Investment).

Purpose: Phase 30's roa_residual is INCORRECT for testing investment efficiency
(it regresses Delta ROA on CapEx, testing investment -> profitability). This
script implements the correct Biddle (2009) specification:

    Investment_t = beta0 + beta1*Tobin's_Q_t-1 + beta2*Sales_Growth_t-1 + epsilon

by FF48 industry-year, where epsilon (InvestmentResidual) represents deviation
from expected investment given growth opportunities.

Investment = (CapEx + R&D + Acquisitions - AssetSales) / lagged(Assets)

Inputs:
    - 4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - 1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet (Compustat raw data)
    - 1_Inputs/Siccodes48.zip (Fama-French 48 industry classifications)
    - 1_Inputs/Siccodes12.zip (Fama-French 12 industry classifications - fallback)

Outputs:
    - 4_Outputs/3_Financial_V2/3.9_H2_BiddleInvestmentResidual/{timestamp}/H2_InvestmentResiduals.parquet
    - 4_Outputs/3_Financial_V2/3.9_H2_BiddleInvestmentResidual/{timestamp}/stats.json
    - 3_Logs/3_Financial_V2/3.9_H2_BiddleInvestmentResidual/{timestamp}_Biddle.log

Declared Outputs:
    - InvestmentResidual: Dependent variable for H2 regression (residual from first-stage)
    - Investment: Raw investment measure (CapEx + R&D + Acq - AssetSales) / lag(AT)
    - TobinQ_lag: Lagged Tobin's Q (first-stage predictor)
    - SalesGrowth_lag: Lagged sales growth (first-stage predictor)
    - Biddle controls: CashFlow, Size, Leverage, TobinQ, SalesGrowth

Deterministic: true
Dependencies:
    - Requires: Step 3.2_H2Variables
    - Uses: pandas, numpy, statsmodels

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import argparse
import gc
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, cast

import numpy as np
import pandas as pd
import yaml

# Import shared path validation utilities
# Import statsmodels for first-stage OLS
import statsmodels.api as sm

# Import industry utilities
from f1d.shared.industry_utils import parse_ff_industries

# Import observability utilities
from f1d.shared.observability_utils import (
    calculate_throughput,
    compute_file_checksum,
    get_process_memory_mb,
    print_stat,
    save_stats,
)
from f1d.shared.path_utils import (
    ensure_output_dir,
    get_latest_output_dir,
    validate_input_file,
)

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

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
    root = Path(__file__).parent.parent.parent

    # Resolve manifest directory using timestamp-based resolution
    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.4_AssembleManifest",
        required_file="master_sample_manifest.parquet",
    )

    paths = {
        "root": root,
        "manifest_dir": manifest_dir,
        "compustat_file": root
        / "1_Inputs"
        / "comp_na_daily_all"
        / "comp_na_daily_all.parquet",
        "siccodes48_file": root / "1_Inputs" / "Siccodes48.zip",
        "siccodes12_file": root / "1_Inputs" / "Siccodes12.zip",
    }

    # Output directory
    output_base = (
        root / "4_Outputs" / "3_Financial_V2" / "3.9_H2_BiddleInvestmentResidual"
    )
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "3_Financial_V2" / "3.9_H2_BiddleInvestmentResidual"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_Biddle.log"

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


def load_compustat_investment(compustat_file):
    """Load Compustat data with required fields for Biddle investment residual"""
    print("  Loading Compustat data...")

    # Required columns for Biddle (2009) investment construction
    # Note: Compustat uses 'q' suffix for quarterly, 'y' suffix for annual
    required_cols = [
        "gvkey",
        "datadate",
        "fyearq",  # Fiscal Year Quarterly (used as fyear)
        "sic",  # SIC code for industry classification
        # Investment components
        "capxy",  # Capital Expenditures Annual
        "xrdy",  # Research and Development Annual
        "aqcy",  # Acquisitions Annual (optional)
        "sppey",  # Sale of Property, Plant, Equipment Annual (optional)
        # Assets and equity (quarterly)
        "atq",  # Total Assets Quarterly
        "mkvaltq",  # Market Value of Equity Quarterly
        "ceqq",  # Common Equity Quarterly
        # Sales (quarterly)
        "saleq",  # Sales Quarterly
        # Control variables
        "oancfy",  # Operating Cash Flow Annual
        "dlttq",  # Long-Term Debt Quarterly
        "dlcq",  # Debt in Current Liabilities Quarterly
        "cshoq",  # Common Shares Outstanding Quarterly
        "prccq",  # Price Close Quarterly
    ]

    # Check which columns actually exist using PyArrow
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
        if col not in ["gvkey", "datadate", "sic", "fyear"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

    # Add fiscal year field if fyear not available
    if "fyearq" in df.columns:
        df["fyear"] = df["fyearq"].astype("Int64")
    else:
        df["fyear"] = df["datadate"].dt.year

    # Rename columns to simpler names for consistency
    # Map quarterly/annual names to simple names used in construction functions
    column_mapping = {
        "atq": "at",
        "capxy": "capx",
        "xrdy": "xrd",
        "aqcy": "aqc",
        "sppey": "sppe",
        "mkvaltq": "mkvalt",
        "ceqq": "ceq",
        "saleq": "sale",
        "oancfy": "oancf",
        "dlttq": "dltt",
        "dlcq": "dlc",
        "cshoq": "csho",
        "prccq": "prcc",
    }
    df = df.rename(columns=column_mapping)

    return df


def build_ff_mappings(siccodes48_file, siccodes12_file):
    """Build Fama-French industry mappings from SIC codes"""
    print("\nBuilding Fama-French industry mappings...")

    ff48_map = parse_ff_industries(siccodes48_file, 48)
    print(f"  FF48 mapping: {len(ff48_map):,} SIC codes")

    ff12_map = parse_ff_industries(siccodes12_file, 12)
    print(f"  FF12 mapping: {len(ff12_map):,} SIC codes")

    return ff48_map, ff12_map


# ==============================================================================
# Industry Classification
# ==============================================================================


def assign_ff48(df, ff48_map, ff12_map):
    """Assign Fama-French 48 industry classification based on SIC code"""
    print("\nAssigning FF48 industries...")

    # Normalize SIC code
    if "sic" in df.columns:
        df["sic"] = pd.to_numeric(df["sic"], errors="coerce")

    # Assign FF48
    df["ff48_code"] = df["sic"].map(
        lambda x: ff48_map.get(int(x), (48, "Other"))[0] if pd.notna(x) else 48
    )

    # Also assign FF12 for fallback
    df["ff12_code"] = df["sic"].map(
        lambda x: ff12_map.get(int(x), (12, "Other"))[0] if pd.notna(x) else 12
    )

    print(f"  FF48 industries: {df['ff48_code'].nunique()} unique")

    return df


# ==============================================================================
# Variable Construction
# ==============================================================================


def construct_investment(df, winsorize=True):
    """Construct Investment = (CapEx + R&D + Acq - AssetSales) / lagged(AT)

    Per Biddle (2009), investment is total capital expenditure scaled by lagged assets.
    If Acquisitions (AQC) or Asset Sales (SPPE) are missing, uses simplified measure.

    Args:
        df: Compustat dataframe with investment components (renamed from q/y suffixes)
        winsorize: If True, winsorize at 1% and 99% by year

    Returns:
        DataFrame with gvkey, fyear, Investment columns
    """
    print("\nConstructing Investment variable...")

    # Require positive assets
    df_work = df[df["at"] > 0].copy()

    # Sort by gvkey and fyear for lagging
    df_work = df_work.sort_values(["gvkey", "fyear"]).copy()

    # Compute lagged assets
    df_work["at_lag"] = df_work.groupby("gvkey")["at"].shift(1)

    # Build Investment components
    # CapEx + R&D are core components
    investment_components = df_work["capx"].fillna(0) + df_work["xrd"].fillna(0)

    # Add Acquisitions if available
    if "aqc" in df_work.columns:
        investment_components += df_work["aqc"].fillna(0)
        print("  Included Acquisitions (AQC)")
    else:
        print("  Acquisitions (AQC) not available - using simplified measure")

    # Subtract Asset Sales if available
    if "sppe" in df_work.columns:
        investment_components -= df_work["sppe"].fillna(0)
        print("  Included Asset Sales (SPPE)")
    else:
        print("  Asset Sales (SPPE) not available - using simplified measure")

    # Compute Investment
    df_work["Investment"] = investment_components / df_work["at_lag"]

    # Winsorize at 1% and 99% by year
    if winsorize:
        df_work["Investment"] = df_work.groupby("fyear")["Investment"].transform(
            lambda x: x.clip(lower=x.quantile(0.01), upper=x.quantile(0.99))
        )
        print("  Winsorized Investment at 1%/99% by year")

    result = df_work[["gvkey", "fyear", "Investment"]].copy()
    n_computed = result["Investment"].notna().sum()
    print(f"  Computed Investment for {n_computed:,} observations")

    return result


def construct_tobins_q(df, winsorize=True):
    """Construct Tobin's Q = (AT + MKVALT - CEQ) / AT

    Args:
        df: Compustat dataframe
        winsorize: If True, winsorize at 1% and 99% by year

    Returns:
        DataFrame with gvkey, fyear, TobinQ, TobinQ_lag columns
    """
    print("\nConstructing Tobin's Q...")

    # Check required fields
    if (
        "mkvalt" not in df.columns
        or "csho" not in df.columns
        or "prcc" not in df.columns
    ):
        print("  Warning: Market value fields not all available")
        # Try to construct market equity from csho * prcc
        if "csho" in df.columns and "prcc" in df.columns:
            df["mkvalt"] = df["csho"] * df["prcc"]
            print("  Constructed MKVALT from CSHO * PRCC")
        else:
            print("  Cannot construct Tobin's Q - returning empty")
            return pd.DataFrame(columns=["gvkey", "fyear", "TobinQ", "TobinQ_lag"])

    # Require positive AT
    df_work = df[df["at"] > 0].copy()

    # Compute Tobin's Q
    df_work["TobinQ"] = (
        df_work["at"] + df_work["mkvalt"].fillna(0) - df_work["ceq"].fillna(0)
    ) / df_work["at"]

    # Sort for lagging
    df_work = df_work.sort_values(["gvkey", "fyear"]).copy()

    # Create lagged version
    df_work["TobinQ_lag"] = df_work.groupby("gvkey")["TobinQ"].shift(1)

    # Winsorize at 1% and 99% by year
    if winsorize:
        df_work["TobinQ_lag"] = df_work.groupby("fyear")["TobinQ_lag"].transform(
            lambda x: x.clip(lower=x.quantile(0.01), upper=x.quantile(0.99))
            if x.notna().sum() > 0
            else x
        )
        print("  Winsorized TobinQ_lag at 1%/99% by year")

    result = df_work[["gvkey", "fyear", "TobinQ", "TobinQ_lag"]].copy()
    n_computed = result["TobinQ_lag"].notna().sum()
    print(f"  Computed TobinQ_lag for {n_computed:,} observations")

    return result


def construct_sales_growth(df, winsorize=True):
    """Construct Sales Growth = (SALE_t - SALE_t-1) / |SALE_t-1|

    Args:
        df: Compustat dataframe
        winsorize: If True, winsorize at 1% and 99% by year

    Returns:
        DataFrame with gvkey, fyear, SalesGrowth, SalesGrowth_lag columns
    """
    print("\nConstructing Sales Growth...")

    if "sale" not in df.columns:
        print("  Warning: SALE not available")
        return pd.DataFrame(
            columns=["gvkey", "fyear", "SalesGrowth", "SalesGrowth_lag"]
        )

    # Sort by gvkey and fyear
    df_work = df.sort_values(["gvkey", "fyear"]).copy()

    # Compute lagged sales
    df_work["sale_lag"] = df_work.groupby("gvkey")["sale"].shift(1)

    # Compute sales growth
    df_work["SalesGrowth"] = (df_work["sale"] - df_work["sale_lag"]) / df_work[
        "sale_lag"
    ].abs()

    # Create lagged version (for first-stage predictors)
    df_work["SalesGrowth_lag"] = df_work.groupby("gvkey")["SalesGrowth"].shift(1)

    # Winsorize at 1% and 99% by year
    if winsorize:
        df_work["SalesGrowth_lag"] = df_work.groupby("fyear")[
            "SalesGrowth_lag"
        ].transform(
            lambda x: x.clip(lower=x.quantile(0.01), upper=x.quantile(0.99))
            if x.notna().sum() > 0
            else x
        )
        print("  Winsorized SalesGrowth_lag at 1%/99% by year")

    result = df_work[["gvkey", "fyear", "SalesGrowth", "SalesGrowth_lag"]].copy()
    n_computed = result["SalesGrowth_lag"].notna().sum()
    print(f"  Computed SalesGrowth_lag for {n_computed:,} observations")

    return result


def construct_biddle_controls(df, winsorize=True):
    """Construct Biddle (2009) control variables

    - CashFlow = OANCF / AT
    - Size = log(AT)
    - Leverage = (DLTT + DLC) / (DLTT + DLC + MKVALT)

    Args:
        df: Compustat dataframe
        winsorize: If True, winsorize all controls at 1%/99% by year

    Returns:
        DataFrame with gvkey, fyear, CashFlow, Size, Leverage columns
    """
    print("\nConstructing Biddle controls...")

    # Require positive assets
    df_work = df[df["at"] > 0].copy()

    # Cash Flow: OANCF / AT
    if "oancf" in df_work.columns:
        df_work["CashFlow"] = df_work["oancf"] / df_work["at"]
        print("  Computed CashFlow (OANCF/AT)")
    else:
        df_work["CashFlow"] = np.nan
        print("  Warning: OANCF not available - CashFlow set to NaN")

    # Firm Size: log(AT)
    df_work["Size"] = np.log(df_work["at"])
    print("  Computed Size (log AT)")

    # Market Leverage: (DLTT + DLC) / (DLTT + DLC + MKVALT)
    if "dltt" in df_work.columns and "dlc" in df_work.columns:
        debt = df_work["dltt"].fillna(0) + df_work["dlc"].fillna(0)
        if "mkvalt" in df_work.columns:
            market_value = debt + df_work["mkvalt"].fillna(0)
            df_work["Leverage"] = debt / market_value
            print("  Computed Leverage (market leverage)")
        else:
            df_work["Leverage"] = np.nan
            print("  Warning: MKVALT not available - Leverage set to NaN")
    else:
        df_work["Leverage"] = np.nan
        print("  Warning: DLTT/DLC not available - Leverage set to NaN")

    # Winsorize controls at 1% and 99% by year
    if winsorize:
        for var in ["CashFlow", "Size", "Leverage"]:
            df_work[var] = df_work.groupby("fyear")[var].transform(
                lambda x: x.clip(lower=x.quantile(0.01), upper=x.quantile(0.99))
                if x.notna().sum() > 0
                else x
            )
        print("  Winsorized controls at 1%/99% by year")

    result = df_work[["gvkey", "fyear", "CashFlow", "Size", "Leverage"]].copy()
    return result


# ==============================================================================
# First-Stage Regressions (Biddle 2009)
# ==============================================================================


def run_first_stage_regressions(df, min_obs=20, ff_industry="ff48_code"):
    """Run Biddle (2009) first-stage regressions by industry-year

    Specification:
        Investment = beta0 + beta1*TobinQ_lag + beta2*SalesGrowth_lag + epsilon

    The residual epsilon is the InvestmentResidual (investment inefficiency measure).

    Args:
        df: DataFrame with Investment, TobinQ_lag, SalesGrowth_lag, ff48_code, fyear
        min_obs: Minimum observations per industry-year cell
        ff_industry: Column name for industry classification

    Returns:
        DataFrame with gvkey, fyear, InvestmentResidual, first_stage_* columns
    """
    print(f"\nRunning first-stage regressions by {ff_industry}-year...")

    # Prepare data for regression
    reg_data = df.dropna(
        subset=["Investment", "TobinQ_lag", "SalesGrowth_lag", ff_industry, "fyear"]
    ).copy()

    if len(reg_data) == 0:
        print("  Error: No valid data for first-stage regression")
        return pd.DataFrame()

    print(f"  Valid observations for regression: {len(reg_data):,}")

    # Track regression results
    residual_list = []
    thin_cells = []

    # Group by industry-year
    grouped = reg_data.groupby([ff_industry, "fyear"])

    n_cells = 0
    n_regressions = 0
    total_cells = len(grouped)

    # Pre-allocate list for efficiency
    results_buffer = []
    buffer_size = 1000

    for i, ((industry, year), group) in enumerate(grouped):
        n_cells += 1

        # Progress indicator every 50 cells
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{total_cells} cells processed...")

        # Check minimum observations
        if len(group) < min_obs:
            thin_cells.append((industry, year, len(group)))
            continue

        # Prepare regression data
        Y = group["Investment"].values
        X = group[["TobinQ_lag", "SalesGrowth_lag"]].values
        X = sm.add_constant(X)

        # Run OLS
        try:
            model = sm.OLS(Y, X).fit()
            predicted = model.predict(X)
            residuals = Y - predicted

            n_regressions += 1

            # Store residuals more efficiently - avoid intermediate dict
            indices = group.index.values
            for j, (idx, res, pred) in enumerate(zip(indices, residuals, predicted)):
                results_buffer.append(
                    {
                        "index": int(idx),
                        "gvkey": group["gvkey"].iloc[j],
                        "fyear": int(group["fyear"].iloc[j]),
                        "ff48_code": int(industry),
                        "InvestmentResidual": float(res),
                        "Investment": float(group["Investment"].iloc[j]),
                        "TobinQ_lag": float(group["TobinQ_lag"].iloc[j]),
                        "SalesGrowth_lag": float(group["SalesGrowth_lag"].iloc[j]),
                        "predicted_investment": float(pred),
                        "first_stage_r2": float(model.rsquared),
                        "first_stage_n": int(len(group)),
                    }
                )

                # Flush buffer periodically
                if len(results_buffer) >= buffer_size:
                    residual_list.extend(results_buffer)
                    results_buffer = []

        except Exception as e:
            print(
                f"  Warning: Regression failed for {ff_industry}={industry}, year={year}: {e}"
            )
            continue

    # Flush remaining buffer
    if results_buffer:
        residual_list.extend(results_buffer)

    if not residual_list:
        print("  Error: No residuals computed")
        return pd.DataFrame()

    # Build result DataFrame
    result = pd.DataFrame(residual_list)

    print("\nFirst-stage regression summary:")
    print(f"  Total cells: {n_cells}")
    print(f"  Regressions run: {n_regressions}")
    print(f"  Thin cells (<{min_obs} obs): {len(thin_cells)}")

    if thin_cells:
        print(f"  Sample thin cells: {thin_cells[:5]}")

    # Residual statistics
    print("\nInvestmentResidual statistics:")
    print(f"  Mean: {result['InvestmentResidual'].mean():.6f} (should be ~0)")
    print(f"  Std: {result['InvestmentResidual'].std():.6f}")
    print(f"  Min: {result['InvestmentResidual'].min():.6f}")
    print(f"  Max: {result['InvestmentResidual'].max():.6f}")
    print(
        f"  Overinvestment (>0): {(result['InvestmentResidual'] > 0).sum():,} ({(result['InvestmentResidual'] > 0).sum() / len(result) * 100:.1f}%)"
    )
    print(
        f"  Underinvestment (<0): {(result['InvestmentResidual'] < 0).sum():,} ({(result['InvestmentResidual'] < 0).sum() / len(result) * 100:.1f}%)"
    )

    return result


def validate_residuals(residuals_df):
    """Validate investment residuals for correctness

    Args:
        residuals_df: DataFrame with InvestmentResidual column

    Returns:
        Dictionary with validation statistics
    """
    print("\nValidating investment residuals...")

    validation = {
        "mean": float(residuals_df["InvestmentResidual"].mean()),
        "std": float(residuals_df["InvestmentResidual"].std()),
        "min": float(residuals_df["InvestmentResidual"].min()),
        "max": float(residuals_df["InvestmentResidual"].max()),
        "n": len(residuals_df),
        "pct_overinvest": float(
            (residuals_df["InvestmentResidual"] > 0).sum() / len(residuals_df) * 100
        ),
        "pct_underinvest": float(
            (residuals_df["InvestmentResidual"] < 0).sum() / len(residuals_df) * 100
        ),
    }

    # Check mean ~ 0 (OLS property)
    if abs(validation["mean"]) < 0.01:
        print("  [OK] Residual mean ~ 0 (OLS property satisfied)")
    else:
        print(f"  [WARNING] Residual mean = {validation['mean']:.6f} (expected ~ 0)")

    # First-stage R2 statistics
    if "first_stage_r2" in residuals_df.columns:
        r2_stats = residuals_df.groupby("ff48_code")["first_stage_r2"].mean()
        print(f"\nFirst-stage R2 by industry (mean): {r2_stats.mean():.4f}")

    return validation


# ==============================================================================
# CLI and Prerequisites
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments for 3.9_H2_BiddleInvestmentResidual.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 3.9: H2 Biddle (2009) Investment Residual

Constructs the correct Biddle (2009) investment residual as the dependent
variable for H2 regression (PRisk x Uncertainty -> Investment Efficiency).

Per Biddle (2009), runs first-stage regressions by FF48-year:
    Investment = beta0 + beta1*TobinQ_lag + beta2*SalesGrowth_lag + epsilon

The residual (InvestmentResidual) measures deviation from expected investment
given growth opportunities (positive = overinvestment, negative = underinvestment).
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
        "SIC Codes 48": paths["siccodes48_file"],
        "SIC Codes 12": paths["siccodes12_file"],
    }

    all_ok = True
    for name, path in required_files.items():
        if path.exists():
            print(f"  [OK] {name}: {path}")
        else:
            print(f"  [MISSING] {name}: {path}")
            all_ok = False

    return all_ok


# ==============================================================================
# Main
# ==============================================================================


def main():
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
        print("STEP 3.9: H2 Biddle Investment Residual - DRY RUN")
        print(f"Timestamp: {timestamp}")
        print("=" * 60)

        prereq_ok = check_prerequisites(paths, args)
        if prereq_ok:
            print("\n[OK] All prerequisites validated")
            print("\nWould compute:")
            print("  - Investment = (CapEx + R&D + Acq - AssetSales) / lag(AT)")
            print("  - Tobin's Q (lagged)")
            print("  - Sales Growth (lagged)")
            print("  - Biddle controls (CashFlow, Size, Leverage)")
            print("  - First-stage regression by FF48-year:")
            print("      Investment ~ TobinQ_lag + SalesGrowth_lag")
            print("  - InvestmentResidual (epsilon from first-stage)")
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

    # Setup logging with dual-writer
    log_file = open(paths["log_file"], "w", buffering=1)

    import builtins

    builtin_print = builtins.print

    def print_both(*args, **kwargs):
        builtin_print(*args, **kwargs)
        kwargs.pop("flush", None)
        builtin_print(*args, file=log_file, flush=True, **kwargs)

    builtins.print = print_both

    print("=" * 60)
    print("STEP 3.9: H2 Biddle (2009) Investment Residual")
    print(f"Timestamp: {timestamp}")
    print("=" * 60)

    # Initialize statistics
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    mem_start = get_process_memory_mb()
    memory_readings = [mem_start["rss_mb"]]

    stats: Dict[str, Any] = {
        "step_id": "3.9_H2_BiddleInvestmentResidual",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0},
        "processing": {},
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

    # Load Compustat
    print("\nCompustat:")
    stats["input"]["files"].append(str(paths["compustat_file"]))
    stats["input"]["checksums"][paths["compustat_file"].name] = compute_file_checksum(
        paths["compustat_file"]
    )
    compustat = load_compustat_investment(paths["compustat_file"])
    print_stat("Compustat rows", value=len(compustat))

    # Build FF industry mappings
    print("\nIndustry Classifications:")
    ff48_map, ff12_map = build_ff_mappings(
        paths["siccodes48_file"], paths["siccodes12_file"]
    )

    # Assign FF48 industries to Compustat
    compustat = assign_ff48(compustat, ff48_map, ff12_map)

    # ========================================================================
    # Filter to Sample Firms FIRST (critical optimization)
    # ========================================================================

    print("\n" + "=" * 60)
    print("Filtering Compustat to Sample Firms")
    print("=" * 60)

    # Get unique gvkeys from manifest
    sample_gvkeys = set(manifest["gvkey"].unique())
    print(f"  Sample firms: {len(sample_gvkeys):,}")

    # Filter Compustat to sample firms
    compustat = compustat[compustat["gvkey"].isin(sample_gvkeys)].copy()
    print(f"  Compustat after sample filter: {len(compustat):,} observations")

    # CRITICAL: Compustat contains quarterly data but we need annual observations
    # For Biddle (2009), we need one observation per firm-year
    # Use the last (quarterly) observation for each gvkey-fyear as the annual value
    # This is standard practice when working with quarterly Compustat data
    print("\n" + "-" * 60)
    print("Aggregating to annual observations")
    print("-" * 60)

    # Count observations before deduplication
    obs_before = len(compustat)
    print(f"  Observations before deduplication: {obs_before:,}")

    # Sort by gvkey, fyear, datadate to get the last observation
    compustat = compustat.sort_values(["gvkey", "fyear", "datadate"])

    # Keep only the last observation per gvkey-fyear (most recent quarter)
    # This gives us annual values (typically Q4 or the most recent reported quarter)
    compustat = compustat.drop_duplicates(subset=["gvkey", "fyear"], keep="last")

    obs_after = len(compustat)
    print(f"  Observations after deduplication: {obs_after:,}")
    print(f"  Duplicates removed: {obs_before - obs_after:,}")

    # ========================================================================
    # Construct Variables
    # ========================================================================

    print("\n" + "=" * 60)
    print("Constructing Biddle (2009) Variables")
    print("=" * 60)

    # Construct Investment
    print("\n" + "-" * 60)
    print("Investment Variable")
    print("-" * 60)
    investment_df = construct_investment(compustat, winsorize=True)

    # Construct Tobin's Q
    print("\n" + "-" * 60)
    print("Tobin's Q")
    print("-" * 60)
    tobins_q_df = construct_tobins_q(compustat, winsorize=True)

    # Construct Sales Growth
    print("\n" + "-" * 60)
    print("Sales Growth")
    print("-" * 60)
    sales_growth_df = construct_sales_growth(compustat, winsorize=True)

    # Construct Biddle controls
    print("\n" + "-" * 60)
    print("Biddle Controls")
    print("-" * 60)
    controls_df = construct_biddle_controls(compustat, winsorize=True)

    # ========================================================================
    # Merge Variables for First-Stage
    # ========================================================================

    print("\n" + "=" * 60)
    print("Merging Variables for First-Stage Regression")
    print("=" * 60)

    # Start with investment and merge all predictors - use reduce() for efficiency
    from functools import reduce

    # Add ff48_code to investment_df first
    investment_with_ff = investment_df.merge(
        compustat[["gvkey", "fyear", "ff48_code"]].drop_duplicates(),
        on=["gvkey", "fyear"],
        how="left",
    )

    # Merge all dataframes at once
    dfs_to_merge = [
        investment_with_ff,
        tobins_q_df[["gvkey", "fyear", "TobinQ_lag"]],
        sales_growth_df[["gvkey", "fyear", "SalesGrowth_lag"]],
    ]

    first_stage_data = reduce(
        lambda left, right: pd.merge(left, right, on=["gvkey", "fyear"], how="inner"),
        dfs_to_merge,
    )

    print(f"  First-stage data: {len(first_stage_data):,} observations")

    # ========================================================================
    # Run First-Stage Regressions
    # ========================================================================

    print("\n" + "=" * 60)
    print("Running First-Stage Regressions")
    print("=" * 60)

    residuals_df = run_first_stage_regressions(
        first_stage_data, min_obs=20, ff_industry="ff48_code"
    )

    if residuals_df.empty:
        print("\n[ERROR] No residuals computed. Exiting.")
        sys.exit(1)

    # Validate residuals
    validation = validate_residuals(residuals_df)
    stats["processing"]["residual_validation"] = validation

    # Save intermediate residuals to disk first
    residuals_file = paths["output_dir"] / "_residuals_intermediate.parquet"
    residuals_df.to_parquet(residuals_file, index=False)
    print(f"  Saved intermediate residuals: {residuals_file.name}")

    # Clean up large intermediate dataframes to free memory
    print("\nCleaning up memory...")
    del first_stage_data
    del residuals_df
    gc.collect()
    mem_after_cleanup = get_process_memory_mb()
    print(f"  Memory after cleanup: {mem_after_cleanup['rss_mb']:.1f} MB")

    # ========================================================================
    # Merge with Controls
    # ========================================================================

    print("\n" + "=" * 60)
    print("Merging with Controls")
    print("=" * 60)

    # Reload residuals from disk (already has Investment, TobinQ_lag, SalesGrowth_lag)
    final_output = pd.read_parquet(residuals_file)
    print(f"  Reloaded residuals: {len(final_output):,} observations")

    # Deduplicate controls to avoid memory bloat during merge
    controls_unique = controls_df.drop_duplicates(subset=["gvkey", "fyear"])
    print(f"  Controls deduplicated: {len(controls_df):,} -> {len(controls_unique):,}")

    # Merge controls one at a time to reduce memory pressure
    print("  Merging CashFlow...")
    final_output = final_output.merge(
        controls_unique[["gvkey", "fyear", "CashFlow"]],
        on=["gvkey", "fyear"],
        how="left",
    )
    gc.collect()

    print("  Merging Size...")
    final_output = final_output.merge(
        controls_unique[["gvkey", "fyear", "Size"]],
        on=["gvkey", "fyear"],
        how="left",
    )
    gc.collect()

    print("  Merging Leverage...")
    final_output = final_output.merge(
        controls_unique[["gvkey", "fyear", "Leverage"]],
        on=["gvkey", "fyear"],
        how="left",
    )
    gc.collect()

    # Deduplicate and merge TobinQ (non-lagged)
    tobins_q_unique = tobins_q_df.drop_duplicates(subset=["gvkey", "fyear"])
    print("  Merging TobinQ (non-lagged)...")
    final_output = final_output.merge(
        tobins_q_unique[["gvkey", "fyear", "TobinQ"]],
        on=["gvkey", "fyear"],
        how="left",
    )
    gc.collect()

    # Deduplicate and merge SalesGrowth (non-lagged)
    sales_growth_unique = sales_growth_df.drop_duplicates(subset=["gvkey", "fyear"])
    print("  Merging SalesGrowth (non-lagged)...")
    final_output = final_output.merge(
        sales_growth_unique[["gvkey", "fyear", "SalesGrowth"]],
        on=["gvkey", "fyear"],
        how="left",
    )
    gc.collect()

    # Clean up intermediate file
    residuals_file.unlink()
    print("  Cleaned up intermediate file")

    print(f"  Final output: {len(final_output):,} observations")

    # ========================================================================
    # Write Outputs
    # ========================================================================

    print("\n" + "=" * 60)
    print("Writing Outputs")
    print("=" * 60)

    # Select output columns
    output_columns = [
        "gvkey",
        "fyear",
        "ff48_code",
        "InvestmentResidual",
        "Investment",
        "TobinQ_lag",
        "SalesGrowth_lag",
        "TobinQ",
        "SalesGrowth",
        "CashFlow",
        "Size",
        "Leverage",
        "predicted_investment",
        "first_stage_r2",
    ]

    # Ensure columns exist
    output_columns = [c for c in output_columns if c in final_output.columns]

    final_for_output = (
        final_output.loc[:, output_columns]
        .sort_values(["gvkey", "fyear"])
        .reset_index(drop=True)
    )

    # Write parquet
    output_file = paths["output_dir"] / "H2_InvestmentResiduals.parquet"
    final_for_output.to_parquet(output_file, index=False)
    print(f"  Wrote: {output_file.name}")
    stats["output"]["files"].append(output_file.name)
    stats["output"]["checksums"][output_file.name] = compute_file_checksum(output_file)
    stats["output"]["final_rows"] = len(final_for_output)

    # Write stats.json
    stats["variables"] = {
        "InvestmentResidual": {
            "mean": float(final_for_output["InvestmentResidual"].mean()),
            "std": float(final_for_output["InvestmentResidual"].std()),
            "min": float(final_for_output["InvestmentResidual"].min()),
            "max": float(final_for_output["InvestmentResidual"].max()),
            "n": int(final_for_output["InvestmentResidual"].notna().sum()),
        },
        "first_stage_summary": {
            "mean_r2": float(final_for_output["first_stage_r2"].mean())
            if "first_stage_r2" in final_for_output.columns
            else None,
            "median_r2": float(final_for_output["first_stage_r2"].median())
            if "first_stage_r2" in final_for_output.columns
            else None,
            "n_industries": int(final_for_output["ff48_code"].nunique())
            if "ff48_code" in final_for_output.columns
            else None,
        },
    }

    save_stats(stats, paths["output_dir"])

    # Update latest/ symlink
    output_base = paths["output_dir"].parent
    latest_link = output_base / "latest"
    if latest_link.exists():
        latest_link.unlink()
    try:
        latest_link.symlink_to(paths["output_dir"])
        print("  Updated latest/ symlink")
    except OSError:
        # Symlink creation may fail on Windows - use junction instead
        import subprocess

        subprocess.run(
            ["mklink", "/J", str(latest_link), str(paths["output_dir"])], shell=True
        )

    # ========================================================================
    # Final Summary
    # ========================================================================

    end_time = time.perf_counter()
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(end_time - start_time, 2)

    mem_end = get_process_memory_mb()
    memory_readings.append(mem_end["rss_mb"])
    stats["memory"]["end_mb"] = mem_end["rss_mb"]
    stats["memory"]["peak_mb"] = round(max(memory_readings), 2)
    stats["memory"]["delta_mb"] = round(mem_end["rss_mb"] - mem_start["rss_mb"], 2)

    duration_seconds = end_time - start_time
    if duration_seconds > 0:
        throughput = calculate_throughput(len(final_for_output), duration_seconds)
        stats["throughput"] = {
            "rows_per_second": throughput,
            "total_rows": len(final_for_output),
            "duration_seconds": round(duration_seconds, 3),
        }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Investment residuals computed: {len(final_for_output):,} observations")
    print(
        f"  InvestmentResidual mean: {stats['variables']['InvestmentResidual']['mean']:.6f}"
    )
    print(
        f"  First-stage mean R2: {stats['variables']['first_stage_summary']['mean_r2']:.4f}"
    )
    print(f"\nOutputs saved to: {paths['output_dir']}")
    print(f"Log saved to: {paths['log_file']}")

    log_file.close()


if __name__ == "__main__":
    main()
