import pandas as pd
import numpy as np
import re
from pathlib import Path
from datetime import datetime
import sys
import hashlib
import json
import time
import psutil
import argparse

# Note: MemoryAwareThrottler from shared/chunked_reader.py is available for future chunked processing.
# Current implementation uses column pruning for memory optimization, avoiding complex refactoring required for process_in_chunks().

# Import shared symlink utility for 'latest' link management
try:
    from shared.symlink_utils import update_latest_link
except ImportError:
    # Fallback if shared/__init__.py hasn't run yet
    script_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(script_dir))
    from shared.symlink_utils import update_latest_link

# Import shared path validation utilities
try:
    from shared.path_utils import (
        validate_output_path,
        ensure_output_dir,
        validate_input_file,
        get_latest_output_dir,
    )
    from shared.observability_utils import DualWriter
except ImportError:
    import sys as _sys
    from pathlib import Path as _Path

    _script_dir = Path(__file__).parent.parent
    _sys.path.insert(0, str(_script_dir))
    from shared.path_utils import (
        validate_output_path,
        ensure_output_dir,
        validate_input_file,
        get_latest_output_dir,
    )
    from shared.observability_utils import DualWriter

# ==============================================================================
# Setup
# ==============================================================================


def setup_logging():
    log_dir = Path(__file__).parent.parent.parent / "3_Logs" / "2.2_ConstructVariables"
    ensure_output_dir(log_dir)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_path = log_dir / f"{timestamp}.log"

    sys.stdout = DualWriter(log_path)
    return log_path


def parse_arguments():
    """Parse command-line arguments for 2.2_ConstructVariables.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 2.2: Construct Text Variables

Constructs text-based variables from word counts (clarity, tone,
complexity). Calculates linguistic measures for regression
analysis (fog index, word length, etc.).
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    return parser.parse_args()


def check_prerequisites(root):
    """Validate all required inputs and prerequisite steps exist."""
    from shared.dependency_checker import validate_prerequisites

    required_files = {}

    required_steps = {
        "2.1_TokenizeAndCount": "linguistic_counts.parquet",
    }

    validate_prerequisites(required_files, required_steps)


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
    inp = stats["input"]
    out = stats["output"]
    delta = inp["total_rows"] - out["final_rows"]
    delta_pct = (delta / inp["total_rows"] * 100) if inp["total_rows"] > 0 else 0
    print(f"\n{'Metric':<25} {'Value':>15}")
    print("-" * 42)
    print(f"{'Input Rows':<25} {inp['total_rows']:>15,}")
    print(f"{'Output Rows':<25} {out['final_rows']:>15,}")
    print(f"{'Rows Removed':<25} {delta:>15,}")
    print(f"{'Removal Rate':<25} {delta_pct:>14.1f}%")
    print(f"{'Duration (seconds)':<25} {stats['timing']['duration_seconds']:>15.2f}")
    if stats["processing"]:
        print(f"\n{'Processing Step':<30} {'Removed':>10}")
        print("-" * 42)
        for step, count in stats["processing"].items():
            print(f"{step:<30} {count:>10,}")
    print("=" * 60)


def save_stats(stats, out_dir):
    stats_path = out_dir / "stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"Saved: {stats_path.name}")


# ==============================================================================
# Observability Helpers
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


def detect_anomalies_zscore(df, columns, threshold=3.0):
    """
    Detect anomalies using z-score (standard deviation) method.

    Deterministic: Same input produces same output.

    Args:
        df: DataFrame to analyze
        columns: List of column names to analyze
        threshold: Number of standard deviations for cutoff (default 3.0)

    Returns:
        Dict mapping column_name -> anomaly info
    """
    anomalies = {}

    for col in columns:
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue

        # Drop NaN for z-score calculation
        series = df[col].dropna()

        if len(series) == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        mean = series.mean()
        std = series.std()

        if std == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        # Calculate z-scores: (value - mean) / std
        z_scores = abs((series - mean) / std)

        # Flag anomalies beyond threshold
        anomaly_mask = z_scores > threshold
        anomaly_indices = df[anomaly_mask].index.tolist()

        anomalies[col] = {
            "count": int(anomaly_mask.sum()),
            "sample_anomalies": anomaly_indices[:10],  # Top 10 for review
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
        Dict mapping column_name -> anomaly info
    """
    anomalies = {}

    for col in columns:
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue

        # Drop NaN for IQR calculation
        series = df[col].dropna()

        if len(series) == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        # Calculate IQR: Q3 - Q1 (75th - 25th percentile)
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            anomalies[col] = {"count": 0, "sample_anomalies": []}
            continue

        # Flag anomalies
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
# Helper Loading Functions
# ==============================================================================
# Helper Loading Functions
# ==============================================================================


def load_manager_keywords(root):
    path = root / "1_Inputs" / "managerial_roles_extracted.txt"
    with open(path, "r") as f:
        keywords = [line.strip() for line in f if line.strip()]
    pattern = re.compile("|".join(keywords), re.IGNORECASE)
    print(f"  Loaded {len(keywords)} manager keywords")
    return pattern


def load_ceo_map(root):
    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.0_BuildSampleManifest",
        required_file="master_sample_manifest.parquet",
    )
    manifest_path = manifest_dir / "master_sample_manifest.parquet"
    validate_input_file(manifest_path, must_exist=True)
    df = pd.read_parquet(
        manifest_path,
        columns=[
            "file_name",
            "ceo_name",
            "prev_ceo_name",
            "gvkey",
            "conm",
            "sic",
            "start_date",
        ],
    )

    # Extract last names
    df["ceo_last"] = df["ceo_name"].fillna("").str.split().str[-1].str.lower()
    df["prev_ceo_last"] = df["prev_ceo_name"].fillna("").str.split().str[-1].str.lower()
    df["ceo_name_lower"] = df["ceo_name"].fillna("").str.lower()
    df["prev_ceo_name_lower"] = df["prev_ceo_name"].fillna("").str.lower()

    # Extract Year from start_date
    df["year"] = pd.to_datetime(df["start_date"]).dt.year

    return df


# ==============================================================================
# Flagging Logic
# ==============================================================================


def flag_speakers(df, manager_pattern, manifest_df):
    # Merge manifest info for context (company name, ceo name)
    # We only need 'conm' and CEO cols for flagging, not everything
    cols_to_merge = [
        "file_name",
        "conm",
        "ceo_name_lower",
        "prev_ceo_name_lower",
        "ceo_last",
        "prev_ceo_last",
    ]
    # Merge only columns that are NOT in df already (except key)
    cols_to_merge = [
        c for c in cols_to_merge if c not in df.columns or c == "file_name"
    ]

    df = df.merge(manifest_df[cols_to_merge], on="file_name", how="left")

    # Fill NA
    role = df["role"].fillna("")
    employer = df["employer"].fillna("")
    conm = df["conm"].fillna("")
    speaker_name = df["speaker_name"].fillna("")

    # Analyst
    df["is_analyst"] = role.str.contains("analyst", case=False)

    # Operator
    df["is_operator"] = role.str.contains("operator", case=False)

    # Manager
    # Keyword match
    is_keyword = role.str.contains(manager_pattern)
    # Employer match
    is_employer = employer.str.lower() == conm.str.lower()

    df["is_manager"] = (~df["is_analyst"] & ~df["is_operator"]) & (
        is_keyword | is_employer
    )

    # CEO (Tiered)
    speaker_lower = speaker_name.str.lower()
    speaker_last = speaker_name.str.split().str[-1].str.lower()

    is_ceo_exact = (speaker_lower == df["ceo_name_lower"]) | (
        speaker_lower == df["prev_ceo_name_lower"]
    )
    is_ceo_last = (speaker_last == df["ceo_last"]) | (
        speaker_last == df["prev_ceo_last"]
    )

    df["is_ceo"] = is_ceo_exact | is_ceo_last

    return df


# ==============================================================================
# Aggregation (Weighted - Ratio of Sums)
# ==============================================================================


def aggregate_weighted(df, sample_mask, context_mask, count_cols):
    subset = df[sample_mask & context_mask].copy()
    if len(subset) == 0:
        return None

    # Group by file
    gb = subset.groupby("file_name")

    # Sum Counts and Totals
    sums = gb[count_cols + ["total_tokens"]].sum()

    # Calculate Pct (x100)
    results = {}
    total_tokens = sums["total_tokens"].replace(0, np.nan)

    for col in count_cols:
        cat = col.replace("_count", "")
        # Variable naming: Sample_Context_Cat_pct
        # We handle sample/context prefix outside
        pct = (sums[col] / total_tokens) * 100.0
        results[f"{cat}_pct"] = pct

    return pd.DataFrame(results)


def process_year(year, root, manager_pattern, manifest_df, out_dir, tokenized_dir):
    in_path = tokenized_dir / f"linguistic_counts_{year}.parquet"
    if not in_path.exists():
        print(f"  Skipping {year}: Input not found")
        return None

    print(f"\nProcessing {year}...")
    validate_input_file(in_path, must_exist=True)
    # Column pruning: Load metadata columns and all count columns (dynamic from LM dictionary)
    # First pass: get schema to identify count columns
    all_cols = pd.read_parquet(in_path, columns=[]).columns.tolist()
    count_cols = [c for c in all_cols if c.endswith("_count")]
    # Second pass: load only needed columns
    df = pd.read_parquet(
        in_path,
        columns=["file_name", "role", "employer", "speaker_name", "total_tokens"]
        + count_cols,
    )
    input_rows = len(df)

    # Flag
    df = flag_speakers(df, manager_pattern, manifest_df)

    analyst_count = df["is_analyst"].sum()
    manager_count = df["is_manager"].sum()
    ceo_count = df["is_ceo"].sum()
    operator_count = df["is_operator"].sum()

    print(f"  Analyst: {analyst_count:,}")
    print(f"  Manager: {manager_count:,}")
    print(f"  CEO: {ceo_count:,}")

    # Identify count columns
    count_cols = [c for c in df.columns if c.endswith("_count")]

    # Define Aggregations
    # Legacy mainly cared about: Manager QA, Analyst QA (?), Manager Pres (?)
    # We will generate comprehensive set

    samples = {
        "Manager": df["is_manager"],
        "Analyst": df["is_analyst"],
        "CEO": df["is_ceo"],
        "NonCEO_Manager": df["is_manager"] & ~df["is_ceo"],  # Managers excluding CEO
        "Entire": pd.Series(True, index=df.index),
    }

    contexts = {
        "QA": df["context"] == "qa",
        "Pres": df["context"] == "pres",
        "All": df["context"].isin(["qa", "pres"]),
    }

    # Initialize result with metadata
    # Use manifest metadata
    meta = manifest_df[manifest_df["year"] == year][
        ["file_name", "start_date", "gvkey", "conm", "sic"]
    ].copy()

    variables_created = 0
    for s_name, s_mask in samples.items():
        for c_name, c_mask in contexts.items():
            agg_df = aggregate_weighted(df, s_mask, c_mask, count_cols)
            if agg_df is not None:
                # Rename columns
                agg_df.columns = [f"{s_name}_{c_name}_{c}" for c in agg_df.columns]
                variables_created += len(agg_df.columns)
                # Merge
                meta = meta.merge(agg_df, on="file_name", how="left")

    # Fill NaN with 0? Or keep NaN for missing sections?
    # Legacy behavior: likely keep NaN or impute.
    # We will keep NaN to distinctions between "No Uncertainty" (0) and "No Text" (NaN).

    out_path = out_dir / f"linguistic_variables_{year}.parquet"
    meta.to_parquet(out_path, index=False)
    print(f"  Saved {out_path.name}: {len(meta):,} rows, {variables_created} variables")

    return {
        "rows": len(meta),
        "cols": len(meta.columns),
        "speaker_flags": {
            "analyst": int(analyst_count),
            "manager": int(manager_count),
            "ceo": int(ceo_count),
            "operator": int(operator_count),
        },
    }


def main():
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    print("=== Step 2.2: Construct Variables (Weighted) ===")
    root = Path(__file__).parent.parent.parent
    setup_logging()

    out_base = root / "4_Outputs" / "2_Textual_Analysis"
    out_dir = out_base / f"2.2_Variables" / timestamp
    ensure_output_dir(out_dir)

    # Memory tracking at script start
    mem_start = get_process_memory_mb()
    all_memory_values = [mem_start["rss_mb"]]

    stats = {
        "step_id": "2.2_ConstructVariables",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {},
        "output": {"final_rows": 0, "final_columns": 0, "files": [], "checksums": {}},
        "missing_values": {},
        "speaker_flags": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
    }

    # Load References and checksum inputs
    keywords_path = root / "1_Inputs" / "managerial_roles_extracted.txt"

    # Resolve manifest path using timestamp-based directory resolution
    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.0_BuildSampleManifest",
        required_file="master_sample_manifest.parquet",
    )
    manifest_path = manifest_dir / "master_sample_manifest.parquet"

    # Resolve tokenized input directory using timestamp-based resolution
    tokenized_dir = get_latest_output_dir(
        root / "4_Outputs" / "2_Textual_Analysis" / "2.1_Tokenized",
        required_file="linguistic_counts_2002.parquet",
    )

    stats["input"]["files"].append(str(keywords_path))
    stats["input"]["checksums"]["managerial_roles_extracted.txt"] = (
        compute_file_checksum(keywords_path)
    )
    stats["input"]["files"].append(str(manifest_path))
    stats["input"]["checksums"]["master_sample_manifest.parquet"] = (
        compute_file_checksum(manifest_path)
    )

    manager_pattern = load_manager_keywords(root)
    manifest_df = load_ceo_map(root)
    stats["input"]["total_rows"] = len(manifest_df)
    stats["input"]["total_columns"] = len(manifest_df.columns)
    print_stat("Manifest rows", value=len(manifest_df))

    # Process
    output_rows = 0
    output_cols = 0
    total_speaker_flags = {"analyst": 0, "manager": 0, "ceo": 0, "operator": 0}
    for year in range(2002, 2019):
        year_output = process_year(
            year, root, manager_pattern, manifest_df, out_dir, tokenized_dir
        )
        if year_output:
            output_rows += year_output["rows"]
            output_cols = max(output_cols, year_output["cols"])
            stats["output"]["files"].append(f"linguistic_variables_{year}.parquet")
            if "speaker_flags" in year_output:
                for k, v in year_output["speaker_flags"].items():
                    total_speaker_flags[k] += v

    stats["output"]["final_rows"] = output_rows
    stats["output"]["final_columns"] = output_cols
    stats["speaker_flags"] = total_speaker_flags

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
    throughput = calculate_throughput(stats["output"]["final_rows"], duration_seconds)
    stats["throughput"] = {
        "rows_per_second": throughput,
        "total_rows": stats["output"]["final_rows"],
        "duration_seconds": round(duration_seconds, 3),
    }

    # Add output checksums
    stats["output"]["checksums"] = {}
    output_files = list(out_dir.glob("linguistic_variables_*.parquet"))
    for filepath in output_files:
        checksum = compute_file_checksum(filepath)
        stats["output"]["checksums"][filepath.name] = checksum

    # Add anomaly detection for numeric columns (linguistic variables)
    # Check if there are any numeric columns suitable for anomaly detection in aggregated data
    # Using first year of output for anomaly detection
    first_year_file = next(
        (f for f in output_files if f.name.endswith("_2002.parquet")), None
    )
    if first_year_file:
        validate_input_file(first_year_file, must_exist=True)
        # Load all columns (need all numeric types for anomaly detection)
        first_year_df = pd.read_parquet(first_year_file)
        numeric_cols = first_year_df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            stats["quality_anomalies"] = detect_anomalies_zscore(
                first_year_df, numeric_cols, threshold=3.0
            )

    print_stats_summary(stats)
    save_stats(stats, out_dir)

    update_latest_link(out_dir, out_base / "2.2_Variables" / "latest")
    print("\n=== Complete ===")


if __name__ == "__main__":
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        print("[OK] All prerequisites validated")
        sys.exit(0)

    check_prerequisites(root)
    main()
