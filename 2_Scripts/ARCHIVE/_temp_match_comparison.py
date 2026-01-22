"""
SDC-CCM Matching Strategy Analysis
==================================
This script tests multiple matching approaches:
1. CUSIP6 (exact)
2. Ticker (temporal-aware)
3. Company Name (vectorized fuzzy)
4. Multi-tier union
"""

import pandas as pd
import numpy as np
from pathlib import Path
from rapidfuzz import fuzz, process
from collections import defaultdict

root = Path(r'c:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D')

print('='*60)
print('COMPREHENSIVE MATCHING STRATEGY ANALYSIS')
print('='*60)

# ============================================================================
# Load Data
# ============================================================================
print('\n[1] Loading data...')
manifest = pd.read_parquet(root / '4_Outputs' / '1.0_BuildSampleManifest' / 'latest' / 'master_sample_manifest.parquet')
sdc = pd.read_parquet(root / '1_Inputs' / 'SDC' / 'sdc-ma-merged.parquet')

# Filter SDC to US Public targets in our sample period
sdc_us = sdc[(sdc['Target Nation'] == 'United States') & (sdc['Target Public Status'] == 'Public')].copy()
sdc_us['announce_date'] = pd.to_datetime(sdc_us['Date Announced'], errors='coerce')
sdc_period = sdc_us[(sdc_us['announce_date'] >= '2002-01-01') & (sdc_us['announce_date'] <= '2018-12-31')].copy()
print(f'  SDC US Public 2002-2018: {len(sdc_period)} deals')

# ============================================================================
# Strategy 1: CUSIP6 (exact)
# ============================================================================
print('\n[2] Strategy 1: CUSIP6 Matching')
manifest['cusip6'] = manifest['cusip'].astype(str).str[:6]
sdc_period['target_cusip6'] = sdc_period['Target 6-digit CUSIP'].astype(str).str.strip()

ccm_cusips = set(manifest['cusip6'].unique())
sdc_cusips = set(sdc_period['target_cusip6'].unique())
overlap_cusip = ccm_cusips & sdc_cusips
sdc_period['match_cusip'] = sdc_period['target_cusip6'].isin(ccm_cusips)
print(f'  Overlap: {len(overlap_cusip)} CUSIPs')
print(f'  Matched Deals: {sdc_period["match_cusip"].sum()}')

# ============================================================================
# Strategy 2: Ticker (Temporal-Aware)
# ============================================================================
print('\n[3] Strategy 2: Temporal Ticker Matching')

# Build manifest ticker lookup by year
# (ticker -> set of years it was valid for this firm)
manifest['call_year'] = pd.to_datetime(manifest['start_date']).dt.year
manifest['ticker_clean'] = manifest['company_ticker'].astype(str).str.upper().str.strip()

# Create year-aware ticker set from manifest
ticker_by_year = defaultdict(set)
for _, row in manifest[['ticker_clean', 'call_year']].drop_duplicates().iterrows():
    ticker_by_year[row['call_year']].add(row['ticker_clean'])

sdc_period['sdc_ticker'] = sdc_period['Target Primary Ticker Symbol'].astype(str).str.upper().str.strip()
sdc_period['announce_year'] = sdc_period['announce_date'].dt.year

# Match ticker considering temporal window (+/- 1 year tolerance)
def temporal_ticker_match(row):
    t = row['sdc_ticker']
    y = row['announce_year']
    if pd.isna(t) or t == 'NAN' or t == '':
        return False
    # Check year and adjacent years
    for check_year in [y-1, y, y+1]:
        if t in ticker_by_year.get(check_year, set()):
            return True
    return False

sdc_period['match_ticker_temporal'] = sdc_period.apply(temporal_ticker_match, axis=1)
print(f'  Matched Deals (temporal): {sdc_period["match_ticker_temporal"].sum()}')

# Compare to naive ticker match
all_tickers = set(manifest['ticker_clean'].unique())
sdc_period['match_ticker_naive'] = sdc_period['sdc_ticker'].isin(all_tickers)
print(f'  Matched Deals (naive, no temporal): {sdc_period["match_ticker_naive"].sum()}')

# ============================================================================
# Strategy 3: Fuzzy Company Name Matching
# ============================================================================
print('\n[4] Strategy 3: Fuzzy Company Name Matching')

# Clean company names
manifest['name_clean'] = manifest['company_name'].astype(str).str.upper().str.strip()
manifest['name_clean'] = manifest['name_clean'].str.replace(r'[^\w\s]', '', regex=True)
manifest['name_clean'] = manifest['name_clean'].str.replace(r'\s+', ' ', regex=True)

sdc_period['target_name_clean'] = sdc_period['Target Full Name'].astype(str).str.upper().str.strip()
sdc_period['target_name_clean'] = sdc_period['target_name_clean'].str.replace(r'[^\w\s]', '', regex=True)
sdc_period['target_name_clean'] = sdc_period['target_name_clean'].str.replace(r'\s+', ' ', regex=True)

# Get unique names from manifest for matching
ccm_names = manifest['name_clean'].unique().tolist()
ccm_names_set = set(ccm_names)

# Vectorized fuzzy matching using rapidfuzz
# For each SDC target name, find best match in CCM names
unmatched_so_far = sdc_period[~(sdc_period['match_cusip'] | sdc_period['match_ticker_temporal'])].copy()
print(f'  Deals unmatched by CUSIP/Ticker: {len(unmatched_so_far)}')

# Use token_sort_ratio for better matching (handles word order)
def fuzzy_match_batch(names_to_match, choices, threshold=85):
    """Vectorized fuzzy matching."""
    results = []
    for name in names_to_match:
        if name == '' or name == 'NAN':
            results.append((None, 0))
            continue
        match = process.extractOne(name, choices, scorer=fuzz.token_sort_ratio)
        if match and match[1] >= threshold:
            results.append((match[0], match[1]))
        else:
            results.append((None, 0))
    return results

# Only run fuzzy on unmatched deals (expensive operation)
if len(unmatched_so_far) > 0:
    print(f'  Running fuzzy match on {len(unmatched_so_far)} unmatched deals...')
    fuzzy_results = fuzzy_match_batch(
        unmatched_so_far['target_name_clean'].tolist(),
        ccm_names,
        threshold=85
    )
    unmatched_so_far['fuzzy_match'] = [r[0] for r in fuzzy_results]
    unmatched_so_far['fuzzy_score'] = [r[1] for r in fuzzy_results]
    
    n_fuzzy_matched = (unmatched_so_far['fuzzy_match'].notna()).sum()
    print(f'  New matches via fuzzy (threshold=85): {n_fuzzy_matched}')
    
    # Show sample fuzzy matches
    sample_fuzzy = unmatched_so_far[unmatched_so_far['fuzzy_match'].notna()][
        ['target_name_clean', 'fuzzy_match', 'fuzzy_score']
    ].head(10)
    print('\n  Sample Fuzzy Matches:')
    for _, row in sample_fuzzy.iterrows():
        print(f"    '{row['target_name_clean'][:40]}' -> '{row['fuzzy_match'][:40]}' (score={row['fuzzy_score']})")

# ============================================================================
# Combined Multi-Tier Strategy
# ============================================================================
print('\n[5] Multi-Tier Strategy (CUSIP OR Ticker OR Fuzzy)')

# Apply fuzzy matches back to full dataset
if len(unmatched_so_far) > 0:
    fuzzy_matched_idx = unmatched_so_far[unmatched_so_far['fuzzy_match'].notna()].index
    sdc_period['match_fuzzy'] = False
    sdc_period.loc[fuzzy_matched_idx, 'match_fuzzy'] = True
else:
    sdc_period['match_fuzzy'] = False

sdc_period['match_any'] = sdc_period['match_cusip'] | sdc_period['match_ticker_temporal'] | sdc_period['match_fuzzy']

print(f'\n  SUMMARY:')
print(f'    CUSIP6 matches: {sdc_period["match_cusip"].sum()}')
print(f'    + Ticker (temporal): {(sdc_period["match_ticker_temporal"] & ~sdc_period["match_cusip"]).sum()} new')
print(f'    + Fuzzy Name: {sdc_period["match_fuzzy"].sum()} new')
print(f'    ---')
print(f'    TOTAL: {sdc_period["match_any"].sum()} deals')

# Classified by attitude
matched = sdc_period[sdc_period['match_any']]
print(f'\n  By Deal Attitude (total {len(matched)}):')
print(matched['Deal Attitude'].value_counts())

uninvited = matched['Deal Attitude'].isin(['Hostile', 'Unsolicited']).sum()
friendly = matched['Deal Attitude'].isin(['Friendly', 'Neutral', 'No Applicable']).sum()
print(f'\n  Classified:')
print(f'    Uninvited (Hostile+Unsolicited): {uninvited}')
print(f'    Friendly (Friendly+Neutral+NA): {friendly}')
