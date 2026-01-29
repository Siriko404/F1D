#!/usr/bin/env python3
"""
==============================================================================
STEP 2.5: Link Multi-Measure F1D Panel to CCM and Fama-French Industries
==============================================================================
ID: 2.5_LinkCcmAndIndustries
Description: Merges 4 measure panels into single wide-format dataset, then enriches
             with Compustat identifiers (gvkey) and Fama-French industry
             classifications (FF12, FF48) using multi-tier CCM linking strategy.
Inputs:
    - config/project.yaml
    - 4_Outputs/2.4_BuildF1dPanel/latest/MaQaUnc_panel_YYYY.parquet (17 files)
    - 4_Outputs/2.4_BuildF1dPanel/latest/MaPresUnc_panel_YYYY.parquet (17 files)
    - 4_Outputs/2.4_BuildF1dPanel/latest/AnaQaUnc_panel_YYYY.parquet (17 files)
    - 4_Outputs/2.4_BuildF1dPanel/latest/EntireCallNeg_panel_YYYY.parquet (17 files)
    - 1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet
    - 1_Inputs/Siccodes12.zip
    - 1_Inputs/Siccodes48.zip
Outputs:
    - 4_Outputs/2.5_LinkCcmAndIndustries/TIMESTAMP/f1d_enriched_YYYY.parquet (17 files)
      (merged panel with all 4 measures + CCM/FF data)
    - 4_Outputs/2.5_LinkCcmAndIndustries/TIMESTAMP/report_step_2_5.md
    - 4_Outputs/2.5_LinkCcmAndIndustries/TIMESTAMP/fuzzy_matches_review.csv
    - 4_Outputs/2.5_LinkCcmAndIndustries/TIMESTAMP/unmatched_calls_audit.csv
    - 4_Outputs/2.5_LinkCcmAndIndustries/latest/ (symlink)
    - 3_Logs/2.5_LinkCcmAndIndustries/TIMESTAMP.log
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
import hashlib
import re
import zipfile
from collections import defaultdict
import psutil

# Try to import rapidfuzz, fall back to difflib if not available
try:
    from rapidfuzz import fuzz, process as rapidfuzz_process
    FUZZ_AVAILABLE = True
except ImportError:
    import difflib
    FUZZ_AVAILABLE = False
    print("Warning: rapidfuzz not available, using difflib for fuzzy matching (slower)")

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
        'measure_panel_dir': root / '4_Outputs' / '2.4_BuildF1dPanel' / 'latest',
        'ccm_file': root / '1_Inputs' / 'CRSPCompustat_CCM' / 'CRSPCompustat_CCM.parquet',
        'ff12_file': root / '1_Inputs' / 'Siccodes12.zip',
        'ff48_file': root / '1_Inputs' / 'Siccodes48.zip',
    }

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config['paths']['outputs'] / "2.5_LinkCcmAndIndustries"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)

    paths['latest_dir'] = output_base / "latest"

    # Create log directory
    log_base = root / config['paths']['logs'] / "2.5_LinkCcmAndIndustries"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}.log"

    return paths, timestamp

# ==============================================================================
# Utility functions
# ==============================================================================

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of file"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()

def normalize_company_name(name):
    """Normalize company name for fuzzy matching"""
    if pd.isna(name):
        return ""

    # Uppercase and remove punctuation
    name = str(name).upper().strip()
    name = re.sub(r'[^\w\s]', ' ', name)

    # Remove common suffixes
    suffixes = ['INC', 'CORP', 'LTD', 'LLC', 'CO', 'COMPANY',
                'CORPORATION', 'INCORPORATED', 'LIMITED', 'PLC', 'SA', 'NV']
    for suffix in suffixes:
        name = re.sub(rf'\b{suffix}\b', '', name)

    # Remove extra whitespace
    name = ' '.join(name.split())
    return name

# ==============================================================================
# Merge multi-measure panels
# ==============================================================================

def merge_measure_panels(measure_panel_dir, year, config):
    """
    Merge all 4 measure panels into single wide-format panel.

    Each measure contributes its specific metrics columns with prefixes.
    FULL OUTER JOIN on file_name since not all calls have all measures.
    """
    print_dual(f"  Loading and merging 4 measure panels...")

    measures = config['step_04']['measures']

    # Load each measure panel
    panels = {}
    for measure_key, measure_config in measures.items():
        panel_file = measure_panel_dir / f"{measure_key}_panel_{year}.parquet"

        if not panel_file.exists():
            print_dual(f"    WARNING: Missing {panel_file.name}")
            continue

        df = pd.read_parquet(panel_file)
        print_dual(f"    {measure_key}: {len(df):,} calls")
        panels[measure_key] = df

    if not panels:
        raise FileNotFoundError(f"No measure panels found for year {year}")

    # Start with first measure panel as base (keep metadata columns)
    first_measure = list(panels.keys())[0]
    merged = panels[first_measure][['file_name', 'start_date', 'business_quarter',
                                      'permno', 'company_name', 'company_id', 'cusip',
                                      'sedol', 'isin', 'company_ticker',
                                      'process_version', 'had_duplicate_metadata']].copy()

    # Add measure-specific columns for each panel
    for measure_key, df in panels.items():
        dict_name = measures[measure_key]['dictionary']
        dataset_name = measures[measure_key]['dataset']

        # Create measure-specific column names
        # Format: MaQaUnc_hits, MaQaUnc_pct, total_tokens_ma_qa
        df_subset = df[['file_name', 'total_word_tokens', f'{dict_name}_hits', f'{dict_name}_pct']].copy()

        # Rename columns with measure prefix
        df_subset = df_subset.rename(columns={
            'total_word_tokens': f'total_tokens_{measure_key.lower()}',
            f'{dict_name}_hits': f'{measure_key}_hits',
            f'{dict_name}_pct': f'{measure_key}_pct'
        })

        # FULL OUTER JOIN
        merged = merged.merge(df_subset, on='file_name', how='outer')

    # Sort by file_name for determinism
    merged = merged.sort_values('file_name').reset_index(drop=True)

    print_dual(f"  Merged panel: {len(merged):,} unique calls")
    print_dual(f"    Columns: {len(merged.columns)}")

    return merged

# ==============================================================================
# CCM and FF Industry data loading
# ==============================================================================

def load_and_prepare_ccm(ccm_path):
    """Load CCM dataset and prepare for linking"""
    print_dual(f"  Loading CCM from {ccm_path}")
    ccm = pd.read_parquet(ccm_path)
    print_dual(f"  Loaded {len(ccm):,} CCM link records")

    # Convert date fields
    ccm['LINKDT'] = pd.to_datetime(ccm['LINKDT'])
    ccm['LINKENDDT_clean'] = ccm['LINKENDDT'].replace('E', '2099-12-31')
    ccm['LINKENDDT_dt'] = pd.to_datetime(ccm['LINKENDDT_clean'])

    # Create cusip8 for matching
    ccm['cusip8'] = ccm['cusip'].astype(str).str[:8]

    # Normalize company names for fuzzy matching
    ccm['conm_normalized'] = ccm['conm'].apply(normalize_company_name)

    print_dual(f"  CCM temporal range: {ccm['LINKDT'].min()} to {ccm['LINKENDDT_dt'].max()}")

    return ccm

def parse_ff_industries(zip_path, num_industries):
    """Parse Fama-French industry classification from SIC code ranges"""
    print_dual(f"  Parsing FF{num_industries} from {zip_path}")

    # Extract text file from zip
    with zipfile.ZipFile(zip_path, 'r') as z:
        txt_file = z.namelist()[0]
        with z.open(txt_file) as f:
            content = f.read().decode('utf-8')

    # Parse SIC ranges and industry mappings
    industry_map = {}
    lines = content.strip().split('\n')

    current_industry_code = None
    current_industry_name = None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        # Check if line starts with a number (new industry definition)
        parts = stripped.split(maxsplit=2)
        if len(parts) >= 2 and parts[0].isdigit():
            current_industry_code = int(parts[0])
            current_industry_name = parts[1]
        elif stripped and current_industry_code is not None:
            # This is a SIC range line (format: XXXX-YYYY or XXXX-YYYY description)
            # Extract just the range part (first token)
            sic_range = stripped.split()[0] if stripped.split() else ""
            if '-' in sic_range:
                try:
                    start, end = sic_range.split('-')
                    for sic in range(int(start), int(end) + 1):
                        industry_map[sic] = (current_industry_code, current_industry_name)
                except ValueError:
                    # Skip malformed ranges
                    continue

    print_dual(f"  Mapped {len(industry_map)} SIC codes to {num_industries} industries")
    return industry_map

# ==============================================================================
# Multi-tier linking strategy
# ==============================================================================

class LinkingStatsTracker:
    """Track linking statistics across all tiers"""
    def __init__(self):
        self.stats = defaultdict(int)
        self.tier_counts = {
            'tier1_permno_date': 0,
            'tier2_cusip_date': 0,
            'tier3_fuzzy_name': 0,
            'tier4_ticker_date': 0,
            'tier5_no_match': 0
        }

    def update(self, tier, count):
        self.tier_counts[tier] += count
        self.stats['total_processed'] += count

    def get_match_rate(self):
        matched = sum(self.tier_counts[k] for k in self.tier_counts if k != 'tier5_no_match')
        total = self.stats['total_processed']
        return (matched / total * 100) if total > 0 else 0

def link_tier1_permno_date(f1d, ccm, call_date_col='start_date'):
    """
    Tier 1: PERMNO + Date Range Matching (PRIMARY)
    Quality Score: 100
    """
    print_dual("  Tier 1: PERMNO + Date range matching...")

    # Filter calls with valid permno (not null and not empty string)
    has_permno = f1d['permno'].notna() & (f1d['permno'] != '')
    f1d_with_permno = f1d[has_permno].copy()

    if len(f1d_with_permno) == 0:
        print_dual("    No calls with PERMNO, skipping")
        return 0

    # Convert permno to int for matching
    f1d_with_permno['permno_int'] = pd.to_numeric(f1d_with_permno['permno'], errors='coerce').astype('Int64')

    # Safety: filter out failed conversions
    f1d_with_permno = f1d_with_permno[f1d_with_permno['permno_int'].notna()]

    if len(f1d_with_permno) == 0:
        print_dual("    No calls with valid numeric PERMNO, skipping")
        return 0

    print_dual(f"    Valid PERMNO identifiers: {len(f1d_with_permno):,}")

    # Convert call start_date to datetime
    f1d_with_permno['start_date_dt'] = pd.to_datetime(f1d_with_permno[call_date_col])

    # Merge with CCM on LPERMNO (use suffixes to avoid column conflicts)
    merged = f1d_with_permno.merge(
        ccm[['LPERMNO', 'gvkey', 'conm', 'sic', 'cusip', 'LINKPRIM', 'LINKTYPE',
             'LINKDT', 'LINKENDDT', 'LINKENDDT_dt']],
        left_on='permno_int',
        right_on='LPERMNO',
        how='left',
        suffixes=('', '_ccm')
    )

    # Apply temporal filter
    valid_link = (
        (merged['start_date_dt'] >= merged['LINKDT']) &
        (merged['start_date_dt'] <= merged['LINKENDDT_dt'])
    )
    merged = merged[valid_link]

    # Prioritize by LINKPRIM (P > C > J > N), then LINKTYPE (LC > LU)
    linkprim_priority = {'P': 1, 'C': 2, 'J': 3, 'N': 4}
    linktype_priority = {'LC': 1, 'LU': 2}

    merged['linkprim_rank'] = merged['LINKPRIM'].map(linkprim_priority).fillna(99)
    merged['linktype_rank'] = merged['LINKTYPE'].map(linktype_priority).fillna(99)

    # Sort and keep best link per file_name
    merged = merged.sort_values(['file_name', 'linkprim_rank', 'linktype_rank'])
    merged = merged.drop_duplicates(subset=['file_name'], keep='first')

    # Filter to only rows with valid gvkey_ccm
    gvkey_col = 'gvkey_ccm' if 'gvkey_ccm' in merged.columns else 'gvkey'
    if gvkey_col in merged.columns:
        merged = merged[merged[gvkey_col].notna()]
        # Rename back to gvkey for consistency
        if gvkey_col == 'gvkey_ccm':
            merged = merged.rename(columns={'gvkey_ccm': 'gvkey', 'cusip_ccm': 'cusip'})
    else:
        # No matches at all
        merged = merged.iloc[0:0]  # Empty dataframe

    # Update main dataframe using mask-based approach (FAST)
    matched_count = 0
    if len(merged) > 0:
        # Create mask for matched file_names
        matched_files = set(merged['file_name'].unique())
        mask = f1d['file_name'].isin(matched_files)

        # Prepare update data
        update_df = merged[['file_name', 'LPERMNO', 'gvkey', 'conm', 'sic', 'cusip', 'LINKPRIM', 'LINKTYPE']].copy()
        # Ensure no duplicate columns
        update_df = update_df.loc[:, ~update_df.columns.duplicated()]

        update_df.rename(columns={
            'conm': 'ccm_conm',
            'sic': 'ccm_sic',
            'cusip': 'ccm_cusip',
            'LINKPRIM': 'ccm_linkprim',
            'LINKTYPE': 'ccm_linktype'
        }, inplace=True)
        update_df['link_method'] = 'permno_date'
        update_df['link_quality_score'] = 100

        # Create dict mapping for fast lookup
        update_dict = update_df.set_index('file_name').to_dict('index')

        # Update using vectorized operations
        for col in ['LPERMNO', 'gvkey', 'ccm_conm', 'ccm_sic', 'ccm_cusip', 'ccm_linkprim', 'ccm_linktype', 'link_method', 'link_quality_score']:
            # Ensure target column has compatible dtype
            if col not in f1d.columns:
                f1d[col] = pd.Series(dtype='object')
            
            if f1d[col].dtype != 'object':
                f1d[col] = f1d[col].astype('object')

            f1d.loc[mask, col] = f1d.loc[mask, 'file_name'].map(lambda fn: update_dict[fn][col])

        matched_count = len(merged)

    print_dual(f"    Matched: {matched_count:,} calls ({matched_count/len(f1d)*100:.1f}%)")
    return matched_count

def link_tier2_cusip_date(f1d, ccm, call_date_col='start_date'):
    """
    Tier 2: CUSIP8 + Date Range Matching (SECONDARY)
    Quality Score: 90
    """
    print_dual("  Tier 2: CUSIP8 + Date range matching...")

    # Filter calls not yet matched and have valid cusip (not null and not empty)
    unmatched = f1d['gvkey'].isna()
    has_cusip = f1d['cusip'].notna() & (f1d['cusip'] != '')
    f1d_with_cusip = f1d[unmatched & has_cusip].copy()

    if len(f1d_with_cusip) == 0:
        print_dual("    No unmatched calls with CUSIP, skipping")
        return 0

    print_dual(f"    Valid CUSIP identifiers: {len(f1d_with_cusip):,}")

    # Create cusip8
    f1d_with_cusip['cusip8'] = f1d_with_cusip['cusip'].astype(str).str[:8]
    f1d_with_cusip['start_date_dt'] = pd.to_datetime(f1d_with_cusip[call_date_col])

    # Merge with CCM on cusip8 (use suffixes to avoid column conflicts)
    merged = f1d_with_cusip.merge(
        ccm[['LPERMNO', 'cusip8', 'gvkey', 'conm', 'sic', 'cusip', 'LINKPRIM', 'LINKTYPE',
             'LINKDT', 'LINKENDDT_dt']],
        on='cusip8',
        how='left',
        suffixes=('', '_ccm')
    )

    # Apply temporal filter
    valid_link = (
        (merged['start_date_dt'] >= merged['LINKDT']) &
        (merged['start_date_dt'] <= merged['LINKENDDT_dt'])
    )
    merged = merged[valid_link]

    # Prioritize as in Tier 1
    linkprim_priority = {'P': 1, 'C': 2, 'J': 3, 'N': 4}
    linktype_priority = {'LC': 1, 'LU': 2}

    merged['linkprim_rank'] = merged['LINKPRIM'].map(linkprim_priority).fillna(99)
    merged['linktype_rank'] = merged['LINKTYPE'].map(linktype_priority).fillna(99)

    merged = merged.sort_values(['file_name', 'linkprim_rank', 'linktype_rank'])
    merged = merged.drop_duplicates(subset=['file_name'], keep='first')

    # Filter to only rows with valid gvkey_ccm
    # Note: gvkey column from CCM will be named 'gvkey_ccm' due to suffix
    gvkey_col = 'gvkey_ccm' if 'gvkey_ccm' in merged.columns else 'gvkey'
    if gvkey_col in merged.columns:
        merged = merged[merged[gvkey_col].notna()]
        # Rename back to gvkey for consistency
        if gvkey_col == 'gvkey_ccm':
            merged = merged.rename(columns={'gvkey_ccm': 'gvkey', 'cusip_ccm': 'cusip'})
    else:
        merged = merged.iloc[0:0]  # Empty dataframe

    # Update main dataframe using mask-based approach (FAST)
    matched_count = 0
    if len(merged) > 0:
        # Create mask for matched file_names
        matched_files = set(merged['file_name'].unique())
        mask = f1d['file_name'].isin(matched_files)

        # Prepare update data
        update_df = merged[['file_name', 'LPERMNO', 'gvkey', 'conm', 'sic', 'cusip', 'LINKPRIM', 'LINKTYPE']].copy()
        # Ensure no duplicate columns
        update_df = update_df.loc[:, ~update_df.columns.duplicated()]

        update_df.rename(columns={
            'conm': 'ccm_conm',
            'sic': 'ccm_sic',
            'cusip': 'ccm_cusip',
            'LINKPRIM': 'ccm_linkprim',
            'LINKTYPE': 'ccm_linktype'
        }, inplace=True)
        update_df['link_method'] = 'cusip8_date'
        update_df['link_quality_score'] = 90

        # Create dict mapping for fast lookup
        update_dict = update_df.set_index('file_name').to_dict('index')

        # Update using vectorized operations
        for col in ['LPERMNO', 'gvkey', 'ccm_conm', 'ccm_sic', 'ccm_cusip', 'ccm_linkprim', 'ccm_linktype', 'link_method', 'link_quality_score']:
             # Ensure target column has compatible dtype
            if col not in f1d.columns:
                f1d[col] = pd.Series(dtype='object')
            
            if f1d[col].dtype != 'object':
                f1d[col] = f1d[col].astype('object')

            f1d.loc[mask, col] = f1d.loc[mask, 'file_name'].map(lambda fn: update_dict[fn][col])

        matched_count = len(merged)

    print_dual(f"    Matched: {matched_count:,} calls ({matched_count/len(f1d)*100:.1f}%)")
    return matched_count

def calculate_safe_chunk_size(n_queries, n_targets, max_memory_pct=85):
    """
    Calculate safe chunk size based on available system memory.

    Args:
        n_queries: Number of queries to match
        n_targets: Number of targets (CCM names)
        max_memory_pct: Maximum system memory usage percentage (default 85%)

    Returns:
        Optimal chunk size
    """
    mem = psutil.virtual_memory()
    current_usage_pct = mem.percent

    # Available memory margin before hitting cap
    available_margin_pct = max_memory_pct - current_usage_pct

    if available_margin_pct <= 5:
        print_dual(f"    WARNING: System memory at {current_usage_pct:.1f}%, limited headroom")
        return 100  # Minimal chunk size

    # Calculate available bytes (90% of margin for safety)
    available_bytes = mem.total * (available_margin_pct / 100) * 0.9

    # Each similarity score is 4 bytes (float32)
    bytes_per_chunk_row = n_targets * 4

    # How many rows can fit?
    safe_chunk_size = int(available_bytes / bytes_per_chunk_row)

    # Bounds: min 100, max 5000
    safe_chunk_size = max(100, min(5000, safe_chunk_size))

    print_dual(f"    Memory: {current_usage_pct:.1f}% used, {available_margin_pct:.1f}% margin -> chunk_size={safe_chunk_size:,}")

    return safe_chunk_size

def link_tier3_fuzzy_name(f1d, ccm, threshold=85):
    """
    Tier 3: Fuzzy Company Name Matching (VECTORIZED with Memory Cap)
    Quality Score: 70-80 depending on match score
    Uses chunked vectorization with dynamic memory monitoring.
    """
    print_dual("  Tier 3: Fuzzy name matching (vectorized)...")

    # Filter unmatched calls with company_name
    unmatched = f1d['gvkey'].isna()
    has_name = f1d['company_name'].notna()
    f1d_with_name = f1d[unmatched & has_name].copy()

    if len(f1d_with_name) == 0:
        print_dual("    No unmatched calls with company name, skipping")
        return 0, []

    # Normalize names
    f1d_with_name['company_name_normalized'] = f1d_with_name['company_name'].apply(normalize_company_name)

    # Filter out empty names
    f1d_with_name = f1d_with_name[f1d_with_name['company_name_normalized'] != ''].copy()

    if len(f1d_with_name) == 0:
        print_dual("    No valid normalized names, skipping")
        return 0, []

    # Get unique CCM names
    ccm_names = ccm[['LPERMNO', 'conm_normalized', 'gvkey', 'conm', 'sic', 'cusip']].drop_duplicates('conm_normalized')
    ccm_names = ccm_names[ccm_names['conm_normalized'] != ''].reset_index(drop=True)

    n_queries = len(f1d_with_name)
    n_targets = len(ccm_names)

    print_dual(f"    Matching {n_queries:,} calls against {n_targets:,} CCM names")

    fuzzy_review_list = []
    matched_count = 0

    if not FUZZ_AVAILABLE:
        print_dual("    WARNING: rapidfuzz not available, falling back to slow sequential mode")
        # Fall back to old sequential method if rapidfuzz unavailable
        return _link_tier3_fuzzy_fallback(f1d, f1d_with_name, ccm_names, threshold)

    # Calculate safe chunk size
    chunk_size = calculate_safe_chunk_size(n_queries, n_targets, max_memory_pct=85)

    # Prepare data
    query_names = f1d_with_name['company_name_normalized'].tolist()
    target_names = ccm_names['conm_normalized'].tolist()
    file_names = f1d_with_name['file_name'].tolist()

    # Ensure columns exist and are object type (done ONCE)
    for col in ['gvkey', 'ccm_conm', 'ccm_sic', 'ccm_cusip', 'link_method', 'fuzzy_matched_name', 'fuzzy_needs_review']:
        if col not in f1d.columns:
            f1d[col] = pd.Series(dtype='object')
        if f1d[col].dtype != 'object':
            f1d[col] = f1d[col].astype('object')

    # Process in chunks
    for chunk_start in range(0, n_queries, chunk_size):
        chunk_end = min(chunk_start + chunk_size, n_queries)
        chunk_queries = query_names[chunk_start:chunk_end]
        chunk_files = file_names[chunk_start:chunk_end]

        print_dual(f"    Processing chunk {chunk_start+1:,}-{chunk_end:,} of {n_queries:,}...")

        # Vectorized similarity matrix for this chunk
        # Returns: (chunk_size, n_targets) matrix of scores
        scores = rapidfuzz_process.cdist(
            chunk_queries,
            target_names,
            scorer=fuzz.token_sort_ratio,
            dtype=np.float32,  # Use float32 instead of float64 (half memory)
            workers=-1  # Use all CPU cores
        )

        # Find best match for each query in chunk
        for i, (query_name, file_name) in enumerate(zip(chunk_queries, chunk_files)):
            best_score_idx = np.argmax(scores[i])
            best_score = scores[i][best_score_idx]

            if best_score < threshold:
                continue

            # Get CCM data
            ccm_data = ccm_names.iloc[best_score_idx]

            # Update f1d
            f1d_idx = f1d[f1d['file_name'] == file_name].index[0]
            
            # (Column initialization moved outside loop)

            f1d.loc[f1d_idx, 'LPERMNO'] = ccm_data['LPERMNO']
            f1d.loc[f1d_idx, 'gvkey'] = ccm_data['gvkey']
            f1d.loc[f1d_idx, 'ccm_conm'] = ccm_data['conm']
            f1d.loc[f1d_idx, 'ccm_sic'] = ccm_data['sic']
            f1d.loc[f1d_idx, 'ccm_cusip'] = ccm_data['cusip']
            f1d.loc[f1d_idx, 'link_method'] = 'name_fuzzy'
            f1d.loc[f1d_idx, 'fuzzy_match_score'] = float(best_score)
            f1d.loc[f1d_idx, 'fuzzy_matched_name'] = ccm_data['conm']

            # Quality score based on match score
            if best_score >= 90:
                f1d.loc[f1d_idx, 'link_quality_score'] = 80
                f1d.loc[f1d_idx, 'fuzzy_needs_review'] = False
            else:
                f1d.loc[f1d_idx, 'link_quality_score'] = 70
                f1d.loc[f1d_idx, 'fuzzy_needs_review'] = True

                # Add to review list
                row_data = f1d_with_name[f1d_with_name['file_name'] == file_name].iloc[0]
                fuzzy_review_list.append({
                    'file_name': file_name,
                    'f1d_company_name': row_data['company_name'],
                    'ccm_matched_name': ccm_data['conm'],
                    'fuzzy_score': float(best_score),
                    'gvkey': ccm_data['gvkey'],
                    'start_date': row_data['start_date']
                })

            matched_count += 1

    print_dual(f"    Matched: {matched_count:,} calls ({matched_count/len(f1d)*100:.1f}%)")
    print_dual(f"    Needs review: {len(fuzzy_review_list):,} matches")
    return matched_count, fuzzy_review_list

def _link_tier3_fuzzy_fallback(f1d, f1d_with_name, ccm_names, threshold):
    """Fallback sequential fuzzy matching when rapidfuzz unavailable"""
    import difflib

    fuzzy_review_list = []
    matched_count = 0

    # Ensure columns exist and are object type (done ONCE)
    for col in ['LPERMNO', 'gvkey', 'ccm_conm', 'ccm_sic', 'ccm_cusip', 'link_method', 'fuzzy_matched_name', 'fuzzy_needs_review']:
        if col not in f1d.columns:
            f1d[col] = pd.Series(dtype='object')
        if f1d[col].dtype != 'object':
            f1d[col] = f1d[col].astype('object')

    for idx, row in f1d_with_name.iterrows():
        f1d_name = row['company_name_normalized']
        if not f1d_name:
            continue

        matches = difflib.get_close_matches(f1d_name, ccm_names['conm_normalized'].tolist(), n=1, cutoff=threshold/100.0)
        if not matches:
            continue

            f1d.loc[f1d_idx, 'link_quality_score'] = 70
            f1d.loc[f1d_idx, 'fuzzy_needs_review'] = True
            fuzzy_review_list.append({
                'file_name': row['file_name'],
                'f1d_company_name': row['company_name'],
                'ccm_matched_name': ccm_data['conm'],
                'fuzzy_score': score,
                'gvkey': ccm_data['gvkey'],
                'start_date': row['start_date']
            })

        matched_count += 1

    return matched_count, fuzzy_review_list

def link_tier4_ticker_date(f1d, ccm, call_date_col='start_date'):
    """
    Tier 4: Ticker Symbol + Date (FALLBACK)
    Quality Score: 60
    """
    print_dual("  Tier 4: Ticker + Date matching...")

    # Filter unmatched calls with ticker
    unmatched = f1d['gvkey'].isna()
    has_ticker = f1d['company_ticker'].notna()
    f1d_with_ticker = f1d[unmatched & has_ticker].copy()

    if len(f1d_with_ticker) == 0:
        print_dual("    No unmatched calls with ticker, skipping")
        return 0

    f1d_with_ticker['start_date_dt'] = pd.to_datetime(f1d_with_ticker[call_date_col])

    # Merge with CCM on ticker (use suffixes to avoid column conflicts)
    merged = f1d_with_ticker.merge(
        ccm[['LPERMNO', 'tic', 'gvkey', 'conm', 'sic', 'cusip', 'LINKPRIM', 'LINKTYPE',
             'LINKDT', 'LINKENDDT_dt']],
        left_on='company_ticker',
        right_on='tic',
        how='left',
        suffixes=('', '_ccm')
    )

    # Apply temporal filter
    valid_link = (
        (merged['start_date_dt'] >= merged['LINKDT']) &
        (merged['start_date_dt'] <= merged['LINKENDDT_dt'])
    )
    merged = merged[valid_link]

    # Prioritize
    linkprim_priority = {'P': 1, 'C': 2, 'J': 3, 'N': 4}
    linktype_priority = {'LC': 1, 'LU': 2}

    merged['linkprim_rank'] = merged['LINKPRIM'].map(linkprim_priority).fillna(99)
    merged['linktype_rank'] = merged['LINKTYPE'].map(linktype_priority).fillna(99)

    merged = merged.sort_values(['file_name', 'linkprim_rank', 'linktype_rank'])
    merged = merged.drop_duplicates(subset=['file_name'], keep='first')

    # Filter to only rows with valid gvkey_ccm
    gvkey_col = 'gvkey_ccm' if 'gvkey_ccm' in merged.columns else 'gvkey'
    if gvkey_col in merged.columns:
        merged = merged[merged[gvkey_col].notna()]
        # Rename back to gvkey for consistency
        if gvkey_col == 'gvkey_ccm':
            merged = merged.rename(columns={'gvkey_ccm': 'gvkey', 'cusip_ccm': 'cusip'})
    else:
        merged = merged.iloc[0:0]  # Empty dataframe

    # Update main dataframe using mask-based approach (FAST)
    matched_count = 0
    if len(merged) > 0:
        # Create mask for matched file_names
        matched_files = set(merged['file_name'].unique())
        mask = f1d['file_name'].isin(matched_files)

        # Prepare update data
        update_df = merged[['file_name', 'LPERMNO', 'gvkey', 'conm', 'sic', 'cusip', 'LINKPRIM', 'LINKTYPE']].copy()
        # Ensure no duplicate columns
        update_df = update_df.loc[:, ~update_df.columns.duplicated()]

        update_df.rename(columns={
            'conm': 'ccm_conm',
            'sic': 'ccm_sic',
            'cusip': 'ccm_cusip',
            'LINKPRIM': 'ccm_linkprim',
            'LINKTYPE': 'ccm_linktype'
        }, inplace=True)
        update_df['link_method'] = 'ticker_date'
        update_df['link_quality_score'] = 60

        # Create dict mapping for fast lookup
        update_dict = update_df.set_index('file_name').to_dict('index')

        # Update using vectorized operations
        for col in ['LPERMNO', 'gvkey', 'ccm_conm', 'ccm_sic', 'ccm_cusip', 'ccm_linkprim', 'ccm_linktype', 'link_method', 'link_quality_score']:
            # Ensure target column has compatible dtype
            if col not in f1d.columns:
                f1d[col] = pd.Series(dtype='object')
            
            if f1d[col].dtype != 'object':
                f1d[col] = f1d[col].astype('object')

            f1d.loc[mask, col] = f1d.loc[mask, 'file_name'].map(lambda fn: update_dict[fn][col])

        matched_count = len(merged)

    print_dual(f"    Matched: {matched_count:,} calls ({matched_count/len(f1d)*100:.1f}%)")
    return matched_count

def mark_unmatched_calls(f1d):
    """Tier 5: Mark unmatched calls and categorize reasons"""
    unmatched = f1d[f1d['gvkey'].isna()].copy()

    unmatched_audit = []
    for idx, row in unmatched.iterrows():
        # Categorize reason
        if pd.isna(row['permno']) and pd.isna(row['cusip']) and pd.isna(row['company_name']):
            reason = 'missing_all_identifiers'
        elif pd.notna(row['permno']):
            reason = 'permno_no_ccm_match'
        elif pd.notna(row['cusip']):
            reason = 'cusip_no_ccm_match'
        else:
            reason = 'name_no_fuzzy_match'

        unmatched_audit.append({
            'file_name': row['file_name'],
            'start_date': row['start_date'],
            'company_name': row['company_name'],
            'permno': row['permno'],
            'cusip': row['cusip'],
            'reason': reason
        })

        # Mark in dataframe
        f1d.loc[idx, 'link_method'] = 'no_match'
        f1d.loc[idx, 'link_quality_score'] = 0

    print_dual(f"  Tier 5: {len(unmatched):,} calls remain unmatched ({len(unmatched)/len(f1d)*100:.1f}%)")
    return unmatched_audit

# ==============================================================================
# Fama-French industry mapping
# ==============================================================================

def map_fama_french_industries(f1d, ff12_map, ff48_map):
    """Map SIC codes to FF12 and FF48 industries"""
    print_dual("  Mapping Fama-French industries...")

    def map_sic(sic, ff_map, default_code, default_name):
        if pd.isna(sic):
            return default_code, default_name
        try:
            sic_int = int(sic)
            if sic_int in ff_map:
                return ff_map[sic_int]
            return default_code, default_name
        except:
            return default_code, default_name

    # Map FF12
    f1d[['ff12_code', 'ff12_name']] = f1d['ccm_sic'].apply(
        lambda x: pd.Series(map_sic(x, ff12_map, 12, 'Other'))
    )

    # Map FF48
    f1d[['ff48_code', 'ff48_name']] = f1d['ccm_sic'].apply(
        lambda x: pd.Series(map_sic(x, ff48_map, 48, 'Other'))
    )

    ff12_coverage = f1d['ff12_code'].notna().sum()
    ff48_coverage = f1d['ff48_code'].notna().sum()

    print_dual(f"    FF12 coverage: {ff12_coverage:,} calls ({ff12_coverage/len(f1d)*100:.1f}%)")
    print_dual(f"    FF48 coverage: {ff48_coverage:,} calls ({ff48_coverage/len(f1d)*100:.1f}%)")

    return f1d

# ==============================================================================
# Report generation
# ==============================================================================

def generate_report(paths, year_stats, linking_stats, fuzzy_review_count, unmatched_count):
    """Generate comprehensive linking report"""
    report_path = paths['output_dir'] / "report_step_2_5.md"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# STEP 2.5: Merge Measures & Link CCM and Fama-French Industries - Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Script:** 2.5_LinkCcmAndIndustries\n\n")
        f.write("---\n\n")

        f.write("## Summary\n\n")
        f.write("Merged 4 measure panels into single wide-format dataset and enriched with:\n")
        f.write("1. **Panel Merge:** FULL OUTER JOIN on file_name across 4 measures\n")
        f.write("   - MaQaUnc, MaPresUnc, AnaQaUnc, MaQaNeg\n")
        f.write("   - Each measure contributes: total_tokens, hits, pct columns\n")
        f.write("2. **Multi-tier CCM linking:** PERMNO, CUSIP8, Fuzzy Name, Ticker\n")
        f.write("3. **Date-aware temporal matching** with CCM link validity periods\n")
        f.write("4. **Comprehensive audit trail** with quality scores\n")
        f.write("5. **FF12 and FF48 industry classifications** via SIC mapping\n\n")

        total_calls = sum(s['calls'] for s in year_stats.values())
        total_matched = sum(s['matched'] for s in year_stats.values())

        f.write(f"**Total calls processed:** {total_calls:,}\n")
        f.write(f"**Calls with gvkey:** {total_matched:,} ({total_matched/total_calls*100:.1f}%)\n")
        f.write(f"**Calls with FF industries:** {sum(s['ff12_coverage'] for s in year_stats.values()):,}\n")
        f.write(f"**Fuzzy matches needing review:** {fuzzy_review_count:,}\n")
        f.write(f"**Unmatched calls:** {unmatched_count:,} ({unmatched_count/total_calls*100:.1f}%)\n\n")

        f.write("---\n\n")

        f.write("## Linking Method Distribution\n\n")
        f.write("| Method | Calls | Percentage | Quality Score |\n")
        f.write("|--------|------:|-----------:|--------------:|\n")
        f.write(f"| Tier 1: PERMNO+Date | {linking_stats['tier1_permno_date']:,} | {linking_stats['tier1_permno_date']/total_calls*100:.1f}% | 100 |\n")
        f.write(f"| Tier 2: CUSIP8+Date | {linking_stats['tier2_cusip_date']:,} | {linking_stats['tier2_cusip_date']/total_calls*100:.1f}% | 90 |\n")
        f.write(f"| Tier 3: Fuzzy Name | {linking_stats['tier3_fuzzy_name']:,} | {linking_stats['tier3_fuzzy_name']/total_calls*100:.1f}% | 70-80 |\n")
        f.write(f"| Tier 4: Ticker+Date | {linking_stats['tier4_ticker_date']:,} | {linking_stats['tier4_ticker_date']/total_calls*100:.1f}% | 60 |\n")
        f.write(f"| Tier 5: No Match | {linking_stats['tier5_no_match']:,} | {linking_stats['tier5_no_match']/total_calls*100:.1f}% | 0 |\n")

        f.write("\n---\n\n")

        f.write("## Year Statistics\n\n")
        f.write("| Year | Calls | Matched | Match Rate | FF12 Coverage | File Size (MB) |\n")
        f.write("|------|------:|--------:|-----------:|--------------:|---------------:|\n")

        for year in sorted(year_stats.keys()):
            s = year_stats[year]
            f.write(f"| {year} | {s['calls']:,} | {s['matched']:,} | {s['matched']/s['calls']*100:.1f}% | "
                   f"{s['ff12_coverage']:,} | {s['file_size_mb']:.1f} |\n")

        f.write("\n---\n\n")

        f.write("## File Checksums (SHA-256)\n\n")
        for year in sorted(year_stats.keys()):
            f.write(f"**f1d_enriched_{year}.parquet:** `{year_stats[year]['sha256']}`\n\n")

        f.write("---\n\n")
        f.write("**End of Report**\n")

    print_dual(f"\nReport generated: {report_path}")

# ==============================================================================
# Main execution
# ==============================================================================

def main():
    """Main execution"""
    start_time = datetime.now()

    # Load configuration
    config = load_config()
    paths, timestamp = setup_paths(config)

    # Set up dual-write logging
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer

    print_dual("="*80)
    print_dual("STEP 2.5: Merge Measures & Link CCM and Fama-French Industries")
    print_dual("="*80)
    print_dual(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_dual(f"Config: {config['project']['name']} v{config['project']['version']}")
    print_dual(f"Log file: {paths['log_file']}")
    print_dual("")

    # Step 1: Load reference datasets
    print_dual("Step 1: Loading reference datasets")
    ccm = load_and_prepare_ccm(paths['ccm_file'])
    ff12_map = parse_ff_industries(paths['ff12_file'], 12)
    ff48_map = parse_ff_industries(paths['ff48_file'], 48)

    # Initialize tracking
    linking_stats = {
        'tier1_permno_date': 0,
        'tier2_cusip_date': 0,
        'tier3_fuzzy_name': 0,
        'tier4_ticker_date': 0,
        'tier5_no_match': 0
    }
    year_stats = {}
    all_fuzzy_reviews = []
    all_unmatched = []

    # Step 2: Process each year
    print_dual("\nStep 2: Processing years with multi-tier linking")
    
    # Allow CLI override for year range
    if len(sys.argv) >= 3:
        year_start = int(sys.argv[1])
        year_end = int(sys.argv[2])
        print_dual(f"  Overriding config: Processing years {year_start}-{year_end}")
    else:
        year_start = config['data']['year_start']
        year_end = config['data']['year_end']

    for year in range(year_start, year_end + 1):
        print_dual(f"\n{'='*60}")
        print_dual(f"Year {year}")
        print_dual(f"{'='*60}")

        # Merge all 4 measure panels into one
        try:
            f1d = merge_measure_panels(paths['measure_panel_dir'], year, config)
            # Ensure no duplicate columns
            f1d = f1d.loc[:, ~f1d.columns.duplicated()]
        except FileNotFoundError as e:
            print_dual(f"  ERROR: {e}, skipping year {year}")
            continue

        # Initialize linking fields
        for col in ['gvkey', 'ccm_conm', 'ccm_sic', 'ccm_cusip', 'ccm_linkprim', 'ccm_linktype',
                    'link_method', 'link_quality_score', 'fuzzy_match_score', 'fuzzy_matched_name',
                    'fuzzy_needs_review', 'ff12_code', 'ff12_name', 'ff48_code', 'ff48_name']:
            f1d[col] = np.nan

        # Tier 1: PERMNO + Date
        tier1_count = link_tier1_permno_date(f1d, ccm)
        linking_stats['tier1_permno_date'] += tier1_count

        # Tier 2: CUSIP8 + Date
        tier2_count = link_tier2_cusip_date(f1d, ccm)
        linking_stats['tier2_cusip_date'] += tier2_count

        # Tier 3: Fuzzy Name (threshold increased from 85 to 92 for better quality)
        tier3_count, fuzzy_reviews = link_tier3_fuzzy_name(f1d, ccm, threshold=92)
        linking_stats['tier3_fuzzy_name'] += tier3_count
        all_fuzzy_reviews.extend(fuzzy_reviews)

        # Tier 4: Ticker + Date
        tier4_count = link_tier4_ticker_date(f1d, ccm)
        linking_stats['tier4_ticker_date'] += tier4_count

        # Tier 5: Mark unmatched
        unmatched_audit = mark_unmatched_calls(f1d)
        linking_stats['tier5_no_match'] += len(unmatched_audit)
        all_unmatched.extend(unmatched_audit)

        # Map Fama-French industries
        f1d = map_fama_french_industries(f1d, ff12_map, ff48_map)

        # Filter to ONLY matched records (exclude records without gvkey)
        total_before_filter = len(f1d)
        f1d = f1d[f1d['gvkey'].notna()].reset_index(drop=True)
        excluded_count = total_before_filter - len(f1d)

        print_dual(f"\n  Filtering unmatched records:")
        print_dual(f"    Before filter: {total_before_filter:,} records")
        print_dual(f"    After filter: {len(f1d):,} records")
        print_dual(f"    Excluded (no gvkey): {excluded_count:,} records ({excluded_count/total_before_filter*100:.1f}%)")

        # Write output
        output_file = paths['output_dir'] / f"f1d_enriched_{year}.parquet"
        f1d.to_parquet(output_file, index=False, engine='pyarrow', compression='snappy')

        file_size_mb = output_file.stat().st_size / (1024**2)

        # Track statistics
        year_stats[year] = {
            'calls': len(f1d),
            'matched': f1d['gvkey'].notna().sum(),
            'ff12_coverage': f1d['ff12_code'].notna().sum(),
            'file_size_mb': file_size_mb,
            'sha256': calculate_file_hash(output_file)
        }

        print_dual(f"  Created f1d_enriched_{year}.parquet ({file_size_mb:.1f} MB)")
        print_dual(f"  gvkey match rate: {year_stats[year]['matched']/len(f1d)*100:.1f}%")

    # Step 3: Save audit files
    print_dual("\nStep 3: Saving audit files")

    if all_fuzzy_reviews:
        fuzzy_df = pd.DataFrame(all_fuzzy_reviews)
        fuzzy_path = paths['output_dir'] / "fuzzy_matches_review.csv"
        fuzzy_df.to_csv(fuzzy_path, index=False)
        print_dual(f"  Saved fuzzy matches review: {fuzzy_path}")

    if all_unmatched:
        unmatched_df = pd.DataFrame(all_unmatched)
        unmatched_path = paths['output_dir'] / "unmatched_calls_audit.csv"
        unmatched_df.to_csv(unmatched_path, index=False)
        print_dual(f"  Saved unmatched calls audit: {unmatched_path}")

    # Step 4: Generate report
    print_dual("\nStep 4: Generating report")
    generate_report(paths, year_stats, linking_stats, len(all_fuzzy_reviews), len(all_unmatched))

    # Step 5: Update latest symlink
    print_dual("\nStep 5: Updating latest symlink")
    if paths['latest_dir'].exists():
        if paths['latest_dir'].is_symlink():
            paths['latest_dir'].unlink()
        else:
            shutil.rmtree(paths['latest_dir'])

    try:
        paths['latest_dir'].symlink_to(paths['output_dir'], target_is_directory=True)
        print_dual(f"  Created symlink: latest -> {paths['output_dir'].name}")
    except OSError:
        shutil.copytree(paths['output_dir'], paths['latest_dir'])
        print_dual(f"  Created copy: latest")

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    total_calls = sum(s['calls'] for s in year_stats.values())
    total_matched = sum(s['matched'] for s in year_stats.values())

    print_dual(f"\n{'='*80}")
    print_dual("SUMMARY")
    print_dual(f"{'='*80}")
    print_dual(f"Total calls processed: {total_calls:,}")
    print_dual(f"Calls with gvkey: {total_matched:,} ({total_matched/total_calls*100:.1f}%)")
    print_dual(f"Unmatched calls: {linking_stats['tier5_no_match']:,} ({linking_stats['tier5_no_match']/total_calls*100:.1f}%)")
    print_dual(f"\nOutput directory: {paths['output_dir']}")
    print_dual(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_dual(f"Duration: {duration:.2f} seconds")
    print_dual("="*80)

    # Close log
    dual_writer.close()
    sys.stdout = dual_writer.terminal

if __name__ == "__main__":
    main()
