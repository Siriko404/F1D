import pandas as pd
from pathlib import Path
from rapidfuzz import fuzz, process

root = Path(r'c:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D')

# Load data
manifest = pd.read_parquet(root / '4_Outputs' / '1.0_BuildSampleManifest' / 'latest' / 'master_sample_manifest.parquet')
sdc = pd.read_parquet(root / '1_Inputs' / 'SDC' / 'sdc-ma-merged.parquet')

# Prepare
sdc_us = sdc[(sdc['Target Nation'] == 'United States') & (sdc['Target Public Status'] == 'Public')].copy()
sdc_us['announce_date'] = pd.to_datetime(sdc_us['Date Announced'], errors='coerce')
sdc_period = sdc_us[(sdc_us['announce_date'] >= '2002-01-01') & (sdc_us['announce_date'] <= '2018-12-31')].copy()

# CUSIP and Ticker matches first
manifest['cusip6'] = manifest['cusip'].astype(str).str[:6]
sdc_period['target_cusip6'] = sdc_period['Target 6-digit CUSIP'].astype(str).str.strip()
ccm_cusips = set(manifest['cusip6'].unique())
sdc_period['match_cusip'] = sdc_period['target_cusip6'].isin(ccm_cusips)

manifest['ticker_clean'] = manifest['company_ticker'].astype(str).str.upper().str.strip()
all_tickers = set(manifest['ticker_clean'].unique())
sdc_period['sdc_ticker'] = sdc_period['Target Primary Ticker Symbol'].astype(str).str.upper().str.strip()
sdc_period['match_ticker'] = sdc_period['sdc_ticker'].isin(all_tickers)

# Prepare names
manifest['name_clean'] = manifest['company_name'].astype(str).str.upper().str.strip()
manifest['name_clean'] = manifest['name_clean'].str.replace(r'[^\w\s]', '', regex=True)

sdc_period['target_name_clean'] = sdc_period['Target Full Name'].astype(str).str.upper().str.strip()
sdc_period['target_name_clean'] = sdc_period['target_name_clean'].str.replace(r'[^\w\s]', '', regex=True)

ccm_names = manifest['name_clean'].unique().tolist()

# Get unmatched
unmatched = sdc_period[~(sdc_period['match_cusip'] | sdc_period['match_ticker'])].copy()
print(f'Unmatched by CUSIP/Ticker: {len(unmatched)}')

# Test thresholds
for threshold in [100, 98, 95]:
    matches = []
    samples = []
    for name in unmatched['target_name_clean'].tolist():
        if name == '' or name == 'NAN':
            matches.append(False)
            continue
        match = process.extractOne(name, ccm_names, scorer=fuzz.token_sort_ratio)
        if match and match[1] >= threshold:
            matches.append(True)
            if len(samples) < 5:
                samples.append((name[:40], match[0][:40], match[1]))
        else:
            matches.append(False)
    
    n_match = sum(matches)
    print(f'\nThreshold {threshold}%: {n_match} fuzzy matches')
    print('  Samples:')
    for s, m, sc in samples:
        print(f'    "{s}" -> "{m}" ({sc:.0f})')
