#!/usr/bin/env python3
"""
==============================================================================
STEP 3.1: Build Firm Controls
==============================================================================
ID: 3.1_FirmControls
Description: Computes firm-level control variables from Compustat and IBES.

Variables Computed:
    - Size: ln(atq) - Log of total assets
    - BM: ceqq / (cshoq * prccq) - Book-to-market ratio
    - Lev: ltq / atq - Leverage
    - ROA: niq / atq - Return on assets
    - EPS_Growth: (EPS - EPS_lag4) / |EPS_lag4| - YoY EPS growth
    - SurpDec: Earnings surprise decile (-5 to +5)
    - shift_intensity: Competition instrument (merged from CCCL)

Inputs:
    - 4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet
    - 1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet
    - 1_Inputs/tr_ibes/tr_ibes.parquet
    - 1_Inputs/CCCL instrument/instrument_shift_intensity_2005_2022.parquet

Outputs:
    - 4_Outputs/3_Financial_Features/{timestamp}/firm_controls_{year}.parquet

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
import importlib.util

# Dynamic import for 3.4_Utils.py
utils_path = Path(__file__).parent / "3.4_Utils.py"
spec = importlib.util.spec_from_file_location("utils", utils_path)
utils = importlib.util.module_from_spec(spec)
sys.modules["utils"] = utils
spec.loader.exec_module(utils)

from utils import DualWriter, get_latest_output_dir, generate_variable_reference, update_latest_symlink

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
        'compustat_file': root / '1_Inputs' / 'comp_na_daily_all' / 'comp_na_daily_all.parquet',
        'ibes_file': root / '1_Inputs' / 'tr_ibes' / 'tr_ibes.parquet',
        'cccl_file': root / '1_Inputs' / 'CCCL instrument' / 'instrument_shift_intensity_2005_2022.parquet',
        'ccm_file': root / '1_Inputs' / 'CRSPCompustat_CCM' / 'CRSPCompustat_CCM.parquet',
    }

    # Output directory
    output_base = root / config['paths']['outputs'] / "3_Financial_Features"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)
    paths['latest_dir'] = output_base / "latest"

    # Log directory
    log_base = root / config['paths']['logs'] / "3_Financial_Features"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}.log"

    return paths

# ==============================================================================
# Data Loading
# ==============================================================================

def load_manifest(manifest_dir):
    """Load manifest data"""
    manifest_file = manifest_dir / "master_sample_manifest.parquet"
    if not manifest_file.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_file}")
    
    df = pd.read_parquet(manifest_file)
    print(f"  Loaded manifest: {len(df):,} calls")
    
    # Ensure gvkey is string and zero-padded
    df['gvkey'] = df['gvkey'].astype(str).str.zfill(6)
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['year'] = df['start_date'].dt.year
    
    return df

def load_compustat(compustat_file):
    """Load Compustat data with only required columns"""
    print(f"  Loading Compustat (metadata only scan first)...")
    
    # Read only needed columns to save memory
    required_cols = ['gvkey', 'datadate', 'atq', 'ceqq', 'cshoq', 'prccq', 'ltq', 'niq', 'epspxq', 'actq', 'lctq', 'xrdq']
    
    df = pd.read_parquet(compustat_file, columns=required_cols)
    print(f"  Loaded Compustat: {len(df):,} quarterly observations")
    
    # Normalize
    df['gvkey'] = df['gvkey'].astype(str).str.zfill(6)
    df['datadate'] = pd.to_datetime(df['datadate'])
    
    # Convert Decimal types to float64 for numpy compatibility
    for col in required_cols[2:]: # fast way to get numeric cols
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('float64')
    
    return df

# ...

def compute_firm_controls(row, compustat_df):
    """Compute firm controls for a single call (vectorized implementation strongly preferred but this is row-wise).
    
    Wait, the original script might use a merge approach. Let's check the context.
    The previous view showed 'compute_firm_controls' was NOT visible in lines 1-100.
    I should check how variables are constructed.
    Based on typical structure, there's likely a merge then vectorized calc.
    
    Let's verify the processing logic in `3.1` before writing the calc code blindly.
    """

def load_ibes(ibes_file):
    """Load IBES data filtered to EPS quarterly"""
    print(f"  Loading IBES...")
    
    df = pd.read_parquet(ibes_file)
    print(f"  Raw IBES: {len(df):,} rows")
    
    # Filter to EPS quarterly only
    df = df[(df['MEASURE'] == 'EPS') & (df['FISCALP'] == 'QTR')].copy()
    print(f"  After EPS/QTR filter: {len(df):,} rows")
    
    # Keep only needed columns
    df = df[['TICKER', 'CUSIP', 'FPEDATS', 'STATPERS', 'MEANEST', 'ACTUAL']].copy()
    
    # Normalize dates
    df['FPEDATS'] = pd.to_datetime(df['FPEDATS'], errors='coerce')
    df['STATPERS'] = pd.to_datetime(df['STATPERS'], errors='coerce')
    
    return df

def load_cccl(cccl_file):
    """Load CCCL instrument data with all 6 shift_intensity variants"""
    print(f"  Loading CCCL instrument...")
    
    df = pd.read_parquet(cccl_file)
    print(f"  Loaded CCCL: {len(df):,} rows, {df['gvkey'].nunique():,} unique gvkeys")
    
    # Keep gvkey, year, and all shift_intensity variants
    intensity_cols = [
        'shift_intensity_sale_ff12', 'shift_intensity_mkvalt_ff12',
        'shift_intensity_sale_ff48', 'shift_intensity_mkvalt_ff48',
        'shift_intensity_sale_sic2', 'shift_intensity_mkvalt_sic2'
    ]
    
    # Filter to columns that exist
    available_cols = ['gvkey', 'year'] + [c for c in intensity_cols if c in df.columns]
    df = df[available_cols].copy()
    df['gvkey'] = df['gvkey'].astype(str).str.zfill(6)
    
    print(f"  Shift intensity variants: {len([c for c in intensity_cols if c in df.columns])}")
    
    return df

# ==============================================================================
# Variable Computation
# ==============================================================================

def compute_compustat_controls(manifest, compustat):
    """Compute Size, BM, Lev, ROA, EPS_Growth from Compustat (Vectorized with merge_asof)"""
    print("\n" + "="*60)
    print("Computing Compustat Controls (Optimized)")
    print("="*60)
    
    # Sort Compustat by gvkey and datadate
    compustat = compustat.sort_values(['gvkey', 'datadate']).reset_index(drop=True)
    
    # Compute lagged EPS (4 quarters back for YoY)
    compustat['epspxq_lag4'] = compustat.groupby('gvkey')['epspxq'].shift(4)
    
    # Compute control variables
    compustat['Size'] = np.log(compustat['atq'].clip(lower=0.01))
    compustat['BM'] = compustat['ceqq'] / (compustat['cshoq'] * compustat['prccq'])
    compustat['Lev'] = compustat['ltq'] / compustat['atq']
    compustat['ROA'] = compustat['niq'] / compustat['atq']
    
    # New Extended Controls
    # Current Ratio: Current Assets / Current Liabilities
    compustat['CurrentRatio'] = compustat['actq'] / compustat['lctq'].replace(0, np.nan)
    
    # R&D Intensity: R&D Expense / Total Assets (Treat missing R&D as 0)
    compustat['RD_Intensity'] = compustat['xrdq'].fillna(0) / compustat['atq']
    
    # EPS Growth: (EPS - EPS_lag4) / |EPS_lag4|
    mask = compustat['epspxq_lag4'].notna() & (compustat['epspxq_lag4'] != 0)
    compustat['EPS_Growth'] = np.nan
    compustat.loc[mask, 'EPS_Growth'] = (
        (compustat.loc[mask, 'epspxq'] - compustat.loc[mask, 'epspxq_lag4']) / 
        compustat.loc[mask, 'epspxq_lag4'].abs()
    )
    
    # Winsorize extreme values
    for col in ['Size', 'BM', 'Lev', 'ROA', 'EPS_Growth', 'CurrentRatio', 'RD_Intensity']:
        if compustat[col].notna().sum() > 0:
            p1, p99 = compustat[col].quantile([0.01, 0.99])
            compustat[col] = compustat[col].clip(lower=p1, upper=p99)
    
    print(f"  Compustat controls computed for {compustat['gvkey'].nunique():,} firms")
    
    # Optimized Matching using merge_asof
    print(f"  Matching calls to Compustat quarters (vectorized)...")
    
    # Prepare Manifest
    # Ensure datetime and sorted
    manifest_sorted = manifest.copy()
    manifest_sorted['start_date'] = pd.to_datetime(manifest_sorted['start_date'])
    manifest_sorted = manifest_sorted.sort_values('start_date')
    
    # Prepare Compustat
    comp_sorted = compustat.copy()
    comp_sorted['datadate'] = pd.to_datetime(comp_sorted['datadate'])
    comp_sorted = comp_sorted.sort_values('datadate')
    
    # Check join keys
    manifest_sorted['gvkey'] = manifest_sorted['gvkey'].astype(str)
    comp_sorted['gvkey'] = comp_sorted['gvkey'].astype(str)
    
    # merge_asof
    # direction='backward': for a call at T, finds the last compustat date <= T
    merged = pd.merge_asof(
        manifest_sorted,
        comp_sorted[['gvkey', 'datadate', 'Size', 'BM', 'Lev', 'ROA', 'EPS_Growth', 'CurrentRatio', 'RD_Intensity']],
        left_on='start_date',
        right_on='datadate',
        by='gvkey',
        direction='backward'
    )
    
    # Check match rate
    matched = merged['Size'].notna().sum()
    print(f"  Matched: {matched:,} / {len(manifest):,} ({matched/len(manifest)*100:.1f}%)")
    
    # Return containing only the result columns, indexed by file_name original order? 
    # The calling function expects a dataframe with these columns that it can merge back to manifest on file_name
    # Since we have file_name in merged (from manifest), we can return the relevant columns.
    
    results_df = merged[['file_name', 'Size', 'BM', 'Lev', 'ROA', 'EPS_Growth', 'CurrentRatio', 'RD_Intensity']].copy()
    
    return results_df

def compute_earnings_surprise(manifest, ibes, ccm_file):
    """Compute SurpDec from IBES"""
    print("\n" + "="*60)
    print("Computing Earnings Surprise (IBES)")
    print("="*60)
    
    # Load CCM for LPERMNO linking
    ccm = pd.read_parquet(ccm_file)
    ccm['cusip8'] = ccm['cusip'].astype(str).str[:8]
    ccm['LPERMNO'] = pd.to_numeric(ccm['LPERMNO'], errors='coerce')
    ccm_cusip = ccm[['cusip8', 'LPERMNO', 'gvkey']].drop_duplicates().dropna()
    ccm_cusip['gvkey'] = ccm_cusip['gvkey'].astype(str).str.zfill(6)
    
    # Link IBES to gvkey via CUSIP
    ibes['cusip8'] = ibes['CUSIP'].astype(str).str[:8]
    ibes_linked = ibes.merge(ccm_cusip[['cusip8', 'gvkey']], on='cusip8', how='inner')
    print(f"  IBES linked to gvkey: {len(ibes_linked):,} / {len(ibes):,}")
    
    # Compute raw surprise
    ibes_linked['surprise_raw'] = ibes_linked['ACTUAL'] - ibes_linked['MEANEST']
    
    # Match to manifest
    print(f"  Matching calls to IBES forecasts...")
    
    ibes_grouped = {gvkey: group for gvkey, group in ibes_linked.groupby('gvkey')}
    
    results = []
    matched = 0
    
    for idx, row in manifest.iterrows():
        gvkey = row['gvkey']
        call_date = row['start_date']
        
        result = {
            'file_name': row['file_name'],
            'ActualEPS': np.nan,
            'ForecastEPS': np.nan,
            'surprise_raw': np.nan
        }
        
        if gvkey in ibes_grouped:
            firm_ibes = ibes_grouped[gvkey]
            # Find forecast within +/- 45 days of call
            mask = (
                (firm_ibes['FPEDATS'] >= call_date - pd.Timedelta(days=45)) &
                (firm_ibes['FPEDATS'] <= call_date + pd.Timedelta(days=45)) &
                (firm_ibes['STATPERS'] <= call_date)
            )
            if mask.any():
                closest = firm_ibes[mask].iloc[-1]
                result['ActualEPS'] = closest['ACTUAL']
                result['ForecastEPS'] = closest['MEANEST']
                result['surprise_raw'] = closest['surprise_raw']
                matched += 1
        
        results.append(result)
    
    results_df = pd.DataFrame(results)
    print(f"  Matched: {matched:,} / {len(manifest):,} ({matched/len(manifest)*100:.1f}%)")
    
    # Compute surprise deciles within quarter
    manifest_with_surprise = manifest.merge(results_df, on='file_name')
    manifest_with_surprise['call_quarter'] = manifest_with_surprise['start_date'].dt.to_period('Q')
    
    def rank_surprises(group):
        """Rank surprises into -5 to +5 scale"""
        surprises = group['surprise_raw']
        ranks = pd.Series(index=group.index, dtype=float)
        
        valid_mask = surprises.notna()
        if valid_mask.sum() < 5:
            return ranks
        
        pos_mask = surprises > 0
        zero_mask = surprises == 0
        neg_mask = surprises < 0
        
        # Positive: 5 (largest) to 1 (smallest)
        if pos_mask.sum() > 0:
            pos_ranks = surprises[pos_mask].rank(ascending=False, pct=True)
            ranks.loc[pos_mask] = (5 - pos_ranks * 4).round().clip(1, 5)
        
        # Zero: 0
        ranks.loc[zero_mask] = 0
        
        # Negative: -1 (smallest abs) to -5 (largest abs)
        if neg_mask.sum() > 0:
            neg_ranks = surprises[neg_mask].abs().rank(ascending=True, pct=True)
            ranks.loc[neg_mask] = -(1 + neg_ranks * 4).round().clip(1, 5)
        
        return ranks
    
    manifest_with_surprise['SurpDec'] = manifest_with_surprise.groupby('call_quarter', group_keys=False).apply(
        lambda g: rank_surprises(g)
    )
    
    # Return just file_name and computed columns
    return manifest_with_surprise[['file_name', 'ActualEPS', 'ForecastEPS', 'surprise_raw', 'SurpDec']]

def merge_cccl(manifest, cccl):
    """Merge all shift_intensity variants from CCCL"""
    print("\n" + "="*60)
    print("Merging CCCL Instrument")
    print("="*60)
    
    # Get shift intensity columns
    intensity_cols = [c for c in cccl.columns if c.startswith('shift_intensity')]
    merge_cols = ['gvkey', 'year'] + intensity_cols
    
    # Merge on gvkey and year
    merged = manifest[['file_name', 'gvkey', 'year']].merge(
        cccl[merge_cols],
        on=['gvkey', 'year'],
        how='left'
    )
    
    # Report coverage for first intensity column
    if intensity_cols:
        matched = merged[intensity_cols[0]].notna().sum()
        print(f"  Matched: {matched:,} / {len(manifest):,} ({matched/len(manifest)*100:.1f}%)")
        print(f"  Shift intensity columns: {intensity_cols}")
    
    return merged[['file_name'] + intensity_cols]

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
    print("STEP 3.1: Build Firm Controls")
    print(f"Timestamp: {timestamp}")
    print("="*60)
    
    # Load data
    print("\nLoading data...")
    manifest = load_manifest(paths['manifest_dir'])
    compustat = load_compustat(paths['compustat_file'])
    ibes = load_ibes(paths['ibes_file'])
    cccl = load_cccl(paths['cccl_file'])
    
    # Compute variables
    comp_controls = compute_compustat_controls(manifest, compustat)
    surp_controls = compute_earnings_surprise(manifest, ibes, paths['ccm_file'])
    cccl_controls = merge_cccl(manifest, cccl)
    
    # Combine all controls
    print("\n" + "="*60)
    print("Combining Controls")
    print("="*60)
    
    result = manifest[['file_name', 'gvkey', 'start_date', 'year']].copy()
    result = result.merge(comp_controls, on='file_name', how='left')
    result = result.merge(surp_controls, on='file_name', how='left')
    result = result.merge(cccl_controls, on='file_name', how='left')
    
    # Save by year
    print("\nSaving outputs by year...")
    for year, group in result.groupby('year'):
        output_file = paths['output_dir'] / f"firm_controls_{year}.parquet"
        group.to_parquet(output_file, index=False)
        print(f"  Saved {year}: {len(group):,} calls -> {output_file.name}")
    
    # Generate variable reference
    generate_variable_reference(result, paths['output_dir'] / "variable_reference.csv")
    
    # Update latest symlink
    update_latest_symlink(paths['latest_dir'], paths['output_dir'])
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total calls processed: {len(result):,}")
    print(f"\nVariable coverage:")
    core_cols = ['Size', 'BM', 'Lev', 'ROA', 'EPS_Growth', 'SurpDec']
    intensity_cols = [c for c in result.columns if c.startswith('shift_intensity')]
    for col in core_cols + intensity_cols:
        if col in result.columns:
            n = result[col].notna().sum()
            print(f"  {col}: {n:,} / {len(result):,} ({n/len(result)*100:.1f}%)")
    
    print(f"\nOutputs saved to: {paths['output_dir']}")
    print(f"Log saved to: {paths['log_file']}")
    
    dual_writer.close()
    sys.stdout = dual_writer.terminal

if __name__ == "__main__":
    main()
