#!/usr/bin/env python3
"""
==============================================================================
STEP 2.2v2e: Re-sort Documents by Actual Year
==============================================================================
ID: 2.2v2e_ResortByYear
Description: Reads all dataset year files, re-sorts records into correct
             year files based on actual year column values.
             Drops year/quarter columns in final output.
Inputs:
    - 4_Outputs/2.2_ExtractFilteredDocs/latest/{dataset}_docs_YYYY.parquet
      (3 datasets: manager_qa, manager_pres, analyst_qa)
Outputs:
    - 4_Outputs/2.2_ExtractFilteredDocs/latest/{dataset}_docs_YYYY.parquet
      (overwritten with correctly sorted data)
Output Schema: file_name, doc_text, approx_char_len, start_date
Deterministic: true
==============================================================================
"""

import sys
from pathlib import Path
import pandas as pd
import yaml

def load_config():
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent / "config" / "project.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def resort_dataset_by_year(dataset_name, output_dir, year_start, year_end):
    """Re-sort all records for one dataset by actual year"""
    print(f"\n{'='*70}")
    print(f"Processing dataset: {dataset_name}")
    print(f"{'='*70}")

    # Step 1: Read all year files for this dataset
    print("\nStep 1: Loading all year files...")
    all_dfs = []
    total_rows = 0

    for year in range(year_start, year_end + 1):
        year_file = output_dir / f"{dataset_name}_docs_{year}.parquet"
        if year_file.exists():
            df = pd.read_parquet(year_file)
            all_dfs.append(df)
            total_rows += len(df)
            print(f"  Loaded {year}: {len(df):,} documents")
        else:
            print(f"  WARNING: Missing {year_file.name}")

    if not all_dfs:
        print(f"ERROR: No data files found for {dataset_name}")
        return

    # Step 2: Concatenate all data
    print(f"\nStep 2: Concatenating all data ({total_rows:,} total documents)")
    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"  Combined shape: {combined.shape}")

    # Check if files have year column
    has_year_column = 'year' in combined.columns

    if has_year_column:
        # Step 3: Check for year mismatches (only if year column exists)
        print("\nStep 3: Checking year distribution...")
        year_counts_before = {}
        for year in range(year_start, year_end + 1):
            count = len(combined[combined['year'] == year])
            if count > 0:
                year_counts_before[year] = count
                print(f"  Year {year}: {count:,} documents")
    else:
        print(f"\nDataset {dataset_name}: No year column (already sorted by year)")
        print(f"Will add quarter column from start_date for downstream compatibility")
        year_counts_before = {}

    # Step 4: Delete old year files
    print("\nStep 4: Deleting old year files...")
    deleted_count = 0
    for year in range(year_start, year_end + 1):
        year_file = output_dir / f"{dataset_name}_docs_{year}.parquet"
        if year_file.exists():
            year_file.unlink()
            deleted_count += 1
    print(f"  Deleted {deleted_count} old files")

    # Step 5: Group by actual year and write new files
    print("\nStep 5: Writing corrected year files...")
    year_counts_after = {}

    # If no year column, derive year from start_date for grouping
    if not has_year_column:
        combined['year'] = combined['start_date'].str[:4].astype(int)

    for year, group in combined.groupby('year', sort=True):
        # Sort by file_name for determinism
        group_sorted = group.sort_values('file_name').reset_index(drop=True)

        # Re-derive quarter from start_date for downstream compatibility
        # Parse start_date string (format: "YYYY-MM-DD..." or "YYYY-MM-DDTHH:MM:SS")
        group_sorted['quarter'] = group_sorted['start_date'].str[5:7].astype(int).map({
            1: 1, 2: 1, 3: 1,      # Q1: Jan-Mar
            4: 2, 5: 2, 6: 2,      # Q2: Apr-Jun
            7: 3, 8: 3, 9: 3,      # Q3: Jul-Sep
            10: 4, 11: 4, 12: 4    # Q4: Oct-Dec
        })

        # Keep core data + quarter column (needed by Step 2.3)
        group_sorted = group_sorted[['file_name', 'doc_text', 'approx_char_len', 'start_date', 'quarter']]

        # Write parquet
        output_path = output_dir / f"{dataset_name}_docs_{year}.parquet"
        group_sorted.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')

        file_size_mb = output_path.stat().st_size / (1024**2)
        year_counts_after[year] = len(group_sorted)
        print(f"  Written {year}: {len(group_sorted):,} docs ({file_size_mb:.1f} MB)")

    # Step 6: Validation
    print("\nStep 6: Validation...")
    total_after = sum(year_counts_after.values())
    if total_after == total_rows:
        print(f"  [OK] Row count matches: {total_after:,}")
    else:
        print(f"  [ERROR] Row count mismatch!")
        print(f"    Before: {total_rows:,}")
        print(f"    After:  {total_after:,}")
        sys.exit(1)

    # Check for year migrations
    print("\nYear migrations detected:")
    for year in sorted(set(year_counts_before.keys()) | set(year_counts_after.keys())):
        before = year_counts_before.get(year, 0)
        after = year_counts_after.get(year, 0)
        if before != after:
            delta = after - before
            sign = "+" if delta > 0 else ""
            print(f"  {year}: {before:,} -> {after:,} ({sign}{delta:,})")

    print(f"\n{'='*70}")
    print(f"Dataset {dataset_name} complete: {total_after:,} documents")
    print(f"{'='*70}")

def main():
    """Main entry point"""
    print("="*70)
    print("STEP 2.2v2e: Re-sort Documents by Actual Year")
    print("="*70)

    # Load config
    config = load_config()
    year_start = config['data']['year_start']
    year_end = config['data']['year_end']

    # Get output directory
    root = Path(__file__).parent.parent
    output_dir = root / config['paths']['outputs'] / "2.2_ExtractFilteredDocs" / "latest"

    if not output_dir.exists():
        print(f"ERROR: Output directory not found: {output_dir}")
        sys.exit(1)

    print(f"\nOutput directory: {output_dir}")
    print(f"Year range: {year_start}-{year_end}")

    # Process each dataset
    datasets = ['manager_qa', 'manager_pres', 'analyst_qa']

    for dataset in datasets:
        resort_dataset_by_year(dataset, output_dir, year_start, year_end)

    print("\n" + "="*70)
    print("ALL DATASETS COMPLETE")
    print("="*70)
    print("\nAll documents have been re-sorted by actual year.")
    print("Year and quarter columns have been dropped from output files.")

if __name__ == "__main__":
    main()
