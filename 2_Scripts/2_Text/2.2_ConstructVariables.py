
import pandas as pd
import numpy as np
import re
from pathlib import Path
from datetime import datetime
import sys
import os
import shutil

# ==============================================================================
# Setup
# ==============================================================================

def setup_logging():
    log_dir = Path(__file__).parent.parent.parent / '3_Logs' / '2.2_ConstructVariables'
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_path = log_dir / f"{timestamp}.log"
    
    class DualWriter:
        def __init__(self, path):
            self.file = open(path, 'w', encoding='utf-8')
            self.stdout = sys.stdout
        def write(self, msg):
            self.stdout.write(msg)
            self.file.write(msg)
            self.file.flush()
        def flush(self):
            self.stdout.flush()
            self.file.flush()
    
    sys.stdout = DualWriter(log_path)
    return log_path

def update_latest_symlink(latest_dir, output_dir):
    if latest_dir.exists() or latest_dir.is_symlink():
        try:
            if latest_dir.is_symlink(): os.unlink(str(latest_dir))
            else: shutil.rmtree(str(latest_dir))
        except Exception: pass
    try:
        os.symlink(str(output_dir), str(latest_dir), target_is_directory=True)
        print(f"\nUpdated 'latest' -> {output_dir.name}")
    except OSError:
        try:
            shutil.copytree(str(output_dir), str(latest_dir))
            print(f"\nCopied outputs to 'latest'")
        except Exception: pass

# ==============================================================================
# Helper Loading Functions
# ==============================================================================

def load_manager_keywords(root):
    path = root / '1_Inputs' / 'managerial_roles_extracted.txt'
    with open(path, 'r') as f:
        keywords = [line.strip() for line in f if line.strip()]
    pattern = re.compile('|'.join(keywords), re.IGNORECASE)
    print(f"  Loaded {len(keywords)} manager keywords")
    return pattern

def load_ceo_map(root):
    manifest_path = root / '4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet'
    df = pd.read_parquet(manifest_path, columns=['file_name', 'ceo_name', 'prev_ceo_name', 'gvkey', 'conm', 'sic', 'start_date'])
    
    # Extract last names
    df['ceo_last'] = df['ceo_name'].fillna('').str.split().str[-1].str.lower()
    df['prev_ceo_last'] = df['prev_ceo_name'].fillna('').str.split().str[-1].str.lower()
    df['ceo_name_lower'] = df['ceo_name'].fillna('').str.lower()
    df['prev_ceo_name_lower'] = df['prev_ceo_name'].fillna('').str.lower()
    
    # Extract Year from start_date
    df['year'] = pd.to_datetime(df['start_date']).dt.year
    
    return df

# ==============================================================================
# Flagging Logic
# ==============================================================================

def flag_speakers(df, manager_pattern, manifest_df):
    # Merge manifest info for context (company name, ceo name)
    # We only need 'conm' and CEO cols for flagging, not everything
    cols_to_merge = ['file_name', 'conm', 'ceo_name_lower', 'prev_ceo_name_lower', 'ceo_last', 'prev_ceo_last']
    # Merge only columns that are NOT in df already (except key)
    cols_to_merge = [c for c in cols_to_merge if c not in df.columns or c == 'file_name']
    
    df = df.merge(manifest_df[cols_to_merge], on='file_name', how='left')
    
    # Fill NA
    role = df['role'].fillna('')
    employer = df['employer'].fillna('')
    conm = df['conm'].fillna('')
    speaker_name = df['speaker_name'].fillna('')
    
    # Analyst
    df['is_analyst'] = role.str.contains('analyst', case=False)
    
    # Operator
    df['is_operator'] = role.str.contains('operator', case=False)
    
    # Manager
    # Keyword match
    is_keyword = role.str.contains(manager_pattern)
    # Employer match
    is_employer = employer.str.lower() == conm.str.lower()
    
    df['is_manager'] = (~df['is_analyst'] & ~df['is_operator']) & (is_keyword | is_employer)
    
    # CEO (Tiered)
    speaker_lower = speaker_name.str.lower()
    speaker_last = speaker_name.str.split().str[-1].str.lower()
    
    is_ceo_exact = (speaker_lower == df['ceo_name_lower']) | (speaker_lower == df['prev_ceo_name_lower'])
    is_ceo_last = (speaker_last == df['ceo_last']) | (speaker_last == df['prev_ceo_last'])
    
    df['is_ceo'] = is_ceo_exact | is_ceo_last
    
    return df

# ==============================================================================
# Aggregation (Weighted - Ratio of Sums)
# ==============================================================================

def aggregate_weighted(df, sample_mask, context_mask, count_cols):
    subset = df[sample_mask & context_mask].copy()
    if len(subset) == 0: return None
    
    # Group by file
    gb = subset.groupby('file_name')
    
    # Sum Counts and Totals
    sums = gb[count_cols + ['total_tokens']].sum()
    
    # Calculate Pct (x100)
    results = {}
    total_tokens = sums['total_tokens'].replace(0, np.nan)
    
    for col in count_cols:
        cat = col.replace('_count', '')
        # Variable naming: Sample_Context_Cat_pct
        # We handle sample/context prefix outside
        pct = (sums[col] / total_tokens) * 100.0
        results[f'{cat}_pct'] = pct
        
    return pd.DataFrame(results)

def process_year(year, root, manager_pattern, manifest_df, out_dir):
    in_path = root / f"4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/linguistic_counts_{year}.parquet"
    if not in_path.exists():
        print(f"  Skipping {year}: Input not found")
        return
    
    print(f"\nProcessing {year}...")
    df = pd.read_parquet(in_path)
    
    # Flag
    df = flag_speakers(df, manager_pattern, manifest_df)
    
    print(f"  Analyst: {df['is_analyst'].sum():,}")
    print(f"  Manager: {df['is_manager'].sum():,}")
    
    # Identify count columns
    count_cols = [c for c in df.columns if c.endswith('_count')]
    
    # Define Aggregations
    # Legacy mainly cared about: Manager QA, Analyst QA (?), Manager Pres (?)
    # We will generate comprehensive set
    
    samples = {
        'Manager': df['is_manager'],
        'Analyst': df['is_analyst'],
        'CEO': df['is_ceo'],
        'NonCEO_Manager': df['is_manager'] & ~df['is_ceo'],  # Managers excluding CEO
        'Entire': pd.Series(True, index=df.index)
    }
    
    contexts = {
        'QA': df['context'] == 'qa',
        'Pres': df['context'] == 'pres',
        'All': df['context'].isin(['qa', 'pres'])
    }
    
    # Initialize result with metadata
    # Use manifest metadata
    meta = manifest_df[manifest_df['year'] == year][['file_name', 'start_date', 'gvkey', 'conm', 'sic']].copy()
    
    for s_name, s_mask in samples.items():
        for c_name, c_mask in contexts.items():
            agg_df = aggregate_weighted(df, s_mask, c_mask, count_cols)
            if agg_df is not None:
                # Rename columns
                agg_df.columns = [f'{s_name}_{c_name}_{c}' for c in agg_df.columns]
                # Merge
                meta = meta.merge(agg_df, on='file_name', how='left')
    
    # Fill NaN with 0? Or keep NaN for missing sections?
    # Legacy behavior: likely keep NaN or impute.
    # We will keep NaN to distinctions between "No Uncertainty" (0) and "No Text" (NaN).
    
    out_path = out_dir / f"linguistic_variables_{year}.parquet"
    meta.to_parquet(out_path, index=False)
    print(f"  Saved {out_path.name}: {len(meta):,} rows")

def main():
    print("=== Step 2.2: Construct Variables (Weighted) ===")
    root = Path(__file__).parent.parent.parent
    setup_logging()
    
    out_base = root / '4_Outputs' / '2_Textual_Analysis'
    out_dir = out_base / f'2.2_Variables' / datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load References
    manager_pattern = load_manager_keywords(root)
    manifest_df = load_ceo_map(root)
    
    # Process
    for year in range(2002, 2019):
        process_year(year, root, manager_pattern, manifest_df, out_dir)
        
    update_latest_symlink(out_base / '2.2_Variables' / 'latest', out_dir)
    print("\n=== Complete ===")

if __name__ == "__main__":
    main()
