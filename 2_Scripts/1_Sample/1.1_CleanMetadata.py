#!/usr/bin/env python3
"""
==============================================================================
STEP 1.1: Clean Metadata & Event Filtering
==============================================================================
ID: 1.1_CleanMetadata
Description: Loads Unified-info, deduplicates exact rows, resolves file_name
             collisions, and filters for earnings calls (event_type='1') in
             the target date range (2002-2018).
             
Inputs:
    - 1_Inputs/Unified-info.parquet
    - config/project.yaml
    
Outputs:
    - 4_Outputs/1.1_CleanMetadata/{timestamp}/metadata_cleaned.parquet
    - 4_Outputs/1.1_CleanMetadata/{timestamp}/variable_reference.csv
    - 4_Outputs/1.1_CleanMetadata/{timestamp}/report_step_1_1.md
    - 3_Logs/1.1_CleanMetadata/{timestamp}.log
    
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
import importlib.util
import sys
from pathlib import Path

# Dynamic import for 1.5_Utils.py to comply with naming convention
# (Python modules cannot start with numbers, so we use importlib)
utils_path = Path(__file__).parent / "1.5_Utils.py"
spec = importlib.util.spec_from_file_location("utils", utils_path)
utils = importlib.util.module_from_spec(spec)
sys.modules["utils"] = utils
spec.loader.exec_module(utils)

from utils import generate_variable_reference, update_latest_symlink

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
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_paths(config):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    paths = {
        'root': root,
        'unified_info': root / '1_Inputs' / 'Unified-info.parquet',
    }

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_base = root / config['paths']['outputs'] / "1.1_CleanMetadata"
    paths['output_dir'] = output_base / timestamp
    paths['output_dir'].mkdir(parents=True, exist_ok=True)

    paths['latest_dir'] = output_base / "latest"

    # Create log directory
    log_base = root / config['paths']['logs'] / "1.1_CleanMetadata"
    log_base.mkdir(parents=True, exist_ok=True)
    paths['log_file'] = log_base / f"{timestamp}.log"

    return paths, timestamp

# Variable reference generation and symlink handling imported from step1_utils

# ==============================================================================
# Main processing
# ==============================================================================

def main():
    """Main processing function"""
    
    # Load config
    config = load_config()
    paths, timestamp = setup_paths(config)
    
    # Setup dual logging
    dual_writer = DualWriter(paths['log_file'])
    sys.stdout = dual_writer
    
    print_dual("="*80)
    print_dual("STEP 1.1: Clean Metadata & Event Filtering")
    print_dual("="*80)
    print_dual(f"Timestamp: {timestamp}")
    print_dual(f"Output Directory: {paths['output_dir']}")
    print_dual("")
    
    # Load Unified-info
    print_dual("Loading Unified-info.parquet...")
    df = pd.read_parquet(paths['unified_info'])
    original_count = len(df)
    print_dual(f"  Loaded {original_count:,} rows, {len(df.columns)} columns")
    
    # Deduplication: Exact duplicates
    print_dual("\nStep 1: Removing exact duplicate rows...")
    df_dedup = df.drop_duplicates()
    exact_dupes = original_count - len(df_dedup)
    print_dual(f"  Removed {exact_dupes:,} exact duplicate rows")
    print_dual(f"  Remaining: {len(df_dedup):,} rows")
    
    # Resolve file_name collisions
    print_dual("\nStep 2: Resolving file_name collisions...")
    collision_mask = df_dedup.duplicated(subset=['file_name'], keep=False)
    collisions = df_dedup[collision_mask].copy()
    
    if len(collisions) > 0:
        print_dual(f"  Found {collisions['file_name'].nunique():,} file_names with multiple rows")
        
        # Sort by validation_timestamp and keep first
        collisions_sorted = collisions.sort_values(['file_name', 'validation_timestamp'])
        keep_indices = collisions_sorted.groupby('file_name').head(1).index
        
        # Remove all collisions, then add back the kept ones
        df_clean = df_dedup[~collision_mask].copy()
        df_clean = pd.concat([df_clean, df_dedup.loc[keep_indices]], ignore_index=True)
        
        resolved = len(collisions) - len(keep_indices)
        print_dual(f"  Resolved {resolved:,} collision rows (kept earliest validation_timestamp)")
    else:
        df_clean = df_dedup.copy()
        print_dual("  No file_name collisions found")
    
    print_dual(f"  Remaining: {len(df_clean):,} rows")
    
    # Event Filter: event_type == '1'
    print_dual("\nStep 3: Filtering for earnings calls (event_type='1')...")
    if 'event_type' not in df_clean.columns:
        print_dual("  WARNING: 'event_type' column not found. Skipping event filter.")
        df_filtered = df_clean.copy()
    else:
        df_filtered = df_clean[df_clean['event_type'] == '1'].copy()
        removed = len(df_clean) - len(df_filtered)
        print_dual(f"  Removed {removed:,} non-earnings calls")
        print_dual(f"  Remaining: {len(df_filtered):,} rows")
    
    # Temporal Filter: 2002-2018
    print_dual("\nStep 4: Filtering for years 2002-2018...")
    year_start = config['data'].get('year_start', 2002)
    year_end = config['data'].get('year_end', 2018)
    
    df_filtered['start_date'] = pd.to_datetime(df_filtered['start_date'])
    df_filtered['year'] = df_filtered['start_date'].dt.year
    
    df_final = df_filtered[(df_filtered['year'] >= year_start) & (df_filtered['year'] <= year_end)].copy()
    removed = len(df_filtered) - len(df_final)
    print_dual(f"  Removed {removed:,} rows outside {year_start}-{year_end} range")
    print_dual(f"  Final count: {len(df_final):,} rows")
    
    # Drop temporary year column
    df_final = df_final.drop(columns=['year'])
    
    # Save output
    output_file = paths['output_dir'] / 'metadata_cleaned.parquet'
    df_final.to_parquet(output_file, index=False)
    print_dual(f"\nSaved cleaned metadata: {output_file}")
    
    # Generate variable reference
    var_ref_file = paths['output_dir'] / 'variable_reference.csv'
    generate_variable_reference(df_final, var_ref_file, print_dual)
    
    # Generate report
    report_lines = [
        "# Step 1.1: Clean Metadata & Event Filtering - Report",
        "",
        f"**Timestamp**: {timestamp}",
        "",
        "## Summary",
        "",
        f"- **Input rows**: {original_count:,}",
        f"- **Exact duplicates removed**: {exact_dupes:,}",
        f"- **Collision rows resolved**: {resolved if len(collisions) > 0 else 0:,}",
        f"- **Non-earnings calls removed**: {len(df_clean) - len(df_filtered) if 'event_type' in df_clean.columns else 0:,}",
        f"- **Out-of-range years removed**: {removed:,}",
        f"- **Final output rows**: {len(df_final):,}",
        "",
        "## Output Files",
        "",
        f"- Cleaned metadata: `{output_file.name}`",
        f"- Variable reference: `{var_ref_file.name}`",
        "",
        "## Columns",
        "",
        f"Total columns: {len(df_final.columns)}",
        "",
        "```",
        ", ".join(df_final.columns.tolist()),
        "```",
    ]
    
    report_file = paths['output_dir'] / 'report_step_1_1.md'
    report_file.write_text("\n".join(report_lines), encoding='utf-8')
    print_dual(f"Report saved: {report_file}")
    
    # Update latest symlink
    update_latest_symlink(paths['latest_dir'], paths['output_dir'], print_dual)
    
    print_dual("\n" + "="*80)
    print_dual("Step 1.1 completed successfully.")
    print_dual("="*80)
    
    # Restore stdout and close log
    sys.stdout = dual_writer.terminal
    dual_writer.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
