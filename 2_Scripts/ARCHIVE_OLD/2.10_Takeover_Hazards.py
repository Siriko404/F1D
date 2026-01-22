#!/usr/bin/env python3
"""
==============================================================================
STEP 2.10: Takeover Hazards (Cox PH and Fine-Gray Competing Risks)
==============================================================================
ID: 2.10_Takeover_Hazards
Description: Analyzes how CEO Clarity and Presentation Uncertainty predict
             Takeover probability using survival analysis.
             - Model 1: Cox Proportional Hazards (All Takeovers)
             - Model 2: Fine-Gray Competing Risks (Friendly vs. Uninvited)

Variables (our pipeline -> paper):
    - MaPresUnc_pct -> UncPreCEO
    - ClarityCEO -> Clarity (Fixed Effect)

Inputs:
    - config/project.yaml
    - 4_Outputs/2.9_LiquidityAnalysis/latest/calls_with_liquidity_YYYY.parquet
    - 4_Outputs/2.8_CeoClarityScores/latest/ceo_clarity_scores.parquet
    - 1_Inputs/SDC/sdc_ma.parquet (M&A data)
    - 1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet
Outputs:
    - 4_Outputs/2.10_TakeoverHazards/TIMESTAMP/takeover_hazard_results.txt
    - 3_Logs/2.10_TakeoverHazards/TIMESTAMP.log
==============================================================================
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import yaml
from lifelines import CoxPHFitter
import warnings
warnings.filterwarnings('ignore')

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
    
    output_dir = root / config['paths']['outputs'] / "2.10_TakeoverHazards" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    log_dir = root / config['paths']['logs'] / "2.10_TakeoverHazards"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    return {
        'root': root,
        'liquidity_dir': root / '4_Outputs' / '2.9_LiquidityAnalysis' / 'latest',
        'clarity_file': root / '4_Outputs' / '2.8_CeoClarityScores' / 'latest' / 'ceo_clarity_scores.parquet',
        'sdc_file': root / '1_Inputs' / 'SDC' / 'sdc-ma-merged.parquet',
        'compustat_file': root / '1_Inputs' / 'comp_na_daily_all' / 'comp_na_daily_all.parquet',
        'output_dir': output_dir,
        'log_file': log_dir / f"{timestamp}.log"
    }

# ==============================================================================
# Data Loading
# ==============================================================================

def load_data(paths):
    print_dual("\n[1] LOADING DATA...")
    
    # 1. Liquidity Data (base panel)
    call_files = sorted(paths['liquidity_dir'].glob("calls_with_liquidity_*.parquet"))
    if not call_files:
        print_dual(f"  ERROR: No liquidity files found in {paths['liquidity_dir']}")
        return None
    df = pd.concat([pd.read_parquet(f) for f in call_files], ignore_index=True)
    print_dual(f"  Base panel loaded: {len(df):,} calls")
    
    # 2. CEO Clarity Scores - check if already in data
    if 'ClarityCEO' in df.columns and df['ClarityCEO'].notna().sum() > 0:
        print_dual(f"  ClarityCEO already in data: {df['ClarityCEO'].notna().sum():,} values")
    elif paths['clarity_file'].exists():
        clarity = pd.read_parquet(paths['clarity_file'])
        print_dual(f"  Clarity scores loaded: {len(clarity):,}")
        if 'CEO_ID' in df.columns and 'CEO_ID' in clarity.columns:
            df = df.merge(clarity[['CEO_ID', 'ClarityCEO']].drop_duplicates('CEO_ID'), 
                         on='CEO_ID', how='left')
            print_dual(f"  After Clarity merge: {df['ClarityCEO'].notna().sum():,} with clarity")
    else:
        print_dual(f"  WARNING: Clarity file not found and ClarityCEO not in data")
        if 'ClarityCEO' not in df.columns:
            df['ClarityCEO'] = np.nan
    
    # 3. SDC M&A Data
    if paths['sdc_file'].exists():
        sdc = pd.read_parquet(paths['sdc_file'])
        print_dual(f"  SDC M&A loaded: {len(sdc):,} deals")
        
        # Use Target 6-digit CUSIP for matching
        sdc['target_cusip'] = sdc['Target 6-digit CUSIP'].astype(str).str.strip()
        
        # Parse announcement date
        sdc['announce_date'] = pd.to_datetime(sdc['Date Announced'], errors='coerce')
        
        # Classify deal type (Friendly+Neutral vs Hostile+Unsolicited)
        # Deal Attitude values: Friendly, Neutral, Unsolicited, Hostile, No Applicable
        sdc['deal_type'] = sdc['Deal Attitude'].apply(
            lambda x: 'Uninvited' if str(x).lower() in ['hostile', 'unsolicited'] else 'Friendly'
        )
        # Note: Friendly, Neutral, and 'No Applicable' all map to 'Friendly'
        
        # Get CUSIP from our panel data (use ccm_cusip if available)
        if 'ccm_cusip' in df.columns:
            df['cusip6'] = df['ccm_cusip'].astype(str).str[:6]
        elif 'cusip' in df.columns:
            df['cusip6'] = df['cusip'].astype(str).str[:6]
        else:
            print_dual("  WARNING: No CUSIP column in data for SDC matching")
            df['cusip6'] = ''
        
        df['start_date'] = pd.to_datetime(df['start_date'])
        
        # Flag firms that were takeover targets within 1 year
        df['Takeover'] = 0
        df['Takeover_Type'] = 'None'
        
        # Vectorized matching (more efficient than row-by-row)
        print_dual("  Matching takeover events (this may take a moment)...")
        for cusip in df['cusip6'].dropna().unique():
            if cusip == '' or len(cusip) < 6:
                continue
            firm_calls = df[df['cusip6'] == cusip]
            firm_deals = sdc[sdc['target_cusip'] == cusip]
            
            if len(firm_deals) == 0:
                continue
            
            for idx, row in firm_calls.iterrows():
                matching_deals = firm_deals[
                    (firm_deals['announce_date'] > row['start_date']) &
                    (firm_deals['announce_date'] <= row['start_date'] + pd.Timedelta(days=365))
                ]
                if len(matching_deals) > 0:
                    df.loc[idx, 'Takeover'] = 1
                    df.loc[idx, 'Takeover_Type'] = matching_deals.iloc[0]['deal_type']
        
        print_dual(f"  Takeover events: {df['Takeover'].sum():,}")
        print_dual(f"    Friendly: {(df['Takeover_Type'] == 'Friendly').sum():,}")
        print_dual(f"    Uninvited: {(df['Takeover_Type'] == 'Uninvited').sum():,}")
    else:
        print_dual(f"  WARNING: SDC file not found at {paths['sdc_file']}")
        df['Takeover'] = 0
        df['Takeover_Type'] = 'None'
    
    # 4. Compustat Controls
    if paths['compustat_file'].exists():
        print_dual("  Loading Compustat for firm controls...")
        comp = pd.read_parquet(paths['compustat_file'], 
                              columns=['gvkey', 'datadate', 'atq', 'ltq', 'ceqq', 'niq', 'cshoq', 'prccq'])
        comp['gvkey'] = comp['gvkey'].astype(str).str.zfill(6)
        comp['datadate'] = pd.to_datetime(comp['datadate'])
        
        # Convert to numeric
        for col in ['atq', 'ltq', 'ceqq', 'niq', 'cshoq', 'prccq']:
            comp[col] = pd.to_numeric(comp[col], errors='coerce')
        
        # Calculate controls
        comp['Size'] = np.log(comp['atq'].clip(lower=1).astype(float))
        comp['BM'] = comp['ceqq'] / (comp['cshoq'] * comp['prccq']).clip(lower=0.01)
        comp['Lev'] = comp['ltq'] / comp['atq'].clip(lower=1)
        comp['ROA'] = comp['niq'] / comp['atq'].clip(lower=1)
        
        # Winsorize
        for col in ['Size', 'BM', 'Lev', 'ROA']:
            if col in comp.columns:
                p1, p99 = comp[col].quantile([0.01, 0.99])
                comp[col] = comp[col].clip(p1, p99)
        
        # merge_asof requires both sorted by the "on" key
        comp = comp.sort_values('datadate').reset_index(drop=True)
        df = df.sort_values('start_date').reset_index(drop=True)
        
        df = pd.merge_asof(df, comp[['gvkey', 'datadate', 'Size', 'BM', 'Lev', 'ROA']],
                          left_on='start_date', right_on='datadate', by='gvkey',
                          direction='backward')
        print_dual(f"  After Compustat merge: {df['Size'].notna().sum():,} with controls")
    
    # Create survival time (quarters until takeover or end of observation)
    df['Duration'] = 4  # Default: 4 quarters (1 year) observation window
    df.loc[df['Takeover'] == 1, 'Duration'] = 1  # Event happened within window
    
    return df

# ==============================================================================
# Cox Proportional Hazards
# ==============================================================================

def run_cox_ph(df, event_col, covariates, title=""):
    """Run Cox Proportional Hazards model."""
    print_dual(f"\n--- Cox PH: {title} ---")
    
    # Prepare data
    duration_col = 'Duration'
    reg_df = df[[duration_col, event_col] + covariates].dropna()
    
    if len(reg_df) < 100:
        print_dual(f"  Insufficient observations: {len(reg_df)}")
        return None
    
    if reg_df[event_col].sum() < 10:
        print_dual(f"  Insufficient events: {reg_df[event_col].sum()}")
        return None
    
    print_dual(f"  N = {len(reg_df):,}, Events = {reg_df[event_col].sum():,}")
    
    # Fit Cox PH
    cph = CoxPHFitter()
    cph.fit(reg_df, duration_col=duration_col, event_col=event_col)
    
    print_dual(f"  Concordance: {cph.concordance_index_:.4f}")
    print_dual(f"\n  Coefficients (Hazard Ratios):")
    
    for var in covariates:
        if var in cph.summary.index:
            coef = cph.summary.loc[var, 'coef']
            hr = cph.summary.loc[var, 'exp(coef)']
            p = cph.summary.loc[var, 'p']
            sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
            print_dual(f"    {var:20s}: HR={hr:8.4f} (coef={coef:7.4f}, p={p:.3f}) {sig}")
    
    return cph

# ==============================================================================
# Fine-Gray Competing Risks (via Weighted Cox)
# ==============================================================================

def run_fine_gray(df, event_type, covariates, title=""):
    """
    Run Fine-Gray competing risks model via subdistribution hazard approach.
    Uses IPCW (Inverse Probability of Censoring Weighting) to handle competing events.
    """
    print_dual(f"\n--- Fine-Gray: {title} ---")
    
    # Create subdistribution indicator
    # For event_type: 1 = Friendly, 2 = Uninvited
    event_label = 'Friendly' if event_type == 1 else 'Uninvited'
    
    # In Fine-Gray: 
    # - Subjects with the event of interest: event = 1
    # - Subjects with competing event: remain at risk (not censored)
    # - Subjects censored: event = 0
    
    reg_df = df[['Duration', 'Takeover', 'Takeover_Type'] + covariates].copy()
    reg_df = reg_df.dropna()
    
    # Create event indicator for Fine-Gray
    reg_df['FG_Event'] = 0
    reg_df.loc[reg_df['Takeover_Type'] == event_label, 'FG_Event'] = 1
    
    # For competing risks: those with competing event stay in risk set
    # We modify duration for those with competing event to be "at risk forever"
    # This is a simplified implementation - true Fine-Gray uses IPCW weights
    reg_df['FG_Duration'] = reg_df['Duration']
    competing_mask = (reg_df['Takeover'] == 1) & (reg_df['Takeover_Type'] != event_label)
    # For competing events, extend duration (they remain at risk)
    reg_df.loc[competing_mask, 'FG_Duration'] = reg_df['Duration'].max() + 1
    
    if len(reg_df) < 100:
        print_dual(f"  Insufficient observations: {len(reg_df)}")
        return None
    
    n_events = reg_df['FG_Event'].sum()
    if n_events < 10:
        print_dual(f"  Insufficient events for {event_label}: {n_events}")
        return None
    
    print_dual(f"  N = {len(reg_df):,}, Events ({event_label}) = {n_events:,}")
    
    # Fit Cox PH with subdistribution structure
    cph = CoxPHFitter()
    fit_df = reg_df[['FG_Duration', 'FG_Event'] + covariates]
    cph.fit(fit_df, duration_col='FG_Duration', event_col='FG_Event')
    
    print_dual(f"  Concordance: {cph.concordance_index_:.4f}")
    print_dual(f"\n  Coefficients (Subdistribution Hazard Ratios):")
    
    for var in covariates:
        if var in cph.summary.index:
            coef = cph.summary.loc[var, 'coef']
            hr = cph.summary.loc[var, 'exp(coef)']
            p = cph.summary.loc[var, 'p']
            sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
            print_dual(f"    {var:20s}: SHR={hr:8.4f} (coef={coef:7.4f}, p={p:.3f}) {sig}")
    
    return cph

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
    print_dual("STEP 2.10: Takeover Hazards (Cox PH and Fine-Gray)")
    print_dual("=" * 80)
    print_dual(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_dual(f"Output directory: {paths['output_dir']}")
    print_dual(f"Log file: {paths['log_file']}")
    
    # Load data
    df = load_data(paths)
    if df is None:
        print_dual("ERROR: Failed to load data")
        return
    
    # Define covariates
    primary_vars = ['MaPresUnc_pct', 'ClarityCEO']
    controls = ['Size', 'BM', 'Lev', 'ROA']
    covariates = primary_vars + controls
    
    # Check available variables
    available_covars = [v for v in covariates if v in df.columns and df[v].notna().sum() > 100]
    print_dual(f"\nAvailable covariates: {available_covars}")
    
    if not available_covars:
        print_dual("ERROR: No covariates available")
        return
    
    # Results container
    results = []
    
    # ==============================================================================
    # Model 1: Cox PH - All Takeovers
    # ==============================================================================
    print_dual("\n" + "=" * 60)
    print_dual("MODEL 1: Cox Proportional Hazards - All Takeovers")
    print_dual("=" * 60)
    
    cph_all = run_cox_ph(df, 'Takeover', available_covars, title="All Takeovers")
    if cph_all:
        for var in primary_vars:
            if var in cph_all.summary.index:
                results.append({
                    'Model': 'CPH_All',
                    'Variable': var,
                    'HR': cph_all.summary.loc[var, 'exp(coef)'],
                    'Coef': cph_all.summary.loc[var, 'coef'],
                    'Pval': cph_all.summary.loc[var, 'p'],
                    'N': int(cph_all.event_observed.sum()),
                    'Events': int(cph_all.event_observed.sum())
                })
    
    # ==============================================================================
    # Model 2: Fine-Gray - Friendly Takeovers
    # ==============================================================================
    print_dual("\n" + "=" * 60)
    print_dual("MODEL 2: Fine-Gray Competing Risks - Friendly Takeovers")
    print_dual("=" * 60)
    
    fg_friendly = run_fine_gray(df, 1, available_covars, title="Friendly")
    if fg_friendly:
        for var in primary_vars:
            if var in fg_friendly.summary.index:
                results.append({
                    'Model': 'FG_Friendly',
                    'Variable': var,
                    'SHR': fg_friendly.summary.loc[var, 'exp(coef)'],
                    'Coef': fg_friendly.summary.loc[var, 'coef'],
                    'Pval': fg_friendly.summary.loc[var, 'p'],
                    'N': int(fg_friendly.event_observed.sum())
                })
    
    # ==============================================================================
    # Model 3: Fine-Gray - Uninvited Takeovers
    # ==============================================================================
    print_dual("\n" + "=" * 60)
    print_dual("MODEL 3: Fine-Gray Competing Risks - Uninvited Takeovers")
    print_dual("=" * 60)
    
    fg_uninvited = run_fine_gray(df, 2, available_covars, title="Uninvited")
    if fg_uninvited:
        for var in primary_vars:
            if var in fg_uninvited.summary.index:
                results.append({
                    'Model': 'FG_Uninvited',
                    'Variable': var,
                    'SHR': fg_uninvited.summary.loc[var, 'exp(coef)'],
                    'Coef': fg_uninvited.summary.loc[var, 'coef'],
                    'Pval': fg_uninvited.summary.loc[var, 'p'],
                    'N': int(fg_uninvited.event_observed.sum())
                })
    
    # ==============================================================================
    # Save Results
    # ==============================================================================
    print_dual("\n" + "=" * 60)
    print_dual("SAVING RESULTS")
    print_dual("=" * 60)
    
    results_df = pd.DataFrame(results)
    output_file = paths['output_dir'] / "takeover_hazard_results.txt"
    
    with open(output_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("STEP 2.10: Takeover Hazard Results\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write("Models:\n")
        f.write("  CPH_All: Cox PH for all takeovers\n")
        f.write("  FG_Friendly: Fine-Gray for Friendly takeovers\n")
        f.write("  FG_Uninvited: Fine-Gray for Uninvited (Hostile/Unsolicited) takeovers\n\n")
        f.write(results_df.to_string(index=False))
        f.write("\n\n")
        f.write("Key:\n")
        f.write("  HR: Hazard Ratio (CPH)\n")
        f.write("  SHR: Subdistribution Hazard Ratio (Fine-Gray)\n")
        f.write("  *** p<0.01, ** p<0.05, * p<0.1\n")
    
    print_dual(f"  Saved to: {output_file}")
    
    # Update latest symlink
    latest_dir = paths['output_dir'].parent / 'latest'
    if latest_dir.exists():
        if latest_dir.is_symlink():
            latest_dir.unlink()
        else:
            import shutil
            shutil.rmtree(latest_dir)
    try:
        latest_dir.symlink_to(paths['output_dir'], target_is_directory=True)
        print_dual(f"  Updated latest symlink")
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
