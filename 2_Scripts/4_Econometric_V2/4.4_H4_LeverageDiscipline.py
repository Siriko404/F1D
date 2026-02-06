#!/usr/bin/env python3
"""
==============================================================================
STEP 4.4: H4 Leverage Disciplines Speech (Data Preparation)
==============================================================================
ID: 4.4_H4_LeverageDiscipline
Description: Data preparation for H4 (Leverage Disciplines Speech Uncertainty).
             Tests whether higher leverage disciplines managers and reduces
             speech uncertainty (reverse causal direction from H1-H3).

Model Specification:
    Uncertainty_t = beta0 + beta1*Leverage_{t-1} + beta2*Analyst_Uncertainty_t
                     + beta3*Presentation_Uncertainty_t + gamma*Controls
                     + Firm FE + Year FE + Industry FE + epsilon

Hypothesis Test:
    H4: beta1 < 0 (Higher leverage leads to lower speech uncertainty - one-tailed)

Note: This script prepares the analysis dataset. Regressions will be run
      in a separate execution step.

Inputs:
    - 4_Outputs/3_Financial_V2/latest/H1_CashHoldings.parquet
      (leverage, firm_size, tobins_q, roa, cash_holdings, dividend_payer)
    - 4_Outputs/3_Financial_V2/latest/H3_PayoutPolicy.parquet
      (firm_maturity, earnings_volatility)
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_*.parquet
      (6 uncertainty DVs, analyst uncertainty, presentation uncertainty)

Outputs:
    - 4_Outputs/4_Econometric_V2/4.4_H4_LeverageDiscipline/{timestamp}/H4_Analysis_Dataset.parquet
      (complete analysis dataset with all variables for 6 regressions)
    - 4_Outputs/4_Econometric_V2/4.4_H4_LeverageDiscipline/{timestamp}/stats.json
      (merge stats, VIF diagnostics, variable availability, execution metadata)
    - 4_Outputs/4_Econometric_V2/4.4_H4_LeverageDiscipline/{timestamp}/H4_DATA_SUMMARY.md
      (human-readable summary of data preparation)
    - 3_Logs/4_Econometric_V2/4.4_H4_LeverageDiscipline/{timestamp}_H4.log
      (execution log with dual-writer output)

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

from shared.diagnostics import check_multicollinearity, format_vif_table

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


# H4: 6 uncertainty DVs (same as H1-H3)
UNCERTAINTY_MEASURES = [
    'Manager_QA_Uncertainty_pct',
    'CEO_QA_Uncertainty_pct',
    'Manager_QA_Weak_Modal_pct',
    'CEO_QA_Weak_Modal_pct',
    'Manager_Pres_Uncertainty_pct',
    'CEO_Pres_Uncertainty_pct',
]

# Analyst uncertainty control (from linguistic variables)
ANALYST_UNCERTAINTY_VAR = 'Analyst_QA_Uncertainty_pct'

# Presentation controls for QA DVs (to control for presentation uncertainty)
PRESENTATION_CONTROL_MAP = {
    'Manager_QA_Uncertainty_pct': 'Manager_Pres_Uncertainty_pct',
    'CEO_QA_Uncertainty_pct': 'CEO_Pres_Uncertainty_pct',
    'Manager_QA_Weak_Modal_pct': None,  # No direct presentation equivalent
    'CEO_QA_Weak_Modal_pct': None,
    'Manager_Pres_Uncertainty_pct': None,  # Already a presentation DV
    'CEO_Pres_Uncertainty_pct': None,
}

# Financial controls (from H1 and H3)
FINANCIAL_CONTROLS = [
    'firm_size',
    'tobins_q',
    'roa',
    'cash_holdings',
    'dividend_payer',
    'firm_maturity',
    'earnings_volatility',
]

# Base specification for VIF check (continuous vars only)
VIF_COLUMNS = [
    'leverage_lag1',
    'analyst_qa_uncertainty',
    'firm_size',
    'tobins_q',
    'roa',
    'cash_holdings',
    'firm_maturity',
    'earnings_volatility',
]

# ==============================================================================
# Path Setup
# ==============================================================================


def setup_paths(config, timestamp):
    """Set up all required paths using get_latest_output_dir"""
    root = Path(__file__).parent.parent.parent

    # Resolve H1 variables directory (for leverage and base controls)
    h1_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H1_CashHoldings.parquet",
    )

    # Resolve H3 variables directory (for firm_maturity, earnings_volatility)
    h3_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H3_PayoutPolicy.parquet",
    )

    # Resolve speech uncertainty directory
    speech_dir = get_latest_output_dir(
        root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
        required_file="linguistic_variables_2002.parquet",  # At least one year must exist
    )

    paths = {
        "root": root,
        "h1_dir": h1_dir,
        "h3_dir": h3_dir,
        "speech_dir": speech_dir,
    }

    # Output directory
    output_base = root / "4_Outputs" / "4_Econometric_V2" / "4.4_H4_LeverageDiscipline"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "4_Econometric_V2" / "4.4_H4_LeverageDiscipline"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H4.log"

    return paths


# ==============================================================================
# Data Loading Functions
# ==============================================================================


def load_h1_variables(h1_dir, dw=None):
    """
    Load H1 Cash Holdings variables.

    Expects H1_CashHoldings.parquet with columns:
    - gvkey, fiscal_year
    - leverage (primary IV for H4)
    - Base controls: firm_size, tobins_q, roa, cash_holdings, dividend_payer
    """
    h1_file = h1_dir / "H1_CashHoldings.parquet"
    if not h1_file.exists():
        raise FileNotFoundError(f"H1_CashHoldings.parquet not found in {h1_dir}")

    validate_input_file(h1_file, must_exist=True)
    df = pd.read_parquet(h1_file)

    if dw:
        dw.write(f"  Loaded H1 variables: {len(df):,} rows\n")
        dw.write(f"    Columns: {df.columns.tolist()}\n")

    # Ensure gvkey is string and zero-padded
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    return df


def load_h3_variables(h3_dir, dw=None):
    """
    Load H3 Payout Policy variables.

    Expects H3_PayoutPolicy.parquet with columns:
    - gvkey, fiscal_year
    - Additional controls: firm_maturity, earnings_volatility
    """
    h3_file = h3_dir / "H3_PayoutPolicy.parquet"
    if not h3_file.exists():
        raise FileNotFoundError(f"H3_PayoutPolicy.parquet not found in {h3_dir}")

    validate_input_file(h3_file, must_exist=True)
    df = pd.read_parquet(h3_file)

    if dw:
        dw.write(f"  Loaded H3 variables: {len(df):,} rows\n")
        dw.write(f"    Columns: {df.columns.tolist()}\n")

    # Ensure gvkey is string and zero-padded
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    # Select only gvkey, fiscal_year, and the two H3-specific controls
    df = df[['gvkey', 'fiscal_year', 'firm_maturity', 'earnings_volatility']].copy()

    return df


def load_speech_uncertainty(speech_dir, uncertainty_cols, dw=None):
    """
    Load all linguistic_variables_*.parquet files and concatenate.

    Returns DataFrame with columns:
    - file_name, gvkey, start_date
    - All uncertainty measures (6 DVs + analyst uncertainty + presentation controls)
    """
    speech_files = sorted(speech_dir.glob("linguistic_variables_*.parquet"))

    if not speech_files:
        raise FileNotFoundError(f"No linguistic_variables files found in {speech_dir}")

    dfs = []
    total_rows = 0
    for f in speech_files:
        df = pd.read_parquet(f)
        dfs.append(df)
        total_rows += len(df)

    if dw:
        dw.write(f"  Loaded speech uncertainty: {total_rows:,} calls across {len(speech_files)} years\n")

    combined = pd.concat(dfs, ignore_index=True)

    # Select only needed columns
    required_cols = ['file_name', 'gvkey', 'start_date'] + uncertainty_cols
    available_cols = [c for c in required_cols if c in combined.columns]
    missing_cols = set(required_cols) - set(available_cols)

    if missing_cols:
        raise ValueError(f"Missing columns in speech data: {missing_cols}")

    combined = combined[available_cols].copy()

    # Ensure gvkey is string and zero-padded
    combined["gvkey"] = combined["gvkey"].astype(str).str.zfill(6)
    combined["start_date"] = pd.to_datetime(combined["start_date"])

    return combined


# ==============================================================================
# Variable Preparation
# ==============================================================================


def create_lagged_leverage(df, leverage_col='leverage', group_col='gvkey', dw=None):
    """
    Create lagged leverage variable (t-1) within firm boundaries.

    Leverage at t-1 is the key independent variable for H4. We group by gvkey
    and shift leverage by 1 year to get the prior year's leverage.

    Args:
        df: DataFrame with gvkey, fiscal_year, leverage
        leverage_col: Name of leverage column
        group_col: Column to group by for lag creation (gvkey)

    Returns:
        DataFrame with new column 'leverage_lag1'
    """
    df_work = df.copy()

    # Sort by gvkey and fiscal_year for proper lagging
    df_work = df_work.sort_values([group_col, 'fiscal_year'])

    # Create lagged leverage within each firm
    df_work['leverage_lag1'] = df_work.groupby(group_col)[leverage_col].shift(1)

    # Validate: Check for cross-entity leakage
    # The first observation for each firm should have NaN lag
    first_obs = df_work.groupby(group_col).head(1)
    if not first_obs['leverage_lag1'].isna().all():
        raise ValueError("Cross-entity leakage detected in lagged leverage!")

    # Check for gaps > 1 year
    df_work['year_diff'] = df_work.groupby(group_col)['fiscal_year'].diff()
    large_gaps = df_work[df_work['year_diff'] > 1]
    if not large_gaps.empty and dw:
        n_large_gaps = len(large_gaps)
        dw.write(f"  Warning: {n_large_gaps} observations have gaps > 1 year in fiscal_year\n")

    if dw:
        before_count = len(df_work)
        after_count = df_work['leverage_lag1'].notna().sum()
        dropped = before_count - after_count
        dw.write(f"  Lagged leverage created: {after_count:,} obs with valid lag\n")
        dw.write(f"    Dropped: {dropped:,} obs (first year per firm)\n")

    return df_work


def aggregate_speech_to_firmyear(speech_df, uncertainty_cols, dw=None):
    """
    Aggregate call-level speech data to firm-year level.

    Extracts fiscal_year from start_date and computes mean of uncertainty
    measures within each firm-year. Counts number of calls per firm-year.
    """
    df = speech_df.copy()

    # Extract year from start_date as fiscal_year
    df["fiscal_year"] = df["start_date"].dt.year

    # Group by gvkey and fiscal_year
    group_cols = ['gvkey', 'fiscal_year']

    # First aggregate numeric columns with mean
    numeric_cols = [c for c in uncertainty_cols if c in df.columns]
    agg_df = df.groupby(group_cols, as_index=False)[numeric_cols].mean()

    # Count calls per firm-year
    call_counts = df.groupby(group_cols, as_index=False)['file_name'].count()
    call_counts = call_counts.rename(columns={'file_name': 'n_calls'})

    # Merge the aggregations
    agg_df = agg_df.merge(call_counts, on=group_cols)

    if dw:
        mean_calls = agg_df['n_calls'].mean()
        dw.write(f"  Aggregated to {len(agg_df):,} firm-years, mean {mean_calls:.2f} calls per firm-year\n")

    return agg_df


# ==============================================================================
# Data Preparation
# ==============================================================================


def prepare_analysis_dataset(h1_df, h3_df, speech_agg_df, uncertainty_measures,
                            analyst_uncertainty_var, vif_columns, vif_threshold=5.0, dw=None):
    """
    Prepare complete H4 analysis dataset by merging all data sources.

    Steps:
    1. Merge H1 with H3 on (gvkey, fiscal_year)
    2. Merge with speech uncertainty data on (gvkey, fiscal_year)
    3. Create lagged leverage (t-1)
    4. Drop observations without valid lag
    5. Run VIF diagnostics on base specification
    6. Validate variable availability

    Args:
        h1_df: H1 data with leverage and base controls
        h3_df: H3 data with firm_maturity, earnings_volatility
        speech_agg_df: Aggregated speech uncertainty by firm-year
        uncertainty_measures: List of 6 uncertainty DVs
        analyst_uncertainty_var: Name of analyst uncertainty column
        vif_columns: List of continuous variables for VIF check
        vif_threshold: VIF threshold for multicollinearity warning

    Returns:
        DataFrame with all required variables for H4 regressions
    """
    # Step 1: Merge H1 with H3
    merge_cols = ['gvkey', 'fiscal_year']
    # H3 has only firm_maturity and earnings_volatility (select columns in load_h3_variables)
    # But to be safe, handle potential duplicates with suffixes
    merged_df = h1_df.merge(h3_df, on=merge_cols, how='outer', suffixes=('', '_h3'))

    # If there were duplicates, coalesce to prefer H1 values for controls
    # (H1 has the full set of controls, H3 only adds firm_maturity and earnings_volatility)
    for col in ['firm_size', 'roa', 'tobins_q', 'cash_holdings']:
        if f'{col}_h3' in merged_df.columns:
            merged_df[col] = merged_df[col].fillna(merged_df[f'{col}_h3'])
            merged_df = merged_df.drop(columns=[f'{col}_h3'])

    if dw:
        h1_only = merged_df['firm_maturity'].isna() & merged_df['leverage'].notna()
        h3_only = merged_df['leverage'].isna() & merged_df['firm_maturity'].notna()
        both = merged_df['leverage'].notna() & merged_df['firm_maturity'].notna()
        dw.write(f"  After H1-H3 merge: {len(merged_df):,} obs\n")
        dw.write(f"    H1 only: {h1_only.sum():,}, H3 only: {h3_only.sum():,}, Both: {both.sum():,}\n")

    # Step 2: Merge with speech uncertainty
    # Use suffixes to handle any duplicate column names
    merged_df = merged_df.merge(speech_agg_df, on=merge_cols, how='inner', suffixes=('', '_speech'))

    # Coalesce any duplicated columns (prefer original values)
    for col in merged_df.columns:
        if col.endswith('_speech'):
            orig_col = col.replace('_speech', '')
            if orig_col in merged_df.columns:
                merged_df[orig_col] = merged_df[orig_col].fillna(merged_df[col])
                merged_df = merged_df.drop(columns=[col])

    if dw:
        dw.write(f"  After speech merge: {len(merged_df):,} obs (complete cases only)\n")

    # Step 3: Create lagged leverage
    merged_df = create_lagged_leverage(merged_df, dw=dw)

    # Step 4: Drop observations without valid lag (first year per firm)
    merged_df = merged_df.dropna(subset=['leverage_lag1'])

    if dw:
        dw.write(f"  After dropping missing lags: {len(merged_df):,} obs\n")

    # Step 5: Select and rename variables for analysis
    # Include all uncertainty measures, analyst uncertainty, presentation controls
    core_cols = ['gvkey', 'fiscal_year', 'leverage', 'leverage_lag1']
    control_cols = FINANCIAL_CONTROLS.copy()

    # Build full column list (preserve order, remove duplicates)
    all_cols = core_cols + control_cols + uncertainty_measures + [analyst_uncertainty_var]

    # Add presentation controls that exist in data (avoid duplicates)
    presentation_cols = [c for c in PRESENTATION_CONTROL_MAP.values()
                        if c is not None and c not in all_cols]
    all_cols.extend(presentation_cols)

    # Add n_calls for reference
    all_cols.append('n_calls')

    # Remove any duplicates while preserving order
    seen = set()
    unique_cols = []
    for col in all_cols:
        if col not in seen:
            seen.add(col)
            unique_cols.append(col)

    # Select available columns only
    available_cols = [c for c in unique_cols if c in merged_df.columns]

    # Also check if merged_df itself has duplicate columns and deduplicate if needed
    if len(merged_df.columns) != len(set(merged_df.columns)):
        # DataFrame has duplicate columns - need to deduplicate
        # Keep first occurrence of each column
        merged_df = merged_df.loc[:, ~merged_df.columns.duplicated(keep='first')]

    analysis_df = merged_df[available_cols].copy()

    # Final check: remove any duplicate columns in analysis_df
    analysis_df = analysis_df.loc[:, ~analysis_df.columns.duplicated(keep='first')]

    # Rename analyst uncertainty to shorter name for regression
    if analyst_uncertainty_var in analysis_df.columns:
        analysis_df = analysis_df.rename(columns={analyst_uncertainty_var: 'analyst_qa_uncertainty'})

    # Step 6: VIF diagnostics on base specification
    vif_vars = [c for c in vif_columns if c in analysis_df.columns]
    if dw:
        dw.write(f"\n[4] Running VIF diagnostics on base specification...\n")
        dw.write(f"  Variables: {vif_vars}\n")

    try:
        vif_result = check_multicollinearity(
            analysis_df,
            vif_vars,
            vif_threshold=vif_threshold,
            condition_threshold=1000.0,
            fail_on_violation=False  # Log warning but continue
        )

        if dw:
            dw.write(str(format_vif_table(vif_result['vif_results'], vif_threshold)) + "\n")

            if vif_result['vif_violations']:
                dw.write(f"  WARNING: VIF violations detected: {vif_result['vif_violations']}\n")
            else:
                dw.write(f"  OK: All VIF values < {vif_threshold}\n")

            if vif_result['condition_number']:
                dw.write(f"  Condition number: {vif_result['condition_number']:.2f}\n")

    except Exception as e:
        if dw:
            dw.write(f"  VIF check failed: {e}\n")

    # Step 7: Validate variable availability
    if dw:
        dw.write(f"\n[5] Variable availability...\n")

        for var in uncertainty_measures:
            avail = analysis_df[var].notna().sum()
            # Convert scalar to int (handle pandas 3.x Series behavior)
            try:
                avail = int(avail.iloc[0] if hasattr(avail, 'iloc') else avail)
            except (AttributeError, IndexError):
                avail = int(avail)
            total = len(analysis_df)
            pct = avail / total * 100
            dw.write(f"  {var}: {avail:,}/{total:,} ({pct:.1f}%)\n")

        for var in ['analyst_qa_uncertainty'] + FINANCIAL_CONTROLS:
            if var in analysis_df.columns:
                avail = analysis_df[var].notna().sum()
                try:
                    avail = int(avail.iloc[0] if hasattr(avail, 'iloc') else avail)
                except (AttributeError, IndexError):
                    avail = int(avail)
                total = len(analysis_df)
                pct = avail / total * 100
                dw.write(f"  {var}: {avail:,}/{total:,} ({pct:.1f}%)\n")

    # Final stats
    if dw:
        dw.write(f"\n[6] Final analysis dataset...\n")
        dw.write(f"  N observations: {len(analysis_df):,}\n")
        dw.write(f"  N unique firms: {analysis_df['gvkey'].nunique():,}\n")
        dw.write(f"  Year range: {analysis_df['fiscal_year'].min()}-{analysis_df['fiscal_year'].max()}\n")

    return analysis_df, vif_result if 'vif_result' in locals() else None


# ==============================================================================
# Output Functions
# ==============================================================================


def save_analysis_dataset(df, output_path, dw=None):
    """Save analysis dataset to parquet file"""
    df.to_parquet(output_path, index=False)

    if dw:
        dw.write(f"\nSaved: {output_path.name} ({len(df):,} rows, {len(df.columns)} cols)\n")

    return output_path


def save_vif_results(vif_result, output_path, dw=None):
    """Save VIF diagnostics to JSON file"""
    if vif_result is None:
        return None

    # Convert VIF DataFrame to dict for JSON serialization
    vif_dict = {
        'vif_results': vif_result['vif_results'].to_dict('records'),
        'condition_number': vif_result['condition_number'],
        'vif_violations': vif_result['vif_violations'],
        'condition_violation': vif_result['condition_violation'],
        'pass': vif_result['pass'],
    }

    with open(output_path, 'w') as f:
        json.dump(vif_dict, f, indent=2, default=str)

    if dw:
        dw.write(f"Saved: {output_path.name}\n")

    return output_path


def generate_data_summary_markdown(df, vif_result, output_dir, dw=None):
    """
    Generate human-readable markdown summary of H4 data preparation.
    """
    lines = []
    lines.append("# H4 Leverage Discipline Analysis Dataset")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Hypothesis
    lines.append("## Hypothesis")
    lines.append("")
    lines.append("**H4: Higher leverage disciplines managers and lowers speech uncertainty**")
    lines.append("")
    lines.append("Model Specification:")
    lines.append("```")
    lines.append("Uncertainty_t = beta0 + beta1*Leverage_{t-1} + beta2*Analyst_Uncertainty_t")
    lines.append("                + beta3*Presentation_Uncertainty_t + gamma*Controls")
    lines.append("                + Firm FE + Year FE + epsilon")
    lines.append("```")
    lines.append("")
    lines.append("- **H4 (one-tailed):** beta1 < 0 (Leverage reduces uncertainty)")
    lines.append("")

    # Data summary
    lines.append("## Dataset Summary")
    lines.append("")
    lines.append(f"- **N observations:** {len(df):,}")
    lines.append(f"- **N unique firms:** {df['gvkey'].nunique():,}")
    lines.append(f"- **Year range:** {df['fiscal_year'].min()}-{df['fiscal_year'].max()}")
    lines.append(f"- **Mean calls per firm-year:** {df['n_calls'].mean():.2f}")
    lines.append("")

    # Uncertainty DVs
    lines.append("## Uncertainty Dependent Variables")
    lines.append("")
    lines.append("| Measure | N Valid | % Valid | Mean | Std |")
    lines.append("|---|---|---|---|---|")

    for var in UNCERTAINTY_MEASURES:
        if var in df.columns:
            valid = df[var].notna().sum()
            pct = valid / len(df) * 100
            mean = df[var].mean()
            std = df[var].std()
            lines.append(f"| {var} | {valid:,} | {pct:.1f}% | {mean:.4f} | {std:.4f} |")

    lines.append("")

    # Key variables
    lines.append("## Key Independent Variables")
    lines.append("")
    lines.append("| Variable | N Valid | % Valid | Mean | Std | Min | Max |")
    lines.append("|---|---|---|---|---|---|---|")

    key_vars = ['leverage', 'leverage_lag1', 'analyst_qa_uncertainty']
    for var in key_vars:
        if var in df.columns:
            valid = df[var].notna().sum()
            pct = valid / len(df) * 100
            mean = df[var].mean()
            std = df[var].std()
            min_val = df[var].min()
            max_val = df[var].max()
            lines.append(f"| {var} | {valid:,} | {pct:.1f}% | {mean:.4f} | {std:.4f} | {min_val:.4f} | {max_val:.4f} |")

    lines.append("")

    # Financial controls
    lines.append("## Financial Controls")
    lines.append("")
    lines.append("| Variable | N Valid | % Valid | Mean | Std |")
    lines.append("|---|---|---|---|---|")

    for var in FINANCIAL_CONTROLS:
        if var in df.columns:
            valid = df[var].notna().sum()
            pct = valid / len(df) * 100
            mean = df[var].mean()
            std = df[var].std()
            lines.append(f"| {var} | {valid:,} | {pct:.1f}% | {mean:.4f} | {std:.4f} |")

    lines.append("")

    # VIF diagnostics
    lines.append("## VIF Diagnostics")
    lines.append("")
    lines.append("VIF thresholds: < 5 (low), 5-10 (moderate), > 10 (high)")
    lines.append("")
    lines.append("| Variable | VIF | Status |")
    lines.append("|---|---|---|")

    if vif_result and 'vif_results' in vif_result:
        vif_df = vif_result['vif_results']
        for _, row in vif_df.iterrows():
            var = row['variable']
            vif = row['VIF']
            exceeded = row['threshold_exceeded']
            status = "*** EXCEEDS" if exceeded else "OK"
            lines.append(f"| {var} | {vif:.2f} | {status} |")

        if vif_result['condition_number']:
            lines.append("")
            lines.append(f"**Condition number:** {vif_result['condition_number']:.2f}")

    lines.append("")

    # Correlation: leverage_lag1 with uncertainty measures
    lines.append("## Correlation: Lagged Leverage vs Uncertainty Measures")
    lines.append("")
    lines.append("| Uncertainty Measure | Correlation |")
    lines.append("|---|---|")

    for var in UNCERTAINTY_MEASURES:
        if var in df.columns:
            corr = df['leverage_lag1'].corr(df[var])
            lines.append(f"| {var} | {corr:.4f} |")

    lines.append("")
    lines.append("*Pearson correlation coefficients")
    lines.append("")

    # Data ready note
    lines.append("## Next Steps")
    lines.append("")
    lines.append("The analysis dataset is ready for H4 regressions. Run the regression")
    lines.append("script to estimate the following models:")
    lines.append("")
    lines.append("1. Manager_QA_Uncertainty ~ leverage_lag1 + controls + FEs")
    lines.append("2. CEO_QA_Uncertainty ~ leverage_lag1 + controls + FEs")
    lines.append("3. Manager_QA_Weak_Modal ~ leverage_lag1 + controls + FEs")
    lines.append("4. CEO_QA_Weak_Modal ~ leverage_lag1 + controls + FEs")
    lines.append("5. Manager_Pres_Uncertainty ~ leverage_lag1 + controls + FEs")
    lines.append("6. CEO_Pres_Uncertainty ~ leverage_lag1 + controls + FEs")
    lines.append("")

    output_path = output_dir / "H4_DATA_SUMMARY.md"
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
        description="H4 Leverage Discipline Data Preparation - Create analysis dataset for reverse causal test"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and setup without running data preparation"
    )
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Run data preparation only (skip regression execution)"
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
    dw.write("STEP 4.4: H4 Leverage Discipline Data Preparation\n")
    dw.write("=" * 80 + "\n")
    dw.write(f"Timestamp: {timestamp}\n")
    dw.write(f"Git SHA: {get_git_sha()}\n")
    dw.write(f"Config: {config.get('step_id', '4.4_H4_LeverageDiscipline')}\n")
    dw.write("")

    # Stats tracking
    stats = {
        'step_id': '4.4_H4_LeverageDiscipline',
        'timestamp': timestamp,
        'git_sha': get_git_sha(),
        'input': {},
        'processing': {},
        'output': {},
        'vif_diagnostics': {},
        'variable_availability': {},
        'timing': {},
        'memory': {},
    }

    start_time = time.time()
    start_mem = get_process_memory_mb()

    try:
        # Build list of all speech columns we need
        speech_cols = UNCERTAINTY_MEASURES + [ANALYST_UNCERTAINTY_VAR]
        speech_cols.extend([c for c in PRESENTATION_CONTROL_MAP.values() if c is not None])

        # Load H1 variables
        dw.write("\n[1] Loading H1 variables (leverage + base controls)...\n")
        h1_df = load_h1_variables(paths["h1_dir"], dw)

        stats['input']['h1_variables'] = {
            'rows': int(len(h1_df)),
            'source': str(paths["h1_dir"]),
        }

        # Load H3 variables
        dw.write("\n[2] Loading H3 variables (firm_maturity, earnings_volatility)...\n")
        h3_df = load_h3_variables(paths["h3_dir"], dw)

        stats['input']['h3_variables'] = {
            'rows': int(len(h3_df)),
            'source': str(paths["h3_dir"]),
        }

        # Load speech uncertainty
        dw.write("\n[3] Loading speech uncertainty data...\n")
        speech_df = load_speech_uncertainty(paths["speech_dir"], speech_cols, dw)

        stats['input']['speech_uncertainty'] = {
            'calls': int(len(speech_df)),
            'years': int(speech_df['start_date'].dt.year.nunique()),
            'source': str(paths["speech_dir"]),
        }

        if args.dry_run:
            dw.write("\n[Dry run] Validation complete. Exiting.\n")
            return

        # Aggregate speech to firm-year
        dw.write("\n[4] Aggregating speech data to firm-year level...\n")
        speech_agg = aggregate_speech_to_firmyear(speech_df, speech_cols, dw)

        stats['processing']['aggregation'] = {
            'firm_years': int(len(speech_agg)),
        }

        # Prepare analysis dataset
        dw.write("\n[5] Preparing H4 analysis dataset...\n")
        analysis_df, vif_result = prepare_analysis_dataset(
            h1_df, h3_df, speech_agg,
            UNCERTAINTY_MEASURES,
            ANALYST_UNCERTAINTY_VAR,
            VIF_COLUMNS,
            vif_threshold=5.0,
            dw=dw
        )

        stats['processing']['analysis_dataset'] = {
            'n_obs': int(len(analysis_df)),
            'n_firms': int(analysis_df['gvkey'].nunique()),
            'year_range': [int(analysis_df['fiscal_year'].min()), int(analysis_df['fiscal_year'].max())],
        }

        # VIF diagnostics
        if vif_result:
            stats['vif_diagnostics'] = {
                'condition_number': vif_result['condition_number'],
                'vif_violations': vif_result['vif_violations'],
                'pass': vif_result['pass'],
                'vif_values': {row['variable']: row['VIF']
                              for _, row in vif_result['vif_results'].iterrows()},
            }

        # Variable availability
        for var in UNCERTAINTY_MEASURES + ['analyst_qa_uncertainty'] + FINANCIAL_CONTROLS:
            if var in analysis_df.columns:
                n_valid = analysis_df[var].notna().sum()
                # Convert scalar to int (handle pandas 3.x Series behavior)
                try:
                    n_valid = int(n_valid.iloc[0] if hasattr(n_valid, 'iloc') else n_valid)
                except (AttributeError, IndexError):
                    n_valid = int(n_valid)
                pct_valid = float(n_valid / len(analysis_df) * 100)
                stats['variable_availability'][var] = {
                    'n_valid': n_valid,
                    'pct_valid': pct_valid,
                }

        # Save outputs
        dw.write("\n[6] Saving outputs...\n")
        save_analysis_dataset(analysis_df, paths["output_dir"] / "H4_Analysis_Dataset.parquet", dw)
        save_vif_results(vif_result, paths["output_dir"] / "vif_diagnostics.json", dw)
        generate_data_summary_markdown(analysis_df, vif_result, paths["output_dir"], dw)

        stats['output']['analysis_dataset'] = {
            'file': 'H4_Analysis_Dataset.parquet',
            'rows': int(len(analysis_df)),
            'columns': len(analysis_df.columns),
        }

        # Final stats
        end_time = time.time()
        end_mem = get_process_memory_mb()

        stats['timing']['duration_seconds'] = end_time - start_time
        stats['memory']['rss_mb_start'] = start_mem['rss_mb']
        stats['memory']['rss_mb_end'] = end_mem['rss_mb']

        save_stats(stats, paths["output_dir"], dw)

        # Summary
        dw.write("\n" + "=" * 80 + "\n")
        dw.write("EXECUTION SUMMARY\n")
        dw.write("=" * 80 + "\n")
        dw.write(f"  Duration: {stats['timing']['duration_seconds']:.2f} seconds\n")
        dw.write(f"  Analysis dataset: {len(analysis_df):,} obs, {analysis_df['gvkey'].nunique():,} firms\n")
        dw.write(f"  Output directory: {paths['output_dir']}\n")

        if vif_result:
            vif_pass = "PASS" if vif_result['pass'] else "WARNING"
            dw.write(f"  VIF check: {vif_pass}\n")
            if vif_result['vif_violations']:
                dw.write(f"    Violations: {vif_result['vif_violations']}\n")

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
