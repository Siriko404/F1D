#!/usr/bin/env python3
"""
==============================================================================
STEP 2.2v2d: Re-sort Documents by Year-Quarter
==============================================================================
ID: 2.2v2d_ResortByYearQuarter
Description: Reads all year-based output files, re-sorts records into correct
             year-quarter files based on actual year and quarter values.
             Drops year/quarter columns in final output.
Inputs:
    - 4_Outputs/2.2v2_ExtractQaManagerDocs/TIMESTAMP/qa_manager_docs_YYYY.parquet
Outputs:
    - 4_Outputs/2.2v2_ExtractQaManagerDocs/TIMESTAMP/qa_manager_docs_YYYY_QX.parquet
Output Schema: file_name, doc_text, approx_char_len, start_date
Deterministic: true
==============================================================================
"""

import sys
import os
from pathlib import Path
import pandas as pd
import yaml

def load_config():
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent / "config" / "project.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def resort_by_year_quarter(output_dir):
    """Re-sort all documents into year-quarter files"""
    print("="*60)
    print("Re-sorting documents by year-quarter")
    print("="*60)

    config = load_config()
    year_start = config['data']['year_start']
    year_end = config['data']['year_end']

    # Step 1: Read all year-based files
    print("\nStep 1: Reading all year-based output files")
    all_dfs = []
    total_rows = 0

    for year in range(year_start, year_end + 1):
        year_file = output_dir / f"qa_manager_docs_{year}.parquet"
        if year_file.exists():
            df = pd.read_parquet(year_file)
            all_dfs.append(df)
            total_rows += len(df)
            print(f"  Loaded {year}: {len(df):,} documents")
        else:
            print(f"  WARNING: Missing {year_file.name}")

    if not all_dfs:
        print("ERROR: No data files found")
        sys.exit(1)

    # Step 2: Concatenate all data
    print(f"\nStep 2: Concatenating all data ({total_rows:,} total documents)")
    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"  Combined shape: {combined.shape}")

    # Step 3: Group by year-quarter and write files
    print("\nStep 3: Writing year-quarter files")

    year_quarter_counts = {}
    for (year, quarter), group in combined.groupby(['year', 'quarter'], sort=True):
        output_path = output_dir / f"qa_manager_docs_{year}_Q{quarter}.parquet"

        # Sort by file_name for determinism
        group_sorted = group.sort_values('file_name').reset_index(drop=True)

        # Drop year and quarter columns - keep only file_name, doc_text, approx_char_len, start_date
        group_sorted = group_sorted[['file_name', 'doc_text', 'approx_char_len', 'start_date']]

        # Write parquet
        group_sorted.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')

        file_size_mb = output_path.stat().st_size / (1024**2)
        year_quarter_counts[(year, quarter)] = len(group_sorted)
        print(f"  Created {year}_Q{quarter}: {len(group_sorted):,} docs ({file_size_mb:.1f} MB)")

    # Step 4: Delete old year-only files
    print("\nStep 4: Deleting old year-only files")
    deleted_count = 0
    for year in range(year_start, year_end + 1):
        year_file = output_dir / f"qa_manager_docs_{year}.parquet"
        if year_file.exists():
            year_file.unlink()
            deleted_count += 1
            print(f"  Deleted: qa_manager_docs_{year}.parquet")

    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"Total documents: {total_rows:,}")
    print(f"Year-quarter files created: {len(year_quarter_counts)}")
    print(f"Old year-only files deleted: {deleted_count}")

    # Check for year mismatches
    print(f"\nYear-quarter distribution:")
    for year in range(year_start, year_end + 1):
        year_total = sum(count for (y, q), count in year_quarter_counts.items() if y == year)
        if year_total > 0:
            quarters_str = ", ".join([f"Q{q}: {year_quarter_counts.get((year, q), 0):,}"
                                     for q in range(1, 5) if (year, q) in year_quarter_counts])
            print(f"  {year}: {year_total:,} total ({quarters_str})")

    print("="*60)
    print("Re-sorting complete")
    print("="*60)

if __name__ == "__main__":
    # Get output directory from command line or use latest
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
    else:
        root = Path(__file__).parent.parent
        config = load_config()
        latest_dir = root / config['paths']['outputs'] / "2.2v2_ExtractQaManagerDocs" / "latest"
        if not latest_dir.exists():
            print("ERROR: Latest directory not found")
            sys.exit(1)
        output_dir = latest_dir

    resort_by_year_quarter(output_dir)
