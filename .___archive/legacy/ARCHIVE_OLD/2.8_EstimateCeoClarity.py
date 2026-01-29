#!/usr/bin/env python3
"""
==============================================================================
STEP 2.8: Estimate CEO Fixed Effects & Compute Clarity Scores
==============================================================================
ID: 2.8_EstimateCeoClarity
Description: Estimates OLS regression with CEO fixed effects to extract
             persistent CEO communication style (g_i coefficients), then
             computes standardized Clarity scores (ClarityCEO = -g_i).

Model:
    UncAnsCEO_it = alpha + g_i*CEO_i + beta_s*Speech_it + beta_k*FirmChars_it + Year_t + epsilon_it

Inputs:
    - config/project.yaml
    - 4_Outputs/2.7_BuildFinancialControls/latest/calls_with_controls_YYYY.parquet
Outputs:
    - 4_Outputs/2.8_EstimateCeoClarity/TIMESTAMP/ceo_clarity_scores.parquet
    - 4_Outputs/2.8_EstimateCeoClarity/TIMESTAMP/calls_with_clarity.parquet
    - 4_Outputs/2.8_EstimateCeoClarity/TIMESTAMP/regression_results.txt
    - 4_Outputs/2.8_EstimateCeoClarity/TIMESTAMP/model_diagnostics.csv
    - 4_Outputs/2.8_EstimateCeoClarity/TIMESTAMP/report_step_08.md
    - 4_Outputs/2.8_EstimateCeoClarity/latest/ (symlink)
    - 3_Logs/2.8_EstimateCeoClarity/TIMESTAMP.log
Deterministic: true
==============================================================================
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import yaml
import shutil
import warnings

# Try importing statsmodels
try:
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    STATSMODELS_AVAILABLE = True
except ImportError:
    print("ERROR: statsmodels not available. Install with: pip install statsmodels")
    STATSMODELS_AVAILABLE = False
    sys.exit(1)

warnings.filterwarnings('ignore', category=FutureWarning)

# ==============================================================================
# Dual-write logging utility
# ==============================================================================

class DualWriter:
    """Writes to both stdout and log file verbatim"""
    def __init__(self, log_path):
        self.terminal = sys.stdout
        self.log = open(log_path, 'w', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()

def print_dual(msg):
    """Print to both terminal and log"""
    print(msg, flush=True)

# ==============================================================================
# Configuration and setup
# ==============================================================================

def load_config():
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent / "config" / "project.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_paths(config):
    """Set up all required paths"""
    root = Path(__file__).parent.parent

    paths = {
        'root': root,
        'controls_dir': root / '4_Outputs' / '2.7_BuildFinancialControls' / 'latest',
    }

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config['paths']['outputs'] / "2.8_EstimateCeoClarity"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)

    paths['latest_dir'] = output_base / "latest"

    # Create log directory
    log_base = root / config['paths']['logs'] / "2.8_EstimateCeoClarity"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}.log"

    return paths, timestamp

# ==============================================================================
# Data loading and preparation
# ==============================================================================

def load_controls_data(controls_dir, year_start, year_end):
    """Load calls with financial controls from Step 2.7"""
    print_dual("\n" + "="*60)
    print_dual("Loading calls with financial controls")
    print_dual("="*60)

    all_data = []
    for year in range(year_start, year_end + 1):
        file_path = controls_dir / f"calls_with_controls_{year}.parquet"
        if not file_path.exists():
            print_dual(f"  WARNING: Missing {file_path.name}, skipping year {year}")
            continue

        df = pd.read_parquet(file_path)
        print_dual(f"  Loaded {year}: {len(df):,} calls")
        all_data.append(df)

    if not all_data:
        raise FileNotFoundError("No control data found")

    combined = pd.concat(all_data, ignore_index=True)
    print_dual(f"\nTotal calls loaded: {len(combined):,}")
    print_dual(f"Unique firms (gvkey): {combined['gvkey'].nunique():,}")
    print_dual(f"Unique CEOs: {combined['ceo_id'].nunique():,}")

    return combined

def prepare_regression_data(df, config):
    """Prepare data for regression: filter, rename, create dummies"""
    print_dual("\n" + "="*60)
    print_dual("Preparing regression data")
    print_dual("="*60)

    initial_n = len(df)

    # Filter to calls with non-null ceo_id
    df = df[df['ceo_id'].notna()].copy()
    print_dual(f"  After filtering to non-null ceo_id: {len(df):,} / {initial_n:,}")

    # Keep our original pipeline variable names
    # Mapping for reference (our names -> paper names):
    #   MaQaUnc_pct -> UncAnsCEO (Manager Q&A Uncertainty %)
    #   MaPresUnc_pct -> UncPreCEO (Manager Presentation Uncertainty %)
    #   AnaQaUnc_pct -> UncQue (Analyst Q&A Uncertainty %)
    #   EntireCallNeg_pct -> NegCall (Entire Call Negativity %)
    #   ceo_id -> CEO_ID
    
    # Only rename ceo_id for categorical treatment
    if 'ceo_id' in df.columns:
        df.rename(columns={'ceo_id': 'CEO_ID'}, inplace=True)

    # Ensure we have all required variables (using OUR pipeline names)
    required_vars = ['MaQaUnc_pct', 'MaPresUnc_pct', 'AnaQaUnc_pct', 'EntireCallNeg_pct', 'CEO_ID',
                     'StockRet', 'MarketRet', 'EPS_Growth', 'SurpDec', 'year']

    # Add year if not present
    if 'year' not in df.columns:
        df['year'] = pd.to_datetime(df['start_date']).dt.year

    # Filter to complete cases
    print_dual("\n  Filtering to complete cases (all controls non-null)...")
    for var in required_vars:
        if var not in df.columns:
            print_dual(f"    ERROR: Required variable '{var}' not found!")
            return None

    complete_mask = df[required_vars].notna().all(axis=1)
    df_complete = df[complete_mask].copy()

    print_dual(f"  Complete cases: {len(df_complete):,} / {len(df):,} ({len(df_complete)/len(df)*100:.1f}%)")

    # Filter to CEOs with minimum calls
    min_calls = config['step_08']['regression']['min_calls_per_ceo']
    ceo_counts = df_complete['CEO_ID'].value_counts()
    valid_ceos = ceo_counts[ceo_counts >= min_calls].index

    df_complete = df_complete[df_complete['CEO_ID'].isin(valid_ceos)].copy()
    print_dual(f"  After filtering to CEOs with >={min_calls} calls: {len(df_complete):,} calls, {df_complete['CEO_ID'].nunique():,} CEOs")

    # Convert CEO_ID to string for categorical treatment
    df_complete['CEO_ID'] = df_complete['CEO_ID'].astype(str)
    df_complete['year'] = df_complete['year'].astype(str)

    print_dual(f"\n  Final regression sample:")
    print_dual(f"    Calls: {len(df_complete):,}")
    print_dual(f"    CEOs: {df_complete['CEO_ID'].nunique():,}")
    print_dual(f"    Firms: {df_complete['gvkey'].nunique():,}")
    print_dual(f"    Years: {sorted(df_complete['year'].astype(int).unique())}")

    return df_complete

# ==============================================================================
# Regression estimation
# ==============================================================================

def estimate_ceo_fixed_effects(df, config):
    """Estimate OLS with CEO fixed effects"""
    print_dual("\n" + "="*60)
    print_dual("Estimating CEO fixed effects regression")
    print_dual("="*60)

    # Build formula
    dep_var = config['step_08']['regression']['dependent_var']
    ling_controls = config['step_08']['regression']['linguistic_controls']
    firm_controls = config['step_08']['regression']['firm_controls']

    formula_parts = [dep_var, '~']

    # CEO fixed effects
    formula_parts.append('C(CEO_ID)')

    # Linguistic controls
    for var in ling_controls:
        formula_parts.append(f'+ {var}')

    # Firm controls
    for var in firm_controls:
        formula_parts.append(f'+ {var}')

    # Year fixed effects
    formula_parts.append('+ C(year)')

    formula = ' '.join(formula_parts)

    print_dual(f"\n  Regression formula:")
    print_dual(f"    {formula}")

    print_dual(f"\n  Estimating model...")
    print_dual(f"    Observations: {len(df):,}")
    print_dual(f"    CEOs: {df['CEO_ID'].nunique():,}")
    print_dual(f"    (This may take several minutes...)")

    start_time = datetime.now()

    # Estimate model
    try:
        model = smf.ols(formula, data=df).fit()
    except Exception as e:
        print_dual(f"\n  ERROR: Regression failed: {e}")
        return None, None

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print_dual(f"\n  [OK] Estimation complete ({duration:.1f} seconds)")
    print_dual(f"\n  Model summary:")
    print_dual(f"    R-squared: {model.rsquared:.4f}")
    print_dual(f"    Adjusted R-squared: {model.rsquared_adj:.4f}")
    print_dual(f"    F-statistic: {model.fvalue:.2f}")
    print_dual(f"    Prob (F-statistic): {model.f_pvalue:.2e}")
    print_dual(f"    AIC: {model.aic:.2f}")
    print_dual(f"    BIC: {model.bic:.2f}")
    print_dual(f"    Number of parameters: {len(model.params)}")

    return model, df

# ==============================================================================
# Extract CEO fixed effects
# ==============================================================================

def extract_ceo_fixed_effects(model, df):
    """Extract g_i coefficients for each CEO"""
    print_dual("\n" + "="*60)
    print_dual("Extracting CEO fixed effects")
    print_dual("="*60)

    # Get all CEO coefficient names
    ceo_coef_names = [p for p in model.params.index if p.startswith('C(CEO_ID)')]

    print_dual(f"  Found {len(ceo_coef_names)} CEO fixed effect coefficients")

    # Parse CEO IDs from coefficient names
    # Format: C(CEO_ID)[T.12345.0]
    ceo_effects = {}
    for coef_name in ceo_coef_names:
        # Extract CEO_ID from bracket notation
        if '[T.' in coef_name:
            ceo_id = coef_name.split('[T.')[1].split(']')[0]
            gamma_i = model.params[coef_name]
            ceo_effects[ceo_id] = gamma_i

    # Reference category (first CEO) has coefficient = 0
    # Find reference CEO
    all_ceos = df['CEO_ID'].unique()
    reference_ceo = [c for c in all_ceos if c not in ceo_effects]

    if len(reference_ceo) > 0:
        # Set reference CEO coefficient to 0
        ceo_effects[reference_ceo[0]] = 0.0
        print_dual(f"  Reference CEO (g=0): {reference_ceo[0]}")

    print_dual(f"  Total CEOs with coefficients: {len(ceo_effects)}")

    # Create DataFrame
    ceo_fe = pd.DataFrame([
        {'CEO_ID': ceo_id, 'gamma_i': gamma}
        for ceo_id, gamma in ceo_effects.items()
    ])

    # Compute Clarity = -gamma_i
    ceo_fe['ClarityCEO_raw'] = -ceo_fe['gamma_i']

    # Standardize globally
    mean_clarity = ceo_fe['ClarityCEO_raw'].mean()
    std_clarity = ceo_fe['ClarityCEO_raw'].std()

    ceo_fe['ClarityCEO'] = (ceo_fe['ClarityCEO_raw'] - mean_clarity) / std_clarity

    print_dual(f"\n  Clarity score statistics:")
    print_dual(f"    Mean (raw): {mean_clarity:.4f}")
    print_dual(f"    Std (raw): {std_clarity:.4f}")
    print_dual(f"    Mean (standardized): {ceo_fe['ClarityCEO'].mean():.4f}")
    print_dual(f"    Std (standardized): {ceo_fe['ClarityCEO'].std():.4f}")
    print_dual(f"    Min: {ceo_fe['ClarityCEO'].min():.4f}")
    print_dual(f"    Max: {ceo_fe['ClarityCEO'].max():.4f}")

    return ceo_fe

# ==============================================================================
# Compute CEO-level statistics
# ==============================================================================

def compute_ceo_level_stats(df, ceo_fe):
    """Compute descriptive stats for each CEO"""
    print_dual("\n" + "="*60)
    print_dual("Computing CEO-level statistics")
    print_dual("="*60)

    ceo_stats = df.groupby('CEO_ID').agg({
        'MaQaUnc_pct': ['count', 'mean', 'std'],  # Paper: UncAnsCEO
        'ceo_name': 'first',
        'start_date': ['min', 'max'],
        'gvkey': 'nunique'
    }).reset_index()

    ceo_stats.columns = ['CEO_ID', 'n_calls', 'avg_MaQaUnc', 'std_MaQaUnc',
                          'ceo_name', 'first_call_date', 'last_call_date', 'n_firms']

    # Merge with fixed effects
    ceo_scores = ceo_fe.merge(ceo_stats, on='CEO_ID', how='left')

    # Sort by Clarity (descending)
    ceo_scores = ceo_scores.sort_values('ClarityCEO', ascending=False).reset_index(drop=True)

    print_dual(f"  CEO-level dataset created: {len(ceo_scores):,} CEOs")

    # Show top/bottom 10
    print_dual(f"\n  Top 10 Clearest CEOs (highest Clarity):")
    for i, row in ceo_scores.head(10).iterrows():
        print_dual(f"    {i+1}. {row['ceo_name']} (ID: {row['CEO_ID']}): Clarity = {row['ClarityCEO']:.3f}, g = {row['gamma_i']:.4f}, n_calls = {row['n_calls']:.0f}")

    print_dual(f"\n  Top 10 Most Uncertain CEOs (lowest Clarity):")
    for i, row in ceo_scores.tail(10).iterrows():
        print_dual(f"    {i+1}. {row['ceo_name']} (ID: {row['CEO_ID']}): Clarity = {row['ClarityCEO']:.3f}, g = {row['gamma_i']:.4f}, n_calls = {row['n_calls']:.0f}")

    return ceo_scores

# ==============================================================================
# Merge clarity back to call level
# ==============================================================================

def merge_clarity_to_calls(df_full, ceo_scores):
    """Merge ClarityCEO back to call-level data"""
    print_dual("\n" + "="*60)
    print_dual("Merging Clarity scores to call-level data")
    print_dual("="*60)

    # Ensure CEO_ID is string in both
    df_full['CEO_ID'] = df_full.get('ceo_id', df_full.get('CEO_ID', np.nan)).astype(str)

    # Merge
    df_with_clarity = df_full.merge(
        ceo_scores[['CEO_ID', 'ClarityCEO', 'gamma_i']],
        on='CEO_ID',
        how='left'
    )

    n_matched = df_with_clarity['ClarityCEO'].notna().sum()
    print_dual(f"  Merged Clarity scores to {n_matched:,} / {len(df_with_clarity):,} calls ({n_matched/len(df_with_clarity)*100:.1f}%)")

    return df_with_clarity

# ==============================================================================
# Model diagnostics
# ==============================================================================

def compute_diagnostics(model, df):
    """Compute model diagnostics"""
    print_dual("\n" + "="*60)
    print_dual("Computing model diagnostics")
    print_dual("="*60)

    diagnostics = {
        'n_obs': int(model.nobs),
        'n_params': len(model.params),
        'r_squared': float(model.rsquared),
        'adj_r_squared': float(model.rsquared_adj),
        'f_statistic': float(model.fvalue),
        'f_pvalue': float(model.f_pvalue),
        'aic': float(model.aic),
        'bic': float(model.bic),
        'log_likelihood': float(model.llf),
        'mse_resid': float(model.mse_resid),
        'mse_model': float(model.mse_model),
        'mse_total': float(model.mse_total),
    }

    # Check residual normality (Jarque-Bera test)
    from scipy import stats
    jb_stat, jb_pvalue = stats.jarque_bera(model.resid)
    diagnostics['jarque_bera_stat'] = float(jb_stat)
    diagnostics['jarque_bera_pvalue'] = float(jb_pvalue)

    print_dual(f"\n  Diagnostics:")
    for key, val in diagnostics.items():
        if isinstance(val, float):
            print_dual(f"    {key}: {val:.4f}")
        else:
            print_dual(f"    {key}: {val}")

    return diagnostics

# ==============================================================================
# Save outputs
# ==============================================================================

def save_outputs(ceo_scores, df_with_clarity, model, diagnostics, paths, config):
    """Save all outputs"""
    print_dual("\n" + "="*60)
    print_dual("Saving outputs")
    print_dual("="*60)

    # CEO-level scores
    ceo_file = paths['output_dir'] / config['step_08']['outputs']['ceo_scores']
    ceo_scores.to_parquet(ceo_file, index=False, compression='snappy')
    print_dual(f"  Saved CEO scores: {ceo_file.name} ({len(ceo_scores):,} CEOs)")

    # Call-level data with clarity
    # Save by year
    df_with_clarity['year'] = pd.to_datetime(df_with_clarity['start_date']).dt.year
    year_start = df_with_clarity['year'].min()
    year_end = df_with_clarity['year'].max()

    for year in range(year_start, year_end + 1):
        year_data = df_with_clarity[df_with_clarity['year'] == year].copy()
        if len(year_data) == 0:
            continue

        year_file = paths['output_dir'] / f"calls_with_clarity_{year}.parquet"
        year_data.to_parquet(year_file, index=False, compression='snappy')
        print_dual(f"  Saved {year}: {len(year_data):,} calls")

    # Regression results (text)
    results_file = paths['output_dir'] / config['step_08']['outputs']['regression_output']
    with open(results_file, 'w') as f:
        f.write(str(model.summary()))
    print_dual(f"  Saved regression results: {results_file.name}")

    # Diagnostics (CSV)
    diag_file = paths['output_dir'] / config['step_08']['outputs']['diagnostics']
    pd.DataFrame([diagnostics]).to_csv(diag_file, index=False)
    print_dual(f"  Saved diagnostics: {diag_file.name}")

    # Update latest symlink
    print_dual("\nUpdating latest symlink...")
    if paths['latest_dir'].exists():
        if paths['latest_dir'].is_symlink():
            paths['latest_dir'].unlink()
        else:
            shutil.rmtree(paths['latest_dir'])

    try:
        paths['latest_dir'].symlink_to(paths['output_dir'].name, target_is_directory=True)
        print_dual(f"  Created symlink: latest -> {paths['output_dir'].name}")
    except OSError:
        shutil.copytree(paths['output_dir'], paths['latest_dir'])
        print_dual(f"  Created copy: latest")

# ==============================================================================
# Generate report
# ==============================================================================

def generate_report(ceo_scores, diagnostics, paths, config, duration):
    """Generate markdown report"""
    report_path = paths['output_dir'] / config['step_08']['outputs']['summary_report']

    report = []
    report.append("# STEP 2.8: Estimate CEO Clarity - Report\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**Process Version:** {config['project']['version']}\n")
    report.append(f"**Script:** 2.8_EstimateCeoClarity.py\n")
    report.append("\n---\n")

    report.append("## Model Specification\n")
    report.append("```\n")
    report.append("UncAnsCEO_it = alpha + g_i*CEO_i + beta_s*Speech_it + beta_k*FirmChars_it + Year_t + epsilon_it\n")
    report.append("```\n")
    report.append("\n---\n")

    report.append("## Sample Summary\n")
    report.append(f"- **Observations**: {diagnostics['n_obs']:,}\n")
    report.append(f"- **CEOs**: {len(ceo_scores):,}\n")
    report.append(f"- **Parameters**: {diagnostics['n_params']:,}\n")
    report.append("\n---\n")

    report.append("## Model Fit\n")
    report.append(f"- **R-squared**: {diagnostics['r_squared']:.4f}\n")
    report.append(f"- **Adjusted R-squared**: {diagnostics['adj_r_squared']:.4f}\n")
    report.append(f"- **F-statistic**: {diagnostics['f_statistic']:.2f} (p = {diagnostics['f_pvalue']:.2e})\n")
    report.append(f"- **AIC**: {diagnostics['aic']:.2f}\n")
    report.append(f"- **BIC**: {diagnostics['bic']:.2f}\n")
    report.append("\n---\n")

    report.append("## CEO Clarity Scores\n")
    report.append(f"- **Mean**: {ceo_scores['ClarityCEO'].mean():.4f}\n")
    report.append(f"- **Std**: {ceo_scores['ClarityCEO'].std():.4f}\n")
    report.append(f"- **Min**: {ceo_scores['ClarityCEO'].min():.4f}\n")
    report.append(f"- **Max**: {ceo_scores['ClarityCEO'].max():.4f}\n")
    report.append("\n---\n")

    report.append("## Top 10 Clearest CEOs\n")
    report.append("| Rank | CEO Name | CEO ID | Clarity | g_i | N Calls |\n")
    report.append("|------|----------|--------|---------|-----|--------|\n")
    for i, row in ceo_scores.head(10).iterrows():
        report.append(f"| {i+1} | {row['ceo_name']} | {row['CEO_ID']} | {row['ClarityCEO']:.3f} | {row['gamma_i']:.4f} | {row['n_calls']:.0f} |\n")

    report.append("\n---\n")

    report.append("## Top 10 Most Uncertain CEOs\n")
    report.append("| Rank | CEO Name | CEO ID | Clarity | g_i | N Calls |\n")
    report.append("|------|----------|--------|---------|-----|--------|\n")
    for i, row in ceo_scores.tail(10).iterrows():
        rank = len(ceo_scores) - i
        report.append(f"| {rank} | {row['ceo_name']} | {row['CEO_ID']} | {row['ClarityCEO']:.3f} | {row['gamma_i']:.4f} | {row['n_calls']:.0f} |\n")

    report.append("\n---\n")
    report.append(f"**Execution time:** {duration:.1f} seconds\n")
    report.append("\n**End of Report**\n")

    with open(report_path, 'w') as f:
        f.writelines(report)

    print_dual(f"\nReport saved: {report_path}")

# ==============================================================================
# Main execution
# ==============================================================================

def main():
    """Main execution"""
    start_time = datetime.now()

    # Load configuration
    config = load_config()
    paths, timestamp = setup_paths(config)

    year_start = config['data']['year_start']
    year_end = config['data']['year_end']

    # Set up dual-write logging
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer

    print_dual("="*80)
    print_dual("STEP 2.8: Estimate CEO Fixed Effects & Compute Clarity Scores")
    print_dual("="*80)
    print_dual(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_dual(f"Config: {config['project']['name']} v{config['project']['version']}")
    print_dual(f"Year range: {year_start}-{year_end}")
    print_dual(f"Log file: {paths['log_file']}")
    print_dual("")

    # Step 1: Load data
    df_full = load_controls_data(paths['controls_dir'], year_start, year_end)

    # Step 2: Prepare regression data
    df_regression = prepare_regression_data(df_full, config)
    if df_regression is None or len(df_regression) == 0:
        print_dual("\nERROR: No valid regression data. Exiting.")
        return

    # Step 3: Estimate model
    model, df_used = estimate_ceo_fixed_effects(df_regression, config)
    if model is None:
        print_dual("\nERROR: Model estimation failed. Exiting.")
        return

    # Step 4: Extract CEO fixed effects
    ceo_fe = extract_ceo_fixed_effects(model, df_used)

    # Step 5: Compute CEO-level stats
    ceo_scores = compute_ceo_level_stats(df_used, ceo_fe)

    # Step 6: Merge clarity to call level
    df_with_clarity = merge_clarity_to_calls(df_full, ceo_scores)

    # Step 7: Compute diagnostics
    diagnostics = compute_diagnostics(model, df_used)

    # Step 8: Save outputs
    save_outputs(ceo_scores, df_with_clarity, model, diagnostics, paths, config)

    # Step 9: Generate report
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    generate_report(ceo_scores, diagnostics, paths, config, duration)

    print_dual("\n" + "="*80)
    print_dual("STEP 2.8 COMPLETE")
    print_dual("="*80)
    print_dual(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_dual(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print_dual(f"Output directory: {paths['output_dir']}")
    print_dual("="*80)

    # Close log
    dual_writer.close()
    sys.stdout = dual_writer.terminal

if __name__ == "__main__":
    main()
