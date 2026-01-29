#!/usr/bin/env python3
"""
==============================================================================
STEP 2.9: Build Liquidity Measures
==============================================================================
ID: 2.9_BuildLiquidityMeasures
Description: Constructs market liquidity measures for CEO clarity regression.
             Measures are computed over a [-5, +5] day window around the call.
             1. Amihud Illiquidity (Daily |Ret| / $Vol)
             2. Kyle's Lambda (Slope of |Ret| ~ Vol)
             3. Corwin-Schultz Spread (High-Low estimator)

Inputs:
    - config/project.yaml
    - 4_Outputs/2.8_EstimateCeoClarity/latest/calls_with_clarity_YYYY.parquet
    - 1_Inputs/CRSP_DSF/CRSP_DSF_YYYY_QQ.parquet
Outputs:
    - 4_Outputs/2.9_LiquidityAnalysis/TIMESTAMP/calls_with_liquidity_YYYY.parquet
    - 4_Outputs/2.9_LiquidityAnalysis/TIMESTAMP/report_step_09.md
    - 3_Logs/2.9_BuildLiquidityMeasures/TIMESTAMP.log
==============================================================================
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yaml
import shutil
import warnings
from scipy import stats

# Dual-write logging
class DualWriter:
    def __init__(self, log_path):
        self.terminal = sys.stdout
        self.log = open(log_path, 'w', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush() # Ensure immediate flush
        
    def flush(self):
        self.terminal.flush()
        self.log.flush()
    
    def close(self):
        self.log.close()

def print_dual(msg):
    print(msg, flush=True)

# Configuration
def load_config():
    config_path = Path(__file__).parent.parent / "config" / "project.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_paths(config):
    root = Path(__file__).parent.parent
    paths = {
        'root': root,
        'input_dir': root / '4_Outputs' / '2.8_EstimateCeoClarity' / 'latest',
        'crsp_dir': root / '1_Inputs' / 'CRSP_DSF',
    }
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config['paths']['outputs'] / "2.9_LiquidityAnalysis"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)
    paths['latest_dir'] = output_base / "latest"
    
    log_base = root / config['paths']['logs'] / "2.9_BuildLiquidityMeasures"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}.log"
    
    return paths, timestamp

# Data Loading
def load_clarity_calls(input_dir, year_start, year_end):
    print_dual("\nLOADING CALLS DATA...")
    all_data = []
    for year in range(year_start, year_end + 1):
        file_path = input_dir / f"calls_with_clarity_{year}.parquet"
        if file_path.exists():
            df = pd.read_parquet(file_path)
            print_dual(f"  Loaded {year}: {len(df):,} calls")
            all_data.append(df)
        else:
            print_dual(f"  WARNING: Missing {file_path.name}")
            
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        # Ensure correct types for linking
        combined['gvkey'] = combined['gvkey'].astype(str).str.zfill(6)
        if 'year' not in combined.columns:
            combined['year'] = pd.to_datetime(combined['start_date']).dt.year
        return combined
    return pd.DataFrame()

def load_crsp_data(crsp_dir, year_start, year_end):
    print_dual("\nLOADING CRSP DATA...")
    all_crsp = []
    # Buffer years for window calculation
    years_to_load = range(year_start - 1, year_end + 2) 
    
    for year in years_to_load:
        for q in range(1, 5):
            fpath = crsp_dir / f"CRSP_DSF_{year}_Q{q}.parquet"
            if fpath.exists():
                df = pd.read_parquet(fpath)
                # Select only needed columns to save memory
                keep_cols = ['PERMNO', 'date', 'PRC', 'VOL', 'ASKHI', 'BIDLO']
                available = [c for c in keep_cols if c in df.columns]
                all_crsp.append(df[available])
                
    if not all_crsp:
        return pd.DataFrame()
        
    crsp = pd.concat(all_crsp, ignore_index=True)
    crsp['date'] = pd.to_datetime(crsp['date'])
    crsp['PRC'] = crsp['PRC'].abs() # Handle negative prices (mid-quotes)
    
    # Calculate Dollar Volume
    crsp['DVol'] = crsp['PRC'] * crsp['VOL']
    
    # Ensure sorted unique index
    crsp.sort_values(['PERMNO', 'date'], inplace=True)
    
    print_dual(f"  Total CRSP rows: {len(crsp):,}")
    return crsp

# Liquidity Calculations
def compute_liquidity(calls, crsp, config):
    print_dual("\nCOMPUTING LIQUIDITY MEASURES (Levels & Deltas)...")
    
    # Event Window: [-5, +5]
    evt_window_days = config['step_09']['liquidity_measures']['window_days'] 
    # Baseline Window: [-35, -6] (30 days prior to event window)
    base_window_days = [-35, -6]
    
    min_days = config['step_09']['liquidity_measures']['min_trading_days']
    
    # Pre-calculate Returns
    crsp['Ret'] = crsp.groupby('PERMNO')['PRC'].pct_change()
    crsp['AbsRet'] = crsp['Ret'].abs()
    
    # Index CRSP
    crsp.set_index(['PERMNO', 'date'], inplace=True)
    crsp.sort_index(inplace=True)
    
    # Initialize cols
    measures = ['Amihud', 'Kyle_Lambda', 'Corwin_Schultz']
    for m in measures:
        calls[m] = np.nan
        calls[f'Delta_{m}'] = np.nan
    
    processed = 0
    total = len(calls)
    
    for idx, row in calls.iterrows():
        try:
            permno = int(row['LPERMNO']) 
        except:
            continue
            
        call_date = row['start_date']
        
        # Define Date Ranges
        evt_start = call_date + timedelta(days=evt_window_days[0])
        evt_end   = call_date + timedelta(days=evt_window_days[1])
        
        base_start = call_date + timedelta(days=base_window_days[0])
        base_end   = call_date + timedelta(days=base_window_days[1])
        
        # Slice full range at once for efficiency
        full_start = min(evt_start, base_start)
        full_end = max(evt_end, base_end)
        
        try:
            firm_data = crsp.loc[(permno, slice(full_start, full_end)), :]
        except KeyError:
            continue
            
        if len(firm_data) < min_days:
            continue
            
        # Helper to calc measures on a slice
        def calc_measures(df_slice):
            res = {}
            if len(df_slice) < min_days:
                return {m: np.nan for m in measures}
                
            # Amihud
            valid_ami = df_slice[df_slice['DVol'] > 0]
            if len(valid_ami) >= min_days:
                res['Amihud'] = (valid_ami['AbsRet'] / valid_ami['DVol']).mean() * 1e6
            else:
                res['Amihud'] = np.nan
                
            # Kyle
            if df_slice['VOL'].std() > 0:
                try:
                    slope, _, _, _, _ = stats.linregress(df_slice['VOL'], df_slice['AbsRet'])
                    res['Kyle_Lambda'] = slope * 1e6
                except:
                    res['Kyle_Lambda'] = np.nan
            else:
                res['Kyle_Lambda'] = np.nan
                
            # Corwin-Schultz (Simple Spread)
            if 'ASKHI' in df_slice.columns and 'BIDLO' in df_slice.columns:
                high = df_slice['ASKHI']
                low = df_slice['BIDLO']
                valid_hl = (high > low) & (low > 0)
                if valid_hl.sum() >= min_days:
                    rel_spread = (high[valid_hl] - low[valid_hl]) / ((high[valid_hl] + low[valid_hl])/2)
                    res['Corwin_Schultz'] = rel_spread.mean() * 100
                else:
                    res['Corwin_Schultz'] = np.nan
            else:
                res['Corwin_Schultz'] = np.nan
            return res

        # Calc Event Level
        evt_data = firm_data.loc[(slice(None), slice(evt_start, evt_end)), :]
        evt_res = calc_measures(evt_data)
        
        # Calc Baseline Level
        base_data = firm_data.loc[(slice(None), slice(base_start, base_end)), :]
        base_res = calc_measures(base_data)
        
        # Store
        for m in measures:
            calls.at[idx, m] = evt_res[m]
            if pd.notna(evt_res[m]) and pd.notna(base_res[m]):
                calls.at[idx, f'Delta_{m}'] = evt_res[m] - base_res[m]
        
        processed += 1
        if processed % 1000 == 0:
            print_dual(f"  Processed {processed} calls...")
            
    return calls

# Main Execution
def main():
    start_time = datetime.now()
    config = load_config()
    paths, timestamp = setup_paths(config)
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer
    
    print_dual("STEP 2.9: Build Liquidity Measures (Year-by-Year)")
    print_dual(f"Config: {config['project']['name']}")
    
    year_start = config['data']['year_start']
    year_end = config['data']['year_end']
    
    # Iterate by year to save memory and produce incremental outputs
    for year in range(year_start, year_end + 1):
        print_dual(f"\nProcessing Year: {year}")
        
        # 1. Load Calls for this year
        # Note: 2.8 output is 'calls_with_clarity_YYYY.parquet'
        # We can just use the load helper but restricted to one year
        year_calls_path = paths['input_dir'] / f"calls_with_clarity_{year}.parquet"
        if not year_calls_path.exists():
            print_dual(f"  Skipping {year}: File not found ({year_calls_path.name})")
            continue
            
        calls = pd.read_parquet(year_calls_path)
        # Ensure gvkey format
        calls['gvkey'] = calls['gvkey'].astype(str).str.zfill(6)
        print_dual(f"  Loaded {len(calls):,} calls")
        
        # 2. Load CRSP for this year (+/- 1 year buffer for window calc)
        # Assuming liquidity window is small (e.g. [-5, +5]), we might cross year boundaries.
        # Loading Y-1, Y, Y+1 is safe.
        crsp = load_crsp_data(paths['crsp_dir'], year - 1, year + 1)
        if crsp.empty:
            print_dual(f"  WARNING: No CRSP data for {year} window. Skipping.")
            continue
            
        # 3. Compute Liquidity
        # Note: compute_liquidity function expects 'calls' and 'crsp'
        calls_liq = compute_liquidity(calls, crsp, config)
        
        # 4. Save Output
        out_file = paths['output_dir'] / config['step_09']['outputs']['liquidity_data'].format(year=year)
        calls_liq.to_parquet(out_file)
        print_dual(f"  Saved: {out_file.name}")
        
        # 5. Cleanup
        del calls, crsp, calls_liq
        
    # Symlink
    if paths['latest_dir'].exists():
        if paths['latest_dir'].is_symlink():
            paths['latest_dir'].unlink()
        else:
            shutil.rmtree(paths['latest_dir'])
    try:
        paths['latest_dir'].symlink_to(paths['output_dir'].name, target_is_directory=True)
    except:
        shutil.copytree(paths['output_dir'], paths['latest_dir'])
        
    print_dual(f"\nDONE. Time: {datetime.now() - start_time}")

if __name__ == "__main__":
    main()
