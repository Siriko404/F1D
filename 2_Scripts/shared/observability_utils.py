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
