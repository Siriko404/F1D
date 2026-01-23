#!/usr/bin/env python3
"""
==============================================================================
STEP 3.1: Build Firm Controls
==============================================================================
ID: 3.1_FirmControls
Description: Computes firm-level control variables from Compustat and IBES.

Variables Computed:
    - Size: ln(atq) - Log of total assets
    - BM: ceqq / (cshoq * prccq) - Book-to-market ratio
    - Lev: ltq / atq - Leverage
    - ROA: niq / atq - Return on assets
    - EPS_Growth: (EPS - EPS_lag4) / |EPS_lag4| - YoY EPS growth
    - SurpDec: Earnings surprise decile (-5 to +5)
    - shift_intensity: Competition instrument (merged from CCCL)

Inputs:
    - 4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet
    - 1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet
    - 1_Inputs/tr_ibes/tr_ibes.parquet
    - 1_Inputs/CCCL instrument/instrument_shift_intensity_2005_2022.parquet

Outputs:
    - 4_Outputs/3_Financial_Features/{timestamp}/firm_controls_{year}.parquet

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
import importlib.util
import hashlib
import json
import time
import psutil

# Dynamic import for 3.4_Utils.py
utils_path = Path(__file__).parent / "3.4_Utils.py"
spec = importlib.util.spec_from_file_location("utils", utils_path)
utils = importlib.util.module_from_spec(spec)
sys.modules["utils"] = utils
spec.loader.exec_module(utils)

from utils import (
    DualWriter,
    get_latest_output_dir,
    generate_variable_reference,
)
from shared.symlink_utils import update_latest_link
from shared.financial_utils import compute_financial_controls_quarterly

# ==============================================================================
# Configuration
# ==============================================================================


def load_config():
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_paths(config, timestamp):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    paths = {
        "root": root,
        "manifest_dir": root / "4_Outputs" / "1.0_BuildSampleManifest" / "latest",
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
    }

    # Output directory
    output_base = root / config["paths"]["outputs"] / "3_Financial_Features"
    paths["output_dir"] = output_base / timestamp
    paths["output_dir"].mkdir(parents=True, exist_ok=True)
    paths["latest_dir"] = output_base / "latest"

    # Log directory
    log_base = root / config["paths"]["logs"] / "3_Financial_Features"
    log_base.mkdir(parents=True, exist_ok=True)
    paths["log_file"] = log_base / f"{timestamp}.log"

    return paths


# ==============================================================================
# Statistics Helpers
# ==============================================================================


def compute_file_checksum(filepath, algorithm="sha256"):
    """Compute checksum for a file."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def print_stat(label, before=None, after=None, value=None, indent=2):
    """Print a statistic with consistent formatting.

    Modes:
        - Delta mode (before/after): "  Label: 1,000 -> 800 (-20.0%)"
        - Value mode: "  Label: 1,000"
    """
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
    """Analyze missing values per column."""
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
    """Print formatted summary table."""
    print("\n" + "=" * 60)
    print("STATISTICS SUMMARY")
    print("=" * 60)

    # Input/Output comparison
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

    print("=" * 60)


def save_stats(stats, out_dir):
    """Save statistics to JSON file."""
    stats_path = out_dir / "stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"Saved: {stats_path.name}")


# ==============================================================================
# Data Loading
# ==============================================================================
# Data Loading
# ==============================================================================


def load_manifest(manifest_dir):
    """Load manifest data"""
    manifest_file = manifest_dir / "master_sample_manifest.parquet"
    if not manifest_file.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_file}")

    df = pd.read_parquet(manifest_file)
    print(f"  Loaded manifest: {len(df):,} calls")

    # Ensure gvkey is string and zero-padded
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["year"] = df["start_date"].dt.year

    return df


def load_compustat(compustat_file):
    """Load Compustat data with only required columns"""
    print(f"  Loading Compustat (metadata only scan first)...")

    # Read only needed columns to save memory
    required_cols = [
        "gvkey",
        "datadate",
        "atq",
        "ceqq",
        "cshoq",
        "prccq",
        "ltq",
        "niq",
        "epspxq",
        "actq",
        "lctq",
        "xrdq",
    ]

    df = pd.read_parquet(compustat_file, columns=required_cols)
    print(f"  Loaded Compustat: {len(df):,} quarterly observations")

    # Normalize
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["datadate"] = pd.to_datetime(df["datadate"])

    # Convert Decimal types to float64 for numpy compatibility
    for col in required_cols[2:]:  # fast way to get numeric cols
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

    return df


# ...


def compute_firm_controls(row, compustat_df):
    """Compute firm controls for a single call (vectorized implementation strongly preferred but this is row-wise).

    Wait, the original script might use a merge approach. Let's check the context.
    The previous view showed 'compute_firm_controls' was NOT visible in lines 1-100.
    I should check how variables are constructed.
    Based on typical structure, there's likely a merge then vectorized calc.

    Let's verify the processing logic in `3.1` before writing the calc code blindly.
    """


def load_ibes(ibes_file):
    """Load IBES data filtered to EPS quarterly"""
    print(f"  Loading IBES...")

    df = pd.read_parquet(ibes_file)
    print(f"  Raw IBES: {len(df):,} rows")

    # Filter to EPS quarterly only
    df = df[(df["MEASURE"] == "EPS") & (df["FISCALP"] == "QTR")].copy()
    print(f"  After EPS/QTR filter: {len(df):,} rows")

    # Keep only needed columns
    df = df[["TICKER", "CUSIP", "FPEDATS", "STATPERS", "MEANEST", "ACTUAL"]].copy()

    # Normalize dates
    df["FPEDATS"] = pd.to_datetime(df["FPEDATS"], errors="coerce")
    df["STATPERS"] = pd.to_datetime(df["STATPERS"], errors="coerce")

    return df


def load_cccl(cccl_file):
    """Load CCCL instrument data with all 6 shift_intensity variants"""
    print(f"  Loading CCCL instrument...")

    df = pd.read_parquet(cccl_file)
    print(f"  Loaded CCCL: {len(df):,} rows, {df['gvkey'].nunique():,} unique gvkeys")

    # Keep gvkey, year, and all shift_intensity variants
    intensity_cols = [
        "shift_intensity_sale_ff12",
        "shift_intensity_mkvalt_ff12",
        "shift_intensity_sale_ff48",
        "shift_intensity_mkvalt_ff48",
        "shift_intensity_sale_sic2",
        "shift_intensity_mkvalt_sic2",
    ]

    # Filter to columns that exist
    available_cols = ["gvkey", "year"] + [c for c in intensity_cols if c in df.columns]
    df = df[available_cols].copy()
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    print(
        f"  Shift intensity variants: {len([c for c in intensity_cols if c in df.columns])}"
    )

    return df


# ==============================================================================
# Variable Computation
# ==============================================================================


def compute_compustat_controls(manifest, compustat):
    """Compute Size, BM, Lev, ROA, EPS_Growth from Compustat (Vectorized with merge_asof)"""
    print("\n" + "=" * 60)
    print("Computing Compustat Controls (Optimized)")
    print("=" * 60)

    # Compute financial controls using shared quarterly function
    compustat = compute_financial_controls_quarterly(compustat, winsorize=True)

    print(f"  Compustat controls computed for {compustat['gvkey'].nunique():,} firms")

    # Optimized Matching using merge_asof
    print(f"  Matching calls to Compustat quarters (vectorized)...")

    # Prepare Manifest
    # Ensure datetime and sorted
    manifest_sorted = manifest.copy()
    manifest_sorted["start_date"] = pd.to_datetime(manifest_sorted["start_date"])
    manifest_sorted = manifest_sorted.sort_values("start_date")

    # Prepare Compustat
    comp_sorted = compustat.copy()
    comp_sorted["datadate"] = pd.to_datetime(comp_sorted["datadate"])
    comp_sorted = comp_sorted.sort_values("datadate")

    # Check join keys
    manifest_sorted["gvkey"] = manifest_sorted["gvkey"].astype(str)
    comp_sorted["gvkey"] = comp_sorted["gvkey"].astype(str)

    # merge_asof
    # direction='backward': for a call at T, finds the last compustat date <= T
    merged = pd.merge_asof(
        manifest_sorted,
        comp_sorted[
            [
                "gvkey",
                "datadate",
                "Size",
                "BM",
                "Lev",
                "ROA",
                "EPS_Growth",
                "CurrentRatio",
                "RD_Intensity",
            ]
        ],
        left_on="start_date",
        right_on="datadate",
        by="gvkey",
        direction="backward",
    )

    # Check match rate
    matched = merged["Size"].notna().sum()
    print(
        f"  Matched: {matched:,} / {len(manifest):,} ({matched / len(manifest) * 100:.1f}%)"
    )

    # Return containing only the result columns, indexed by file_name original order?
    # The calling function expects a dataframe with these columns that it can merge back to manifest on file_name
    # Since we have file_name in merged (from manifest), we can return the relevant columns.

    results_df = merged[
        [
            "file_name",
            "Size",
            "BM",
            "Lev",
            "ROA",
            "EPS_Growth",
            "CurrentRatio",
            "RD_Intensity",
        ]
    ].copy()

    return results_df


def compute_earnings_surprise(manifest, ibes, ccm_file):
    """Compute SurpDec from IBES"""
    print("\n" + "=" * 60)
    print("Computing Earnings Surprise (IBES)")
    print("=" * 60)

    # Load CCM for LPERMNO linking
    ccm = pd.read_parquet(ccm_file)
    ccm["cusip8"] = ccm["cusip"].astype(str).str[:8]
    ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce")
    ccm_cusip = ccm[["cusip8", "LPERMNO", "gvkey"]].drop_duplicates().dropna()
    ccm_cusip["gvkey"] = ccm_cusip["gvkey"].astype(str).str.zfill(6)

    # Link IBES to gvkey via CUSIP
    ibes["cusip8"] = ibes["CUSIP"].astype(str).str[:8]
    ibes_linked = ibes.merge(ccm_cusip[["cusip8", "gvkey"]], on="cusip8", how="inner")
    print(f"  IBES linked to gvkey: {len(ibes_linked):,} / {len(ibes):,}")

    # Compute raw surprise
    ibes_linked["surprise_raw"] = ibes_linked["ACTUAL"] - ibes_linked["MEANEST"]

    # Match to manifest
    print(f"  Matching calls to IBES forecasts...")

    ibes_grouped = {gvkey: group for gvkey, group in ibes_linked.groupby("gvkey")}

    results = []
    matched = 0

    for idx, row in manifest.iterrows():
        gvkey = row["gvkey"]
        call_date = row["start_date"]

        result = {
            "file_name": row["file_name"],
            "ActualEPS": np.nan,
            "ForecastEPS": np.nan,
            "surprise_raw": np.nan,
        }

        if gvkey in ibes_grouped:
            firm_ibes = ibes_grouped[gvkey]
            # Find forecast within +/- 45 days of call
            mask = (
                (firm_ibes["FPEDATS"] >= call_date - pd.Timedelta(days=45))
                & (firm_ibes["FPEDATS"] <= call_date + pd.Timedelta(days=45))
                & (firm_ibes["STATPERS"] <= call_date)
            )
            if mask.any():
                closest = firm_ibes[mask].iloc[-1]
                result["ActualEPS"] = closest["ACTUAL"]
                result["ForecastEPS"] = closest["MEANEST"]
                result["surprise_raw"] = closest["surprise_raw"]
                matched += 1

        results.append(result)

    results_df = pd.DataFrame(results)
    print(
        f"  Matched: {matched:,} / {len(manifest):,} ({matched / len(manifest) * 100:.1f}%)"
    )

    # Compute surprise deciles within quarter
    manifest_with_surprise = manifest.merge(results_df, on="file_name")
    manifest_with_surprise["call_quarter"] = manifest_with_surprise[
        "start_date"
    ].dt.to_period("Q")

    def rank_surprises(group):
        """Rank surprises into -5 to +5 scale"""
        surprises = group["surprise_raw"]
        ranks = pd.Series(index=group.index, dtype=float)

        valid_mask = surprises.notna()
        if valid_mask.sum() < 5:
            return ranks

        pos_mask = surprises > 0
        zero_mask = surprises == 0
        neg_mask = surprises < 0

        # Positive: 5 (largest) to 1 (smallest)
        if pos_mask.sum() > 0:
            pos_ranks = surprises[pos_mask].rank(ascending=False, pct=True)
            ranks.loc[pos_mask] = (5 - pos_ranks * 4).round().clip(1, 5)

        # Zero: 0
        ranks.loc[zero_mask] = 0

        # Negative: -1 (smallest abs) to -5 (largest abs)
        if neg_mask.sum() > 0:
            neg_ranks = surprises[neg_mask].abs().rank(ascending=True, pct=True)
            ranks.loc[neg_mask] = -(1 + neg_ranks * 4).round().clip(1, 5)

        return ranks

    manifest_with_surprise["SurpDec"] = manifest_with_surprise.groupby(
        "call_quarter", group_keys=False
    ).apply(lambda g: rank_surprises(g))

    # Return just file_name and computed columns
    return manifest_with_surprise[
        ["file_name", "ActualEPS", "ForecastEPS", "surprise_raw", "SurpDec"]
    ]


def merge_cccl(manifest, cccl):
    """Merge all shift_intensity variants from CCCL"""
    print("\n" + "=" * 60)
    print("Merging CCCL Instrument")
    print("=" * 60)

    # Get shift intensity columns
    intensity_cols = [c for c in cccl.columns if c.startswith("shift_intensity")]
    merge_cols = ["gvkey", "year"] + intensity_cols

    # Merge on gvkey and year
    merged = manifest[["file_name", "gvkey", "year"]].merge(
        cccl[merge_cols], on=["gvkey", "year"], how="left"
    )

    # Report coverage for first intensity column
    if intensity_cols:
        matched = merged[intensity_cols[0]].notna().sum()
        print(
            f"  Matched: {matched:,} / {len(manifest):,} ({matched / len(manifest) * 100:.1f}%)"
        )
        print(f"  Shift intensity columns: {intensity_cols}")

    return merged[["file_name"] + intensity_cols]


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
# Main
# ==============================================================================


def main():
    """Main execution"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    config = load_config()
    paths = setup_paths(config, timestamp)

    # Setup logging
    dual_writer = DualWriter(paths["log_file"])
    sys.stdout = dual_writer

    print("=" * 60)
    print("STEP 3.1: Build Firm Controls")
    print(f"Timestamp: {timestamp}")
    print("=" * 60)

    # Initialize statistics with observability sections
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    mem_start = get_process_memory_mb()
    memory_readings = [mem_start["rss_mb"]]

    stats = {
        "step_id": "3.1_FirmControls",
        "timestamp": timestamp,
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

    # Load data with stats collection
    print("\nLoading data...")

    # Load manifest
    manifest_file = paths["manifest_dir"] / "master_sample_manifest.parquet"
    stats["input"]["files"].append(str(manifest_file))
    stats["input"]["checksums"][manifest_file.name] = compute_file_checksum(
        manifest_file
    )
    manifest = load_manifest(paths["manifest_dir"])
    print_stat("Manifest rows", value=len(manifest))
    stats["input"]["total_rows"] += len(manifest)

    # Load Compustat
    print("\nCompustat:")
    stats["input"]["files"].append(str(paths["compustat_file"]))
    stats["input"]["checksums"][paths["compustat_file"].name] = compute_file_checksum(
        paths["compustat_file"]
    )
    compustat = load_compustat(paths["compustat_file"])
    print_stat("Compustat rows", value=len(compustat))
    stats["input"]["total_rows"] += len(compustat)

    # Load IBES
    print("\nIBES:")
    stats["input"]["files"].append(str(paths["ibes_file"]))
    stats["input"]["checksums"][paths["ibes_file"].name] = compute_file_checksum(
        paths["ibes_file"]
    )
    ibes = load_ibes(paths["ibes_file"])
    print_stat("IBES rows", value=len(ibes))
    stats["input"]["total_rows"] += len(ibes)

    # Load CCCL
    print("\nCCCL:")
    stats["input"]["files"].append(str(paths["cccl_file"]))
    stats["input"]["checksums"][paths["cccl_file"].name] = compute_file_checksum(
        paths["cccl_file"]
    )
    cccl = load_cccl(paths["cccl_file"])
    print_stat("CCCL rows", value=len(cccl))
    stats["input"]["total_rows"] += len(cccl)

    # Compute variables with merge diagnostics
    print("\nComputing variables...")

    # Compustat controls (includes merge)
    print("\n" + "=" * 60)
    print("Compustat Controls Merge")
    print("=" * 60)
    comp_controls = compute_compustat_controls(manifest, compustat)
    matched_comp = comp_controls["Size"].notna().sum()
    unmatched_comp = len(manifest) - matched_comp
    print_stat("Compustat matched", before=len(manifest), after=matched_comp)

    stats["merges"]["compustat_controls"] = {
        "left_rows": len(manifest),
        "right_rows": len(compustat),
        "result_rows": len(comp_controls),
        "matched": int(matched_comp),
        "unmatched_left": int(unmatched_comp),
        "merge_type": "asof_backward",
    }

    # Earnings surprise (includes multiple merges)
    print("\n" + "=" * 60)
    print("Earnings Surprise Merges")
    print("=" * 60)
    ccm_file = paths["ccm_file"]
    stats["input"]["files"].append(str(ccm_file))
    stats["input"]["checksums"][ccm_file.name] = compute_file_checksum(ccm_file)

    surp_controls = compute_earnings_surprise(manifest, ibes, ccm_file)
    matched_surp = surp_controls["SurpDec"].notna().sum()
    unmatched_surp = len(manifest) - matched_surp
    print_stat("IBES matched", before=len(manifest), after=matched_surp)

    stats["merges"]["ibes_surprise"] = {
        "left_rows": len(manifest),
        "right_rows": len(ibes),
        "result_rows": len(surp_controls),
        "matched": int(matched_surp),
        "unmatched_left": int(unmatched_surp),
        "merge_type": "complex_linkage",
    }

    # CCCL merge
    print("\n" + "=" * 60)
    print("CCCL Merge")
    print("=" * 60)
    cccl_controls = merge_cccl(manifest, cccl)
    if [c for c in cccl.columns if c.startswith("shift_intensity")]:
        matched_cccl = (
            cccl_controls[
                [c for c in cccl.columns if c.startswith("shift_intensity")][0]
            ]
            .notna()
            .sum()
        )
        unmatched_cccl = len(manifest) - matched_cccl
        print_stat("CCCL matched", before=len(manifest), after=matched_cccl)

        stats["merges"]["cccl_instrument"] = {
            "left_rows": len(manifest),
            "right_rows": len(cccl),
            "result_rows": len(cccl_controls),
            "matched": int(matched_cccl),
            "unmatched_left": int(unmatched_cccl),
            "merge_type": "1:1_left",
        }

    # Combine all controls
    print("\n" + "=" * 60)
    print("Combining Controls")
    print("=" * 60)

    result = manifest[["file_name", "gvkey", "start_date", "year"]].copy()
    result = result.merge(comp_controls, on="file_name", how="left")
    result = result.merge(surp_controls, on="file_name", how="left")
    result = result.merge(cccl_controls, on="file_name", how="left")

    print_stat("Final result rows", value=len(result))

    # Variable construction stats
    print("\n" + "=" * 60)
    print("Variable Construction")
    print("=" * 60)
    core_cols = ["Size", "BM", "Lev", "ROA", "EPS_Growth", "SurpDec"]
    stats["processing"]["variable_coverage"] = {}
    for col in core_cols + ["CurrentRatio", "RD_Intensity"]:
        if col in result.columns:
            n = result[col].notna().sum()
            print_stat(col, value=f"{n:,} ({n / len(result) * 100:.1f}%)")
            stats["processing"]["variable_coverage"][col] = {
                "count": int(n),
                "percent": round(n / len(result) * 100, 2),
            }

    # Save by year
    print("\nSaving outputs by year...")
    for year, group in result.groupby("year"):
        output_file = paths["output_dir"] / f"firm_controls_{year}.parquet"
        group.to_parquet(output_file, index=False)
        print(f"  Saved {year}: {len(group):,} calls -> {output_file.name}")
        stats["output"]["files"].append(output_file.name)

    # Generate variable reference
    generate_variable_reference(result, paths["output_dir"] / "variable_reference.csv")

    # Update latest link
    update_latest_link(paths["latest_dir"], paths["output_dir"])

    # Output stats
    stats["output"]["final_rows"] = len(result)
    stats["output"]["final_columns"] = len(result.columns)

    # Missing values analysis
    stats["missing_values"] = analyze_missing_values(result)

    # Timing
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

    # Detect anomalies in final result (financial controls)
    print("\nDetecting anomalies in final data...")
    financial_control_cols = [
        "Size",
        "BM",
        "Lev",
        "ROA",
        "EPS_Growth",
        "SurpDec",
        "CurrentRatio",
        "RD_Intensity",
    ]
    cols_to_check = [c for c in financial_control_cols if c in result.columns]
    if cols_to_check:
        stats["quality_anomalies"] = detect_anomalies_zscore(
            result, cols_to_check, threshold=3.0
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

    # Final summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total calls processed: {len(result):,}")
    print(f"\nOutputs saved to: {paths['output_dir']}")
    print(f"Log saved to: {paths['log_file']}")

    dual_writer.close()
    sys.stdout = dual_writer.terminal


if __name__ == "__main__":
    main()
