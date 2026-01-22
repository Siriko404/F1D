#!/usr/bin/env python3
"""
==============================================================================
STEP 3.3: Build Event Flags
==============================================================================
ID: 3.3_EventFlags
Description: Computes takeover event flags from SDC M&A data.

Variables Computed:
    - Takeover: Binary flag (1 if firm was takeover target within 365 days)
    - Takeover_Type: "Friendly" or "Uninvited" (from Deal Attitude)
    - Duration: Quarters until takeover event (for survival analysis)

Inputs:
    - 4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet
    - 1_Inputs/SDC/sdc-ma-merged.parquet

Outputs:
    - 4_Outputs/3_Financial_Features/{timestamp}/event_flags_{year}.parquet

Deterministic: true
==============================================================================
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yaml
import importlib.util

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
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_paths(config, timestamp):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    paths = {
        'root': root,
        'manifest_dir': root / '4_Outputs' / '1.0_BuildSampleManifest' / 'latest',
        'sdc_file': root / '1_Inputs' / 'SDC' / 'sdc-ma-merged.parquet',
    }

    # Output directory
    output_base = root / config['paths']['outputs'] / "3_Financial_Features"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)
    paths['latest_dir'] = output_base / "latest"

    # Log directory
    log_base = root / config['paths']['logs'] / "3_Financial_Features"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}_events.log"

    return paths

# ==============================================================================
# Data Loading
# ==============================================================================

def load_manifest(manifest_dir):
    """Load manifest data"""
    manifest_file = manifest_dir / "master_sample_manifest.parquet"
    df = pd.read_parquet(manifest_file)
    
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['year'] = df['start_date'].dt.year
    
    # Extract CUSIP6 for SDC matching
    if 'cusip' in df.columns:
        df['cusip6'] = df['cusip'].astype(str).str[:6]
    
    print(f"  Loaded manifest: {len(df):,} calls")
    print(f"  Calls with CUSIP: {df['cusip6'].notna().sum():,}")
    
    return df

def load_sdc(sdc_file):
    """Load SDC M&A data"""
    print(f"  Loading SDC M&A data...")
    
    df = pd.read_parquet(sdc_file)
    print(f"  Raw SDC: {len(df):,} deals")
    
    # Normalize column names (SDC has spaces in names)
    col_mapping = {
        'Target 6-digit CUSIP': 'target_cusip6',
        'Date Announced': 'date_announced',
        'Date Effective': 'date_effective',
        'Date Withdrawn': 'date_withdrawn',
        'Deal Attitude': 'deal_attitude',
        'Deal Status': 'deal_status'
    }
    
    for old_name, new_name in col_mapping.items():
        if old_name in df.columns:
            df.rename(columns={old_name: new_name}, inplace=True)
    
    # Ensure dates are datetime
    for col in ['date_announced', 'date_effective', 'date_withdrawn']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Clean CUSIP
    df['target_cusip6'] = df['target_cusip6'].astype(str).str[:6]
    
    print(f"  SDC date range: {df['date_announced'].min()} to {df['date_announced'].max()}")
    print(f"  Unique target CUSIPs: {df['target_cusip6'].nunique():,}")
    
    # Categorize deal attitude
    print(f"\n  Deal Attitude distribution:")
    if 'deal_attitude' in df.columns:
        print(df['deal_attitude'].value_counts())
    
    return df

# ==============================================================================
# Variable Computation
# ==============================================================================

def compute_takeover_flags(manifest, sdc):
    """Compute takeover flags for each call"""
    print("\n" + "="*60)
    print("Computing Takeover Flags")
    print("="*60)
    
    # Create lookup: cusip6 -> list of (date_announced, deal_attitude)
    sdc_by_cusip = {}
    for _, row in sdc.iterrows():
        cusip6 = row['target_cusip6']
        if pd.notna(row['date_announced']):
            if cusip6 not in sdc_by_cusip:
                sdc_by_cusip[cusip6] = []
            sdc_by_cusip[cusip6].append({
                'date_announced': row['date_announced'],
                'deal_attitude': row.get('deal_attitude', 'Unknown')
            })
    
    print(f"  SDC lookup built: {len(sdc_by_cusip):,} unique target CUSIPs")
    
    results = []
    takeover_count = 0
    
    for idx, row in manifest.iterrows():
        cusip6 = row.get('cusip6')
        call_date = row['start_date']
        
        result = {
            'file_name': row['file_name'],
            'Takeover': 0,
            'Takeover_Type': None,
            'Duration': 4.0  # Default: censored at 4 quarters
        }
        
        if pd.isna(cusip6) or cusip6 not in sdc_by_cusip:
            results.append(result)
            continue
        
        # Check for takeover within 365 days of call
        for deal in sdc_by_cusip[cusip6]:
            days_until = (deal['date_announced'] - call_date).days
            
            if 0 <= days_until <= 365:
                result['Takeover'] = 1
                
                # Classify deal type
                attitude = str(deal['deal_attitude']).lower() if deal['deal_attitude'] else ''
                if 'hostile' in attitude or 'unsolicited' in attitude:
                    result['Takeover_Type'] = 'Uninvited'
                else:
                    result['Takeover_Type'] = 'Friendly'
                
                # Duration in quarters
                result['Duration'] = max(0.25, days_until / 91.25)  # ~91.25 days per quarter
                
                takeover_count += 1
                break  # Take first matching deal
        
        results.append(result)
        
        if (idx + 1) % 10000 == 0:
            print(f"  Processed {idx + 1:,} calls...")
    
    results_df = pd.DataFrame(results)
    
    print(f"\n  Takeover events: {takeover_count:,} / {len(manifest):,} ({takeover_count/len(manifest)*100:.2f}%)")
    print(f"\n  Takeover Type distribution:")
    print(results_df[results_df['Takeover'] == 1]['Takeover_Type'].value_counts())
    
    return results_df

# ==============================================================================
# Main
# ==============================================================================

def main():
    """Main execution"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    config = load_config()
    paths = setup_paths(config, timestamp)
    
    # Setup logging
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer
    
    print("="*60)
    print("STEP 3.3: Build Event Flags")
    print(f"Timestamp: {timestamp}")
    print("="*60)
    
    # Load data
    print("\nLoading data...")
    manifest = load_manifest(paths['manifest_dir'])
    sdc = load_sdc(paths['sdc_file'])
    
    # Compute takeover flags
    event_flags = compute_takeover_flags(manifest, sdc)
    
    # Merge with manifest
    result = manifest[['file_name', 'gvkey', 'start_date', 'year']].merge(event_flags, on='file_name')
    
    # Save by year
    print("\nSaving outputs by year...")
    for year, group in result.groupby('year'):
        output_file = paths['output_dir'] / f"event_flags_{year}.parquet"
        group.to_parquet(output_file, index=False)
        print(f"  Saved {year}: {len(group):,} calls -> {output_file.name}")
    
    # Generate variable reference
    generate_variable_reference(result, paths['output_dir'] / "event_flags_variable_reference.csv")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total calls processed: {len(result):,}")
    print(f"\nVariable coverage:")
    print(f"  Takeover: {result['Takeover'].sum():,} events ({result['Takeover'].mean()*100:.2f}%)")
    print(f"  Duration mean (takeovers only): {result[result['Takeover']==1]['Duration'].mean():.2f} quarters")
    
    print(f"\nOutputs saved to: {paths['output_dir']}")
    
    dual_writer.close()
    sys.stdout = dual_writer.terminal

if __name__ == "__main__":
    main()
