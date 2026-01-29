"""
Step 2.4: Linguistic Variables (Aggregation)
============================================
Aggregates speaker-level measures from Step 2.3 into call-level variables.

Inputs:
    - 4_Outputs/2_Linguistic_Analysis/extended_latest/linguistic_measures_{year}.parquet
    - 4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet
    - managerial_roles_extracted.txt

Outputs:
    - 4_Outputs/2.4_Linguistic_Variables/{timestamp}/linguistic_variables_{year}.parquet
    - 4_Outputs/2.4_Linguistic_Variables/{timestamp}/variable_reference.csv
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
from datetime import datetime
import sys
import os
import shutil

# ==============================================================================
# Setup & Utilities
# ==============================================================================

def setup_logging(log_dir):
    """Setup dual logging to console and file."""
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
    """Update the 'latest' symlink to point to output_dir."""
    if latest_dir.exists() or latest_dir.is_symlink():
        try:
            if latest_dir.is_symlink():
                os.unlink(str(latest_dir))
            else:
                shutil.rmtree(str(latest_dir))
        except Exception as e:
            print(f"  Warning: Could not remove old 'latest': {e}")
    try:
        os.symlink(str(output_dir), str(latest_dir), target_is_directory=True)
        print(f"\nUpdated 'latest' -> {output_dir.name}")
    except OSError:
        try:
            shutil.copytree(str(output_dir), str(latest_dir))
            print(f"\nCopied outputs to 'latest' (symlink not available)")
        except Exception as e2:
            print(f"\n  Warning: Could not create 'latest': {e2}")

# ==============================================================================
# Data Loading
# ==============================================================================

def load_manager_keywords(root):
    """Load manager keywords from file and compile regex pattern."""
    keywords_path = root / 'managerial_roles_extracted.txt'
    with open(keywords_path, 'r') as f:
        keywords = [line.strip() for line in f if line.strip()]
    # Compile regex pattern for efficient matching
    pattern = re.compile('|'.join(keywords), re.IGNORECASE)
    print(f"  Loaded {len(keywords)} manager keywords")
    return pattern

def load_ceo_map(root):
    """Load manifest and create CEO lookup with last names extracted."""
    manifest_path = root / '4_Outputs' / '1.0_BuildSampleManifest' / 'latest' / 'master_sample_manifest.parquet'
    df = pd.read_parquet(manifest_path, columns=['file_name', 'ceo_name', 'prev_ceo_name'])
    
    # Extract last names (last word after split)
    df['ceo_last'] = df['ceo_name'].fillna('').str.split().str[-1].str.lower()
    df['prev_ceo_last'] = df['prev_ceo_name'].fillna('').str.split().str[-1].str.lower()
    df['ceo_name_lower'] = df['ceo_name'].fillna('').str.lower()
    df['prev_ceo_name_lower'] = df['prev_ceo_name'].fillna('').str.lower()
    
    print(f"  Loaded CEO data for {len(df):,} files")
    return df[['file_name', 'ceo_name_lower', 'prev_ceo_name_lower', 'ceo_last', 'prev_ceo_last']]

def load_measures(root, year):
    """Load linguistic measures for a year."""
    path = root / '4_Outputs' / '2_Linguistic_Analysis' / 'extended_latest' / f'linguistic_measures_{year}.parquet'
    if not path.exists():
        print(f"  Warning: File not found: {path}")
        return None
    df = pd.read_parquet(path)
    print(f"  Loaded {len(df):,} rows for {year}")
    return df

# ==============================================================================
# Flagging (Vectorized)
# ==============================================================================

def flag_speakers(df, manager_pattern):
    """Create boolean flags for speaker roles (fully vectorized)."""
    # Fill NaN values in string columns
    role = df['role'].fillna('')
    employer = df['employer'].fillna('')
    conm = df['conm'].fillna('')
    speaker_name = df['speaker_name'].fillna('')
    
    # Analyst flag
    df['is_analyst'] = role.str.contains('analyst', case=False, na=False)
    
    # Operator flag
    df['is_operator'] = role.str.contains('operator', case=False, na=False)
    
    # Manager keyword flag (using pre-compiled regex)
    df['is_manager_keyword'] = role.str.contains(manager_pattern, na=False)
    
    # Employer match flag
    df['is_employer_match'] = employer.str.lower() == conm.str.lower()
    
    # Manager flag: NOT(analyst|operator) AND (keyword|employer)
    df['is_manager'] = (~df['is_analyst'] & ~df['is_operator']) & \
                       (df['is_manager_keyword'] | df['is_employer_match'])
    
    # CEO matching (multi-tier)
    speaker_lower = speaker_name.str.lower()
    speaker_last = speaker_name.str.split().str[-1].str.lower()
    
    # Tier 1: Exact match
    is_ceo_exact = (speaker_lower == df['ceo_name_lower']) | \
                   (speaker_lower == df['prev_ceo_name_lower'])
    
    # Tier 2: Last name match
    is_ceo_last = (speaker_last == df['ceo_last']) | \
                  (speaker_last == df['prev_ceo_last'])
    
    df['is_ceo'] = is_ceo_exact | is_ceo_last
    
    return df

# ==============================================================================
# Aggregation
# ==============================================================================

def aggregate_measures(df, sample_name, sample_mask, context_name, context_mask, measure_cols):
    """Aggregate measures for a specific sample-context combination."""
    # Apply both masks
    filtered = df[sample_mask & context_mask].copy()
    
    if len(filtered) == 0:
        return None
    
    # 1. Standard Aggregations (Mean of Ratios)
    grouped = filtered.groupby('file_name')[measure_cols].agg(
        ['mean', 'max', lambda x: x.quantile(0.8)]
    )
    
    # Flatten column names
    new_cols = {}
    for col, stat in grouped.columns:
        stat_name = 'p80' if 'lambda' in str(stat) else stat
        new_cols[f'{sample_name}_{context_name}_{col}_{stat_name}'] = grouped[(col, stat)]
    
    standard_df = pd.DataFrame(new_cols)
    
    # 2. Weighted Aggregations (Ratio of Sums) - Matches Legacy Logic
    # Reconstruct counts: val * total_tokens
    # Then Sum(counts) / Sum(total_tokens)
    
    # Prepare weights
    weights = filtered['total_tokens'].fillna(0)
    
    # Group sum of weights
    sum_weights = weights.groupby(filtered['file_name']).sum()
    
    weighted_data = {}
    
    for col in measure_cols:
        # Reconstruct numerator (count or mass)
        numerator = filtered[col].fillna(0) * weights
        
        # Sum numerator per file
        sum_numerator = numerator.groupby(filtered['file_name']).sum()
        
        # Calculate weighted mean (Ratio of Sums)
        weighted_mean = sum_numerator / sum_weights.replace(0, np.nan)
        
        # Apply scaling if it's a percentage column (Match Legacy x100)
        if 'pct' in col or 'unique_pct' in col:
            weighted_mean = weighted_mean * 100.0
            
        weighted_data[f'{sample_name}_{context_name}_{col}_weighted'] = weighted_mean

    weighted_df = pd.DataFrame(weighted_data)
    
    # Join both
    result = standard_df.join(weighted_df, how='outer').reset_index()
    return result

def process_year(year, root, manager_pattern, ceo_df, out_dir):
    """Process a single year."""
    print(f"\n{'='*60}")
    print(f"Processing Year {year}")
    print(f"{'='*60}")
    
    # Load measures
    df = load_measures(root, year)
    if df is None:
        return None
    
    # Merge CEO data
    df = df.merge(ceo_df, on='file_name', how='left')
    
    # Flag speakers
    df = flag_speakers(df, manager_pattern)
    
    # Report flagging stats
    print(f"  Analysts: {df['is_analyst'].sum():,}")
    print(f"  Managers: {df['is_manager'].sum():,}")
    print(f"  CEOs: {df['is_ceo'].sum():,}")
    
    # Get measure columns (all *_pct, *_entropy, *_interaction, *_unique_pct)
    measure_cols = [c for c in df.columns if any(c.endswith(s) for s in 
                   ['_pct', '_entropy', '_interaction', '_unique_pct'])]
    print(f"  Measure columns: {len(measure_cols)}")
    
    # Define samples
    samples = {
        'Entire': pd.Series(True, index=df.index),
        'Analyst': df['is_analyst'],
        'Manager': df['is_manager'],
        'CEO': df['is_ceo']
    }
    
    # Define contexts
    contexts = {
        'All': df['context'].isin(['pres', 'qa']),
        'Pres': df['context'] == 'pres',
        'QA': df['context'] == 'qa'
    }
    
    # Aggregate for each sample-context combo
    results = []
    for sample_name, sample_mask in samples.items():
        for context_name, context_mask in contexts.items():
            agg = aggregate_measures(df, sample_name, sample_mask, 
                                    context_name, context_mask, measure_cols)
            if agg is not None:
                results.append(agg)
                print(f"    {sample_name}_{context_name}: {len(agg):,} files")
    
    # Merge all results
    if not results:
        print("  Warning: No results to merge")
        return None
    
    # Start with file metadata
    metadata_cols = ['file_name', 'gvkey', 'conm', 'sic', 'start_date', 'year']
    metadata = df[metadata_cols].drop_duplicates('file_name')
    
    # Outer join all aggregated dataframes
    final = metadata
    for agg in results:
        final = final.merge(agg, on='file_name', how='outer')
    
    print(f"  Final: {len(final):,} files, {len(final.columns):,} columns")
    
    # Save
    out_path = out_dir / f'linguistic_variables_{year}.parquet'
    final.to_parquet(out_path, index=False)
    print(f"  Saved: {out_path.name}")
    
    return final

# ==============================================================================
# Variable Reference
# ==============================================================================

def generate_variable_reference(sample_df, out_dir):
    """Generate variable_reference.csv."""
    rows = []
    
    # Metadata columns
    metadata = [
        ('file_name', 'Input', 'Unique identifier for the earnings call'),
        ('gvkey', 'Merged', 'Global Company Key'),
        ('conm', 'Merged', 'Company Name'),
        ('sic', 'Merged', 'Standard Industrial Classification'),
        ('start_date', 'Merged', 'Call date'),
        ('year', 'Merged', 'Year of the call'),
    ]
    rows.extend(metadata)
    
    # Generated columns
    for col in sample_df.columns:
        if col in [m[0] for m in metadata]:
            continue
        
        # Parse column name: Sample_Context_Category_Measure_Stat
        parts = col.rsplit('_', 2)
        if len(parts) >= 3:
            stat = parts[-1]  # mean or max
            measure = parts[-2]  # pct, entropy, etc.
            prefix = '_'.join(parts[:-2])  # Sample_Context_Category
            desc = f"{prefix} {measure} ({stat})"
            rows.append((col, 'Calculated (2.4)', desc))
        else:
            rows.append((col, 'Calculated (2.4)', 'Aggregated measure'))
    
    df = pd.DataFrame(rows, columns=['Variable', 'Source', 'Description'])
    out_path = out_dir / 'variable_reference.csv'
    df.to_csv(out_path, index=False)
    print(f"\nSaved variable_reference.csv ({len(df)} variables)")

# ==============================================================================
# Main
# ==============================================================================

# Global variables for worker processes
_manager_pattern = None
_ceo_df = None
_root = None
_out_dir = None

def init_worker(manager_pattern, ceo_df, root, out_dir):
    """Initialize global variables for worker processes."""
    global _manager_pattern, _ceo_df, _root, _out_dir
    _manager_pattern = manager_pattern
    _ceo_df = ceo_df
    _root = root
    _out_dir = out_dir

def process_year_worker(year):
    """Worker function to process a single year."""
    return process_year(year, _root, _manager_pattern, _ceo_df, _out_dir)

def main(year_start=2002, year_end=2018, workers=2):
    print("=" * 80)
    print("STEP 2.4: Linguistic Variables (Aggregation)")
    print("=" * 80)
    
    root = Path(__file__).parent.parent.parent
    
    # Setup output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_base = root / '4_Outputs' / '2.4_Linguistic_Variables'
    out_dir = out_base / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup logging
    log_dir = root / '3_Logs' / '2.4_Linguistic_Variables'
    setup_logging(log_dir)
    
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")
    print(f"Years: {year_start}-{year_end}")
    print(f"Workers: {workers}")
    
    # Load reference data
    print("\nLoading reference data...")
    manager_pattern = load_manager_keywords(root)
    ceo_df = load_ceo_map(root)
    
    # Initialize globals for this process (for sequential fallback)
    global _manager_pattern, _ceo_df, _root, _out_dir
    _manager_pattern = manager_pattern
    _ceo_df = ceo_df
    _root = root
    _out_dir = out_dir
    
    # Process years in parallel
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import multiprocessing
    
    years = list(range(year_start, year_end + 1))
    sample_df = None
    
    if workers > 1:
        print(f"\nProcessing {len(years)} years with {workers} workers...")
        with ProcessPoolExecutor(max_workers=workers, initializer=init_worker,
                                  initargs=(manager_pattern, ceo_df, root, out_dir)) as executor:
            futures = {executor.submit(process_year_worker, year): year for year in years}
            for future in as_completed(futures):
                year = futures[future]
                try:
                    result = future.result()
                    if result is not None and sample_df is None:
                        sample_df = result
                except Exception as e:
                    print(f"  Error processing {year}: {e}")
    else:
        # Sequential fallback
        for year in years:
            result = process_year(year, root, manager_pattern, ceo_df, out_dir)
            if result is not None and sample_df is None:
                sample_df = result
    
    # Generate variable reference
    if sample_df is not None:
        generate_variable_reference(sample_df, out_dir)
    
    # Update symlink
    update_latest_symlink(out_base / 'latest', out_dir)
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    
    # Parse command line args for year range and workers
    if len(sys.argv) == 4:
        main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    elif len(sys.argv) == 3:
        main(int(sys.argv[1]), int(sys.argv[2]))
    else:
        main()

