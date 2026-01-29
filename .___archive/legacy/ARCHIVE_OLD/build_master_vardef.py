#!/usr/bin/env python3
"""Build master variable definitions from all sources"""

import pandas as pd
from pathlib import Path

root = Path(__file__).parent.parent

# Define sources
sources = {
    'CCM': root / '1_Inputs' / 'CRSPCompustat_CCM' / 'CRSP_CCM_Variable_Reference.csv',
    'CRSP_DSF': root / '1_Inputs' / 'CRSP_DSF' / 'CRSP_DSF_Variable_Reference.csv',
    'Execucomp': root / '1_Inputs' / 'Execucomp' / 'vr.csv',
    'Compustat': root / '1_Inputs' / 'comp_na_daily_all' / 'Compustat_Variable_Reference.csv',
    'IBES': root / '1_Inputs' / 'tr_ibes' / 'IBES_Variable_reference.csv',
}

all_vars = []

for source_name, csv_path in sources.items():
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        # Standardize
        df.columns = [c.strip().lower() for c in df.columns]
        
        # Handle different column names
        var_col = 'variable' if 'variable' in df.columns else df.columns[0]
        desc_col = 'description' if 'description' in df.columns else df.columns[-1]
        
        for _, row in df.iterrows():
            all_vars.append({
                'variable': str(row[var_col]).lower().strip(),
                'source': source_name,
                'description': str(row[desc_col]).strip()
            })

# Create master DataFrame
master_df = pd.DataFrame(all_vars)

# Add custom computed variables
computed_vars = [
    ('link_method', 'Computed', 'Method used for CCM linking: permno_date, cusip8_date, or name_fuzzy'),
    ('link_quality', 'Computed', 'Quality score: 100 (PERMNO), 90 (CUSIP), 80 (Fuzzy)'),
    ('ff12_code', 'Computed', 'Fama-French 12 industry code based on SIC'),
    ('ff12_name', 'Computed', 'Fama-French 12 industry name'),
    ('ff48_code', 'Computed', 'Fama-French 48 industry code based on SIC'),
    ('ff48_name', 'Computed', 'Fama-French 48 industry name'),
    ('sic_int', 'Computed', 'SIC code converted to integer'),
    ('year', 'Computed', 'Year extracted from date'),
    ('month', 'Computed', 'Month extracted from date'),
    ('ceo_id', 'Execucomp', 'CEO executive ID (execid) from Execucomp'),
    ('ceo_name', 'Execucomp', 'CEO full name from Execucomp'),
    ('prev_ceo_id', 'Computed', 'Previous CEO executive ID'),
    ('prev_ceo_name', 'Computed', 'Previous CEO full name'),
]

for var, source, desc in computed_vars:
    master_df = pd.concat([master_df, pd.DataFrame([{
        'variable': var,
        'source': source,
        'description': desc
    }])], ignore_index=True)

# Add Unified-info columns (original metadata)
unified_vars = [
    ('file_name', 'Unified-info', 'Unique call document identifier'),
    ('company_name', 'Unified-info', 'Company name from transcript'),
    ('company_id', 'Unified-info', 'Company identifier in transcript database'),
    ('company_ticker', 'Unified-info', 'Stock ticker symbol'),
    ('start_date', 'Unified-info', 'Date and time when call started'),
    ('event_type', 'Unified-info', 'Event type code (1=Earnings Call)'),
    ('event_title', 'Unified-info', 'Title of the event'),
    ('city', 'Unified-info', 'City where call was hosted'),
    ('processing_lag_hours', 'Unified-info', 'Hours between call and transcript processing'),
    ('business_quarter', 'Unified-info', 'Fiscal quarter being discussed'),
    ('permno', 'Unified-info', 'CRSP PERMNO identifier'),
    ('cusip', 'Unified-info', 'CUSIP identifier'),
]

for var, source, desc in unified_vars:
    existing = master_df[master_df['variable'] == var]
    if len(existing) == 0:
        master_df = pd.concat([master_df, pd.DataFrame([{
            'variable': var,
            'source': source,
            'description': desc
        }])], ignore_index=True)

# Drop duplicates, keeping first (more specific)
master_df = master_df.drop_duplicates(subset=['variable'], keep='first')

# Save
output_path = root / '1_Inputs' / 'master_variable_definitions.csv'
master_df.to_csv(output_path, index=False)
print(f"Created master variable definitions: {output_path}")
print(f"Total variables: {len(master_df)}")
