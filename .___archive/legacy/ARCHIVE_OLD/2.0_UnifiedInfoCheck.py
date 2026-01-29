#!/usr/bin/env python3
"""
Step: 2.0
Name: UnifiedInfoCheck
Inputs: 1_Inputs/Unified-info.parquet
Outputs: 4_Outputs/2.0_UnifiedInfoCheck/<timestamp>/unified_info_duplicate_file_names.csv
         4_Outputs/2.0_UnifiedInfoCheck/<timestamp>/report_step_00.md
Logs: 3_Logs/2.0_UnifiedInfoCheck/<timestamp>.log
Deterministic: True
Description: Unified Info sanity check & exact-row dedup detection

This script:
1. Loads Unified Info parquet
2. Identifies and removes exact duplicate rows (bit-for-bit identical)
3. Detects file_names with multiple non-identical rows
4. Reports which columns differ for non-identical duplicates
5. Generates comprehensive report with coverage statistics
"""

import os
import sys
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

import yaml
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


class DualWriter:
    """Write to both stdout and log file simultaneously (verbatim)."""

    def __init__(self, log_file_path: Path):
        self.terminal = sys.stdout
        self.log_file = open(log_file_path, 'w', encoding='utf-8')

    def write(self, message: str):
        """Write message to both stdout and log file."""
        self.terminal.write(message)
        self.log_file.write(message)
        self.flush()

    def flush(self):
        """Flush both streams."""
        self.terminal.flush()
        self.log_file.flush()

    def close(self):
        """Close log file."""
        self.log_file.close()


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load central configuration from YAML."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def compute_file_hash(file_path: Path, algorithm: str = 'sha256', chunk_size: int = 65536) -> str:
    """Compute hash of file for reproducibility."""
    hash_func = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def create_timestamped_output_dir(base_output_dir: Path) -> Tuple[Path, Path]:
    """Create timestamped output directory and latest symlink."""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    timestamped_dir = base_output_dir / timestamp
    latest_dir = base_output_dir / 'latest'

    # Create timestamped directory
    timestamped_dir.mkdir(parents=True, exist_ok=True)

    # Update latest symlink (remove old one if exists)
    if latest_dir.exists() or latest_dir.is_symlink():
        latest_dir.unlink()

    # Create new symlink (use relative path for portability)
    latest_dir.symlink_to(timestamp, target_is_directory=True)

    return timestamped_dir, latest_dir


def load_unified_info(unified_info_path: Path) -> pd.DataFrame:
    """Load Unified Info parquet."""
    print(f"Loading Unified Info from: {unified_info_path}")
    df = pd.read_parquet(unified_info_path)
    print(f"  Loaded {len(df):,} rows, {len(df.columns)} columns")
    print(f"  Columns: {', '.join(df.columns.tolist())}")
    return df


def remove_exact_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Remove exact duplicate rows (bit-for-bit identical across all columns).
    Keep first occurrence.

    Returns: (deduplicated dataframe, number of exact duplicates removed)
    """
    print("\nRemoving exact duplicate rows...")
    original_len = len(df)

    # Drop exact duplicates (keep first)
    df_deduped = df.drop_duplicates(keep='first').copy()

    duplicates_removed = original_len - len(df_deduped)
    print(f"  Original rows: {original_len:,}")
    print(f"  Exact duplicates removed: {duplicates_removed:,}")
    print(f"  Remaining rows: {len(df_deduped):,}")

    return df_deduped, duplicates_removed


def find_non_identical_duplicates(df: pd.DataFrame, max_sample: int = 1000) -> Tuple[pd.DataFrame, Dict[str, List[int]], List[str]]:
    """
    Find file_names with multiple non-identical rows.

    Returns:
    - DataFrame containing SAMPLE of rows for file_names with non-identical duplicates
    - Dictionary mapping SAMPLED file_name to list of row indices
    - List of ALL duplicate file_names (for counting purposes)
    """
    print("\nScanning for non-identical duplicate file_names...")

    # Group by file_name and count
    file_name_counts = df['file_name'].value_counts()

    # Find file_names with multiple rows
    all_duplicate_file_names = file_name_counts[file_name_counts > 1].index.tolist()

    print(f"  Unique file_names: {df['file_name'].nunique():,}")
    print(f"  file_names with >1 row: {len(all_duplicate_file_names):,}")

    if len(all_duplicate_file_names) == 0:
        print("  No non-identical duplicates found!")
        return pd.DataFrame(), {}, []

    # Take only a sample for detailed CSV (to avoid huge files and long processing)
    if len(all_duplicate_file_names) > max_sample:
        print(f"  Sampling first {max_sample:,} file_names for detailed CSV...")
        sampled_file_names = sorted(all_duplicate_file_names)[:max_sample]
    else:
        sampled_file_names = all_duplicate_file_names

    # Extract rows for SAMPLED file_names only
    duplicate_rows = df[df['file_name'].isin(sampled_file_names)].copy()

    # Sort by file_name for deterministic output
    duplicate_rows = duplicate_rows.sort_values('file_name').reset_index(drop=True)

    # Create mapping of file_name to row indices (for sampled ones only)
    file_name_to_indices = {}
    for file_name in sampled_file_names:
        indices = df[df['file_name'] == file_name].index.tolist()
        file_name_to_indices[file_name] = indices

    print(f"  Sampled {len(sampled_file_names):,} file_names for CSV")
    print(f"  Total rows in sampled duplicates: {len(duplicate_rows):,}")

    return duplicate_rows, file_name_to_indices, all_duplicate_file_names


def analyze_column_differences(df: pd.DataFrame, duplicate_file_names: List[str]) -> Dict[str, int]:
    """
    Analyze which columns vary across non-identical duplicates.

    Optimized version using groupby.

    Returns dictionary: column_name -> count of file_names where this column differs
    """
    print("\nAnalyzing column differences (optimized)...")

    # Filter to only duplicate file_names
    dup_df = df[df['file_name'].isin(duplicate_file_names)].copy()

    print(f"  Processing {len(dup_df):,} rows across {len(duplicate_file_names):,} file_names...")

    column_diff_counts = {}

    # For each column (except file_name), count how many file_names have >1 unique value
    for col in df.columns:
        if col == 'file_name':
            continue

        # Group by file_name and count unique values in this column
        unique_counts = dup_df.groupby('file_name')[col].nunique()

        # Count how many file_names have more than 1 unique value
        diff_count = (unique_counts > 1).sum()
        column_diff_counts[col] = diff_count

    # Sort by count descending
    sorted_diffs = dict(sorted(column_diff_counts.items(), key=lambda x: x[1], reverse=True))

    # Show top varying columns
    top_n = 10
    print(f"  Top {top_n} varying columns:")
    for i, (col, count) in enumerate(list(sorted_diffs.items())[:top_n]):
        if count > 0:
            print(f"    {i+1}. {col}: {count:,} file_names have differences")

    return sorted_diffs


def create_duplicate_report_csv(duplicate_rows: pd.DataFrame,
                                column_diffs: Dict[str, int],
                                output_path: Path):
    """
    Create CSV report of non-identical duplicates.

    For each file_name with duplicates, show all rows and indicate which columns differ.
    """
    print(f"\nCreating duplicate report CSV: {output_path}")

    if len(duplicate_rows) == 0:
        # Create empty CSV with headers
        empty_df = pd.DataFrame(columns=['file_name', 'row_num', 'notes'])
        empty_df.to_csv(output_path, index=False)
        print("  No duplicates to report - created empty CSV")
        return

    # Get file_names with duplicates
    duplicate_file_names = duplicate_rows['file_name'].unique()

    # Build report
    report_rows = []

    for file_name in sorted(duplicate_file_names):
        rows = duplicate_rows[duplicate_rows['file_name'] == file_name]

        # Identify differing columns for this file_name
        differing_cols = []
        for col in duplicate_rows.columns:
            if col == 'file_name':
                continue
            if rows[col].nunique() > 1:
                differing_cols.append(col)

        # Add all rows for this file_name
        for idx, row in rows.iterrows():
            report_row = row.to_dict()
            report_row['_row_num'] = idx
            report_row['_differing_columns'] = '; '.join(differing_cols) if differing_cols else 'NONE'
            report_row['_num_variants'] = len(rows)
            report_rows.append(report_row)

    # Create DataFrame
    report_df = pd.DataFrame(report_rows)

    # Reorder columns: metadata first, then original columns
    metadata_cols = ['_row_num', '_num_variants', '_differing_columns']
    original_cols = [col for col in report_df.columns if not col.startswith('_')]
    report_df = report_df[metadata_cols + original_cols]

    # Write CSV
    report_df.to_csv(output_path, index=False, encoding='utf-8')

    file_size = output_path.stat().st_size
    print(f"  Written {len(report_df):,} rows ({file_size:,} bytes)")
    print(f"  Covers {len(duplicate_file_names):,} file_names with non-identical duplicates")


def extract_year_from_date(df: pd.DataFrame) -> pd.DataFrame:
    """Extract year from start_date for coverage analysis."""
    df = df.copy()

    if 'start_date' in df.columns:
        # Try to parse start_date
        try:
            df['_year'] = pd.to_datetime(df['start_date'], errors='coerce').dt.year
        except:
            df['_year'] = None
    else:
        df['_year'] = None

    return df


def generate_report(config: Dict[str, Any],
                   unified_info_path: Path,
                   df_original: pd.DataFrame,
                   df_deduped: pd.DataFrame,
                   exact_duplicates_removed: int,
                   duplicate_file_names_count: int,
                   column_diffs: Dict[str, int],
                   input_hash: str,
                   csv_output_path: Path,
                   report_path: Path,
                   start_time: datetime,
                   end_time: datetime):
    """Generate comprehensive markdown report."""
    print(f"\nGenerating report: {report_path}")

    # Year coverage analysis
    df_with_year = extract_year_from_date(df_deduped)
    year_counts = df_with_year['_year'].value_counts().sort_index()

    # Top varying columns
    top_varying = [(col, count) for col, count in list(column_diffs.items())[:10] if count > 0]

    # Build report content
    report_content = f"""# STEP 00: Unified Info Check - Report

**Generated:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}
**Process Version:** {config['project']['version']}
**Script:** 2.0_UnifiedInfoCheck.py

---

## Summary

Performed sanity check on Unified Info dataset:
1. Removed exact duplicate rows (bit-for-bit identical)
2. Identified file_names with multiple non-identical rows
3. Analyzed which columns vary across duplicates

**Key Finding:** {duplicate_file_names_count:,} file_names have multiple non-identical rows

---

## Input

**File:** `{unified_info_path}`
**SHA-256:** `{input_hash}`
**Total rows:** {len(df_original):,}
**Columns:** {len(df_original.columns)}

### Column List:
{', '.join(df_original.columns.tolist())}

---

## Exact Duplicate Removal

| Metric | Count |
|--------|------:|
| Original rows | {len(df_original):,} |
| Exact duplicates removed | {exact_duplicates_removed:,} |
| Remaining rows | {len(df_deduped):,} |

**Note:** Exact duplicates are bit-for-bit identical across ALL columns. Only first occurrence was kept.

---

## Non-Identical Duplicate Detection

| Metric | Count |
|--------|------:|
| Unique file_names | {df_deduped['file_name'].nunique():,} |
| file_names with >1 row | {duplicate_file_names_count:,} |
| Percentage with duplicates | {(duplicate_file_names_count / df_deduped['file_name'].nunique() * 100):.2f}% |

---

## Column Variation Analysis

**Top 10 columns that differ across non-identical duplicates:**

| Rank | Column | file_names with differences |
|------|--------|----------------------------:|
"""

    if len(top_varying) > 0:
        for i, (col, count) in enumerate(top_varying, 1):
            report_content += f"| {i} | `{col}` | {count:,} |\n"
    else:
        report_content += "| - | No differences found | 0 |\n"

    report_content += f"""

**Note:** These columns have different values across rows with the same file_name.

---

## Year Coverage

Distribution of rows by year (extracted from start_date):

| Year | Row Count |
|------|----------:|
"""

    if len(year_counts) > 0:
        for year, count in year_counts.items():
            if pd.notna(year):
                report_content += f"| {int(year)} | {count:,} |\n"

        # Count missing years
        missing_year_count = df_with_year['_year'].isna().sum()
        if missing_year_count > 0:
            report_content += f"| (Missing/Invalid) | {missing_year_count:,} |\n"
    else:
        report_content += "| (No valid dates) | {len(df_deduped):,} |\n"

    report_content += f"""

---

## Outputs

**Duplicate Report CSV:** `{csv_output_path}`

The CSV contains a **sample** of rows for file_names with non-identical duplicates (limited to first 1,000 file_names for performance), with metadata columns:
- `_row_num`: Original row index
- `_num_variants`: Number of rows for this file_name
- `_differing_columns`: List of columns that differ

**Note:** Due to the large number of duplicates ({duplicate_file_names_count:,}), only a sample is included in the CSV. Full statistics are computed over all duplicates and reported above.

---

## Execution

**Start time:** {start_time.strftime('%Y-%m-%d %H:%M:%S')}
**End time:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}
**Duration:** {(end_time - start_time).total_seconds():.2f} seconds

---

## Determinism

- Configuration read from: `{config['project']['name']}`
- Sort order: By file_name (alphabetical)
- Duplicate handling: Keep first exact duplicate, report all non-identical duplicates

---

## Important Notes

1. **Exact duplicates removed:** {exact_duplicates_removed:,} rows were bit-for-bit identical and removed
2. **Non-identical duplicates NOT removed:** {duplicate_file_names_count:,} file_names have multiple rows with different data
3. **Downstream handling:** Steps 02 and 04 will use deterministic selection (first by validation_timestamp, then start_date)

---

**End of Report**
"""

    # Write report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"  Report written: {len(report_content):,} characters")


def main():
    """Main execution function."""
    # Record start time
    start_time = datetime.now()

    # Determine project root (parent of 2_Scripts)
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    # Load configuration
    config_path = project_root / 'config' / 'project.yaml'
    config = load_config(config_path)

    # Setup output and log directories
    step_name = config['step_00']['output_subdir']
    log_base_dir = project_root / config['paths']['logs'] / step_name
    output_base_dir = project_root / config['paths']['outputs'] / step_name

    log_base_dir.mkdir(parents=True, exist_ok=True)
    output_base_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped log file
    log_timestamp = start_time.strftime('%Y-%m-%d_%H%M%S')
    log_file_path = log_base_dir / f"{log_timestamp}.log"

    # Setup dual writer (stdout + log file)
    dual_writer = DualWriter(log_file_path)
    sys.stdout = dual_writer

    # Print header
    print("=" * 80)
    print(f"STEP 00: Unified Info Check")
    print(f"Process Version: {config['project']['version']}")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    print(f"\nProject root: {project_root}")
    print(f"Config loaded from: {config_path}")
    print(f"Log file: {log_file_path}")

    # Create timestamped output directory
    timestamped_output_dir, latest_output_dir = create_timestamped_output_dir(output_base_dir)
    print(f"Output directory: {timestamped_output_dir}")
    print(f"Latest symlink: {latest_output_dir}")

    # Define paths
    unified_info_path = project_root / config['paths']['unified_info']
    csv_filename = config['step_00']['outputs']['duplicate_report']
    report_filename = config['step_00']['outputs']['summary_report']

    csv_output_path = timestamped_output_dir / csv_filename
    report_path = timestamped_output_dir / report_filename

    # Check input file exists
    if not unified_info_path.exists():
        print(f"\nERROR: Input file not found: {unified_info_path}")
        sys.exit(1)

    # Compute input hash
    print(f"\nComputing input hash...")
    input_hash = compute_file_hash(
        unified_info_path,
        algorithm=config['hashing']['algorithm'],
        chunk_size=config['hashing']['chunk_size']
    )
    print(f"  Input SHA-256: {input_hash}")

    # Load Unified Info
    df_original = load_unified_info(unified_info_path)

    # Remove exact duplicates
    df_deduped, exact_duplicates_removed = remove_exact_duplicates(df_original)

    # Find non-identical duplicates
    duplicate_rows, file_name_to_indices, all_duplicate_file_names = find_non_identical_duplicates(df_deduped)
    duplicate_file_names_count = len(all_duplicate_file_names)  # Total count, not just sample

    # Analyze column differences (use ALL duplicates, not just sample)
    if duplicate_file_names_count > 0:
        column_diffs = analyze_column_differences(df_deduped, all_duplicate_file_names)
    else:
        column_diffs = {}

    # Create duplicate report CSV
    create_duplicate_report_csv(duplicate_rows, column_diffs, csv_output_path)

    # Record end time
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Generate report
    generate_report(
        config=config,
        unified_info_path=unified_info_path,
        df_original=df_original,
        df_deduped=df_deduped,
        exact_duplicates_removed=exact_duplicates_removed,
        duplicate_file_names_count=duplicate_file_names_count,
        column_diffs=column_diffs,
        input_hash=input_hash,
        csv_output_path=csv_output_path,
        report_path=report_path,
        start_time=start_time,
        end_time=end_time
    )

    # Print summary
    print("\n" + "=" * 80)
    print("STEP 00: COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"Duration: {duration:.2f} seconds")
    print(f"Exact duplicates removed: {exact_duplicates_removed:,}")
    print(f"file_names with non-identical duplicates: {duplicate_file_names_count:,}")
    print(f"Duplicate report CSV: {csv_output_path}")
    print(f"Summary report: {report_path}")
    print(f"Latest symlink: {latest_output_dir}")
    print(f"Log file: {log_file_path}")
    print("=" * 80)

    # Close dual writer
    dual_writer.close()
    sys.stdout = dual_writer.terminal


if __name__ == '__main__':
    main()
