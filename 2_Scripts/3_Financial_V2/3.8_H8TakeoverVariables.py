#!/usr/bin/env python3
"""
==============================================================================
STEP 3.8: H8 Takeover Variables
==============================================================================
ID: 3.8_H8TakeoverVariables
Description: Construct takeover target indicator for H8 (Speech Uncertainty ->
             Takeover Target Probability). Uses SDC Platinum M&A data.

Model Specification (H8):
    logit(P(Takeover_{t+1}=1)) = beta0 + beta1*Uncertainty_t + gamma*Controls

Hypothesis:
    H8a: beta1 > 0 (Higher uncertainty -> Higher takeover probability)

Inputs:
    - SDC Platinum M&A data (1_Inputs/SDC/sdc-ma-merged.parquet)
    - V2 speech uncertainty measures (from 4_Outputs/2_Textual_Analysis/)
    - V2 firm controls (from 4_Outputs/3_Financial_Features/)
    - Sample manifest (from 4_Outputs/1.4_AssembleManifest/)

Outputs:
    - 4_Outputs/3_Financial_V2/{timestamp}/H8_Takeover.parquet
    - 4_Outputs/3_Financial_V2/{timestamp}/stats.json

Deterministic: true
==============================================================================
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import yaml
import hashlib
import json
import time

# Add parent directory to sys.path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Import shared path validation utilities
from shared.path_utils import (
    validate_output_path,
    ensure_output_dir,
    validate_input_file,
    get_latest_output_dir,
)

# Import DualWriter from shared.observability_utils
from shared.observability_utils import (
    DualWriter,
    compute_file_checksum,
    print_stat,
    print_stats_summary,
    save_stats,
    get_process_memory_mb,
    calculate_throughput,
    detect_anomalies_zscore,
)

# ==============================================================================
# Configuration
# ==============================================================================

# H8 Takeover Variables Configuration
CONFIG = {
    'year_start': 2002,
    'year_end': 2018,
    'sdc_file': '1_Inputs/SDC/sdc-ma-merged.parquet',
    'min_firm_years': 3,
    'winsor_lower': 0.01,
    'winsor_upper': 0.99,
    # Takeover rate validation thresholds
    'takeover_rate_min': 0.005,  # 0.5% minimum annual takeover rate
    'takeover_rate_max': 0.05,   # 5% maximum annual takeover rate
    'min_takeover_events': 100,   # Minimum takeover events in sample
}

# Takeover type definitions
TAKEOVER_TYPES = {
    'primary': 'completed',     # Completed deals (primary)
    'announced': 'announced',   # Announced deals (robustness)
    'hostile': 'hostile',       # Hostile/unsolicited deals (robustness)
}

# M&A prediction literature control variables
MNA_CONTROL_VARS = [
    'size',          # Firm size (log assets or market cap)
    'leverage',      # Debt / Assets
    'roa',           # Return on Assets
    'mtb',           # Market-to-book ratio
    'liquidity',     # Current ratio or quick ratio
    'efficiency',    # Asset turnover (Sales / Assets)
    'stock_ret',     # Stock returns (abnormal returns)
    'rd_intensity',  # R&D / Assets (if available)
]

# ==============================================================================
# Path Setup
# ==============================================================================


def setup_paths(timestamp):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    # Resolve manifest directory using timestamp-based resolution
    try:
        manifest_dir = get_latest_output_dir(
            root / "4_Outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
    except Exception as e:
        # Fallback to 1.0_BuildSampleManifest
        manifest_dir = get_latest_output_dir(
            root / "4_Outputs" / "1.0_BuildSampleManifest",
            required_file="master_sample_manifest.parquet",
        )

    # Resolve textual analysis directory
    text_dir = get_latest_output_dir(
        root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
        required_file_pattern="linguistic_variables_",
    )

    # Resolve H7 illiquidity output (for base dataset with uncertainty measures)
    h7_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H7_Illiquidity.parquet",
    )

    paths = {
        "root": root,
        "manifest_dir": manifest_dir,
        "text_dir": text_dir,
        "h7_dir": h7_dir,
        "sdc_file": root / CONFIG['sdc_file'],
    }

    # Output directory
    output_base = root / "4_Outputs" / "3_Financial_V2"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "3_Financial_V2"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H8.log"

    return paths


# ==============================================================================
# CLI and Prerequisites
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments for 3.8_H8TakeoverVariables.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 3.8: H8 Takeover Variables

Construct takeover target indicator for H8 hypothesis testing.
Creates dependent variable (takeover target at t+1) and merges
with speech uncertainty measures and M&A control variables.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    return parser.parse_args()


def check_prerequisites(paths):
    """Validate all required inputs and prerequisite steps exist."""
    print("\nChecking prerequisites...")

    required_files = {
        "SDC M&A data": paths["sdc_file"],
        "Manifest": paths["manifest_dir"] / "master_sample_manifest.parquet",
        "H7 Illiquidity": paths["h7_dir"] / "H7_Illiquidity.parquet",
    }

    all_ok = True
    for name, path in required_files.items():
        if path.exists():
            print(f"  [OK] {name}: {path}")
        else:
            print(f"  [MISSING] {name}: {path}")
            all_ok = False

    return all_ok


# ==============================================================================
# Main
# ==============================================================================


def main():
    """Main execution"""
    args = parse_arguments()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    paths = setup_paths(timestamp)

    # Handle dry-run mode
    if args.dry_run:
        print("=" * 60)
        print("STEP 3.8: H8 Takeover Variables - DRY RUN")
        print(f"Timestamp: {timestamp}")
        print("=" * 60)

        prereq_ok = check_prerequisites(paths)
        if prereq_ok:
            print("\n[OK] All prerequisites validated")
            print("\nWould compute:")
            print("  - Takeover target indicator (completed deals)")
            print("  - Alternative takeover definitions (announced, hostile)")
            print("  - Forward-looking takeover indicator (t+1)")
            print("  - Merge with V2 uncertainty measures")
            print("  - M&A control variables from literature")
            print(f"\nOutput would be written to: {paths['output_dir']}")
            sys.exit(0)
        else:
            print("\n[ERROR] Prerequisites not met")
            sys.exit(1)

    # Check prerequisites before processing
    prereq_ok = check_prerequisites(paths)
    if not prereq_ok:
        print("\n[ERROR] Prerequisites not met. Exiting.")
        sys.exit(1)

    # Setup logging
    dual_writer = DualWriter(paths["log_file"])
    sys.stdout = dual_writer

    print("=" * 60)
    print("STEP 3.8: H8 Takeover Variables")
    print(f"Timestamp: {timestamp}")
    print("=" * 60)

    # Initialize statistics
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    mem_start = get_process_memory_mb()
    memory_readings = [mem_start["rss_mb"]]

    stats = {
        "step_id": "3.8_H8TakeoverVariables",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0},
        "processing": {
            "takeover_indicators": [],
            "winsorization": {},
            "missing_dropped": 0,
        },
        "output": {"final_rows": 0, "files": [], "checksums": {}},
        "variables": {},
        "takeover_stats": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
        "memory": {
            "start_mb": mem_start["rss_mb"],
            "end_mb": 0.0,
            "peak_mb": 0.0,
            "delta_mb": 0.0,
        },
    }

    print("\n[TODO] Implementation continues in next tasks...")
    print("This is Task 1: Script header and setup")

    # Close logging
    dual_writer.close()
    sys.stdout = dual_writer.terminal


if __name__ == "__main__":
    main()
