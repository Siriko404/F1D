#!/usr/bin/env python3
"""
==============================================================================
STEP 1.2: Entity Resolution (CCM Linking) - OPTIMIZED WITH DEDUP-INDEX
==============================================================================
ID: 1.2_LinkEntities
Description: Links cleaned metadata to CCM database using 4-tier strategy:
             Tier 1 (PERMNO+Date), Tier 2 (CUSIP8+Date), Tier 3 (Fuzzy Name).
             
             OPTIMIZATION: Deduplicates by company_id before matching,
             then broadcasts results to all related records.
             ~11k unique companies instead of 297k individual calls.
             
Inputs:
    - 4_Outputs/1.1_CleanMetadata/latest/metadata_cleaned.parquet
    - 1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet
    - 1_Inputs/Siccodes12.zip
    - 1_Inputs/Siccodes48.zip
    - config/project.yaml
    
Outputs:
    - 4_Outputs/1.2_LinkEntities/{timestamp}/metadata_linked.parquet
    - 4_Outputs/1.2_LinkEntities/{timestamp}/variable_reference.csv
    - 4_Outputs/1.2_LinkEntities/{timestamp}/report_step_1_2.md
    - 3_Logs/1.2_LinkEntities/{timestamp}.log
    
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
import re
import zipfile

# Try rapidfuzz
try:
    from rapidfuzz import fuzz, process
    FUZZ_AVAILABLE = True
except ImportError:
    FUZZ_AVAILABLE = False
    print("Warning: rapidfuzz not available, skipping fuzzy matching")

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
        'metadata': root / '4_Outputs' / '1.1_CleanMetadata' / 'latest' / 'metadata_cleaned.parquet',
        'ccm': root / '1_Inputs' / 'CRSPCompustat_CCM' / 'CRSPCompustat_CCM.parquet',
        'ccm_varref': root / '1_Inputs' / 'CRSPCompustat_CCM' / 'CRSP_CCM_Variable_Reference.txt',
        'ff12': root / '1_Inputs' / 'Siccodes12.zip',
        'ff48': root / '1_Inputs' / 'Siccodes48.zip',
    }

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config['paths']['outputs'] / "1.2_LinkEntities"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)

    paths['latest_dir'] = output_base / "latest"

    log_base = root / config['paths']['logs'] / "1.2_LinkEntities"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}.log"

    return paths, timestamp

# ==============================================================================
# Utility functions
# ==============================================================================

def normalize_company_name(name):
    """Normalize company name for fuzzy matching"""
    if pd.isna(name):
        return ""
    
    name = str(name).upper().strip()
    name = re.sub(r'[^\w\s]', ' ', name)
    
    suffixes = ['INC', 'CORP', 'LTD', 'LLC', 'CO', 'COMPANY',
                'CORPORATION', 'INCORPORATED', 'LIMITED', 'PLC', 'SA', 'NV']
    for suffix in suffixes:
        name = re.sub(rf'\b{suffix}\b', '', name)
    
    name = ' '.join(name.split())
    return name

def parse_ff_industries(zip_path, num_industries):
    """Parse Fama-French industry classification from SIC code ranges"""
    with zipfile.ZipFile(zip_path, 'r') as z:
        txt_file = z.namelist()[0]
        with z.open(txt_file) as f:
            content = f.read().decode('utf-8')
    
    industry_map = {}
    lines = content.strip().split('\n')
    
    current_industry_code = None
    current_industry_name = None
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        
        parts = stripped.split(maxsplit=2)
        if len(parts) >= 2 and parts[0].isdigit():
            current_industry_code = int(parts[0])
            current_industry_name = parts[1]
        elif stripped and current_industry_code is not None:
            sic_range = stripped.split()[0] if stripped.split() else ""
            if '-' in sic_range:
                try:
                    start, end = sic_range.split('-')
                    for sic in range(int(start), int(end) + 1):
                        industry_map[sic] = (current_industry_code, current_industry_name)
                except ValueError:
                    continue
    
    return industry_map

def load_variable_descriptions(ref_files):
    """Load variable descriptions from reference files"""
    descriptions = {}
    
    for source, path in ref_files.items():
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for line in lines[1:]:  # Skip header
                    parts = line.strip().split('\t')
                    if len(parts) >= 3:
                        var_name = parts[0].lower()
                        var_desc = parts[2]
                        descriptions[var_name] = {'source': source, 'description': var_desc}
            except Exception:
                pass
    
    return descriptions

# Generate_variable_reference and update_latest_symlink imported from step1_utils

# ==============================================================================
# Main processing with DEDUP-INDEX optimization
# ==============================================================================

def main():
    config = load_config()
    paths, timestamp = setup_paths(config)
    
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer
    
    print_dual("="*80)
    print_dual("STEP 1.2: Entity Resolution (CCM Linking) - DEDUP-INDEX OPTIMIZED")
    print_dual("="*80)
    print_dual(f"Timestamp: {timestamp}\n")
    
    # Load metadata
    print_dual("Loading cleaned metadata...")
    df = pd.read_parquet(paths['metadata'])
    total_calls = len(df)
    print_dual(f"  Loaded {total_calls:,} calls\n")
    
    # Load CCM
    print_dual("Loading CCM database...")
    ccm = pd.read_parquet(paths['ccm'])
    ccm['LINKDT'] = pd.to_datetime(ccm['LINKDT'])
    ccm['LINKENDDT_clean'] = ccm['LINKENDDT'].replace('E', '2099-12-31')
    ccm['LINKENDDT_dt'] = pd.to_datetime(ccm['LINKENDDT_clean'])
    ccm['cusip8'] = ccm['cusip'].astype(str).str[:8]
    print_dual(f"  Loaded {len(ccm):,} CCM link records\n")
    
    # ==========================================================================
    # DEDUP-INDEX OPTIMIZATION
    # ==========================================================================
    print_dual("Building dedup-index...")
    
    # Build index: company_id -> list of file_names
    dedup_index = df.groupby('company_id')['file_name'].apply(list).to_dict()
    unique_company_ids = list(dedup_index.keys())
    
    print_dual(f"  Unique companies: {len(unique_company_ids):,} (from {total_calls:,} calls)")
    print_dual(f"  Compression ratio: {total_calls / len(unique_company_ids):.1f}x\n")
    
    # Create unique records (one per company_id)
    unique_df = df.drop_duplicates('company_id')[['company_id', 'permno', 'cusip', 
                                                   'company_name', 'company_ticker', 'start_date']].copy()
    unique_df = unique_df.reset_index(drop=True)
    
    # Initialize linking columns on unique_df
    unique_df['gvkey'] = np.nan
    unique_df['conm'] = np.nan
    unique_df['sic'] = np.nan
    unique_df['link_method'] = np.nan
    unique_df['link_quality'] = np.nan
    
    # Convert to object type
    for col in ['gvkey', 'conm', 'sic', 'link_method']:
        unique_df[col] = unique_df[col].astype('object')
    
    unique_df['start_date'] = pd.to_datetime(unique_df['start_date'])
    
    print_dual("Executing 4-tier linking strategy on UNIQUE companies:")
    
    # ==========================================================================
    # TIER 1: PERMNO + Date Range
    # ==========================================================================
    print_dual("\n  Tier 1: PERMNO + Date Range...")
    
    unmatched_mask = unique_df['gvkey'].isna()
    has_permno = unique_df['permno'].notna() & (unique_df['permno'] != '')
    tier1_candidates = unique_df[unmatched_mask & has_permno].copy()
    
    print_dual(f"    Candidates: {len(tier1_candidates):,} unmatched companies with PERMNO")
    
    if len(tier1_candidates) > 0:
        tier1_candidates['permno_int'] = pd.to_numeric(tier1_candidates['permno'], errors='coerce').astype('Int64')
        tier1_candidates = tier1_candidates[tier1_candidates['permno_int'].notna()]
        
        merged = tier1_candidates[['company_id', 'permno_int', 'start_date']].merge(
            ccm[['LPERMNO', 'gvkey', 'conm', 'sic', 'LINKPRIM', 'LINKTYPE', 'LINKDT', 'LINKENDDT_dt']],
            left_on='permno_int',
            right_on='LPERMNO',
            how='inner'
        )
        
        merged = merged[(merged['start_date'] >= merged['LINKDT']) & 
                        (merged['start_date'] <= merged['LINKENDDT_dt'])]
        
        linkprim_priority = {'P': 1, 'C': 2, 'J': 3, 'N': 4}
        linktype_priority = {'LC': 1, 'LU': 2}
        merged['linkprim_rank'] = merged['LINKPRIM'].map(linkprim_priority).fillna(99)
        merged['linktype_rank'] = merged['LINKTYPE'].map(linktype_priority).fillna(99)
        merged = merged.sort_values(['company_id', 'linkprim_rank', 'linktype_rank'])
        merged = merged.drop_duplicates(subset=['company_id'], keep='first')
        
        print_dual(f"    Matched: {len(merged):,} companies")
        
        if len(merged) > 0:
            update_df = merged[['company_id', 'gvkey', 'conm', 'sic']].copy()
            update_df['link_method'] = 'permno_date'
            update_df['link_quality'] = 100
            
            unique_df = unique_df.set_index('company_id')
            update_df = update_df.set_index('company_id')
            
            unique_df.loc[update_df.index, 'gvkey'] = update_df['gvkey']
            unique_df.loc[update_df.index, 'conm'] = update_df['conm']
            unique_df.loc[update_df.index, 'sic'] = update_df['sic']
            unique_df.loc[update_df.index, 'link_method'] = update_df['link_method']
            unique_df.loc[update_df.index, 'link_quality'] = update_df['link_quality']
            
            unique_df = unique_df.reset_index()
    
    tier1_matched = unique_df['gvkey'].notna().sum()
    print_dual(f"    [CHECK] Total matched after Tier 1: {tier1_matched:,}")
    
    # ==========================================================================
    # TIER 2: CUSIP8 + Date Range
    # ==========================================================================
    print_dual("\n  Tier 2: CUSIP8 + Date Range...")
    
    unmatched_mask = unique_df['gvkey'].isna()
    has_cusip = unique_df['cusip'].notna() & (unique_df['cusip'] != '')
    tier2_candidates = unique_df[unmatched_mask & has_cusip].copy()
    
    print_dual(f"    Candidates: {len(tier2_candidates):,} unmatched companies with CUSIP")
    
    if len(tier2_candidates) > 0:
        tier2_candidates['cusip8'] = tier2_candidates['cusip'].astype(str).str[:8]
        
        merged = tier2_candidates[['company_id', 'cusip8', 'start_date']].merge(
            ccm[['cusip8', 'gvkey', 'conm', 'sic', 'LINKDT', 'LINKENDDT_dt']],
            on='cusip8',
            how='inner'
        )
        
        merged = merged[(merged['start_date'] >= merged['LINKDT']) & 
                        (merged['start_date'] <= merged['LINKENDDT_dt'])]
        merged = merged.drop_duplicates(subset=['company_id'], keep='first')
        
        print_dual(f"    Matched: {len(merged):,} companies")
        
        if len(merged) > 0:
            update_df = merged[['company_id', 'gvkey', 'conm', 'sic']].copy()
            update_df['link_method'] = 'cusip8_date'
            update_df['link_quality'] = 90
            
            unique_df = unique_df.set_index('company_id')
            update_df = update_df.set_index('company_id')
            
            unique_df.loc[update_df.index, 'gvkey'] = update_df['gvkey']
            unique_df.loc[update_df.index, 'conm'] = update_df['conm']
            unique_df.loc[update_df.index, 'sic'] = update_df['sic']
            unique_df.loc[update_df.index, 'link_method'] = update_df['link_method']
            unique_df.loc[update_df.index, 'link_quality'] = update_df['link_quality']
            
            unique_df = unique_df.reset_index()
    
    tier2_matched = unique_df['gvkey'].notna().sum()
    print_dual(f"    [CHECK] Total matched after Tier 2: {tier2_matched:,}")
    
    # ==========================================================================
    # TIER 3: Fuzzy Name Match
    # ==========================================================================
    print_dual("\n  Tier 3: Fuzzy Name Match (threshold=92)...")
    
    if not FUZZ_AVAILABLE:
        print_dual("    WARNING: rapidfuzz not available, skipping")
    else:
        unmatched_mask = unique_df['gvkey'].isna()
        has_name = unique_df['company_name'].notna()
        tier3_candidates = unique_df[unmatched_mask & has_name].copy()
        
        print_dual(f"    Candidates: {len(tier3_candidates):,} unmatched companies with name")
        
        if len(tier3_candidates) > 0:
            tier3_candidates['company_name_norm'] = tier3_candidates['company_name'].apply(normalize_company_name)
            tier3_candidates = tier3_candidates[tier3_candidates['company_name_norm'] != '']
            
            ccm_names = ccm[['conm', 'gvkey', 'sic']].copy()
            ccm_names['conm_norm'] = ccm_names['conm'].apply(normalize_company_name)
            ccm_names = ccm_names[ccm_names['conm_norm'] != ''].drop_duplicates('conm_norm')
            
            choices = {row['conm_norm']: {'gvkey': row['gvkey'], 'conm': row['conm'], 'sic': row['sic']} 
                       for _, row in ccm_names.iterrows()}
            choice_list = list(choices.keys())
            
            print_dual(f"    Matching {len(tier3_candidates):,} names against {len(ccm_names):,} CCM names...")
            
            matched_records = []
            total = len(tier3_candidates)
            progress_interval = max(500, total // 20)
            
            for i, (idx, row) in enumerate(tier3_candidates.iterrows(), 1):
                query_name = row['company_name_norm']
                
                result = process.extractOne(query_name, choice_list, scorer=fuzz.token_sort_ratio, score_cutoff=92)
                
                if result is not None:
                    best_match, best_score, _ = result
                    ccm_data = choices[best_match]
                    matched_records.append({
                        'company_id': row['company_id'],
                        'gvkey': ccm_data['gvkey'],
                        'conm': ccm_data['conm'],
                        'sic': ccm_data['sic'],
                        'fuzzy_score': float(best_score)
                    })
                
                if i % progress_interval == 0 or i == total:
                    print_dual(f"      Progress: {i:,}/{total:,} ({i/total*100:.1f}%) - Matched: {len(matched_records):,}")
            
            print_dual(f"    Matched: {len(matched_records):,} companies")
            
            if len(matched_records) > 0:
                update_df = pd.DataFrame(matched_records)
                update_df['link_method'] = 'name_fuzzy'
                update_df['link_quality'] = 80
                
                unique_df = unique_df.set_index('company_id')
                update_df = update_df.set_index('company_id')
                
                unique_df.loc[update_df.index, 'gvkey'] = update_df['gvkey']
                unique_df.loc[update_df.index, 'conm'] = update_df['conm']
                unique_df.loc[update_df.index, 'sic'] = update_df['sic']
                unique_df.loc[update_df.index, 'link_method'] = update_df['link_method']
                unique_df.loc[update_df.index, 'link_quality'] = update_df['link_quality']
                
                unique_df = unique_df.reset_index()
    
    tier3_matched = unique_df['gvkey'].notna().sum()
    print_dual(f"    [CHECK] Total matched after Tier 3: {tier3_matched:,}")
    
    # ==========================================================================
    # BROADCAST RESULTS back to full dataset
    # ==========================================================================
    print_dual("\n" + "="*60)
    print_dual("Broadcasting results to all calls...")
    
    # Create lookup from company_id to CCM data
    matched_companies = unique_df[unique_df['gvkey'].notna()][['company_id', 'gvkey', 'conm', 'sic', 'link_method', 'link_quality']].copy()
    
    print_dual(f"  Matched companies: {len(matched_companies):,}")
    print_dual(f"  Total calls to update: {sum(len(dedup_index[cid]) for cid in matched_companies['company_id']):,}")
    
    # Initialize columns in original df
    df['gvkey'] = np.nan
    df['conm'] = np.nan
    df['sic'] = np.nan
    df['link_method'] = np.nan
    df['link_quality'] = np.nan
    
    for col in ['gvkey', 'conm', 'sic', 'link_method']:
        df[col] = df[col].astype('object')
    
    # Broadcast via merge (most efficient)
    df = df.merge(
        matched_companies,
        on='company_id',
        how='left',
        suffixes=('_old', '')
    )
    
    # Clean up old columns if they exist
    for col in ['gvkey', 'conm', 'sic', 'link_method', 'link_quality']:
        if f'{col}_old' in df.columns:
            df = df.drop(columns=[f'{col}_old'])
    
    total_matched_calls = df['gvkey'].notna().sum()
    print_dual(f"  Total calls with GVKEY: {total_matched_calls:,} ({total_matched_calls/total_calls*100:.1f}%)")
    
    # ==========================================================================
    # Filter unmatched and add FF industries
    # ==========================================================================
    print_dual(f"\nFiltering calls without GVKEY...")
    df_linked = df[df['gvkey'].notna()].copy()
    removed = len(df) - len(df_linked)
    print_dual(f"  Removed {removed:,} unmatched calls")
    print_dual(f"  Final count: {len(df_linked):,} calls")
    
    # Parse FF industries
    print_dual("\nMapping SIC codes to FF industries...")
    ff12_map = parse_ff_industries(paths['ff12'], 12)
    ff48_map = parse_ff_industries(paths['ff48'], 48)
    
    df_linked['sic_int'] = pd.to_numeric(df_linked['sic'], errors='coerce').astype('Int64')
    
    df_linked['ff12_code'] = df_linked['sic_int'].map(lambda x: ff12_map.get(x, (None, None))[0] if pd.notna(x) else None)
    df_linked['ff12_name'] = df_linked['sic_int'].map(lambda x: ff12_map.get(x, (None, None))[1] if pd.notna(x) else None)
    df_linked['ff48_code'] = df_linked['sic_int'].map(lambda x: ff48_map.get(x, (None, None))[0] if pd.notna(x) else None)
    df_linked['ff48_name'] = df_linked['sic_int'].map(lambda x: ff48_map.get(x, (None, None))[1] if pd.notna(x) else None)
    
    ff12_matched = df_linked['ff12_code'].notna().sum()
    ff48_matched = df_linked['ff48_code'].notna().sum()
    print_dual(f"  FF12 matched: {ff12_matched:,} ({ff12_matched/len(df_linked)*100:.1f}%)")
    print_dual(f"  FF48 matched: {ff48_matched:,} ({ff48_matched/len(df_linked)*100:.1f}%)")
    
    # Save output
    output_file = paths['output_dir'] / 'metadata_linked.parquet'
    df_linked.to_parquet(output_file, index=False)
    print_dual(f"\nSaved linked metadata: {output_file}")
    
    # Generate enhanced variable reference
    var_ref_file = paths['output_dir'] / 'variable_reference.csv'
    generate_variable_reference(df_linked, var_ref_file, print_dual)
    
    # Update latest symlink
    update_latest_symlink(paths['latest_dir'], paths['output_dir'], print_dual)
    
    print_dual("\n" + "="*80)
    print_dual("Step 1.2 completed successfully.")
    print_dual("="*80)
    
    sys.stdout = dual_writer.terminal
    dual_writer.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
