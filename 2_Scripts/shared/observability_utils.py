#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Observability and Statistics Helpers
================================================================================
ID: shared/observability_utils
Description: Provides reusable functions for statistics, monitoring,
             anomaly detection, and performance tracking.

Inputs:
    - File paths for checksum computation
    - DataFrames for analysis
    - Process information for memory tracking

Outputs:
    - Checksum strings
    - Statistics dictionaries
    - Anomaly detection results
    - Memory usage metrics
    - Throughput calculations

Deterministic: true
================================================================================
"""

import hashlib
import psutil
import pandas as pd
from typing import Dict, List, Optional, Any
from pathlib import Path


def compute_file_checksum(filepath: Path, algorithm: str = "sha256") -> str:
    """
    Compute checksum for a file.

    Args:
        filepath: Path to file to compute checksum for
        algorithm: Hash algorithm to use (default: sha256)

    Returns:
        Hexadecimal checksum string
    """
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def print_stat(
    label: str,
    before: Optional[int] = None,
    after: Optional[int] = None,
    value: Optional[Any] = None,
    indent: int = 2,
) -> None:
    """
    Print a statistic with consistent formatting.

    Args:
        label: Statistic label
        before: Value before operation (for delta calculation)
        after: Value after operation (for delta calculation)
        value: Direct value to print
        indent: Number of spaces to indent
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


def analyze_missing_values(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Analyze missing values per column.

    Args:
        df: DataFrame to analyze

    Returns:
        Dictionary mapping column names to missing value info:
        - count: Number of missing values
        - percent: Percentage of missing values
    """
    missing = {}
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            missing[col] = {
                "count": int(null_count),
                "percent": round(null_count / len(df) * 100, 2),
            }
    return missing


def print_stats_summary(stats: Dict[str, Any]) -> None:
    """
    Print formatted summary table from statistics dictionary.

    Args:
        stats: Statistics dictionary with 'input', 'output', 'timing', 'processing' keys
    """
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


def save_stats(stats: Dict[str, Any], out_dir: Path) -> None:
    """
    Save statistics to JSON file.

    Args:
        stats: Statistics dictionary to save
        out_dir: Output directory path
    """
    import json

    stats_path = out_dir / "stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"Saved: {stats_path.name}")


def get_process_memory_mb() -> Dict[str, float]:
    """
    Get current process memory usage in MB.

    Returns:
        Dictionary with keys:
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


def calculate_throughput(rows_processed: int, duration_seconds: float) -> float:
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


def detect_anomalies_zscore(
    df: pd.DataFrame, columns: List[str], threshold: float = 3.0
) -> Dict[str, Dict[str, Any]]:
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


def detect_anomalies_iqr(
    df: pd.DataFrame, columns: List[str], multiplier: float = 3.0
) -> Dict[str, Dict[str, Any]]:
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


def compute_input_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze raw input data characteristics.

    Provides comprehensive descriptive statistics for input data including
    record counts, column types, distributions, and cardinality analysis.

    Deterministic: Same input produces same output (no random operations).

    Args:
        df: DataFrame to analyze

    Returns:
        Dictionary with keys:
        - record_count: Total number of rows
        - column_count: Total number of columns
        - memory_mb: Memory footprint in MB
        - column_types: Dict with counts of numeric, datetime, string, bool columns
        - numeric_stats: Dict mapping column_name -> {min, max, mean, median, std, q25, q75}
        - datetime_stats: Dict mapping column_name -> {min_date, max_date, span_days}
        - string_stats: Dict mapping column_name -> {avg_length, max_length, unique_count, empty_count}
        - cardinality: Dict mapping column_name -> distinct_count
    """
    import numpy as np

    stats = {
        "record_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
    }

    # Column type distribution
    type_counts = {
        "numeric": 0,
        "datetime": 0,
        "string": 0,
        "bool": 0,
        "other": 0,
    }

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            type_counts["numeric"] += 1
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            type_counts["datetime"] += 1
        elif pd.api.types.is_bool_dtype(df[col]):
            type_counts["bool"] += 1
        elif pd.api.types.is_string_dtype(df[col]) or df[col].dtype == "object":
            type_counts["string"] += 1
        else:
            type_counts["other"] += 1

    stats["column_types"] = type_counts

    # Numeric column statistics
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    stats["numeric_stats"] = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) > 0:
            stats["numeric_stats"][col] = {
                "min": round(float(series.min()), 4),
                "max": round(float(series.max()), 4),
                "mean": round(float(series.mean()), 4),
                "median": round(float(series.median()), 4),
                "std": round(float(series.std()), 4),
                "q25": round(float(series.quantile(0.25)), 4),
                "q75": round(float(series.quantile(0.75)), 4),
            }

    # Datetime column statistics
    datetime_cols = df.select_dtypes(include=["datetime64", "datetime64[ns]"]).columns.tolist()
    stats["datetime_stats"] = {}
    for col in datetime_cols:
        series = df[col].dropna()
        if len(series) > 0:
            min_date = series.min()
            max_date = series.max()
            span_days = (max_date - min_date).days
            stats["datetime_stats"][col] = {
                "min_date": min_date.isoformat() if pd.notna(min_date) else None,
                "max_date": max_date.isoformat() if pd.notna(max_date) else None,
                "span_days": int(span_days),
            }

    # String column statistics
    string_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    stats["string_stats"] = {}
    for col in string_cols:
        # Skip if column looks like it was already processed as datetime
        if col in datetime_cols:
            continue
        series = df[col].dropna()
        if len(series) > 0:
            # Convert to string and compute length statistics
            str_lengths = series.astype(str).str.len()
            stats["string_stats"][col] = {
                "avg_length": round(float(str_lengths.mean()), 2),
                "max_length": int(str_lengths.max()),
                "unique_count": int(series.nunique()),
                "empty_count": int((series == "").sum()),
            }

    # Cardinality analysis for key categorical columns
    stats["cardinality"] = {}
    categorical_cols = (
        df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
    )
    for col in categorical_cols:
        if col in datetime_cols:
            continue
        distinct_count = df[col].nunique()
        stats["cardinality"][col] = int(distinct_count)

    return stats


def compute_temporal_stats(df: pd.DataFrame, date_col: str = "start_date") -> Dict[str, Any]:
    """
    Analyze temporal coverage of the dataset.

    Provides detailed temporal statistics including year, month, quarter,
    and day-of-week distributions.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        df: DataFrame to analyze
        date_col: Name of date column to analyze (default: 'start_date')

    Returns:
        Dictionary with keys:
        - year_distribution: Dict mapping year -> count
        - month_distribution: Dict mapping month_num (1-12) -> count
        - quarter_distribution: Dict mapping quarter (1-4) -> count
        - day_of_week_distribution: Dict mapping day (0=Mon, 6=Sun) -> count
        - date_range: {earliest: ISO date, latest: ISO date, span_days: int}
        - calls_per_year: {mean: float, median: float, min: int, max: int}
        - target_year_coverage: Dict mapping year -> coverage_percentage
    """
    # Ensure date column is datetime
    if date_col not in df.columns:
        return {
            "error": f"Column '{date_col}' not found in DataFrame",
            "year_distribution": {},
            "month_distribution": {},
            "quarter_distribution": {},
            "day_of_week_distribution": {},
            "date_range": {},
            "calls_per_year": {},
            "target_year_coverage": {},
        }

    df_temp = df[[date_col]].copy()
    df_temp[date_col] = pd.to_datetime(df_temp[date_col])
    df_temp = df_temp.dropna(subset=[date_col])

    if len(df_temp) == 0:
        return {
            "error": "No valid dates found",
            "year_distribution": {},
            "month_distribution": {},
            "quarter_distribution": {},
            "day_of_week_distribution": {},
            "date_range": {},
            "calls_per_year": {},
            "target_year_coverage": {},
        }

    # Extract temporal components
    df_temp["year"] = df_temp[date_col].dt.year
    df_temp["month"] = df_temp[date_col].dt.month
    df_temp["quarter"] = df_temp[date_col].dt.quarter
    df_temp["day_of_week"] = df_temp[date_col].dt.dayofweek

    # Year distribution
    year_counts = df_temp["year"].value_counts().sort_index()
    year_dist = {int(year): int(count) for year, count in year_counts.items()}

    # Month distribution
    month_counts = df_temp["month"].value_counts().sort_index()
    month_dist = {int(month): int(count) for month, count in month_counts.items()}

    # Quarter distribution
    quarter_counts = df_temp["quarter"].value_counts().sort_index()
    quarter_dist = {int(q): int(count) for q, count in quarter_counts.items()}

    # Day of week distribution
    dow_counts = df_temp["day_of_week"].value_counts().sort_index()
    dow_dist = {int(dow): int(count) for dow, count in dow_counts.items()}

    # Date range
    earliest = df_temp[date_col].min()
    latest = df_temp[date_col].max()
    span_days = (latest - earliest).days

    # Calls per year statistics
    year_values = df_temp["year"].values
    calls_per_year = {
        "mean": round(float(year_counts.mean()), 2),
        "median": round(float(year_counts.median()), 2),
        "min": int(year_counts.min()),
        "max": int(year_counts.max()),
    }

    # Target year coverage (2002-2018)
    target_years = range(2002, 2019)
    coverage = {}
    for year in target_years:
        if year in year_dist:
            coverage[str(year)] = round(year_dist[year] / len(df_temp) * 100, 2)
        else:
            coverage[str(year)] = 0.0

    return {
        "year_distribution": year_dist,
        "month_distribution": month_dist,
        "quarter_distribution": quarter_dist,
        "day_of_week_distribution": dow_dist,
        "date_range": {
            "earliest": earliest.isoformat(),
            "latest": latest.isoformat(),
            "span_days": int(span_days),
        },
        "calls_per_year": calls_per_year,
        "target_year_coverage": coverage,
    }


def compute_entity_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze entity and quality characteristics of the dataset.

    Provides statistics about company coverage, geographic distribution,
    data quality scores, speaker data availability, and processing lags.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        df: DataFrame to analyze

    Returns:
        Dictionary with keys:
        - company_coverage: {unique_companies: int, avg_calls_per_company: float}
        - geographic_coverage: {unique_cities: int, top_cities: [{city, count}]}
        - data_quality_distribution: {mean, median, histogram: {bucket_range: count}}
        - speaker_coverage: {percent_with_speaker_data: float, speaker_record_distribution}
        - processing_lag_stats: {mean_hours, median_hours, min_hours, max_hours}
    """
    stats = {}

    # Company coverage
    if "company_id" in df.columns:
        unique_companies = df["company_id"].nunique()
        avg_calls = df.groupby("company_id").size().mean()
        stats["company_coverage"] = {
            "unique_companies": int(unique_companies),
            "avg_calls_per_company": round(float(avg_calls), 2),
        }
    elif "company_ticker" in df.columns:
        unique_companies = df["company_ticker"].nunique()
        avg_calls = df.groupby("company_ticker").size().mean()
        stats["company_coverage"] = {
            "unique_companies": int(unique_companies),
            "avg_calls_per_company": round(float(avg_calls), 2),
        }
    else:
        stats["company_coverage"] = {
            "unique_companies": 0,
            "avg_calls_per_company": 0.0,
        }

    # Geographic coverage
    if "city" in df.columns:
        unique_cities = df["city"].nunique()
        city_counts = df["city"].value_counts().head(10)  # Top 10 cities
        top_cities = [
            {"city": str(city), "count": int(count)}
            for city, count in city_counts.items()
        ]
        stats["geographic_coverage"] = {
            "unique_cities": int(unique_cities),
            "top_cities": top_cities,
        }
    else:
        stats["geographic_coverage"] = {
            "unique_cities": 0,
            "top_cities": [],
        }

    # Data quality score distribution
    if "data_quality_score" in df.columns:
        quality_scores = df["data_quality_score"].dropna()
        if len(quality_scores) > 0:
            mean_quality = quality_scores.mean()
            median_quality = quality_scores.median()

            # Create histogram buckets
            try:
                min_score = quality_scores.min()
                max_score = quality_scores.max()
                if min_score != max_score:
                    buckets = pd.cut(
                        quality_scores, bins=5, retbins=True, include_lowest=True
                    )
                    bucket_counts = quality_scores.groupby(buckets[0]).count()
                    histogram = {
                        f"{round(interval.left, 2)}-{round(interval.right, 2)}": int(
                            count
                        )
                        for interval, count in bucket_counts.items()
                    }
                else:
                    histogram = {"all_same_value": int(len(quality_scores))}
            except Exception:
                histogram = {"error": "Could not create histogram"}

            stats["data_quality_distribution"] = {
                "mean": round(float(mean_quality), 4),
                "median": round(float(median_quality), 4),
                "histogram": histogram,
            }
        else:
            stats["data_quality_distribution"] = {"error": "No quality scores available"}
    else:
        stats["data_quality_distribution"] = {"error": "Column not found"}

    # Speaker data coverage
    if "has_speaker_data" in df.columns:
        with_speaker = df[df["has_speaker_data"] == True].shape[0]
        percent_with_speaker = round(with_speaker / len(df) * 100, 2)
        stats["speaker_coverage"] = {
            "percent_with_speaker_data": percent_with_speaker,
        }

        # Speaker record count distribution
        if "speaker_record_count" in df.columns:
            speaker_counts = df["speaker_record_count"].dropna()
            if len(speaker_counts) > 0:
                stats["speaker_coverage"]["speaker_record_distribution"] = {
                    "mean": round(float(speaker_counts.mean()), 2),
                    "median": round(float(speaker_counts.median()), 2),
                    "min": int(speaker_counts.min()),
                    "max": int(speaker_counts.max()),
                }
    else:
        stats["speaker_coverage"] = {"error": "Column not found"}

    # Processing lag statistics
    if "processing_lag_hours" in df.columns:
        lag_values = df["processing_lag_hours"].dropna()
        if len(lag_values) > 0:
            stats["processing_lag_stats"] = {
                "mean_hours": round(float(lag_values.mean()), 2),
                "median_hours": round(float(lag_values.median()), 2),
                "min_hours": round(float(lag_values.min()), 2),
                "max_hours": round(float(lag_values.max()), 2),
            }
        else:
            stats["processing_lag_stats"] = {"error": "No lag data available"}
    else:
        stats["processing_lag_stats"] = {"error": "Column not found"}

    return stats


class DualWriter:
    """
    Writes to both stdout and log file verbatim.

    Attributes:
        terminal: Reference to sys.stdout
        log: File handle for log file
    """

    def __init__(self, log_path: Path):
        """
        Initialize dual-writer.

        Args:
            log_path: Path to log file
        """
        import sys

        self.terminal = sys.stdout
        self.log = open(log_path, "w", encoding="utf-8")

    def write(self, message: str) -> None:
        """
        Write message to both terminal and log file.

        Args:
            message: Message to write
        """
        self.terminal.write(message)
        self.log.write(message)

    def flush(self) -> None:
        """Flush both terminal and log file."""
        self.terminal.flush()
        self.log.flush()

    def close(self) -> None:
        """Close log file handle."""
        self.log.close()
