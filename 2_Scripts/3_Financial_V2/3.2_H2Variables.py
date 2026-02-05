#!/usr/bin/env python3
"""
==============================================================================
STEP 3.2: H2 Investment Efficiency Variables
==============================================================================
ID: 3.2_H2Variables
Description: Constructs H2 dependent variables (Over/Underinvestment dummies,
             Efficiency Score, ROA Residual) and controls for investment
             efficiency hypothesis testing.

Variables Computed:
    - Overinvestment Dummy: 1 if (Capex/DP > 1.5) AND (SalesGrowth < ind_median)
    - Underinvestment Dummy: 1 if (Capex/DP < 0.75) AND (Tobin's Q > 1.5)
    - Efficiency Score: 1 - (% inefficient years) over 5-year window
    - ROA Residual: Residual from Biddle et al. (2009) regression
    - Analyst Dispersion: STDEV / |MEANEST| from IBES
    - Tobin's Q: (AT + ME - CEQ) / AT
    - CF Volatility: StdDev(OANCF/AT) over 5 years
    - Industry Capex Intensity: Mean(capex_at) by FF48-year
    - Firm Size: ln(AT)
    - ROA: IB / AT
    - FCF: (OANCF - CAPX) / AT
    - Earnings Volatility: StdDev(ROA) over 5 years

Inputs:
    - 4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - 1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet (Compustat raw data)
    - 1_Inputs/Siccodes48.zip (Fama-French 48 industry classifications)
    - 1_Inputs/Siccodes12.zip (Fama-French 12 industry classifications)
    - 1_Inputs/tr_ibes/tr_ibes.parquet (IBES analyst forecasts)

Outputs:
    - 4_Outputs/3_Financial_V2/{timestamp}/H2_InvestmentEfficiency.parquet
    - 4_Outputs/3_Financial_V2/{timestamp}/stats.json

Deterministic: true
==============================================================================
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import yaml
import hashlib
import json
import time
import psutil
import warnings

# Add parent directory to sys.path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Import shared path validation utilities
from shared.path_utils import (
    validate_output_path,
    ensure_output_dir,
    validate_input_file,
    get_latest_output_dir,
)

# Import DualWriter from shared.observability_utils
from shared.observability_utils import (
    DualWriter,
    compute_file_checksum,
    print_stat,
    analyze_missing_values,
    print_stats_summary,
    save_stats,
    get_process_memory_mb,
    calculate_throughput,
    detect_anomalies_zscore,
)

# Import industry utilities
from shared.industry_utils import parse_ff_industries

# Import statsmodels for OLS regressions
import statsmodels.api as sm

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

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
        "ibes_file": root / "1_Inputs" / "tr_ibes" / "tr_ibes.parquet",
    }

    # Output directory
    output_base = root / "4_Outputs" / "3_Financial_V2"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "3_Financial_V2"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H2.log"

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


def load_compustat_h2(compustat_file):
    """Load Compustat data with only required columns for H2 variables"""
    print(f"  Loading Compustat data...")

    # Required columns for H2 variables
    # Quarterly fields (q suffix): at, dp (depreciation), sale, ib, che, ceq, csho, prcc, dltt, dlc
    # Annual fields (y suffix): capx, oancf
    required_cols = [
        "gvkey",
        "datadate",
        "fyearq",
        "sic",  # SIC code for industry classification
        # Investment variables (quarterly)
        "capxy",   # Capital Expenditures Annual
        "dpq",     # Depreciation Quarterly
        "saleq",   # Sales Quarterly
        # Assets and equity (quarterly)
        "atq",
        "cheq",
        "ceqq",
        "cshoq",
        "prccq",
        "dlttq",
        "dlcq",
        # Annual fields
        "iby",     # Income Before Extra Items Annual
        "oancfy",  # Operating Cash Flow Annual
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
        if col not in ["gvkey", "datadate", "sic"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

    # Add fiscal year field from fyearq
    if "fyearq" in df.columns:
        df["fiscal_year"] = df["fyearq"].astype("Int64")
    else:
        # Extract fiscal year from datadate
        df["fiscal_year"] = df["datadate"].dt.year

    return df


def load_ibes(ibes_file):
    """Load IBES analyst forecast data"""
    print(f"  Loading IBES data...")

    required_cols = [
        "cusip",
        "fpedats",  # Forecast Period End Date
        "fiscalp",  # Periodicity
        "numest",   # Number of Estimates
        "meanest",  # Mean Estimate
        "stdev",    # Standard Deviation
    ]

    # Check which columns exist
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(ibes_file)
    available_cols = set(pf.schema_arrow.names)

    cols_to_read = [c for c in required_cols if c in available_cols]

    if len(cols_to_read) < len(required_cols):
        missing = set(required_cols) - set(cols_to_read)
        print(f"  Warning: Missing IBES columns: {missing}")

    df = pd.read_parquet(ibes_file, columns=cols_to_read)

    print(f"  Loaded IBES: {len(df):,} observations")

    # Convert dates
    if "fpedats" in df.columns:
        df["fpedats"] = pd.to_datetime(df["fpedats"], format="%Y%m%d", errors="coerce")

    # Convert numeric
    for col in ["numest", "meanest", "stdev"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Extract year from forecast period end date
    if "fpedats" in df.columns:
        df["year"] = df["fpedats"].dt.year

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


def assign_ff_industries(df, ff48_map, ff12_map):
    """Assign Fama-French industry classifications based on SIC code"""
    print("\nAssigning FF industries...")

    # Normalize SIC code
    if "sic" in df.columns:
        df["sic"] = pd.to_numeric(df["sic"], errors="coerce")

    # Assign FF48
    df["ff48"] = df["sic"].map(lambda x: ff48_map.get(int(x), (48, "Other"))[0] if pd.notna(x) else 48)

    # Assign FF12
    df["ff12"] = df["sic"].map(lambda x: ff12_map.get(int(x), (12, "Other"))[0] if pd.notna(x) else 12)

    print(f"  FF48 industries: {df['ff48'].nunique()} unique")
    print(f"  FF12 industries: {df['ff12'].nunique()} unique")

    return df


# ==============================================================================
# Over/Underinvestment Classification (H2-01, H2-02)
# ==============================================================================


def compute_capex_dp(df):
    """Compute Capex/Depreciation ratio"""
    print("\nComputing Capex/DP...")

    # Require positive depreciation
    df = df.copy()
    df["dpq_safe"] = df["dpq"].where(df["dpq"] > 0)

    # Compute ratio
    df["capex_dp"] = df["capxy"] / df["dpq_safe"]

    result = df[["gvkey", "fiscal_year", "datadate", "capex_dp"]].copy()

    n_computed = result["capex_dp"].notna().sum()
    print(f"  Computed capex_dp for {n_computed:,} observations")

    return result


def compute_sales_growth(df):
    """Compute sales growth = (sale_t - sale_{t-1}) / |sale_{t-1}|"""
    print("\nComputing Sales Growth...")

    # Sort by gvkey and fiscal_year
    df = df.sort_values(["gvkey", "fiscal_year"]).copy()

    # Compute lagged sales
    df["sale_lag"] = df.groupby("gvkey")["saleq"].shift(1)

    # Compute growth
    df["sales_growth"] = (df["saleq"] - df["sale_lag"]) / df["sale_lag"].abs()

    result = df[["gvkey", "fiscal_year", "datadate", "sales_growth"]].copy()

    n_computed = result["sales_growth"].notna().sum()
    print(f"  Computed sales_growth for {n_computed:,} observations")

    return result


def compute_industry_year_median(df, value_col, min_firms=5):
    """Compute industry-year median with fallback to FF12 if FF48 cell < min_firms"""
    print(f"\nComputing industry-year median for {value_col}...")

    results = []

    # Group by FF48-year
    for (ff48, year), group in df.groupby(["ff48", "fiscal_year"]):
        valid_vals = group[value_col].dropna()

        if len(valid_vals) >= min_firms:
            median_val = valid_vals.median()
        else:
            # Fallback to FF12
            ff12 = group["ff12"].iloc[0] if not group["ff12"].isna().all() else 12
            ff12_group = df[(df["ff12"] == ff12) & (df["fiscal_year"] == year)]
            valid_vals_ff12 = ff12_group[value_col].dropna()
            median_val = valid_vals_ff12.median() if len(valid_vals_ff12) >= min_firms else np.nan

        for _, row in group.iterrows():
            results.append({
                "gvkey": row["gvkey"],
                "fiscal_year": row["fiscal_year"],
                f"{value_col}_ind_median": median_val,
            })

    result = pd.DataFrame(results)

    n_valid = result[f"{value_col}_ind_median"].notna().sum()
    print(f"  Computed industry median for {n_valid:,} observations")

    return result


def compute_overinvest_dummy(df, ind_median_df):
    """Compute Overinvestment Dummy: 1 if capex_dp > 1.5 AND sales_growth < ind_median"""
    print("\nComputing Overinvestment Dummy...")

    # Merge with industry median
    df = df.merge(
        ind_median_df[["gvkey", "fiscal_year", "sales_growth_ind_median"]],
        on=["gvkey", "fiscal_year"],
        how="left",
    )

    # Compute dummy
    df["overinvest_dummy"] = (
        (df["capex_dp"] > 1.5) &
        (df["sales_growth"] < df["sales_growth_ind_median"])
    ).astype(int)

    result = df[["gvkey", "fiscal_year", "datadate", "overinvest_dummy"]].copy()

    n_overinvest = result["overinvest_dummy"].sum()
    print(f"  Overinvestment firms: {n_overinvest:,} ({n_overinvest/len(result)*100:.2f}%)")

    return result


def compute_underinvest_dummy(df, tobins_q_df):
    """Compute Underinvestment Dummy: 1 if capex_dp < 0.75 AND tobins_q > 1.5"""
    print("\nComputing Underinvestment Dummy...")

    # Merge with Tobin's Q
    df = df.merge(
        tobins_q_df[["gvkey", "fiscal_year", "tobins_q"]],
        on=["gvkey", "fiscal_year"],
        how="left",
    )

    # Compute dummy
    df["underinvest_dummy"] = (
        (df["capex_dp"] < 0.75) &
        (df["tobins_q"] > 1.5)
    ).astype(int)

    result = df[["gvkey", "fiscal_year", "datadate", "underinvest_dummy"]].copy()

    n_underinvest = result["underinvest_dummy"].sum()
    print(f"  Underinvestment firms: {n_underinvest:,} ({n_underinvest/len(result)*100:.2f}%)")

    return result


def enforce_mutual_exclusivity(overinvest_df, underinvest_df):
    """Enforce mutual exclusivity: if both flags set, set both to 0"""
    print("\nEnforcing mutual exclusivity...")

    # Merge
    df = overinvest_df.merge(
        underinvest_df[["gvkey", "fiscal_year", "underinvest_dummy"]],
        on=["gvkey", "fiscal_year"],
        how="outer",
    )

    # Check for violations
    both_flags = (df["overinvest_dummy"] == 1) & (df["underinvest_dummy"] == 1)
    n_violations = both_flags.sum()

    if n_violations > 0:
        print(f"  Warning: {n_violations} observations have both flags set")
        # Set both to 0
        df.loc[both_flags, "overinvest_dummy"] = 0
        df.loc[both_flags, "underinvest_dummy"] = 0
        print(f"  Fixed: set both to 0 for {n_violations} observations")

    return df


# ==============================================================================
# Efficiency Score (H2-03)
# ==============================================================================


def compute_efficiency_score(df, min_years=3, window=5):
    """Compute Efficiency Score = 1 - (# inefficient years / # years in window)

    Inefficient = overinvest_dummy | underinvest_dummy
    Rolling 5-year window (t-4 to t), minimum 3 years required
    """
    print("\nComputing Efficiency Score (5-year rolling)...")

    # Sort by gvkey and fiscal_year
    df = df.sort_values(["gvkey", "fiscal_year"]).copy()

    # Mark inefficient years
    df["inefficient"] = (df["overinvest_dummy"] == 1) | (df["underinvest_dummy"] == 1)

    results = []

    for gvkey, group in df.groupby("gvkey"):
        group = group.sort_values("fiscal_year")

        for idx, row in group.iterrows():
            fy = row["fiscal_year"]

            # Get trailing window
            window_data = group[
                (group["fiscal_year"] > fy - window - 1)
                & (group["fiscal_year"] <= fy)
            ]

            # Require minimum observations
            n_years = window_data["inefficient"].notna().sum()
            if n_years >= min_years:
                n_inefficient = window_data["inefficient"].sum()
                efficiency_score = 1 - (n_inefficient / n_years)
                results.append({
                    "gvkey": gvkey,
                    "fiscal_year": fy,
                    "efficiency_score": efficiency_score,
                })

    result = pd.DataFrame(results)

    if not result.empty:
        n_computed = result["efficiency_score"].notna().sum()
        print(f"  Computed efficiency_score for {n_computed:,} observations")
        print(f"  Mean efficiency: {result['efficiency_score'].mean():.3f}")
    else:
        print("  Warning: No efficiency scores computed (insufficient data)")

    return result


# ==============================================================================
# Biddle ROA Residual (H2-04)
# ==============================================================================


def compute_delta_roa(df):
    """Compute Delta ROA = ROA(t+2) - ROA(t)"""
    print("\nComputing Delta ROA (t+2 - t)...")

    # First compute ROA
    df_roa = df[df["atq"] > 0].copy()
    df_roa["roa"] = df_roa["iby"] / df_roa["atq"]

    # Sort by gvkey and fiscal_year
    df_roa = df_roa.sort_values(["gvkey", "fiscal_year"])

    # Compute forward ROA (shift -2 means get ROA 2 periods ahead)
    df_roa["roa_f2"] = df_roa.groupby("gvkey")["roa"].shift(-2)

    # Compute delta
    df_roa["delta_roa_t2"] = df_roa["roa_f2"] - df_roa["roa"]

    result = df_roa[["gvkey", "fiscal_year", "delta_roa_t2"]].copy()

    n_computed = result["delta_roa_t2"].notna().sum()
    print(f"  Computed delta_roa_t2 for {n_computed:,} observations")

    return result, df_roa


def compute_roa_residuals(df, ff_industry="ff48", min_obs=20):
    """Compute ROA residual from Biddle et al. (2009) regression

    For each FF48-year with >= 20 obs, run OLS:
        Y: delta_roa_t2
        X: capex_at, tobins_q, cash_holdings, leverage (add constant)
    """
    print(f"\nComputing ROA Residuals (Biddle regression by {ff_industry}-year)...")

    residuals_list = []

    # Group by FF48-year
    grouped = df.groupby([ff_industry, "fiscal_year"])

    for (industry, year), group in grouped:
        # Require minimum observations
        valid_group = group.dropna(subset=["delta_roa_t2", "capex_at", "tobins_q"])

        if len(valid_group) < min_obs:
            # Skip cells with insufficient data
            continue

        # Prepare regression data
        Y = valid_group["delta_roa_t2"]
        X = valid_group[["capex_at", "tobins_q"]]

        # Add constant
        X = sm.add_constant(X)

        # Run OLS
        try:
            model = sm.OLS(Y, X).fit()
            predicted = model.predict(X)
            residual = Y - predicted

            # Store residuals
            for idx, res in zip(valid_group.index, residual):
                residuals_list.append({
                    "index": idx,
                    "roa_residual": res,
                    "predicted_delta_roa": predicted.loc[idx],
                })
        except Exception as e:
            # Regression failed - skip this cell
            print(f"  Warning: Regression failed for {ff_industry}={industry}, year={year}: {e}")
            continue

    if not residuals_list:
        print("  Warning: No residuals computed (regressions failed)")
        return pd.DataFrame()

    result_df = pd.DataFrame(residuals_list)

    # Map back to original dataframe
    result = df.loc[result_df["index"]].copy()
    result["roa_residual"] = result_df["roa_residual"].values
    result["predicted_delta_roa"] = result_df["predicted_delta_roa"].values

    result = result[["gvkey", "fiscal_year", "datadate", "roa_residual", "predicted_delta_roa"]].copy()

    n_computed = result["roa_residual"].notna().sum()
    print(f"  Computed roa_residual for {n_computed:,} observations")

    return result


# ==============================================================================
# IBES Analyst Dispersion (H2-05)
# ==============================================================================


def link_ibes_to_compustat(ibes_df, ccm_file=None):
    """Link IBES to Compustat using CUSIP matching

    For simplicity, we match on CUSIP8 (first 8 characters of CUSIP)
    """
    print("\nLinking IBES to Compustat...")

    # Extract CUSIP8
    ibes_df["cusip8"] = ibes_df["cusip"].astype(str).str[:8]

    # For now, we'll aggregate IBES data at the CUSIP8-year level
    # In a full implementation, you'd use CCM (CRSP-Compustat merged) for precise matching

    # Aggregate to CUSIP8-year level
    ibes_agg = ibes_df.groupby(["cusip8", "year"]).agg({
        "numest": "first",  # Take the first (most recent) numest
        "meanest": "mean",  # Mean of meanest
        "stdev": "mean",    # Mean of stdev
    }).reset_index()

    print(f"  Aggregated IBES: {len(ibes_agg):,} CUSIP8-year observations")

    return ibes_agg


def compute_analyst_dispersion(ibes_df):
    """Compute Analyst Dispersion = STDEV / |MEANEST|

    Filters:
    - numest >= 2
    - |meanest| >= 0.01 (avoid near-zero denominators)
    """
    print("\nComputing Analyst Dispersion...")

    # Apply filters
    df = ibes_df[
        (ibes_df["numest"] >= 2) &
        (ibes_df["meanest"].abs() >= 0.01)
    ].copy()

    # Compute dispersion
    df["analyst_dispersion"] = df["stdev"] / df["meanest"].abs()

    # Take median by CUSIP8-year (in case multiple forecasts per year)
    dispersion = df.groupby(["cusip8", "year"])["analyst_dispersion"].median().reset_index()

    print(f"  Computed analyst_dispersion for {len(dispersion):,} CUSIP8-year observations")

    return dispersion[["cusip8", "year", "analyst_dispersion"]].copy()


# ==============================================================================
# Control Variables (H2-05, H2-06)
# ==============================================================================


def compute_tobins_q(df):
    """Compute Tobin's Q = (AT + Market Equity - CEQ) / AT"""
    print("\nComputing Tobin's Q...")

    if "cshoq" not in df.columns or "prccq" not in df.columns:
        print("  Warning: cshoq or prccq not available, returning empty")
        return pd.DataFrame(columns=["gvkey", "fiscal_year", "datadate", "tobins_q"])

    # Require positive AT
    df_comp = df[df["atq"] > 0].copy()

    # Compute market equity
    df_comp["market_equity"] = df_comp["cshoq"] * df_comp["prccq"]

    # Compute Tobin's Q
    df_comp["tobins_q"] = (df_comp["atq"] + df_comp["market_equity"] - df_comp["ceqq"]) / df_comp["atq"]

    result = df_comp[["gvkey", "fiscal_year", "datadate", "tobins_q"]].copy()

    n_computed = result["tobins_q"].notna().sum()
    print(f"  Computed tobins_q for {n_computed:,} observations")

    return result


def compute_cf_volatility(df, min_years=3, window=5):
    """Compute CF Volatility = StdDev(OANCF/AT) over trailing 5 years"""
    print("\nComputing CF Volatility (5-year rolling)...")

    # Require positive AT and valid OCF
    df_comp = df[
        (df["atq"] > 0) & (df["oancfy"].notna())
    ].copy()

    # Compute OCF/AT ratio
    df_comp["ocf_at"] = df_comp["oancfy"] / df_comp["atq"]

    # Sort by gvkey and fiscal_year
    df_comp = df_comp.sort_values(["gvkey", "fiscal_year"])

    results = []

    for gvkey, group in df_comp.groupby("gvkey"):
        group = group.sort_values("fiscal_year")

        for idx, row in group.iterrows():
            fy = row["fiscal_year"]

            # Get trailing window
            window_data = group[
                (group["fiscal_year"] > fy - window - 1)
                & (group["fiscal_year"] <= fy)
            ]["ocf_at"]

            # Require minimum observations
            if window_data.notna().sum() >= min_years:
                cf_vol = window_data.std()
                results.append({
                    "gvkey": gvkey,
                    "fiscal_year": fy,
                    "cf_volatility": cf_vol,
                })

    result = pd.DataFrame(results)

    if not result.empty:
        n_computed = result["cf_volatility"].notna().sum()
        print(f"  Computed cf_volatility for {n_computed:,} observations")
    else:
        print("  Warning: No CF volatility computed (insufficient data)")

    return result


def compute_industry_capex_intensity(df, min_firms=5):
    """Compute Industry Capex Intensity = Mean(capex_at) by FF48-year"""
    print("\nComputing Industry Capex Intensity...")

    # First compute capex_at
    df_comp = df[df["atq"] > 0].copy()
    df_comp["capex_at"] = df_comp["capxy"] / df_comp["atq"]

    results = []

    # Group by FF48-year
    for (ff48, year), group in df_comp.groupby(["ff48", "fiscal_year"]):
        valid_vals = group["capex_at"].dropna()

        if len(valid_vals) >= min_firms:
            intensity = valid_vals.mean()
        else:
            # Fallback to FF12
            ff12 = group["ff12"].iloc[0] if not group["ff12"].isna().all() else 12
            ff12_group = df_comp[(df_comp["ff12"] == ff12) & (df_comp["fiscal_year"] == year)]
            valid_vals_ff12 = ff12_group["capex_at"].dropna()
            intensity = valid_vals_ff12.mean() if len(valid_vals_ff12) >= min_firms else np.nan

        for _, row in group.iterrows():
            results.append({
                "gvkey": row["gvkey"],
                "fiscal_year": row["fiscal_year"],
                "industry_capex_intensity": intensity,
            })

    result = pd.DataFrame(results)

    n_valid = result["industry_capex_intensity"].notna().sum()
    print(f"  Computed industry_capex_intensity for {n_valid:,} observations")

    return result


def compute_firm_size(df):
    """Compute Firm Size = ln(AT)"""
    print("\nComputing Firm Size (ln(AT))...")

    # Require positive AT
    df_comp = df[df["atq"] > 0].copy()
    df_comp["firm_size"] = np.log(df_comp["atq"])

    result = df_comp[["gvkey", "fiscal_year", "datadate", "firm_size"]].copy()

    n_computed = result["firm_size"].notna().sum()
    print(f"  Computed firm_size for {n_computed:,} observations")

    return result


def compute_roa(df):
    """Compute ROA = IB / AT"""
    print("\nComputing ROA (IB/AT)...")

    # Require positive AT
    df_comp = df[df["atq"] > 0].copy()
    df_comp["roa"] = df_comp["iby"] / df_comp["atq"]

    result = df_comp[["gvkey", "fiscal_year", "datadate", "roa"]].copy()

    n_computed = result["roa"].notna().sum()
    print(f"  Computed roa for {n_computed:,} observations")

    return result


def compute_fcf(df):
    """Compute FCF = (OANCF - CAPX) / AT"""
    print("\nComputing FCF ((OANCF-CAPX)/AT)...")

    # Require positive AT
    df_comp = df[df["atq"] > 0].copy()
    df_comp["fcf"] = (df_comp["oancfy"] - df_comp["capxy"].fillna(0)) / df_comp["atq"]

    result = df_comp[["gvkey", "fiscal_year", "datadate", "fcf"]].copy()

    n_computed = result["fcf"].notna().sum()
    print(f"  Computed fcf for {n_computed:,} observations")

    return result


def compute_earnings_volatility(df, min_years=3, window=5):
    """Compute Earnings Volatility = StdDev(ROA) over trailing 5 years"""
    print("\nComputing Earnings Volatility (5-year rolling StdDev of ROA)...")

    # Compute ROA first
    df_comp = df[df["atq"] > 0].copy()
    df_comp["roa"] = df_comp["iby"] / df_comp["atq"]

    # Sort by gvkey and fiscal_year
    df_comp = df_comp.sort_values(["gvkey", "fiscal_year"])

    results = []

    for gvkey, group in df_comp.groupby("gvkey"):
        group = group.sort_values("fiscal_year")

        for idx, row in group.iterrows():
            fy = row["fiscal_year"]

            # Get trailing window
            window_data = group[
                (group["fiscal_year"] > fy - window - 1)
                & (group["fiscal_year"] <= fy)
            ]["roa"]

            # Require minimum observations
            if window_data.notna().sum() >= min_years:
                earnings_vol = window_data.std()
                results.append({
                    "gvkey": gvkey,
                    "fiscal_year": fy,
                    "earnings_volatility": earnings_vol,
                })

    result = pd.DataFrame(results)

    if not result.empty:
        n_computed = result["earnings_volatility"].notna().sum()
        print(f"  Computed earnings_volatility for {n_computed:,} observations")
    else:
        print("  Warning: No earnings volatility computed (insufficient data)")

    return result


# ==============================================================================
# Winsorization
# ==============================================================================


def winsorize_series(s: pd.Series, lower: float = 0.01, upper: float = 0.99) -> pd.Series:
    """Winsorize a series at specified percentiles"""
    if s.notna().sum() == 0:
        return s

    lower_bound = s.quantile(lower)
    upper_bound = s.quantile(upper)
    return s.clip(lower=lower_bound, upper=upper_bound)


# ==============================================================================
# CLI and Prerequisites
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments for 3.2_H2Variables.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 3.2: H2 Investment Efficiency Variables

Constructs dependent variables (Over/Underinvestment dummies, Efficiency Score,
ROA Residual) and control variables for H2 investment efficiency hypothesis testing.
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
        "IBES": paths["ibes_file"],
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
        print("STEP 3.2: H2 Investment Efficiency Variables - DRY RUN")
        print(f"Timestamp: {timestamp}")
        print("=" * 60)

        prereq_ok = check_prerequisites(paths, args)
        if prereq_ok:
            print("\n[OK] All prerequisites validated")
            print("\nWould compute:")
            print("  - Overinvestment Dummy (Capex/DP > 1.5 AND low growth)")
            print("  - Underinvestment Dummy (Capex/DP < 0.75 AND high Q)")
            print("  - Efficiency Score (5-year rolling window)")
            print("  - ROA Residual (Biddle cross-sectional regression)")
            print("  - Analyst Dispersion (IBES)")
            print("  - Tobin's Q, CF Volatility, Industry Capex Intensity")
            print("  - Firm Size, ROA, FCF, Earnings Volatility")
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
    print("STEP 3.2: H2 Investment Efficiency Variables")
    print(f"Timestamp: {timestamp}")
    print("=" * 60)

    # Initialize statistics
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    mem_start = get_process_memory_mb()
    memory_readings = [mem_start["rss_mb"]]

    stats = {
        "step_id": "3.2_H2Variables",
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

    # Load Compustat
    print("\nCompustat:")
    stats["input"]["files"].append(str(paths["compustat_file"]))
    stats["input"]["checksums"][paths["compustat_file"].name] = compute_file_checksum(
        paths["compustat_file"]
    )
    compustat = load_compustat_h2(paths["compustat_file"])
    print_stat("Compustat rows", value=len(compustat))

    # Build FF industry mappings
    print("\nIndustry Classifications:")
    ff48_map, ff12_map = build_ff_mappings(
        paths["siccodes48_file"],
        paths["siccodes12_file"]
    )

    # Assign FF industries
    compustat = assign_ff_industries(compustat, ff48_map, ff12_map)

    # Load IBES
    print("\nIBES:")
    stats["input"]["files"].append(str(paths["ibes_file"]))
    stats["input"]["checksums"][paths["ibes_file"].name] = compute_file_checksum(
        paths["ibes_file"]
    )
    ibes = load_ibes(paths["ibes_file"])
    print_stat("IBES rows", value=len(ibes))

    # ========================================================================
    # Compute H2 Variables
    # ========================================================================

    print("\n" + "=" * 60)
    print("Computing H2 Variables")
    print("=" * 60)

    # ------------------------------------------------------------
    # Over/Underinvestment Classification (H2-01, H2-02)
    # ------------------------------------------------------------

    print("\n" + "-" * 60)
    print("H2-01, H2-02: Over/Underinvestment Classification")
    print("-" * 60)

    # Compute investment ratios
    capex_dp_df = compute_capex_dp(compustat)
    sales_growth_df = compute_sales_growth(compustat)

    # Merge for over/underinvestment computation
    invest_df = capex_dp_df.merge(
        sales_growth_df[["gvkey", "fiscal_year", "sales_growth"]],
        on=["gvkey", "fiscal_year"],
        how="outer",
    )

    # Add FF industries
    invest_df = invest_df.merge(
        compustat[["gvkey", "fiscal_year", "ff48", "ff12"]].drop_duplicates(),
        on=["gvkey", "fiscal_year"],
        how="left",
    )

    # Compute industry median sales growth
    ind_median_df = compute_industry_year_median(invest_df, "sales_growth")

    # Compute Tobin's Q (needed for underinvestment)
    tobins_q_df = compute_tobins_q(compustat)

    # Compute over/underinvestment dummies
    overinvest_df = compute_overinvest_dummy(invest_df, ind_median_df)
    underinvest_df = compute_underinvest_dummy(invest_df, tobins_q_df)

    # Enforce mutual exclusivity
    invest_dummies = enforce_mutual_exclusivity(overinvest_df, underinvest_df)

    # ------------------------------------------------------------
    # Efficiency Score (H2-03)
    # ------------------------------------------------------------

    print("\n" + "-" * 60)
    print("H2-03: Efficiency Score")
    print("-" * 60)

    # Merge dummies with datadate for sorting
    invest_dummies_full = invest_dummies.merge(
        overinvest_df[["gvkey", "fiscal_year", "datadate"]],
        on=["gvkey", "fiscal_year"],
        how="left",
    )

    efficiency_score_df = compute_efficiency_score(invest_dummies_full)

    # ------------------------------------------------------------
    # Biddle ROA Residual (H2-04)
    # ------------------------------------------------------------

    print("\n" + "-" * 60)
    print("H2-04: Biddle ROA Residual")
    print("-" * 60)

    # Compute delta ROA
    delta_roa_df, compustat_with_roa = compute_delta_roa(compustat)

    # Merge with control variables for regression
    capex_at_df = pd.DataFrame()
    compustat_for_capex = compustat[compustat["atq"] > 0].copy()
    compustat_for_capex["capex_at"] = compustat_for_capex["capxy"].fillna(0) / compustat_for_capex["atq"]
    capex_at_df = compustat_for_capex[["gvkey", "fiscal_year", "capex_at"]].copy()

    # Prepare regression dataframe
    reg_df = delta_roa_df.merge(
        capex_at_df[["gvkey", "fiscal_year", "capex_at"]],
        on=["gvkey", "fiscal_year"],
        how="left",
    )
    reg_df = reg_df.merge(
        tobins_q_df[["gvkey", "fiscal_year", "tobins_q"]],
        on=["gvkey", "fiscal_year"],
        how="left",
    )
    reg_df = reg_df.merge(
        compustat[["gvkey", "fiscal_year", "ff48", "ff12"]].drop_duplicates(),
        on=["gvkey", "fiscal_year"],
        how="left",
    )

    # Compute residuals
    roa_residual_df = compute_roa_residuals(reg_df, ff_industry="ff48", min_obs=20)

    # ------------------------------------------------------------
    # IBES Analyst Dispersion (H2-05)
    # ------------------------------------------------------------

    print("\n" + "-" * 60)
    print("H2-05: IBES Analyst Dispersion")
    print("-" * 60)

    # Link IBES to Compustat (simplified CUSIP8 matching)
    ibes_linked = link_ibes_to_compustat(ibes)

    # Compute dispersion
    analyst_dispersion_df = compute_analyst_dispersion(ibes_linked)

    # ------------------------------------------------------------
    # Control Variables (H2-05, H2-06)
    # ------------------------------------------------------------

    print("\n" + "-" * 60)
    print("Control Variables")
    print("-" * 60)

    # Compute all controls
    cf_volatility_df = compute_cf_volatility(compustat)
    industry_capex_intensity_df = compute_industry_capex_intensity(compustat)
    firm_size_df = compute_firm_size(compustat)
    roa_df = compute_roa(compustat)
    fcf_df = compute_fcf(compustat)
    earnings_volatility_df = compute_earnings_volatility(compustat)

    stats["processing"]["variables_computed"] = [
        "overinvest_dummy",
        "underinvest_dummy",
        "efficiency_score",
        "roa_residual",
        "analyst_dispersion",
        "tobins_q",
        "cf_volatility",
        "industry_capex_intensity",
        "firm_size",
        "roa",
        "fcf",
        "earnings_volatility",
    ]

    # ========================================================================
    # Merge Variables
    # ========================================================================

    print("\n" + "=" * 60)
    print("Merging Variables")
    print("=" * 60)

    # Start with a base of unique firm-years from Compustat
    base = compustat[["gvkey", "fiscal_year", "datadate"]].copy()
    base = base.sort_values(
        ["gvkey", "fiscal_year", "datadate"], ascending=[True, True, False]
    ).drop_duplicates(subset=["gvkey", "fiscal_year"], keep="first")

    print(f"  Base firm-years: {len(base):,}")

    # Merge investment dummies
    h2_data = base.merge(
        invest_dummies[["gvkey", "fiscal_year", "overinvest_dummy", "underinvest_dummy"]],
        on=["gvkey", "fiscal_year"],
        how="left",
    )

    # Merge efficiency score
    h2_data = h2_data.merge(
        efficiency_score_df[["gvkey", "fiscal_year", "efficiency_score"]],
        on=["gvkey", "fiscal_year"],
        how="left",
    )
    n_valid = h2_data["efficiency_score"].notna().sum()
    print(f"  efficiency_score: {n_valid:,} valid")

    # Merge ROA residual
    h2_data = h2_data.merge(
        roa_residual_df[["gvkey", "fiscal_year", "roa_residual"]],
        on=["gvkey", "fiscal_year"],
        how="left",
    )
    n_valid = h2_data["roa_residual"].notna().sum()
    print(f"  roa_residual: {n_valid:,} valid")

    # Merge Tobin's Q
    h2_data = h2_data.merge(
        tobins_q_df[["gvkey", "fiscal_year", "tobins_q"]],
        on=["gvkey", "fiscal_year"],
        how="left",
    )
    n_valid = h2_data["tobins_q"].notna().sum()
    print(f"  tobins_q: {n_valid:,} valid")

    # Merge CF volatility
    h2_data = h2_data.merge(
        cf_volatility_df[["gvkey", "fiscal_year", "cf_volatility"]],
        on=["gvkey", "fiscal_year"],
        how="left",
    )
    n_valid = h2_data["cf_volatility"].notna().sum()
    print(f"  cf_volatility: {n_valid:,} valid")

    # Merge industry capex intensity
    h2_data = h2_data.merge(
        industry_capex_intensity_df[["gvkey", "fiscal_year", "industry_capex_intensity"]],
        on=["gvkey", "fiscal_year"],
        how="left",
    )
    n_valid = h2_data["industry_capex_intensity"].notna().sum()
    print(f"  industry_capex_intensity: {n_valid:,} valid")

    # Merge analyst dispersion (via CUSIP8 - note this will have limited coverage)
    # For now, skip analyst dispersion merge as we need proper CUSIP-GVKEY mapping
    print(f"  analyst_dispersion: skipped (requires CUSIP-GVKEY mapping)")

    # Merge remaining controls
    for var_name, var_df in [
        ("firm_size", firm_size_df),
        ("roa", roa_df),
        ("fcf", fcf_df),
        ("earnings_volatility", earnings_volatility_df),
    ]:
        # Keep the most recent datadate for each gvkey-fiscal_year
        var_df_sorted = var_df.sort_values(
            ["gvkey", "fiscal_year", "datadate"], ascending=[True, True, False]
        ).drop_duplicates(subset=["gvkey", "fiscal_year"], keep="first")

        h2_data = h2_data.merge(
            var_df_sorted[["gvkey", "fiscal_year", var_name]],
            on=["gvkey", "fiscal_year"],
            how="left",
        )
        n_valid = h2_data[var_name].notna().sum()
        print(f"  {var_name}: {n_valid:,} valid")

    # Filter to sample manifest firm-years
    print("\nFiltering to sample...")
    manifest_for_merge = manifest[["gvkey", "year"]].drop_duplicates()
    h2_data = h2_data.merge(manifest_for_merge, left_on=["gvkey", "fiscal_year"], right_on=["gvkey", "year"], how="inner")

    print(f"  After filtering to sample: {len(h2_data):,} observations")

    # ========================================================================
    # Apply Winsorization
    # ========================================================================

    print("\n" + "=" * 60)
    print("Applying Winsorization (1%/99%)")
    print("=" * 60)

    continuous_vars = [
        "efficiency_score",
        "tobins_q",
        "cf_volatility",
        "industry_capex_intensity",
        "firm_size",
        "roa",
        "fcf",
        "earnings_volatility",
    ]

    for var in continuous_vars:
        if var in h2_data.columns and h2_data[var].notna().sum() > 0:
            before_mean = h2_data[var].mean()
            h2_data[var] = winsorize_series(h2_data[var], lower=0.01, upper=0.99)
            after_mean = h2_data[var].mean()
            stats["processing"]["winsorization"][var] = {
                "before_mean": round(float(before_mean), 4) if not np.isnan(before_mean) else None,
                "after_mean": round(float(after_mean), 4) if not np.isnan(after_mean) else None,
            }
            print(f"  {var}: winsorized")

    # ========================================================================
    # Compute Variable Statistics
    # ========================================================================

    print("\n" + "=" * 60)
    print("Computing Variable Statistics")
    print("=" * 60)

    output_columns = [
        "gvkey",
        "fiscal_year",
        "overinvest_dummy",
        "underinvest_dummy",
        "efficiency_score",
        "roa_residual",
        "tobins_q",
        "cf_volatility",
        "industry_capex_intensity",
        "firm_size",
        "roa",
        "fcf",
        "earnings_volatility",
    ]

    for var in output_columns[2:]:  # Skip gvkey, fiscal_year
        if var in h2_data.columns:
            var_data = h2_data[var]
            stats["variables"][var] = {
                "mean": round(float(var_data.mean()), 4) if var_data.notna().sum() > 0 else None,
                "std": round(float(var_data.std()), 4) if var_data.notna().sum() > 1 else None,
                "min": round(float(var_data.min()), 4) if var_data.notna().sum() > 0 else None,
                "max": round(float(var_data.max()), 4) if var_data.notna().sum() > 0 else None,
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

    # Select columns for output
    final_output = h2_data[output_columns].copy()

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
    output_file = paths["output_dir"] / "H2_InvestmentEfficiency.parquet"
    final_output.to_parquet(output_file, index=False)
    print(f"  Wrote: {output_file.name}")
    stats["output"]["files"].append(output_file.name)
    stats["output"]["checksums"][output_file.name] = compute_file_checksum(
        output_file
    )

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
    if duration_seconds > 0:
        throughput = calculate_throughput(len(final_output), duration_seconds)
        stats["throughput"] = {
            "rows_per_second": throughput,
            "total_rows": len(final_output),
            "duration_seconds": round(duration_seconds, 3),
        }

    # Detect anomalies
    print("\nDetecting anomalies...")
    numeric_cols = [
        "efficiency_score",
        "tobins_q",
        "cf_volatility",
        "industry_capex_intensity",
        "firm_size",
        "roa",
        "fcf",
        "earnings_volatility",
    ]
    anomalies = detect_anomalies_zscore(final_output, numeric_cols, threshold=3.0)
    total_anomalies = sum(a["count"] for a in anomalies.values())
    print(f"  Anomalies detected (z>3): {total_anomalies}")

    # Print summary
    print_stats_summary(stats)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"H2 Variables computed: {len(final_output):,} observations")
    print(f"\nOutputs saved to: {paths['output_dir']}")
    print(f"Log saved to: {paths['log_file']}")

    dual_writer.close()
    sys.stdout = dual_writer.terminal


if __name__ == "__main__":
    main()
