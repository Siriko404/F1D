#!/usr/bin/env python3
"""
==============================================================================
STEP 1.3: CEO Tenure Map Construction
==============================================================================
ID: 1.3_BuildTenureMap
Description: Constructs monthly CEO tenure panel from Execucomp data.
             Aggregates annual records into episodes, links predecessors,
             and expands to monthly panel with current + previous CEO info.
             
Inputs:
    - 1_Inputs/Execucomp/comp_execucomp.parquet
    - config/project.yaml
    
Outputs:
    - 4_Outputs/1.3_BuildTenureMap/{timestamp}/tenure_monthly.parquet
    - 4_Outputs/1.3_BuildTenureMap/{timestamp}/variable_reference.csv
    - 4_Outputs/1.3_BuildTenureMap/{timestamp}/report_step_1_3.md
    - 3_Logs/1.3_BuildTenureMap/{timestamp}.log
    
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
import importlib.util
import sys
from pathlib import Path

# Dynamic import for 1.5_Utils.py to comply with naming convention
try:
    utils_path = Path(__file__).parent / "1.5_Utils.py"
    spec = importlib.util.spec_from_file_location("utils", utils_path)
    utils = importlib.util.module_from_spec(spec)
    sys.modules["utils"] = utils
    spec.loader.exec_module(utils)
    from utils import generate_variable_reference, update_latest_symlink
except ImportError as e:
    print(f"Criticial Error importing utils: {e}")
    sys.exit(1)

# ==============================================================================
# Dual-write logging utility
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
# Configuration and setup
# ==============================================================================

def load_config():
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_paths(config):
    root = Path(__file__).parent.parent.parent

    paths = {
        'root': root,
        'execucomp': root / '1_Inputs' / 'Execucomp' / 'comp_execucomp.parquet',
    }

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config['paths']['outputs'] / "1.3_BuildTenureMap"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)

    paths['latest_dir'] = output_base / "latest"

    log_base = root / config['paths']['logs'] / "1.3_BuildTenureMap"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}.log"

    return paths, timestamp

# Generate_variable_reference and update_latest_symlink imported from step1_utils

# ==============================================================================
# Main processing
# ==============================================================================

def main():
    config = load_config()
    paths, timestamp = setup_paths(config)
    
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer
    
    print_dual("="*80)
    print_dual("STEP 1.3: CEO Tenure Map Construction")
    print_dual("="*80)
    print_dual(f"Timestamp: {timestamp}\n")
    
    # Load Execucomp
    print_dual("Loading Execucomp data...")
    df = pd.read_parquet(paths['execucomp'])
    print_dual(f"  Loaded {len(df):,} records\n")
    
    # Filter for CEO records (ceoann == 'CEO' or becameceo is not null)
    print_dual("Identifying CEO records...")
    ceo_records = df[(df['ceoann'] == 'CEO') | (df['becameceo'].notna())].copy()
    print_dual(f"  Found {len(ceo_records):,} CEO-related records")
    print_dual(f"  Unique firms (gvkey): {ceo_records['gvkey'].nunique():,}")
    print_dual(f"  Unique executives (execid): {ceo_records['execid'].nunique():,}\n")
    
    # Build tenure episodes
    print_dual("Building tenure episodes per (gvkey, execid)...")
    
    episodes = []
    for (gvkey, execid), group in ceo_records.groupby(['gvkey', 'execid']):
        # Get start and end dates
        became_ceo_dates = group['becameceo'].dropna()
        left_dates = group['leftofc'].dropna()
        
        if len(became_ceo_dates) == 0:
            continue  # Skip if no becameceo date (not strictly a CEO)
        
        start_date = became_ceo_dates.min()
        
        if len(left_dates) > 0:
            end_date = left_dates.max()
        else:
            # Active CEO: check if in latest fiscal year
            max_year = group['year'].max()
            latest_dataset_year = ceo_records['year'].max()
            
            if max_year >= latest_dataset_year:
                # Active CEO, impute future end date
                end_date = pd.Timestamp('2025-12-31')
            else:
                # Missing data, use last year's end
                end_date = pd.Timestamp(f'{int(max_year)}-12-31')
        
        episodes.append({
            'gvkey': gvkey,
            'execid': execid,
            'exec_fullname': group['exec_fullname'].iloc[0] if 'exec_fullname' in group.columns else None,
            'start_date': start_date,
            'end_date': end_date
        })
    
    episodes_df = pd.DataFrame(episodes)
    print_dual(f"  Created {len(episodes_df):,} tenure episodes\n")
    
    # Link predecessors
    print_dual("Linking predecessors (prev_execid)...")
    
    episodes_df['start_date'] = pd.to_datetime(episodes_df['start_date'])
    episodes_df['end_date'] = pd.to_datetime(episodes_df['end_date'])
    
    episodes_df = episodes_df.sort_values(['gvkey', 'start_date']).reset_index(drop=True)
    
    # Compute prev_execid
    episodes_df['prev_execid'] = None
    episodes_df['prev_exec_fullname'] = None
    
    for gvkey, group in episodes_df.groupby('gvkey'):
        indices = group.index.tolist()
        for i in range(1, len(indices)):
            current_idx = indices[i]
            prev_idx = indices[i-1]
            
            episodes_df.at[current_idx, 'prev_execid'] = episodes_df.at[prev_idx, 'execid']
            episodes_df.at[current_idx, 'prev_exec_fullname'] = episodes_df.at[prev_idx, 'exec_fullname']
    
    linked_count = episodes_df['prev_execid'].notna().sum()
    print_dual(f"  Linked {linked_count:,} episodes to predecessors\n")
    
    # Expand to monthly panel
    print_dual("Expanding to monthly panel...")
    
    monthly_records = []
    total_episodes = len(episodes_df)
    progress_interval = max(500, total_episodes // 20)
    
    for i, (idx, row) in enumerate(episodes_df.iterrows(), 1):
        # Generate monthly dates
        months = pd.date_range(
            start=row['start_date'].to_period('M').to_timestamp(),
            end=row['end_date'].to_period('M').to_timestamp(),
            freq='MS'
        )
        
        for month_start in months:
            monthly_records.append({
                'gvkey': row['gvkey'],
                'year': month_start.year,
                'month': month_start.month,
                'date': month_start,
                'ceo_id': row['execid'],
                'ceo_name': row['exec_fullname'],
                'prev_ceo_id': row['prev_execid'],
                'prev_ceo_name': row['prev_exec_fullname']
            })
        
        # Progress indicator
        if i % progress_interval == 0 or i == total_episodes:
            pct = (i / total_episodes) * 100
            print_dual(f"    Progress: {i:,}/{total_episodes:,} episodes ({pct:.1f}%) - {len(monthly_records):,} monthly records")
    
    monthly_df = pd.DataFrame(monthly_records)
    print_dual(f"  Generated {len(monthly_df):,} monthly records")
    
    # Resolve overlaps (if CEO A ends after CEO B starts, B takes precedence)
    print_dual("\nResolving overlaps...")
    monthly_df = monthly_df.sort_values(['gvkey', 'year', 'month', 'date'])
    monthly_df = monthly_df.drop_duplicates(subset=['gvkey', 'year', 'month'], keep='last')
    print_dual(f"  Final monthly panel: {len(monthly_df):,} records")
    print_dual(f"  Date range: {monthly_df['date'].min()} to {monthly_df['date'].max()}\n")
    
    # Save output
    output_file = paths['output_dir'] / 'tenure_monthly.parquet'
    monthly_df.to_parquet(output_file, index=False)
    print_dual(f"Saved monthly tenure panel: {output_file}")
    
    # Generate variable reference
    var_ref_file = paths['output_dir'] / 'variable_reference.csv'
    generate_variable_reference(monthly_df, var_ref_file, print_dual)
    
    # Update latest symlink
    update_latest_symlink(paths['latest_dir'], paths['output_dir'], print_dual)
    
    print_dual("\n" + "="*80)
    print_dual("Step 1.3 completed successfully.")
    print_dual("="*80)
    
    sys.stdout = dual_writer.terminal
    dual_writer.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
