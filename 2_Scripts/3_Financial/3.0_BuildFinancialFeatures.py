#!/usr/bin/env python3
"""
==============================================================================
STEP 3: Build Financial Features (Orchestrator)
==============================================================================
Coordinates 3.1, 3.2, 3.3 to write ALL outputs to a single timestamped folder.
==============================================================================
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import yaml
import pandas as pd
import importlib.util

# Dynamic import for 3.4_Utils.py
utils_path = Path(__file__).parent / "3.4_Utils.py"
spec = importlib.util.spec_from_file_location("utils", utils_path)
utils = importlib.util.module_from_spec(spec)
sys.modules["utils"] = utils
spec.loader.exec_module(utils)

from utils import DualWriter, update_latest_symlink, generate_variable_reference

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
        'script_dir': Path(__file__).parent,
        'manifest_dir': root / '4_Outputs' / '1.0_BuildSampleManifest' / 'latest',
        'compustat_file': root / '1_Inputs' / 'comp_na_daily_all' / 'comp_na_daily_all.parquet',
        'ibes_file': root / '1_Inputs' / 'tr_ibes' / 'tr_ibes.parquet',
        'cccl_file': root / '1_Inputs' / 'CCCL instrument' / 'instrument_shift_intensity_2005_2022.parquet',
        'ccm_file': root / '1_Inputs' / 'CRSPCompustat_CCM' / 'CRSPCompustat_CCM.parquet',
        'crsp_dir': root / '1_Inputs' / 'CRSP_DSF',
        'sdc_file': root / '1_Inputs' / 'SDC' / 'sdc-ma-merged.parquet',
    }
    
    output_base = root / config['paths']['outputs'] / "3_Financial_Features"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)
    paths['latest_dir'] = output_base / "latest"
    
    log_base = root / config['paths']['logs'] / "3_Financial_Features"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}.log"
    
    return paths

# ==============================================================================
# Import substep modules directly
# ==============================================================================

def import_module(name, path):
    """Dynamically import a module by path."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# ==============================================================================
# Main
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description='Step 3: Build Financial Features')
    parser.add_argument('--dry-run', action='store_true', help='Show plan without executing')
    parser.add_argument('--test', action='store_true', help='Run on first 3 years only for testing')
    args = parser.parse_args()
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    config = load_config()
    paths = setup_paths(config, timestamp)
    
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer
    
    print("="*60)
    print("STEP 3: Build Financial Features (Orchestrator)")
    print(f"Timestamp: {timestamp}")
    print(f"Output: {paths['output_dir']}")
    if args.test:
        print("Mode: TEST (First 3 years only)")
    print("="*60)
    
    if args.dry_run:
        print("\n[DRY RUN MODE]")
        print("  1. Load manifest")
        print("  2. Compute Firm Controls (3.1) -> firm_controls_{year}.parquet")
        print("  3. Compute Market Variables (3.2) -> market_variables_{year}.parquet")
        print("  4. Compute Event Flags (3.3) -> event_flags_{year}.parquet")
        print("  5. Generate report_step3.md + variable_reference.csv")
        dual_writer.close()
        sys.stdout = dual_writer.terminal
        return
    
    # Import substep modules
    script_dir = paths['script_dir']
    step31 = import_module("step31", script_dir / "3.1_FirmControls.py")
    step32 = import_module("step32", script_dir / "3.2_MarketVariables.py")
    step33 = import_module("step33", script_dir / "3.3_EventFlags.py")
    
    # Load manifest once
    print("\nLoading manifest...")
    manifest = pd.read_parquet(paths['manifest_dir'] / "master_sample_manifest.parquet")
    manifest['start_date'] = pd.to_datetime(manifest['start_date'])
    manifest['year'] = manifest['start_date'].dt.year
    manifest['gvkey'] = manifest['gvkey'].astype(str).str.zfill(6)
    print(f"  Loaded: {len(manifest):,} calls")
    
    years = sorted(manifest['year'].unique())
    if args.test:
        years = years[:3]
        print(f"  TEST MODE: Limiting to years {years}")
    
    # ========== 3.1 Firm Controls ==========
    
    # ========== 3.1 Firm Controls ==========
    print("\n" + "="*60)
    print("STEP 3.1: Firm Controls")
    print("="*60)
    
    # Load data
    compustat = step31.load_compustat(paths['compustat_file'])
    ibes = step31.load_ibes(paths['ibes_file'])
    cccl = step31.load_cccl(paths['cccl_file'])
    
    # Compute
    comp_controls = step31.compute_compustat_controls(manifest, compustat)
    surp_controls = step31.compute_earnings_surprise(manifest, ibes, paths['ccm_file'])
    cccl_controls = step31.merge_cccl(manifest, cccl)
    
    # Merge
    firm_result = manifest[['file_name', 'gvkey', 'start_date', 'year']].copy()
    firm_result = firm_result.merge(comp_controls, on='file_name', how='left')
    firm_result = firm_result.merge(surp_controls, on='file_name', how='left')
    firm_result = firm_result.merge(cccl_controls, on='file_name', how='left')
    
    # Save by year
    for year, group in firm_result.groupby('year'):
        group.to_parquet(paths['output_dir'] / f"firm_controls_{year}.parquet", index=False)
    print(f"  Saved {len(years)} firm_controls files")
    
    del compustat, ibes, cccl
    
    # ========== 3.2 Market Variables ==========
    print("\n" + "="*60)
    print("STEP 3.2: Market Variables")
    print("="*60)
    
    # Prepare manifest with PERMNO
    manifest_with_permno = step32.load_manifest_with_permno(paths['manifest_dir'], paths['ccm_file'])
    
    all_market_results = []
    for year in years:
        print(f"\n  Year {year}...")
        year_manifest = manifest_with_permno[manifest_with_permno['year'] == year].copy()
        
        crsp = step32.load_crsp_for_years(paths['crsp_dir'], [year - 1, year])
        if crsp is None:
            print(f"    No CRSP data, skipping")
            continue
        
        year_manifest = step32.compute_returns_for_year(year_manifest, crsp, config)
        year_manifest = step32.compute_liquidity_for_year(year_manifest, crsp, config)
        
        cols = ['file_name', 'gvkey', 'start_date', 'year', 'StockRet', 'MarketRet',
                'Amihud', 'Corwin_Schultz', 'Delta_Amihud', 'Delta_Corwin_Schultz', 'Volatility']
        year_manifest[cols].to_parquet(paths['output_dir'] / f"market_variables_{year}.parquet", index=False)
        all_market_results.append(year_manifest[cols])
        
        del crsp
        import gc
        gc.collect()
    
    print(f"  Saved {len(years)} market_variables files")
    
    # ========== 3.3 Event Flags ==========
    print("\n" + "="*60)
    print("STEP 3.3: Event Flags")
    print("="*60)
    
    manifest_for_sdc = step33.load_manifest(paths['manifest_dir'])
    sdc = step33.load_sdc(paths['sdc_file'])
    event_flags = step33.compute_takeover_flags(manifest_for_sdc, sdc)
    
    event_result = manifest_for_sdc[['file_name', 'gvkey', 'start_date', 'year']].merge(event_flags, on='file_name')
    
    for year, group in event_result.groupby('year'):
        group.to_parquet(paths['output_dir'] / f"event_flags_{year}.parquet", index=False)
    print(f"  Saved {len(years)} event_flags files")
    
    # ========== Generate Reports ==========
    print("\n" + "="*60)
    print("Generating Reports")
    print("="*60)
    
    # Combine for variable reference
    all_data = pd.concat([firm_result, pd.concat(all_market_results, ignore_index=True)], axis=1)
    generate_variable_reference(all_data, paths['output_dir'] / "variable_reference.csv")
    
    # Report
    report = f"""# Step 3: Financial Features Report

**Generated:** {timestamp}
**Output:** `{paths['output_dir']}`

## Outputs (per year)

| Type | Files | Variables |
|------|-------|-----------|
| Firm Controls | {len(list(paths['output_dir'].glob('firm_controls_*.parquet')))} | Size, BM, Lev, ROA, EPS_Growth, SurpDec, shift_intensity |
| Market Variables | {len(list(paths['output_dir'].glob('market_variables_*.parquet')))} | StockRet, MarketRet, Amihud, Corwin_Schultz, Deltas |
| Event Flags | {len(list(paths['output_dir'].glob('event_flags_*.parquet')))} | Takeover, Takeover_Type, Duration |

## Coverage Summary

- Total calls: {len(manifest):,}
- StockRet: {pd.concat(all_market_results)['StockRet'].notna().sum():,} ({pd.concat(all_market_results)['StockRet'].notna().mean()*100:.1f}%)
- Amihud: {pd.concat(all_market_results)['Amihud'].notna().sum():,} ({pd.concat(all_market_results)['Amihud'].notna().mean()*100:.1f}%)
"""
    
    with open(paths['output_dir'] / "report_step3.md", 'w') as f:
        f.write(report)
    print("  Generated report_step3.md")
    
    # Update symlink
    update_latest_symlink(paths['latest_dir'], paths['output_dir'])
    
    print("\n" + "="*60)
    print("COMPLETE")
    print("="*60)
    print(f"All outputs in: {paths['output_dir']}")
    
    dual_writer.close()
    sys.stdout = dual_writer.terminal

if __name__ == "__main__":
    main()
