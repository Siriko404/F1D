import pandas as pd
from pathlib import Path
import sys
import hashlib
import json
import time
from datetime import datetime
import numpy as np
import psutil

# Note: MemoryAwareThrottler from shared/chunked_reader.py is available for future chunked processing.
# Current implementation uses column pruning for memory optimization, avoiding complex refactoring required for process_in_chunks().
# Note: For this verification script, we load all columns to enable comprehensive missing value analysis.

# Import shared path validation utilities
try:
    from shared.path_utils import (
        validate_output_path,
        ensure_output_dir,
        validate_input_file,
    )
except ImportError:
    import sys as _sys
    from pathlib import Path as _Path

    _script_dir = Path(__file__).parent.parent
    _sys.path.insert(0, str(_script_dir))
    from shared.path_utils import (
        validate_output_path,
        ensure_output_dir,
        validate_input_file,
    )


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
        "rss_mb": mem_info.rss / (1024 * 1024),  # Resident Set Size
        "vms_mb": mem_info.vms / (1024 * 1024),  # Virtual Memory Size
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


def compute_file_checksum(filepath, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def print_stat(label, before=None, after=None, value=None, indent=2):
    prefix = " " * indent
    if before is not None and after is not None:
        delta = after - before
        pct = (delta / before * 100) if before != 0 else 0
        sign = "+" if delta >= 0 else ""
        print(f"{prefix}{label}: {before:,} -> {after:,} ({sign}{pct:.1f}%)")
    else:
        v = value if value is not None else after
        if isinstance(v, float):
            print(f"{prefix}{label}: {v:,.2f}")
        elif isinstance(v, int):
            print(f"{prefix}{label}: {v:,}")
        else:
            print(f"{prefix}{label}: {v}")


def analyze_missing_values(df):
    missing = {}
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            missing[col] = {
                "count": int(null_count),
                "percent": round(null_count / len(df) * 100, 2),
            }
    return missing


def print_stats_summary(stats):
    print("\n" + "=" * 60)
    print("STATISTICS SUMMARY")
    print("=" * 60)

    print(f"\n{'Metric':<25} {'Value':>15}")
    print("-" * 42)
    print(f"{'Years Processed':<25} {stats['processing']['years_processed']:>15,}")
    print(f"{'Files Verified':<25} {stats['processing']['total_files_verified']:>15,}")
    print(f"{'Files Passed':<25} {stats['processing']['files_passed']:>15,}")
    print(f"{'Files Failed':<25} {stats['processing']['files_failed']:>15,}")
    print(f"{'Total Rows':<25} {stats['output']['final_rows']:>15,}")
    print(f"{'Missing DepVar':<25} {stats['processing']['missing_depvar_count']:>15,}")
    print(f"{'Duration (seconds)':<25} {stats['timing']['duration_seconds']:>15.2f}")

    print("=" * 60)


def save_stats(stats, out_dir):
    stats_path = out_dir / "stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"Saved: {stats_path.name}")


def main():
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("=== Step 2.3: Verify Step 2 Outputs ===")
    root = Path(__file__).parent.parent.parent

    # Memory tracking at script start
    mem_start = get_process_memory_mb()
    all_memory_values = [mem_start["rss_mb"]]

    stats = {
        "step_id": "2.3_VerifyStep2",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {
            "years_processed": 0,
            "total_files_verified": 0,
            "files_passed": 0,
            "files_failed": 0,
        },
        "output": {"final_rows": 0, "final_columns": 0, "files": [], "checksums": {}},
        "missing_values": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
    }

    out_base = root / "4_Outputs" / "2_Textual_Analysis"

    years = range(2002, 2019)
    all_ok = True

    print(
        f"{'Year':<6} {'Counts File':<20} {'Variables File':<20} {'Rows (Vars)':<12} {'Missing DepVar':<15}"
    )
    print("-" * 80)

    for year in years:
        counts_path = (
            out_base / f"2.1_Tokenized/latest/linguistic_counts_{year}.parquet"
        )
        vars_path = (
            out_base / f"2.2_Variables/latest/linguistic_variables_{year}.parquet"
        )

        counts_ok = "OK" if counts_path.exists() else "MISSING"
        vars_ok = "OK" if vars_path.exists() else "MISSING"

        stats["processing"]["total_files_verified"] += 2

        rows = 0
        missing_dep = 0

        if vars_path.exists():
            validate_input_file(vars_path, must_exist=True)
            # Note: Loading all columns for comprehensive missing value analysis
            # analyze_missing_values() iterates over all columns to detect data quality issues
            df = pd.read_parquet(vars_path)
            rows = len(df)
            stats["output"]["final_rows"] += rows
            stats["processing"]["years_processed"] += 1

            checksum = compute_file_checksum(vars_path)
            stats["input"]["checksums"][vars_path.name] = checksum
            stats["input"]["files"].append(str(vars_path))

            col = "Manager_QA_Uncertainty_pct"
            if col not in df.columns:
                vars_ok = "BAD COL"
                stats["processing"]["files_failed"] += 1
            else:
                missing_dep = df[col].isna().sum()
                stats["processing"]["missing_depvar_count"] += missing_dep

                missing_analysis = analyze_missing_values(df)
                if missing_analysis:
                    stats["missing_values"][year] = missing_analysis

                stats["processing"]["files_passed"] += 1
        else:
            stats["processing"]["files_failed"] += 1

        if counts_path.exists():
            checksum = compute_file_checksum(counts_path)
            stats["input"]["checksums"][counts_path.name] = checksum
            stats["input"]["files"].append(str(counts_path))
            stats["processing"]["files_passed"] += 1
        else:
            stats["processing"]["files_failed"] += 1

        print(f"{year:<6} {counts_ok:<20} {vars_ok:<20} {rows:<12,} {missing_dep:<15,}")

        if counts_ok != "OK" or vars_ok != "OK":
            all_ok = False

    if all_ok:
        print("\n[SUCCESS] All files present and valid.")
    else:
        print("\n[FAILURE] Some files missing or invalid.")

    end_time = time.perf_counter()
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(end_time - start_time, 2)

    # Memory tracking at script end
    mem_end = get_process_memory_mb()
    all_memory_values.append(mem_end["rss_mb"])

    # Add memory stats to stats
    stats["memory"] = {
        "start_mb": round(mem_start["rss_mb"], 2),
        "end_mb": round(mem_end["rss_mb"], 2),
        "peak_mb": round(max(all_memory_values), 2),
        "delta_mb": round(mem_end["rss_mb"] - mem_start["rss_mb"], 2),
    }

    # Add throughput to stats
    duration_seconds = stats["timing"]["duration_seconds"]
    # Note: 2.3 is a validation script with minimal data processing
    # throughput calculation may be very low or zero, which is expected
    throughput = calculate_throughput(
        stats["processing"]["total_files_verified"], duration_seconds
    )
    stats["throughput"] = {
        "rows_per_second": throughput,
        "total_rows": stats["processing"]["total_files_verified"],
        "duration_seconds": round(duration_seconds, 3),
    }

    # Add output checksums (minimal for validation script)
    stats["output"]["checksums"] = {}

    # Note: 2.3 is a validation script that checks output files
    # It does not generate new data files, so anomaly detection is not applicable

    print_stats_summary(stats)
    save_stats(stats, root / "3_Logs" / "2.3_VerifyStep2")


if __name__ == "__main__":
    main()
