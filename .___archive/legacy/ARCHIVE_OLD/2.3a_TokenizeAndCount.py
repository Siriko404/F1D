#!/usr/bin/env python3
"""
==============================================================================
STEP 2.3a: Tokenize and Count - Orchestrator (Multi-Dataset)
==============================================================================
ID: 2.3a_TokenizeAndCount
Description: Orchestrates C++ tokenization with 2 dictionaries (Uncertainty,
             Negative) across 3 datasets (manager_qa, manager_pres, analyst_qa),
             converts Parquet<->JSON, aggregates to year-level files
Inputs:
    - config/project.yaml
    - 4_Outputs/2.1_BuildLmClarityDictionary/latest/lm_Uncertainty_dictionary.parquet
    - 4_Outputs/2.1_BuildLmClarityDictionary/latest/lm_Negative_dictionary.parquet
    - 4_Outputs/2.2_ExtractFilteredDocs/latest/{dataset}_docs_YYYY.parquet
Outputs:
    - 4_Outputs/2.3_TokenizeAndCount/TIMESTAMP/{dataset}_call_YYYY.parquet
    - 4_Outputs/2.3_TokenizeAndCount/latest/ (symlink)
    - 3_Logs/2.3_TokenizeAndCount/TIMESTAMP.log
Deterministic: true
==============================================================================
"""

import sys
import os
import json
import subprocess
import multiprocessing
from pathlib import Path
from datetime import datetime
import pandas as pd
import yaml
import shutil

# ==============================================================================
# Dataset definitions
# ==============================================================================

DATASETS = ['manager_qa', 'manager_pres', 'analyst_qa', 'entire_call']

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
        'unc_dictionary': root / '4_Outputs' / '2.1_BuildLmClarityDictionary' / 'latest' / 'lm_Uncertainty_dictionary.parquet',
        'neg_dictionary': root / '4_Outputs' / '2.1_BuildLmClarityDictionary' / 'latest' / 'lm_Negative_dictionary.parquet',
        'docs_pattern': str(root / '4_Outputs' / '2.2_ExtractFilteredDocs' / 'latest' / '{dataset}_docs_{year}.parquet'),
        'cpp_exe': root / '2_Scripts' / '2.3b_TokenizeText.exe',
        'build_script': root / '2_Scripts' / '2.3b_Build.bat',
        'temp_dir': root / '2_Scripts',
    }

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config['paths']['outputs'] / "2.3_TokenizeAndCount"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)

    paths['latest_dir'] = output_base / "latest"

    # Create log directory
    log_base = root / config['paths']['logs'] / "2.3_TokenizeAndCount"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}.log"

    return paths, timestamp

# ==============================================================================
# File conversion utilities
# ==============================================================================

def parquet_to_jsonl(parquet_path, jsonl_path):
    """Convert Parquet file to JSON Lines format"""
    print_dual(f"Converting {parquet_path.name} to JSONL...")

    df = pd.read_parquet(parquet_path)

    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            record = row.to_dict()
            # Convert timestamps to ISO format strings
            for key, val in record.items():
                if pd.isna(val):
                    record[key] = None
                elif isinstance(val, pd.Timestamp):
                    record[key] = val.isoformat()
            json.dump(record, f, ensure_ascii=False)
            f.write('\n')

    size_mb = jsonl_path.stat().st_size / (1024**2)
    print_dual(f"  Created {jsonl_path.name} ({size_mb:.1f} MB)")
    return df.shape[0]

def jsonl_to_parquet(jsonl_path, parquet_path):
    """Convert JSON Lines file to Parquet format"""
    print_dual(f"Converting {jsonl_path.name} to Parquet...")

    records = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                # Parse top5 JSON strings back to objects
                if 'top5_uncertainty' in record and isinstance(record['top5_uncertainty'], str):
                    record['top5_uncertainty'] = json.loads(record['top5_uncertainty'])
                if 'top5_negative' in record and isinstance(record['top5_negative'], str):
                    record['top5_negative'] = json.loads(record['top5_negative'])
                records.append(record)

    df = pd.DataFrame(records)

    # Ensure proper data types
    if 'total_word_tokens' in df.columns:
        df['total_word_tokens'] = df['total_word_tokens'].astype('int64')
    if 'Uncertainty_hits' in df.columns:
        df['Uncertainty_hits'] = df['Uncertainty_hits'].astype('int64')
    if 'Negative_hits' in df.columns:
        df['Negative_hits'] = df['Negative_hits'].astype('int64')
    if 'unc_pct' in df.columns:
        df['unc_pct'] = df['unc_pct'].astype('float64')
    if 'neg_pct' in df.columns:
        df['neg_pct'] = df['neg_pct'].astype('float64')

    df.to_parquet(parquet_path, index=False, engine='pyarrow', compression='snappy')

    size_mb = parquet_path.stat().st_size / (1024**2)
    print_dual(f"  Created {parquet_path.name} ({size_mb:.1f} MB, {len(df):,} rows)")
    return len(df)

# ==============================================================================
# C++ compilation and execution
# ==============================================================================

def compile_cpp_if_needed(paths):
    """Compile C++ executable if it doesn't exist"""
    if paths['cpp_exe'].exists():
        print_dual(f"C++ executable already exists: {paths['cpp_exe'].name}")
        return True

    if not paths['build_script'].exists():
        print_dual(f"ERROR: Build script not found: {paths['build_script']}")
        return False

    print_dual(f"Compiling C++ executable...")
    result = subprocess.run(
        [str(paths['build_script'])],
        cwd=paths['temp_dir'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print_dual(f"ERROR: Compilation failed!")
        print_dual(result.stdout)
        print_dual(result.stderr)
        return False

    print_dual(f"  Compilation successful")
    return True

def run_cpp_processing(paths, year, quarter):
    """Run C++ processing for a single year-quarter"""
    print_dual(f"  Running C++ processing for {year} Q{quarter}...")

    result = subprocess.run(
        [str(paths['cpp_exe']), str(year), str(quarter)],
        cwd=paths['temp_dir'],
        capture_output=True,
        text=True
    )

    # Print C++ output
    if result.stdout:
        for line in result.stdout.splitlines():
            print_dual(f"    [C++] {line}")

    if result.returncode != 0:
        print_dual(f"  ERROR: C++ processing failed for {year} Q{quarter}")
        if result.stderr:
            print_dual(f"  STDERR: {result.stderr}")
        return False

    return True

# ==============================================================================
# Main processing pipeline
# ==============================================================================

def safe_delete(path, retries=5, delay=1.0):
    """Safely delete a file with retries for Windows file locking"""
    if not path.exists():
        return True

    import time
    for i in range(retries):
        try:
            path.unlink()
            return True
        except PermissionError:
            if i < retries - 1:
                time.sleep(delay)
            else:
                print_dual(f"  WARNING: Could not delete {path.name} after {retries} retries")
                return False
    return False

def cleanup_orphaned_temp_files(temp_dir):
    """Clean up any orphaned temp files from previous interrupted runs"""
    print_dual("Pre-run cleanup: Checking for orphaned temp files...")

    # Patterns for temp files created by this script
    patterns = [
        'temp_docs_*.jsonl',
        'temp_output_*.jsonl',
        'temp_dict_*.jsonl'
    ]

    orphaned_files = []
    for pattern in patterns:
        orphaned_files.extend(temp_dir.glob(pattern))

    if not orphaned_files:
        print_dual("  No orphaned temp files found")
        return

    print_dual(f"  Found {len(orphaned_files)} orphaned temp file(s):")
    total_size = 0
    for temp_file in orphaned_files:
        file_size = temp_file.stat().st_size / (1024**2)  # MB
        total_size += file_size
        print_dual(f"    - {temp_file.name} ({file_size:.1f} MB)")

    print_dual(f"  Deleting {len(orphaned_files)} file(s) ({total_size:.1f} MB total)...")
    deleted_count = 0
    for temp_file in orphaned_files:
        if safe_delete(temp_file):
            deleted_count += 1

    print_dual(f"  Cleanup complete: {deleted_count}/{len(orphaned_files)} file(s) deleted")

def process_year_quarter_dataset(year, quarter, dataset, paths, config):
    """Process a single year-quarter-dataset: Parquet -> JSON -> C++ -> JSON -> Parquet"""
    # Define file paths
    docs_parquet = Path(paths['docs_pattern'].format(dataset=dataset, year=year))
    temp_docs_jsonl = paths['temp_dir'] / f"temp_docs_{year}_Q{quarter}.jsonl"
    temp_output_jsonl = paths['temp_dir'] / f"temp_output_{year}_Q{quarter}.jsonl"
    output_parquet = paths['output_dir'] / f"{dataset}_call_{year}_Q{quarter}.parquet"

    try:
        # Step 1: Check if docs exist for this year
        if not docs_parquet.exists():
            print_dual(f"  WARNING: Docs not found for {dataset}: {docs_parquet.name}")
            return None

        # Step 2: Load docs and filter by quarter
        df = pd.read_parquet(docs_parquet)
        if 'quarter' in df.columns:
            df_quarter = df[df['quarter'] == quarter]
        else:
            # If no quarter column, skip
            print_dual(f"  WARNING: No quarter column in {docs_parquet.name}")
            return None

        if len(df_quarter) == 0:
            print_dual(f"  No data for {dataset} {year} Q{quarter}")
            return 0

        # Step 3: Convert to JSONL
        df_quarter.to_json(temp_docs_jsonl, orient='records', lines=True)
        print_dual(f"  Loaded {len(df_quarter):,} documents for {dataset} {year} Q{quarter}")

        # Step 4: Run C++ processing
        success = run_cpp_processing(paths, year, quarter)

        # Step 5: Delete input JSONL immediately
        if safe_delete(temp_docs_jsonl):
            print_dual(f"  Deleted {temp_docs_jsonl.name}")

        if not success:
            return None

        # Step 6: Check if output exists
        if not temp_output_jsonl.exists():
            print_dual(f"  ERROR: C++ did not create output file")
            return None

        # Step 7: Convert output JSONL to Parquet
        doc_count = jsonl_to_parquet(temp_output_jsonl, output_parquet)

        # Step 8: Delete output JSONL immediately
        if safe_delete(temp_output_jsonl):
            print_dual(f"  Deleted {temp_output_jsonl.name}")

        print_dual(f"  [OK] {dataset} {year} Q{quarter} complete: {doc_count:,} documents")
        return doc_count

    except Exception as e:
        print_dual(f"  ERROR processing {dataset} {year} Q{quarter}: {e}")
        # Cleanup on error
        safe_delete(temp_docs_jsonl)
        safe_delete(temp_output_jsonl)
        return None

def aggregate_to_years(paths, year_start, year_end):
    """Aggregate quarter files into year files for each dataset"""
    print_dual(f"\n{'='*60}")
    print_dual("Aggregating quarters to years")
    print_dual(f"{'='*60}")

    for dataset in DATASETS:
        print_dual(f"\nDataset: {dataset}")
        for year in range(year_start, year_end + 1):
            year_dfs = []

            for quarter in range(1, 5):
                qfile = paths['output_dir'] / f"{dataset}_call_{year}_Q{quarter}.parquet"
                if qfile.exists():
                    df = pd.read_parquet(qfile)
                    year_dfs.append(df)

            if not year_dfs:
                print_dual(f"  No data for {year}, skipping")
                continue

            # Combine all quarters
            year_df = pd.concat(year_dfs, ignore_index=True)

            # Sort by file_name for determinism
            year_df = year_df.sort_values('file_name').reset_index(drop=True)

            # Write year file
            year_file = paths['output_dir'] / f"{dataset}_call_{year}.parquet"
            year_df.to_parquet(year_file, index=False, engine='pyarrow', compression='snappy')

            file_size_mb = year_file.stat().st_size / (1024**2)
            print_dual(f"  Created {dataset}_call_{year}.parquet: {len(year_df):,} docs ({file_size_mb:.1f} MB)")

            # Delete quarter files
            for quarter in range(1, 5):
                qfile = paths['output_dir'] / f"{dataset}_call_{year}_Q{quarter}.parquet"
                if qfile.exists():
                    qfile.unlink()

def process_quarter_wrapper(args):
    """Worker function to process a single quarter"""
    year, quarter, dataset, paths, config = args
    try:
        doc_count = process_year_quarter_dataset(year, quarter, dataset, paths, config)
        return (dataset, year, quarter, doc_count)
    except Exception as e:
        print(f"ERROR in worker {dataset} {year} Q{quarter}: {e}")
        return (dataset, year, quarter, None)

def main():
    """Main execution"""
    start_time = datetime.now()

    # Parse command-line arguments (optional year range override)
    if len(sys.argv) == 3:
        year_start = int(sys.argv[1])
        year_end = int(sys.argv[2])
    elif len(sys.argv) == 1:
        year_start = None
        year_end = None
    else:
        print("Usage: python 2.3a_TokenizeAndCount.py [YEAR_START YEAR_END]")
        sys.exit(1)

    # Load configuration
    config = load_config()
    paths, timestamp = setup_paths(config)

    # Use config values if not overridden
    if year_start is None:
        year_start = config['data']['year_start']
        year_end = config['data']['year_end']

    # Set up dual-write logging
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer

    print_dual("="*80)
    print_dual("STEP 2.3a: Tokenize and Count - Orchestrator (Multi-Dataset)")
    print_dual("="*80)
    print_dual(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_dual(f"Config: {config['project']['name']} v{config['project']['version']}")
    print_dual(f"Year range: {year_start}-{year_end}")
    print_dual(f"Datasets: {', '.join(DATASETS)}")
    print_dual(f"Log file: {paths['log_file']}")
    
    # Determine worker count
    cpu_count = multiprocessing.cpu_count()
    # Limit to 1 worker to avoid memory issues
    worker_count = 1
    print_dual(f"Parallel execution: {worker_count} workers")
    print_dual("")

    # Step 0: Clean up orphaned temp files from previous runs
    cleanup_orphaned_temp_files(paths['temp_dir'])
    print_dual("")

    # Step 1: Compile C++ if needed
    print_dual("Step 1: Checking C++ executable")
    if not compile_cpp_if_needed(paths):
        print_dual("\nFATAL: Could not compile C++ executable")
        sys.exit(1)
    print_dual("")

    # Step 2: Convert BOTH dictionaries to JSONL (once)
    print_dual("Step 2: Converting dictionaries to JSONL")
    temp_unc_dict_jsonl = paths['temp_dir'] / "temp_unc_dictionary.jsonl"
    temp_neg_dict_jsonl = paths['temp_dir'] / "temp_neg_dictionary.jsonl"

    unc_rows = parquet_to_jsonl(paths['unc_dictionary'], temp_unc_dict_jsonl)
    print_dual(f"  Loaded {unc_rows:,} Uncertainty tokens")

    neg_rows = parquet_to_jsonl(paths['neg_dictionary'], temp_neg_dict_jsonl)
    print_dual(f"  Loaded {neg_rows:,} Negative tokens")
    print_dual("")

    # Step 3: Process each dataset x year x quarter (Parallel)
    print_dual("Step 3: Processing dataset x year x quarters (Parallel)")

    # Prepare arguments
    worker_args = []
    for dataset in DATASETS:
        for year in range(year_start, year_end + 1):
            for quarter in range(1, 5):
                worker_args.append((year, quarter, dataset, paths, config))

    results = {d: {} for d in DATASETS}
    
    # Execute in parallel
    with multiprocessing.Pool(processes=worker_count) as pool:
        for dataset, year, quarter, doc_count in pool.imap_unordered(process_quarter_wrapper, worker_args):
            if doc_count is not None:
                if year not in results[dataset]:
                    results[dataset][year] = {}
                results[dataset][year][quarter] = doc_count

    # Step 4: Aggregate to year files
    aggregate_to_years(paths, year_start, year_end)

    # Step 5: Delete dictionary JSONLs
    print_dual(f"\n{'='*60}")
    print_dual("Cleanup")
    print_dual(f"{'='*60}")
    if temp_unc_dict_jsonl.exists():
        temp_unc_dict_jsonl.unlink()
        print_dual(f"Deleted {temp_unc_dict_jsonl.name}")
    if temp_neg_dict_jsonl.exists():
        temp_neg_dict_jsonl.unlink()
        print_dual(f"Deleted {temp_neg_dict_jsonl.name}")

    # Step 6: Update latest symlink
    print_dual("\nStep 6: Updating latest symlink")
    
    def remove_latest(path):
        if path.is_symlink() or path.exists():
            try:
                if path.is_symlink():
                    path.unlink()
                else:
                    shutil.rmtree(path)
            except Exception as e:
                print_dual(f"  WARNING: Failed to remove existing 'latest': {e}")

    remove_latest(paths['latest_dir'])

    # Create symlink (or copy on Windows if symlink fails)
    try:
        paths['latest_dir'].symlink_to(timestamp, target_is_directory=True)
        print_dual(f"  Created symlink: latest -> {timestamp}")
    except OSError:
        # Fallback to copy if symlink fails (common on Windows)
        remove_latest(paths['latest_dir'])
        try:
            shutil.copytree(paths['output_dir'], paths['latest_dir'])
            print_dual(f"  Created copy: latest")
        except Exception as e:
            print_dual(f"  ERROR: Could not create 'latest' copy: {e}")

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print_dual(f"\n{'='*80}")
    print_dual("SUMMARY")
    print_dual(f"{'='*80}")

    for dataset in DATASETS:
        total_docs = sum(sum(q.values()) for q in results[dataset].values() if q)
        years_processed = len(results[dataset])
        print_dual(f"\n{dataset.upper()}:")
        print_dual(f"  Total documents processed: {total_docs:,}")
        print_dual(f"  Years processed: {years_processed}/{year_end - year_start + 1}")

    print_dual(f"\nOutput directory: {paths['output_dir']}")
    print_dual(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_dual(f"Duration: {duration:.2f} seconds")
    print_dual("="*80)

    # Close log
    dual_writer.close()
    sys.stdout = dual_writer.terminal

if __name__ == "__main__":
    # Support for Windows multiprocessing
    multiprocessing.freeze_support()
    main()
