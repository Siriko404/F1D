#!/usr/bin/env python3
"""
==============================================================================
STEP 2.9b: Liquidity Regression (OLS and IV)
==============================================================================
ID: 2.9b_Regression_Liquidity
Description: Regresses Liquidity Measures on CEO Clarity and Presentation Uncertainty.
             - Model 1: Simple OLS
             - Model 2: Instrumented OLS (2SLS) using CCCL shift_intensity
             Reports Kleibergen-Paap (KP) rk F-statistic for weak identification.

Variables (our pipeline -> paper):
    - MaPresUnc_pct -> UncPreCEO
    - ClarityCEO -> Clarity (Fixed Effect)

Inputs:
    - config/project.yaml
    - 4_Outputs/2.9_LiquidityAnalysis/latest/calls_with_liquidity_YYYY.parquet
    - 4_Outputs/2.8_CeoClarityScores/latest/ceo_clarity_scores.parquet
    - 1_Inputs/CCCL instrument/instrument_shift_intensity_2005_2022.parquet
    - 1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet
Outputs:
    - 4_Outputs/2.9_LiquidityAnalysis/latest/regression_results_liquidity.txt
    - 3_Logs/2.9b_Regression_Liquidity/TIMESTAMP.log
==============================================================================
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import yaml
import statsmodels.api as sm
from statsmodels.sandbox.regression.gmm import IV2SLS

# ==============================================================================
# Dual-write logging
# ==============================================================================

class DualWriter:
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
    print(msg, flush=True)

# ==============================================================================
# Configuration
# ==============================================================================

def load_config():
    config_path = Path(__file__).parent.parent / "config" / "project.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_paths(config):
    root = Path(__file__).parent.parent
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    
    base_dir = root / config['paths']['outputs'] / "2.9_LiquidityAnalysis"
    latest_link = base_dir / "latest"
    
    # Input directory: use latest or most recent timestamped folder
    if latest_link.exists():
        input_dir = latest_link
    else:
        subdirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name != 'latest']
        if not subdirs:
            print_dual(f"ERROR: No output directories found in {base_dir}")
            sys.exit(1)
        input_dir = sorted(subdirs)[-1]
    
    # Output directory: create new timestamped folder
    output_dir = base_dir / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    log_dir = root / config['paths']['logs'] / "2.9b_Regression_Liquidity"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    return {
        'root': root,
        'input_dir': input_dir,
        'output_dir': output_dir,
        'latest_link': latest_link,
        'clarity_file': root / '4_Outputs' / '2.8_CeoClarityScores' / 'latest' / 'ceo_clarity_scores.parquet',
        'cccl_file': root / '1_Inputs' / 'CCCL instrument' / 'instrument_shift_intensity_2005_2022.parquet',
        'compustat_file': root / '1_Inputs' / 'comp_na_daily_all' / 'comp_na_daily_all.parquet',
        'log_file': log_dir / f"{timestamp}.log"
    }

# ==============================================================================
# Data Loading
# ==============================================================================

def load_data(paths):
    print_dual("\n[1] LOADING DATA...")
    
    # 1. Liquidity Data
    call_files = sorted(paths['input_dir'].glob("calls_with_liquidity_*.parquet"))
    if not call_files:
        print_dual(f"  ERROR: No liquidity files found in {paths['input_dir']}")
        return None
    df = pd.concat([pd.read_parquet(f) for f in call_files], ignore_index=True)
    print_dual(f"  Liquidity calls loaded: {len(df):,}")
    
    # 2. CEO Clarity Scores - check if already in data
    if 'ClarityCEO' in df.columns and df['ClarityCEO'].notna().sum() > 0:
        print_dual(f"  ClarityCEO already in data: {df['ClarityCEO'].notna().sum():,} values")
    elif paths['clarity_file'].exists():
        clarity = pd.read_parquet(paths['clarity_file'])
        print_dual(f"  Clarity scores loaded: {len(clarity):,}")
        if 'CEO_ID' in df.columns and 'CEO_ID' in clarity.columns:
            df = df.merge(clarity[['CEO_ID', 'ClarityCEO']].drop_duplicates('CEO_ID'), 
                         on='CEO_ID', how='left')
            print_dual(f"  After Clarity merge: {len(df):,} calls, {df['ClarityCEO'].notna().sum():,} with clarity")
    else:
        print_dual(f"  WARNING: Clarity file not found and ClarityCEO not in data")
        if 'ClarityCEO' not in df.columns:
            df['ClarityCEO'] = np.nan
    
    # 3. CCCL Instrument
    if paths['cccl_file'].exists():
        cccl = pd.read_parquet(paths['cccl_file'])
        # Prepare for merge
        if 'sic2' in cccl.columns and 'year' in cccl.columns:
            cccl = cccl.drop_duplicates(['sic2', 'year'])
            df['year'] = pd.to_datetime(df['start_date']).dt.year
            # Get SIC2 from ccm_sic or sic
            if 'ccm_sic' in df.columns:
                df['sic2'] = df['ccm_sic'].fillna(0).astype(str).str[:2].astype(int)
            elif 'sic' in df.columns:
                df['sic2'] = df['sic'].fillna(0).astype(str).str[:2].astype(int)
            else:
                df['sic2'] = 0
            df = df.merge(cccl[['sic2', 'year', 'shift_intensity']], on=['sic2', 'year'], how='left')
            print_dual(f"  CCCL instrument merged: {df['shift_intensity'].notna().sum():,} with instrument")
    else:
        print_dual(f"  WARNING: CCCL file not found at {paths['cccl_file']}")
        df['shift_intensity'] = np.nan
    
    # 4. Compustat Controls (Size, BM, Lev, ROA)
    if paths['compustat_file'].exists():
        print_dual("  Loading Compustat for firm controls...")
        comp = pd.read_parquet(paths['compustat_file'], 
                              columns=['gvkey', 'datadate', 'atq', 'ltq', 'ceqq', 'niq', 'cshoq', 'prccq'])
        comp['gvkey'] = comp['gvkey'].astype(str).str.zfill(6)
        comp['datadate'] = pd.to_datetime(comp['datadate'])
        
        # Calculate controls
        comp['atq'] = pd.to_numeric(comp['atq'], errors='coerce')
        comp['ltq'] = pd.to_numeric(comp['ltq'], errors='coerce')
        comp['ceqq'] = pd.to_numeric(comp['ceqq'], errors='coerce')
        comp['niq'] = pd.to_numeric(comp['niq'], errors='coerce')
        comp['cshoq'] = pd.to_numeric(comp['cshoq'], errors='coerce')
        comp['prccq'] = pd.to_numeric(comp['prccq'], errors='coerce')
        
        comp['Size'] = np.log(comp['atq'].clip(lower=1).astype(float))
        comp['BM'] = comp['ceqq'] / (comp['cshoq'] * comp['prccq']).clip(lower=0.01)
        comp['Lev'] = comp['ltq'] / comp['atq'].clip(lower=1)
        comp['ROA'] = comp['niq'] / comp['atq'].clip(lower=1)
        
        # Winsorize
        for col in ['Size', 'BM', 'Lev', 'ROA']:
            if col in comp.columns:
                p1, p99 = comp[col].quantile([0.01, 0.99])
                comp[col] = comp[col].clip(p1, p99)
        
        # Merge to calls (asof merge by gvkey and date)
        df['gvkey'] = df['gvkey'].astype(str).str.zfill(6)
        df['start_date'] = pd.to_datetime(df['start_date'])
        
        # merge_asof requires both to be sorted by the "on" key
        comp = comp.sort_values('datadate').reset_index(drop=True)
        df = df.sort_values('start_date').reset_index(drop=True)
        
        df = pd.merge_asof(df, comp[['gvkey', 'datadate', 'Size', 'BM', 'Lev', 'ROA']],
                          left_on='start_date', right_on='datadate', by='gvkey',
                          direction='backward')
        print_dual(f"  After Compustat merge: {df['Size'].notna().sum():,} with controls")
    
    return df

# ==============================================================================
# Regression Functions
# ==============================================================================

def run_ols_regression(df, dep_var, indep_vars, controls):
    """Run Simple OLS regression."""
    all_vars = indep_vars + controls
    reg_df = df[[dep_var] + all_vars].dropna()
    
    if len(reg_df) < 100:
        return None, f"Insufficient observations: {len(reg_df)}"
    
    X = sm.add_constant(reg_df[all_vars])
    y = reg_df[dep_var]
    
    model = sm.OLS(y, X).fit(cov_type='HC1')
    return model, None

def run_iv_regression(df, dep_var, endog_var, instrument, exog_vars):
    """Run IV 2SLS regression using statsmodels."""
    all_vars = [dep_var, endog_var, instrument] + exog_vars
    reg_df = df[all_vars].dropna().copy()
    
    if len(reg_df) < 100:
        return None, f"Insufficient observations: {len(reg_df)}"
    
    # Ensure all columns are float type
    for col in all_vars:
        reg_df[col] = pd.to_numeric(reg_df[col], errors='coerce')
    reg_df = reg_df.dropna()
    
    if len(reg_df) < 100:
        return None, f"Insufficient observations after type conversion: {len(reg_df)}"
    
    # Prepare matrices for statsmodels IV2SLS
    # y = dependent variable
    y = reg_df[dep_var].values.astype(float)
    
    # endog = endogenous variable (instrumented)
    endog = sm.add_constant(reg_df[[endog_var] + exog_vars].astype(float))
    
    # instrument = exogenous variables + the instrument
    instr = sm.add_constant(reg_df[[instrument] + exog_vars].astype(float))
    
    # Run IV2SLS
    model = IV2SLS(y, endog, instr).fit()
    
    return model, None

def calculate_kp_fstat(df, endog_var, instrument, exog_vars):
    """Calculate Kleibergen-Paap F-statistic for weak identification."""
    # First stage regression
    all_vars = [endog_var, instrument] + exog_vars
    reg_df = df[all_vars].dropna().copy()
    
    if len(reg_df) < 100:
        return np.nan
    
    # Ensure all columns are float type
    for col in all_vars:
        reg_df[col] = pd.to_numeric(reg_df[col], errors='coerce')
    reg_df = reg_df.dropna()
    
    if len(reg_df) < 100:
        return np.nan
    
    X = sm.add_constant(reg_df[[instrument] + exog_vars].astype(float))
    y = reg_df[endog_var].astype(float)
    
    first_stage = sm.OLS(y, X).fit(cov_type='HC1')
    
    # Get t-stat on instrument
    if instrument in first_stage.params.index:
        t_stat = first_stage.tvalues[instrument]
        f_stat = t_stat ** 2  # For single instrument, KP F = t^2
        return f_stat
    return np.nan

# ==============================================================================
# Main Execution
# ==============================================================================

def main():
    start_time = datetime.now()
    
    # Load config and setup paths
    config = load_config()
    paths = setup_paths(config)
    
    # Setup logging
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer
    
    print_dual("=" * 80)
    print_dual("STEP 2.9b: Liquidity Regression (OLS and IV)")
    print_dual("=" * 80)
    print_dual(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_dual(f"Log file: {paths['log_file']}")
    
    # Load data
    df = load_data(paths)
    if df is None:
        print_dual("ERROR: Failed to load data")
        return
    
    # Define variables
    dep_vars = ['Amihud', 'QuotedSpread', 'EffectiveSpread']  # Liquidity measures
    indep_vars = ['MaPresUnc_pct', 'ClarityCEO']
    controls = ['Size', 'BM', 'Lev', 'ROA']
    
    # Check available liquidity measures
    available_dep = [v for v in dep_vars if v in df.columns]
    if not available_dep:
        print_dual("ERROR: No liquidity measures found in data")
        return
    print_dual(f"\nAvailable liquidity measures: {available_dep}")
    
    # Results container
    results = []
    
    # ==============================================================================
    # Model 1: Simple OLS
    # ==============================================================================
    print_dual("\n" + "=" * 60)
    print_dual("MODEL 1: Simple OLS")
    print_dual("=" * 60)
    
    for dep_var in available_dep:
        print_dual(f"\n--- Dependent: {dep_var} ---")
        
        model, error = run_ols_regression(df, dep_var, indep_vars, controls)
        if error:
            print_dual(f"  {error}")
            continue
        
        print_dual(f"  N = {int(model.nobs):,}")
        print_dual(f"  R2 = {model.rsquared:.4f}")
        print_dual(f"\n  Coefficients:")
        for var in indep_vars:
            if var in model.params.index:
                coef = model.params[var]
                se = model.bse[var]
                t = model.tvalues[var]
                p = model.pvalues[var]
                sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
                print_dual(f"    {var:20s}: {coef:10.4f} (t={t:6.2f}) {sig}")
        
        results.append({
            'Model': 'OLS',
            'Dependent': dep_var,
            'N': int(model.nobs),
            'R2': model.rsquared,
            'MaPresUnc_coef': model.params.get('MaPresUnc_pct', np.nan),
            'MaPresUnc_pval': model.pvalues.get('MaPresUnc_pct', np.nan),
            'ClarityCEO_coef': model.params.get('ClarityCEO', np.nan),
            'ClarityCEO_pval': model.pvalues.get('ClarityCEO', np.nan),
        })
    
    # ==============================================================================
    # Model 2: Instrumented OLS (2SLS)
    # ==============================================================================
    print_dual("\n" + "=" * 60)
    print_dual("MODEL 2: Instrumented OLS (2SLS)")
    print_dual("Endogenous: MaPresUnc_pct | Instrument: shift_intensity")
    print_dual("=" * 60)
    
    for dep_var in available_dep:
        print_dual(f"\n--- Dependent: {dep_var} ---")
        
        # Calculate KP F-stat
        kp_f = calculate_kp_fstat(df, 'MaPresUnc_pct', 'shift_intensity', controls + ['ClarityCEO'])
        print_dual(f"  Kleibergen-Paap F-stat: {kp_f:.2f}" + (" (WEAK)" if kp_f < 10 else " (OK)"))
        
        model, error = run_iv_regression(df, dep_var, 'MaPresUnc_pct', 'shift_intensity', 
                                        controls + ['ClarityCEO'])
        if error:
            print_dual(f"  {error}")
            continue
        
        print_dual(f"  N = {int(model.nobs):,}")
        print_dual(f"  R2 = {model.rsquared:.4f}")
        print_dual(f"\n  Coefficients:")
        for var in ['MaPresUnc_pct', 'ClarityCEO']:
            if var in model.params.index:
                coef = model.params[var]
                se = model.bse[var]
                t = model.tvalues[var]
                p = model.pvalues[var]
                sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
                print_dual(f"    {var:20s}: {coef:10.4f} (t={t:6.2f}) {sig}")
        
        results.append({
            'Model': 'IV',
            'Dependent': dep_var,
            'N': int(model.nobs),
            'R2': model.rsquared,
            'KP_F': kp_f,
            'MaPresUnc_coef': model.params.get('MaPresUnc_pct', np.nan),
            'MaPresUnc_pval': model.pvalues.get('MaPresUnc_pct', np.nan),
            'ClarityCEO_coef': model.params.get('ClarityCEO', np.nan),
            'ClarityCEO_pval': model.pvalues.get('ClarityCEO', np.nan),
        })
    
    # ==============================================================================
    # Save Results
    # ==============================================================================
    print_dual("\n" + "=" * 60)
    print_dual("SAVING RESULTS")
    print_dual("=" * 60)
    
    results_df = pd.DataFrame(results)
    output_file = paths['output_dir'] / "regression_results_liquidity.txt"
    
    with open(output_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("STEP 2.9b: Liquidity Regression Results\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(results_df.to_string(index=False))
        f.write("\n\n")
        f.write("Key:\n")
        f.write("  *** p<0.01, ** p<0.05, * p<0.1\n")
        f.write("  KP_F: Kleibergen-Paap F-stat (>10 indicates strong instrument)\n")
    
    print_dual(f"  Saved to: {output_file}")
    
    # Update latest symlink
    latest_dir = paths['latest_link']
    if latest_dir.exists():
        if latest_dir.is_symlink():
            latest_dir.unlink()
        else:
            import shutil
            shutil.rmtree(latest_dir)
    try:
        latest_dir.symlink_to(paths['output_dir'], target_is_directory=True)
        print_dual(f"  Updated latest symlink -> {paths['output_dir'].name}")
    except OSError:
        import shutil
        shutil.copytree(paths['output_dir'], latest_dir)
        print_dual(f"  Created latest copy")
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print_dual("\n" + "=" * 80)
    print_dual("COMPLETE")
    print_dual("=" * 80)
    print_dual(f"Duration: {duration:.1f} seconds")
    print_dual(f"Results: {output_file}")
    
    # Close log
    dual_writer.close()
    sys.stdout = dual_writer.terminal

if __name__ == "__main__":
    main()
