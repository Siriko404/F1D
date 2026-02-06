#!/usr/bin/env python3
"""
==============================================================================
STEP 4.7: H7 Illiquidity Regression
==============================================================================
ID: 4.7_H7IlliquidityRegression
Description: Panel regressions for H7 (Speech Uncertainty -> Stock Illiquidity).
             Tests whether vague managers face higher stock illiquidity.

Model Specification:
    Illiquidity_{t+1} = beta0 + beta1*Uncertainty_t + gamma*Controls
                        + Firm FE + Year FE + epsilon

Hypothesis Tests:
    H7a: beta1 > 0 (Higher uncertainty -> Higher illiquidity)

Econometric Standards:
    - Fixed effects: Firm + Year (Cameron & Miller 2015)
    - SE: Clustered at firm level (Petersen 2009)
    - DV: Forward-looking (t+1) for causal interpretation

Inputs:
    - 4_Outputs/3_Financial_V2/latest/H7_Illiquidity.parquet

Outputs:
    - 4_Outputs/4_Econometric_V2/{timestamp}/H7_Regression_Results.parquet
    - 4_Outputs/4_Econometric_V2/{timestamp}/H7_RESULTS.md
    - 4_Outputs/4_Econometric_V2/{timestamp}/stats.json

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
import json
import time
import subprocess

# Add parent directory to sys.path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Import shared utilities
from shared.path_utils import (
    validate_output_path,
    ensure_output_dir,
    validate_input_file,
    get_latest_output_dir,
)

from shared.observability_utils import (
    DualWriter,
    compute_file_checksum,
    print_stat,
    analyze_missing_values,
    print_stats_summary,
    save_stats,
    get_process_memory_mb,
    calculate_throughput,
)

from shared.panel_ols import run_panel_ols
from shared.diagnostics import check_multicollinearity, MulticollinearityError

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


def get_git_sha():
    """Get current git commit SHA for reproducibility"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


# Uncertainty measures (4 total available in H7_Illiquidity.parquet)
# Note: Weak Modal variables not available in H7 data
UNCERTAINTY_MEASURES = [
    'Manager_QA_Uncertainty_pct',
    'CEO_QA_Uncertainty_pct',
    'Manager_Pres_Uncertainty_pct',
    'CEO_Pres_Uncertainty_pct',
]

# Control variables
CONTROL_VARS = [
    'Volatility', 'StockRet'
]

# Regression specifications
SPECS = {
    'primary': {'entity_effects': True, 'time_effects': True, 'cluster_entity': True},
    'firm_only': {'entity_effects': True, 'time_effects': False, 'cluster_entity': True},
    'pooled': {'entity_effects': False, 'time_effects': False, 'cluster_entity': True},
    'double_cluster': {'entity_effects': True, 'time_effects': True, 'cluster_entity': True, 'cluster_time': True},
}

# =============================================================================
# Robustness Configuration
# =============================================================================

ROBUSTNESS_CONFIG = {
    'alternative_dvs': {
        'roll_spread': 'Roll (1984) implicit spread',
        'bidask_spread': 'Bid-ask spread (if available)',
    },
    'alternative_specs': {
        'firm_only': {'entity_effects': True, 'time_effects': False, 'cluster_entity': True},
        'pooled': {'entity_effects': False, 'time_effects': False, 'cluster_entity': True},
        'double_cluster': {'entity_effects': True, 'time_effects': True, 'cluster_entity': True, 'cluster_time': True},
    },
    'alternative_ivs': {
        'ceo_only': ['CEO_QA_Uncertainty_pct', 'CEO_Pres_Uncertainty_pct'],
        'presentation_only': ['Manager_Pres_Uncertainty_pct', 'CEO_Pres_Uncertainty_pct'],
        'qa_only': ['Manager_QA_Uncertainty_pct', 'CEO_QA_Uncertainty_pct'],
    },
    'timing_tests': {
        'concurrent': 0,   # Uncertainty_t -> Illiquidity_t
        'forward': -1,     # Uncertainty_t -> Illiquidity_{t+1} (primary)
        'lead': -2,        # Uncertainty_t -> Illiquidity_{t+2}
    },
}

# ==============================================================================
# Path Setup
# ==============================================================================


def setup_paths(config, timestamp):
    """Set up all required paths using get_latest_output_dir"""
    root = Path(__file__).parent.parent.parent

    # Resolve H7 illiquidity directory
    h7_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H7_Illiquidity.parquet",
    )

    paths = {
        "root": root,
        "h7_dir": h7_dir,
    }

    # Output directory - organize by script name
    output_base = root / "4_Outputs" / "4_Econometric_V2" / "4.7_H7IlliquidityRegression"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory - organize by script name
    log_base = root / "3_Logs" / "4_Econometric_V2" / "4.7_H7IlliquidityRegression"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H7.log"

    return paths


# ==============================================================================
# Data Loading and Preparation
# ==============================================================================


def load_data(h7_dir, dw=None):
    """
    Load H7 Illiquidity data.

    Expects H7_Illiquidity.parquet with columns:
    - gvkey, year
    - amihud_lag1, log_amihud_lag1, roll_spread_lag1 (DVs)
    - UNCERTAINTY_MEASURES (IVs)
    - Volatility, StockRet (controls)
    - trading_days
    """
    h7_file = h7_dir / "H7_Illiquidity.parquet"
    if not h7_file.exists():
        raise FileNotFoundError(f"H7_Illiquidity.parquet not found in {h7_dir}")

    validate_input_file(h7_file, must_exist=True)
    df = pd.read_parquet(h7_file)

    if dw:
        dw.write(f"  Loaded H7 data: {len(df):,} rows\n")
        dw.write(f"    Columns: {df.columns.tolist()}\n")

    # Ensure gvkey is string and zero-padded
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    return df


def prepare_regression_data(df, uncertainty_vars, control_vars, dv_col='amihud_lag1',
                           min_obs_per_firm=3, dw=None):
    """
    Prepare data for regression analysis.

    Steps:
    1. Aggregate duplicates (mean) to get one row per gvkey-year
    2. Set MultiIndex (gvkey, year) for panel data
    3. Filter to firms with minimum observations
    4. Drop rows with missing DV or IV
    5. Keep rows with missing controls (will be handled by FE)
    """
    df_work = df.copy()

    # Aggregate duplicates by gvkey-year (take mean)
    if dw:
        before_agg = len(df_work)

    # Group by gvkey and year, take mean of all numeric columns
    agg_cols = [dv_col] + uncertainty_vars + control_vars + ['trading_days']
    df_work = df_work.groupby(['gvkey', 'year'], as_index=False)[agg_cols].mean()

    if dw:
        after_agg = len(df_work)
        dw.write(f"  Aggregated {before_agg:,} -> {after_agg:,} rows (removed duplicates)\n")

    # Set MultiIndex for panel data
    df_work = df_work.set_index(['gvkey', 'year'])
    df_work = df_work.sort_index()

    # Check required columns
    required_cols = [dv_col] + uncertainty_vars
    missing = set(required_cols) - set(df_work.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Drop rows with missing DV
    before_drop = len(df_work)
    df_work = df_work[df_work[dv_col].notna()]
    after_drop = len(df_work)

    if dw:
        dw.write(f"  Dropped {before_drop - after_drop:,} rows with missing DV\n")

    # Drop rows with missing primary IV (will do for each IV separately in regression loop)
    # For now, just keep all and let regression handle missingness per IV

    # Filter to firms with minimum observations
    firm_obs = df_work.index.get_level_values('gvkey').value_counts()
    firms_with_min_obs = firm_obs[firm_obs >= min_obs_per_firm].index
    df_work = df_work[df_work.index.get_level_values('gvkey').isin(firms_with_min_obs)]

    if dw:
        n_firms = df_work.index.get_level_values('gvkey').nunique()
        n_obs = len(df_work)
        year_min = df_work.index.get_level_values('year').min()
        year_max = df_work.index.get_level_values('year').max()
        dw.write(f"  Final sample: {n_obs:,} obs, {n_firms} firms, {year_min}-{year_max}\n")

    return df_work


def validate_data(df, dv_col, uncertainty_vars, control_vars, dw=None):
    """
    Validate data quality and print summary statistics.
    """
    if dw:
        dw.write("\n  Data validation:\n")

        # Sample size checks
        n_obs = len(df)
        n_firms = df.index.get_level_values('gvkey').nunique()
        years = df.index.get_level_values('year').unique()

        dw.write(f"    N (observations): {n_obs:,}\n")
        dw.write(f"    N (firms): {n_firms:,}\n")
        dw.write(f"    Years: {len(years)} ({min(years)}-{max(years)})\n")

        # Check N >= 10,000
        if n_obs >= 10000:
            dw.write(f"    Sample size: PASS (>= 10,000)\n")
        else:
            dw.write(f"    Sample size: WARNING (< 10,000)\n")

        # Check N_firms >= 1,000
        if n_firms >= 1000:
            dw.write(f"    Firm count: PASS (>= 1,000)\n")
        else:
            dw.write(f"    Firm count: WARNING (< 1,000)\n")

        # DV distribution
        dv_stats = df[dv_col].describe()
        dw.write(f"\n    DV ({dv_col}) distribution:\n")
        dw.write(f"      Mean: {dv_stats['mean']:.6f}\n")
        dw.write(f"      Std: {dv_stats['std']:.6f}\n")
        dw.write(f"      Min: {dv_stats['min']:.6f}\n")
        dw.write(f"      Max: {dv_stats['max']:.6f}\n")

        # Missingness
        dw.write(f"\n    Missing values:\n")
        for var in [dv_col] + uncertainty_vars + control_vars:
            if var in df.columns:
                n_missing = df[var].isna().sum()
                pct_missing = n_missing / len(df) * 100
                dw.write(f"      {var}: {n_missing:,} ({pct_missing:.1f}%)\n")


# =============================================================================
# Robustness Helper Functions
# =============================================================================


def create_alternative_dvs(df, dw=None):
    """
    Create alternative dependent variables for robustness testing.

    Creates forward-looking versions of alternative illiquidity measures:
    - Roll (1984) spread: roll_spread_fwd
    - Bid-ask spread (if available): bidask_spread_fwd

    Args:
        df: Panel data with illiquidity measures
        dw: DualWriter for logging

    Returns:
        DataFrame with additional DV columns
    """
    df_work = df.copy()

    # Reset index temporarily to work with columns
    if isinstance(df_work.index, pd.MultiIndex):
        df_work = df_work.reset_index()

    # Roll spread (should exist from variable construction)
    if 'roll_spread' in df_work.columns:
        df_work['roll_spread_fwd'] = df_work.groupby('gvkey')['roll_spread'].shift(-1)
        if dw:
            n_roll = df_work['roll_spread_fwd'].notna().sum()
            dw.write(f"  Created roll_spread_fwd: {n_roll:,} observations\n")
    else:
        if dw:
            dw.write(f"  WARNING: roll_spread not in data\n")

    # Bid-ask spread (if available)
    if 'bidask_spread' in df_work.columns:
        df_work['bidask_spread_fwd'] = df_work.groupby('gvkey')['bidask_spread'].shift(-1)
        if dw:
            n_bidask = df_work['bidask_spread_fwd'].notna().sum()
            dw.write(f"  Created bidask_spread_fwd: {n_bidask:,} observations\n")
    else:
        if dw:
            dw.write(f"  NOTE: bidask_spread not in data (optional DV)\n")

    return df_work


def create_timing_variants(df, dv_base='amihud_illiquidity', lags=[0, -1, -2], dw=None):
    """
    Create DV variants for different timing assumptions.

    Args:
        df: Panel data (should have gvkey in index or columns)
        dv_base: Base DV column name (current period illiquidity)
        lags: List of lag values (0 = concurrent, -1 = forward, -2 = lead)
        dw: DualWriter for logging

    Returns:
        dict with timing_name -> (df, dv_col)
    """
    # Work with copy
    df_work = df.copy()

    # Reset index if MultiIndex to access gvkey easily
    was_multiindex = isinstance(df_work.index, pd.MultiIndex)
    if was_multiindex:
        index_names = df_work.index.names
        df_work = df_work.reset_index()

    timing_variants = {}
    timing_names = {0: 'concurrent', -1: 'forward', -2: 'lead'}

    for lag in lags:
        df_lag = df_work.copy()

        if lag == 0:
            dv_name = dv_base
            # No shifting needed for concurrent
            # Just remove rows with missing DV
        else:
            dv_name = f'{dv_base}_lag{abs(lag)}'
            df_lag[dv_name] = df_lag.groupby('gvkey')[dv_base].shift(lag)

        # Remove missing DV
        df_lag = df_lag[df_lag[dv_name].notna()]

        # Set back MultiIndex if needed
        if was_multiindex:
            df_lag = df_lag.set_index(index_names)

        timing_variants[timing_names[lag]] = (df_lag, dv_name)

        if dw:
            n_obs = len(df_lag)
            dw.write(f"  Timing {timing_names[lag]} ({dv_name}): {n_obs:,} observations\n")

    return timing_variants


def run_h7_regression(df, uncertainty_var, dv_col='amihud_lag1',
                     controls=None, spec_name='primary', spec_config=None,
                     vif_threshold=5.0, dv_type='Amihud (2002)',
                     iv_type=None, timing=None, dw=None):
    """
    Run single H7 regression.

    Specification:
        Illiquidity_{t+1} = beta0 + beta1*Uncertainty + Controls + FE

    Args:
        df: Panel data with MultiIndex (gvkey, year)
        uncertainty_var: Name of uncertainty IV
        dv_col: Name of dependent variable
        controls: List of control variable names
        spec_name: Specification name for reporting
        spec_config: Dictionary with entity_effects, time_effects, cluster_entity
        dv_type: Label for dependent variable type (for robustness tracking)
        iv_type: Label for IV type (for robustness tracking)
        timing: Label for timing assumption (for robustness tracking)

    Returns:
        dict with coefficients, SEs, p-values, diagnostics
    """
    if spec_config is None:
        spec_config = SPECS['primary']

    if controls is None:
        controls = []

    # Reset index to preserve gvkey and year as columns
    # run_panel_ols will set the MultiIndex itself
    df_work = df.reset_index()

    # Prepare formula variables
    iv_vars = [uncertainty_var]
    # Only add controls that exist in df and are not all NA
    for ctl in controls:
        if ctl in df_work.columns and df_work[ctl].notna().sum() > 0:
            iv_vars.append(ctl)

    # Create working dataframe with only needed variables
    needed_cols = ['gvkey', 'year', dv_col] + iv_vars
    model_df = df_work[needed_cols].copy()

    # Drop rows with missing IV
    model_df = model_df[model_df[uncertainty_var].notna()]

    # For controls, we can allow some missingness (FE will handle)
    # But for regression, drop rows with all controls missing
    if controls:
        # Check if any control has data
        has_control_data = False
        for ctl in controls:
            if ctl in model_df.columns:
                if model_df[ctl].notna().sum() > 0:
                    has_control_data = True
                    break

        if has_control_data:
            # Drop rows where all included controls are missing
            control_cols = [c for c in controls if c in model_df.columns]
            model_df['any_control'] = model_df[control_cols].notna().any(axis=1)
            model_df = model_df[model_df['any_control']]
            model_df = model_df.drop(columns=['any_control'])

    # Drop any rows with missing DV or IV values
    model_df = model_df.dropna(subset=[dv_col, uncertainty_var])

    # Sort for panel regression
    model_df = model_df.sort_values(['gvkey', 'year'])

    # Run panel OLS
    try:
        cluster_cols = ['gvkey']
        if spec_config.get('cluster_time', False):
            cluster_cols = ['gvkey', 'year']

        result = run_panel_ols(
            df=model_df,
            dependent=dv_col,
            exog=iv_vars,
            entity_col='gvkey',
            time_col='year',
            entity_effects=spec_config.get('entity_effects', True),
            time_effects=spec_config.get('time_effects', True),
            cov_type='clustered',
            cluster_cols=cluster_cols,
            check_collinearity=False,  # Check manually
            vif_threshold=vif_threshold,
        )
    except Exception as e:
        if dw:
            dw.write(f"    ERROR in regression: {e}\n")
        return {
            'uncertainty_var': uncertainty_var,
            'spec': spec_name,
            'error': str(e),
            'coefficient': np.nan,
            'se': np.nan,
            'p_two_sided': np.nan,
            'p_one_sided': np.nan,
            'n': 0,
            'n_firms': 0,
            'r2_within': np.nan,
            'r2': np.nan,
            'f_statistic': np.nan,
            'f_pvalue': np.nan,
            'entity_effects': False,
            'time_effects': False,
            'warnings': [],
            'dv_type': dv_type,
            'iv_type': iv_type,
            'timing': timing,
        }

    # Extract results for uncertainty variable
    coeffs_df = result['coefficients']
    summary = result['summary']

    coef = np.nan
    se = np.nan
    p_two = np.nan
    p_one = np.nan

    if uncertainty_var in coeffs_df.index:
        coef = coeffs_df.loc[uncertainty_var, 'Coefficient']
        se = coeffs_df.loc[uncertainty_var, 'Std. Error']
        p_two = result['model'].pvalues.get(uncertainty_var, np.nan)

        # One-tailed test: H7a: beta1 > 0 (uncertainty increases illiquidity)
        if not np.isnan(p_two) and not np.isnan(coef):
            if coef > 0:
                p_one = p_two / 2
            else:
                p_one = 1 - p_two / 2

    return {
        'uncertainty_var': uncertainty_var,
        'spec': spec_name,
        'coefficient': coef,
        'se': se,
        'p_two_sided': p_two,
        'p_one_sided': p_one,
        'n': summary['nobs'],
        'n_firms': model_df['gvkey'].nunique(),
        'r2_within': summary.get('rsquared_within', None),
        'r2': summary['rsquared'],
        'f_statistic': summary.get('f_statistic', None),
        'f_pvalue': summary.get('f_pvalue', None),
        'entity_effects': summary['entity_effects'],
        'time_effects': summary['time_effects'],
        'warnings': result.get('warnings', []),
        'dv_type': dv_type,
        'iv_type': iv_type,
        'timing': timing,
    }


def run_all_h7_regressions(df, uncertainty_measures, specs, control_vars,
                          dv_col='amihud_lag1', vif_threshold=5.0, dw=None):
    """
    Run all H7 regressions: 6 uncertainty measures x 4 specifications = 24 total.

    Returns list of regression result dictionaries.
    """
    results = []

    for uncertainty_var in uncertainty_measures:
        for spec_name, spec_config in specs.items():
            if dw:
                dw.write(f"\n  Running: {uncertainty_var} x {spec_name}\n")

            result = run_h7_regression(
                df, uncertainty_var, dv_col, control_vars,
                spec_name, spec_config, vif_threshold, dw
            )

            results.append(result)

            if dw:
                if 'error' not in result:
                    dw.write(f"    N={result['n']}, R2w={result['r2_within']:.4f}, "
                            f"beta={result['coefficient']:.6f} (p1={result['p_one_sided']:.4f})\n")
                else:
                    dw.write(f"    ERROR: {result['error']}\n")

    return results


def run_robustness_suite(df, uncertainty_measures, control_vars,
                         vif_threshold=5.0, dw=None):
    """
    Run full robustness suite for H7.

    Dimensions:
    1. Alternative DVs (Roll spread, bid-ask spread)
    2. Alternative specs (Firm only, Pooled, Double-cluster) - uses primary DV
    3. Alternative IVs (CEO-only, Presentation-only, QA-only)
    4. Timing variants (concurrent, forward, lead)

    Args:
        df: Panel data with MultiIndex (gvkey, year)
        uncertainty_measures: List of primary uncertainty IVs
        control_vars: List of control variable names
        vif_threshold: VIF threshold for multicollinearity check
        dw: DualWriter for logging

    Returns:
        List of robustness result dictionaries
    """
    results = []
    df_work = df.copy()

    if dw:
        dw.write("\n=== Robustness Suite ===\n")

    # Dimension 1: Alternative DVs (Roll spread, bid-ask spread)
    if dw:
        dw.write("\n[Dimension 1] Alternative Dependent Variables\n")

    # Check if alternative DVs exist
    alt_dvs = []
    if 'roll_spread' in df_work.columns:
        alt_dvs.append(('roll_spread', 'Roll (1984)'))
    if 'bidask_spread' in df_work.columns:
        alt_dvs.append(('bidask_spread', 'Bid-Ask Spread'))

    for dv_col, dv_label in alt_dvs:
        if dw:
            dw.write(f"  Testing DV: {dv_label}\n")

        # Create forward-looking DV
        if isinstance(df_work.index, pd.MultiIndex):
            df_alt = df_work.reset_index()
        else:
            df_alt = df_work.copy()

        df_alt[f'{dv_col}_fwd'] = df_alt.groupby('gvkey')[dv_col].shift(-1)
        df_alt = df_alt[df_alt[f'{dv_col}_fwd'].notna()]
        df_alt = df_alt.set_index(['gvkey', 'year'])

        for uv in uncertainty_measures:
            if uv not in df_alt.columns:
                continue
            result = run_h7_regression(
                df_alt, uv, f'{dv_col}_fwd', control_vars,
                spec_name='primary',
                spec_config=SPECS['primary'],
                vif_threshold=vif_threshold,
                dv_type=dv_label,
                dw=dw
            )
            if result and 'error' not in result:
                results.append(result)

    # Dimension 2: Alternative specs (use primary DV - already in run_all_h7_regressions)
    # This is handled by the main regression loop with SPECS dict

    # Dimension 3: Alternative IVs
    if dw:
        dw.write("\n[Dimension 2] Alternative Independent Variables\n")

    for iv_type, ivs in ROBUSTNESS_CONFIG['alternative_ivs'].items():
        if dw:
            dw.write(f"  Testing IV type: {iv_type}\n")

        for uv in ivs:
            if uv not in df_work.columns:
                continue
            result = run_h7_regression(
                df_work, uv, 'amihud_lag1', control_vars,
                spec_name='primary',
                spec_config=SPECS['primary'],
                vif_threshold=vif_threshold,
                dv_type='Amihud (2002)',
                iv_type=iv_type,
                dw=dw
            )
            if result and 'error' not in result:
                results.append(result)

    # Dimension 4: Timing variants
    if dw:
        dw.write("\n[Dimension 3] Timing Tests\n")

    # Need to use amihud_illiquidity (current period) to create timing variants
    if 'amihud_illiquidity' in df_work.columns:
        timing_variants = create_timing_variants(
            df_work, 'amihud_illiquidity', [0, -1, -2], dw
        )

        for timing_name, (df_t, dv_col) in timing_variants.items():
            if dw:
                dw.write(f"  Testing timing: {timing_name} ({dv_col})\n")

            for uv in uncertainty_measures:
                if uv not in df_t.columns:
                    continue
                result = run_h7_regression(
                    df_t, uv, dv_col, control_vars,
                    spec_name='primary',
                    spec_config=SPECS['primary'],
                    vif_threshold=vif_threshold,
                    dv_type='Amihud (2002)',
                    timing=timing_name,
                    dw=None  # Suppress verbose output
                )
                if result and 'error' not in result:
                    results.append(result)

    if dw:
        dw.write(f"\nRobustness suite complete: {len(results)} results\n")

    return results


def apply_fdr_correction(results_list, alpha=0.05, dw=None):
    """
    Apply Benjamini-Hochberg FDR correction to p-values.

    Only applies to primary specification results.
    """
    from statsmodels.stats.multitest import multipletests

    # Extract p-values from primary spec results
    primary_results = [r for r in results_list if r['spec'] == 'primary' and 'error' not in r]
    p_values = [r['p_one_sided'] for r in primary_results if not np.isnan(r['p_one_sided'])]

    if not p_values:
        if dw:
            dw.write("\n  No valid p-values for FDR correction\n")
        return results_list

    # Apply FDR
    reject, p_corrected, _, _ = multipletests(p_values, alpha=alpha, method='fdr_bh')

    # Update results
    idx = 0
    for r in results_list:
        if r['spec'] == 'primary' and 'error' not in r and not np.isnan(r['p_one_sided']):
            r['p_fdr'] = p_corrected[idx]
            r['fdr_significant'] = bool(reject[idx])
            idx += 1
        else:
            r['p_fdr'] = np.nan
            r['fdr_significant'] = False

    if dw:
        n_signif = sum(1 for r in results_list if r.get('fdr_significant', False))
        dw.write(f"\n  FDR correction: {n_signif}/{len(primary_results)} significant at alpha={alpha}\n")

    return results_list


# ==============================================================================
# Output Functions
# ==============================================================================


def save_regression_results(results, output_dir, dw=None):
    """
    Save regression results to parquet file.

    Creates DataFrame with columns:
    - uncertainty_var, spec, coefficient, se, p_two_sided, p_one_sided, p_fdr
    - n, n_firms, r2_within, r2, f_statistic, f_pvalue
    - fdr_significant, dv_type, iv_type, timing (for robustness tracking)
    """
    rows = []

    for r in results:
        rows.append({
            'uncertainty_var': r['uncertainty_var'],
            'spec': r['spec'],
            'coefficient': r['coefficient'],
            'se': r['se'],
            't_stat': r['coefficient'] / r['se'] if r.get('se', 0) > 0 else np.nan,
            'p_two_sided': r.get('p_two_sided', np.nan),
            'p_one_sided': r.get('p_one_sided', np.nan),
            'p_fdr': r.get('p_fdr', np.nan),
            'fdr_significant': r.get('fdr_significant', False),
            'n': r.get('n', 0),
            'n_firms': r.get('n_firms', 0),
            'r2_within': r.get('r2_within', np.nan),
            'r2': r.get('r2', np.nan),
            'f_statistic': r.get('f_statistic', np.nan),
            'f_pvalue': r.get('f_pvalue', np.nan),
            'entity_effects': r.get('entity_effects', False),
            'time_effects': r.get('time_effects', False),
            'dv_type': r.get('dv_type', 'Amihud (2002)'),
            'iv_type': r.get('iv_type', None),
            'timing': r.get('timing', None),
        })

    results_df = pd.DataFrame(rows)
    output_path = output_dir / "H7_Regression_Results.parquet"
    results_df.to_parquet(output_path, index=False)

    if dw:
        dw.write(f"\nSaved: {output_path.name} ({len(results_df)} rows)\n")

    return results_df


def generate_results_markdown(results, output_dir, sample_stats, dv_col='amihud_lag1', dw=None):
    """
    Generate human-readable markdown summary of H7 regression results.
    """
    lines = []
    lines.append("# H7 Regression Results: Speech Uncertainty -> Stock Illiquidity")
    lines.append("")
    lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append(f"**Sample:** {sample_stats['n_obs']:,} firm-years, {sample_stats['n_firms']:,} firms")
    lines.append(f"**Period:** {sample_stats['year_min']}-{sample_stats['year_max']}")
    lines.append("")

    # Executive summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("**Hypothesis H7a:** Higher speech uncertainty predicts HIGHER stock illiquidity (beta > 0)")
    lines.append("")

    # Count significant results
    primary_results = [r for r in results if r['spec'] == 'primary' and 'error' not in r]
    fdr_signif = [r for r in primary_results if r.get('fdr_significant', False)]
    raw_signif = [r for r in primary_results if r.get('p_one_sided', 1) < 0.05]

    lines.append(f"**Conclusion:** ",)
    if len(fdr_signif) >= 4:  # Strong support
        lines.append("SUPPORTED - Uncertainty significantly predicts illiquidity")
    elif len(fdr_signif) >= 2:  # Moderate support
        lines.append("PARTIALLY SUPPORTED - Some uncertainty measures predict illiquidity")
    elif len(raw_signif) >= 2:
        lines.append("WEAK SUPPORT - Effects significant before FDR correction")
    else:
        lines.append("NOT SUPPORTED - No significant effects of uncertainty on illiquidity")

    lines.append("")
    lines.append(f"- Primary spec: {len(raw_signif)}/6 measures significant (p < 0.05, one-tailed)")
    lines.append(f"- After FDR correction: {len(fdr_signif)}/6 measures significant")
    lines.append("")

    # Primary specification results table
    lines.append("## Primary Specification Results")
    lines.append("")
    lines.append("Model: PanelOLS with Firm + Year FE, firm-clustered SE")
    lines.append("")
    lines.append("| Uncertainty Measure | Beta | SE | t-stat | p (one-tailed) | FDR | Significant? |")
    lines.append("|---|---|---|---|---|---|---|")

    for r in primary_results:
        var = r['uncertainty_var']
        beta = r['coefficient']
        se = r['se']
        t = beta / se if se > 0 else np.nan
        p = r['p_one_sided']
        fdr = r.get('p_fdr', np.nan)
        sig = 'Yes' if r.get('fdr_significant', False) else 'No'

        lines.append(f"| {var} | {beta:.6f} | {se:.6f} | {t:.2f} | {p:.4f} | {fdr:.4f} | {sig} |")

    lines.append("")
    lines.append("*Significance: FDR-corrected p < 0.05, one-tailed (beta > 0)*")
    lines.append("")

    # Robustness specifications
    lines.append("## Robustness Specifications")
    lines.append("")

    spec_summary = {}
    for spec_name in ['firm_only', 'pooled', 'double_cluster']:
        spec_results = [r for r in results if r['spec'] == spec_name and 'error' not in r]
        n_signif = sum(1 for r in spec_results if r.get('p_one_sided', 1) < 0.05)

        if spec_results:
            avg_beta = np.mean([r['coefficient'] for r in spec_results if not np.isnan(r['coefficient'])])
            spec_summary[spec_name] = {
                'n_signif': n_signif,
                'avg_beta': avg_beta,
                'n': spec_results[0]['n'],
            }

    lines.append("| Spec | Entity FE | Time FE | Cluster | N | Signif (p<0.05) | Avg Beta |")
    lines.append("|---|---|---|---|---|---|---|")
    lines.append("| primary | Yes | Yes | firm | " + f"{primary_results[0]['n']:,}" + f" | {len(raw_signif)}/6 | " + f"{np.mean([r['coefficient'] for r in primary_results if not np.isnan(r['coefficient'])]):.6f} |")

    for spec_name, summ in spec_summary.items():
        fe = 'Yes' if 'firm' in spec_name or spec_name == 'double_cluster' else 'No'
        te = 'Yes' if spec_name in ['primary', 'double_cluster'] else 'No'
        cl = 'firm+year' if spec_name == 'double_cluster' else 'firm'
        lines.append(f"| {spec_name} | {fe} | {te} | {cl} | {summ['n']:,} | {summ['n_signif']}/6 | {summ['avg_beta']:.6f} |")

    lines.append("")

    # Sample statistics
    lines.append("## Sample Statistics")
    lines.append("")
    lines.append(f"- DV mean: {sample_stats.get('dv_mean', 'N/A')}")
    lines.append(f"- DV std: {sample_stats.get('dv_std', 'N/A')}")
    lines.append(f"- N (observations): {sample_stats['n_obs']:,}")
    lines.append(f"- N (firms): {sample_stats['n_firms']:,}")
    lines.append(f"- Years: {sample_stats['year_min']}-{sample_stats['year_max']}")
    lines.append("")

    # Robustness tests section
    robustness_results = [r for r in results if 'error' not in r and (
        r.get('dv_type') != 'Amihud (2002)' or
        r.get('iv_type') is not None or
        r.get('timing') is not None
    )]

    if robustness_results:
        lines.append("## Robustness Tests")
        lines.append("")
        lines.append("### Alternative Dependent Variables")
        lines.append("")

        alt_dv_results = [r for r in robustness_results if r.get('dv_type') != 'Amihud (2002)']
        if alt_dv_results:
            dv_groups = {}
            for r in alt_dv_results:
                dv_type = r.get('dv_type', 'Unknown')
                if dv_type not in dv_groups:
                    dv_groups[dv_type] = []
                dv_groups[dv_type].append(r)

            for dv_type, group in dv_groups.items():
                n_sig = sum(1 for r in group if r.get('p_one_sided', 1) < 0.05)
                avg_beta = np.mean([r['coefficient'] for r in group if not np.isnan(r['coefficient'])])
                lines.append(f"**{dv_type}:** {n_sig}/{len(group)} significant, avg beta = {avg_beta:.6f}")
            lines.append("")
        else:
            lines.append("No alternative DVs available in data.")
            lines.append("")

        lines.append("### Alternative Independent Variables")
        lines.append("")

        alt_iv_results = [r for r in robustness_results if r.get('iv_type') is not None]
        if alt_iv_results:
            iv_groups = {}
            for r in alt_iv_results:
                iv_type = r.get('iv_type', 'Unknown')
                if iv_type not in iv_groups:
                    iv_groups[iv_type] = []
                iv_groups[iv_type].append(r)

            for iv_type, group in iv_groups.items():
                n_sig = sum(1 for r in group if r.get('p_one_sided', 1) < 0.05)
                avg_beta = np.mean([r['coefficient'] for r in group if not np.isnan(r['coefficient'])])
                lines.append(f"**{iv_type}:** {n_sig}/{len(group)} significant, avg beta = {avg_beta:.6f}")
            lines.append("")
        else:
            lines.append("No alternative IV tests run.")
            lines.append("")

        lines.append("### Timing Tests")
        lines.append("")

        timing_results = [r for r in robustness_results if r.get('timing') is not None]
        if timing_results:
            timing_groups = {}
            for r in timing_results:
                timing = r.get('timing', 'Unknown')
                if timing not in timing_groups:
                    timing_groups[timing] = []
                timing_groups[timing].append(r)

            for timing, group in timing_groups.items():
                n_sig = sum(1 for r in group if r.get('p_one_sided', 1) < 0.05)
                avg_beta = np.mean([r['coefficient'] for r in group if not np.isnan(r['coefficient'])])
                lines.append(f"**{timing}:** {n_sig}/{len(group)} significant, avg beta = {avg_beta:.6f}")
            lines.append("")
        else:
            lines.append("No timing tests run.")
            lines.append("")

        # Overall robustness conclusion
        total_rob = len(robustness_results)
        rob_sig = sum(1 for r in robustness_results if r.get('p_one_sided', 1) < 0.05)
        rob_pct = rob_sig / total_rob * 100 if total_rob > 0 else 0

        lines.append(f"**Robustness Summary:** {rob_sig}/{total_rob} ({rob_pct:.1f}%) robustness tests significant (p < 0.05)")
        lines.append("")
    else:
        lines.append("## Robustness Tests")
        lines.append("")
        lines.append("No robustness tests run.")
        lines.append("")

    # Hypothesis conclusion
    lines.append("## Hypothesis Conclusion")
    lines.append("")

    if len(fdr_signif) >= 4:
        lines.append("**H7a SUPPORTED:** Managerial speech uncertainty predicts higher stock illiquidity.")
        lines.append("")
        lines.append("The results provide strong support for the hypothesis that firms with more")
        lines.append("uncertain managerial speech face higher stock illiquidity, consistent with")
        lines.append("increased information asymmetry and reduced informed trading.")
    elif len(fdr_signif) >= 2:
        lines.append("**H7a PARTIALLY SUPPORTED:** Some uncertainty measures predict stock illiquidity.")
        lines.append("")
        lines.append("The results provide partial support for the hypothesis. While some uncertainty")
        lines.append("measures show significant effects, the evidence is not consistent across all")
        lines.append("measures.")
    elif len(raw_signif) >= 2:
        lines.append("**H7a WEAK SUPPORT:** Effects present before multiple testing correction.")
        lines.append("")
        lines.append("Some uncertainty measures show significant effects before FDR correction,")
        lines.append("but these do not survive multiple testing adjustment. The evidence is weak.")
    else:
        lines.append("**H7a NOT SUPPORTED:** No significant effect of uncertainty on illiquidity.")
        lines.append("")
        lines.append("The results do not support the hypothesis that managerial speech uncertainty")
        lines.append("predicts stock illiquidity. Any observed relationships are not statistically")
        lines.append("significant after appropriate multiple testing correction.")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated by 4.7_H7IlliquidityRegression.py*")

    output_path = output_dir / "H7_RESULTS.md"
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    if dw:
        dw.write(f"Saved: {output_path.name}\n")

    return output_path


def save_stats(stats, output_dir, dw=None):
    """Save statistics dictionary to JSON file"""
    stats_path = output_dir / "stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2, default=str)

    if dw:
        dw.write(f"Saved: {stats_path.name}\n")

    return stats_path


# ==============================================================================
# CLI and Main
# ==============================================================================


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="H7 Illiquidity Regression - Panel OLS with Uncertainty -> Illiquidity"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and setup without running regressions"
    )
    return parser.parse_args()


def main():
    """Main execution function"""
    args = parse_args()

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # Load config
    config = load_config()

    # Setup paths
    paths = setup_paths(config, timestamp)

    # Initialize DualWriter for logging
    dw = DualWriter(paths["log_file"])

    # Script header
    dw.write("=" * 80 + "\n")
    dw.write("STEP 4.7: H7 Illiquidity Regression\n")
    dw.write("=" * 80 + "\n")
    dw.write(f"Timestamp: {timestamp}\n")
    dw.write(f"Git SHA: {get_git_sha()}\n")
    dw.write(f"Config: {config.get('step_id', '4.7_H7IlliquidityRegression')}\n")
    dw.write("")

    # Stats tracking
    stats = {
        'step_id': '4.7_H7IlliquidityRegression',
        'timestamp': timestamp,
        'git_sha': get_git_sha(),
        'input': {},
        'processing': {},
        'output': {},
        'regressions': [],
        'timing': {},
        'memory': {},
        'sample_stats': {},
    }

    start_time = time.time()
    start_mem = get_process_memory_mb()

    try:
        # Load H7 data
        dw.write("\n[1] Loading H7 illiquidity data...\n")
        df = load_data(paths["h7_dir"], dw)

        stats['input']['h7_data'] = {
            'rows': int(len(df)),
            'source': str(paths["h7_dir"]),
        }

        # Prepare regression data
        dw.write("\n[2] Preparing regression data...\n")
        dv_col = 'amihud_lag1'
        reg_df = prepare_regression_data(
            df, UNCERTAINTY_MEASURES, CONTROL_VARS,
            dv_col=dv_col, min_obs_per_firm=3, dw=dw
        )

        # Validate data
        dw.write("\n[3] Validating data...\n")
        validate_data(reg_df, dv_col, UNCERTAINTY_MEASURES, CONTROL_VARS, dw)

        # Collect sample statistics
        stats['sample_stats'] = {
            'n_obs': int(len(reg_df)),
            'n_firms': int(reg_df.index.get_level_values('gvkey').nunique()),
            'year_min': int(reg_df.index.get_level_values('year').min()),
            'year_max': int(reg_df.index.get_level_values('year').max()),
            'dv_mean': float(reg_df[dv_col].mean()),
            'dv_std': float(reg_df[dv_col].std()),
            'dv_min': float(reg_df[dv_col].min()),
            'dv_max': float(reg_df[dv_col].max()),
        }

        stats['processing']['regression_prep'] = {
            'final_obs': stats['sample_stats']['n_obs'],
            'unique_firms': stats['sample_stats']['n_firms'],
            'year_range': [stats['sample_stats']['year_min'], stats['sample_stats']['year_max']],
        }

        if args.dry_run:
            dw.write("\n[Dry run] Validation complete. Exiting.\n")
            return

        # Run all regressions
        dw.write("\n[4] Running H7 regressions...\n")
        dw.write(f"  {len(UNCERTAINTY_MEASURES)} uncertainty measures x {len(SPECS)} specifications = "
                f"{len(UNCERTAINTY_MEASURES) * len(SPECS)} regressions\n")

        results = run_all_h7_regressions(
            reg_df, UNCERTAINTY_MEASURES, SPECS, CONTROL_VARS,
            dv_col=dv_col, vif_threshold=5.0, dw=dw
        )

        # Apply FDR correction to primary results
        dw.write("\n[5] Applying FDR correction to primary results...\n")
        results = apply_fdr_correction(results, alpha=0.05, dw=dw)

        # Run robustness suite (alternative DVs, IVs, timing)
        dw.write("\n[6] Running robustness suite...\n")
        robustness_results = run_robustness_suite(
            reg_df, UNCERTAINTY_MEASURES, CONTROL_VARS,
            vif_threshold=5.0, dw=dw
        )

        # Combine primary and robustness results
        all_results = results + robustness_results
        dw.write(f"\n  Total results: {len(all_results)} ({len(results)} primary + {len(robustness_results)} robustness)\n")

        stats['regressions'] = [{
            'spec': r['spec'],
            'uncertainty_var': r['uncertainty_var'],
            'n_obs': r['n'],
            'n_firms': r['n_firms'],
            'coefficient': r['coefficient'],
            'p_one_sided': r['p_one_sided'],
            'p_fdr': r.get('p_fdr', np.nan),
            'fdr_significant': r.get('fdr_significant', False),
            'dv_type': r.get('dv_type', 'Amihud (2002)'),
            'iv_type': r.get('iv_type'),
            'timing': r.get('timing'),
        } for r in all_results]

        # Save outputs
        dw.write("\n[7] Saving outputs...\n")
        results_df = save_regression_results(all_results, paths["output_dir"], dw)
        generate_results_markdown(all_results, paths["output_dir"], stats['sample_stats'], dv_col, dw)

        stats['output']['regression_results'] = {
            'file': 'H7_Regression_Results.parquet',
            'rows': int(len(results_df)),
            'regressions': len(all_results),
            'primary': len(results),
            'robustness': len(robustness_results),
        }

        # Final stats
        end_time = time.time()
        end_mem = get_process_memory_mb()

        stats['timing']['duration_seconds'] = end_time - start_time
        stats['memory']['rss_mb_start'] = start_mem['rss_mb']
        stats['memory']['rss_mb_end'] = end_mem['rss_mb']

        # Robustness summary
        stats['robustness'] = {
            'total': len(robustness_results),
            'alt_dv': len([r for r in robustness_results if r.get('dv_type') != 'Amihud (2002)']),
            'alt_iv': len([r for r in robustness_results if r.get('iv_type')]),
            'timing': len([r for r in robustness_results if r.get('timing')]),
        }

        save_stats(stats, paths["output_dir"], dw)

        # Summary
        dw.write("\n" + "=" * 80 + "\n")
        dw.write("EXECUTION SUMMARY\n")
        dw.write("=" * 80 + "\n")
        dw.write(f"  Duration: {stats['timing']['duration_seconds']:.2f} seconds\n")
        dw.write(f"  Total regressions: {len(all_results)}\n")
        dw.write(f"    Primary: {len(results)}\n")
        dw.write(f"    Robustness: {len(robustness_results)}\n")
        dw.write(f"  Output directory: {paths['output_dir']}\n")

        # Count significant results
        primary_fdr_signif = sum(1 for r in results if r['spec'] == 'primary' and r.get('fdr_significant', False))
        primary_raw_signif = sum(1 for r in results if r['spec'] == 'primary' and r.get('p_one_sided', 1) < 0.05)

        dw.write(f"\n  Primary spec - H7a (beta > 0): {primary_raw_signif}/4 significant (raw)")
        dw.write(f"\n  Primary spec - H7a (beta > 0): {primary_fdr_signif}/4 significant (FDR-corrected)")

        # Robustness summary
        rob_sig = sum(1 for r in robustness_results if r.get('p_one_sided', 1) < 0.05)
        dw.write(f"\n  Robustness tests: {rob_sig}/{len(robustness_results)} significant (p<0.05)")
        dw.write("=" * 80 + "\n")
        dw.write("COMPLETE\n")

    except Exception as e:
        dw.write(f"\nERROR: {e}\n")
        import traceback
        dw.write(traceback.format_exc())
        raise
    finally:
        dw.close()


if __name__ == "__main__":
    main()
