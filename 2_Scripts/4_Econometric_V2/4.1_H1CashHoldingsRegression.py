#!/usr/bin/env python3
"""
==============================================================================
STEP 4.1: H1 Cash Holdings Regression
==============================================================================
ID: 4.1_H1CashHoldingsRegression
Description: Panel OLS regressions for H1 (Speech Uncertainty & Cash Holdings).
             Tests whether vague managers hoard more cash (precautionary motive)
             and whether leverage moderates this effect (debt discipline).

Model Specification:
    CashHoldings_{t+1} = beta0 + beta1*Uncertainty_t + beta2*Leverage_t
                         + beta3*(Uncertainty_t * Leverage_t)
                         + gamma*Controls + Firm FE + Year FE + epsilon

Hypothesis Tests:
    H1a: beta1 > 0 (Higher uncertainty leads to more cash holdings)
    H1b: beta3 < 0 (Leverage attenuates the uncertainty-cash relationship)

Inputs:
    - 4_Outputs/3_Financial_V2/latest/H1_CashHoldings.parquet
      (cash_holdings, leverage, controls at firm-year level)
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_*.parquet
      (speech uncertainty measures at call level)

Outputs:
    - 4_Outputs/4_Econometric_V2/{timestamp}/H1_Regression_Results.parquet
      (all regression coefficients, SEs, p-values, diagnostics)
    - 4_Outputs/4_Econometric_V2/{timestamp}/stats.json
      (regression summaries, hypothesis tests, execution metadata)
    - 4_Outputs/4_Econometric_V2/{timestamp}/H1_RESULTS.md
      (human-readable summary of key findings)
    - 3_Logs/4_Econometric_V2/{timestamp}_H1.log
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

from shared.panel_ols import run_panel_ols
from shared.centering import center_continuous
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


UNCERTAINTY_MEASURES = [
    'Manager_QA_Uncertainty_pct',
    'CEO_QA_Uncertainty_pct',
    'Manager_QA_Weak_Modal_pct',
    'CEO_QA_Weak_Modal_pct',
    'Manager_Pres_Uncertainty_pct',
    'CEO_Pres_Uncertainty_pct',
]

CONTROL_VARS = [
    'firm_size', 'tobins_q', 'roa', 'capex_at',
    'dividend_payer', 'ocf_volatility', 'current_ratio'
]

SPECS = {
    'primary': {'entity_effects': True, 'time_effects': True, 'double_cluster': False},
    'pooled': {'entity_effects': False, 'time_effects': False, 'double_cluster': False},
    'year_only': {'entity_effects': False, 'time_effects': True, 'double_cluster': False},
    'double_cluster': {'entity_effects': True, 'time_effects': True, 'double_cluster': True},
}


# ==============================================================================
# Path Setup
# ==============================================================================


def setup_paths(config, timestamp):
    """Set up all required paths using get_latest_output_dir"""
    root = Path(__file__).parent.parent.parent

    # Resolve H1 variables directory
    h1_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H1_CashHoldings.parquet",
    )

    # Resolve speech uncertainty directory
    speech_dir = get_latest_output_dir(
        root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
        required_file="linguistic_variables_2002.parquet",  # At least one year must exist
    )

    paths = {
        "root": root,
        "h1_dir": h1_dir,
        "speech_dir": speech_dir,
    }

    # Output directory
    output_base = root / "4_Outputs" / "4_Econometric_V2"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "4_Econometric_V2"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H1.log"

    return paths


# ==============================================================================
# Data Loading
# ==============================================================================


def load_h1_variables(h1_dir, dw=None):
    """
    Load H1 Cash Holdings variables.

    Expects H1_CashHoldings.parquet with columns:
    - gvkey, fiscal_year, file_name
    - cash_holdings, leverage
    - Controls: firm_size, tobins_q, roa, capex_at, dividend_payer,
                ocf_volatility, current_ratio
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

    # Handle multiple observations per gvkey-year from firm controls merge
    # Take mean of controls to get one row per gvkey-fiscal_year
    if dw:
        unique_firm_years = df[['gvkey', 'fiscal_year']].drop_duplicates().shape[0]
        dw.write(f"    Unique firm-years: {unique_firm_years:,}\n")

    return df


def load_speech_uncertainty(speech_dir, uncertainty_cols, dw=None):
    """
    Load all linguistic_variables_*.parquet files and concatenate.

    Returns DataFrame with columns:
    - file_name, gvkey, start_date
    - uncertainty_cols (6 measures)
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
# Aggregation
# ==============================================================================


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

    # Compute mean of uncertainty columns, count of file_name
    agg_dict = {col: 'mean' for col in uncertainty_cols}
    agg_dict['file_name'] = 'count'

    agg_df = df.groupby(group_cols, as_index=False).agg(agg_dict)
    agg_df = agg_df.rename(columns={'file_name': 'n_calls'})

    if dw:
        mean_calls = agg_df['n_calls'].mean()
        dw.write(f"  Aggregated to {len(agg_df):,} firm-years, mean {mean_calls:.2f} calls per firm-year\n")

    return agg_df


# ==============================================================================
# Data Preparation
# ==============================================================================


def prepare_regression_data(h1_df, speech_agg_df, uncertainty_cols, dw=None):
    """
    Merge H1 variables with speech data and create lead dependent variable.

    Steps:
    1. Merge on gvkey and fiscal_year (inner join)
    2. Sort by gvkey and fiscal_year
    3. Create cash_holdings_lead via groupby shift(-1)
    4. Drop rows where lead is NaN (last year per firm)
    """
    # Merge H1 variables with aggregated speech data
    merge_cols = ['gvkey', 'fiscal_year']
    reg_df = h1_df.merge(speech_agg_df, on=merge_cols, how='inner')

    if dw:
        merge_rate = len(reg_df) / len(h1_df) * 100
        dw.write(f"  Merged: {len(reg_df):,} obs ({merge_rate:.1f}% of H1 data)\n")

    # Aggregate H1 data to one row per gvkey-fiscal_year before creating lead
    # (H1 has multiple obs per firm-year from firm controls merge)
    h1_agg = reg_df.groupby(['gvkey', 'fiscal_year'], as_index=False).agg({
        'cash_holdings': 'mean',
        'leverage': 'mean',
        'firm_size': 'mean',
        'tobins_q': 'mean',
        'roa': 'mean',
        'capex_at': 'mean',
        'dividend_payer': 'mean',
        'ocf_volatility': 'mean',
        'current_ratio': 'mean',
        **{col: 'mean' for col in uncertainty_cols},
        'n_calls': 'mean',
    })

    # Sort and create lead dependent variable
    h1_agg = h1_agg.sort_values(['gvkey', 'fiscal_year'])
    h1_agg['cash_holdings_lead'] = h1_agg.groupby('gvkey')['cash_holdings'].shift(-1)

    # Drop NaN in lead (last year per firm)
    before_drop = len(h1_agg)
    reg_df = h1_agg.dropna(subset=['cash_holdings_lead'])
    after_drop = len(reg_df)
    dropped = before_drop - after_drop

    if dw:
        dw.write(f"  Lead variable created, dropped {dropped:,} obs (last year per firm)\n")
        dw.write(f"  Final regression sample: {len(reg_df):,} obs\n")

    return reg_df


# ==============================================================================
# Single Regression
# ==============================================================================


def run_single_h1_regression(df, uncertainty_var, spec_name, spec_config,
                             control_vars, vif_threshold=5.0, dw=None):
    """
    Run a single H1 regression with specified uncertainty measure and spec.

    Model:
        cash_holdings_lead ~ uncertainty_c + leverage_c + uncertainty_c:leverage_c
                            + controls

    Steps:
    1. Center uncertainty and leverage variables
    2. Create interaction term
    3. Build exog list
    4. Pre-flight VIF check on controls only (STRICT mode)
    5. Run panel OLS with specified FE config
    6. Extract results and perform one-tailed hypothesis tests

    Hypothesis tests:
    - H1a: beta1 > 0 (uncertainty coefficient)
      p_one_tail = p_two_tail / 2 if beta > 0, else 1 - p_two_tail/2
    - H1b: beta3 < 0 (interaction coefficient)
      p_one_tail = p_two_tail / 2 if beta < 0, else 1 - p_two_tail/2
    """
    df_work = df.copy()

    # Center variables
    vars_to_center = [uncertainty_var, 'leverage']
    df_work, means = center_continuous(df_work, vars_to_center, suffix='_c')

    # Create interaction term
    uncertainty_c = f"{uncertainty_var}_c"
    leverage_c = 'leverage_c'
    interaction_col = f"{uncertainty_var}_x_leverage"
    df_work[interaction_col] = df_work[uncertainty_c] * df_work[leverage_c]

    # Build exog list
    exog = [uncertainty_c, leverage_c, interaction_col] + control_vars

    # Pre-flight VIF check on control variables only (not interaction terms)
    # Note: We only fail on VIF violations, not condition number, because
    # high condition numbers are common with multiple controls and fixed effects.
    # VIF is the more relevant diagnostic for multicollinearity concerns.
    controls_only = [c for c in control_vars if c in df_work.columns]
    try:
        vif_result = check_multicollinearity(
            df_work, controls_only, vif_threshold=vif_threshold,
            condition_threshold=1000.0,  # Relaxed condition threshold
            fail_on_violation=True  # Only fails on VIF violations with relaxed condition threshold
        )
    except MulticollinearityError as e:
        if dw:
            dw.write(f"  VIF check failed: {e}\n")
        raise

    # Run panel OLS
    cluster_cols = ['gvkey', 'fiscal_year'] if spec_config['double_cluster'] else ['gvkey']

    result = run_panel_ols(
        df=df_work,
        dependent='cash_holdings_lead',
        exog=exog,
        entity_col='gvkey',
        time_col='fiscal_year',
        entity_effects=spec_config['entity_effects'],
        time_effects=spec_config['time_effects'],
        cov_type='clustered',
        cluster_cols=cluster_cols,
        check_collinearity=False,  # Already checked above
        vif_threshold=vif_threshold,
    )

    # Extract results
    coeffs_df = result['coefficients']
    summary = result['summary']

    # Get coefficients of interest
    beta1_name = uncertainty_c
    beta3_name = interaction_col

    beta1 = coeffs_df.loc[beta1_name, 'Coefficient'] if beta1_name in coeffs_df.index else np.nan
    beta3 = coeffs_df.loc[beta3_name, 'Coefficient'] if beta3_name in coeffs_df.index else np.nan

    # Get p-values
    pvalues = result['model'].pvalues
    p1_two = pvalues.get(beta1_name, np.nan)
    p3_two = pvalues.get(beta3_name, np.nan)

    # One-tailed hypothesis tests
    # H1a: beta1 > 0 (positive coefficient supports hypothesis)
    if not np.isnan(p1_two) and not np.isnan(beta1):
        if beta1 > 0:
            p1_one = p1_two / 2
        else:
            p1_one = 1 - p1_two / 2
    else:
        p1_one = np.nan

    # H1b: beta3 < 0 (negative coefficient supports hypothesis)
    if not np.isnan(p3_two) and not np.isnan(beta3):
        if beta3 < 0:
            p3_one = p3_two / 2
        else:
            p3_one = 1 - p3_two / 2
    else:
        p3_one = np.nan

    # Hypothesis test outcomes
    h1a_supported = (not np.isnan(p1_one)) and (p1_one < 0.05) and (beta1 > 0)
    h1b_supported = (not np.isnan(p3_one)) and (p3_one < 0.05) and (beta3 < 0)

    return {
        'spec': spec_name,
        'uncertainty_var': uncertainty_var,
        'n_obs': summary['nobs'],
        'r_squared': summary['rsquared'],
        'r_squared_within': summary.get('rsquared_within', None),
        'f_stat': summary.get('f_statistic', None),
        'f_pvalue': summary.get('f_pvalue', None),
        'coefficients': coeffs_df.to_dict('index'),
        'pvalues': pvalues.to_dict(),
        'beta1': beta1,
        'beta1_se': coeffs_df.loc[beta1_name, 'Std. Error'] if beta1_name in coeffs_df.index else np.nan,
        'beta1_t': coeffs_df.loc[beta1_name, 't-stat'] if beta1_name in coeffs_df.index else np.nan,
        'beta1_p_two': p1_two,
        'beta1_p_one': p1_one,
        'beta1_signif': h1a_supported,
        'beta3': beta3,
        'beta3_se': coeffs_df.loc[beta3_name, 'Std. Error'] if beta3_name in coeffs_df.index else np.nan,
        'beta3_t': coeffs_df.loc[beta3_name, 't-stat'] if beta3_name in coeffs_df.index else np.nan,
        'beta3_p_two': p3_two,
        'beta3_p_one': p3_one,
        'beta3_signif': h1b_supported,
        'centering_means': means,
        'warnings': result.get('warnings', []),
    }


# ==============================================================================
# Main Regression Loop
# ==============================================================================


def run_all_h1_regressions(reg_df, uncertainty_measures, specs, control_vars,
                          vif_threshold=5.0, dw=None):
    """
    Run all H1 regressions: 6 uncertainty measures x 4 specifications = 24 total.

    Returns list of regression result dictionaries.
    """
    results = []

    for uncertainty_var in uncertainty_measures:
        for spec_name, spec_config in specs.items():
            if dw:
                dw.write(f"\nRunning: {uncertainty_var} x {spec_name}\n")

            result = run_single_h1_regression(
                reg_df, uncertainty_var, spec_name, spec_config,
                control_vars, vif_threshold, dw
            )

            results.append(result)

            if dw:
                dw.write(f"  N={result['n_obs']}, R2={result['r_squared']:.4f}, "
                        f"beta1={result['beta1']:.4f} (p1={result['beta1_p_one']:.4f}), "
                        f"beta3={result['beta3']:.4f} (p3={result['beta3_p_one']:.4f})\n")

    return results


# ==============================================================================
# Output Functions
# ==============================================================================


def save_regression_results(results, output_dir, dw=None):
    """
    Save regression results to parquet file.

    Creates long-format DataFrame with columns:
    - spec, uncertainty_var, variable, coefficient, se, t_stat, p_value
    - n_obs, r_squared, r_squared_within, f_stat, f_pvalue
    - hypothesis_test (for beta1 and beta3)
    """
    rows = []

    for r in results:
        base_info = {
            'spec': r['spec'],
            'uncertainty_var': r['uncertainty_var'],
            'n_obs': r['n_obs'],
            'r_squared': r['r_squared'],
            'r_squared_within': r['r_squared_within'],
            'f_stat': r['f_stat'],
            'f_pvalue': r['f_pvalue'],
        }

        # Add each coefficient
        for var_name, coeff_dict in r['coefficients'].items():
            row = base_info.copy()
            row['variable'] = var_name
            row['coefficient'] = coeff_dict['Coefficient']
            row['se'] = coeff_dict['Std. Error']
            row['t_stat'] = coeff_dict['t-stat']
            row['p_value'] = r['pvalues'].get(var_name, np.nan)

            # Mark hypothesis test variables
            if var_name.endswith('_c') and '_x_leverage' not in var_name:
                # This is an uncertainty main effect (beta1 equivalent)
                row['hypothesis_test'] = 'H1a_beta1'
                row['p_value_one_tail'] = r['beta1_p_one']
                row['hypothesis_supported'] = r['beta1_signif']
            elif f'{r["uncertainty_var"]}_x_leverage' in var_name:
                # This is the interaction (beta3)
                row['hypothesis_test'] = 'H1b_beta3'
                row['p_value_one_tail'] = r['beta3_p_one']
                row['hypothesis_supported'] = r['beta3_signif']
            else:
                row['hypothesis_test'] = None
                row['p_value_one_tail'] = np.nan
                row['hypothesis_supported'] = None

            rows.append(row)

    results_df = pd.DataFrame(rows)
    output_path = output_dir / "H1_Regression_Results.parquet"
    results_df.to_parquet(output_path, index=False)

    if dw:
        dw.write(f"\nSaved: {output_path.name} ({len(results_df)} rows)\n")

    return results_df


def generate_results_markdown(results, output_dir, dw=None):
    """
    Generate human-readable markdown summary of H1 regression results.
    """
    lines = []
    lines.append("# H1 Cash Holdings Regression Results")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Hypothesis")
    lines.append("")
    lines.append("- **H1a:** Higher speech uncertainty leads to more cash holdings (beta1 > 0)")
    lines.append("- **H1b:** Leverage attenuates the uncertainty-cash relationship (beta3 < 0)")
    lines.append("")

    # Summary table: Primary specification
    lines.append("## Primary Specification Results")
    lines.append("")
    lines.append("Firm + Year FE, clustered SE at firm level")
    lines.append("")
    lines.append("| Uncertainty Measure | N | R2 | beta1 (SE) | p1 | beta3 (SE) | p3 | H1a | H1b |")
    lines.append("|---|---|---|---|---|---|---|---|---|")

    for r in results:
        if r['spec'] == 'primary':
            uncertainty = r['uncertainty_var']
            n = r['n_obs']
            r2 = r['r_squared']
            beta1 = r['beta1']
            beta1_se = r['beta1_se']
            p1 = r['beta1_p_one']
            beta3 = r['beta3']
            beta3_se = r['beta3_se']
            p3 = r['beta3_p_one']
            h1a = 'Yes' if r['beta1_signif'] else 'No'
            h1b = 'Yes' if r['beta3_signif'] else 'No'

            lines.append(f"| {uncertainty} | {n:,} | {r2:.4f} | "
                        f"{beta1:.4f} ({beta1_se:.4f}) | {p1:.4f} | "
                        f"{beta3:.4f} ({beta3_se:.4f}) | {p3:.4f} | {h1a} | {h1b} |")

    lines.append("")
    lines.append("*Significance: p < 0.05 (one-tailed)")
    lines.append("")

    # Hypothesis test outcomes summary
    lines.append("## Hypothesis Test Outcomes")
    lines.append("")

    # Count significant results
    h1a_count = sum(1 for r in results if r['spec'] == 'primary' and r['beta1_signif'])
    h1b_count = sum(1 for r in results if r['spec'] == 'primary' and r['beta3_signif'])

    lines.append(f"**Primary Specification:**")
    lines.append(f"- H1a (beta1 > 0): {h1a_count}/6 measures significant")
    lines.append(f"- H1b (beta3 < 0): {h1b_count}/6 measures significant")
    lines.append("")

    # List significant measures
    h1a_measures = [r['uncertainty_var'] for r in results
                    if r['spec'] == 'primary' and r['beta1_signif']]
    h1b_measures = [r['uncertainty_var'] for r in results
                    if r['spec'] == 'primary' and r['beta3_signif']]

    if h1a_measures:
        lines.append(f"**Supporting H1a (beta1 > 0):** {', '.join(h1a_measures)}")
    else:
        lines.append("**No measures support H1a**")

    if h1b_measures:
        lines.append(f"**Supporting H1b (beta3 < 0):** {', '.join(h1b_measures)}")
    else:
        lines.append("**No measures support H1b**")

    lines.append("")

    # Key findings
    lines.append("## Key Findings")
    lines.append("")

    # Find strongest effects
    primary_results = [r for r in results if r['spec'] == 'primary']

    if primary_results:
        # Sort by beta1 p-value
        sorted_by_h1a = sorted(primary_results, key=lambda x: x['beta1_p_one'] if not np.isnan(x['beta1_p_one']) else 1)
        top_h1a = [r for r in sorted_by_h1a if r['beta1_signif']]

        if top_h1a:
            lines.append(f"**Strongest support for H1a:**")
            for r in top_h1a[:3]:
                lines.append(f"- {r['uncertainty_var']}: beta1={r['beta1']:.4f}, p={r['beta1_p_one']:.4f}")

        # Sort by beta3 p-value
        sorted_by_h1b = sorted(primary_results, key=lambda x: x['beta3_p_one'] if not np.isnan(x['beta3_p_one']) else 1)
        top_h1b = [r for r in sorted_by_h1b if r['beta3_signif']]

        if top_h1b:
            lines.append(f"**Strongest support for H1b:**")
            for r in top_h1b[:3]:
                lines.append(f"- {r['uncertainty_var']}: beta3={r['beta3']:.4f}, p={r['beta3_p_one']:.4f}")

    lines.append("")

    # Specification comparison
    lines.append("## Specification Comparison")
    lines.append("")
    lines.append("| Spec | Entity FE | Time FE | Cluster |")
    lines.append("|---|---|---|---|")
    lines.append("| primary | Yes | Yes | firm |")
    lines.append("| pooled | No | No | firm |")
    lines.append("| year_only | No | Yes | firm |")
    lines.append("| double_cluster | Yes | Yes | firm+year |")
    lines.append("")

    output_path = output_dir / "H1_RESULTS.md"
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
        description="H1 Cash Holdings Regression - Panel OLS with Uncertainty x Leverage interaction"
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
    dw.write("STEP 4.1: H1 Cash Holdings Regression\n")
    dw.write("=" * 80 + "\n")
    dw.write(f"Timestamp: {timestamp}\n")
    dw.write(f"Git SHA: {get_git_sha()}\n")
    dw.write(f"Config: {config.get('step_id', '4.1_H1CashHoldingsRegression')}\n")
    dw.write("")

    # Stats tracking
    stats = {
        'step_id': '4.1_H1CashHoldingsRegression',
        'timestamp': timestamp,
        'git_sha': get_git_sha(),
        'input': {},
        'processing': {},
        'output': {},
        'regressions': [],
        'timing': {},
        'memory': {},
    }

    start_time = time.time()
    start_mem = get_process_memory_mb()

    try:
        # Load H1 variables
        dw.write("\n[1] Loading H1 variables...\n")
        h1_df = load_h1_variables(paths["h1_dir"], dw)

        stats['input']['h1_variables'] = {
            'rows': int(len(h1_df)),
            'unique_firm_years': int(h1_df[['gvkey', 'fiscal_year']].drop_duplicates().shape[0]),
            'source': str(paths["h1_dir"]),
        }

        # Load speech uncertainty
        dw.write("\n[2] Loading speech uncertainty data...\n")
        speech_df = load_speech_uncertainty(paths["speech_dir"], UNCERTAINTY_MEASURES, dw)

        stats['input']['speech_uncertainty'] = {
            'calls': int(len(speech_df)),
            'years': int(speech_df['start_date'].dt.year.nunique()),
            'source': str(paths["speech_dir"]),
        }

        if args.dry_run:
            dw.write("\n[Dry run] Validation complete. Exiting.\n")
            return

        # Aggregate speech to firm-year
        dw.write("\n[3] Aggregating speech data to firm-year level...\n")
        speech_agg = aggregate_speech_to_firmyear(speech_df, UNCERTAINTY_MEASURES, dw)

        stats['processing']['aggregation'] = {
            'firm_years': int(len(speech_agg)),
        }

        # Prepare regression data
        dw.write("\n[4] Preparing regression data...\n")
        reg_df = prepare_regression_data(h1_df, speech_agg, UNCERTAINTY_MEASURES, dw)

        stats['processing']['regression_prep'] = {
            'final_obs': int(len(reg_df)),
            'unique_firms': int(reg_df['gvkey'].nunique()),
            'year_range': [int(reg_df['fiscal_year'].min()), int(reg_df['fiscal_year'].max())],
        }

        # Run all regressions
        dw.write("\n[5] Running H1 regressions...\n")
        dw.write(f"  {len(UNCERTAINTY_MEASURES)} uncertainty measures x {len(SPECS)} specifications = "
                f"{len(UNCERTAINTY_MEASURES) * len(SPECS)} regressions\n")

        results = run_all_h1_regressions(
            reg_df, UNCERTAINTY_MEASURES, SPECS, CONTROL_VARS,
            vif_threshold=5.0, dw=dw
        )

        stats['regressions'] = [{
            'spec': r['spec'],
            'uncertainty_var': r['uncertainty_var'],
            'n_obs': r['n_obs'],
            'r_squared': r['r_squared'],
            'beta1': r['beta1'],
            'beta1_p_one': r['beta1_p_one'],
            'beta1_signif': r['beta1_signif'],
            'beta3': r['beta3'],
            'beta3_p_one': r['beta3_p_one'],
            'beta3_signif': r['beta3_signif'],
        } for r in results]

        # Save outputs
        dw.write("\n[6] Saving outputs...\n")
        results_df = save_regression_results(results, paths["output_dir"], dw)
        generate_results_markdown(results, paths["output_dir"], dw)

        stats['output']['regression_results'] = {
            'file': 'H1_Regression_Results.parquet',
            'rows': int(len(results_df)),
            'regressions': len(results),
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
        dw.write(f"  Regressions: {len(results)}\n")
        dw.write(f"  Output directory: {paths['output_dir']}\n")

        # Count significant results
        primary_signif_h1a = sum(1 for r in results if r['spec'] == 'primary' and r['beta1_signif'])
        primary_signif_h1b = sum(1 for r in results if r['spec'] == 'primary' and r['beta3_signif'])

        dw.write(f"\n  Primary spec - H1a (beta1 > 0): {primary_signif_h1a}/6 significant\n")
        dw.write(f"  Primary spec - H1b (beta3 < 0): {primary_signif_h1b}/6 significant\n")
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
