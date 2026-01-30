#!/usr/bin/env python3

"""

==============================================================================

STEP 3.2: Build Market Variables (VECTORIZED + CHUNKED)

==============================================================================

ID: 3.2_MarketVariables

Description: Computes stock returns and liquidity measures from CRSP.

             Uses vectorized pandas operations with year-based chunking

             for memory efficiency.



Variables Computed:

    - StockRet: Compound stock return (prev_call+5d to call-5d)

    - MarketRet: Value-weighted market return over same window

    - Amihud: Illiquidity measure (mean of |ret|/volume)

    - Corwin_Schultz: High-low spread estimator

    - Delta_Amihud, Delta_Corwin_Schultz: Event - Baseline



Deterministic: true

==============================================================================

"""

import sys

import argparse

from pathlib import Path

from datetime import datetime, timedelta

import pandas as pd

import numpy as np

import yaml

import importlib.util

import warnings

import gc

import time

import hashlib

import json

import psutil


warnings.filterwarnings("ignore")


# Dynamic import for 3.4_Utils.py

utils_path = Path(__file__).parent / "3.4_Utils.py"

spec = importlib.util.spec_from_file_location("utils", utils_path)

utils = importlib.util.module_from_spec(spec)

sys.modules["utils"] = utils

spec.loader.exec_module(utils)


from utils import generate_variable_reference

# Add parent directory to sys.path for shared module imports
import sys as _sys
from pathlib import Path as _Path

_script_dir = Path(__file__).parent.parent
_sys.path.insert(0, str(_script_dir))

# Import shared path validation utilities
from shared.path_utils import (
    validate_output_path,
    ensure_output_dir,
    validate_input_file,
    get_latest_output_dir,
)

# Import DualWriter from shared.observability_utils
from shared.observability_utils import DualWriter

# Import shared observability utilities (new Step 3.2 statistics functions)
try:
    from shared.observability_utils import (
        get_process_memory_mb,
        calculate_throughput,
        detect_anomalies_zscore,
        detect_anomalies_iqr,
        compute_step32_input_stats,
        compute_step32_process_stats,
        compute_step32_output_stats,
        generate_financial_report_markdown,
    )
    from shared.observability_utils import save_stats as save_stats_shared
    # Use local save_stats to avoid conflicts
    HAS_OBSERVABILITY = True
except ImportError:
    HAS_OBSERVABILITY = False


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
        print(f"\n{'Processing Step':<30} {'Rows':>10}")

        print("-" * 42)

        for step, count in stats["processing"].items():
            print(f"{step:<30} {count:>10,}")

    if "merges" in stats:
        print(f"\n{'Merge':<20} {'Matched':>12} {'Left Unmatched':>15}")

        print("-" * 48)

        for merge_name, merge_stats in stats["merges"].items():
            print(
                f"{merge_name:<20} {merge_stats['matched']:>12,} {merge_stats['unmatched_left']:>15,}"
            )

    print("=" * 60)


def save_stats(stats, out_dir):
    """Save statistics to JSON file."""

    stats_path = out_dir / "stats.json"

    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, default=str)

    print(f"Saved: {stats_path.name}")


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

    validate_input_file(config_path, must_exist=True)

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
        "crsp_dir": root / "1_Inputs" / "CRSP_DSF",
        "manifest_dir": manifest_dir,
        "ccm_file": root
        / "1_Inputs"
        / "CRSPCompustat_CCM"
        / "CRSPCompustat_CCM.parquet",
    }

    output_base = root / config["paths"]["outputs"] / "3_Financial_Features"

    paths["output_dir"] = output_base / timestamp

    ensure_output_dir(paths["output_dir"])

    log_base = root / config["paths"]["logs"] / "3_Financial_Features"

    ensure_output_dir(log_base)

    paths["log_file"] = log_base / f"{timestamp}_market.log"

    return paths


# ==============================================================================

# Data Loading

# ==============================================================================


def load_manifest_with_permno(manifest_dir, ccm_file):
    """Load manifest with 100% PERMNO coverage via gvkey->CCM fallback."""

    # Column pruning: only reading needed columns

    df = pd.read_parquet(
        manifest_dir / "master_sample_manifest.parquet",
        columns=["file_name", "gvkey", "start_date", "permno", "year"],
    )

    df["start_date"] = pd.to_datetime(df["start_date"])

    df["year"] = df["start_date"].dt.year

    df["permno"] = pd.to_numeric(df["permno"], errors="coerce")

    direct = df["permno"].notna().sum()

    print(
        f"  Manifest: {len(df):,} calls, direct permno: {direct:,} ({direct / len(df) * 100:.1f}%)"
    )

    # CCM fallback

    # Column pruning: only reading needed columns

    ccm = pd.read_parquet(ccm_file, columns=["gvkey", "LPERMNO"])

    ccm["gvkey_clean"] = ccm["gvkey"].astype(str).str.zfill(6)

    ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce")

    gvkey_map = ccm.groupby("gvkey_clean")["LPERMNO"].first().to_dict()

    df["gvkey_clean"] = df["gvkey"].astype(str).str.zfill(6)

    missing = df["permno"].isna()

    df.loc[missing, "permno"] = df.loc[missing, "gvkey_clean"].map(gvkey_map)

    final = df["permno"].notna().sum()

    print(f"  After CCM fallback: {final:,} ({final / len(df) * 100:.1f}%)")

    # Compute prev_call_date once

    df = df.sort_values(["gvkey", "start_date"])

    df["prev_call_date"] = df.groupby("gvkey")["start_date"].shift(1)

    return df


def load_crsp_for_years(crsp_dir, years):
    """Load CRSP for specific years only."""

    all_data = []

    for year in years:
        for q in range(1, 5):
            fp = crsp_dir / f"CRSP_DSF_{year}_Q{q}.parquet"

            if fp.exists():
                all_data.append(pd.read_parquet(fp))

    if not all_data:
        return None

    crsp = pd.concat(all_data, ignore_index=True)

    # Normalize

    col_map = {c: c.upper() for c in crsp.columns if c.lower() != "date"}

    crsp = crsp.rename(columns=col_map)

    if "DATE" in crsp.columns:
        crsp = crsp.rename(columns={"DATE": "date"})

    crsp["date"] = pd.to_datetime(crsp["date"])

    for col in ["RET", "VOL", "VWRETD", "ASKHI", "BIDLO", "PRC"]:
        if col in crsp.columns:
            crsp[col] = pd.to_numeric(crsp[col], errors="coerce")

    if "PRC" in crsp.columns:
        crsp["PRC"] = crsp["PRC"].abs()

    return crsp


# ==============================================================================

# VECTORIZED Computations (per-year chunk)

# ==============================================================================


def compute_returns_for_year(year_manifest, crsp, config):
    """Vectorized stock return computation for one year."""

    days_after = (
        config.get("step_07", {})
        .get("return_windows", {})
        .get("days_after_prev_call", 5)
    )

    days_before = (
        config.get("step_07", {})
        .get("return_windows", {})
        .get("days_before_current_call", 5)
    )

    min_days = (
        config.get("step_07", {}).get("return_windows", {}).get("min_trading_days", 10)
    )

    # Window bounds

    year_manifest = year_manifest.copy()

    year_manifest["window_start"] = year_manifest["prev_call_date"] + pd.Timedelta(
        days=days_after
    )

    year_manifest["window_end"] = year_manifest["start_date"] - pd.Timedelta(
        days=days_before
    )

    valid = year_manifest[
        year_manifest["permno"].notna()
        & year_manifest["prev_call_date"].notna()
        & (year_manifest["window_end"] > year_manifest["window_start"])
    ].copy()

    if len(valid) == 0:
        year_manifest["StockRet"] = np.nan

        year_manifest["MarketRet"] = np.nan

        return year_manifest

    valid["permno_int"] = valid["permno"].astype(int)

    crsp["PERMNO"] = crsp["PERMNO"].astype(int)

    # Merge

    merged = valid[["file_name", "permno_int", "window_start", "window_end"]].merge(
        crsp[["PERMNO", "date", "RET", "VWRETD"]],
        left_on="permno_int",
        right_on="PERMNO",
        how="inner",
    )

    merged = merged[
        (merged["date"] >= merged["window_start"])
        & (merged["date"] <= merged["window_end"])
    ]

    # Compound returns

    def compound(x):
        v = x.dropna()

        return ((1 + v).prod() - 1) * 100 if len(v) >= min_days else np.nan

    # Volatility (Annualized Standard Deviation of daily returns * 100 for percent)

    def volatility(x):
        v = x.dropna()

        # Annualize: std * sqrt(252). Multiply by 100 to match return units (%)

        return v.std() * np.sqrt(252) * 100 if len(v) >= min_days else np.nan

    stock_rets = merged.groupby("file_name")["RET"].apply(compound)

    market_rets = merged.groupby("file_name")["VWRETD"].apply(compound)

    stock_vol = merged.groupby("file_name")["RET"].apply(volatility)

    year_manifest["StockRet"] = year_manifest["file_name"].map(stock_rets)

    year_manifest["MarketRet"] = year_manifest["file_name"].map(market_rets)

    year_manifest["Volatility"] = year_manifest["file_name"].map(stock_vol)

    return year_manifest


def compute_liquidity_for_year(year_manifest, crsp, config):
    """Vectorized liquidity computation for one year."""

    event_days = config.get("step_09", {}).get("window_days", 5)

    baseline_start = config.get("step_09", {}).get("baseline_start", -35)

    baseline_end = config.get("step_09", {}).get("baseline_end", -6)

    year_manifest = year_manifest.copy()

    valid = year_manifest[year_manifest["permno"].notna()].copy()

    if len(valid) == 0:
        for col in ["Amihud", "Corwin_Schultz", "Delta_Amihud", "Delta_Corwin_Schultz"]:
            year_manifest[col] = np.nan

        return year_manifest

    valid["permno_int"] = valid["permno"].astype(int)

    valid["event_start"] = valid["start_date"] - pd.Timedelta(days=event_days)

    valid["event_end"] = valid["start_date"] + pd.Timedelta(days=event_days)

    valid["baseline_start"] = valid["start_date"] + pd.Timedelta(days=baseline_start)

    valid["baseline_end"] = valid["start_date"] + pd.Timedelta(days=baseline_end)

    crsp["PERMNO"] = crsp["PERMNO"].astype(int)

    crsp["dollar_vol"] = crsp["VOL"] * crsp["PRC"]

    # Amihud

    def amihud(df):
        v = df[(df["RET"].notna()) & (df["dollar_vol"] > 0)]

        return (
            (v["RET"].abs() / v["dollar_vol"]).mean() * 1e6 if len(v) >= 5 else np.nan
        )

    # Event Amihud

    em = valid[["file_name", "permno_int", "event_start", "event_end"]].merge(
        crsp[["PERMNO", "date", "RET", "dollar_vol"]],
        left_on="permno_int",
        right_on="PERMNO",
        how="inner",
    )

    em = em[(em["date"] >= em["event_start"]) & (em["date"] <= em["event_end"])]

    amihud_event = (
        em.groupby("file_name").apply(amihud, include_groups=False)
        if len(em) > 0
        else pd.Series(dtype=float)
    )

    # Baseline Amihud

    bm = valid[["file_name", "permno_int", "baseline_start", "baseline_end"]].merge(
        crsp[["PERMNO", "date", "RET", "dollar_vol"]],
        left_on="permno_int",
        right_on="PERMNO",
        how="inner",
    )

    bm = bm[(bm["date"] >= bm["baseline_start"]) & (bm["date"] <= bm["baseline_end"])]

    amihud_base = (
        bm.groupby("file_name").apply(amihud, include_groups=False)
        if len(bm) > 0
        else pd.Series(dtype=float)
    )

    # Corwin-Schultz

    def cs(df):
        v = df[
            (df["ASKHI"].notna())
            & (df["BIDLO"].notna())
            & (df["ASKHI"] > 0)
            & (df["BIDLO"] > 0)
        ]

        if len(v) < 5:
            return np.nan

        beta = (np.log(v["ASKHI"] / v["BIDLO"])) ** 2

        bm = beta.mean()

        if bm <= 0:
            return np.nan

        alpha = (np.sqrt(2 * bm) - np.sqrt(bm)) / (3 - 2 * np.sqrt(2))

        return max(0, 2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha)))

    # Event CS

    csm = valid[["file_name", "permno_int", "event_start", "event_end"]].merge(
        crsp[["PERMNO", "date", "ASKHI", "BIDLO"]],
        left_on="permno_int",
        right_on="PERMNO",
        how="inner",
    )

    csm = csm[(csm["date"] >= csm["event_start"]) & (csm["date"] <= csm["event_end"])]

    cs_event = (
        csm.groupby("file_name").apply(cs, include_groups=False)
        if len(csm) > 0
        else pd.Series(dtype=float)
    )

    # Baseline CS

    csb = valid[["file_name", "permno_int", "baseline_start", "baseline_end"]].merge(
        crsp[["PERMNO", "date", "ASKHI", "BIDLO"]],
        left_on="permno_int",
        right_on="PERMNO",
        how="inner",
    )

    csb = csb[
        (csb["date"] >= csb["baseline_start"]) & (csb["date"] <= csb["baseline_end"])
    ]

    cs_base = (
        csb.groupby("file_name").apply(cs, include_groups=False)
        if len(csb) > 0
        else pd.Series(dtype=float)
    )

    # Map

    year_manifest["Amihud"] = year_manifest["file_name"].map(amihud_event)

    year_manifest["Corwin_Schultz"] = year_manifest["file_name"].map(cs_event)

    year_manifest["Delta_Amihud"] = year_manifest["file_name"].map(
        amihud_event
    ) - year_manifest["file_name"].map(amihud_base)

    year_manifest["Delta_Corwin_Schultz"] = year_manifest["file_name"].map(
        cs_event
    ) - year_manifest["file_name"].map(cs_base)

    return year_manifest


# ==============================================================================

# CLI and Prerequisites

# ==============================================================================


def parse_arguments():
    """Parse command-line arguments for 3.2_MarketVariables.py."""

    parser = argparse.ArgumentParser(
        description="""

STEP 3.2: Build Market Variables



Constructs market-level variables from CRSP and IBES

data (returns, volume, analyst forecasts). Merges

with master sample for analysis.

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

    required_files = {
        "CRSP": root / "1_Inputs" / "CRSP_DSF",
        "IBES": root / "1_Inputs" / "IBES",
    }

    required_steps = {
        "1.4_AssembleManifest": "master_sample_manifest.parquet",
    }

    validate_prerequisites(required_files, required_steps)


# ==============================================================================

# Main

# ==============================================================================


def main():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    config = load_config()

    paths = setup_paths(config, timestamp)

    start_time = time.perf_counter()

    start_iso = datetime.now().isoformat()

    mem_start = get_process_memory_mb()

    memory_readings = [mem_start["rss_mb"]]

    dual_writer = DualWriter(paths["log_file"])

    sys.stdout = dual_writer

    print("=" * 60)

    print("STEP 3.2: Build Market Variables (VECTORIZED + CHUNKED)")

    print(f"Timestamp: {timestamp}")

    print("=" * 60)

    stats = {
        "step_id": "3.2_MarketVariables",
        "timestamp": timestamp,
        "input": {
            "files": [],
            "checksums": {},
            "total_rows": 0,
            "total_columns": 0,
        },
        "processing": {},
        "output": {
            "final_rows": 0,
            "final_columns": 0,
            "files": [],
            "checksums": {},
        },
        "missing_values": {},
        "merges": {},
        "timing": {
            "start_iso": start_iso,
            "end_iso": "",
            "duration_seconds": 0.0,
        },
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

    print("\nLoading manifest...")

    manifest_file = paths["manifest_dir"] / "master_sample_manifest.parquet"

    stats["input"]["files"].append(str(manifest_file))

    stats["input"]["checksums"][manifest_file.name] = compute_file_checksum(
        manifest_file
    )

    manifest = load_manifest_with_permno(paths["manifest_dir"], paths["ccm_file"])

    years = sorted(manifest["year"].unique())

    print(f"\nProcessing {len(years)} years: {years[0]} to {years[-1]}")

    stats["input"]["total_rows"] = len(manifest)

    stats["input"]["total_columns"] = len(manifest.columns)

    print_stat("Input rows", value=len(manifest))

    print_stat("Input columns", value=len(manifest.columns))

    # Collect INPUT statistics for Step 3.2 (if observability available)
    if HAS_OBSERVABILITY:
        print("\nCollecting INPUT statistics...")
        # CRSP data by year will be collected during processing
        stats["step32_input"] = {
            "manifest_stats": {
                "total_records": int(len(manifest)),
                "unique_gvkey": int(manifest["gvkey"].nunique()) if "gvkey" in manifest.columns else 0,
                "unique_permno": int(manifest["permno"].nunique()) if "permno" in manifest.columns else 0,
                "years_present": [int(y) for y in years],
            },
            "crsp_stats_by_year": {},  # Will be populated during processing
        }

    all_results = []
    per_year_stats_list = []  # For PROCESS statistics

    for year in years:
        print(f"\n{'=' * 40}")

        print(f"Year {year}")

        print("=" * 40)

        year_manifest = manifest[manifest["year"] == year].copy()

        print(f"  Calls: {len(year_manifest):,}")

        # Load CRSP for current year + previous year (for return windows)

        crsp = load_crsp_for_years(paths["crsp_dir"], [year - 1, year])

        if crsp is None:
            print(f"  WARNING: No CRSP data, skipping")

            continue

        print(f"  CRSP loaded: {len(crsp):,} observations")

        stats["processing"][f"crsp_observations_{year}"] = len(crsp)

        # Collect CRSP stats for INPUT statistics
        if HAS_OBSERVABILITY and "step32_input" in stats:
            stats["step32_input"]["crsp_stats_by_year"][str(year)] = {
                "observations": int(len(crsp)),
                "unique_stocks": int(crsp["PERMNO"].nunique()) if "PERMNO" in crsp.columns else 0,
            }

        # Collect per-year stats for PROCESS statistics
        per_year_stats_list.append({
            "year": year,
            "total_records": len(year_manifest),
            "stock_ret_count": int(year_manifest["StockRet"].notna().sum()) if "StockRet" in year_manifest.columns else 0,
            "amihud_count": int(year_manifest["Amihud"].notna().sum()) if "Amihud" in year_manifest.columns else 0,
        })

        # Compute (vectorized within year)

        year_manifest = compute_returns_for_year(year_manifest, crsp, config)

        n_ret = year_manifest["StockRet"].notna().sum()

        print(f"  StockRet: {n_ret:,} ({n_ret / len(year_manifest) * 100:.1f}%)")

        stats["processing"][f"stockret_computed_{year}"] = int(n_ret)

        year_manifest = compute_liquidity_for_year(year_manifest, crsp, config)

        n_liq = year_manifest["Amihud"].notna().sum()

        print(f"  Amihud: {n_liq:,} ({n_liq / len(year_manifest) * 100:.1f}%)")

        stats["processing"][f"amihud_computed_{year}"] = int(n_liq)

        # Save

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
        ]

        output_file = paths["output_dir"] / f"market_variables_{year}.parquet"

        year_manifest[cols].to_parquet(output_file, index=False)

        print(f"  Saved: {output_file.name}")

        stats["output"]["files"].append(output_file.name)

        all_results.append(year_manifest[cols])

        # Free memory

        del crsp

        gc.collect()

    # Summary

    all_df = pd.concat(all_results, ignore_index=True)

    generate_variable_reference(
        all_df, paths["output_dir"] / "market_variable_reference.csv"
    )

    stats["output"]["final_rows"] = len(all_df)

    stats["output"]["final_columns"] = len(all_df.columns)

    stats["missing_values"] = analyze_missing_values(all_df)

    # Collect PROCESS and OUTPUT statistics for Step 3.2 (if observability available)
    if HAS_OBSERVABILITY and per_year_stats_list:
        print("\nCollecting PROCESS statistics...")
        stats["step32_process"] = compute_step32_process_stats(
            per_year_stats=per_year_stats_list,
        )

        print("\nCollecting OUTPUT statistics...")
        variables_list = ["StockRet", "MarketRet", "Amihud", "Corwin_Schultz", "Delta_Amihud", "Delta_Corwin_Schultz", "Volatility"]
        stats["step32_output"] = compute_step32_output_stats(
            output_df=all_df,
            variables_list=variables_list,
        )

        # Generate report
        print("\nGenerating Step 3.2 report...")
        report_path = paths["output_dir"] / "report_step_3_2.md"
        generate_financial_report_markdown(
            input_stats=stats.get("step32_input", {}),
            process_stats=stats.get("step32_process", {}),
            output_stats=stats.get("step32_output", {}),
            step_name="3.2_MarketVariables",
            output_path=report_path,
        )
        print(f"  Report saved to: {report_path.name}")

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

    # Detect anomalies in final data (market variables)

    print("\nDetecting anomalies in final data...")

    market_var_cols = [
        "StockRet",
        "MarketRet",
        "Amihud",
        "Corwin_Schultz",
        "Delta_Amihud",
        "Delta_Corwin_Schultz",
        "Volatility",
    ]

    cols_to_check = [c for c in market_var_cols if c in all_df.columns]

    if cols_to_check:
        stats["quality_anomalies"] = detect_anomalies_zscore(
            all_df, cols_to_check, threshold=3.0
        )

        total_anomalies = sum(a["count"] for a in stats["quality_anomalies"].values())

        print(
            f"  Anomalies detected: {total_anomalies} across {len(stats['quality_anomalies'])} columns"
        )

    else:
        stats["quality_anomalies"] = {}

        print("  No numeric columns to check for anomalies")

    print("\n" + "=" * 60)

    print("SUMMARY")

    print("=" * 60)

    print(f"Total: {len(all_df):,} calls")

    for col in ["StockRet", "MarketRet", "Amihud", "Corwin_Schultz"]:
        n = all_df[col].notna().sum()

        print(f"  {col}: {n:,} ({n / len(all_df) * 100:.1f}%)")

    print(f"\nOutputs: {paths['output_dir']}")

    print_stats_summary(stats)

    save_stats(stats, paths["output_dir"])

    dual_writer.close()

    sys.stdout = dual_writer.terminal


if __name__ == "__main__":
    args = parse_arguments()

    root = Path(__file__).parent.parent.parent

    if args.dry_run:
        print("Dry-run mode: validating inputs...")

        check_prerequisites(root)
        sys.exit(0)

    check_prerequisites(root)

    main()
