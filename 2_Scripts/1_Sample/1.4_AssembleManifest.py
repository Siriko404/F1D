#!/usr/bin/env python3
"""
==============================================================================
STEP 1.4: Manifest Assembly & CEO Filtering
==============================================================================
ID: 1.4_AssembleManifest
Description: Joins linked metadata with CEO tenure panel, filters for
             CEOs with minimum call threshold, and produces final manifest.
             
Inputs:
    - 4_Outputs/1.2_LinkEntities/latest/metadata_linked.parquet
    - 4_Outputs/1.3_BuildTenureMap/latest/tenure_monthly.parquet
    - config/project.yaml
    
Outputs:
    - 4_Outputs/1.4_AssembleManifest/{timestamp}/master_sample_manifest.parquet
    - 4_Outputs/1.4_AssembleManifest/{timestamp}/variable_reference.csv
    - 4_Outputs/1.4_AssembleManifest/{timestamp}/report_step_1_4.md
    - 3_Logs/1.4_AssembleManifest/{timestamp}.log
    
Deterministic: true
==============================================================================
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import yaml
import shutil
import importlib.util
import sys
from pathlib import Path

# Dynamic import for 1.5_Utils.py to comply with naming convention
try:
    utils_path = Path(__file__).parent / "1.5_Utils.py"
    spec = importlib.util.spec_from_file_location("utils", utils_path)
    utils = importlib.util.module_from_spec(spec)
    sys.modules["utils"] = utils
    spec.loader.exec_module(utils)
    from utils import generate_variable_reference, update_latest_symlink, get_latest_output_dir
except ImportError as e:
    print(f"Criticial Error importing utils: {e}")
    sys.exit(1)

# ==============================================================================
# Dual-write logging utility
# ==============================================================================

class DualWriter:
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
    print(msg, flush=True)

# ==============================================================================
# Configuration and setup
# ==============================================================================

def load_config():
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_paths(config):
    root = Path(__file__).parent.parent.parent
    
    # Use get_latest_output_dir to robustly find inputs even if symlinks are broken
    metadata_base = root / '4_Outputs' / '1.2_LinkEntities'
    tenure_base = root / '4_Outputs' / '1.3_BuildTenureMap'

    paths = {
        'root': root,
        'metadata': get_latest_output_dir(metadata_base, 'metadata_linked.parquet') / 'metadata_linked.parquet',
        'tenure': get_latest_output_dir(tenure_base, 'tenure_monthly.parquet') / 'tenure_monthly.parquet',
    }

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config['paths']['outputs'] / "1.4_AssembleManifest"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)

    paths['latest_dir'] = output_base / "latest"

    log_base = root / config['paths']['logs'] / "1.4_AssembleManifest"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}.log"

    return paths, timestamp

# Generate_variable_reference and update_latest_symlink imported from step1_utils

# ==============================================================================
# Main processing
# ==============================================================================

def main():
    config = load_config()
    paths, timestamp = setup_paths(config)
    
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer
    
    print_dual("="*80)
    print_dual("STEP 1.4: Manifest Assembly & CEO Filtering")
    print_dual("="*80)
    print_dual(f"Timestamp: {timestamp}\n")
    
    # Load inputs
    print_dual("Loading linked metadata...")
    metadata = pd.read_parquet(paths['metadata'])
    print_dual(f"  Loaded {len(metadata):,} calls\n")
    
    print_dual("Loading CEO tenure panel...")
    tenure = pd.read_parquet(paths['tenure'])
    print_dual(f"  Loaded {len(tenure):,} monthly CEO records")
    print_dual(f"  Unique firms: {tenure['gvkey'].nunique():,}")
    print_dual(f"  Unique CEOs: {tenure['ceo_id'].nunique():,}\n")
    
    # Prepare for join
    print_dual("Preparing data for join...")
    metadata['start_date'] = pd.to_datetime(metadata['start_date'])
    metadata['year'] = metadata['start_date'].dt.year
    metadata['month'] = metadata['start_date'].dt.month
    
    # Convert gvkey to string with 6-digit zero-padding for consistent join
    # Metadata gvkey is numeric (e.g., 3082), tenure gvkey is string with leading zeros ('001004')
    metadata['gvkey'] = metadata['gvkey'].apply(lambda x: str(int(x)).zfill(6) if pd.notna(x) else None)
    tenure['gvkey'] = tenure['gvkey'].astype(str).str.zfill(6)
    
    print_dual(f"  Metadata gvkey sample: {metadata['gvkey'].dropna().iloc[0]}")
    print_dual(f"  Tenure gvkey sample: {tenure['gvkey'].iloc[0]}")
    print_dual(f"  Metadata calls by year: {metadata['year'].min()}-{metadata['year'].max()}")
    print_dual(f"  Tenure panel by year: {tenure['year'].min()}-{tenure['year'].max()}\n")
    
    # Join on (gvkey, year, month)
    print_dual("Joining metadata with CEO tenure on (gvkey, year, month)...")
    merged = metadata.merge(
        tenure[['gvkey', 'year', 'month', 'ceo_id', 'ceo_name', 'prev_ceo_id', 'prev_ceo_name']],
        on=['gvkey', 'year', 'month'],
        how='left'
    )
    
    matched = merged['ceo_id'].notna().sum()
    unmatched = merged['ceo_id'].isna().sum()
    print_dual(f"  Matched: {matched:,} calls ({matched/len(merged)*100:.1f}%)")
    print_dual(f"  Unmatched: {unmatched:,} calls ({unmatched/len(merged)*100:.1f}%)\n")
    
    # Filter unmatched
    print_dual("Filtering out unmatched calls...")
    df_matched = merged[merged['ceo_id'].notna()].copy()
    print_dual(f"  Remaining: {len(df_matched):,} calls\n")
    
    # Apply minimum call threshold
    min_calls = config.get('step_02_5c', {}).get('min_calls_threshold', 5)
    print_dual(f"Applying minimum call threshold (>= {min_calls} calls per CEO)...")
    
    # Count calls per CEO
    ceo_counts = df_matched['ceo_id'].value_counts()
    valid_ceos = set(ceo_counts[ceo_counts >= min_calls].index)
    
    print_dual(f"  Total unique CEOs: {len(ceo_counts):,}")
    print_dual(f"  CEOs with >= {min_calls} calls: {len(valid_ceos):,}")
    print_dual(f"  CEOs dropped: {len(ceo_counts) - len(valid_ceos):,}\n")
    
    # Filter for valid CEOs
    df_final = df_matched[df_matched['ceo_id'].isin(valid_ceos)].copy()
    dropped_calls = len(df_matched) - len(df_final)
    print_dual(f"  Calls dropped: {dropped_calls:,}")
    print_dual(f"  Final manifest size: {len(df_final):,} calls\n")
    
    # Drop temporary columns
    df_final = df_final.drop(columns=['year', 'month'])
    
    # Sort for determinism
    df_final = df_final.sort_values('file_name').reset_index(drop=True)
    
    # Save output
    output_file = paths['output_dir'] / 'master_sample_manifest.parquet'
    df_final.to_parquet(output_file, index=False)
    print_dual(f"Saved master sample manifest: {output_file}")
    
    # Generate variable reference
    var_ref_file = paths['output_dir'] / 'variable_reference.csv'
    generate_variable_reference(df_final, var_ref_file, print_dual)
    
    # Generate summary report
    report_lines = [
        "# Step 1.4: Manifest Assembly & CEO Filtering - Report",
        "",
        f"**Timestamp**: {timestamp}",
        "",
        "## Summary",
        "",
        f"- **Input calls (linked metadata)**: {len(metadata):,}",
        f"- **Matched to CEO**: {matched:,} ({matched/len(metadata)*100:.1f}%)",
        f"- **Unmatched to CEO**: {unmatched:,} ({unmatched/len(metadata)*100:.1f}%)",
        f"- **Minimum call threshold**: {min_calls}",
        f"- **Valid CEOs**: {len(valid_ceos):,}",
        f"- **Dropped CEOs**: {len(ceo_counts) - len(valid_ceos):,}",
        f"- **Final manifest size**: {len(df_final):,} calls",
        "",
        "## CEO Distribution",
        "",
        f"- **Mean calls per CEO**: {df_final.groupby('ceo_id').size().mean():.1f}",
        f"- **Median calls per CEO**: {df_final.groupby('ceo_id').size().median():.0f}",
        f"- **Max calls (single CEO)**: {df_final.groupby('ceo_id').size().max():.0f}",
        "",
        "## Columns in Manifest",
        "",
        f"Total columns: {len(df_final.columns)}",
        "",
        "Key columns:",
        "- `file_name`: Unique call identifier",
        "- `gvkey`: Compustat firm identifier",
        "- `ceo_id`: Executive ID (execid)",
        "- `ceo_name`: CEO full name",
        "- `prev_ceo_id`: Previous CEO's execid",
        "- `prev_ceo_name`: Previous CEO's full name",
        "- `start_date`: Call date",
        "- `ff48_code`, `ff48_name`: Industry classification",
        "",
        "## Next Steps",
        "",
        "This manifest defines the **Universe of Analysis**. All text processing",
        "in Step 2 will be restricted to `file_name` values present in this manifest.",
    ]
    
    report_file = paths['output_dir'] / 'report_step_1_4.md'
    report_file.write_text("\n".join(report_lines), encoding='utf-8')
    print_dual(f"Report saved: {report_file}")
    
    # Update latest symlink
    update_latest_symlink(paths['latest_dir'], paths['output_dir'], print_dual)
    
    print_dual("\n" + "="*80)
    print_dual("Step 1.4 completed successfully.")
    print_dual("="*80)
    
    sys.stdout = dual_writer.terminal
    dual_writer.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
