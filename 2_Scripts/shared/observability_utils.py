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


def compute_linking_input_stats(df_input: pd.DataFrame, df_ccm: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze input and reference data for entity linking.

    Provides comprehensive statistics about the input metadata and CCM reference
    database, including coverage analysis of key identifiers used in matching.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        df_input: Input metadata DataFrame (from step 1.1)
        df_ccm: CCM reference database DataFrame

    Returns:
        Dictionary with keys:
        - input_metadata: {record_count, unique_companies, column_count, memory_mb}
        - reference_database: {total_records, unique_gvkey, unique_lpermno,
                               date_coverage: {earliest: ISO, latest: ISO, span_days}}
        - coverage_metrics: {permno_coverage_pct, cusip_coverage_pct,
                             ticker_coverage_pct, name_coverage_pct}
    """
    stats = {}

    # Input metadata characteristics
    stats["input_metadata"] = {
        "record_count": int(len(df_input)),
        "unique_companies": int(df_input["company_id"].nunique()) if "company_id" in df_input.columns else 0,
        "column_count": int(len(df_input.columns)),
        "memory_mb": round(df_input.memory_usage(deep=True).sum() / (1024 * 1024), 2),
    }

    # CCM reference database characteristics
    stats["reference_database"] = {
        "total_records": int(len(df_ccm)),
        "unique_gvkey": int(df_ccm["gvkey"].nunique()) if "gvkey" in df_ccm.columns else 0,
        "unique_lpermno": int(df_ccm["LPERMNO"].nunique()) if "LPERMNO" in df_ccm.columns else 0,
    }

    # CCM date coverage
    if "LINKDT" in df_ccm.columns and "LINKENDDT_dt" in df_ccm.columns:
        linkdt = df_ccm["LINKDT"].dropna()
        linkenddt = df_ccm["LINKENDDT_dt"].dropna()
        if len(linkdt) > 0 and len(linkenddt) > 0:
            stats["reference_database"]["date_coverage"] = {
                "earliest": linkdt.min().isoformat(),
                "latest": linkenddt.max().isoformat(),
                "span_days": int((linkenddt.max() - linkdt.min()).days),
            }

    # Coverage analysis - what percentage of input companies have each identifier
    total_companies = stats["input_metadata"]["unique_companies"]

    coverage = {}
    if "permno" in df_input.columns:
        permno_available = df_input[df_input["permno"].notna() & (df_input["permno"] != "")]["company_id"].nunique()
        coverage["permno_coverage_pct"] = round(permno_available / total_companies * 100, 2) if total_companies > 0 else 0.0

    if "cusip" in df_input.columns:
        cusip_available = df_input[df_input["cusip"].notna() & (df_input["cusip"] != "")]["company_id"].nunique()
        coverage["cusip_coverage_pct"] = round(cusip_available / total_companies * 100, 2) if total_companies > 0 else 0.0

    if "company_ticker" in df_input.columns:
        ticker_available = df_input[df_input["company_ticker"].notna() & (df_input["company_ticker"] != "")]["company_id"].nunique()
        coverage["ticker_coverage_pct"] = round(ticker_available / total_companies * 100, 2) if total_companies > 0 else 0.0

    if "company_name" in df_input.columns:
        name_available = df_input[df_input["company_name"].notna() & (df_input["company_name"] != "")]["company_id"].nunique()
        coverage["name_coverage_pct"] = round(name_available / total_companies * 100, 2) if total_companies > 0 else 0.0

    stats["coverage_metrics"] = coverage

    return stats


def compute_linking_process_stats(unique_df: pd.DataFrame, stats_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze 4-tier matching process outcomes.

    Provides detailed funnel analysis of the entity linking process, including
    match rates at each tier, link quality distribution, and attrition tracking.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        unique_df: DataFrame with unique companies after matching (contains gvkey, link_quality, link_method)
        stats_dict: Statistics dictionary containing tier match counts from main execution

    Returns:
        Dictionary with keys:
        - funnel_analysis: {tier1_candidates, tier1_matched, tier2_candidates, tier2_matched,
                            tier3_candidates, tier3_matched, total_matched}
        - match_rates: {tier1_match_pct, tier2_match_pct, tier3_match_pct, overall_match_pct}
        - link_quality_distribution: {quality_100_count, quality_90_count, quality_80_count}
        - link_method_distribution: {permno_date_count, cusip8_date_count, name_fuzzy_count}
    """
    stats = {}

    # Get tier counts from stats_dict (populated by main execution)
    tier1_matched = stats_dict.get("linking", {}).get("tier1_matched", 0)
    tier2_matched = stats_dict.get("linking", {}).get("tier2_matched", 0)
    tier3_matched = stats_dict.get("linking", {}).get("tier3_matched", 0)
    total_unique = stats_dict.get("linking", {}).get("unique_companies", len(unique_df))

    # Calculate candidates (approximately - unmatched before each tier)
    tier1_candidates = total_unique
    tier2_candidates = total_unique - tier1_matched
    tier3_candidates = total_unique - tier2_matched

    stats["funnel_analysis"] = {
        "tier1_candidates": int(tier1_candidates),
        "tier1_matched": int(tier1_matched),
        "tier2_candidates": int(tier2_candidates),
        "tier2_matched": int(tier2_matched - tier1_matched) if tier2_matched > tier1_matched else 0,
        "tier3_candidates": int(tier3_candidates),
        "tier3_matched": int(tier3_matched - tier2_matched) if tier3_matched > tier2_matched else 0,
        "total_matched": int(tier3_matched),
    }

    # Match rate calculations
    stats["match_rates"] = {}
    if tier1_candidates > 0:
        stats["match_rates"]["tier1_match_pct"] = round(tier1_matched / tier1_candidates * 100, 2)
    if tier2_candidates > 0:
        tier2_new_matches = stats["funnel_analysis"]["tier2_matched"]
        stats["match_rates"]["tier2_match_pct"] = round(tier2_new_matches / tier2_candidates * 100, 2)
    if tier3_candidates > 0:
        tier3_new_matches = stats["funnel_analysis"]["tier3_matched"]
        stats["match_rates"]["tier3_match_pct"] = round(tier3_new_matches / tier3_candidates * 100, 2)
    if total_unique > 0:
        stats["match_rates"]["overall_match_pct"] = round(tier3_matched / total_unique * 100, 2)

    # Link quality distribution (from link_quality column)
    if "link_quality" in unique_df.columns:
        quality_counts = unique_df["link_quality"].value_counts().sort_index()
        stats["link_quality_distribution"] = {
            "quality_100_count": int(quality_counts.get(100, 0)),
            "quality_90_count": int(quality_counts.get(90, 0)),
            "quality_80_count": int(quality_counts.get(80, 0)),
        }

        # Add percentages
        total_quality_matches = sum(stats["link_quality_distribution"].values())
        if total_quality_matches > 0:
            stats["link_quality_distribution"]["quality_100_pct"] = round(
                stats["link_quality_distribution"]["quality_100_count"] / total_quality_matches * 100, 2
            )
            stats["link_quality_distribution"]["quality_90_pct"] = round(
                stats["link_quality_distribution"]["quality_90_count"] / total_quality_matches * 100, 2
            )
            stats["link_quality_distribution"]["quality_80_pct"] = round(
                stats["link_quality_distribution"]["quality_80_count"] / total_quality_matches * 100, 2
            )

    # Link method distribution (from link_method column)
    if "link_method" in unique_df.columns:
        method_counts = unique_df["link_method"].value_counts()
        stats["link_method_distribution"] = {
            "permno_date_count": int(method_counts.get("permno_date", 0)),
            "cusip8_date_count": int(method_counts.get("cusip8_date", 0)),
            "name_fuzzy_count": int(method_counts.get("name_fuzzy", 0)),
        }

    return stats


def compute_linking_output_stats(df_linked: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze linked entities output characteristics.

    Provides comprehensive statistics about the final linked dataset, including
    linkage success rates, industry coverage, SIC distribution, and quality metrics.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        df_linked: Final linked metadata DataFrame (with gvkey, ff12_code, ff48_name, sic, etc.)

    Returns:
        Dictionary with keys:
        - linkage_summary: {total_calls_linked, unique_companies_linked, unique_gvkey_assigned,
                           linkage_success_rate, calls_per_company_avg}
        - industry_coverage: {ff12_assigned, ff12_unique_industries, ff12_completion_pct,
                             ff48_assigned, ff48_unique_industries, ff48_completion_pct}
        - sic_distribution: {unique_sic_codes, top_industries: [{sic, count, percentage}]}
        - quality_metrics: {avg_link_quality, link_quality_by_method: {method: avg_quality}}
        - temporal_coverage: {earliest_date: ISO, latest_date: ISO} (if date column exists)
    """
    stats = {}

    total_calls = len(df_linked)

    # Linkage success summary
    unique_companies = df_linked["company_id"].nunique() if "company_id" in df_linked.columns else 0
    unique_gvkey = df_linked["gvkey"].nunique() if "gvkey" in df_linked.columns else 0

    stats["linkage_summary"] = {
        "total_calls_linked": int(total_calls),
        "unique_companies_linked": int(unique_companies),
        "unique_gvkey_assigned": int(unique_gvkey),
        "calls_per_company_avg": round(total_calls / unique_companies, 2) if unique_companies > 0 else 0.0,
    }

    # Calculate linkage success rate (from input perspective - not available here, only relative stats)
    # The success rate relative to unique companies
    if unique_companies > 0:
        stats["linkage_summary"]["company_linkage_rate"] = round(unique_gvkey / unique_companies * 100, 2)

    # Industry coverage - FF12
    if "ff12_code" in df_linked.columns:
        ff12_assigned = df_linked["ff12_code"].notna().sum()
        ff12_unique = df_linked["ff12_code"].nunique()
        stats["industry_coverage"] = {
            "ff12_assigned": int(ff12_assigned),
            "ff12_unique_industries": int(ff12_unique),
            "ff12_completion_pct": round(ff12_assigned / total_calls * 100, 2) if total_calls > 0 else 0.0,
        }
    else:
        stats["industry_coverage"] = {"error": "FF12 columns not found"}

    # Industry coverage - FF48
    if "ff48_code" in df_linked.columns:
        ff48_assigned = df_linked["ff48_code"].notna().sum()
        ff48_unique = df_linked["ff48_code"].nunique()
        stats["industry_coverage"]["ff48_assigned"] = int(ff48_assigned)
        stats["industry_coverage"]["ff48_unique_industries"] = int(ff48_unique)
        stats["industry_coverage"]["ff48_completion_pct"] = round(ff48_assigned / total_calls * 100, 2) if total_calls > 0 else 0.0

    # SIC code distribution
    if "sic" in df_linked.columns:
        sic_counts = df_linked["sic"].value_counts().head(10)  # Top 10 SICs
        top_industries = []
        for sic, count in sic_counts.items():
            top_industries.append({
                "sic": int(sic) if pd.notna(sic) else None,
                "count": int(count),
                "percentage": round(count / total_calls * 100, 2) if total_calls > 0 else 0.0,
            })

        stats["sic_distribution"] = {
            "unique_sic_codes": int(df_linked["sic"].nunique()),
            "top_industries": top_industries,
        }
    else:
        stats["sic_distribution"] = {"error": "SIC column not found"}

    # Quality metrics
    if "link_quality" in df_linked.columns:
        quality_values = df_linked["link_quality"].dropna()
        if len(quality_values) > 0:
            stats["quality_metrics"] = {
                "avg_link_quality": round(float(quality_values.mean()), 2),
            }

            # Link quality by method
            if "link_method" in df_linked.columns:
                quality_by_method = df_linked.groupby("link_method")["link_quality"].mean().sort_index()
                stats["quality_metrics"]["link_quality_by_method"] = {
                    method: round(float(avg_quality), 2)
                    for method, avg_quality in quality_by_method.items()
                }
        else:
            stats["quality_metrics"] = {"error": "No quality data available"}
    else:
        stats["quality_metrics"] = {"error": "link_quality column not found"}

    # Temporal coverage
    if "start_date" in df_linked.columns:
        date_col = pd.to_datetime(df_linked["start_date"]).dropna()
        if len(date_col) > 0:
            stats["temporal_coverage"] = {
                "earliest_date": date_col.min().isoformat(),
                "latest_date": date_col.max().isoformat(),
            }

    return stats


def collect_fuzzy_match_samples(unique_df: pd.DataFrame, n_samples: int = 5) -> Dict[str, Any]:
    """
    Collect fuzzy name match examples for review.

    Provides samples of Tier 3 fuzzy matches, including both high-score (>98)
    and borderline (92-95) cases to assess matching quality.

    Deterministic: Same input produces same output (sorted, limited samples).

    Args:
        unique_df: DataFrame with unique companies after matching (must contain link_method, company_name, conm, gvkey, sic)
        n_samples: Number of samples to collect per category (default: 5)

    Returns:
        Dictionary with keys:
        - high_score: List of high-score fuzzy matches (>98)
        - borderline: List of borderline fuzzy matches (92-95)
        Each sample contains: company_id, company_name, conm (matched name), score, gvkey, sic
    """
    samples = {"high_score": [], "borderline": []}

    # Filter for fuzzy matches
    fuzzy_mask = unique_df["link_method"] == "name_fuzzy"
    fuzzy_df = unique_df[fuzzy_mask].copy()

    if len(fuzzy_df) == 0:
        return samples

    # Check if fuzzy_score column exists (it might not in unique_df after processing)
    # If not, we'll use link_quality as a proxy (80 for fuzzy matches)
    if "fuzzy_score" in fuzzy_df.columns:
        fuzzy_df["score"] = fuzzy_df["fuzzy_score"]
    else:
        # All fuzzy matches have link_quality = 80, but we don't have actual scores
        # Return empty samples since we can't distinguish high vs borderline
        return samples

    # Get high-score matches (>98)
    high_score_df = fuzzy_df[fuzzy_df["score"] > 98].sort_values("score", ascending=False)
    for _, row in high_score_df.head(n_samples).iterrows():
        samples["high_score"].append({
            "company_id": str(row.get("company_id", "")),
            "company_name": str(row.get("company_name", "")) if pd.notna(row.get("company_name")) else "",
            "matched_name": str(row.get("conm", "")) if pd.notna(row.get("conm")) else "",
            "score": round(float(row.get("score", 0)), 1),
            "gvkey": str(row.get("gvkey", "")) if pd.notna(row.get("gvkey")) else "",
            "sic": int(row["sic"]) if pd.notna(row.get("sic")) else None,
        })

    # Get borderline matches (92-95)
    borderline_df = fuzzy_df[(fuzzy_df["score"] >= 92) & (fuzzy_df["score"] <= 95)].sort_values("score", ascending=False)
    for _, row in borderline_df.head(n_samples).iterrows():
        samples["borderline"].append({
            "company_id": str(row.get("company_id", "")),
            "company_name": str(row.get("company_name", "")) if pd.notna(row.get("company_name")) else "",
            "matched_name": str(row.get("conm", "")) if pd.notna(row.get("conm")) else "",
            "score": round(float(row.get("score", 0)), 1),
            "gvkey": str(row.get("gvkey", "")) if pd.notna(row.get("gvkey")) else "",
            "sic": int(row["sic"]) if pd.notna(row.get("sic")) else None,
        })

    return samples


def collect_tier_match_samples(unique_df: pd.DataFrame, n_samples: int = 3) -> Dict[str, Any]:
    """
    Collect Tier 1 and Tier 2 match examples for review.

    Provides samples of high-quality PERMNO and CUSIP8 matches to demonstrate
    precise identifier-based linkage.

    Deterministic: Same input produces same output (random seed set).

    Args:
        unique_df: DataFrame with unique companies after matching (must contain link_method, permno/cusip8, gvkey, conm, sic, link_quality)
        n_samples: Number of samples to collect per tier (default: 3)

    Returns:
        Dictionary with keys:
        - tier1: List of Tier 1 (PERMNO) match examples
        - tier2: List of Tier 2 (CUSIP8) match examples
        Each sample contains: company_id, permno/cusip8, gvkey, conm, sic, link_quality
    """
    import random

    samples = {"tier1": [], "tier2": []}

    # Set random seed for deterministic sampling
    random.seed(42)

    # Tier 1: PERMNO matches
    tier1_mask = unique_df["link_method"] == "permno_date"
    tier1_df = unique_df[tier1_mask].copy()

    if len(tier1_df) > 0:
        # Sample n_samples random examples
        sample_size = min(n_samples, len(tier1_df))
        tier1_samples = tier1_df.sample(n=sample_size, random_state=42)

        for _, row in tier1_samples.iterrows():
            samples["tier1"].append({
                "company_id": str(row.get("company_id", "")),
                "permno": str(row.get("permno", "")) if pd.notna(row.get("permno")) else "",
                "gvkey": str(row.get("gvkey", "")) if pd.notna(row.get("gvkey")) else "",
                "conm": str(row.get("conm", "")) if pd.notna(row.get("conm")) else "",
                "sic": int(row["sic"]) if pd.notna(row.get("sic")) else None,
                "link_quality": int(row.get("link_quality", 100)),
            })

    # Tier 2: CUSIP8 matches
    tier2_mask = unique_df["link_method"] == "cusip8_date"
    tier2_df = unique_df[tier2_mask].copy()

    if len(tier2_df) > 0:
        # Sample n_samples random examples
        sample_size = min(n_samples, len(tier2_df))
        tier2_samples = tier2_df.sample(n=sample_size, random_state=42)

        for _, row in tier2_samples.iterrows():
            samples["tier2"].append({
                "company_id": str(row.get("company_id", "")),
                "cusip8": str(row.get("cusip8", "")) if pd.notna(row.get("cusip8")) else "",
                "gvkey": str(row.get("gvkey", "")) if pd.notna(row.get("gvkey")) else "",
                "conm": str(row.get("conm", "")) if pd.notna(row.get("conm")) else "",
                "sic": int(row["sic"]) if pd.notna(row.get("sic")) else None,
                "link_quality": int(row.get("link_quality", 90)),
            })

    return samples


def collect_unmatched_samples(df_original: pd.DataFrame, unique_df: pd.DataFrame, n_samples: int = 5) -> List[Dict[str, Any]]:
    """
    Collect unmatched company samples for analysis.

    Provides examples of companies that could not be matched, with information
    about what identifiers were available to diagnose matching failures.

    Deterministic: Same input produces same output (sorted, limited samples).

    Args:
        df_original: Original metadata DataFrame (before linking, must contain company_id, company_name, permno, cusip, company_ticker)
        unique_df: DataFrame with unique companies after matching (must contain company_id, gvkey)
        n_samples: Number of samples to collect (default: 5)

    Returns:
        List of unmatched company samples, each containing:
        - company_id, company_name, has_permno, has_cusip, has_ticker, likely_reason
    """
    import random

    # Set random seed for deterministic sampling
    random.seed(42)

    samples = []

    # Find unmatched companies (gvkey is NaN in unique_df)
    unmatched_mask = unique_df["gvkey"].isna()
    unmatched_company_ids = set(unique_df[unmatched_mask]["company_id"].unique())

    if len(unmatched_company_ids) == 0:
        return samples

    # Get unmatched companies from original df
    unmatched_df = df_original[df_original["company_id"].isin(unmatched_company_ids)].drop_duplicates("company_id")

    # Sample n_samples unmatched companies
    sample_size = min(n_samples, len(unmatched_df))
    unmatched_samples = unmatched_df.sample(n=sample_size, random_state=42)

    for _, row in unmatched_samples.iterrows():
        # Check what identifiers are available
        has_permno = pd.notna(row.get("permno")) and str(row.get("permno", "")) != ""
        has_cusip = pd.notna(row.get("cusip")) and str(row.get("cusip", "")) != ""
        has_ticker = pd.notna(row.get("company_ticker")) and str(row.get("company_ticker", "")) != ""
        has_name = pd.notna(row.get("company_name")) and str(row.get("company_name", "")) != ""

        # Classify likely reason for no match
        if not has_permno and not has_cusip and not has_ticker:
            likely_reason = "missing_identifiers"
        elif has_name:
            likely_reason = "no_ccm_match"
        else:
            likely_reason = "unknown"

        samples.append({
            "company_id": str(row.get("company_id", "")),
            "company_name": str(row.get("company_name", "")) if pd.notna(row.get("company_name")) else "",
            "has_permno": bool(has_permno),
            "has_cusip": bool(has_cusip),
            "has_ticker": bool(has_ticker),
            "likely_reason": likely_reason,
        })

    return samples


def collect_before_after_samples(df_original: pd.DataFrame, df_linked: pd.DataFrame, n_samples: int = 3) -> List[Dict[str, Any]]:
    """
    Collect before/after examples showing the linking transformation.

    Provides concrete examples of how company records are enriched with CCM
    data through the entity linking process.

    Deterministic: Same input produces same output (random seed set).

    Args:
        df_original: Original metadata DataFrame (must contain company_id, company_name, company_ticker, permno, cusip)
        df_linked: Final linked metadata DataFrame (must contain company_id, gvkey, conm, sic, ff12_name, ff48_name, link_method, link_quality)
        n_samples: Number of samples to collect (default: 3)

    Returns:
        List of before/after examples, each containing:
        - before: {company_id, company_name, company_ticker, permno, cusip}
        - after: {gvkey, conm, sic, ff12_name, ff48_name, link_method, link_quality}
    """
    import random

    # Set random seed for deterministic sampling
    random.seed(42)

    samples = []

    # Sample successfully linked companies
    linked_companies = df_linked["company_id"].unique()
    sample_size = min(n_samples, len(linked_companies))
    sampled_ids = random.sample(list(linked_companies), sample_size)

    for company_id in sampled_ids:
        # Get original record
        original_rows = df_original[df_original["company_id"] == company_id]
        if len(original_rows) == 0:
            continue
        orig_row = original_rows.iloc[0]

        # Get linked record
        linked_rows = df_linked[df_linked["company_id"] == company_id]
        if len(linked_rows) == 0:
            continue
        link_row = linked_rows.iloc[0]

        samples.append({
            "before": {
                "company_id": str(orig_row.get("company_id", "")),
                "company_name": str(orig_row.get("company_name", "")) if pd.notna(orig_row.get("company_name")) else "",
                "company_ticker": str(orig_row.get("company_ticker", "")) if pd.notna(orig_row.get("company_ticker")) else "",
                "permno": str(orig_row.get("permno", "")) if pd.notna(orig_row.get("permno")) else "",
                "cusip": str(orig_row.get("cusip", "")) if pd.notna(orig_row.get("cusip")) else "",
            },
            "after": {
                "gvkey": str(link_row.get("gvkey", "")) if pd.notna(link_row.get("gvkey")) else "",
                "conm": str(link_row.get("conm", "")) if pd.notna(link_row.get("conm")) else "",
                "sic": int(link_row["sic"]) if pd.notna(link_row.get("sic")) else None,
                "ff12_name": str(link_row.get("ff12_name", "")) if pd.notna(link_row.get("ff12_name")) else "",
                "ff48_name": str(link_row.get("ff48_name", "")) if pd.notna(link_row.get("ff48_name")) else "",
                "link_method": str(link_row.get("link_method", "")) if pd.notna(link_row.get("link_method")) else "",
                "link_quality": int(link_row.get("link_quality", 0)),
            }
        })

    return samples


def compute_tenure_input_stats(df_input: pd.DataFrame, df_ceo: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze Execucomp input data for CEO tenure mapping.

    Provides comprehensive statistics about the Execucomp dataset characteristics,
    including CEO subset analysis, date field coverage, and executive name availability.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        df_input: Full Execucomp DataFrame
        df_ceo: CEO subset DataFrame (filtered by ceoann='CEO' or becameceo not null)

    Returns:
        Dictionary with keys:
        - overall_execucomp: {total_records, unique_gvkey, unique_execid, date_range}
        - ceo_subset: {ceo_records, pct_of_total, unique_ceo_firms, unique_ceo_executives}
        - date_field_coverage: {becameceo_available_pct, leftofc_available_pct}
        - ceo_indicators: {ceoann_ceo_count, becameceo_nonnull_count}
        - name_coverage: {exec_fullname_available_pct}
    """
    stats = {}

    # Overall Execucomp characteristics
    stats["overall_execucomp"] = {
        "total_records": int(len(df_input)),
        "unique_gvkey": int(df_input["gvkey"].nunique()) if "gvkey" in df_input.columns else 0,
        "unique_execid": int(df_input["execid"].nunique()) if "execid" in df_input.columns else 0,
    }

    # Date range from year column
    if "year" in df_input.columns:
        year_series = df_input["year"].dropna()
        if len(year_series) > 0:
            stats["overall_execucomp"]["date_range"] = {
                "earliest_year": int(year_series.min()),
                "latest_year": int(year_series.max()),
                "span_years": int(year_series.max() - year_series.min()),
            }

    # CEO subset analysis
    total_records = len(df_input)
    ceo_records = len(df_ceo)

    stats["ceo_subset"] = {
        "ceo_records": int(ceo_records),
        "pct_of_total": round(ceo_records / total_records * 100, 2) if total_records > 0 else 0.0,
        "unique_ceo_firms": int(df_ceo["gvkey"].nunique()) if "gvkey" in df_ceo.columns else 0,
        "unique_ceo_executives": int(df_ceo["execid"].nunique()) if "execid" in df_ceo.columns else 0,
    }

    # Date field coverage
    if "becameceo" in df_ceo.columns:
        becameceo_available = df_ceo["becameceo"].notna().sum()
        stats["date_field_coverage"] = {
            "becameceo_available_pct": round(becameceo_available / len(df_ceo) * 100, 2) if len(df_ceo) > 0 else 0.0,
        }

    if "leftofc" in df_ceo.columns:
        leftofc_available = df_ceo["leftofc"].notna().sum()
        stats["date_field_coverage"]["leftofc_available_pct"] = round(leftofc_available / len(df_ceo) * 100, 2) if len(df_ceo) > 0 else 0.0

    # CEO indicators
    if "ceoann" in df_ceo.columns:
        ceoann_ceo_count = (df_ceo["ceoann"] == "CEO").sum()
        stats["ceo_indicators"] = {
            "ceoann_ceo_count": int(ceoann_ceo_count),
        }

    if "becameceo" in df_ceo.columns:
        becameceo_nonnull = df_ceo["becameceo"].notna().sum()
        stats["ceo_indicators"]["becameceo_nonnull_count"] = int(becameceo_nonnull)

    # Executive name coverage
    if "exec_fullname" in df_ceo.columns:
        name_available = df_ceo["exec_fullname"].notna().sum()
        stats["name_coverage"] = {
            "exec_fullname_available_pct": round(name_available / len(df_ceo) * 100, 2) if len(df_ceo) > 0 else 0.0,
        }

    return stats


def compute_tenure_process_stats(episodes_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze tenure episode construction and linking process.

    Provides detailed statistics about episode building, tenure length distribution,
    predecessor linking success, and date validity checks.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        episodes_df: DataFrame with tenure episodes (must contain gvkey, execid, start_date, end_date, prev_execid)

    Returns:
        Dictionary with keys:
        - episode_counts: {total_episodes, episodes_per_firm: {mean, median, min, max},
                         episodes_per_ceo: {mean, median, min, max}}
        - tenure_distribution: {mean_months, median_months, min_months, max_months, std_months,
                               buckets: {<1yr, 1-3yr, 3-5yr, 5-10yr, 10+yr: {count, pct}}}
        - predecessor_linking: {linked_count, orphan_count, link_rate_pct}
        - date_validity: {future_dates, end_before_start, active_ceo_count}
    """
    stats = {}

    # Ensure datetime columns
    if "start_date" in episodes_df.columns:
        episodes_df["start_date"] = pd.to_datetime(episodes_df["start_date"])
    if "end_date" in episodes_df.columns:
        episodes_df["end_date"] = pd.to_datetime(episodes_df["end_date"])

    # Episode counts
    total_episodes = len(episodes_df)

    # Episodes per firm
    if "gvkey" in episodes_df.columns:
        episodes_per_firm = episodes_df.groupby("gvkey").size()
        stats["episode_counts"] = {
            "total_episodes": int(total_episodes),
            "episodes_per_firm": {
                "mean": round(float(episodes_per_firm.mean()), 2),
                "median": round(float(episodes_per_firm.median()), 2),
                "min": int(episodes_per_firm.min()),
                "max": int(episodes_per_firm.max()),
            }
        }

    # Episodes per CEO
    if "execid" in episodes_df.columns:
        episodes_per_ceo = episodes_df.groupby("execid").size()
        stats["episode_counts"]["episodes_per_ceo"] = {
            "mean": round(float(episodes_per_ceo.mean()), 2),
            "median": round(float(episodes_per_ceo.median()), 2),
            "min": int(episodes_per_ceo.min()),
            "max": int(episodes_per_ceo.max()),
        }

    # Tenure length distribution
    if "start_date" in episodes_df.columns and "end_date" in episodes_df.columns:
        # Calculate tenure in months
        episodes_df["tenure_months"] = (
            (episodes_df["end_date"] - episodes_df["start_date"]).dt.total_seconds() / (30 * 24 * 3600)
        )

        tenure_months = episodes_df["tenure_months"].dropna()

        stats["tenure_distribution"] = {
            "mean_months": round(float(tenure_months.mean()), 2),
            "median_months": round(float(tenure_months.median()), 2),
            "min_months": round(float(tenure_months.min()), 2),
            "max_months": round(float(tenure_months.max()), 2),
            "std_months": round(float(tenure_months.std()), 2),
        }

        # Tenure buckets
        buckets = {
            "<1 year": 0,
            "1-3 years": 0,
            "3-5 years": 0,
            "5-10 years": 0,
            "10+ years": 0,
        }

        buckets["<1 year"] = int((tenure_months < 12).sum())
        buckets["1-3 years"] = int(((tenure_months >= 12) & (tenure_months < 36)).sum())
        buckets["3-5 years"] = int(((tenure_months >= 36) & (tenure_months < 60)).sum())
        buckets["5-10 years"] = int(((tenure_months >= 60) & (tenure_months < 120)).sum())
        buckets["10+ years"] = int((tenure_months >= 120).sum())

        # Calculate percentages
        bucket_stats = {}
        for bucket_name, count in buckets.items():
            bucket_pct = round(count / total_episodes * 100, 2) if total_episodes > 0 else 0.0
            bucket_stats[bucket_name] = {
                "count": count,
                "pct": bucket_pct,
            }

        stats["tenure_distribution"]["buckets"] = bucket_stats

    # Predecessor linking
    if "prev_execid" in episodes_df.columns:
        linked_count = episodes_df["prev_execid"].notna().sum()
        orphan_count = episodes_df["prev_execid"].isna().sum()

        stats["predecessor_linking"] = {
            "linked_count": int(linked_count),
            "orphan_count": int(orphan_count),
            "link_rate_pct": round(linked_count / total_episodes * 100, 2) if total_episodes > 0 else 0.0,
        }

    # Date validity checks
    today = pd.Timestamp.now()

    if "start_date" in episodes_df.columns:
        future_dates = int((episodes_df["start_date"] > today).sum())
        stats["date_validity"] = {
            "future_dates": future_dates,
        }

    if "start_date" in episodes_df.columns and "end_date" in episodes_df.columns:
        end_before_start = int((episodes_df["end_date"] < episodes_df["start_date"]).sum())
        stats["date_validity"]["end_before_start"] = end_before_start

        # Count active CEOs (end_date imputed to 2025-12-31 or future dates)
        active_ceo_cutoff = pd.Timestamp("2025-01-01")
        active_ceo_count = int((episodes_df["end_date"] >= active_ceo_cutoff).sum())
        stats["date_validity"]["active_ceo_count"] = active_ceo_count

    return stats


def compute_tenure_output_stats(monthly_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze monthly tenure panel output characteristics.

    Provides comprehensive statistics about the monthly panel, including temporal coverage,
    CEO turnover rates, predecessor information coverage, and multi-CEO firm analysis.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        monthly_df: Monthly tenure panel DataFrame (must contain gvkey, year, month, date, ceo_id, prev_ceo_id)

    Returns:
        Dictionary with keys:
        - panel_dimensions: {total_firm_months, unique_firms, unique_ceos, date_range: {earliest, latest, span_years}}
        - temporal_coverage: [{year, firm_months, unique_firms, unique_ceos}]
        - turnover_metrics: {turnover_events, turnover_rate_per_100_firm_years}
        - predecessor_coverage: {with_predecessor_pct, without_predecessor_pct}
        - multi_ceo_analysis: {firms_with_multiple_ceos, max_ceos_per_firm}
        - ceo_careers: {ceos_multiple_firms, ceos_multiple_episodes_same_firm}
    """
    stats = {}

    # Panel dimensions
    total_firm_months = len(monthly_df)

    stats["panel_dimensions"] = {
        "total_firm_months": int(total_firm_months),
        "unique_firms": int(monthly_df["gvkey"].nunique()) if "gvkey" in monthly_df.columns else 0,
        "unique_ceos": int(monthly_df["ceo_id"].nunique()) if "ceo_id" in monthly_df.columns else 0,
    }

    # Date range
    if "date" in monthly_df.columns:
        monthly_df["date"] = pd.to_datetime(monthly_df["date"])
        date_col = monthly_df["date"].dropna()

        if len(date_col) > 0:
            earliest = date_col.min()
            latest = date_col.max()
            span_years = round((latest - earliest).days / 365.25, 2)

            stats["panel_dimensions"]["date_range"] = {
                "earliest": earliest.isoformat(),
                "latest": latest.isoformat(),
                "span_years": span_years,
            }

    # Temporal coverage by year
    if "year" in monthly_df.columns:
        temporal_coverage = []

        for year in sorted(monthly_df["year"].unique()):
            year_df = monthly_df[monthly_df["year"] == year]

            temporal_coverage.append({
                "year": int(year),
                "firm_months": int(len(year_df)),
                "unique_firms": int(year_df["gvkey"].nunique()) if "gvkey" in year_df.columns else 0,
                "unique_ceos": int(year_df["ceo_id"].nunique()) if "ceo_id" in year_df.columns else 0,
            })

        stats["temporal_coverage"] = temporal_coverage

    # CEO turnover analysis (prev_ceo_id changes indicate transitions)
    if "gvkey" in monthly_df.columns and "prev_ceo_id" in monthly_df.columns:
        # Sort by firm and date
        monthly_df_sorted = monthly_df.sort_values(["gvkey", "year", "month"])

        # Find prev_ceo_id changes within each firm (indicates CEO transitions)
        monthly_df_sorted["prev_ceo_id_shifted"] = monthly_df_sorted.groupby("gvkey")["prev_ceo_id"].shift(1)

        # Count transitions (where prev_ceo_id changes)
        transitions_mask = (
            monthly_df_sorted["prev_ceo_id"].notna() &
            monthly_df_sorted["prev_ceo_id_shifted"].notna() &
            (monthly_df_sorted["prev_ceo_id"] != monthly_df_sorted["prev_ceo_id_shifted"])
        )

        turnover_events = int(transitions_mask.sum())

        stats["turnover_metrics"] = {
            "turnover_events": turnover_events,
        }

        # Calculate firm-years for turnover rate
        if "year" in monthly_df.columns and "gvkey" in monthly_df.columns:
            firm_years = monthly_df[["gvkey", "year"]].drop_duplicates().shape[0]
            if firm_years > 0:
                turnover_rate = round(turnover_events / firm_years * 100, 2)
                stats["turnover_metrics"]["turnover_rate_per_100_firm_years"] = turnover_rate

    # Predecessor coverage
    if "prev_ceo_id" in monthly_df.columns:
        with_predecessor = monthly_df["prev_ceo_id"].notna().sum()
        without_predecessor = monthly_df["prev_ceo_id"].isna().sum()

        stats["predecessor_coverage"] = {
            "with_predecessor_pct": round(with_predecessor / total_firm_months * 100, 2) if total_firm_months > 0 else 0.0,
            "without_predecessor_pct": round(without_predecessor / total_firm_months * 100, 2) if total_firm_months > 0 else 0.0,
        }

    # Multi-CEO firm analysis
    if "gvkey" in monthly_df.columns and "ceo_id" in monthly_df.columns:
        ceos_per_firm = monthly_df.groupby("gvkey")["ceo_id"].nunique()
        firms_with_multiple = int((ceos_per_firm > 1).sum())

        stats["multi_ceo_analysis"] = {
            "firms_with_multiple_ceos": firms_with_multiple,
            "max_ceos_per_firm": int(ceos_per_firm.max()) if len(ceos_per_firm) > 0 else 0,
        }

    # CEO career analysis
    if "ceo_id" in monthly_df.columns and "gvkey" in monthly_df.columns:
        # CEOs spanning multiple firms
        firms_per_ceo = monthly_df.groupby("ceo_id")["gvkey"].nunique()
        ceos_multiple_firms = int((firms_per_ceo > 1).sum())

        stats["ceo_careers"] = {
            "ceos_multiple_firms": ceos_multiple_firms,
        }

    return stats


def collect_tenure_samples(episodes_df: pd.DataFrame, monthly_df: pd.DataFrame, n_samples: int = 3) -> Dict[str, Any]:
    """
    Collect qualitative tenure episode and transition examples for review.

    Provides sample episodes (short/long tenures), CEO transitions, and overlap
    resolution cases for methodology discussions and quality assessment.

    Deterministic: Same input produces same output (sorted, limited samples).

    Args:
        episodes_df: DataFrame with tenure episodes (must contain gvkey, exec_fullname, start_date, end_date, prev_exec_fullname)
        monthly_df: Monthly tenure panel DataFrame (must contain gvkey, year, month, date, ceo_name, prev_ceo_name)
        n_samples: Number of samples to collect per category (default: 3)

    Returns:
        Dictionary with keys:
        - short_tenures: List of short tenure examples (<12 months)
        - long_tenures: List of long tenure examples (>120 months)
        - transitions: List of CEO transition examples
        - overlaps: List of overlap resolution examples
    """
    samples = {
        "short_tenures": [],
        "long_tenures": [],
        "transitions": [],
        "overlaps": [],
    }

    # Ensure datetime columns
    if "start_date" in episodes_df.columns:
        episodes_df["start_date"] = pd.to_datetime(episodes_df["start_date"])
    if "end_date" in episodes_df.columns:
        episodes_df["end_date"] = pd.to_datetime(episodes_df["end_date"])

    # Calculate tenure in months
    if "start_date" in episodes_df.columns and "end_date" in episodes_df.columns:
        episodes_df["tenure_months"] = (
            (episodes_df["end_date"] - episodes_df["start_date"]).dt.total_seconds() / (30 * 24 * 3600)
        )
    else:
        episodes_df["tenure_months"] = pd.Series([0] * len(episodes_df))

    # Short tenure examples (<12 months)
    short_tenures_df = episodes_df[episodes_df["tenure_months"] < 12].sort_values("tenure_months")

    for _, row in short_tenures_df.head(n_samples).iterrows():
        samples["short_tenures"].append({
            "gvkey": str(row.get("gvkey", "")) if pd.notna(row.get("gvkey")) else "",
            "ceo_name": str(row.get("exec_fullname", "")) if pd.notna(row.get("exec_fullname")) else "",
            "start_date": row.get("start_date").isoformat() if pd.notna(row.get("start_date")) else "",
            "end_date": row.get("end_date").isoformat() if pd.notna(row.get("end_date")) else "",
            "tenure_months": round(float(row.get("tenure_months", 0)), 1),
        })

    # Long tenure examples (>120 months)
    long_tenures_df = episodes_df[episodes_df["tenure_months"] > 120].sort_values("tenure_months", ascending=False)

    for _, row in long_tenures_df.head(n_samples).iterrows():
        samples["long_tenures"].append({
            "gvkey": str(row.get("gvkey", "")) if pd.notna(row.get("gvkey")) else "",
            "ceo_name": str(row.get("exec_fullname", "")) if pd.notna(row.get("exec_fullname")) else "",
            "start_date": row.get("start_date").isoformat() if pd.notna(row.get("start_date")) else "",
            "end_date": row.get("end_date").isoformat() if pd.notna(row.get("end_date")) else "",
            "tenure_months": round(float(row.get("tenure_months", 0)), 1),
        })

    # CEO transition examples (predecessor -> successor)
    if "prev_exec_fullname" in episodes_df.columns:
        transitions_df = episodes_df[
            episodes_df["prev_exec_fullname"].notna() &
            (episodes_df["prev_exec_fullname"] != "")
        ].copy()

        # Calculate gap days between predecessor end and successor start
        transitions_df = transitions_df.sort_values(["gvkey", "start_date"])

        for _, row in transitions_df.head(n_samples).iterrows():
            # Try to find the predecessor episode to calculate gap
            gvkey = row.get("gvkey")
            successor_start = row.get("start_date")

            # Find predecessor episode (same firm, earlier start_date)
            predecessor_mask = (
                (transitions_df["gvkey"] == gvkey) &
                (transitions_df["exec_fullname"] == row.get("prev_exec_fullname"))
            )
            predecessor_episode = transitions_df[predecessor_mask]

            gap_days = None
            if len(predecessor_episode) > 0:
                predecessor_end = predecessor_episode.iloc[0].get("end_date")
                if pd.notna(predecessor_end) and pd.notna(successor_start):
                    gap_days = int((successor_start - predecessor_end).days)

            samples["transitions"].append({
                "gvkey": str(gvkey) if pd.notna(gvkey) else "",
                "prev_ceo_name": str(row.get("prev_exec_fullname", "")) if pd.notna(row.get("prev_exec_fullname")) else "",
                "new_ceo_name": str(row.get("exec_fullname", "")) if pd.notna(row.get("exec_fullname")) else "",
                "transition_date": successor_start.isoformat() if pd.notna(successor_start) else "",
                "gap_days": gap_days,
            })

    # Overlap resolution examples (from monthly panel)
    # Find firms with multiple CEOs in the same year/month
    if "gvkey" in monthly_df.columns and "year" in monthly_df.columns and "month" in monthly_df.columns:
        # Count CEOs per firm-month
        ceo_counts = monthly_df.groupby(["gvkey", "year", "month"])["ceo_id"].nunique()
        # Only single CEO per month after resolution, so we need to look for potential overlaps
        # by checking if prev_ceo_id exists and is different from ceo_id
        overlap_candidates = monthly_df[
            monthly_df["prev_ceo_id"].notna() &
            (monthly_df["prev_ceo_id"] != monthly_df["ceo_id"])
        ].copy()

        if len(overlap_candidates) > 0:
            # Sample n_samples overlap candidates
            overlap_samples = overlap_candidates.head(n_samples)

            for _, row in overlap_samples.iterrows():
                samples["overlaps"].append({
                    "gvkey": str(row.get("gvkey", "")) if pd.notna(row.get("gvkey")) else "",
                    "resolved_ceo": str(row.get("ceo_name", "")) if pd.notna(row.get("ceo_name")) else "",
                    "overlapped_ceo": str(row.get("prev_ceo_name", "")) if pd.notna(row.get("prev_ceo_name")) else "",
                    "overlap_period": f"{int(row.get('year', 0))}-{int(row.get('month', 0))}" if pd.notna(row.get("year")) else "",
                    "resolution_reason": "later_ceo_takes_precedence",
                })

    return samples


def compute_manifest_input_stats(df_metadata: pd.DataFrame, df_tenure: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze input data characteristics for manifest assembly.

    Provides comprehensive statistics about linked metadata (from step 1.2)
    and CEO tenure panel (from step 1.3) including industry coverage and
    temporal coverage.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        df_metadata: Linked metadata DataFrame (from step 1.2, with gvkey, start_date, ff12_code, ff48_code)
        df_tenure: Tenure monthly DataFrame (from step 1.3, with gvkey, year, month, ceo_id)

    Returns:
        Dictionary with keys:
        - linked_metadata: {total_calls, unique_gvkey, columns, memory_mb}
        - tenure_panel: {total_firm_months, unique_firms, unique_ceos,
                        date_range: {earliest, latest, span_years}}
        - industry_coverage: {ff12_count, ff48_count}
        - temporal_coverage: {year_range: {earliest, latest}, call_count_per_year}
    """
    stats = {}

    # Linked metadata characteristics
    stats["linked_metadata"] = {
        "total_calls": int(len(df_metadata)),
        "unique_gvkey": int(df_metadata["gvkey"].nunique()) if "gvkey" in df_metadata.columns else 0,
        "columns": int(len(df_metadata.columns)),
        "memory_mb": round(df_metadata.memory_usage(deep=True).sum() / (1024 * 1024), 2),
    }

    # Tenure panel characteristics
    stats["tenure_panel"] = {
        "total_firm_months": int(len(df_tenure)),
        "unique_firms": int(df_tenure["gvkey"].nunique()) if "gvkey" in df_tenure.columns else 0,
        "unique_ceos": int(df_tenure["ceo_id"].nunique()) if "ceo_id" in df_tenure.columns else 0,
    }

    # Tenure date coverage
    if "year" in df_tenure.columns:
        year_series = df_tenure["year"].dropna()
        if len(year_series) > 0:
            stats["tenure_panel"]["date_range"] = {
                "earliest": int(year_series.min()),
                "latest": int(year_series.max()),
                "span_years": int(year_series.max() - year_series.min()),
            }

    # Industry coverage from metadata
    if "ff12_code" in df_metadata.columns:
        stats["industry_coverage"] = {
            "ff12_count": int(df_metadata["ff12_code"].nunique()),
        }
    else:
        stats["industry_coverage"] = {"ff12_count": 0}

    if "ff48_code" in df_metadata.columns:
        stats["industry_coverage"]["ff48_count"] = int(df_metadata["ff48_code"].nunique())
    else:
        stats["industry_coverage"]["ff48_count"] = 0

    # Temporal coverage from metadata
    if "start_date" in df_metadata.columns:
        df_metadata_temp = df_metadata.copy()
        df_metadata_temp["start_date"] = pd.to_datetime(df_metadata_temp["start_date"])
        df_metadata_temp = df_metadata_temp.dropna(subset=["start_date"])

        if len(df_metadata_temp) > 0:
            years = df_metadata_temp["start_date"].dt.year
            year_counts = years.value_counts().sort_index()
            stats["temporal_coverage"] = {
                "year_range": {
                    "earliest": int(years.min()),
                    "latest": int(years.max()),
                },
                "call_count_per_year": {str(int(y)): int(c) for y, c in year_counts.items()},
            }
        else:
            stats["temporal_coverage"] = {"error": "No valid dates"}
    else:
        stats["temporal_coverage"] = {"error": "start_date column not found"}

    return stats


def compute_manifest_process_stats(
    df_metadata: pd.DataFrame,
    merged_df: pd.DataFrame,
    df_matched: pd.DataFrame,
    stats_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Analyze merge and CEO filtering process outcomes.

    Provides detailed statistics about the merge between metadata and tenure
    panel, including match rate by year, unmatched analysis, and CEO filtering
    impact.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        df_metadata: Original metadata DataFrame (before merge)
        merged_df: DataFrame after merge operation
        df_matched: DataFrame with matched calls (ceo_id not null)
        stats_dict: Statistics dictionary containing merge stats from main execution

    Returns:
        Dictionary with keys:
        - merge_outcome: {left_rows, right_rows, result_rows, matched_count,
                         unmatched_count, match_rate_pct}
        - match_rate_by_year: [{year, total_calls, matched_calls, match_rate_pct}]
        - unmatched_analysis: {unique_gvkey_unmatched, calls_unmatched,
                              temporal_distribution: {year: count}}
        - ceo_filtering: {total_ceos_before_filter, ceos_above_threshold,
                         ceos_dropped, threshold_value, calls_dropped}
    """
    stats = {}

    # Merge outcome
    left_rows = len(df_metadata)
    right_rows = stats_dict.get("merges", {}).get("ceo_tenure_join", {}).get("right_rows", 0)
    result_rows = len(merged_df)
    matched_count = int(merged_df["ceo_id"].notna().sum()) if "ceo_id" in merged_df.columns else 0
    unmatched_count = int(merged_df["ceo_id"].isna().sum()) if "ceo_id" in merged_df.columns else 0
    match_rate_pct = round(matched_count / left_rows * 100, 2) if left_rows > 0 else 0.0

    stats["merge_outcome"] = {
        "left_rows": int(left_rows),
        "right_rows": int(right_rows),
        "result_rows": int(result_rows),
        "matched_count": matched_count,
        "unmatched_count": unmatched_count,
        "match_rate_pct": match_rate_pct,
    }

    # Match rate by year
    if "year" in merged_df.columns and "ceo_id" in merged_df.columns:
        match_by_year = []
        for year in sorted(merged_df["year"].unique()):
            year_df = merged_df[merged_df["year"] == year]
            year_total = len(year_df)
            year_matched = int(year_df["ceo_id"].notna().sum())
            year_rate = round(year_matched / year_total * 100, 2) if year_total > 0 else 0.0

            match_by_year.append({
                "year": int(year),
                "total_calls": year_total,
                "matched_calls": year_matched,
                "match_rate_pct": year_rate,
            })
        stats["match_rate_by_year"] = match_by_year
    else:
        stats["match_rate_by_year"] = []

    # Unmatched analysis
    unmatched_df = merged_df[merged_df["ceo_id"].isna()] if "ceo_id" in merged_df.columns else pd.DataFrame()

    if len(unmatched_df) > 0:
        unique_gvkey_unmatched = int(unmatched_df["gvkey"].nunique()) if "gvkey" in unmatched_df.columns else 0

        # Temporal distribution of unmatched
        temporal_dist = {}
        if "year" in unmatched_df.columns:
            year_counts = unmatched_df["year"].value_counts().sort_index()
            temporal_dist = {str(int(y)): int(c) for y, c in year_counts.items()}

        stats["unmatched_analysis"] = {
            "unique_gvkey_unmatched": unique_gvkey_unmatched,
            "calls_unmatched": int(len(unmatched_df)),
            "temporal_distribution": temporal_dist,
        }
    else:
        stats["unmatched_analysis"] = {
            "unique_gvkey_unmatched": 0,
            "calls_unmatched": 0,
            "temporal_distribution": {},
        }

    # CEO filtering statistics
    if "ceo_id" in df_matched.columns:
        ceo_counts = df_matched["ceo_id"].value_counts()
        total_ceos_before_filter = len(ceo_counts)

        # Get threshold from processing stats or use default
        threshold = stats_dict.get("processing", {}).get("min_call_threshold", 5)
        ceos_above_threshold = int((ceo_counts >= threshold).sum())
        ceos_dropped = total_ceos_before_filter - ceos_above_threshold

        # Calculate calls dropped
        calls_dropped = stats_dict.get("processing", {}).get("below_threshold_calls_removed", 0)

        stats["ceo_filtering"] = {
            "total_ceos_before_filter": total_ceos_before_filter,
            "ceos_above_threshold": ceos_above_threshold,
            "ceos_dropped": ceos_dropped,
            "threshold_value": int(threshold),
            "calls_dropped": int(calls_dropped),
        }
    else:
        stats["ceo_filtering"] = {"error": "ceo_id column not found"}

    return stats


def compute_manifest_output_stats(df_final: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze final manifest characteristics.

    Provides comprehensive statistics about the final master sample manifest,
    including panel dimensions, call concentration, industry coverage, temporal
    coverage, and predecessor coverage.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        df_final: Final manifest DataFrame (must contain file_name, gvkey, ceo_id, ceo_name,
                 prev_ceo_id, start_date, ff12_code, ff12_name, ff48_code, ff48_name)

    Returns:
        Dictionary with keys:
        - panel_dimensions: {total_calls, unique_gvkey, unique_ceos, date_range}
        - call_concentration: {calls_per_ceo: {mean, median, min, max, std},
                             distribution_buckets: {bucket: {count, pct}}}
        - industry_coverage_ff12: [{ff12_code, ff12_name, call_count, percentage}]
        - industry_coverage_ff48: {unique_industries, completion_pct}
        - temporal_coverage: [{year, call_count, unique_firms, unique_ceos}]
        - predecessor_coverage: {pct_with_prev_ceo, pct_without_prev_ceo}
    """
    stats = {}

    # Panel dimensions
    total_calls = len(df_final)
    unique_gvkey = int(df_final["gvkey"].nunique()) if "gvkey" in df_final.columns else 0
    unique_ceos = int(df_final["ceo_id"].nunique()) if "ceo_id" in df_final.columns else 0

    stats["panel_dimensions"] = {
        "total_calls": total_calls,
        "unique_gvkey": unique_gvkey,
        "unique_ceos": unique_ceos,
    }

    # Date range
    if "start_date" in df_final.columns:
        df_final_temp = df_final.copy()
        df_final_temp["start_date"] = pd.to_datetime(df_final_temp["start_date"])
        date_col = df_final_temp["start_date"].dropna()

        if len(date_col) > 0:
            stats["panel_dimensions"]["date_range"] = {
                "earliest": date_col.min().isoformat(),
                "latest": date_col.max().isoformat(),
            }

    # Call concentration
    if "ceo_id" in df_final.columns:
        calls_per_ceo = df_final.groupby("ceo_id").size()

        stats["call_concentration"] = {
            "calls_per_ceo": {
                "mean": round(float(calls_per_ceo.mean()), 2),
                "median": round(float(calls_per_ceo.median()), 2),
                "min": int(calls_per_ceo.min()),
                "max": int(calls_per_ceo.max()),
                "std": round(float(calls_per_ceo.std()), 2),
            }
        }

        # Call distribution buckets
        buckets = {
            "<10": 0,
            "10-50": 0,
            "50-100": 0,
            "100+": 0,
        }

        buckets["<10"] = int((calls_per_ceo < 10).sum())
        buckets["10-50"] = int(((calls_per_ceo >= 10) & (calls_per_ceo < 50)).sum())
        buckets["50-100"] = int(((calls_per_ceo >= 50) & (calls_per_ceo < 100)).sum())
        buckets["100+"] = int((calls_per_ceo >= 100).sum())

        # Calculate percentages
        bucket_stats = {}
        for bucket_name, count in buckets.items():
            bucket_pct = round(count / len(calls_per_ceo) * 100, 2) if len(calls_per_ceo) > 0 else 0.0
            bucket_stats[bucket_name] = {
                "count": count,
                "pct": bucket_pct,
            }

        stats["call_concentration"]["distribution_buckets"] = bucket_stats

    # Industry coverage FF12
    if "ff12_code" in df_final.columns:
        ff12_counts = df_final["ff12_code"].value_counts()
        industry_coverage = []

        for ff12_code in ff12_counts.index[:10]:  # Top 10 industries
            count = int(ff12_counts[ff12_code])
            percentage = round(count / total_calls * 100, 2) if total_calls > 0 else 0.0

            # Get industry name if available
            ff12_name = ""
            if "ff12_name" in df_final.columns:
                name_rows = df_final[df_final["ff12_code"] == ff12_code]["ff12_name"]
                if len(name_rows) > 0:
                    ff12_name = str(name_rows.iloc[0]) if pd.notna(name_rows.iloc[0]) else ""

            industry_coverage.append({
                "ff12_code": str(ff12_code) if pd.notna(ff12_code) else "",
                "ff12_name": ff12_name,
                "call_count": count,
                "percentage": percentage,
            })

        stats["industry_coverage_ff12"] = industry_coverage

        # Top 5 industries summary
        stats["industry_coverage_ff12_top_5"] = industry_coverage[:5]
    else:
        stats["industry_coverage_ff12"] = []
        stats["industry_coverage_ff12_top_5"] = []

    # Industry coverage FF48
    if "ff48_code" in df_final.columns:
        unique_ff48 = int(df_final["ff48_code"].nunique())
        ff48_assigned = int(df_final["ff48_code"].notna().sum())

        stats["industry_coverage_ff48"] = {
            "unique_industries": unique_ff48,
            "completion_pct": round(ff48_assigned / total_calls * 100, 2) if total_calls > 0 else 0.0,
        }
    else:
        stats["industry_coverage_ff48"] = {"unique_industries": 0, "completion_pct": 0.0}

    # Temporal coverage by year
    if "start_date" in df_final.columns:
        df_final_temp = df_final.copy()
        df_final_temp["start_date"] = pd.to_datetime(df_final_temp["start_date"])
        df_final_temp["year"] = df_final_temp["start_date"].dt.year

        temporal_coverage = []
        for year in sorted(df_final_temp["year"].unique()):
            year_df = df_final_temp[df_final_temp["year"] == year]

            temporal_coverage.append({
                "year": int(year),
                "call_count": int(len(year_df)),
                "unique_firms": int(year_df["gvkey"].nunique()) if "gvkey" in year_df.columns else 0,
                "unique_ceos": int(year_df["ceo_id"].nunique()) if "ceo_id" in year_df.columns else 0,
            })

        stats["temporal_coverage"] = temporal_coverage
    else:
        stats["temporal_coverage"] = []

    # Predecessor coverage
    if "prev_ceo_id" in df_final.columns:
        with_predecessor = int(df_final["prev_ceo_id"].notna().sum())
        without_predecessor = int(df_final["prev_ceo_id"].isna().sum())

        stats["predecessor_coverage"] = {
            "pct_with_prev_ceo": round(with_predecessor / total_calls * 100, 2) if total_calls > 0 else 0.0,
            "pct_without_prev_ceo": round(without_predecessor / total_calls * 100, 2) if total_calls > 0 else 0.0,
        }
    else:
        stats["predecessor_coverage"] = {"error": "prev_ceo_id column not found"}

    return stats


def collect_ceo_distribution_samples(df_final: pd.DataFrame, n_samples: int = 5) -> Dict[str, Any]:
    """
    Collect CEO distribution examples from final manifest.

    Provides samples of top/bottom CEOs by call count, single-call CEOs,
    and multi-firm CEOs to illustrate sample concentration characteristics.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        df_final: Final manifest DataFrame (must contain ceo_id, ceo_name, gvkey)
        n_samples: Number of samples to collect per category (default: 5)

    Returns:
        Dictionary with keys:
        - top_ceos: List of top N CEOs by call count
        - bottom_ceos: List of bottom N CEOs by call count (above threshold)
        - single_call_ceos: {count, percentage}
        - multi_firm_ceos: List of CEOs spanning multiple firms
    """
    samples = {
        "top_ceos": [],
        "bottom_ceos": [],
        "single_call_ceos": {"count": 0, "percentage": 0.0},
        "multi_firm_ceos": [],
    }

    if "ceo_id" not in df_final.columns:
        return samples

    # Calculate call counts per CEO
    ceo_stats = df_final.groupby("ceo_id").agg({
        "file_name": "count",  # Call count
        "gvkey": "nunique",    # Unique firms
    }).rename(columns={"file_name": "call_count", "gvkey": "firm_count"})

    # Get CEO names
    if "ceo_name" in df_final.columns:
        ceo_names = df_final.groupby("ceo_id")["ceo_name"].first()
    else:
        ceo_names = pd.Series(dtype=str)

    total_ceos = len(ceo_stats)
    total_calls = len(df_final)

    # Top CEOs by call count
    top_ceos_df = ceo_stats.nlargest(n_samples, "call_count")
    for ceo_id, row in top_ceos_df.iterrows():
        ceo_name = str(ceo_names.get(ceo_id, "")) if ceo_id in ceo_names.index else ""
        percentage = round(row["call_count"] / total_calls * 100, 2) if total_calls > 0 else 0.0

        samples["top_ceos"].append({
            "ceo_id": str(ceo_id),
            "ceo_name": ceo_name,
            "call_count": int(row["call_count"]),
            "unique_firms": int(row["firm_count"]),
            "percentage": percentage,
        })

    # Bottom CEOs by call count (minimum 1 call, smallest counts first)
    bottom_ceos_df = ceo_stats[ceo_stats["call_count"] > 0].nsmallest(n_samples, "call_count")
    for ceo_id, row in bottom_ceos_df.iterrows():
        ceo_name = str(ceo_names.get(ceo_id, "")) if ceo_id in ceo_names.index else ""
        percentage = round(row["call_count"] / total_calls * 100, 2) if total_calls > 0 else 0.0

        samples["bottom_ceos"].append({
            "ceo_id": str(ceo_id),
            "ceo_name": ceo_name,
            "call_count": int(row["call_count"]),
            "unique_firms": int(row["firm_count"]),
            "percentage": percentage,
        })

    # Single call CEOs
    single_call_count = int((ceo_stats["call_count"] == 1).sum())
    samples["single_call_ceos"] = {
        "count": single_call_count,
        "percentage": round(single_call_count / total_ceos * 100, 2) if total_ceos > 0 else 0.0,
    }

    # Multi-firm CEOs
    multi_firm_df = ceo_stats[ceo_stats["firm_count"] > 1].nlargest(n_samples, "firm_count")
    for ceo_id, row in multi_firm_df.iterrows():
        ceo_name = str(ceo_names.get(ceo_id, "")) if ceo_id in ceo_names.index else ""

        samples["multi_firm_ceos"].append({
            "ceo_id": str(ceo_id),
            "ceo_name": ceo_name,
            "call_count": int(row["call_count"]),
            "firm_count": int(row["firm_count"]),
        })

    return samples


def compute_tokenize_input_stats(
    manifest_df: pd.DataFrame,
    lm_dict_path: Path,
    vocab_list: List[str],
    cat_sets: Dict[str, set],
) -> Dict[str, Any]:
    """
    Analyze input data and LM dictionary for tokenization.

    Provides comprehensive statistics about the manifest file and
    Loughran-McDonald master dictionary, including vocabulary size,
    category word counts, overlap analysis, and word length characteristics.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        manifest_df: Manifest DataFrame (from step 1.4)
        lm_dict_path: Path to LM dictionary CSV file
        vocab_list: List of vocabulary words (from load_lm_dictionary)
        cat_sets: Dictionary mapping category names to word sets

    Returns:
        Dictionary with keys:
        - manifest_stats: {total_files, unique_companies (if available),
                          date_range (if available), event_type_dist (if available)}
        - dictionary_stats: {total_words, vocabulary_size, avg_word_length,
                           word_length_distribution: {bucket: count}}
        - category_breakdown: {category: {word_count, sample_words}}
        - overlap_analysis: {words_in_multiple_categories, category_overlaps: {cat_pair: count}}
    """
    import numpy as np

    stats = {}

    # Manifest analysis
    stats["manifest_stats"] = {
        "total_files": int(len(manifest_df)),
    }

    # Check for additional manifest columns
    if "gvkey" in manifest_df.columns:
        stats["manifest_stats"]["unique_companies"] = int(manifest_df["gvkey"].nunique())

    if "start_date" in manifest_df.columns:
        manifest_df_temp = manifest_df.copy()
        manifest_df_temp["start_date"] = pd.to_datetime(manifest_df_temp["start_date"])
        date_col = manifest_df_temp["start_date"].dropna()
        if len(date_col) > 0:
            stats["manifest_stats"]["date_range"] = {
                "earliest": date_col.min().isoformat(),
                "latest": date_col.max().isoformat(),
            }

    if "event_type" in manifest_df.columns:
        event_counts = manifest_df["event_type"].value_counts().sort_index()
        stats["manifest_stats"]["event_type_dist"] = {
            str(int(et)): int(count) for et, count in event_counts.items()
        }

    # LM dictionary analysis
    stats["dictionary_stats"] = {
        "total_words": len(vocab_list),
        "vocabulary_size": len(vocab_list),
    }

    # Word length characteristics
    word_lengths = [len(w) for w in vocab_list]
    stats["dictionary_stats"]["avg_word_length"] = round(float(np.mean(word_lengths)), 2)

    # Word length distribution buckets
    length_buckets = {
        "1-3": 0,
        "4-6": 0,
        "7-9": 0,
        "10-12": 0,
        "13+": 0,
    }

    for wl in word_lengths:
        if wl <= 3:
            length_buckets["1-3"] += 1
        elif wl <= 6:
            length_buckets["4-6"] += 1
        elif wl <= 9:
            length_buckets["7-9"] += 1
        elif wl <= 12:
            length_buckets["10-12"] += 1
        else:
            length_buckets["13+"] += 1

    stats["dictionary_stats"]["word_length_distribution"] = length_buckets

    # Category breakdown
    stats["category_breakdown"] = {}
    for cat_name, cat_words in cat_sets.items():
        # Get first 10 sample words (sorted for determinism)
        sample_words = sorted(list(cat_words))[:10]
        stats["category_breakdown"][cat_name] = {
            "word_count": int(len(cat_words)),
            "sample_words": sample_words,
        }

    # Overlap analysis
    overlap_stats = {
        "words_in_multiple_categories": 0,
        "category_overlaps": {},
    }

    # Count words appearing in multiple categories
    all_words = {}
    for cat_name, cat_words in cat_sets.items():
        for word in cat_words:
            if word not in all_words:
                all_words[word] = []
            all_words[word].append(cat_name)

    multi_cat_words = {w: cats for w, cats in all_words.items() if len(cats) > 1}
    overlap_stats["words_in_multiple_categories"] = int(len(multi_cat_words))

    # Category pair overlaps
    category_names = sorted(cat_sets.keys())
    for i, cat1 in enumerate(category_names):
        for cat2 in category_names[i + 1:]:
            overlap = cat_sets[cat1] & cat_sets[cat2]
            if len(overlap) > 0:
                overlap_stats["category_overlaps"][f"{cat1}_{cat2}"] = int(len(overlap))

    stats["overlap_analysis"] = overlap_stats

    return stats


def compute_tokenize_process_stats(
    per_year_stats: List[Dict[str, Any]],
    cat_sets: Dict[str, set],
    vocab_list: List[str],
    duration_seconds: float,
) -> Dict[str, Any]:
    """
    Analyze tokenization process performance and coverage.

    Provides detailed statistics about tokenization volume, vocabulary
    coverage, category hit rates, efficiency metrics, and yearly trends.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        per_year_stats: List of per-year statistics dictionaries from processing
        cat_sets: Dictionary mapping category names to word sets
        vocab_list: List of vocabulary words
        duration_seconds: Total processing duration

    Returns:
        Dictionary with keys:
        - volume_metrics: {total_input_rows, total_output_rows, total_tokens,
                          total_vocab_hits}
        - coverage_metrics: {vocab_hit_rate, oov_rate}
        - category_hit_rates: {category: {hit_count, hit_rate_pct}}
        - efficiency_metrics: {docs_per_second, tokens_per_second,
                              tokens_per_doc: {mean, median, min, max},
                              workers_used, years_processed}
        - yearly_trends: {tokens_per_year: {year: count},
                         vocab_hits_per_year: {year: count}}
    """
    import numpy as np

    stats = {}

    # Volume metrics
    total_input_rows = sum(s.get("input_rows", 0) for s in per_year_stats)
    total_output_rows = sum(s.get("output_rows", 0) for s in per_year_stats)
    total_tokens = sum(s.get("total_tokens", 0) for s in per_year_stats)
    total_vocab_hits = sum(s.get("vocab_hits", 0) for s in per_year_stats)

    stats["volume_metrics"] = {
        "total_input_rows": int(total_input_rows),
        "total_output_rows": int(total_output_rows),
        "total_tokens": int(total_tokens),
        "total_vocab_hits": int(total_vocab_hits),
    }

    # Coverage metrics
    vocab_hit_rate = round(total_vocab_hits / total_tokens * 100, 2) if total_tokens > 0 else 0.0
    oov_rate = round(100.0 - vocab_hit_rate, 2) if total_tokens > 0 else 0.0

    stats["coverage_metrics"] = {
        "vocab_hit_rate": vocab_hit_rate,
        "oov_rate": oov_rate,
    }

    # Category hit rates (percentage of total tokens)
    # This requires re-aggregating category counts from output files
    # Since we don't have access to output data here, we'll provide placeholder
    # that will be filled during script execution
    stats["category_hit_rates"] = {}
    for cat_name in cat_sets.keys():
        stats["category_hit_rates"][cat_name] = {
            "hit_count": 0,  # To be filled during script execution
            "hit_rate_pct": 0.0,  # To be filled during script execution
        }

    # Efficiency metrics
    docs_per_second = round(total_output_rows / duration_seconds, 2) if duration_seconds > 0 else 0.0
    tokens_per_second = round(total_tokens / duration_seconds, 2) if duration_seconds > 0 else 0.0

    tokens_per_doc_values = [s.get("avg_tokens_per_doc", 0) for s in per_year_stats if s.get("output_rows", 0) > 0]

    tokens_per_doc_stats = {
        "mean": round(float(np.mean(tokens_per_doc_values)), 2) if tokens_per_doc_values else 0.0,
        "median": round(float(np.median(tokens_per_doc_values)), 2) if tokens_per_doc_values else 0.0,
        "min": round(float(np.min(tokens_per_doc_values)), 2) if tokens_per_doc_values else 0.0,
        "max": round(float(np.max(tokens_per_doc_values)), 2) if tokens_per_doc_values else 0.0,
    }

    stats["efficiency_metrics"] = {
        "docs_per_second": docs_per_second,
        "tokens_per_second": tokens_per_second,
        "tokens_per_doc": tokens_per_doc_stats,
        "workers_used": len(per_year_stats),  # Approximate
        "years_processed": len(per_year_stats),
    }

    # Yearly trends
    tokens_per_year = {}
    vocab_hits_per_year = {}

    for year_stat in per_year_stats:
        year = year_stat.get("year")
        if year is not None:
            tokens_per_year[str(year)] = year_stat.get("total_tokens", 0)
            vocab_hits_per_year[str(year)] = year_stat.get("vocab_hits", 0)

    stats["yearly_trends"] = {
        "tokens_per_year": tokens_per_year,
        "vocab_hits_per_year": vocab_hits_per_year,
    }

    return stats


def compute_tokenize_output_stats(
    output_dfs: List[pd.DataFrame],
    cat_sets: Dict[str, set],
) -> Dict[str, Any]:
    """
    Analyze linguistic counts output from tokenization.

    Provides comprehensive statistics about category count distributions,
    total tokens statistics, speaker-level analysis (if available),
    and sparsity analysis.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        output_dfs: List of per-year DataFrames with linguistic counts
                    (must contain {category}_count columns and total_tokens)
        cat_sets: Dictionary mapping category names to word sets

    Returns:
        Dictionary with keys:
        - category_distributions: {category: {mean, median, std, min, max,
                                             q25, q75, zeros_count, zeros_pct,
                                             percentiles: {p10, p25, p50, p75, p90, p95, p99}}}
        - total_tokens_stats: {mean, median, std, min, max,
                              percentiles: {p10, p25, p50, p75, p90, p95, p99}}
        - speaker_analysis: (if role column exists) {documents_per_role: {role: count},
                                                    avg_tokens_per_role: {role: avg},
                                                    avg_category_per_role: {role: {category: avg}}}
        - sparsity_analysis: {zero_counts_per_category: {category: {count, pct}},
                             documents_with_no_matches: count}
    """
    import numpy as np

    # Concatenate all output DataFrames for analysis
    if len(output_dfs) == 0:
        return {
            "category_distributions": {},
            "total_tokens_stats": {},
            "speaker_analysis": {"error": "No output data"},
            "sparsity_analysis": {},
        }

    df_all = pd.concat(output_dfs, ignore_index=True)

    stats = {}

    # Category distributions
    stats["category_distributions"] = {}
    for cat_name in cat_sets.keys():
        col_name = f"{cat_name}_count"
        if col_name not in df_all.columns:
            continue

        cat_series = df_all[col_name]

        # Basic statistics
        cat_stats = {
            "mean": round(float(cat_series.mean()), 4),
            "median": round(float(cat_series.median()), 4),
            "std": round(float(cat_series.std()), 4),
            "min": int(cat_series.min()),
            "max": int(cat_series.max()),
        }

        # Quartiles
        cat_stats["q25"] = round(float(cat_series.quantile(0.25)), 4)
        cat_stats["q75"] = round(float(cat_series.quantile(0.75)), 4)

        # Zero counts
        zeros_count = int((cat_series == 0).sum())
        cat_stats["zeros_count"] = zeros_count
        cat_stats["zeros_pct"] = round(zeros_count / len(cat_series) * 100, 2) if len(cat_series) > 0 else 0.0

        # Percentiles
        cat_stats["percentiles"] = {
            "p10": round(float(cat_series.quantile(0.10)), 4),
            "p25": round(float(cat_series.quantile(0.25)), 4),
            "p50": round(float(cat_series.quantile(0.50)), 4),
            "p75": round(float(cat_series.quantile(0.75)), 4),
            "p90": round(float(cat_series.quantile(0.90)), 4),
            "p95": round(float(cat_series.quantile(0.95)), 4),
            "p99": round(float(cat_series.quantile(0.99)), 4),
        }

        stats["category_distributions"][cat_name] = cat_stats

    # Total tokens statistics
    if "total_tokens" in df_all.columns:
        tokens_series = df_all["total_tokens"]
        stats["total_tokens_stats"] = {
            "mean": round(float(tokens_series.mean()), 2),
            "median": round(float(tokens_series.median()), 2),
            "std": round(float(tokens_series.std()), 2),
            "min": int(tokens_series.min()),
            "max": int(tokens_series.max()),
            "percentiles": {
                "p10": round(float(tokens_series.quantile(0.10)), 2),
                "p25": round(float(tokens_series.quantile(0.25)), 2),
                "p50": round(float(tokens_series.quantile(0.50)), 2),
                "p75": round(float(tokens_series.quantile(0.75)), 2),
                "p90": round(float(tokens_series.quantile(0.90)), 2),
                "p95": round(float(tokens_series.quantile(0.95)), 2),
                "p99": round(float(tokens_series.quantile(0.99)), 2),
            },
        }

    # Speaker-level analysis (if role column exists)
    if "role" in df_all.columns:
        role_stats = {}

        # Documents per role
        role_counts = df_all["role"].value_counts().sort_index()
        role_stats["documents_per_role"] = {
            str(role): int(count) for role, count in role_counts.items()
        }

        # Average tokens per role
        if "total_tokens" in df_all.columns:
            tokens_by_role = df_all.groupby("role")["total_tokens"].mean().sort_index()
            role_stats["avg_tokens_per_role"] = {
                str(role): round(float(avg), 2) for role, avg in tokens_by_role.items()
            }

        # Average category counts per role
        role_stats["avg_category_per_role"] = {}
        for cat_name in cat_sets.keys():
            col_name = f"{cat_name}_count"
            if col_name in df_all.columns:
                cat_by_role = df_all.groupby("role")[col_name].mean().sort_index()
                role_stats["avg_category_per_role"][cat_name] = {
                    str(role): round(float(avg), 4) for role, avg in cat_by_role.items()
                }

        stats["speaker_analysis"] = role_stats
    else:
        stats["speaker_analysis"] = {"error": "role column not found"}

    # Sparsity analysis
    stats["sparsity_analysis"] = {
        "zero_counts_per_category": {},
        "documents_with_no_matches": 0,
    }

    for cat_name in cat_sets.keys():
        col_name = f"{cat_name}_count"
        if col_name not in df_all.columns:
            continue

        zeros_count = int((df_all[col_name] == 0).sum())
        zeros_pct = round(zeros_count / len(df_all) * 100, 2) if len(df_all) > 0 else 0.0

        stats["sparsity_analysis"]["zero_counts_per_category"][cat_name] = {
            "count": zeros_count,
            "pct": zeros_pct,
        }

    # Documents with no linguistic matches (all categories zero)
    cat_cols = [f"{cat}_count" for cat in cat_sets.keys() if f"{cat}_count" in df_all.columns]
    if cat_cols:
        # Check if all category columns are zero
        zero_mask = (df_all[cat_cols] == 0).all(axis=1)
        stats["sparsity_analysis"]["documents_with_no_matches"] = int(zero_mask.sum())

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
