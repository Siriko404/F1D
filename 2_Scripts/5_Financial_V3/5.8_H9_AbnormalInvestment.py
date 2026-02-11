#!/usr/bin/env python3
"""
================================================================================
STEP 5.8: H9 Abnormal Investment (Biddle 2009)
================================================================================
ID: 5.8_H9_AbnormalInvestment
Description: Constructs Biddle-style abnormal investment (AbsAbInv) and control
             variables for H9 regression.

Purpose: Implement Biddle et al. (2009) investment efficiency measure as the
dependent variable for H9 regression, along with all required control variables.

Specification:
    TotalInv_{t+1} = (capx_{t+1} + xrd_{t+1} + aqc_{t+1} - sppe_{t+1}) / at_t
    Expected Inv: TotalInv_{i,t+1} = a_{ind2,t} + b_{ind2,t} * SalesGrowth_{i,t} + e
    AbsAbInv_{t+1} = |e| (absolute residual from first-stage)

Inputs:
    - 1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet (Compustat annual data)

Outputs:
    - 4_Outputs/5.8_H9_AbnormalInvestment/{timestamp}/abnormal_investment.parquet
    - 4_Outputs/5.8_H9_AbnormalInvestment/{timestamp}/report_step58_03.md
    - 4_Outputs/5.8_H9_AbnormalInvestment/{timestamp}/stats.json
    - 4_Outputs/5.8_H9_AbnormalInvestment/{timestamp}/first_stage_diagnostics.csv

Declared Outputs:
    - AbsAbInv: Absolute abnormal investment (dependent variable for H9)
    - TotalInv: Raw investment measure
    - Controls: ln_at_t, lev_t, cash_t, roa_t, mb_t, SalesGrowth_t

Deterministic: true
Dependencies:
    - Requires: Step 4.x
    - Uses: pandas, numpy, statsmodels

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import argparse
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# Add parent directory to sys.path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Import shared path validation utilities
# Import statsmodels for first-stage OLS
import statsmodels.api as sm

# Import observability utilities
from shared.observability_utils import (
    calculate_throughput,
    compute_file_checksum,
    get_process_memory_mb,
    print_stat,
    save_stats,
)
from shared.path_utils import (
    ensure_output_dir,
)

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# ==============================================================================
# Configuration
# ==============================================================================


def setup_paths(timestamp):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    paths = {
        "root": root,
        "compustat_file": root
        / "1_Inputs"
        / "comp_na_daily_all"
        / "comp_na_daily_all.parquet",
    }

    # Output directory
    output_base = root / "4_Outputs" / "5.8_H9_AbnormalInvestment"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "5_Financial_V3" / "5.8_H9_AbnormalInvestment"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H9AbInv.log"

    return paths


# ==============================================================================
# Data Loading
# ==============================================================================


def load_compustat(compustat_file, fyear_min=2002, fyear_max=2018):
    """Load Compustat data with required fields for Biddle abnormal investment

    Args:
        compustat_file: Path to Compustat parquet file
        fyear_min: Minimum fiscal year (default 2002)
        fyear_max: Maximum fiscal year (default 2018)

    Returns:
        DataFrame with Compustat data
    """
    print(f"  Loading Compustat data (fyear {fyear_min}-{fyear_max})...")

    # Check which columns exist using PyArrow
    import pyarrow.parquet as pq

    pf = pq.ParquetFile(compustat_file)
    available_cols = set(pf.schema_arrow.names)

    # Required columns for investment construction
    # Compustat data uses quarterly (q suffix) and annual (y suffix) columns
    # We'll use annual (y) columns for investment variables
    required_cols = [
        "gvkey",
        "datadate",
        "fyearq",  # Fiscal year (quarterly data field)
        "sic",
        # Investment components (annual)
        "capxy",  # Capital Expenditures Annual (REQUIRED)
        "xrdy",  # Research and Development Annual (optional)
        "aqcy",  # Acquisitions Annual (optional)
        "sppey",  # Sale of Property, Plant, Equipment Annual (optional)
        # Assets and sales (use quarterly for at, annual for sale)
        "atq",  # Total Assets Quarterly
        "saleq",  # Sales Quarterly
        "saley",  # Sales Annual (backup)
        # Control variables
        "oibdpq",  # Operating Income Before Depreciation Quarterly (preferred for ROA)
        "niq",  # Net Income Quarterly (fallback for ROA)
        "niy",  # Net Income Annual (backup)
        "dlttq",  # Long-Term Debt Quarterly
        "dlcq",  # Debt in Current Liabilities Quarterly
        "cheq",  # Cash and Equivalents Quarterly
        "prccq",  # Price Close Quarterly
        "cshoq",  # Common Shares Outstanding Quarterly
        "mkvaltq",  # Market Value of Equity Quarterly
    ]

    # Filter to only columns that exist
    cols_to_read = [c for c in required_cols if c in available_cols]

    if len(cols_to_read) < len(required_cols):
        missing = set(required_cols) - set(cols_to_read)
        print(f"  Warning: Missing columns will be unavailable: {missing}")

    # Verify critical columns exist
    critical_cols = ["gvkey", "datadate", "fyearq", "sic", "capxy", "atq", "saleq"]
    for col in critical_cols:
        if col not in available_cols:
            raise ValueError(f"Critical column missing: {col}")

    # Use PyArrow to filter on fyear before reading into pandas (memory efficient)
    # Read with filters to only get rows in our fyear range
    filters = [("fyearq", ">=", fyear_min), ("fyearq", "<=", fyear_max)]

    # Read the dataset
    table = pq.read_table(compustat_file, columns=cols_to_read, filters=filters)

    # Convert to pandas
    df = table.to_pandas()

    print(
        f"  Loaded Compustat: {len(df):,} observations (fyear {fyear_min}-{fyear_max})"
    )

    # Normalize gvkey
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["datadate"] = pd.to_datetime(df["datadate"])

    # Convert fyearq to fyear as regular int
    df["fyear"] = pd.to_numeric(df["fyearq"], errors="coerce")
    df = df[df["fyear"].notna()].copy()
    df["fyear"] = df["fyear"].astype("int64")

    # Rename columns to simpler names used in construction functions
    # Map quarterly/annual names to simple names
    column_mapping = {
        "atq": "at",
        "capxy": "capx",
        "xrdy": "xrd",
        "aqcy": "aqc",
        "sppey": "sppe",
        "saleq": "sale",
        "saley": "sale_y",  # backup annual sales
        "oibdpq": "oibdp",
        "niq": "ni",
        "niy": "ni_y",  # backup annual NI
        "dlttq": "dltt",
        "dlcq": "dlc",
        "cheq": "che",
        "prccq": "prcc_f",
        "cshoq": "csho",
        "mkvaltq": "mkvalt",
    }
    df = df.rename(columns=column_mapping)

    # If sale is all missing, try sale_y
    if "sale" in df.columns and df["sale"].isna().all() and "sale_y" in df.columns:
        df["sale"] = df["sale_y"]
        print("  Using annual sales (saley) as saleq is missing")

    # Convert numeric columns
    numeric_cols = [
        "sic",
        "capx",
        "xrd",
        "aqc",
        "sppe",
        "at",
        "sale",
        "oibdp",
        "ni",
        "dltt",
        "dlc",
        "che",
        "prcc_f",
        "csho",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

    # Deduplicate to get annual observations (keep last quarterly observation per gvkey-fyear)
    # This is standard practice when working with quarterly Compustat data
    obs_before = len(df)
    df = df.sort_values(["gvkey", "fyear", "datadate"])
    df = df.drop_duplicates(subset=["gvkey", "fyear"], keep="last")
    obs_after = len(df)
    print(f"  Deduplicated to annual observations: {obs_before:,} -> {obs_after:,}")

    return df


# ==============================================================================
# Industry Classification
# ==============================================================================


def assign_industry(df):
    """Assign SIC-based industry classifications and exclude utilities/financials

    Args:
        df: DataFrame with sic column

    Returns:
        DataFrame with ind1, ind2 columns and utilities/financials excluded
    """
    print("\nAssigning industry classifications...")

    # Drop missing SIC
    n_before = len(df)
    df = df[df["sic"].notna()].copy()
    print(f"  Dropped missing SIC: {n_before - len(df):,} observations")

    # Valid SIC range
    df = df[(df["sic"] >= 100) & (df["sic"] <= 9999)].copy()
    print(f"  Dropped invalid SIC: {n_before - len(df):,} observations")

    # Create ind2 = floor(sic / 100)
    df["ind2"] = (df["sic"] / 100).astype(int)

    # Create ind1 = floor(sic / 1000) for fallback
    df["ind1"] = (df["sic"] / 1000).astype(int)

    # Exclude utilities (4900-4999)
    n_utils = ((df["sic"] >= 4900) & (df["sic"] <= 4999)).sum()
    df = df[~((df["sic"] >= 4900) & (df["sic"] <= 4999))].copy()
    print(f"  Dropped utilities (4900-4999): {n_utils:,} observations")

    # Exclude financials (6000-6999)
    n_fin = ((df["sic"] >= 6000) & (df["sic"] <= 6999)).sum()
    df = df[~((df["sic"] >= 6000) & (df["sic"] <= 6999))].copy()
    print(f"  Dropped financials (6000-6999): {n_fin:,} observations")

    print(f"  Industries (ind2): {df['ind2'].nunique()} unique")
    print(f"  Industries (ind1): {df['ind1'].nunique()} unique")

    return df


# ==============================================================================
# Panel Creation with Leads/Lags
# ==============================================================================


def create_panel_with_leads_lags(df):
    """Create panel with leads and lags for investment construction

    Creates:
    - at_t: Assets at time t (for scaling)
    - sale_t: Sales at time t
    - sale_tm1: Lagged sales (t-1) for sales growth
    - capx_tp1: Lead CAPEX (t+1)
    - xrd_tp1: Lead R&D (t+1)
    - aqc_tp1: Lead acquisitions (t+1)
    - sppe_tp1: Lead asset sales (t+1)

    Args:
        df: Compustat dataframe sorted by gvkey, fyear

    Returns:
        DataFrame with lead/lag variables
    """
    print("\nCreating panel with leads and lags...")

    # Sort by gvkey and fyear
    df = df.sort_values(["gvkey", "fyear"]).copy()

    # Current year variables
    df["at_t"] = df["at"]
    df["sale_t"] = df["sale"]

    # Lagged sales (t-1)
    df["sale_tm1"] = df.groupby("gvkey")["sale"].shift(1)

    # Lead variables (t+1)
    df["capx_tp1"] = df.groupby("gvkey")["capx"].shift(-1)
    df["xrd_tp1"] = df.groupby("gvkey")["xrd"].shift(-1)
    df["aqc_tp1"] = df.groupby("gvkey")["aqc"].shift(-1)
    df["sppe_tp1"] = df.groupby("gvkey")["sppe"].shift(-1)

    print(f"  Panel created: {len(df):,} observations")

    return df


# ==============================================================================
# Investment Construction
# ==============================================================================


def construct_investment(df):
    """Construct TotalInv at t+1 with Biddle (2009) missingness rules

    NON-NEGOTIABLE RULES:
    - DROP if at_t is missing OR at_t <= 0
    - DROP if capx_tp1 is missing (CAPEX required)
    - Set xrd_tp1 = 0 if missing (R&D optional)
    - Set aqc_tp1 = 0 if missing (acquisitions optional)
    - Set sppe_tp1 = 0 if missing (asset sales optional)

    Args:
        df: DataFrame with at_t, capx_tp1, xrd_tp1, aqc_tp1, sppe_tp1

    Returns:
        DataFrame with TotalInv column and filters applied
    """
    print("\nConstructing TotalInv_{t+1}...")

    n_start = len(df)

    # Rule 1: Require at_t > 0
    df = df[df["at_t"].notna() & (df["at_t"] > 0)].copy()
    n_at = len(df)
    print(f"  Require at_t > 0: {n_start - n_at:,} dropped")

    # Rule 2: Require capx_tp1 non-missing (CAPX is REQUIRED)
    df = df[df["capx_tp1"].notna()].copy()
    n_capx = len(df)
    print(f"  Require capx_tp1 non-missing: {n_at - n_capx:,} dropped")

    # Rule 3: Set optional components to 0 if missing
    df["xrd_tp1"] = df["xrd_tp1"].fillna(0)
    df["aqc_tp1"] = df["aqc_tp1"].fillna(0)
    df["sppe_tp1"] = df["sppe_tp1"].fillna(0)

    # Construct TotalInv = (capx + xrd + aqc - sppe) / at_t
    df["TotalInv"] = (
        df["capx_tp1"] + df["xrd_tp1"] + df["aqc_tp1"] - df["sppe_tp1"]
    ) / df["at_t"]

    print(f"  TotalInv computed for {len(df):,} observations")
    print(
        f"  TotalInv mean: {df['TotalInv'].mean():.4f}, std: {df['TotalInv'].std():.4f}"
    )

    return df


# ==============================================================================
# Sales Growth Construction
# ==============================================================================


def construct_sales_growth(df):
    """Construct SalesGrowth at time t

    SalesGrowth_t = (sale_t - sale_tm1) / sale_tm1

    NON-NEGOTIABLE RULES:
    - DROP if sale_tm1 is missing OR sale_tm1 <= 0
    - DROP if sale_t is missing

    Args:
        df: DataFrame with sale_t, sale_tm1

    Returns:
        DataFrame with SalesGrowth column and filters applied
    """
    print("\nConstructing SalesGrowth_t...")

    n_start = len(df)

    # Rule 1: Require sale_tm1 > 0
    df = df[df["sale_tm1"].notna() & (df["sale_tm1"] > 0)].copy()
    n_lag = len(df)
    print(f"  Require sale_tm1 > 0: {n_start - n_lag:,} dropped")

    # Rule 2: Require sale_t non-missing
    df = df[df["sale_t"].notna()].copy()
    n_curr = len(df)
    print(f"  Require sale_t non-missing: {n_lag - n_curr:,} dropped")

    # Construct SalesGrowth = (sale_t - sale_tm1) / sale_tm1
    df["SalesGrowth"] = (df["sale_t"] - df["sale_tm1"]) / df["sale_tm1"]

    print(f"  SalesGrowth computed for {len(df):,} observations")
    print(
        f"  SalesGrowth mean: {df['SalesGrowth'].mean():.4f}, std: {df['SalesGrowth'].std():.4f}"
    )

    return df


# ==============================================================================
# First-Stage Regression
# ==============================================================================


def run_first_stage_regression(df, min_cell_size=30):
    """Run Biddle (2009) first-stage regressions by (ind2, fyear)

    Specification:
        TotalInv_{i,t+1} = a_{ind2,t} + b_{ind2,t} * SalesGrowth_{i,t} + e

    CELL SIZE RULE (LOCKED):
    - If N < 30 for (ind2, fyear) cell:
        - Try fallback to (ind1, fyear) with N >= 30
        - If still N < 30, DROP those observations
    - Report fraction of cells with N >= 30, fraction dropped

    Args:
        df: DataFrame with TotalInv, SalesGrowth, ind2, ind1, fyear
        min_cell_size: Minimum observations per industry-year cell (default 30)

    Returns:
        DataFrame with AbsAbInv column and first-stage diagnostics
    """
    print(
        f"\nRunning first-stage regressions by (ind2, fyear) with min_cell_size={min_cell_size}..."
    )

    # Prepare data for regression
    reg_data = df.dropna(
        subset=["TotalInv", "SalesGrowth", "ind2", "ind1", "fyear"]
    ).copy()

    if len(reg_data) == 0:
        raise ValueError("No valid data for first-stage regression")

    print(f"  Valid observations for regression: {len(reg_data):,}")

    # Track regression results
    results_buffer = []
    thin_cells_ind2 = []
    thin_cells_ind1 = []
    cell_stats = []

    # Group by (ind2, fyear) for first attempt
    grouped_ind2 = reg_data.groupby(["ind2", "fyear"])

    total_cells_ind2 = len(grouped_ind2)
    n_cells_with_n_ge_30 = 0
    n_cells_fallback_to_ind1 = 0
    n_observations_dropped = 0

    print(f"  Total (ind2, fyear) cells: {total_cells_ind2}")

    # Track processed indices to avoid duplicates from ind1 fallback
    processed_indices = set()

    # First pass: Process ind2 cells with sufficient size
    cells_with_sufficient_size = []
    cells_too_small = []

    for (ind2, fyear), group in grouped_ind2:
        if len(group) >= min_cell_size:
            cells_with_sufficient_size.append(((ind2, fyear), group))
            n_cells_with_n_ge_30 += 1
        else:
            cells_too_small.append(((ind2, fyear), group))

    # Process cells with sufficient size
    for i, ((ind2, fyear), group) in enumerate(cells_with_sufficient_size):
        if (i + 1) % 50 == 0:
            print(
                f"  Progress: {i + 1}/{len(cells_with_sufficient_size)} sufficient cells processed..."
            )

        n_obs = len(group)

        # Prepare regression data
        Y = group["TotalInv"].values
        X = group[["SalesGrowth"]].values
        X = sm.add_constant(X)

        # Run OLS
        try:
            model = sm.OLS(Y, X).fit()
            predicted = model.predict(X)
            residuals = Y - predicted

            # Store results and mark as processed
            for j, (idx, res, pred) in enumerate(
                zip(group.index, residuals, predicted)
            ):
                results_buffer.append(
                    {
                        "index": int(idx),
                        "gvkey": group["gvkey"].iloc[j],
                        "fyear": int(group["fyear"].iloc[j]),
                        "TotalInv": float(group["TotalInv"].iloc[j]),
                        "SalesGrowth": float(group["SalesGrowth"].iloc[j]),
                        "AbInv": float(res),  # Residual (can be negative)
                        "predicted_investment": float(pred),
                        "first_stage_n": int(n_obs),
                        "first_stage_r2": float(model.rsquared),
                        "industry_type": "ind2",
                        "industry_code": int(ind2),
                    }
                )
                processed_indices.add(idx)

            # Track cell statistics
            cell_stats.append(
                {
                    "industry_type": "ind2",
                    "industry_code": int(ind2),
                    "fyear": int(fyear),
                    "n": int(n_obs),
                    "r2": float(model.rsquared),
                    "coef_sales_growth": float(model.params[1]),
                }
            )

        except Exception as e:
            print(f"  Warning: Regression failed for ind2={ind2}, fyear={fyear}: {e}")
            thin_cells_ind2.append((ind2, fyear, n_obs, str(e)))
            continue

    # Second pass: Handle ind1 fallback for unprocessed observations
    # Group unprocessed observations by (ind1, fyear)
    unprocessed_indices = [
        idx
        for _, group in cells_too_small
        for idx in group.index
        if idx not in processed_indices
    ]

    if unprocessed_indices:
        unprocessed_data = reg_data.loc[unprocessed_indices]
        grouped_ind1 = unprocessed_data.groupby(["ind1", "fyear"])

        for (ind1, fyear), group in grouped_ind1:
            n_obs = len(group)

            if n_obs >= min_cell_size:
                # Run regression with ind1
                n_cells_fallback_to_ind1 += 1

                Y = group["TotalInv"].values
                X = group[["SalesGrowth"]].values
                X = sm.add_constant(X)

                try:
                    model = sm.OLS(Y, X).fit()
                    predicted = model.predict(X)
                    residuals = Y - predicted

                    # Store results for this group
                    for k, (idx, res, pred) in enumerate(
                        zip(group.index, residuals, predicted)
                    ):
                        results_buffer.append(
                            {
                                "index": int(idx),
                                "gvkey": group["gvkey"].iloc[k],
                                "fyear": int(group["fyear"].iloc[k]),
                                "TotalInv": float(group["TotalInv"].iloc[k]),
                                "SalesGrowth": float(group["SalesGrowth"].iloc[k]),
                                "AbInv": float(res),
                                "predicted_investment": float(pred),
                                "first_stage_n": int(n_obs),
                                "first_stage_r2": float(model.rsquared),
                                "industry_type": "ind1_fallback",
                                "industry_code": int(ind1),
                            }
                        )
                        processed_indices.add(idx)

                    # Track cell statistics
                    cell_stats.append(
                        {
                            "industry_type": "ind1_fallback",
                            "industry_code": int(ind1),
                            "fyear": int(fyear),
                            "n": int(n_obs),
                            "r2": float(model.rsquared),
                            "coef_sales_growth": float(model.params[1]),
                        }
                    )

                except Exception as e:
                    print(
                        f"  Warning: Fallback regression failed for ind1={ind1}, fyear={fyear}: {e}"
                    )
                    thin_cells_ind1.append((ind1, fyear, n_obs, str(e)))
                    n_observations_dropped += len(group)
                    continue

            else:
                # ind1 cell too small - drop these observations
                n_observations_dropped += len(group)
                thin_cells_ind1.append((ind1, fyear, n_obs, "N < min_cell_size"))

    # Convert to DataFrame
    if not results_buffer:
        raise ValueError("No residuals computed - all cells too small")

    result_df = pd.DataFrame(results_buffer)

    # Compute AbsAbInv = |residual|
    result_df["AbsAbInv"] = result_df["AbInv"].abs()

    # Print summary
    pct_cells_with_n_ge_30 = (
        (n_cells_with_n_ge_30 / total_cells_ind2 * 100) if total_cells_ind2 > 0 else 0
    )
    pct_observations_dropped = (
        (n_observations_dropped / len(reg_data) * 100) if len(reg_data) > 0 else 0
    )

    print("\nFirst-stage regression summary:")
    print(f"  Total (ind2, fyear) cells: {total_cells_ind2}")
    print(
        f"  Cells with N >= {min_cell_size}: {n_cells_with_n_ge_30} ({pct_cells_with_n_ge_30:.1f}%)"
    )
    print(f"  Cells using ind1 fallback: {n_cells_fallback_to_ind1}")
    print(
        f"  Observations dropped: {n_observations_dropped:,} ({pct_observations_dropped:.1f}%)"
    )
    print(f"  Final observations with residuals: {len(result_df):,}")

    print("\nAbsAbInv statistics:")
    print(f"  Mean: {result_df['AbsAbInv'].mean():.6f}")
    print(f"  Std: {result_df['AbsAbInv'].std():.6f}")
    print(f"  Min: {result_df['AbsAbInv'].min():.6f}")
    print(f"  Max: {result_df['AbsAbInv'].max():.6f}")

    # Cell diagnostics DataFrame
    cell_diagnostics = pd.DataFrame(cell_stats)

    return (
        result_df,
        cell_diagnostics,
        {
            "total_cells": total_cells_ind2,
            "cells_with_n_ge_30": n_cells_with_n_ge_30,
            "cells_fallback_to_ind1": n_cells_fallback_to_ind1,
            "observations_dropped": n_observations_dropped,
            "final_observations": len(result_df),
        },
    )


# ==============================================================================
# Control Variables Construction
# ==============================================================================


def construct_controls(df):
    """Construct Biddle (2009) control variables at year t

    Controls:
    - ln_at_t: log(at_t) - size
    - lev_t: (dltt + dlc) / at_t - leverage
    - cash_t: che / at_t - cash holdings
    - roa_t: oibdp / at_t (or ni / at_t) - profitability
    - mb_t: (prcc_f * csho) / at_t - market-to-book

    Args:
        df: DataFrame with Compustat variables

    Returns:
        DataFrame with control variables
    """
    print("\nConstructing control variables...")

    # Size: ln(at_t)
    df["ln_at_t"] = np.log(df["at_t"])
    print("  Computed ln_at_t (log assets)")

    # Leverage: (dltt + dlc) / at_t
    df["lev_t"] = (df["dltt"].fillna(0) + df["dlc"].fillna(0)) / df["at_t"]
    print("  Computed lev_t (leverage)")

    # Cash: che / at_t
    df["cash_t"] = df["che"].fillna(0) / df["at_t"]
    print("  Computed cash_t (cash/assets)")

    # ROA: oibdp / at_t (preferred) or ni / at_t (fallback)
    df["roa_t"] = np.where(
        df["oibdp"].notna(), df["oibdp"] / df["at_t"], df["ni"] / df["at_t"]
    )
    n_oibdp = df["oibdp"].notna().sum()
    n_ni_fallback = df["oibdp"].isna().sum() & df["ni"].notna().sum()
    print(
        f"  Computed roa_t: {n_oibdp:,} from OIBDP, {n_ni_fallback:,} from NI fallback"
    )

    # Market-to-book: (prcc_f * csho) / at_t
    df["mve_t"] = df["prcc_f"] * df["csho"]
    df["mb_t"] = np.where(
        (df["mve_t"].notna()) & (df["mve_t"] > 0), df["mve_t"] / df["at_t"], np.nan
    )
    n_mb_valid = df["mb_t"].notna().sum()
    print(f"  Computed mb_t: {n_mb_valid:,} valid observations")

    return df


# ==============================================================================
# Winsorization
# ==============================================================================


def winsorize_by_fyear(df, variables, lower=0.01, upper=0.99):
    """Winsorize variables at 1% and 99% by fiscal year

    For each fyear, compute p1 and p99 from non-missing values.
    Replace values < p1 with p1, values > p99 with p99.

    Args:
        df: DataFrame with fyear column
        variables: List of variable names to winsorize
        lower: Lower percentile (default 0.01)
        upper: Upper percentile (default 0.99)

    Returns:
        DataFrame with winsorized variables
    """
    print(f"\nWinsorizing at {lower * 100:.0f}%/{upper * 100:.0f}% by fyear...")

    for var in variables:
        if var not in df.columns:
            print(f"  Skipping {var} (not in DataFrame)")
            continue

        # Compute percentile bounds by fyear
        bounds = df.groupby("fyear")[var].agg(
            lambda x: (x.quantile(lower), x.quantile(upper))
            if x.notna().sum() > 0
            else (np.nan, np.nan)
        )

        # Apply winsorization
        def winsorize_group(x, var_name, fyear_val):
            if (fyear_val, var_name) not in bounds.index:
                return x
            lower_bound, upper_bound = bounds.loc[(fyear_val, var_name)]
            if pd.isna(lower_bound) or pd.isna(upper_bound):
                return x
            return x.clip(lower=lower_bound, upper=upper_bound)

        # Apply winsorization by group
        df[var] = df.groupby("fyear")[var].transform(
            lambda x: x.clip(lower=x.quantile(lower), upper=x.quantile(upper))
            if x.notna().sum() > 0
            else x
        )

        print(f"  Winsorized {var}")

    return df


# ==============================================================================
# Report Generation
# ==============================================================================


def generate_report(df, cell_diagnostics, regression_stats, output_dir, stats):
    """Generate summary report for H9 abnormal investment construction

    Args:
        df: DataFrame with AbsAbInv and controls
        cell_diagnostics: DataFrame with first-stage cell statistics
        regression_stats: Dictionary with regression summary stats
        output_dir: Output directory path
        stats: Statistics dictionary for JSON output
    """
    print("\nGenerating summary report...")

    report_path = output_dir / "report_step58_03.md"

    with open(report_path, "w") as f:
        f.write("# Step 58-03: H9 Abnormal Investment Construction Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Summary\n\n")
        f.write(f"- **Final observations:** {len(df):,}\n")
        f.write(f"- **Firms:** {df['gvkey'].nunique():,}\n")
        f.write(f"- **Fiscal years:** {df['fyear'].min()}-{df['fyear'].max()}\n\n")

        f.write("## Sample Construction\n\n")
        f.write("| Stage | N | Pct |\n")
        f.write("|-------|---|-----|\n")
        f.write(
            f"| Input (Compustat) | {stats['input'].get('total_rows', 'N/A'):,} | 100% |\n"
        )
        f.write(
            f"| Final sample | {len(df):,} | {(len(df) / stats['input'].get('total_rows', 1) * 100):.1f}% |\n\n"
        )

        f.write("## First-Stage Regression Diagnostics\n\n")
        f.write(f"- **Total (ind2, fyear) cells:** {regression_stats['total_cells']}\n")
        f.write(f"- **Cells with N >= 30:** {regression_stats['cells_with_n_ge_30']}\n")
        f.write(
            f"- **Cells using ind1 fallback:** {regression_stats['cells_fallback_to_ind1']}\n"
        )
        f.write(
            f"- **Observations dropped:** {regression_stats['observations_dropped']:,}\n\n"
        )

        f.write("### First-Stage R2 Distribution\n\n")
        if "first_stage_r2" in df.columns:
            r2_stats = df["first_stage_r2"].describe()
            f.write("| Statistic | R2 |\n")
            f.write("|-----------|----|\n")
            f.write(f"| Mean | {r2_stats['mean']:.4f} |\n")
            f.write(f"| Median | {r2_stats['50%']:.4f} |\n")
            f.write(f"| Std | {r2_stats['std']:.4f} |\n")
            f.write(f"| Min | {r2_stats['min']:.4f} |\n")
            f.write(f"| Max | {r2_stats['max']:.4f} |\n\n")

        f.write("## Variable Distributions\n\n")

        # Investment variables
        f.write("### Investment Variables\n\n")
        for var in ["TotalInv", "SalesGrowth", "AbsAbInv"]:
            if var in df.columns:
                desc = df[var].describe(percentiles=[0.01, 0.99])
                f.write(f"**{var}:**\n\n")
                f.write(f"- Mean: {desc['mean']:.6f}\n")
                f.write(f"- Std: {desc['std']:.6f}\n")
                f.write(f"- Min: {desc['min']:.6f}\n")
                f.write(f"- Max: {desc['max']:.6f}\n")
                f.write(f"- p1: {desc['1%']:.6f}\n")
                f.write(f"- p99: {desc['99%']:.6f}\n\n")

        # Control variables
        f.write("### Control Variables\n\n")
        for var in ["ln_at_t", "lev_t", "cash_t", "roa_t", "mb_t"]:
            if var in df.columns:
                desc = df[var].describe()
                missing = df[var].isna().sum()
                f.write(f"**{var}:**\n\n")
                f.write(f"- Mean: {desc['mean']:.6f}\n")
                f.write(f"- Std: {desc['std']:.6f}\n")
                f.write(f"- Min: {desc['min']:.6f}\n")
                f.write(f"- Max: {desc['max']:.6f}\n")
                f.write(f"- Missing: {missing:,} ({missing / len(df) * 100:.1f}%)\n\n")

        f.write("## Methodology Notes\n\n")
        f.write("### Investment Specification (Biddle 2009)\n\n")
        f.write("```\n")
        f.write(
            "TotalInv_{t+1} = (capx_{t+1} + xrd_{t+1} + aqc_{t+1} - sppe_{t+1}) / at_t\n"
        )
        f.write(
            "Expected Inv: TotalInv_{i,t+1} = a_{ind2,t} + b_{ind2,t} * SalesGrowth_{i,t} + e\n"
        )
        f.write("AbsAbInv_{t+1} = |e|\n")
        f.write("```\n\n")

        f.write("### Missingness Rules\n\n")
        f.write("- **CAPX (capx_tp1):** Required non-missing\n")
        f.write("- **R&D (xrd_tp1):** Set to 0 if missing\n")
        f.write("- **Acquisitions (aqc_tp1):** Set to 0 if missing\n")
        f.write("- **Asset Sales (sppe_tp1):** Set to 0 if missing\n")
        f.write("- **SalesGrowth:** Require sale_tm1 > 0 (valid lagged sales)\n\n")

        f.write("### First-Stage Cell Size Rule\n\n")
        f.write("- Require N >= 30 observations per (ind2, fyear) cell\n")
        f.write("- Fallback to (ind1, fyear) if ind2 cell too small\n")
        f.write("- Drop observations if both ind2 and ind1 cells too small\n\n")

        f.write("### Industry Exclusions\n\n")
        f.write("- Utilities: SIC 4900-4999\n")
        f.write("- Financials: SIC 6000-6999\n\n")

        f.write("### Winsorization\n\n")
        f.write("- All variables winsorized at 1% and 99% by fiscal year\n")
        f.write("- Applied AFTER first-stage regression\n\n")

    print(f"  Wrote: {report_path.name}")

    # Save cell diagnostics
    diag_path = output_dir / "first_stage_diagnostics.csv"
    cell_diagnostics.to_csv(diag_path, index=False)
    print(f"  Wrote: {diag_path.name}")

    return report_path


# ==============================================================================
# CLI and Prerequisites
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="""
STEP 5.8: H9 Abnormal Investment (Biddle 2009)

Constructs Biddle-style abnormal investment (AbsAbInv) and control variables
for H9 regression testing PRisk x CEO Style -> Abnormal Investment.

Per Biddle (2009), runs first-stage regressions by (ind2, fyear):
    TotalInv_{t+1} = a_{ind2,t} + b_{ind2,t} * SalesGrowth_t + e

The absolute residual (AbsAbInv = |e|) measures investment inefficiency.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    parser.add_argument(
        "--min-cell-size",
        type=int,
        default=30,
        help="Minimum observations per industry-year cell (default 30)",
    )

    parser.add_argument(
        "--fyear-min",
        type=int,
        default=2002,
        help="Minimum fiscal year (default 2002)",
    )

    parser.add_argument(
        "--fyear-max",
        type=int,
        default=2018,
        help="Maximum fiscal year (default 2018)",
    )

    return parser.parse_args()


def check_prerequisites(paths, args):
    """Validate all required inputs exist"""
    print("\nChecking prerequisites...")

    required_files = {
        "Compustat": paths["compustat_file"],
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
    paths = setup_paths(timestamp)

    # Handle dry-run mode
    if args.dry_run:
        print("=" * 60)
        print("STEP 5.8: H9 Abnormal Investment - DRY RUN")
        print(f"Timestamp: {timestamp}")
        print("=" * 60)

        prereq_ok = check_prerequisites(paths, args)
        if prereq_ok:
            print("\n[OK] All prerequisites validated")
            print("\nWould compute:")
            print("  - TotalInv_{t+1} = (capx + xrd + aqc - sppe) / at_t")
            print("  - SalesGrowth_t = (sale_t - sale_tm1) / sale_tm1")
            print("  - First-stage regression by (ind2, fyear):")
            print("      TotalInv ~ SalesGrowth")
            print("  - AbsAbInv = |residual|")
            print("  - Controls: ln_at, lev, cash, roa, mb")
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
    print("STEP 5.8: H9 Abnormal Investment (Biddle 2009)")
    print(f"Timestamp: {timestamp}")
    print("=" * 60)

    # Initialize statistics
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    mem_start = get_process_memory_mb()
    memory_readings = [mem_start["rss_mb"]]

    stats = {
        "step_id": "5.8_H9_AbnormalInvestment",
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

    # Load Compustat
    print("\nCompustat:")
    stats["input"]["files"].append(str(paths["compustat_file"]))
    stats["input"]["checksums"][paths["compustat_file"].name] = compute_file_checksum(
        paths["compustat_file"]
    )
    compustat = load_compustat(
        paths["compustat_file"], fyear_min=args.fyear_min, fyear_max=args.fyear_max
    )
    print_stat("Compustat rows", value=len(compustat))
    stats["input"]["total_rows"] = len(compustat)

    # ========================================================================
    # Industry Classification
    # ========================================================================

    print("\n" + "=" * 60)
    print("Industry Classification")
    print("=" * 60)

    len(compustat)
    compustat = assign_industry(compustat)
    stats["processing"]["after_industry_filter"] = len(compustat)

    # ========================================================================
    # Create Panel with Leads/Lags
    # ========================================================================

    print("\n" + "=" * 60)
    print("Creating Panel with Leads/Lags")
    print("=" * 60)

    compustat = create_panel_with_leads_lags(compustat)

    # ========================================================================
    # Construct Investment
    # ========================================================================

    print("\n" + "=" * 60)
    print("Constructing Investment")
    print("=" * 60)

    n_before_inv = len(compustat)
    compustat = construct_investment(compustat)
    stats["processing"]["after_investment_filter"] = len(compustat)
    print_stat("Investment filter", before=n_before_inv, after=len(compustat))

    # ========================================================================
    # Construct Sales Growth
    # ========================================================================

    print("\n" + "=" * 60)
    print("Constructing Sales Growth")
    print("=" * 60)

    n_before_sg = len(compustat)
    compustat = construct_sales_growth(compustat)
    stats["processing"]["after_sales_growth_filter"] = len(compustat)
    print_stat("Sales growth filter", before=n_before_sg, after=len(compustat))

    # ========================================================================
    # Run First-Stage Regressions
    # ========================================================================

    print("\n" + "=" * 60)
    print("Running First-Stage Regressions")
    print("=" * 60)

    result_df, cell_diagnostics, regression_stats = run_first_stage_regression(
        compustat, min_cell_size=args.min_cell_size
    )

    stats["processing"]["first_stage"] = regression_stats

    # ========================================================================
    # Merge Back Original Data
    # ========================================================================

    print("\n" + "=" * 60)
    print("Merging Back Original Data")
    print("=" * 60)

    # Select original variables from compustat for controls
    control_vars = [
        "gvkey",
        "fyear",
        "at_t",
        "dltt",
        "dlc",
        "che",
        "oibdp",
        "ni",
        "prcc_f",
        "csho",
        "sic",
        "ind2",
        "ind1",
    ]

    # Get unique rows from compustat with control variables
    compustat_controls = compustat[
        control_vars + ["sale_t", "sale_tm1"]
    ].drop_duplicates(subset=["gvkey", "fyear"])

    # Merge with results
    result_df = result_df.merge(compustat_controls, on=["gvkey", "fyear"], how="left")
    print(f"  Merged data: {len(result_df):,} observations")

    # ========================================================================
    # Construct Controls
    # ========================================================================

    print("\n" + "=" * 60)
    print("Constructing Control Variables")
    print("=" * 60)

    result_df = construct_controls(result_df)

    # Re-compute SalesGrowth from merged data (use the original value)
    # This is already in result_df from the first-stage data

    # ========================================================================
    # Winsorize Variables
    # ========================================================================

    print("\n" + "=" * 60)
    print("Winsorizing Variables")
    print("=" * 60)

    vars_to_winsorize = [
        "AbsAbInv",
        "TotalInv",
        "SalesGrowth",
        "ln_at_t",
        "lev_t",
        "cash_t",
        "roa_t",
        "mb_t",
    ]
    result_df = winsorize_by_fyear(result_df, vars_to_winsorize, lower=0.01, upper=0.99)

    # ========================================================================
    # Final Output Selection
    # ========================================================================

    print("\n" + "=" * 60)
    print("Preparing Final Output")
    print("=" * 60)

    # Select output columns
    output_columns = [
        "gvkey",
        "fyear",
        "AbsAbInv",
        "TotalInv",
        "SalesGrowth",
        "ln_at_t",
        "lev_t",
        "cash_t",
        "roa_t",
        "mb_t",
        "ind2",
        "sic",
    ]

    final_output = result_df[output_columns].copy()
    final_output = final_output.sort_values(["gvkey", "fyear"]).reset_index(drop=True)

    print(f"  Final output: {len(final_output):,} observations")
    print(f"  Firms: {final_output['gvkey'].nunique():,}")
    print(
        f"  Fiscal years: {final_output['fyear'].min()}-{final_output['fyear'].max()}"
    )

    # Check missingness
    print("\n  Missingness in controls:")
    for var in ["ln_at_t", "lev_t", "cash_t", "roa_t", "mb_t"]:
        n_missing = final_output[var].isna().sum()
        print(f"    {var}: {n_missing:,} ({n_missing / len(final_output) * 100:.1f}%)")

    # ========================================================================
    # Write Outputs
    # ========================================================================

    print("\n" + "=" * 60)
    print("Writing Outputs")
    print("=" * 60)

    # Write parquet
    output_file = paths["output_dir"] / "abnormal_investment.parquet"
    final_output.to_parquet(output_file, index=False)
    print(f"  Wrote: {output_file.name}")
    stats["output"]["files"].append(output_file.name)
    stats["output"]["checksums"][output_file.name] = compute_file_checksum(output_file)
    stats["output"]["final_rows"] = len(final_output)

    # Generate report
    report_path = generate_report(
        final_output, cell_diagnostics, regression_stats, paths["output_dir"], stats
    )
    stats["output"]["files"].append(report_path.name)

    # Write stats.json
    stats["variables"] = {
        "AbsAbInv": {
            "mean": float(final_output["AbsAbInv"].mean()),
            "std": float(final_output["AbsAbInv"].std()),
            "min": float(final_output["AbsAbInv"].min()),
            "max": float(final_output["AbsAbInv"].max()),
            "n": int(final_output["AbsAbInv"].notna().sum()),
        },
        "TotalInv": {
            "mean": float(final_output["TotalInv"].mean()),
            "std": float(final_output["TotalInv"].std()),
        },
        "SalesGrowth": {
            "mean": float(final_output["SalesGrowth"].mean()),
            "std": float(final_output["SalesGrowth"].std()),
        },
    }

    # Add control stats
    for var in ["ln_at_t", "lev_t", "cash_t", "roa_t", "mb_t"]:
        if var in final_output.columns:
            stats["variables"][var] = {
                "mean": float(final_output[var].mean()),
                "std": float(final_output[var].std()),
                "missing": int(final_output[var].isna().sum()),
            }

    save_stats(stats, paths["output_dir"])

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
        throughput = calculate_throughput(len(final_output), duration_seconds)
        stats["throughput"] = {
            "rows_per_second": throughput,
            "total_rows": len(final_output),
            "duration_seconds": round(duration_seconds, 3),
        }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Abnormal investment constructed: {len(final_output):,} observations")
    print(f"  AbsAbInv mean: {stats['variables']['AbsAbInv']['mean']:.6f}")
    print(f"  Firms: {final_output['gvkey'].nunique():,}")
    print(f"\nOutputs saved to: {paths['output_dir']}")
    print(f"Log saved to: {paths['log_file']}")

    log_file.close()


if __name__ == "__main__":
    main()
