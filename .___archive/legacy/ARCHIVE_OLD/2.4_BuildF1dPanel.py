#!/usr/bin/env python3
"""
==============================================================================
STEP 2.4: Build F1D Panel
==============================================================================
ID: 2.4_BuildF1dPanel
Description: Builds call-level F1D panel with metadata from Unified-info.
             No aggregation - keeps each call as a separate record with both
             start_date and business_quarter.
Inputs:
    - config/project.yaml
    - 1_Inputs/Unified-info.parquet
    - 4_Outputs/2.3_TokenizeAndCount/latest/{dataset}_call_YYYY.parquet (4 datasets × 17 years)
Outputs:
    - 4_Outputs/2.4_BuildF1dPanel/TIMESTAMP/{measure}_panel_YYYY.parquet (4 measures × 17 years)
      where measure ∈ {MaQaUnc, MaPresUnc, AnaQaUnc, EntireCallNeg}
    - 4_Outputs/2.4_BuildF1dPanel/TIMESTAMP/report_step_04.md
    - 4_Outputs/2.4_BuildF1dPanel/latest/ (symlink)
    - 3_Logs/2.4_BuildF1dPanel/TIMESTAMP.log
Deterministic: true
==============================================================================
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import yaml
import shutil
import hashlib

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
        'unified_info': root / '1_Inputs' / 'Unified-info.parquet',
        'tokenized_dir': root / '4_Outputs' / '2.3_TokenizeAndCount' / 'latest',
    }

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config['paths']['outputs'] / "2.4_BuildF1dPanel"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)

    paths['latest_dir'] = output_base / "latest"

    # Create log directory
    log_base = root / config['paths']['logs'] / "2.4_BuildF1dPanel"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}.log"

    return paths, timestamp

# ==============================================================================
# Utility functions
# ==============================================================================

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of file"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()

# ==============================================================================
# Duplicate handling
# ==============================================================================

def deduplicate_unified_info(unified_df):
    """
    Deduplicate Unified-info by file_name using deterministic sort.

    Strategy (matching Step 2.0 precedent):
    - Sort by: validation_timestamp DESC, start_date DESC
    - Keep first row per file_name (most recent metadata)
    - Track which file_names had duplicates
    """
    print_dual("\nDeduplicating Unified-info metadata...")

    original_count = len(unified_df)
    duplicate_file_names = set()

    # Identify duplicates
    duplicated_mask = unified_df.duplicated(subset=['file_name'], keep=False)
    if duplicated_mask.any():
        duplicate_file_names = set(unified_df[duplicated_mask]['file_name'].unique())
        print_dual(f"  Found {len(duplicate_file_names):,} file_names with duplicates")

    # Sort deterministically and keep first
    unified_df = unified_df.sort_values(
        by=['file_name', 'validation_timestamp', 'start_date'],
        ascending=[True, False, False]
    ).drop_duplicates(subset=['file_name'], keep='first').reset_index(drop=True)

    dedup_count = len(unified_df)
    print_dual(f"  Original rows: {original_count:,}")
    print_dual(f"  After deduplication: {dedup_count:,}")
    print_dual(f"  Rows removed: {original_count - dedup_count:,}")

    return unified_df, duplicate_file_names

# ==============================================================================
# Call-level panel construction (NO AGGREGATION)
# ==============================================================================

def build_measure_panel_for_year(measure_key, year, dataset_name, dict_name, tokenized_df, unified_df, duplicate_file_names):
    """
    Build call-level panel for a specific measure (dataset + dictionary combo).

    Args:
        measure_key: Measure identifier (e.g., 'MaQaUnc')
        year: Year being processed
        dataset_name: Dataset name (e.g., 'manager_qa')
        dict_name: Dictionary name ('Uncertainty' or 'Negative')
        tokenized_df: Tokenization output for this dataset
        unified_df: Deduplicated Unified-info metadata
        duplicate_file_names: Set of file_names with duplicate metadata

    Returns:
        Panel DataFrame with measure-specific columns
    """
    print_dual(f"\n  {measure_key} (year {year})...")
    print_dual(f"    Dataset: {dataset_name}, Dictionary: {dict_name}")
    print_dual(f"    Input calls: {len(tokenized_df):,}")

    # Sort by file_name for determinism
    df = tokenized_df.sort_values('file_name').reset_index(drop=True).copy()

    # Select dictionary-specific columns
    if dict_name == 'Uncertainty':
        hits_col = 'Uncertainty_hits'
        pct_col = 'unc_pct'
        top5_col = 'top5_uncertainty'
    else:  # Negative
        hits_col = 'Negative_hits'
        pct_col = 'neg_pct'
        top5_col = 'top5_negative'

    # Keep only relevant columns
    df = df[['file_name', 'start_date', 'total_word_tokens', hits_col, pct_col, 'process_version']].copy()

    # Rename to standardized measure column names
    df = df.rename(columns={
        hits_col: f'{dict_name}_hits',
        pct_col: f'{dict_name}_pct'
    })

    # Mark calls with duplicate metadata
    df['had_duplicate_metadata'] = df['file_name'].isin(duplicate_file_names)

    # Ensure file_name is clean for merging
    df['file_name'] = df['file_name'].astype(str).str.strip()
    unified_df['file_name'] = unified_df['file_name'].astype(str).str.strip()

    # LEFT JOIN with Unified-info
    panel = df.merge(
        unified_df[['file_name', 'permno', 'company_name', 'company_id', 'cusip',
                    'sedol', 'isin', 'company_ticker', 'business_quarter']],
        on='file_name',
        how='left'
    )

    # Check for missing metadata (failed join)
    # We check company_name because permno might be null for non-US firms
    missing_metadata = panel['company_name'].isna().sum()
    if missing_metadata > 0:
        print_dual(f"    WARNING: {missing_metadata:,} calls failed to match Unified-info")
    
    # Check for missing PERMNO specifically (informational)
    missing_permno = panel['permno'].isna().sum()
    if missing_permno > 0:
        print_dual(f"    INFO: {missing_permno:,} calls matched but have no PERMNO (likely non-US)")
    # Reorder columns
    panel = panel[[
        'file_name', 'start_date', 'business_quarter',
        'permno', 'company_name', 'company_id', 'cusip', 'sedol', 'isin', 'company_ticker',
        'total_word_tokens', f'{dict_name}_hits', f'{dict_name}_pct',
        'process_version', 'had_duplicate_metadata'
    ]]

    # Sort by file_name for determinism
    panel = panel.sort_values('file_name').reset_index(drop=True)

    print_dual(f"    Output panel rows: {len(panel):,}")

    # Validation
    assert len(panel) == len(df), f"Row count mismatch! Input: {len(df)}, Output: {len(panel)}"

    return panel

# ==============================================================================
# Report generation
# ==============================================================================

def generate_report(paths, measure_stats, measures, duplicate_file_names):
    """Generate markdown report for multi-measure call-level panels"""
    report_path = paths['output_dir'] / "report_step_04.md"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# STEP 04: Build Multi-Measure Panels - Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Script:** 2.4_BuildF1dPanel\n\n")
        f.write("---\n\n")

        f.write("## Summary\n\n")
        f.write("Built 4 call-level measure panels from 3 datasets × 2 dictionaries:\n\n")
        for measure_key, measure_config in measures.items():
            total_calls = sum(stats['calls'] for stats in measure_stats[measure_key].values())
            f.write(f"- **{measure_key}** ({measure_config['description']}): {total_calls:,} calls\n")

        f.write(f"\n**File_names with duplicate metadata:** {len(duplicate_file_names):,}\n\n")
        f.write("---\n\n")

        f.write("## Measures\n\n")
        f.write("| Measure | Dataset | Dictionary | Description |\n")
        f.write("|---------|---------|------------|-------------|\n")
        for measure_key, measure_config in measures.items():
            f.write(f"| {measure_key} | {measure_config['dataset']} | {measure_config['dictionary']} | {measure_config['description']} |\n")
        f.write("\n---\n\n")

        f.write("## Statistics by Measure\n\n")
        for measure_key in measures.keys():
            f.write(f"### {measure_key}\n\n")
            f.write("| Year | Calls | Avg Tokens | Avg Hits | Avg % | File Size (MB) |\n")
            f.write("|------|------:|-----------:|---------:|------:|---------------:|\n")

            for year in sorted(measure_stats[measure_key].keys()):
                stats = measure_stats[measure_key][year]
                f.write(f"| {year} | {stats['calls']:,} | {stats['avg_tokens']:.1f} | "
                       f"{stats['avg_hits']:.2f} | {stats['avg_pct']:.4f} | {stats['file_size_mb']:.1f} |\n")

            f.write("\n")

        f.write("---\n\n")

        f.write("## File Checksums (SHA-256)\n\n")
        for measure_key in measures.keys():
            f.write(f"### {measure_key}\n\n")
            for year in sorted(measure_stats[measure_key].keys()):
                f.write(f"**{measure_key}_panel_{year}.parquet:** `{measure_stats[measure_key][year]['sha256']}`\n\n")
            f.write("\n")

        f.write("---\n\n")

        f.write("## Processing Details\n\n")
        f.write("**Multi-Measure Architecture:**\n")
        f.write("- 3 datasets × 2 dictionaries = 4 specific measures\n")
        f.write("- Each measure: dataset-specific file + dictionary-specific columns\n")
        f.write(f"- Total outputs: {len(measures)} measures × {len(measure_stats[list(measures.keys())[0]])} years = {sum(len(stats) for stats in measure_stats.values())} files\n\n")

        f.write("**Duplicate Handling:**\n")
        f.write("- Sort by: (file_name, validation_timestamp DESC, start_date DESC)\n")
        f.write("- Keep: First row per file_name (most recent metadata)\n")
        f.write(f"- Duplicates found: {len(duplicate_file_names):,} file_names\n\n")

        f.write("**Panel Construction:**\n")
        f.write("- LEFT JOIN: {dataset}_call + Unified-info on file_name\n")
        f.write("- NO AGGREGATION: Each call is a separate record\n")
        f.write("- Dictionary selection: Uncertainty_hits/unc_pct OR Negative_hits/neg_pct\n")
        f.write("- Dropped: top5_matches (not needed for panel analysis)\n")
        f.write("- Schema: 15 columns (file_name, start_date, business_quarter, identifiers, metrics)\n\n")

        f.write("**Determinism:**\n")
        f.write("- Input sorting: tokenized data sorted by file_name\n")
        f.write("- Duplicate resolution: deterministic sort on timestamps\n")
        f.write("- Output sorting: panel sorted by file_name\n\n")

        f.write("---\n\n")
        f.write("**End of Report**\n")

    print_dual(f"\nReport generated: {report_path}")

# ==============================================================================
# Main execution
# ==============================================================================

def main():
    """Main execution"""
    start_time = datetime.now()

    # Load configuration
    config = load_config()
    paths, timestamp = setup_paths(config)

    # Set up dual-write logging
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer

    print_dual("="*80)
    print_dual("STEP 2.4: Build F1D Panel (Call-Level)")
    print_dual("="*80)
    print_dual(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_dual(f"Config: {config['project']['name']} v{config['project']['version']}")
    print_dual(f"Log file: {paths['log_file']}")
    print_dual("")

    # Step 1: Load and deduplicate Unified-info
    print_dual("Step 1: Loading Unified-info metadata")
    print_dual(f"  File: {paths['unified_info']}")

    unified_df = pd.read_parquet(paths['unified_info'])
    print_dual(f"  Loaded {len(unified_df):,} rows")

    unified_df, duplicate_file_names = deduplicate_unified_info(unified_df)

    # Step 2: Process each measure × year
    print_dual("\nStep 2: Building call-level panels by measure and year")
    year_start = config['data']['year_start']
    year_end = config['data']['year_end']

    measures = config['step_04']['measures']
    measure_stats = {measure_key: {} for measure_key in measures.keys()}

    for year in range(year_start, year_end + 1):
        print_dual(f"\n{'='*60}")
        print_dual(f"Year {year}")
        print_dual(f"{'='*60}")

        for measure_key, measure_config in measures.items():
            dataset_name = measure_config['dataset']
            dict_name = measure_config['dictionary']

            # Load dataset-specific tokenized file
            tokenized_file = paths['tokenized_dir'] / f"{dataset_name}_call_{year}.parquet"

            if not tokenized_file.exists():
                print_dual(f"\n  WARNING: Missing {tokenized_file.name}, skipping {measure_key} for year {year}")
                continue

            # Load tokenized data
            tokenized_df = pd.read_parquet(tokenized_file)

            # Build measure-specific panel
            panel = build_measure_panel_for_year(
                measure_key, year, dataset_name, dict_name,
                tokenized_df, unified_df, duplicate_file_names
            )

            # Write output
            output_file = paths['output_dir'] / f"{measure_key}_panel_{year}.parquet"
            panel.to_parquet(output_file, index=False, engine='pyarrow', compression='snappy')

            file_size_mb = output_file.stat().st_size / (1024**2)

            # Calculate statistics
            measure_stats[measure_key][year] = {
                'calls': len(panel),
                'avg_tokens': panel['total_word_tokens'].mean(),
                'avg_hits': panel[f'{dict_name}_hits'].mean(),
                'avg_pct': panel[f'{dict_name}_pct'].mean(),
                'file_size_mb': file_size_mb,
                'sha256': calculate_file_hash(output_file)
            }

            print_dual(f"    Created {measure_key}_panel_{year}.parquet ({file_size_mb:.1f} MB)")

    # Step 3: Generate report
    print_dual("\nStep 3: Generating report")
    generate_report(paths, measure_stats, measures, duplicate_file_names)

    # Step 4: Update latest symlink
    print_dual("\nStep 4: Updating latest symlink")
    if paths['latest_dir'].exists():
        if paths['latest_dir'].is_symlink():
            paths['latest_dir'].unlink()
        else:
            shutil.rmtree(paths['latest_dir'])

    # Create symlink (or copy on Windows if symlink fails)
    try:
        paths['latest_dir'].symlink_to(paths['output_dir'], target_is_directory=True)
        print_dual(f"  Created symlink: latest -> {paths['output_dir'].name}")
    except OSError:
        shutil.copytree(paths['output_dir'], paths['latest_dir'])
        print_dual(f"  Created copy: latest")

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print_dual(f"\n{'='*80}")
    print_dual("SUMMARY")
    print_dual(f"{'='*80}")

    for measure_key in measures.keys():
        total_calls = sum(stats['calls'] for stats in measure_stats[measure_key].values())
        years_processed = len(measure_stats[measure_key])
        print_dual(f"{measure_key}: {total_calls:,} calls, {years_processed}/{year_end - year_start + 1} years")

    print_dual(f"\nOutput directory: {paths['output_dir']}")
    print_dual(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_dual(f"Duration: {duration:.2f} seconds")
    print_dual("="*80)

    # Close log
    dual_writer.close()
    sys.stdout = dual_writer.terminal

if __name__ == "__main__":
    main()
