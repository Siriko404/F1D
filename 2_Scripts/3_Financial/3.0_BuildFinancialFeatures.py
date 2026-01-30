#!/usr/bin/env python3
"""
==============================================================================
STEP 3: Build Financial Features (Orchestrator)
==============================================================================
Coordinates 3.1, 3.2, 3.3 to write ALL outputs to a single timestamped folder.

Note: MemoryAwareThrottler from shared/chunked_reader.py is available for future
      chunked processing. Current implementation uses column pruning for memory optimization.
==============================================================================
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import yaml
import pandas as pd
import numpy as np
import importlib.util
import hashlib
import time
import json
import psutil

# Dynamic import for 3.4_Utils.py
utils_path = Path(__file__).parent / "3.4_Utils.py"
spec = importlib.util.spec_from_file_location("utils", utils_path)
utils = importlib.util.module_from_spec(spec)
sys.modules["utils"] = utils
spec.loader.exec_module(utils)

from utils import DualWriter, generate_variable_reference

try:
    from shared.path_utils import (
        validate_output_path,
        ensure_output_dir,
        validate_input_file,
        get_latest_output_dir,
    )
except ImportError:
    # Fallback if shared/__init__.py hasn't run yet
    from shared.path_utils import (
        validate_output_path,
        ensure_output_dir,
        validate_input_file,
        get_latest_output_dir,
    )

# ==============================================================================
# Stats Helper Functions
# ==============================================================================


# ==============================================================================
# Observability Helper Functions
# ==============================================================================


def get_process_memory_mb():
    """
    Get current process memory usage in MB.

    Returns:
        Dict with keys:
        - rss_mb: Resident Set Size (actual physical memory in use)
        - vms_mb: Virtual Memory Size (total memory allocated)
        - percent: Memory usage as percentage of system memory
    """
    process = psutil.Process()
    mem_info = process.memory_info()
    mem_percent = process.memory_percent()

    return {
        "rss_mb": mem_info.rss / (1024 * 1024),
        "vms_mb": mem_info.vms / (1024 * 1024),
        "percent": mem_percent,
    }


def calculate_throughput(rows_processed, duration_seconds):
    """
    Calculate throughput in rows per second.

    Args:
        rows_processed: Number of rows processed
        duration_seconds: Duration in seconds

    Returns:
        Throughput in rows per second (rounded to 2 decimals)
        Returns 0.0 if duration_seconds <= 0 to avoid division by zero
    """
    if duration_seconds <= 0:
        return 0.0
    return round(rows_processed / duration_seconds, 2)


def detect_anomalies_zscore(df, columns, threshold=3.0):
    """
    Detect anomalies using z-score (standard deviation) method.

    Deterministic: Same input produces same output.

    Args:
        df: DataFrame to analyze
        columns: List of column names to analyze
        threshold: Number of standard deviations for cutoff (default 3.0)

    Returns:
        Dict mapping column_name -> anomaly info with keys:
        - count: Number of anomalies detected
        - sample_anomalies: List of first 10 anomaly indices (for review)
        - threshold: Threshold used
        - mean: Column mean (rounded to 4 decimals)
        - std: Column standard deviation (rounded to 4 decimals)
    """
    anomalies = {}

    for col in columns:
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue

        series = df[col].dropna()

        if len(series) == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        mean = series.mean()
        std = series.std()

        if std == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        z_scores = abs((series - mean) / std)
        anomaly_mask = z_scores > threshold
        anomaly_indices = df[anomaly_mask].index.tolist()

        anomalies[col] = {
            "count": int(anomaly_mask.sum()),
            "sample_anomalies": anomaly_indices[:10],
            "threshold": threshold,
            "mean": round(mean, 4),
            "std": round(std, 4),
        }

    return anomalies


def detect_anomalies_iqr(df, columns, multiplier=3.0):
    """
    Detect anomalies using IQR (Interquartile Range) method.

    Deterministic: Same input produces same output.

    Args:
        df: DataFrame to analyze
        columns: List of column names to analyze
        multiplier: IQR multiplier for cutoff (default 3.0 = strong outliers)

    Returns:
        Dict mapping column_name -> anomaly info with keys:
        - count: Number of anomalies detected
        - sample_anomalies: List of first 10 anomaly indices (for review)
        - iqr_bounds: List of [lower_bound, upper_bound] (rounded to 4 decimals)
    """
    anomalies = {}

    for col in columns:
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue

        series = df[col].dropna()

        if len(series) == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr

        anomaly_mask = (series < lower_bound) | (series > upper_bound)
        anomaly_indices = df[anomaly_mask].index.tolist()

        anomalies[col] = {
            "count": int(anomaly_mask.sum()),
            "sample_anomalies": anomaly_indices[:10],
            "iqr_bounds": [round(lower_bound, 4), round(upper_bound, 4)],
        }

    return anomalies


# ==============================================================================
# Configuration
# ==============================================================================


def load_config():
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_paths(config, timestamp):
    root = Path(__file__).parent.parent.parent

    # Resolve manifest directory using timestamp-based resolution
    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.0_BuildSampleManifest",
        required_file="master_sample_manifest.parquet",
    )

    paths = {
        "root": root,
        "script_dir": Path(__file__).parent,
        "manifest_dir": manifest_dir,
        "compustat_file": root
        / "1_Inputs"
        / "comp_na_daily_all"
        / "comp_na_daily_all.parquet",
        "ibes_file": root / "1_Inputs" / "tr_ibes" / "tr_ibes.parquet",
        "cccl_file": root
        / "1_Inputs"
        / "CCCL instrument"
        / "instrument_shift_intensity_2005_2022.parquet",
        "ccm_file": root
        / "1_Inputs"
        / "CRSPCompustat_CCM"
        / "CRSPCompustat_CCM.parquet",
        "crsp_dir": root / "1_Inputs" / "CRSP_DSF",
        "sdc_file": root / "1_Inputs" / "SDC" / "sdc-ma-merged.parquet",
    }

    output_base = root / config["paths"]["outputs"] / "3_Financial_Features"
    paths["output_dir"] = output_base / timestamp
    paths["output_dir"].mkdir(parents=True, exist_ok=True)

    log_base = root / config["paths"]["logs"] / "3_Financial_Features"
    log_base.mkdir(parents=True, exist_ok=True)
    paths["log_file"] = log_base / f"{timestamp}.log"

    return paths


# ==============================================================================
# Import substep modules directly
# ==============================================================================


def import_module(name, path):
    """Dynamically import a module by path."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ==============================================================================
# Prerequisite Checking
# ==============================================================================


def check_prerequisites(root, args):
    """Validate all required inputs and prerequisite steps exist."""
    from shared.dependency_checker import validate_prerequisites

    required_files = {
        "Compustat": root / "1_Inputs" / "Compustat",
        "IBES": root / "1_Inputs" / "IBES",
        "CRSP": root / "1_Inputs" / "CRSP",
        "SDC": root / "1_Inputs" / "SDC",
    }

    required_steps = {
        "1.4_AssembleManifest": "master_sample_manifest.parquet",
    }

    validate_prerequisites(required_files, required_steps)


# ==============================================================================
# Main
# ==============================================================================


def main():
    parser = argparse.ArgumentParser(description="Step 3: Build Financial Features")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )
    parser.add_argument(
        "--test", action="store_true", help="Run on first 3 years only for testing"
    )
    args = parser.parse_args()

    root = Path(__file__).parent.parent.parent

    # Handle dry-run mode
    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root, args)
        print("[OK] All prerequisites validated")
        sys.exit(0)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    config = load_config()
    paths = setup_paths(config, timestamp)

    # Check prerequisites before processing
    check_prerequisites(root, args)

    dual_writer = DualWriter(paths["log_file"])
    sys.stdout = dual_writer

    # Initialize stats with observability sections
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    mem_start = get_process_memory_mb()
    memory_readings = [mem_start["rss_mb"]]  # Track all memory readings for peak

    stats = {
        "step_id": "3.0_BuildFinancialFeatures",
        "timestamp": timestamp,
        "git_sha": get_git_sha(),
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {},
        "output": {"final_rows": 0, "final_columns": 0, "files": [], "checksums": {}},
        "missing_values": {},
        "merges": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
        "memory": {
            "start_mb": mem_start["rss_mb"],
            "end_mb": 0.0,
            "peak_mb": 0.0,
            "delta_mb": 0.0,
        },
        "throughput": {
            "rows_per_second": 0.0,
            "total_rows": 0,
            "duration_seconds": 0.0,
        },
        "quality_anomalies": {},
    }

    print("=" * 60)
    print("STEP 3: Build Financial Features (Orchestrator)")
    print(f"Timestamp: {timestamp}")
    print(f"Output: {paths['output_dir']}")
    if args.test:
        print("Mode: TEST (First 3 years only)")
    print("=" * 60)

    if args.dry_run:
        print("\n[DRY RUN MODE]")
        print("  1. Load manifest")
        print("  2. Compute Firm Controls (3.1) -> firm_controls_{year}.parquet")
        print("  3. Compute Market Variables (3.2) -> market_variables_{year}.parquet")
        print("  4. Compute Event Flags (3.3) -> event_flags_{year}.parquet")
        print("  5. Generate report_step3.md + variable_reference.csv")
        dual_writer.close()
        sys.stdout = dual_writer.terminal
        return

    # Import substep modules
    script_dir = paths["script_dir"]
    step31 = import_module("step31", script_dir / "3.1_FirmControls.py")
    step32 = import_module("step32", script_dir / "3.2_MarketVariables.py")
    step33 = import_module("step33", script_dir / "3.3_EventFlags.py")

    # Load manifest once
    print("\nLoading manifest...")
    manifest_path = paths["manifest_dir"] / "master_sample_manifest.parquet"
    # Column pruning: Load only required columns to reduce memory footprint
    manifest = pd.read_parquet(
        manifest_path, columns=["file_name", "gvkey", "start_date"]
    )
    manifest["start_date"] = pd.to_datetime(manifest["start_date"])
    manifest["year"] = manifest["start_date"].dt.year
    manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)

    # Input stats
    stats["input"]["files"].append(str(manifest_path))
    stats["input"]["checksums"]["master_sample_manifest.parquet"] = (
        compute_file_checksum(manifest_path)
    )
    stats["input"]["total_rows"] = len(manifest)
    stats["input"]["total_columns"] = len(manifest.columns)

    # Memory checkpoint after loading manifest
    mem_after_manifest = get_process_memory_mb()
    memory_readings.append(mem_after_manifest["rss_mb"])
    print(f"  Loaded: {len(manifest):,} calls")
    print(f"  Columns: {len(manifest.columns)}")
    print(f"  Memory: {mem_after_manifest['rss_mb']:.2f} MB")

    years = sorted(manifest["year"].unique())
    if args.test:
        years = years[:3]
        print(f"  TEST MODE: Limiting to years {years}")

    # ========== 3.1 Firm Controls ==========

    # ========== 3.1 Firm Controls ==========
    print("\n" + "=" * 60)
    print("STEP 3.1: Firm Controls")
    print("=" * 60)

    # Load data
    print("  Loading input files...")
    compustat = step31.load_compustat(paths["compustat_file"])
    print(f"    Compustat: {len(compustat):,} rows")

    ibes = step31.load_ibes(paths["ibes_file"])
    print(f"    IBES: {len(ibes):,} rows")

    cccl = step31.load_cccl(paths["cccl_file"])
    print(f"    CCCL: {len(cccl):,} rows")

    # Add input file stats
    for fname, fpath in [
        ("compustat.parquet", paths["compustat_file"]),
        ("ibes.parquet", paths["ibes_file"]),
        ("cccl.parquet", paths["cccl_file"]),
    ]:
        if fpath.exists():
            stats["input"]["files"].append(str(fpath))
            stats["input"]["checksums"][fname] = compute_file_checksum(fpath)

    # Compute
    comp_controls = step31.compute_compustat_controls(manifest, compustat)
    surp_controls = step31.compute_earnings_surprise(manifest, ibes, paths["ccm_file"])
    cccl_controls = step31.merge_cccl(manifest, cccl)

    # Merge
    firm_result = manifest[["file_name", "gvkey", "start_date", "year"]].copy()

    # Merge 1: Compustat controls
    before_merge = len(firm_result)
    firm_result = firm_result.merge(comp_controls, on="file_name", how="left")
    matched_count = firm_result["Size"].notna().sum()
    stats["merges"]["compustat_controls"] = {
        "left_rows": before_merge,
        "right_rows": len(comp_controls),
        "result_rows": len(firm_result),
        "matched": matched_count,
        "unmatched_left": before_merge - matched_count,
        "unmatched_right": len(comp_controls) - matched_count,
        "merge_type": "1:1",
    }
    print(
        f"    Compustat merge: {matched_count:,}/{before_merge:,} matched ({matched_count / before_merge * 100:.1f}%)"
    )

    # Merge 2: Earnings surprise
    before_merge = len(firm_result)
    firm_result = firm_result.merge(surp_controls, on="file_name", how="left")
    matched_count = firm_result["SurpDec"].notna().sum()
    stats["merges"]["earnings_surprise"] = {
        "left_rows": before_merge,
        "right_rows": len(surp_controls),
        "result_rows": len(firm_result),
        "matched": matched_count,
        "unmatched_left": before_merge - matched_count,
        "unmatched_right": len(surp_controls) - matched_count,
        "merge_type": "1:1",
    }
    print(
        f"    IBES merge: {matched_count:,}/{before_merge:,} matched ({matched_count / before_merge * 100:.1f}%)"
    )

    # Merge 3: CCCL
    before_merge = len(firm_result)
    firm_result = firm_result.merge(cccl_controls, on="file_name", how="left")
    # Get first shift_intensity column for stats
    intensity_cols = [
        c for c in cccl_controls.columns if c.startswith("shift_intensity")
    ]
    matched_count = (
        firm_result[intensity_cols[0]].notna().sum() if intensity_cols else 0
    )
    stats["merges"]["cccl_controls"] = {
        "left_rows": before_merge,
        "right_rows": len(cccl_controls),
        "result_rows": len(firm_result),
        "matched": matched_count,
        "unmatched_left": before_merge - matched_count,
        "unmatched_right": len(cccl_controls) - matched_count,
        "merge_type": "1:1",
    }
    if intensity_cols:
        print(
            f"    CCCL merge: {matched_count:,}/{before_merge:,} matched ({matched_count / before_merge * 100:.1f}%)"
        )
    else:
        print("    CCCL merge: No intensity columns found")

    # Save by year
    for year, group in firm_result.groupby("year"):
        group.to_parquet(
            paths["output_dir"] / f"firm_controls_{year}.parquet", index=False
        )
        stats["output"]["files"].append(f"firm_controls_{year}.parquet")
    print(f"  Saved {len(years)} firm_controls files")

    del compustat, ibes, cccl

    # ========== 3.2 Market Variables ==========
    print("\n" + "=" * 60)
    print("STEP 3.2: Market Variables")
    print("=" * 60)

    # Prepare manifest with PERMNO
    manifest_with_permno = step32.load_manifest_with_permno(
        paths["manifest_dir"], paths["ccm_file"]
    )
    print(f"  Manifest with PERMNO: {len(manifest_with_permno):,} rows")

    # Add CCM file to input stats
    if paths["ccm_file"].exists():
        stats["input"]["files"].append(str(paths["ccm_file"]))
        stats["input"]["checksums"]["ccm.parquet"] = compute_file_checksum(
            paths["ccm_file"]
        )

    all_market_results = []
    market_years_processed = 0
    total_crsp_rows = 0

    for year in years:
        print(f"\n  Year {year}...")
        year_manifest = manifest_with_permno[
            manifest_with_permno["year"] == year
        ].copy()

        crsp = step32.load_crsp_for_years(paths["crsp_dir"], [year - 1, year])
        if crsp is None:
            print(f"    No CRSP data, skipping")
            continue

        total_crsp_rows += len(crsp)
        print(f"    CRSP rows: {len(crsp):,}")

        year_manifest = step32.compute_returns_for_year(year_manifest, crsp, config)
        year_manifest = step32.compute_liquidity_for_year(year_manifest, crsp, config)

        # Collect stats for this year
        stockret_count = year_manifest["StockRet"].notna().sum()
        amihud_count = year_manifest["Amihud"].notna().sum()
        print(
            f"    StockRet coverage: {stockret_count:,}/{len(year_manifest):,} ({stockret_count / len(year_manifest) * 100:.1f}%)"
        )
        print(
            f"    Amihud coverage: {amihud_count:,}/{len(year_manifest):,} ({amihud_count / len(year_manifest) * 100:.1f}%)"
        )

        cols = [
            "file_name",
            "gvkey",
            "start_date",
            "year",
            "StockRet",
            "MarketRet",
            "Amihud",
            "Corwin_Schultz",
            "Delta_Amihud",
            "Delta_Corwin_Schultz",
            "Volatility",
        ]
        year_manifest[cols].to_parquet(
            paths["output_dir"] / f"market_variables_{year}.parquet", index=False
        )
        all_market_results.append(year_manifest[cols])
        stats["output"]["files"].append(f"market_variables_{year}.parquet")
        market_years_processed += 1

        del crsp
        import gc

        gc.collect()

    # Add processing stats for market variables
    if total_crsp_rows > 0:
        stats["processing"]["market_variables"] = {
            "years_processed": market_years_processed,
            "total_crsp_rows": total_crsp_rows,
            "market_files_created": market_years_processed,
        }

    print(f"  Saved {market_years_processed} market_variables files")

    # ========== 3.3 Event Flags ==========
    print("\n" + "=" * 60)
    print("STEP 3.3: Event Flags")
    print("=" * 60)

    manifest_for_sdc = step33.load_manifest(paths["manifest_dir"])
    sdc = step33.load_sdc(paths["sdc_file"])
    print(f"  SDC data: {len(sdc):,} rows")

    # Add SDC file to input stats
    if paths["sdc_file"].exists():
        stats["input"]["files"].append(str(paths["sdc_file"]))
        stats["input"]["checksums"]["sdc.parquet"] = compute_file_checksum(
            paths["sdc_file"]
        )

    event_flags = step33.compute_takeover_flags(manifest_for_sdc, sdc)

    event_result = manifest_for_sdc[["file_name", "gvkey", "start_date", "year"]].merge(
        event_flags, on="file_name"
    )

    # Collect event flag stats
    takeover_count = event_result["Takeover"].notna().sum()
    print(
        f"  Events with takeover flags: {takeover_count:,}/{len(event_result):,} ({takeover_count / len(event_result) * 100:.1f}%)"
    )

    for year, group in event_result.groupby("year"):
        group.to_parquet(
            paths["output_dir"] / f"event_flags_{year}.parquet", index=False
        )
        stats["output"]["files"].append(f"event_flags_{year}.parquet")
    print(f"  Saved {len(years)} event_flags files")

    # Add processing stats for event flags
    stats["processing"]["event_flags"] = {
        "sdc_rows": len(sdc),
        "takeover_events": int(takeover_count),
    }

    # ========== Generate Reports ==========
    print("\n" + "=" * 60)
    print("Generating Reports")
    print("=" * 60)

    # Combine for variable reference
    all_data = pd.concat(
        [firm_result, pd.concat(all_market_results, ignore_index=True)], axis=1
    )

    # Analyze missing values for output
    print("  Analyzing missing values...")
    stats["missing_values"] = analyze_missing_values(all_data)
    print(f"    Columns with missing values: {len(stats['missing_values'])}")

    # Set final output stats
    stats["output"]["final_rows"] = len(manifest)
    stats["output"]["final_columns"] = len(all_data.columns)

    generate_variable_reference(
        all_data, paths["output_dir"] / "variable_reference.csv"
    )

    # Report
    report = f"""# Step 3: Financial Features Report

**Generated:** {timestamp}
**Output:** `{paths["output_dir"]}`

## Outputs (per year)

| Type | Files | Variables |
|------|-------|-----------|
| Firm Controls | {len(list(paths["output_dir"].glob("firm_controls_*.parquet")))} | Size, BM, Lev, ROA, EPS_Growth, SurpDec, shift_intensity |
| Market Variables | {len(list(paths["output_dir"].glob("market_variables_*.parquet")))} | StockRet, MarketRet, Amihud, Corwin_Schultz, Deltas |
| Event Flags | {len(list(paths["output_dir"].glob("event_flags_*.parquet")))} | Takeover, Takeover_Type, Duration |

## Coverage Summary

- Total calls: {len(manifest):,}
- StockRet: {pd.concat(all_market_results)["StockRet"].notna().sum():,} ({pd.concat(all_market_results)["StockRet"].notna().mean() * 100:.1f}%)
- Amihud: {pd.concat(all_market_results)["Amihud"].notna().sum():,} ({pd.concat(all_market_results)["Amihud"].notna().mean() * 100:.1f}%)
"""

    with open(paths["output_dir"] / "report_step3.md", "w") as f:
        f.write(report)
    print("  Generated report_step3.md")

    # Finalize timing and stats
    end_time = time.perf_counter()
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(end_time - start_time, 2)

    # Final memory tracking
    mem_end = get_process_memory_mb()
    memory_readings.append(mem_end["rss_mb"])
    stats["memory"]["end_mb"] = mem_end["rss_mb"]
    stats["memory"]["peak_mb"] = round(max(memory_readings), 2)
    stats["memory"]["delta_mb"] = round(mem_end["rss_mb"] - mem_start["rss_mb"], 2)

    # Calculate throughput
    duration_seconds = end_time - start_time
    if duration_seconds > 0 and stats["output"]["final_rows"] > 0:
        throughput = calculate_throughput(
            stats["output"]["final_rows"], duration_seconds
        )
        stats["throughput"]["rows_per_second"] = throughput
        stats["throughput"]["total_rows"] = stats["output"]["final_rows"]
        stats["throughput"]["duration_seconds"] = round(duration_seconds, 3)

    # Compute output file checksums
    stats["output"]["checksums"] = {}
    for fname in stats["output"]["files"]:
        if fname.endswith(".parquet"):
            output_path = paths["output_dir"] / fname
            if output_path.exists():
                checksum = compute_file_checksum(output_path)
                stats["output"]["checksums"][fname] = checksum
    print(f"  Computed output checksums: {len(stats['output']['checksums'])} files")

    # Detect anomalies in final combined data
    print("\nDetecting anomalies in final data...")
    numeric_cols = all_data.select_dtypes(include=[np.number]).columns.tolist()
    # Skip ID columns and calculated columns that shouldn't be checked
    cols_to_check = [c for c in numeric_cols if c not in ["file_name", "gvkey", "year"]]
    if cols_to_check:
        stats["quality_anomalies"] = detect_anomalies_zscore(
            all_data, cols_to_check, threshold=3.0
        )
        total_anomalies = sum(a["count"] for a in stats["quality_anomalies"].values())
        print(
            f"  Anomalies detected: {total_anomalies} across {len(stats['quality_anomalies'])} columns"
        )
    else:
        stats["quality_anomalies"] = {}
        print("  No numeric columns to check for anomalies")

    # Print and save stats
    print_stats_summary(stats)
    save_stats(stats, paths["output_dir"])

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"All outputs in: {paths['output_dir']}")

    dual_writer.close()
    sys.stdout = dual_writer.terminal


if __name__ == "__main__":
    main()
