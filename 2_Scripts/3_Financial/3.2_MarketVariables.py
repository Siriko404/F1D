#!/usr/bin/env python3
"""
==============================================================================
STEP 3.2: Build Market Variables (VECTORIZED + CHUNKED)
==============================================================================
ID: 3.2_MarketVariables
Description: Computes stock returns and liquidity measures from CRSP.
             Uses vectorized pandas operations with year-based chunking 
             for memory efficiency.

Variables Computed:
    - StockRet: Compound stock return (prev_call+5d to call-5d)
    - MarketRet: Value-weighted market return over same window
    - Amihud: Illiquidity measure (mean of |ret|/volume)
    - Corwin_Schultz: High-low spread estimator
    - Delta_Amihud, Delta_Corwin_Schultz: Event - Baseline

Deterministic: true
==============================================================================
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yaml
import importlib.util
import warnings
import gc
warnings.filterwarnings('ignore')

# Dynamic import for 3.4_Utils.py
utils_path = Path(__file__).parent / "3.4_Utils.py"
spec = importlib.util.spec_from_file_location("utils", utils_path)
utils = importlib.util.module_from_spec(spec)
sys.modules["utils"] = utils
spec.loader.exec_module(utils)

from utils import DualWriter, generate_variable_reference, update_latest_symlink

# ==============================================================================
# Configuration
# ==============================================================================

def load_config():
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_paths(config, timestamp):
    root = Path(__file__).parent.parent.parent
    paths = {
        'root': root,
        'crsp_dir': root / '1_Inputs' / 'CRSP_DSF',
        'manifest_dir': root / '4_Outputs' / '1.0_BuildSampleManifest' / 'latest',
        'ccm_file': root / '1_Inputs' / 'CRSPCompustat_CCM' / 'CRSPCompustat_CCM.parquet',
    }
    output_base = root / config['paths']['outputs'] / "3_Financial_Features"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)
    paths['latest_dir'] = output_base / "latest"
    log_base = root / config['paths']['logs'] / "3_Financial_Features"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}_market.log"
    return paths

# ==============================================================================
# Data Loading
# ==============================================================================

def load_manifest_with_permno(manifest_dir, ccm_file):
    """Load manifest with 100% PERMNO coverage via gvkey->CCM fallback."""
    df = pd.read_parquet(manifest_dir / "master_sample_manifest.parquet")
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['year'] = df['start_date'].dt.year
    
    df['permno'] = pd.to_numeric(df['permno'], errors='coerce')
    direct = df['permno'].notna().sum()
    print(f"  Manifest: {len(df):,} calls, direct permno: {direct:,} ({direct/len(df)*100:.1f}%)")
    
    # CCM fallback
    ccm = pd.read_parquet(ccm_file)
    ccm['gvkey_clean'] = ccm['gvkey'].astype(str).str.zfill(6)
    ccm['LPERMNO'] = pd.to_numeric(ccm['LPERMNO'], errors='coerce')
    gvkey_map = ccm.groupby('gvkey_clean')['LPERMNO'].first().to_dict()
    
    df['gvkey_clean'] = df['gvkey'].astype(str).str.zfill(6)
    missing = df['permno'].isna()
    df.loc[missing, 'permno'] = df.loc[missing, 'gvkey_clean'].map(gvkey_map)
    
    final = df['permno'].notna().sum()
    print(f"  After CCM fallback: {final:,} ({final/len(df)*100:.1f}%)")
    
    # Compute prev_call_date once
    df = df.sort_values(['gvkey', 'start_date'])
    df['prev_call_date'] = df.groupby('gvkey')['start_date'].shift(1)
    
    return df

def load_crsp_for_years(crsp_dir, years):
    """Load CRSP for specific years only."""
    all_data = []
    for year in years:
        for q in range(1, 5):
            fp = crsp_dir / f"CRSP_DSF_{year}_Q{q}.parquet"
            if fp.exists():
                all_data.append(pd.read_parquet(fp))
    
    if not all_data:
        return None
    
    crsp = pd.concat(all_data, ignore_index=True)
    
    # Normalize
    col_map = {c: c.upper() for c in crsp.columns if c.lower() != 'date'}
    crsp = crsp.rename(columns=col_map)
    if 'DATE' in crsp.columns:
        crsp = crsp.rename(columns={'DATE': 'date'})
    
    crsp['date'] = pd.to_datetime(crsp['date'])
    for col in ['RET', 'VOL', 'VWRETD', 'ASKHI', 'BIDLO', 'PRC']:
        if col in crsp.columns:
            crsp[col] = pd.to_numeric(crsp[col], errors='coerce')
    if 'PRC' in crsp.columns:
        crsp['PRC'] = crsp['PRC'].abs()
    
    return crsp

# ==============================================================================
# VECTORIZED Computations (per-year chunk)
# ==============================================================================

def compute_returns_for_year(year_manifest, crsp, config):
    """Vectorized stock return computation for one year."""
    days_after = config.get('step_07', {}).get('return_windows', {}).get('days_after_prev_call', 5)
    days_before = config.get('step_07', {}).get('return_windows', {}).get('days_before_current_call', 5)
    min_days = config.get('step_07', {}).get('return_windows', {}).get('min_trading_days', 10)
    
    # Window bounds
    year_manifest = year_manifest.copy()
    year_manifest['window_start'] = year_manifest['prev_call_date'] + pd.Timedelta(days=days_after)
    year_manifest['window_end'] = year_manifest['start_date'] - pd.Timedelta(days=days_before)
    
    valid = year_manifest[
        year_manifest['permno'].notna() & 
        year_manifest['prev_call_date'].notna() &
        (year_manifest['window_end'] > year_manifest['window_start'])
    ].copy()
    
    if len(valid) == 0:
        year_manifest['StockRet'] = np.nan
        year_manifest['MarketRet'] = np.nan
        return year_manifest
    
    valid['permno_int'] = valid['permno'].astype(int)
    crsp['PERMNO'] = crsp['PERMNO'].astype(int)
    
    # Merge
    merged = valid[['file_name', 'permno_int', 'window_start', 'window_end']].merge(
        crsp[['PERMNO', 'date', 'RET', 'VWRETD']],
        left_on='permno_int', right_on='PERMNO', how='inner'
    )
    merged = merged[(merged['date'] >= merged['window_start']) & (merged['date'] <= merged['window_end'])]
    
    # Compound returns
    def compound(x):
        v = x.dropna()
        return ((1 + v).prod() - 1) * 100 if len(v) >= min_days else np.nan

    # Volatility (Annualized Standard Deviation of daily returns * 100 for percent)
    def volatility(x):
        v = x.dropna()
        # Annualize: std * sqrt(252). Multiply by 100 to match return units (%)
        return v.std() * np.sqrt(252) * 100 if len(v) >= min_days else np.nan
    
    stock_rets = merged.groupby('file_name')['RET'].apply(compound)
    market_rets = merged.groupby('file_name')['VWRETD'].apply(compound)
    stock_vol = merged.groupby('file_name')['RET'].apply(volatility)
    
    year_manifest['StockRet'] = year_manifest['file_name'].map(stock_rets)
    year_manifest['MarketRet'] = year_manifest['file_name'].map(market_rets)
    year_manifest['Volatility'] = year_manifest['file_name'].map(stock_vol)
    
    return year_manifest

def compute_liquidity_for_year(year_manifest, crsp, config):
    """Vectorized liquidity computation for one year."""
    event_days = config.get('step_09', {}).get('window_days', 5)
    baseline_start = config.get('step_09', {}).get('baseline_start', -35)
    baseline_end = config.get('step_09', {}).get('baseline_end', -6)
    
    year_manifest = year_manifest.copy()
    valid = year_manifest[year_manifest['permno'].notna()].copy()
    
    if len(valid) == 0:
        for col in ['Amihud', 'Corwin_Schultz', 'Delta_Amihud', 'Delta_Corwin_Schultz']:
            year_manifest[col] = np.nan
        return year_manifest
    
    valid['permno_int'] = valid['permno'].astype(int)
    valid['event_start'] = valid['start_date'] - pd.Timedelta(days=event_days)
    valid['event_end'] = valid['start_date'] + pd.Timedelta(days=event_days)
    valid['baseline_start'] = valid['start_date'] + pd.Timedelta(days=baseline_start)
    valid['baseline_end'] = valid['start_date'] + pd.Timedelta(days=baseline_end)
    
    crsp['PERMNO'] = crsp['PERMNO'].astype(int)
    crsp['dollar_vol'] = crsp['VOL'] * crsp['PRC']
    
    # Amihud
    def amihud(df):
        v = df[(df['RET'].notna()) & (df['dollar_vol'] > 0)]
        return (v['RET'].abs() / v['dollar_vol']).mean() * 1e6 if len(v) >= 5 else np.nan
    
    # Event Amihud
    em = valid[['file_name', 'permno_int', 'event_start', 'event_end']].merge(
        crsp[['PERMNO', 'date', 'RET', 'dollar_vol']], left_on='permno_int', right_on='PERMNO', how='inner'
    )
    em = em[(em['date'] >= em['event_start']) & (em['date'] <= em['event_end'])]
    amihud_event = em.groupby('file_name').apply(amihud, include_groups=False) if len(em) > 0 else pd.Series(dtype=float)
    
    # Baseline Amihud
    bm = valid[['file_name', 'permno_int', 'baseline_start', 'baseline_end']].merge(
        crsp[['PERMNO', 'date', 'RET', 'dollar_vol']], left_on='permno_int', right_on='PERMNO', how='inner'
    )
    bm = bm[(bm['date'] >= bm['baseline_start']) & (bm['date'] <= bm['baseline_end'])]
    amihud_base = bm.groupby('file_name').apply(amihud, include_groups=False) if len(bm) > 0 else pd.Series(dtype=float)
    
    # Corwin-Schultz
    def cs(df):
        v = df[(df['ASKHI'].notna()) & (df['BIDLO'].notna()) & (df['ASKHI'] > 0) & (df['BIDLO'] > 0)]
        if len(v) < 5:
            return np.nan
        beta = (np.log(v['ASKHI'] / v['BIDLO'])) ** 2
        bm = beta.mean()
        if bm <= 0:
            return np.nan
        alpha = (np.sqrt(2 * bm) - np.sqrt(bm)) / (3 - 2 * np.sqrt(2))
        return max(0, 2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha)))
    
    # Event CS
    csm = valid[['file_name', 'permno_int', 'event_start', 'event_end']].merge(
        crsp[['PERMNO', 'date', 'ASKHI', 'BIDLO']], left_on='permno_int', right_on='PERMNO', how='inner'
    )
    csm = csm[(csm['date'] >= csm['event_start']) & (csm['date'] <= csm['event_end'])]
    cs_event = csm.groupby('file_name').apply(cs, include_groups=False) if len(csm) > 0 else pd.Series(dtype=float)
    
    # Baseline CS
    csb = valid[['file_name', 'permno_int', 'baseline_start', 'baseline_end']].merge(
        crsp[['PERMNO', 'date', 'ASKHI', 'BIDLO']], left_on='permno_int', right_on='PERMNO', how='inner'
    )
    csb = csb[(csb['date'] >= csb['baseline_start']) & (csb['date'] <= csb['baseline_end'])]
    cs_base = csb.groupby('file_name').apply(cs, include_groups=False) if len(csb) > 0 else pd.Series(dtype=float)
    
    # Map
    year_manifest['Amihud'] = year_manifest['file_name'].map(amihud_event)
    year_manifest['Corwin_Schultz'] = year_manifest['file_name'].map(cs_event)
    year_manifest['Delta_Amihud'] = year_manifest['file_name'].map(amihud_event) - year_manifest['file_name'].map(amihud_base)
    year_manifest['Delta_Corwin_Schultz'] = year_manifest['file_name'].map(cs_event) - year_manifest['file_name'].map(cs_base)
    
    return year_manifest

# ==============================================================================
# Main
# ==============================================================================

def main():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    config = load_config()
    paths = setup_paths(config, timestamp)
    
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer
    
    print("="*60)
    print("STEP 3.2: Build Market Variables (VECTORIZED + CHUNKED)")
    print(f"Timestamp: {timestamp}")
    print("="*60)
    
    # Load manifest
    print("\nLoading manifest...")
    manifest = load_manifest_with_permno(paths['manifest_dir'], paths['ccm_file'])
    
    years = sorted(manifest['year'].unique())
    print(f"\nProcessing {len(years)} years: {years[0]} to {years[-1]}")
    
    all_results = []
    
    for year in years:
        print(f"\n{'='*40}")
        print(f"Year {year}")
        print("="*40)
        
        year_manifest = manifest[manifest['year'] == year].copy()
        print(f"  Calls: {len(year_manifest):,}")
        
        # Load CRSP for current year + previous year (for return windows)
        crsp = load_crsp_for_years(paths['crsp_dir'], [year - 1, year])
        if crsp is None:
            print(f"  WARNING: No CRSP data, skipping")
            continue
        print(f"  CRSP loaded: {len(crsp):,} observations")
        
        # Compute (vectorized within year)
        year_manifest = compute_returns_for_year(year_manifest, crsp, config)
        n_ret = year_manifest['StockRet'].notna().sum()
        print(f"  StockRet: {n_ret:,} ({n_ret/len(year_manifest)*100:.1f}%)")
        
        year_manifest = compute_liquidity_for_year(year_manifest, crsp, config)
        n_liq = year_manifest['Amihud'].notna().sum()
        print(f"  Amihud: {n_liq:,} ({n_liq/len(year_manifest)*100:.1f}%)")
        
        # Save
        cols = ['file_name', 'gvkey', 'start_date', 'year', 'StockRet', 'MarketRet',
                'Amihud', 'Corwin_Schultz', 'Delta_Amihud', 'Delta_Corwin_Schultz']
        output_file = paths['output_dir'] / f"market_variables_{year}.parquet"
        year_manifest[cols].to_parquet(output_file, index=False)
        print(f"  Saved: {output_file.name}")
        
        all_results.append(year_manifest[cols])
        
        # Free memory
        del crsp
        gc.collect()
    
    # Summary
    all_df = pd.concat(all_results, ignore_index=True)
    generate_variable_reference(all_df, paths['output_dir'] / "market_variable_reference.csv")
    update_latest_symlink(paths['latest_dir'], paths['output_dir'])
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total: {len(all_df):,} calls")
    for col in ['StockRet', 'MarketRet', 'Amihud', 'Corwin_Schultz']:
        n = all_df[col].notna().sum()
        print(f"  {col}: {n:,} ({n/len(all_df)*100:.1f}%)")
    print(f"\nOutputs: {paths['output_dir']}")
    
    dual_writer.close()
    sys.stdout = dual_writer.terminal

if __name__ == "__main__":
    main()
