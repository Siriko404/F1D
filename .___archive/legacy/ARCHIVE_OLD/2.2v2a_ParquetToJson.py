#!/usr/bin/env python3
"""
==============================================================================
STEP 2.2v2a: Parquet to JSON Conversion & C++ Orchestration (Multi-Dataset)
==============================================================================
ID: 2.2v2a_ParquetToJson
Description: Converts Parquet files to JSON Lines format, orchestrates C++
             processing for 3 datasets, converts output back to Parquet
Inputs:
    - config/project.yaml
    - 1_Inputs/Unified-info.parquet
    - 1_Inputs/speaker_data_YYYY.parquet (Y=2002-2018)
Outputs:
    - 4_Outputs/2.2_ExtractFilteredDocs/TIMESTAMP/{dataset_type}_docs_YYYY.parquet
      (3 datasets: manager_qa, manager_pres, analyst_qa)
    - 4_Outputs/2.2_ExtractFilteredDocs/latest/ (symlink)
    - 3_Logs/2.2_ExtractFilteredDocs/TIMESTAMP.log
Deterministic: true
==============================================================================
"""

import sys
import os
import json
import hashlib
import subprocess
import time
import multiprocessing
from pathlib import Path
from datetime import datetime
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
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
        'unified_info': root / config['paths']['unified_info'],
        'speaker_pattern': str(root / config['paths']['speaker_data_pattern']),
        'cpp_exe': root / '2_Scripts' / '2.2v2b_ProcessManagerDocs.exe',
        'build_script': root / '2_Scripts' / '2.2v2b_Build.bat',
        'temp_dir': root / '2_Scripts',
    }

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config['paths']['outputs'] / "2.2_ExtractFilteredDocs"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)

    paths['latest_dir'] = output_base / "latest"

    # Create log directory
    log_base = root / config['paths']['logs'] / "2.2_ExtractFilteredDocs"
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
            # Convert to dict, handle datetime conversion
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

def jsonl_to_parquet(jsonl_path, parquet_path, schema=None):
    """Convert JSON Lines file to Parquet format"""
    print_dual(f"Converting {jsonl_path.name} to Parquet...")

    records = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    df = pd.DataFrame(records)

    # Ensure proper data types for output
    if 'approx_char_len' in df.columns:
        df['approx_char_len'] = df['approx_char_len'].astype('int64')
    if 'year' in df.columns:
        df['year'] = df['year'].astype('int64')

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

def run_cpp_processing(paths, year, dataset_type):
    """Run C++ processing for a single year and dataset type"""
    print_dual(f"  Running C++ processing for {year} ({dataset_type})...")

    result = subprocess.run(
        [str(paths['cpp_exe']), str(year), dataset_type],
        cwd=paths['temp_dir'],
        capture_output=True,
        text=True
    )

    # Print C++ output
    if result.stdout:
        for line in result.stdout.splitlines():
            print_dual(f"    [C++] {line}")

    if result.returncode != 0:
        print_dual(f"  ERROR: C++ processing failed for {year} ({dataset_type})")
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
        'temp_speaker_*.jsonl',
        'temp_output_*.jsonl',
        'temp_unified_info.jsonl'
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

def process_year_dataset(year, dataset_type, paths, speaker_jsonl_exists):
    """Process a single year-dataset combination"""
    # Define file paths
    speaker_parquet = Path(paths['speaker_pattern'].format(year=year))
    temp_speaker_jsonl = paths['temp_dir'] / f"temp_speaker_{year}.jsonl"
    temp_output_jsonl = paths['temp_dir'] / f"temp_output_{year}_{dataset_type}.jsonl"
    output_parquet = paths['output_dir'] / f"{dataset_type}_docs_{year}.parquet"

    try:
        # Step 1: Convert speaker data Parquet to JSONL (only if not already done)
        if not speaker_jsonl_exists:
            if not speaker_parquet.exists():
                print_dual(f"  WARNING: Speaker data not found: {speaker_parquet}")
                return None, False

            rows = parquet_to_jsonl(speaker_parquet, temp_speaker_jsonl)
            print_dual(f"  Loaded {rows:,} speaker turns")
            speaker_jsonl_exists = True

        # Step 2: Run C++ processing
        success = run_cpp_processing(paths, year, dataset_type)

        if not success:
            return None, speaker_jsonl_exists

        # Step 3: Check if output exists
        if not temp_output_jsonl.exists():
            print_dual(f"  ERROR: C++ did not create output file")
            return None, speaker_jsonl_exists

        # Step 4: Convert output JSONL to Parquet
        doc_count = jsonl_to_parquet(temp_output_jsonl, output_parquet)

        # Step 5: Delete output JSONL immediately
        if safe_delete(temp_output_jsonl):
            print_dual(f"  Deleted {temp_output_jsonl.name}")

        print_dual(f"  [OK] {dataset_type} ({year}): {doc_count:,} documents")
        return doc_count, speaker_jsonl_exists

    except Exception as e:
        print_dual(f"  ERROR processing {dataset_type} ({year}): {e}")
        # Cleanup output JSONL on error
        safe_delete(temp_output_jsonl)
        return None, speaker_jsonl_exists

def process_year_all_datasets(args):
    """Worker function to process all datasets for a single year"""
    year, paths, datasets = args
    
    print(f"Starting Year {year}...")
    
    results = {}
    temp_speaker_jsonl = paths['temp_dir'] / f"temp_speaker_{year}.jsonl"
    speaker_jsonl_exists = False
    
    try:
        # Process all datasets for this year
        for dataset_type in datasets:
            # We pass False for speaker_jsonl_exists initially, and it returns True if it created it
            # Subsequent calls will reuse it
            doc_count, speaker_jsonl_exists = process_year_dataset(
                year, dataset_type, paths, speaker_jsonl_exists
            )
            if doc_count is not None:
                results[dataset_type] = doc_count
                
        # Delete speaker JSONL after all datasets processed
        if temp_speaker_jsonl.exists():
            safe_delete(temp_speaker_jsonl)
            print(f"  Deleted {temp_speaker_jsonl.name}")
            
        print(f"Finished Year {year}")
        return year, results
        
    except Exception as e:
        print(f"ERROR in Year {year}: {e}")
        if temp_speaker_jsonl.exists():
            safe_delete(temp_speaker_jsonl)
        return year, {}

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
        print("Usage: python 2.2v2a_ParquetToJson.py [YEAR_START YEAR_END]")
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
    print_dual("STEP 2.2v2a: Multi-Dataset Parquet to JSON Conversion & C++ Orchestration")
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

    # Step 2: Convert Unified Info to JSONL (once)
    print_dual("Step 2: Converting Unified Info to JSONL")
    temp_unified_jsonl = paths['temp_dir'] / "temp_unified_info.jsonl"
    unified_rows = parquet_to_jsonl(paths['unified_info'], temp_unified_jsonl)
    print_dual(f"  Loaded {unified_rows:,} unified info rows")
    print_dual("")

    # Step 3: Process each year for each dataset (Parallel)
    print_dual("Step 3: Processing datasets x years (Parallel)")

    # Prepare arguments for workers
    years = list(range(year_start, year_end + 1))
    worker_args = [(year, paths, DATASETS) for year in years]
    
    # Results: {dataset_type: {year: doc_count}}
    results = {dataset: {} for dataset in DATASETS}

    # Execute in parallel
    with multiprocessing.Pool(processes=worker_count) as pool:
        for year, year_results in pool.imap_unordered(process_year_all_datasets, worker_args):
            for dataset, count in year_results.items():
                results[dataset][year] = count

    # Step 4: Delete Unified Info JSONL
    print_dual(f"\n{'='*60}")
    print_dual("Cleanup")
    print_dual(f"{'='*60}")
    if temp_unified_jsonl.exists():
        safe_delete(temp_unified_jsonl)
        print_dual(f"Deleted {temp_unified_jsonl.name}")

    # Step 5: Update latest symlink
    print_dual(f"\nStep 5: Updating latest symlink")
    
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

    total_docs = 0
    for dataset in DATASETS:
        dataset_total = sum(results[dataset].values())
        total_docs += dataset_total
        print_dual(f"\n{dataset}:")
        print_dual(f"  Total documents: {dataset_total:,}")
        print_dual(f"  Years processed: {len(results[dataset])}/{year_end - year_start + 1}")
        if results[dataset]:
            print_dual(f"  Per-year counts:")
            for year in sorted(results[dataset].keys()):
                print_dual(f"    {year}: {results[dataset][year]:,}")

    print_dual(f"\nOverall:")
    print_dual(f"  Total documents across all datasets: {total_docs:,}")
    print_dual(f"  Output directory: {paths['output_dir']}")
    print_dual(f"  End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_dual(f"  Duration: {duration:.1f} seconds")
    print_dual("="*80)

    # Close log
    dual_writer.close()
    sys.stdout = dual_writer.terminal

if __name__ == "__main__":
    # Support for Windows multiprocessing
    multiprocessing.freeze_support()
    main()
