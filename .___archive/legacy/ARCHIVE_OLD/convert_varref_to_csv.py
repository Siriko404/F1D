#!/usr/bin/env python3
"""Convert all variable reference .txt files to .csv format"""

import pandas as pd
from pathlib import Path

root = Path(__file__).parent.parent

# Define source txt files and their output paths
txt_files = [
    root / '1_Inputs' / 'CRSPCompustat_CCM' / 'CRSP_CCM_Variable_Reference.txt',
    root / '1_Inputs' / 'CRSP_DSF' / 'CRSP_DSF_Variable_Reference.txt',
    root / '1_Inputs' / 'Execucomp' / 'vr.txt',
    root / '1_Inputs' / 'comp_na_daily_all' / 'Compustat_Variable_Reference.txt',
    root / '1_Inputs' / 'tr_ibes' / 'IBES_Variable_reference.txt',
]

for txt_path in txt_files:
    if not txt_path.exists():
        print(f"Skip: {txt_path} not found")
        continue
    
    try:
        # Read tab-separated file
        df = pd.read_csv(txt_path, sep='\t', encoding='utf-8')
        
        # Standardize column names
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        
        # Rename first column to 'variable' if named differently
        if df.columns[0] != 'variable':
            df = df.rename(columns={df.columns[0]: 'variable'})
        
        # Save as CSV
        csv_path = txt_path.with_suffix('.csv')
        df.to_csv(csv_path, index=False)
        print(f"Created: {csv_path.name} ({len(df)} rows)")
        
    except Exception as e:
        print(f"Error processing {txt_path.name}: {e}")

print("\nDone!")
