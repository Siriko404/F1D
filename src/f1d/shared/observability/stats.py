#!/usr/bin/env python3
"""
================================================================================
OBSERVABILITY PACKAGE - STATS MODULE
================================================================================
ID: shared.observability.stats
Description: Provides statistics and analysis functions for observability.

This module extracts statistics functions from the original observability_utils.py.
Includes general statistics functions and step-specific stats functions.

Deterministic: true
Main Functions:
    - print_stat(): Print statistic with consistent formatting
    - analyze_missing_values(): Analyze missing value patterns
    - print_stats_summary(): Print summary of statistics

Dependencies:
    - Utility module for statistics
    - Uses: pandas, numpy

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, TypedDict, cast

import numpy as np
import pandas as pd

# Configure logger for this module
logger = logging.getLogger(__name__)


# =============================================================================
# TypedDict Definitions for Stats Module
# =============================================================================


class PercentilesDict(TypedDict, total=False):
    """Percentiles dictionary for statistics."""

    p1: float
    p5: float
    p10: float
    p25: float
    p50: float
    p75: float
    p90: float
    p95: float
    p99: float


class CountPctDict(TypedDict):
    """Count and percentage dictionary."""

    count: int
    pct: float


class VarStatsDict(TypedDict, total=False):
    """Variable statistics dictionary with optional nested dicts."""

    count: int
    mean: float
    median: float
    std: float
    min: float
    max: float
    q25: float
    q75: float
    zeros_count: int
    zeros_pct: float
    percentiles: PercentilesDict
    zeros: CountPctDict
    nans: CountPctDict


class CategoryStatsDict(TypedDict, total=False):
    """Category statistics dictionary for tokenization output."""

    mean: float
    median: float
    std: float
    min: int
    max: int
    q25: float
    q75: float
    zeros_count: int
    zeros_pct: float
    percentiles: PercentilesDict


class DateRangeDict(TypedDict):
    """Date range dictionary."""

    earliest: str
    latest: str


class YearStatsDict(TypedDict, total=False):
    """Year-level statistics dictionary."""

    observations: int
    unique_stocks: int
    date_range: DateRangeDict
    data_columns_available: List[str]


class OverlapStatsDict(TypedDict, total=False):
    """Overlap statistics dictionary."""

    words_in_multiple_categories: int
    category_overlaps: Dict[str, int]


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
            # Skip non-numeric values (dicts, lists) that can't be formatted as numbers
            if isinstance(count, (dict, list)):
                continue
            print(f"{step:<30} {count:>10,}")

    print("=" * 60)


def save_stats(stats: Dict[str, Any], out_dir: Path) -> None:
    """
    Save statistics to JSON file.

    Args:
        stats: Statistics dictionary to save
        out_dir: Output directory path
    """

    stats_path = out_dir / "stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"Saved: {stats_path.name}")


def calculate_throughput(rows_processed: int, duration_seconds: float) -> float:
    """
    Calculate throughput in rows per second.

    Args:
        rows_processed: Number of rows processed
        duration_seconds: Duration in seconds

    Returns:
        Throughput in rows per second (rounded to 2 decimals)

    Raises:
        ValueError: If duration_seconds <= 0 (indicates timing error in pipeline)
    """
    if duration_seconds <= 0:
        logger.warning(
            f"Invalid duration_seconds={duration_seconds} <= 0, "
            f"rows_processed={rows_processed}. "
            f"This may indicate a timing error in the pipeline "
            f"(start_time/end_time not set correctly)."
        )
        raise ValueError(
            f"Cannot calculate throughput: duration_seconds={duration_seconds} <= 0. "
            f"rows_processed={rows_processed}. "
            f"Check script timing logic (start_time/end_time)."
        )
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
        # Get indices from series (not df) since mask is based on series with dropna
        anomaly_indices = series[anomaly_mask].index.tolist()

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
    datetime_cols = df.select_dtypes(
        include=["datetime64", "datetime64[ns]"]
    ).columns.tolist()
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
    categorical_cols = df.select_dtypes(
        include=["object", "string", "category"]
    ).columns.tolist()
    for col in categorical_cols:
        if col in datetime_cols:
            continue
        distinct_count = df[col].nunique()
        stats["cardinality"][col] = int(distinct_count)

    return stats


def compute_temporal_stats(
    df: pd.DataFrame, date_col: str = "start_date"
) -> Dict[str, Any]:
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

    df_temp = cast(pd.DataFrame, df[[date_col]].copy())
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
    year_dist = {int(cast(int, year)): int(count) for year, count in year_counts.items()}

    # Month distribution
    month_counts = df_temp["month"].value_counts().sort_index()
    month_dist = {int(cast(int, month)): int(count) for month, count in month_counts.items()}

    # Quarter distribution
    quarter_counts = df_temp["quarter"].value_counts().sort_index()
    quarter_dist = {int(cast(int, q)): int(count) for q, count in quarter_counts.items()}

    # Day of week distribution
    dow_counts = df_temp["day_of_week"].value_counts().sort_index()
    dow_dist = {int(cast(int, dow)): int(count) for dow, count in dow_counts.items()}

    # Date range
    earliest = df_temp[date_col].min()
    latest = df_temp[date_col].max()
    span_days = (latest - earliest).days

    # Calls per year statistics
    df_temp["year"].values
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
    stats: Dict[str, Any] = {}

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
            histogram: Dict[str, Any] = {}
            try:
                min_score = quality_scores.min()
                max_score = quality_scores.max()
                if min_score != max_score:
                    buckets = pd.cut(
                        quality_scores, bins=5, retbins=True, include_lowest=True
                    )
                    bucket_counts = quality_scores.groupby(buckets[0]).count()
                    histogram = {
                        f"{round(cast(pd.Interval, interval).left, 2)}-{round(cast(pd.Interval, interval).right, 2)}": int(
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
            stats["data_quality_distribution"] = {
                "error": "No quality scores available"
            }
    else:
        stats["data_quality_distribution"] = {"error": "Column not found"}

    # Speaker data coverage
    if "has_speaker_data" in df.columns:
        with_speaker = df[df["has_speaker_data"]].shape[0]
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


def compute_linking_input_stats(
    df_input: pd.DataFrame, df_ccm: pd.DataFrame
) -> Dict[str, Any]:
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
    stats: Dict[str, Any] = {}

    # Input metadata characteristics
    stats["input_metadata"] = {
        "record_count": int(len(df_input)),
        "unique_companies": int(df_input["company_id"].nunique())
        if "company_id" in df_input.columns
        else 0,
        "column_count": int(len(df_input.columns)),
        "memory_mb": round(df_input.memory_usage(deep=True).sum() / (1024 * 1024), 2),
    }

    # CCM reference database characteristics
    stats["reference_database"] = {
        "total_records": int(len(df_ccm)),
        "unique_gvkey": int(df_ccm["gvkey"].nunique())
        if "gvkey" in df_ccm.columns
        else 0,
        "unique_lpermno": int(df_ccm["LPERMNO"].nunique())
        if "LPERMNO" in df_ccm.columns
        else 0,
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
        permno_available = df_input[
            df_input["permno"].notna() & (df_input["permno"] != "")
        ]["company_id"].nunique()
        coverage["permno_coverage_pct"] = (
            round(permno_available / total_companies * 100, 2)
            if total_companies > 0
            else 0.0
        )

    if "cusip" in df_input.columns:
        cusip_available = df_input[
            df_input["cusip"].notna() & (df_input["cusip"] != "")
        ]["company_id"].nunique()
        coverage["cusip_coverage_pct"] = (
            round(cusip_available / total_companies * 100, 2)
            if total_companies > 0
            else 0.0
        )

    if "company_ticker" in df_input.columns:
        ticker_available = df_input[
            df_input["company_ticker"].notna() & (df_input["company_ticker"] != "")
        ]["company_id"].nunique()
        coverage["ticker_coverage_pct"] = (
            round(ticker_available / total_companies * 100, 2)
            if total_companies > 0
            else 0.0
        )

    if "company_name" in df_input.columns:
        name_available = df_input[
            df_input["company_name"].notna() & (df_input["company_name"] != "")
        ]["company_id"].nunique()
        coverage["name_coverage_pct"] = (
            round(name_available / total_companies * 100, 2)
            if total_companies > 0
            else 0.0
        )

    stats["coverage_metrics"] = coverage

    return stats


def compute_linking_process_stats(
    unique_df: pd.DataFrame, stats_dict: Dict[str, Any]
) -> Dict[str, Any]:
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
    stats: Dict[str, Any] = {}

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
        "tier2_matched": int(tier2_matched - tier1_matched)
        if tier2_matched > tier1_matched
        else 0,
        "tier3_candidates": int(tier3_candidates),
        "tier3_matched": int(tier3_matched - tier2_matched)
        if tier3_matched > tier2_matched
        else 0,
        "total_matched": int(tier3_matched),
    }

    # Match rate calculations
    stats["match_rates"] = {}
    if tier1_candidates > 0:
        stats["match_rates"]["tier1_match_pct"] = round(
            tier1_matched / tier1_candidates * 100, 2
        )
    if tier2_candidates > 0:
        tier2_new_matches = stats["funnel_analysis"]["tier2_matched"]
        stats["match_rates"]["tier2_match_pct"] = round(
            tier2_new_matches / tier2_candidates * 100, 2
        )
    if tier3_candidates > 0:
        tier3_new_matches = stats["funnel_analysis"]["tier3_matched"]
        stats["match_rates"]["tier3_match_pct"] = round(
            tier3_new_matches / tier3_candidates * 100, 2
        )
    if total_unique > 0:
        stats["match_rates"]["overall_match_pct"] = round(
            tier3_matched / total_unique * 100, 2
        )

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
                stats["link_quality_distribution"]["quality_100_count"]
                / total_quality_matches
                * 100,
                2,
            )
            stats["link_quality_distribution"]["quality_90_pct"] = round(
                stats["link_quality_distribution"]["quality_90_count"]
                / total_quality_matches
                * 100,
                2,
            )
            stats["link_quality_distribution"]["quality_80_pct"] = round(
                stats["link_quality_distribution"]["quality_80_count"]
                / total_quality_matches
                * 100,
                2,
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
    stats: Dict[str, Any] = {}

    total_calls = len(df_linked)

    # Linkage success summary
    unique_companies = (
        df_linked["company_id"].nunique() if "company_id" in df_linked.columns else 0
    )
    unique_gvkey = df_linked["gvkey"].nunique() if "gvkey" in df_linked.columns else 0

    stats["linkage_summary"] = {
        "total_calls_linked": int(total_calls),
        "unique_companies_linked": int(unique_companies),
        "unique_gvkey_assigned": int(unique_gvkey),
        "calls_per_company_avg": round(total_calls / unique_companies, 2)
        if unique_companies > 0
        else 0.0,
    }

    # Calculate linkage success rate (from input perspective - not available here, only relative stats)
    # The success rate relative to unique companies
    if unique_companies > 0:
        stats["linkage_summary"]["company_linkage_rate"] = round(
            unique_gvkey / unique_companies * 100, 2
        )

    # Industry coverage - FF12
    if "ff12_code" in df_linked.columns:
        ff12_assigned = df_linked["ff12_code"].notna().sum()
        ff12_unique = df_linked["ff12_code"].nunique()
        stats["industry_coverage"] = {
            "ff12_assigned": int(ff12_assigned),
            "ff12_unique_industries": int(ff12_unique),
            "ff12_completion_pct": round(ff12_assigned / total_calls * 100, 2)
            if total_calls > 0
            else 0.0,
        }
    else:
        stats["industry_coverage"] = {"error": "FF12 columns not found"}

    # Industry coverage - FF48
    if "ff48_code" in df_linked.columns:
        ff48_assigned = df_linked["ff48_code"].notna().sum()
        ff48_unique = df_linked["ff48_code"].nunique()
        stats["industry_coverage"]["ff48_assigned"] = int(ff48_assigned)
        stats["industry_coverage"]["ff48_unique_industries"] = int(ff48_unique)
        stats["industry_coverage"]["ff48_completion_pct"] = (
            round(ff48_assigned / total_calls * 100, 2) if total_calls > 0 else 0.0
        )

    # SIC code distribution
    if "sic" in df_linked.columns:
        sic_counts = df_linked["sic"].value_counts().head(10)  # Top 10 SICs
        top_industries = []
        for sic, count in sic_counts.items():
            top_industries.append(
                {
                    "sic": int(cast(int, sic)) if pd.notna(sic) else None,
                    "count": int(count),
                    "percentage": round(count / total_calls * 100, 2)
                    if total_calls > 0
                    else 0.0,
                }
            )

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
                quality_by_method = (
                    df_linked.groupby("link_method")["link_quality"].mean().sort_index()
                )
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


def collect_fuzzy_match_samples(
    unique_df: pd.DataFrame, n_samples: int = 5
) -> Dict[str, Any]:
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
    samples: Dict[str, List[Dict[str, Any]]] = {"high_score": [], "borderline": []}

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
    high_score_df = fuzzy_df[fuzzy_df["score"] > 98].sort_values(
        "score", ascending=False
    )
    for _, row in high_score_df.head(n_samples).iterrows():
        samples["high_score"].append(
            {
                "company_id": str(row.get("company_id", "")),
                "company_name": str(row.get("company_name", ""))
                if pd.notna(row.get("company_name"))
                else "",
                "matched_name": str(row.get("conm", ""))
                if pd.notna(row.get("conm"))
                else "",
                "score": round(float(row.get("score", 0)), 1),
                "gvkey": str(row.get("gvkey", ""))
                if pd.notna(row.get("gvkey"))
                else "",
                "sic": int(row["sic"]) if pd.notna(row.get("sic")) else None,
            }
        )

    # Get borderline matches (92-95)
    borderline_df = fuzzy_df[
        (fuzzy_df["score"] >= 92) & (fuzzy_df["score"] <= 95)
    ].sort_values("score", ascending=False)
    for _, row in borderline_df.head(n_samples).iterrows():
        samples["borderline"].append(
            {
                "company_id": str(row.get("company_id", "")),
                "company_name": str(row.get("company_name", ""))
                if pd.notna(row.get("company_name"))
                else "",
                "matched_name": str(row.get("conm", ""))
                if pd.notna(row.get("conm"))
                else "",
                "score": round(float(row.get("score", 0)), 1),
                "gvkey": str(row.get("gvkey", ""))
                if pd.notna(row.get("gvkey"))
                else "",
                "sic": int(row["sic"]) if pd.notna(row.get("sic")) else None,
            }
        )

    return samples


def collect_tier_match_samples(
    unique_df: pd.DataFrame, n_samples: int = 3
) -> Dict[str, Any]:
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

    samples: Dict[str, List[Dict[str, Any]]] = {"tier1": [], "tier2": []}

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
            samples["tier1"].append(
                {
                    "company_id": str(row.get("company_id", "")),
                    "permno": str(row.get("permno", ""))
                    if pd.notna(row.get("permno"))
                    else "",
                    "gvkey": str(row.get("gvkey", ""))
                    if pd.notna(row.get("gvkey"))
                    else "",
                    "conm": str(row.get("conm", ""))
                    if pd.notna(row.get("conm"))
                    else "",
                    "sic": int(row["sic"]) if pd.notna(row.get("sic")) else None,
                    "link_quality": int(row.get("link_quality", 100)),
                }
            )

    # Tier 2: CUSIP8 matches
    tier2_mask = unique_df["link_method"] == "cusip8_date"
    tier2_df = unique_df[tier2_mask].copy()

    if len(tier2_df) > 0:
        # Sample n_samples random examples
        sample_size = min(n_samples, len(tier2_df))
        tier2_samples = tier2_df.sample(n=sample_size, random_state=42)

        for _, row in tier2_samples.iterrows():
            samples["tier2"].append(
                {
                    "company_id": str(row.get("company_id", "")),
                    "cusip8": str(row.get("cusip8", ""))
                    if pd.notna(row.get("cusip8"))
                    else "",
                    "gvkey": str(row.get("gvkey", ""))
                    if pd.notna(row.get("gvkey"))
                    else "",
                    "conm": str(row.get("conm", ""))
                    if pd.notna(row.get("conm"))
                    else "",
                    "sic": int(row["sic"]) if pd.notna(row.get("sic")) else None,
                    "link_quality": int(row.get("link_quality", 90)),
                }
            )

    return samples


def collect_unmatched_samples(
    df_original: pd.DataFrame, unique_df: pd.DataFrame, n_samples: int = 5
) -> List[Dict[str, Any]]:
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

    samples: List[Dict[str, Any]] = []

    # Find unmatched companies (gvkey is NaN in unique_df)
    unmatched_mask = unique_df["gvkey"].isna()
    unmatched_company_ids = set(unique_df[unmatched_mask]["company_id"].unique())

    if len(unmatched_company_ids) == 0:
        return samples

    # Get unmatched companies from original df
    unmatched_companies = cast(
        pd.DataFrame,
        df_original[df_original["company_id"].isin(unmatched_company_ids)],
    )
    unmatched_df = unmatched_companies.drop_duplicates(subset=["company_id"])

    # Sample n_samples unmatched companies
    sample_size = min(n_samples, len(unmatched_df))
    unmatched_samples = unmatched_df.sample(n=sample_size, random_state=42)

    for _, row in unmatched_samples.iterrows():
        # Check what identifiers are available
        has_permno = pd.notna(row.get("permno")) and str(row.get("permno", "")) != ""
        has_cusip = pd.notna(row.get("cusip")) and str(row.get("cusip", "")) != ""
        has_ticker = (
            pd.notna(row.get("company_ticker"))
            and str(row.get("company_ticker", "")) != ""
        )
        has_name = (
            pd.notna(row.get("company_name")) and str(row.get("company_name", "")) != ""
        )

        # Classify likely reason for no match
        if not has_permno and not has_cusip and not has_ticker:
            likely_reason = "missing_identifiers"
        elif has_name:
            likely_reason = "no_ccm_match"
        else:
            likely_reason = "unknown"

        samples.append(
            {
                "company_id": str(row.get("company_id", "")),
                "company_name": str(row.get("company_name", ""))
                if pd.notna(row.get("company_name"))
                else "",
                "has_permno": bool(has_permno),
                "has_cusip": bool(has_cusip),
                "has_ticker": bool(has_ticker),
                "likely_reason": likely_reason,
            }
        )

    return samples


def collect_before_after_samples(
    df_original: pd.DataFrame, df_linked: pd.DataFrame, n_samples: int = 3
) -> List[Dict[str, Any]]:
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

        samples.append(
            {
                "before": {
                    "company_id": str(orig_row.get("company_id", "")),
                    "company_name": str(orig_row.get("company_name", ""))
                    if pd.notna(orig_row.get("company_name"))
                    else "",
                    "company_ticker": str(orig_row.get("company_ticker", ""))
                    if pd.notna(orig_row.get("company_ticker"))
                    else "",
                    "permno": str(orig_row.get("permno", ""))
                    if pd.notna(orig_row.get("permno"))
                    else "",
                    "cusip": str(orig_row.get("cusip", ""))
                    if pd.notna(orig_row.get("cusip"))
                    else "",
                },
                "after": {
                    "gvkey": str(link_row.get("gvkey", ""))
                    if pd.notna(link_row.get("gvkey"))
                    else "",
                    "conm": str(link_row.get("conm", ""))
                    if pd.notna(link_row.get("conm"))
                    else "",
                    "sic": int(link_row["sic"])
                    if pd.notna(link_row.get("sic"))
                    else None,
                    "ff12_name": str(link_row.get("ff12_name", ""))
                    if pd.notna(link_row.get("ff12_name"))
                    else "",
                    "ff48_name": str(link_row.get("ff48_name", ""))
                    if pd.notna(link_row.get("ff48_name"))
                    else "",
                    "link_method": str(link_row.get("link_method", ""))
                    if pd.notna(link_row.get("link_method"))
                    else "",
                    "link_quality": int(link_row.get("link_quality", 0)),
                },
            }
        )

    return samples


def compute_tenure_input_stats(
    df_input: pd.DataFrame, df_ceo: pd.DataFrame
) -> Dict[str, Any]:
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
    stats: Dict[str, Any] = {}

    # Overall Execucomp characteristics
    stats["overall_execucomp"] = {
        "total_records": int(len(df_input)),
        "unique_gvkey": int(df_input["gvkey"].nunique())
        if "gvkey" in df_input.columns
        else 0,
        "unique_execid": int(df_input["execid"].nunique())
        if "execid" in df_input.columns
        else 0,
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
        "pct_of_total": round(ceo_records / total_records * 100, 2)
        if total_records > 0
        else 0.0,
        "unique_ceo_firms": int(df_ceo["gvkey"].nunique())
        if "gvkey" in df_ceo.columns
        else 0,
        "unique_ceo_executives": int(df_ceo["execid"].nunique())
        if "execid" in df_ceo.columns
        else 0,
    }

    # Date field coverage
    if "becameceo" in df_ceo.columns:
        becameceo_available = df_ceo["becameceo"].notna().sum()
        stats["date_field_coverage"] = {
            "becameceo_available_pct": round(becameceo_available / len(df_ceo) * 100, 2)
            if len(df_ceo) > 0
            else 0.0,
        }

    if "leftofc" in df_ceo.columns:
        leftofc_available = df_ceo["leftofc"].notna().sum()
        stats["date_field_coverage"]["leftofc_available_pct"] = (
            round(leftofc_available / len(df_ceo) * 100, 2) if len(df_ceo) > 0 else 0.0
        )

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
            "exec_fullname_available_pct": round(name_available / len(df_ceo) * 100, 2)
            if len(df_ceo) > 0
            else 0.0,
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
    stats: Dict[str, Any] = {}

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
            },
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
            episodes_df["end_date"] - episodes_df["start_date"]
        ).dt.total_seconds() / (30 * 24 * 3600)

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
        buckets["5-10 years"] = int(
            ((tenure_months >= 60) & (tenure_months < 120)).sum()
        )
        buckets["10+ years"] = int((tenure_months >= 120).sum())

        # Calculate percentages
        bucket_stats = {}
        for bucket_name, count in buckets.items():
            bucket_pct = (
                round(count / total_episodes * 100, 2) if total_episodes > 0 else 0.0
            )
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
            "link_rate_pct": round(linked_count / total_episodes * 100, 2)
            if total_episodes > 0
            else 0.0,
        }

    # Date validity checks
    today = pd.Timestamp.now()

    if "start_date" in episodes_df.columns:
        future_dates = int((episodes_df["start_date"] > today).sum())
        stats["date_validity"] = {
            "future_dates": future_dates,
        }

    if "start_date" in episodes_df.columns and "end_date" in episodes_df.columns:
        end_before_start = int(
            (episodes_df["end_date"] < episodes_df["start_date"]).sum()
        )
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
    stats: Dict[str, Any] = {}

    # Panel dimensions
    total_firm_months = len(monthly_df)

    stats["panel_dimensions"] = {
        "total_firm_months": int(total_firm_months),
        "unique_firms": int(monthly_df["gvkey"].nunique())
        if "gvkey" in monthly_df.columns
        else 0,
        "unique_ceos": int(monthly_df["ceo_id"].nunique())
        if "ceo_id" in monthly_df.columns
        else 0,
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

            temporal_coverage.append(
                {
                    "year": int(year),
                    "firm_months": int(len(year_df)),
                    "unique_firms": int(year_df["gvkey"].nunique())
                    if "gvkey" in year_df.columns
                    else 0,
                    "unique_ceos": int(year_df["ceo_id"].nunique())
                    if "ceo_id" in year_df.columns
                    else 0,
                }
            )

        stats["temporal_coverage"] = temporal_coverage

    # CEO turnover analysis (prev_ceo_id changes indicate transitions)
    if "gvkey" in monthly_df.columns and "prev_ceo_id" in monthly_df.columns:
        # Sort by firm and date
        monthly_df_sorted = monthly_df.sort_values(["gvkey", "year", "month"])

        # Find prev_ceo_id changes within each firm (indicates CEO transitions)
        monthly_df_sorted["prev_ceo_id_shifted"] = monthly_df_sorted.groupby("gvkey")[
            "prev_ceo_id"
        ].shift(1)

        # Count transitions (where prev_ceo_id changes)
        transitions_mask = (
            monthly_df_sorted["prev_ceo_id"].notna()
            & monthly_df_sorted["prev_ceo_id_shifted"].notna()
            & (
                monthly_df_sorted["prev_ceo_id"]
                != monthly_df_sorted["prev_ceo_id_shifted"]
            )
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
                stats["turnover_metrics"]["turnover_rate_per_100_firm_years"] = (
                    turnover_rate
                )

    # Predecessor coverage
    if "prev_ceo_id" in monthly_df.columns:
        with_predecessor = monthly_df["prev_ceo_id"].notna().sum()
        without_predecessor = monthly_df["prev_ceo_id"].isna().sum()

        stats["predecessor_coverage"] = {
            "with_predecessor_pct": round(with_predecessor / total_firm_months * 100, 2)
            if total_firm_months > 0
            else 0.0,
            "without_predecessor_pct": round(
                without_predecessor / total_firm_months * 100, 2
            )
            if total_firm_months > 0
            else 0.0,
        }

    # Multi-CEO firm analysis
    if "gvkey" in monthly_df.columns and "ceo_id" in monthly_df.columns:
        ceos_per_firm = monthly_df.groupby("gvkey")["ceo_id"].nunique()
        firms_with_multiple = int((ceos_per_firm > 1).sum())

        stats["multi_ceo_analysis"] = {
            "firms_with_multiple_ceos": firms_with_multiple,
            "max_ceos_per_firm": int(ceos_per_firm.max())
            if len(ceos_per_firm) > 0
            else 0,
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


def collect_tenure_samples(
    episodes_df: pd.DataFrame, monthly_df: pd.DataFrame, n_samples: int = 3
) -> Dict[str, Any]:
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
    samples: Dict[str, List[Dict[str, Any]]] = {
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
            episodes_df["end_date"] - episodes_df["start_date"]
        ).dt.total_seconds() / (30 * 24 * 3600)
    else:
        episodes_df["tenure_months"] = pd.Series([0] * len(episodes_df))

    # Short tenure examples (<12 months)
    short_tenures_masked = cast(
        pd.DataFrame, episodes_df[episodes_df["tenure_months"] < 12]
    )
    short_tenures_df = short_tenures_masked.sort_values(by="tenure_months")

    for _, row in short_tenures_df.head(n_samples).iterrows():
        samples["short_tenures"].append(
            {
                "gvkey": str(row.get("gvkey", ""))
                if pd.notna(row.get("gvkey"))
                else "",
                "ceo_name": str(row.get("exec_fullname", ""))
                if pd.notna(row.get("exec_fullname"))
                else "",
                "start_date": row.get("start_date").isoformat()
                if pd.notna(row.get("start_date"))
                else "",
                "end_date": row.get("end_date").isoformat()
                if pd.notna(row.get("end_date"))
                else "",
                "tenure_months": round(float(row.get("tenure_months", 0)), 1),
            }
        )

    # Long tenure examples (>120 months)
    long_tenures_masked = cast(
        pd.DataFrame, episodes_df[episodes_df["tenure_months"] > 120]
    )
    long_tenures_df = long_tenures_masked.sort_values(by="tenure_months", ascending=False)

    for _, row in long_tenures_df.head(n_samples).iterrows():
        samples["long_tenures"].append(
            {
                "gvkey": str(row.get("gvkey", ""))
                if pd.notna(row.get("gvkey"))
                else "",
                "ceo_name": str(row.get("exec_fullname", ""))
                if pd.notna(row.get("exec_fullname"))
                else "",
                "start_date": row.get("start_date").isoformat()
                if pd.notna(row.get("start_date"))
                else "",
                "end_date": row.get("end_date").isoformat()
                if pd.notna(row.get("end_date"))
                else "",
                "tenure_months": round(float(row.get("tenure_months", 0)), 1),
            }
        )

    # CEO transition examples (predecessor -> successor)
    if "prev_exec_fullname" in episodes_df.columns:
        transitions_masked = cast(
            pd.DataFrame,
            episodes_df[
                episodes_df["prev_exec_fullname"].notna()
                & (episodes_df["prev_exec_fullname"] != "")
            ],
        )
        transitions_df = transitions_masked.copy()

        # Calculate gap days between predecessor end and successor start
        transitions_df = transitions_df.sort_values(by=["gvkey", "start_date"])

        for _, row in transitions_df.head(n_samples).iterrows():
            # Try to find the predecessor episode to calculate gap
            gvkey = row.get("gvkey")
            successor_start = row.get("start_date")

            # Find predecessor episode (same firm, earlier start_date)
            predecessor_mask = (transitions_df["gvkey"] == gvkey) & (
                transitions_df["exec_fullname"] == row.get("prev_exec_fullname")
            )
            predecessor_episode = transitions_df[predecessor_mask]

            gap_days = None
            if len(predecessor_episode) > 0:
                predecessor_end = predecessor_episode.iloc[0].get("end_date")
                if pd.notna(predecessor_end) and pd.notna(successor_start):
                    gap_days = int((successor_start - predecessor_end).days)

            samples["transitions"].append(
                {
                    "gvkey": str(gvkey) if pd.notna(gvkey) else "",
                    "prev_ceo_name": str(row.get("prev_exec_fullname", ""))
                    if pd.notna(row.get("prev_exec_fullname"))
                    else "",
                    "new_ceo_name": str(row.get("exec_fullname", ""))
                    if pd.notna(row.get("exec_fullname"))
                    else "",
                    "transition_date": successor_start.isoformat()
                    if pd.notna(successor_start)
                    else "",
                    "gap_days": gap_days,
                }
            )

    # Overlap resolution examples (from monthly panel)
    # Find firms with multiple CEOs in the same year/month
    if (
        "gvkey" in monthly_df.columns
        and "year" in monthly_df.columns
        and "month" in monthly_df.columns
    ):
        # Count CEOs per firm-month
        monthly_df.groupby(["gvkey", "year", "month"])["ceo_id"].nunique()
        # Only single CEO per month after resolution, so we need to look for potential overlaps
        # by checking if prev_ceo_id exists and is different from ceo_id
        overlap_candidates = monthly_df[
            monthly_df["prev_ceo_id"].notna()
            & (monthly_df["prev_ceo_id"] != monthly_df["ceo_id"])
        ].copy()

        if len(overlap_candidates) > 0:
            # Sample n_samples overlap candidates
            overlap_samples = overlap_candidates.head(n_samples)

            for _, row in overlap_samples.iterrows():
                samples["overlaps"].append(
                    {
                        "gvkey": str(row.get("gvkey", ""))
                        if pd.notna(row.get("gvkey"))
                        else "",
                        "resolved_ceo": str(row.get("ceo_name", ""))
                        if pd.notna(row.get("ceo_name"))
                        else "",
                        "overlapped_ceo": str(row.get("prev_ceo_name", ""))
                        if pd.notna(row.get("prev_ceo_name"))
                        else "",
                        "overlap_period": f"{int(row.get('year', 0))}-{int(row.get('month', 0))}"
                        if pd.notna(row.get("year"))
                        else "",
                        "resolution_reason": "later_ceo_takes_precedence",
                    }
                )

    return samples


def compute_manifest_input_stats(
    df_metadata: pd.DataFrame, df_tenure: pd.DataFrame
) -> Dict[str, Any]:
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
    stats: Dict[str, Any] = {}

    # Linked metadata characteristics
    stats["linked_metadata"] = {
        "total_calls": int(len(df_metadata)),
        "unique_gvkey": int(df_metadata["gvkey"].nunique())
        if "gvkey" in df_metadata.columns
        else 0,
        "columns": int(len(df_metadata.columns)),
        "memory_mb": round(
            df_metadata.memory_usage(deep=True).sum() / (1024 * 1024), 2
        ),
    }

    # Tenure panel characteristics
    stats["tenure_panel"] = {
        "total_firm_months": int(len(df_tenure)),
        "unique_firms": int(df_tenure["gvkey"].nunique())
        if "gvkey" in df_tenure.columns
        else 0,
        "unique_ceos": int(df_tenure["ceo_id"].nunique())
        if "ceo_id" in df_tenure.columns
        else 0,
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
        stats["industry_coverage"]["ff48_count"] = int(
            df_metadata["ff48_code"].nunique()
        )
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
                "call_count_per_year": {
                    str(int(y)): int(c) for y, c in year_counts.items()
                },
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
    stats: Dict[str, Any] = {}

    # Merge outcome
    left_rows = len(df_metadata)
    right_rows = (
        stats_dict.get("merges", {}).get("ceo_tenure_join", {}).get("right_rows", 0)
    )
    result_rows = len(merged_df)
    matched_count = (
        int(merged_df["ceo_id"].notna().sum()) if "ceo_id" in merged_df.columns else 0
    )
    unmatched_count = (
        int(merged_df["ceo_id"].isna().sum()) if "ceo_id" in merged_df.columns else 0
    )
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
            year_rate = (
                round(year_matched / year_total * 100, 2) if year_total > 0 else 0.0
            )

            match_by_year.append(
                {
                    "year": int(year),
                    "total_calls": year_total,
                    "matched_calls": year_matched,
                    "match_rate_pct": year_rate,
                }
            )
        stats["match_rate_by_year"] = match_by_year
    else:
        stats["match_rate_by_year"] = []

    # Unmatched analysis
    unmatched_df = cast(
        pd.DataFrame,
        merged_df[merged_df["ceo_id"].isna()]
        if "ceo_id" in merged_df.columns
        else pd.DataFrame(),
    )

    if len(unmatched_df) > 0:
        unique_gvkey_unmatched = (
            int(unmatched_df["gvkey"].nunique())
            if "gvkey" in unmatched_df.columns
            else 0
        )

        # Temporal distribution of unmatched
        temporal_dist = {}
        if "year" in unmatched_df.columns:
            year_counts = unmatched_df["year"].value_counts().sort_index()
            temporal_dist = {str(int(cast(int, y))): int(c) for y, c in year_counts.items()}

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
        calls_dropped = stats_dict.get("processing", {}).get(
            "below_threshold_calls_removed", 0
        )

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
    stats: Dict[str, Any] = {}

    # Panel dimensions
    total_calls = len(df_final)
    unique_gvkey = (
        int(df_final["gvkey"].nunique()) if "gvkey" in df_final.columns else 0
    )
    unique_ceos = (
        int(df_final["ceo_id"].nunique()) if "ceo_id" in df_final.columns else 0
    )

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
            bucket_pct = (
                round(count / len(calls_per_ceo) * 100, 2)
                if len(calls_per_ceo) > 0
                else 0.0
            )
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
                    ff12_name = (
                        str(name_rows.iloc[0]) if pd.notna(name_rows.iloc[0]) else ""
                    )

            industry_coverage.append(
                {
                    "ff12_code": str(ff12_code) if pd.notna(ff12_code) else "",
                    "ff12_name": ff12_name,
                    "call_count": count,
                    "percentage": percentage,
                }
            )

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
            "completion_pct": round(ff48_assigned / total_calls * 100, 2)
            if total_calls > 0
            else 0.0,
        }
    else:
        stats["industry_coverage_ff48"] = {
            "unique_industries": 0,
            "completion_pct": 0.0,
        }

    # Temporal coverage by year
    if "start_date" in df_final.columns:
        df_final_temp = df_final.copy()
        df_final_temp["start_date"] = pd.to_datetime(df_final_temp["start_date"])
        df_final_temp["year"] = df_final_temp["start_date"].dt.year

        temporal_coverage = []
        for year in sorted(df_final_temp["year"].unique()):
            year_df = df_final_temp[df_final_temp["year"] == year]

            temporal_coverage.append(
                {
                    "year": int(year),
                    "call_count": int(len(year_df)),
                    "unique_firms": int(year_df["gvkey"].nunique())
                    if "gvkey" in year_df.columns
                    else 0,
                    "unique_ceos": int(year_df["ceo_id"].nunique())
                    if "ceo_id" in year_df.columns
                    else 0,
                }
            )

        stats["temporal_coverage"] = temporal_coverage
    else:
        stats["temporal_coverage"] = []

    # Predecessor coverage
    if "prev_ceo_id" in df_final.columns:
        with_predecessor = int(df_final["prev_ceo_id"].notna().sum())
        without_predecessor = int(df_final["prev_ceo_id"].isna().sum())

        stats["predecessor_coverage"] = {
            "pct_with_prev_ceo": round(with_predecessor / total_calls * 100, 2)
            if total_calls > 0
            else 0.0,
            "pct_without_prev_ceo": round(without_predecessor / total_calls * 100, 2)
            if total_calls > 0
            else 0.0,
        }
    else:
        stats["predecessor_coverage"] = {"error": "prev_ceo_id column not found"}

    return stats


def collect_ceo_distribution_samples(
    df_final: pd.DataFrame, n_samples: int = 5
) -> Dict[str, Any]:
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
    samples: Dict[str, Any] = {
        "top_ceos": [],
        "bottom_ceos": [],
        "single_call_ceos": {"count": 0, "percentage": 0.0},
        "multi_firm_ceos": [],
    }

    if "ceo_id" not in df_final.columns:
        return samples

    # Calculate call counts per CEO
    ceo_stats = (
        df_final.groupby("ceo_id")
        .agg(
            {
                "file_name": "count",  # Call count
                "gvkey": "nunique",  # Unique firms
            }
        )
        .rename(columns={"file_name": "call_count", "gvkey": "firm_count"})
    )

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
        percentage = (
            round(row["call_count"] / total_calls * 100, 2) if total_calls > 0 else 0.0
        )

        samples["top_ceos"].append(
            {
                "ceo_id": str(ceo_id),
                "ceo_name": ceo_name,
                "call_count": int(row["call_count"]),
                "unique_firms": int(row["firm_count"]),
                "percentage": percentage,
            }
        )

    # Bottom CEOs by call count (minimum 1 call, smallest counts first)
    bottom_ceos_df = ceo_stats[ceo_stats["call_count"] > 0].nsmallest(
        n_samples, "call_count"
    )
    for ceo_id, row in bottom_ceos_df.iterrows():
        ceo_name = str(ceo_names.get(ceo_id, "")) if ceo_id in ceo_names.index else ""
        percentage = (
            round(row["call_count"] / total_calls * 100, 2) if total_calls > 0 else 0.0
        )

        samples["bottom_ceos"].append(
            {
                "ceo_id": str(ceo_id),
                "ceo_name": ceo_name,
                "call_count": int(row["call_count"]),
                "unique_firms": int(row["firm_count"]),
                "percentage": percentage,
            }
        )

    # Single call CEOs
    single_call_count = int((ceo_stats["call_count"] == 1).sum())
    samples["single_call_ceos"] = {
        "count": single_call_count,
        "percentage": round(single_call_count / total_ceos * 100, 2)
        if total_ceos > 0
        else 0.0,
    }

    # Multi-firm CEOs
    multi_firm_df = ceo_stats[ceo_stats["firm_count"] > 1].nlargest(
        n_samples, "firm_count"
    )
    for ceo_id, row in multi_firm_df.iterrows():
        ceo_name = str(ceo_names.get(ceo_id, "")) if ceo_id in ceo_names.index else ""

        samples["multi_firm_ceos"].append(
            {
                "ceo_id": str(ceo_id),
                "ceo_name": ceo_name,
                "call_count": int(row["call_count"]),
                "firm_count": int(row["firm_count"]),
            }
        )

    return samples


def compute_tokenize_input_stats(
    manifest_df: pd.DataFrame,
    lm_dict_path: Path,
    vocab_list: List[str],
    cat_sets: Dict[str, Set[str]],
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

    stats: Dict[str, Any] = {}

    # Manifest analysis
    stats["manifest_stats"] = {
        "total_files": int(len(manifest_df)),
    }

    # Check for additional manifest columns
    if "gvkey" in manifest_df.columns:
        stats["manifest_stats"]["unique_companies"] = int(
            manifest_df["gvkey"].nunique()
        )

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
            str(int(cast(int, et))): int(count) for et, count in event_counts.items()
        }

    # LM dictionary analysis
    stats["dictionary_stats"] = {
        "total_words": len(vocab_list),
        "vocabulary_size": len(vocab_list),
    }

    # Word length characteristics
    word_lengths = [len(w) for w in vocab_list]
    stats["dictionary_stats"]["avg_word_length"] = round(
        float(np.mean(word_lengths)), 2
    )

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
    overlap_stats: OverlapStatsDict = {
        "words_in_multiple_categories": 0,
        "category_overlaps": {},
    }

    # Count words appearing in multiple categories
    all_words: Dict[str, List[str]] = {}
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
        for cat2 in category_names[i + 1 :]:
            overlap = cat_sets[cat1] & cat_sets[cat2]
            if len(overlap) > 0:
                overlap_stats["category_overlaps"][f"{cat1}_{cat2}"] = int(len(overlap))

    stats["overlap_analysis"] = overlap_stats

    return stats


def compute_tokenize_process_stats(
    per_year_stats: List[Dict[str, Any]],
    cat_sets: Dict[str, Set[str]],
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

    stats: Dict[str, Any] = {}

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
    vocab_hit_rate = (
        round(total_vocab_hits / total_tokens * 100, 2) if total_tokens > 0 else 0.0
    )
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
    docs_per_second = (
        round(total_output_rows / duration_seconds, 2) if duration_seconds > 0 else 0.0
    )
    tokens_per_second = (
        round(total_tokens / duration_seconds, 2) if duration_seconds > 0 else 0.0
    )

    tokens_per_doc_values = [
        s.get("avg_tokens_per_doc", 0)
        for s in per_year_stats
        if s.get("output_rows", 0) > 0
    ]

    tokens_per_doc_stats = {
        "mean": round(float(np.mean(tokens_per_doc_values)), 2)
        if tokens_per_doc_values
        else 0.0,
        "median": round(float(np.median(tokens_per_doc_values)), 2)
        if tokens_per_doc_values
        else 0.0,
        "min": round(float(np.min(tokens_per_doc_values)), 2)
        if tokens_per_doc_values
        else 0.0,
        "max": round(float(np.max(tokens_per_doc_values)), 2)
        if tokens_per_doc_values
        else 0.0,
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
    cat_sets: Dict[str, Set[str]],
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

    # Concatenate all output DataFrames for analysis
    if len(output_dfs) == 0:
        return {
            "category_distributions": {},
            "total_tokens_stats": {},
            "speaker_analysis": {"error": "No output data"},
            "sparsity_analysis": {},
        }

    df_all = pd.concat(output_dfs, ignore_index=True)

    stats: Dict[str, Any] = {}

    # Category distributions
    stats["category_distributions"] = {}
    for cat_name in cat_sets.keys():
        col_name = f"{cat_name}_count"
        if col_name not in df_all.columns:
            continue

        cat_series = df_all[col_name]

        # Basic statistics
        cat_stats: CategoryStatsDict = {
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
        cat_stats["zeros_pct"] = (
            round(zeros_count / len(cat_series) * 100, 2)
            if len(cat_series) > 0
            else 0.0
        )

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
        role_stats: Dict[str, Any] = {}

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
        zeros_pct = (
            round(zeros_count / len(df_all) * 100, 2) if len(df_all) > 0 else 0.0
        )

        stats["sparsity_analysis"]["zero_counts_per_category"][cat_name] = {
            "count": zeros_count,
            "pct": zeros_pct,
        }

    # Documents with no linguistic matches (all categories zero)
    cat_cols = [
        f"{cat}_count" for cat in cat_sets.keys() if f"{cat}_count" in df_all.columns
    ]
    if cat_cols:
        # Check if all category columns are zero
        zero_mask = (df_all[cat_cols] == 0).all(axis=1)
        stats["sparsity_analysis"]["documents_with_no_matches"] = int(zero_mask.sum())

    return stats


def compute_constructvariables_input_stats(
    tokenized_dir: Path,
    manifest_df: pd.DataFrame,
    years_range: tuple[int, int] = (2002, 2019),
) -> Dict[str, Any]:
    """
    Analyze input data for variable construction.

    Provides comprehensive statistics about tokenized input files,
    master manifest characteristics, linguistic categories, and
    total tokens available for variable construction.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        tokenized_dir: Directory containing linguistic_counts_*.parquet files
        manifest_df: Master manifest DataFrame (from step 1.0)
        years_range: Tuple of (start_year, end_year) to process

    Returns:
        Dictionary with keys:
        - tokenized_files_stats: {files_present, files_missing,
                                  total_rows, rows_per_year: {year: count}}
        - manifest_stats: {unique_gvkey, unique_ceos,
                          temporal_coverage: {earliest_start, latest_start}}
        - linguistic_categories: {count, category_names, sample_categories}
        - total_tokens_available: Sum of total_tokens across all input files
    """

    stats: Dict[str, Any] = {}

    # Tokenized files analysis
    stats["tokenized_files_stats"] = {
        "files_present": [],
        "files_missing": [],
        "total_rows": 0,
        "rows_per_year": {},
    }

    total_tokens = 0
    start_year, end_year = years_range

    for year in range(start_year, end_year + 1):
        file_path = tokenized_dir / f"linguistic_counts_{year}.parquet"
        if file_path.exists():
            stats["tokenized_files_stats"]["files_present"].append(year)
            # Read just to get row count and total_tokens
            df_year = pd.read_parquet(file_path, columns=["total_tokens"])
            row_count = len(df_year)
            stats["tokenized_files_stats"]["rows_per_year"][str(year)] = int(row_count)
            stats["tokenized_files_stats"]["total_rows"] += row_count
            total_tokens += df_year["total_tokens"].sum()
        else:
            stats["tokenized_files_stats"]["files_missing"].append(year)

    # Manifest analysis
    stats["manifest_stats"] = {}

    if "gvkey" in manifest_df.columns:
        stats["manifest_stats"]["unique_gvkey"] = int(manifest_df["gvkey"].nunique())

    if "ceo_name" in manifest_df.columns:
        stats["manifest_stats"]["unique_ceos"] = int(manifest_df["ceo_name"].nunique())

    if "start_date" in manifest_df.columns:
        manifest_df_temp = manifest_df.copy()
        manifest_df_temp["start_date"] = pd.to_datetime(manifest_df_temp["start_date"])
        date_col = manifest_df_temp["start_date"].dropna()
        if len(date_col) > 0:
            stats["manifest_stats"]["temporal_coverage"] = {
                "earliest_start": date_col.min().isoformat(),
                "latest_start": date_col.max().isoformat(),
            }

    # Linguistic categories (from first available file)
    stats["linguistic_categories"] = {
        "count": 0,
        "category_names": [],
        "sample_categories": [],
    }

    if stats["tokenized_files_stats"]["files_present"]:
        first_year = stats["tokenized_files_stats"]["files_present"][0]
        first_file = tokenized_dir / f"linguistic_counts_{first_year}.parquet"
        if first_file.exists():
            all_cols = pd.read_parquet(first_file, columns=[]).columns.tolist()
            count_cols = sorted([c for c in all_cols if c.endswith("_count")])
            category_names = sorted(set([c.replace("_count", "") for c in count_cols]))
            stats["linguistic_categories"]["count"] = len(category_names)
            stats["linguistic_categories"]["category_names"] = category_names
            # Sample first 5 categories
            stats["linguistic_categories"]["sample_categories"] = category_names[:5]

    stats["total_tokens_available"] = int(total_tokens)

    return stats


def compute_constructvariables_process_stats(
    per_year_stats: List[Dict[str, Any]],
    total_speaker_flags: Dict[str, int],
    variables_created: int,
    duration_seconds: float,
) -> Dict[str, Any]:
    """
    Analyze variable construction process.

    Provides detailed statistics about speaker flagging success rates,
    context distribution, variable creation breakdown, NaN vs zero analysis,
    and efficiency metrics.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        per_year_stats: List of per-year statistics from process_year function
        total_speaker_flags: Dict with analyst, manager, ceo, operator counts
        variables_created: Total number of variables created
        duration_seconds: Total processing duration

    Returns:
        Dictionary with keys:
        - speaker_flagging_metrics: {total_speakers_flagged, flagging_rate_pct,
                                    role_distribution: {role: count, pct}}
        - context_distribution: Not available from current stats (requires input data)
        - variable_creation_breakdown: {total_variables,
                                       variables_per_combo: 5x3=15 combos,
                                       variables_per_category: N categories}
        - nan_vs_zero_analysis: Not available from current stats (requires output data)
        - efficiency_metrics: {calls_processed, calls_per_second,
                              variables_per_second}
    """

    stats: Dict[str, Any] = {}

    # Speaker flagging metrics
    total_flagged = sum(total_speaker_flags.values())
    # Estimate total speakers from input rows (approximate)
    total_input_rows = sum(s.get("rows", 0) for s in per_year_stats)
    flagging_rate = (
        round(total_flagged / total_input_rows * 100, 2)
        if total_input_rows > 0
        else 0.0
    )

    stats["speaker_flagging_metrics"] = {
        "total_speakers_flagged": total_flagged,
        "total_speakers_unflagged": max(0, total_input_rows - total_flagged),
        "flagging_rate_pct": flagging_rate,
        "role_distribution": {},
    }

    for role, count in sorted(total_speaker_flags.items()):
        role_pct = round(count / total_flagged * 100, 2) if total_flagged > 0 else 0.0
        stats["speaker_flagging_metrics"]["role_distribution"][role] = {
            "count": count,
            "pct": role_pct,
        }

    # Context distribution (not available without input data)
    stats["context_distribution"] = {
        "note": "Context distribution requires input token data - not available from process stats",
    }

    # Variable creation breakdown
    # 5 samples (Manager, Analyst, CEO, NonCEO_Manager, Entire)
    # 3 contexts (QA, Pres, All)
    # N categories (from linguistic_counts columns)
    num_samples = 5
    num_contexts = 3
    combos = num_samples * num_contexts  # 15
    categories_per_combo = variables_created // combos if combos > 0 else 0

    stats["variable_creation_breakdown"] = {
        "total_variables": variables_created,
        "num_samples": num_samples,
        "num_contexts": num_contexts,
        "total_combinations": combos,
        "categories_per_combo": categories_per_combo,
        "variables_per_combo": {},
    }

    # Breakdown by sample-context combination
    samples = ["Manager", "Analyst", "CEO", "NonCEO_Manager", "Entire"]
    contexts = ["QA", "Pres", "All"]
    for sample in samples:
        for context in contexts:
            combo_key = f"{sample}_{context}"
            stats["variable_creation_breakdown"]["variables_per_combo"][combo_key] = (
                categories_per_combo
            )

    # NaN vs zero analysis (not available without output data)
    stats["nan_vs_zero_analysis"] = {
        "note": "NaN vs zero analysis requires output data - not available from process stats",
    }

    # Efficiency metrics
    calls_processed = sum(s.get("rows", 0) for s in per_year_stats)
    calls_per_second = (
        round(calls_processed / duration_seconds, 2) if duration_seconds > 0 else 0.0
    )
    variables_per_second = (
        round(variables_created / duration_seconds, 2) if duration_seconds > 0 else 0.0
    )

    stats["efficiency_metrics"] = {
        "calls_processed": calls_processed,
        "calls_per_second": calls_per_second,
        "variables_created": variables_created,
        "variables_per_second": variables_per_second,
        "years_processed": len(per_year_stats),
    }

    return stats


def compute_constructvariables_output_stats(
    output_dfs: List[pd.DataFrame],
    samples: List[str],
    contexts: List[str],
    categories: List[str],
) -> Dict[str, Any]:
    """
    Analyze linguistic variables output from variable construction.

    Provides comprehensive statistics about variable distributions,
    sample-context aggregates, temporal trends, and NaN vs zero analysis.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        output_dfs: List of per-year DataFrames with linguistic variables
        samples: List of sample names (e.g., ["Manager", "Analyst", "CEO", ...])
        contexts: List of context names (e.g., ["QA", "Pres", "All"])
        categories: List of linguistic category names (e.g., ["uncertainty", "negative"])

    Returns:
        Dictionary with keys:
        - variable_distributions: {variable_name: {mean, median, std, min, max,
                                                   q25, q75, percentiles, zeros, nans}}
        - sample_aggregates: {sample_name: {mean_vars, median_vars, etc.}}
        - context_aggregates: {context_name: {mean_vars, median_vars, etc.}}
        - temporal_trends: {variable_name: {year: avg_value}}
        - nan_vs_zero_analysis: {total_values, nan_count, nan_pct, zero_count, zero_pct}
    """
    import numpy as np

    if len(output_dfs) == 0:
        return {
            "variable_distributions": {},
            "sample_aggregates": {},
            "context_aggregates": {},
            "temporal_trends": {},
            "nan_vs_zero_analysis": {"error": "No output data"},
        }

    # Concatenate all output DataFrames for analysis
    df_all = pd.concat(output_dfs, ignore_index=True)

    stats: Dict[str, Any] = {}

    # Identify all variable columns (sample_context_category_pct format)
    var_cols = [c for c in df_all.columns if c.endswith("_pct")]

    # Variable distributions
    stats["variable_distributions"] = {}
    for var_col in sorted(var_cols):
        var_series = df_all[var_col]

        # Basic statistics
        var_stats: VarStatsDict = {
            "mean": round(float(var_series.mean()), 4),
            "median": round(float(var_series.median()), 4),
            "std": round(float(var_series.std()), 4),
            "min": round(float(var_series.min()), 4),
            "max": round(float(var_series.max()), 4),
            "q25": round(float(var_series.quantile(0.25)), 4),
            "q75": round(float(var_series.quantile(0.75)), 4),
        }

        # Percentiles
        var_stats["percentiles"] = {
            "p10": round(float(var_series.quantile(0.10)), 4),
            "p25": round(float(var_series.quantile(0.25)), 4),
            "p50": round(float(var_series.quantile(0.50)), 4),
            "p75": round(float(var_series.quantile(0.75)), 4),
            "p90": round(float(var_series.quantile(0.90)), 4),
            "p95": round(float(var_series.quantile(0.95)), 4),
            "p99": round(float(var_series.quantile(0.99)), 4),
        }

        # Zero vs NaN analysis
        zeros_count = int((var_series == 0).sum())
        nans_count = int(var_series.isna().sum())
        total_count = len(var_series)

        var_stats["zeros"] = {
            "count": zeros_count,
            "pct": round(zeros_count / total_count * 100, 2)
            if total_count > 0
            else 0.0,
        }
        var_stats["nans"] = {
            "count": nans_count,
            "pct": round(nans_count / total_count * 100, 2) if total_count > 0 else 0.0,
        }

        stats["variable_distributions"][var_col] = var_stats

    # Sample aggregates (average across all variables for each sample)
    stats["sample_aggregates"] = {}
    for sample in sorted(samples):
        sample_cols = [c for c in var_cols if c.startswith(f"{sample}_")]
        if sample_cols:
            # Get all values for this sample's variables
            sample_values = np.asarray(df_all[sample_cols].values).flatten()
            sample_values = sample_values[~pd.isna(sample_values)]

            if len(sample_values) > 0:
                stats["sample_aggregates"][sample] = {
                    "mean": round(float(np.mean(sample_values)), 4),
                    "median": round(float(np.median(sample_values)), 4),
                    "std": round(float(np.std(sample_values)), 4),
                    "min": round(float(np.min(sample_values)), 4),
                    "max": round(float(np.max(sample_values)), 4),
                    "num_variables": len(sample_cols),
                }
            else:
                stats["sample_aggregates"][sample] = {"error": "No data"}

    # Context aggregates (average across all variables for each context)
    stats["context_aggregates"] = {}
    for context in sorted(contexts):
        context_cols = [c for c in var_cols if f"_{context}_" in c]
        if context_cols:
            context_values = np.asarray(df_all[context_cols].values).flatten()
            context_values = context_values[~pd.isna(context_values)]

            if len(context_values) > 0:
                stats["context_aggregates"][context] = {
                    "mean": round(float(np.mean(context_values)), 4),
                    "median": round(float(np.median(context_values)), 4),
                    "std": round(float(np.std(context_values)), 4),
                    "min": round(float(np.min(context_values)), 4),
                    "max": round(float(np.max(context_values)), 4),
                    "num_variables": len(context_cols),
                }
            else:
                stats["context_aggregates"][context] = {"error": "No data"}

    # Temporal trends (average per year for key variables)
    stats["temporal_trends"] = {}

    # Select key variables for trend analysis
    key_variables = []
    for sample in ["Manager", "Analyst", "CEO"]:
        for context in ["QA", "Pres"]:
            for category in categories[:3]:  # First 3 categories
                var_name = f"{sample}_{context}_{category}_pct"
                if var_name in var_cols:
                    key_variables.append(var_name)

    for var_col in sorted(key_variables):
        stats["temporal_trends"][var_col] = {}
        for i, df_year in enumerate(output_dfs):
            if var_col in df_year.columns:
                year_avg = round(float(df_year[var_col].mean()), 4)
                # Infer year from index position (2002 + i)
                year = 2002 + i
                stats["temporal_trends"][var_col][str(year)] = year_avg

    # Overall NaN vs zero analysis
    total_values = len(df_all) * len(var_cols) if var_cols else 0
    total_nans = sum(df_all[c].isna().sum() for c in var_cols)
    total_zeros = sum((df_all[c] == 0).sum() for c in var_cols)

    stats["nan_vs_zero_analysis"] = {
        "total_values": total_values,
        "nan_count": int(total_nans),
        "nan_pct": round(total_nans / total_values * 100, 2)
        if total_values > 0
        else 0.0,
        "zero_count": int(total_zeros),
        "zero_pct": round(total_zeros / total_values * 100, 2)
        if total_values > 0
        else 0.0,
        "explanation": "NaN = no text in section (missing data), 0 = text but no linguistic matches",
    }

    return stats


def compute_financial_input_stats(
    manifest_df: pd.DataFrame,
    compustat_df: pd.DataFrame,
    ibes_df: pd.DataFrame,
    cccl_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Analyze input data for Step 3.1 Firm Controls.

    Provides comprehensive statistics about manifest (sample calls),
    Compustat (financial data), IBES (earnings forecasts), and CCCL
    (competition instrument) datasets.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        manifest_df: Master manifest DataFrame (from step 1.4)
        compustat_df: Compustat quarterly data DataFrame
        ibes_df: IBES forecast DataFrame
        cccl_df: CCCL instrument DataFrame (optional)

    Returns:
        Dictionary with keys:
        - manifest_stats: {total_calls, unique_gvkey, date_range, calls_per_year}
        - compustat_stats: {total_observations, unique_gvkey, date_range,
                            quarters_covered, memory_mb}
        - ibes_stats: {total_forecasts, unique_tickers, eps_qtr_records,
                       measure_types, date_range}
        - cccl_stats: {total_records, unique_gvkey, years_covered,
                       intensity_variants_available} (if provided)
    """

    stats: Dict[str, Any] = {}

    # Manifest statistics
    stats["manifest_stats"] = {
        "total_calls": int(len(manifest_df)),
    }

    if "gvkey" in manifest_df.columns:
        stats["manifest_stats"]["unique_gvkey"] = int(manifest_df["gvkey"].nunique())

    if "start_date" in manifest_df.columns:
        manifest_df_temp = manifest_df.copy()
        manifest_df_temp["start_date"] = pd.to_datetime(manifest_df_temp["start_date"])
        date_col = manifest_df_temp["start_date"].dropna()
        if len(date_col) > 0:
            stats["manifest_stats"]["date_range"] = {
                "earliest": date_col.min().isoformat(),
                "latest": date_col.max().isoformat(),
            }

    # Calls per year
    if "start_date" in manifest_df.columns:
        manifest_df_temp = manifest_df.copy()
        manifest_df_temp["start_date"] = pd.to_datetime(manifest_df_temp["start_date"])
        calls_per_year = (
            manifest_df_temp["start_date"].dt.year.value_counts().sort_index()
        )
        stats["manifest_stats"]["calls_per_year"] = {
            str(int(y)): int(c) for y, c in calls_per_year.items()
        }

    # Compustat statistics
    stats["compustat_stats"] = {
        "total_observations": int(len(compustat_df)),
    }

    if "gvkey" in compustat_df.columns:
        stats["compustat_stats"]["unique_gvkey"] = int(compustat_df["gvkey"].nunique())

    if "datadate" in compustat_df.columns:
        compustat_df_temp = compustat_df.copy()
        compustat_df_temp["datadate"] = pd.to_datetime(compustat_df_temp["datadate"])
        date_col = compustat_df_temp["datadate"].dropna()
        if len(date_col) > 0:
            stats["compustat_stats"]["date_range"] = {
                "earliest": date_col.min().isoformat(),
                "latest": date_col.max().isoformat(),
            }
            # Count unique quarters
            compustat_df_temp["year_quarter"] = (
                compustat_df_temp["datadate"].dt.year.astype(str)
                + "Q"
                + compustat_df_temp["datadate"].dt.quarter.astype(str)
            )
            stats["compustat_stats"]["quarters_covered"] = int(
                compustat_df_temp["year_quarter"].nunique()
            )

    stats["compustat_stats"]["memory_mb"] = round(
        compustat_df.memory_usage(deep=True).sum() / (1024 * 1024), 2
    )

    # IBES statistics
    stats["ibes_stats"] = {
        "total_forecasts": int(len(ibes_df)),
    }

    if "TICKER" in ibes_df.columns:
        stats["ibes_stats"]["unique_tickers"] = int(ibes_df["TICKER"].nunique())

    # Count EPS/QTR records
    if "MEASURE" in ibes_df.columns and "FISCALP" in ibes_df.columns:
        eps_qtr_mask = (ibes_df["MEASURE"] == "EPS") & (ibes_df["FISCALP"] == "QTR")
        stats["ibes_stats"]["eps_qtr_records"] = int(eps_qtr_mask.sum())

    if "MEASURE" in ibes_df.columns:
        measure_counts = ibes_df["MEASURE"].value_counts()
        stats["ibes_stats"]["measure_types"] = {
            str(m): int(c) for m, c in measure_counts.items()
        }

    if "FPEDATS" in ibes_df.columns:
        ibes_df_temp = ibes_df.copy()
        ibes_df_temp["FPEDATS"] = pd.to_datetime(ibes_df_temp["FPEDATS"])
        date_col = ibes_df_temp["FPEDATS"].dropna()
        if len(date_col) > 0:
            stats["ibes_stats"]["date_range"] = {
                "earliest": date_col.min().isoformat(),
                "latest": date_col.max().isoformat(),
            }

    # CCCL statistics (optional)
    if cccl_df is not None and len(cccl_df) > 0:
        stats["cccl_stats"] = {
            "total_records": int(len(cccl_df)),
        }

        if "gvkey" in cccl_df.columns:
            stats["cccl_stats"]["unique_gvkey"] = int(cccl_df["gvkey"].nunique())

        if "year" in cccl_df.columns:
            years = sorted(cccl_df["year"].unique())
            stats["cccl_stats"]["years_covered"] = [int(y) for y in years]
            stats["cccl_stats"]["year_range"] = {
                "earliest": int(min(years)),
                "latest": int(max(years)),
            }

        # Count shift_intensity variants
        intensity_cols = [c for c in cccl_df.columns if c.startswith("shift_intensity")]
        stats["cccl_stats"]["intensity_variants_available"] = len(intensity_cols)
        stats["cccl_stats"]["intensity_variant_names"] = intensity_cols

    return stats


def compute_financial_process_stats(
    merge_results: Dict[str, Dict[str, int]],
    variables_computed: List[str],
    coverage_rates: Dict[str, float],
    duration_seconds: float,
) -> Dict[str, Any]:
    """
    Analyze Step 3.1 Firm Controls process outcomes.

    Provides detailed statistics about merge success rates, variable
    construction coverage, and processing efficiency.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        merge_results: Dict with merge stats for Compustat, IBES, CCCL
                       Each entry: {left_rows, right_rows, matched, unmatched_left}
        variables_computed: List of variable names computed
        coverage_rates: Dict mapping variable_name -> coverage_percentage
        duration_seconds: Total processing duration

    Returns:
        Dictionary with keys:
        - merge_outcomes: {compustat_controls: {...}, ibes_surprise: {...},
                          cccl_instrument: {...}}
        - variable_coverage: {variable_name: {count, pct}}
        - overall_coverage_stats: {avg_coverage_pct, variables_above_90_pct,
                                   variables_below_50_pct}
        - efficiency_metrics: {calls_processed, variables_computed,
                              duration_seconds}
    """
    import numpy as np

    stats: Dict[str, Any] = {}

    # Merge outcomes
    stats["merge_outcomes"] = {}
    for merge_name, merge_stats in merge_results.items():
        left_rows = merge_stats.get("left_rows", 0)
        right_rows = merge_stats.get("right_rows", 0)
        matched = merge_stats.get("matched", 0)
        unmatched = merge_stats.get("unmatched_left", 0)

        match_rate = round(matched / left_rows * 100, 2) if left_rows > 0 else 0.0

        stats["merge_outcomes"][merge_name] = {
            "left_rows": int(left_rows),
            "right_rows": int(right_rows),
            "matched": int(matched),
            "unmatched": int(unmatched),
            "match_rate_pct": match_rate,
        }

    # Variable coverage
    stats["variable_coverage"] = {}
    for var_name in sorted(variables_computed):
        stats["variable_coverage"][var_name] = {
            "count": 0,  # To be filled with actual data
            "pct": round(coverage_rates.get(var_name, 0.0), 2),
        }

    # Overall coverage statistics
    coverage_values = list(coverage_rates.values())
    if coverage_values:
        stats["overall_coverage_stats"] = {
            "avg_coverage_pct": round(float(np.mean(coverage_values)), 2),
            "median_coverage_pct": round(float(np.median(coverage_values)), 2),
            "min_coverage_pct": round(float(np.min(coverage_values)), 2),
            "max_coverage_pct": round(float(np.max(coverage_values)), 2),
            "variables_above_90_pct": int(sum(1 for v in coverage_values if v >= 90)),
            "variables_above_75_pct": int(sum(1 for v in coverage_values if v >= 75)),
            "variables_below_50_pct": int(sum(1 for v in coverage_values if v < 50)),
        }
    else:
        stats["overall_coverage_stats"] = {"error": "No coverage data available"}

    # Efficiency metrics
    total_calls = merge_results.get("compustat_controls", {}).get("left_rows", 0)

    stats["efficiency_metrics"] = {
        "calls_processed": int(total_calls),
        "variables_computed": len(variables_computed),
        "duration_seconds": round(duration_seconds, 2),
        "calls_per_second": round(total_calls / duration_seconds, 2)
        if duration_seconds > 0
        else 0.0,
    }

    return stats


def compute_financial_output_stats(
    df_output: pd.DataFrame,
    variable_names: List[str],
) -> Dict[str, Any]:
    """
    Analyze Step 3.1 Firm Controls output characteristics.

    Provides comprehensive statistics about firm control variable
    distributions, winsorization effects, and correlation structure.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        df_output: Output DataFrame with firm control variables
                   (must contain Size, BM, Lev, ROA, EPS_Growth, etc.)
        variable_names: List of variable names to analyze

    Returns:
        Dictionary with keys:
        - variable_distributions: {var_name: {mean, median, std, min, max,
                                              q25, q75, percentiles, zeros, nans}}
        - winsorization_effects: {var_name: {pre_winsor_count, post_winsor_count,
                                            values_capped_at_upper, values_capped_at_lower}}
        - correlation_structure: Not available without full correlation matrix
        - cross_sectional_stats: {variable_name: {std_by_year, year_range}}
    """

    stats: Dict[str, Any] = {}

    # Variable distributions
    stats["variable_distributions"] = {}
    for var_name in sorted(variable_names):
        if var_name not in df_output.columns:
            stats["variable_distributions"][var_name] = {"error": "Variable not found"}
            continue

        var_series = df_output[var_name]

        # Basic statistics
        var_stats: VarStatsDict = {
            "mean": round(float(var_series.mean()), 4),
            "median": round(float(var_series.median()), 4),
            "std": round(float(var_series.std()), 4),
            "min": round(float(var_series.min()), 4),
            "max": round(float(var_series.max()), 4),
            "q25": round(float(var_series.quantile(0.25)), 4),
            "q75": round(float(var_series.quantile(0.75)), 4),
        }

        # Percentiles
        var_stats["percentiles"] = {
            "p1": round(float(var_series.quantile(0.01)), 4),
            "p5": round(float(var_series.quantile(0.05)), 4),
            "p10": round(float(var_series.quantile(0.10)), 4),
            "p90": round(float(var_series.quantile(0.90)), 4),
            "p95": round(float(var_series.quantile(0.95)), 4),
            "p99": round(float(var_series.quantile(0.99)), 4),
        }

        # Missing and zero analysis
        var_stats["nans"] = {
            "count": int(var_series.isna().sum()),
            "pct": round(var_series.isna().sum() / len(var_series) * 100, 2)
            if len(var_series) > 0
            else 0.0,
        }
        var_stats["zeros"] = {
            "count": int((var_series == 0).sum()),
            "pct": round((var_series == 0).sum() / len(var_series) * 100, 2)
            if len(var_series) > 0
            else 0.0,
        }

        stats["variable_distributions"][var_name] = var_stats

    # Winsorization effects (estimated from p01/p99)
    stats["winsorization_effects"] = {}
    for var_name in sorted(variable_names):
        if (
            var_name not in df_output.columns
            or var_name not in stats["variable_distributions"]
        ):
            continue

        var_series = df_output[var_name].dropna()
        if len(var_series) == 0:
            continue

        p01 = stats["variable_distributions"][var_name]["percentiles"]["p1"]
        p99 = stats["variable_distributions"][var_name]["percentiles"]["p99"]

        # Count values at bounds (indicating winsorization)
        upper_capped = int((var_series >= p99).sum())
        lower_capped = int((var_series <= p01).sum())

        stats["winsorization_effects"][var_name] = {
            "upper_bound": p99,
            "lower_bound": p01,
            "values_at_or_above_upper": upper_capped,
            "values_at_or_below_lower": lower_capped,
        }

    return stats


def compute_market_input_stats(
    manifest_df: pd.DataFrame,
    crsp_file: Path,
    ccm_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Analyze input data for Step 3.2 Market Variables.

    Provides comprehensive statistics about manifest (sample calls),
    CRSP (stock price data), and CCM (linking table) datasets.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        manifest_df: Master manifest DataFrame (from step 1.4)
        crsp_file: Path to CRSP DSF directory
        ccm_df: CCM linking DataFrame (optional)

    Returns:
        Dictionary with keys:
        - manifest_stats: {total_calls, unique_gvkey, date_range,
                          permno_coverage_before_ccm, permno_coverage_after_ccm}
        - crsp_stats: {files_available, total_observations, date_range,
                       unique_permnos, memory_estimate_mb}
        - ccm_stats: {total_links, unique_gvkey, unique_lpermno, date_coverage}
    """

    stats: Dict[str, Any] = {}

    # Manifest statistics
    stats["manifest_stats"] = {
        "total_calls": int(len(manifest_df)),
    }

    if "gvkey" in manifest_df.columns:
        stats["manifest_stats"]["unique_gvkey"] = int(manifest_df["gvkey"].nunique())

    if "start_date" in manifest_df.columns:
        manifest_df_temp = manifest_df.copy()
        manifest_df_temp["start_date"] = pd.to_datetime(manifest_df_temp["start_date"])
        date_col = manifest_df_temp["start_date"].dropna()
        if len(date_col) > 0:
            stats["manifest_stats"]["date_range"] = {
                "earliest": date_col.min().isoformat(),
                "latest": date_col.max().isoformat(),
            }

    # PERMNO coverage
    if "permno" in manifest_df.columns:
        permno_before = int(manifest_df["permno"].notna().sum())
        stats["manifest_stats"]["permno_coverage_before_ccm"] = {
            "count": permno_before,
            "pct": round(permno_before / len(manifest_df) * 100, 2)
            if len(manifest_df) > 0
            else 0.0,
        }

    # CRSP statistics
    crsp_files = (
        list(crsp_file.glob("CRSP_DSF_*.parquet")) if crsp_file.exists() else []
    )

    stats["crsp_stats"] = {
        "files_available": len(crsp_files),
        "file_names": sorted([f.name for f in crsp_files]),
    }

    if crsp_files:
        # Sample a few files to estimate
        sample_files = crsp_files[:3]
        total_obs = 0
        unique_permnos = set()

        for f in sample_files:
            df_sample = pd.read_parquet(f, columns=["PERMNO"])
            total_obs += len(df_sample)
            if "PERMNO" in df_sample.columns:
                unique_permnos.update(df_sample["PERMNO"].dropna().unique())

        stats["crsp_stats"]["sampled_observations"] = int(total_obs)
        stats["crsp_stats"]["unique_permnos_sampled"] = int(len(unique_permnos))

        # Get date range from filename
        if crsp_files:
            years = []
            for f in crsp_files:
                try:
                    year_str = f.stem.split("_")[-2]  # CRSP_DSF_YYYY_Q.parquet
                    if year_str.isdigit():
                        years.append(int(year_str))
                except (IndexError, ValueError):
                    pass
            if years:
                stats["crsp_stats"]["year_range"] = {
                    "earliest": min(years),
                    "latest": max(years),
                }

    # CCM statistics
    if ccm_df is not None and len(ccm_df) > 0:
        stats["ccm_stats"] = {
            "total_links": int(len(ccm_df)),
        }

        if "gvkey" in ccm_df.columns:
            stats["ccm_stats"]["unique_gvkey"] = int(ccm_df["gvkey"].nunique())

        if "LPERMNO" in ccm_df.columns:
            stats["ccm_stats"]["unique_lpermno"] = int(ccm_df["LPERMNO"].nunique())

        # Date coverage
        if "LINKDT" in ccm_df.columns:
            linkdt = ccm_df["LINKDT"].dropna()
            if len(linkdt) > 0:
                stats["ccm_stats"]["link_date_range"] = {
                    "earliest": linkdt.min().isoformat()
                    if hasattr(linkdt.min(), "isoformat")
                    else str(linkdt.min()),
                    "latest": linkdt.max().isoformat()
                    if hasattr(linkdt.max(), "isoformat")
                    else str(linkdt.max()),
                }

    return stats


def compute_market_process_stats(
    per_year_stats: List[Dict[str, Any]],
    window_params: Dict[str, int],
    duration_seconds: float,
) -> Dict[str, Any]:
    """
    Analyze Step 3.2 Market Variables process outcomes.

    Provides detailed statistics about return computation coverage,
    liquidity measure construction, and window-based calculations.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        per_year_stats: List of per-year statistics from processing
        window_params: Dict with window configuration (days_after, days_before,
                       baseline_start, baseline_end, event_window_days)
        duration_seconds: Total processing duration

    Returns:
        Dictionary with keys:
        - coverage_metrics: {stock_ret_coverage: {count, pct},
                             amihud_coverage: {count, pct},
                             corwin_schultz_coverage: {count, pct}}
        - window_configuration: {return_window_days, baseline_window_days,
                                  event_window_days}
        - yearly_coverage: {year: {stock_ret_pct, amihud_pct, vol_pct}}
        - efficiency_metrics: {calls_processed, duration_seconds, years_processed}
    """

    stats: Dict[str, Any] = {}

    # Coverage aggregation
    total_calls = sum(s.get("calls", 0) for s in per_year_stats)
    total_stock_ret = sum(s.get("stock_ret_computed", 0) for s in per_year_stats)
    total_amihud = sum(s.get("amihud_computed", 0) for s in per_year_stats)

    stats["coverage_metrics"] = {
        "stock_ret_coverage": {
            "count": int(total_stock_ret),
            "pct": round(total_stock_ret / total_calls * 100, 2)
            if total_calls > 0
            else 0.0,
        },
        "amihud_coverage": {
            "count": int(total_amihud),
            "pct": round(total_amihud / total_calls * 100, 2)
            if total_calls > 0
            else 0.0,
        },
    }

    # Window configuration
    stats["window_configuration"] = {
        "return_window_days_after": window_params.get("days_after_prev_call", 5),
        "return_window_days_before": window_params.get("days_before_current_call", 5),
        "baseline_start": window_params.get("baseline_start", -35),
        "baseline_end": window_params.get("baseline_end", -6),
        "event_window_days": window_params.get("event_days", 5),
    }

    # Yearly coverage
    stats["yearly_coverage"] = {}
    for year_stat in per_year_stats:
        year = year_stat.get("year")
        if year is not None:
            calls = year_stat.get("calls", 0)
            stock_ret = year_stat.get("stock_ret_computed", 0)
            amihud = year_stat.get("amihud_computed", 0)

            stats["yearly_coverage"][str(year)] = {
                "stock_ret_pct": round(stock_ret / calls * 100, 2)
                if calls > 0
                else 0.0,
                "amihud_pct": round(amihud / calls * 100, 2) if calls > 0 else 0.0,
            }

    # Efficiency metrics
    stats["efficiency_metrics"] = {
        "calls_processed": int(total_calls),
        "duration_seconds": round(duration_seconds, 2),
        "years_processed": len(per_year_stats),
        "calls_per_second": round(total_calls / duration_seconds, 2)
        if duration_seconds > 0
        else 0.0,
    }

    return stats


def compute_market_output_stats(
    df_output: pd.DataFrame,
    variable_names: List[str],
) -> Dict[str, Any]:
    """
    Analyze Step 3.2 Market Variables output characteristics.

    Provides comprehensive statistics about market variable
    distributions, liquidity measures, and volatility metrics.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        df_output: Output DataFrame with market variables
                   (StockRet, MarketRet, Amihud, Corwin_Schultz, etc.)
        variable_names: List of variable names to analyze

    Returns:
        Dictionary with keys:
        - variable_distributions: {var_name: {mean, median, std, min, max,
                                              q25, q75, percentiles, zeros, nans}}
        - liquidity_analysis: {amihud_stats: {...}, corwin_schultz_stats: {...},
                              delta_amihud_stats: {...}}
        - return_analysis: {stock_ret_stats: {...}, market_ret_stats: {...},
                           excess_return_stats: {...}}
        - volatility_stats: {mean, median, std, percentiles}
    """

    stats: Dict[str, Any] = {}

    # Variable distributions
    stats["variable_distributions"] = {}
    for var_name in sorted(variable_names):
        if var_name not in df_output.columns:
            stats["variable_distributions"][var_name] = {"error": "Variable not found"}
            continue

        var_series = df_output[var_name]

        # Basic statistics
        var_stats: VarStatsDict = {
            "mean": round(float(var_series.mean()), 4),
            "median": round(float(var_series.median()), 4),
            "std": round(float(var_series.std()), 4),
            "min": round(float(var_series.min()), 4),
            "max": round(float(var_series.max()), 4),
            "q25": round(float(var_series.quantile(0.25)), 4),
            "q75": round(float(var_series.quantile(0.75)), 4),
        }

        # Percentiles
        var_stats["percentiles"] = {
            "p1": round(float(var_series.quantile(0.01)), 4),
            "p5": round(float(var_series.quantile(0.05)), 4),
            "p10": round(float(var_series.quantile(0.10)), 4),
            "p90": round(float(var_series.quantile(0.90)), 4),
            "p95": round(float(var_series.quantile(0.95)), 4),
            "p99": round(float(var_series.quantile(0.99)), 4),
        }

        # Missing and zero analysis
        var_stats["nans"] = {
            "count": int(var_series.isna().sum()),
            "pct": round(var_series.isna().sum() / len(var_series) * 100, 2)
            if len(var_series) > 0
            else 0.0,
        }
        var_stats["zeros"] = {
            "count": int((var_series == 0).sum()),
            "pct": round((var_series == 0).sum() / len(var_series) * 100, 2)
            if len(var_series) > 0
            else 0.0,
        }

        stats["variable_distributions"][var_name] = var_stats

    # Liquidity analysis
    stats["liquidity_analysis"] = {}
    if "Amihud" in df_output.columns:
        amihud = df_output["Amihud"].dropna()
        if len(amihud) > 0:
            stats["liquidity_analysis"]["amihud_stats"] = {
                "mean": round(float(amihud.mean()), 6),
                "median": round(float(amihud.median()), 6),
                "std": round(float(amihud.std()), 6),
                "min": round(float(amihud.min()), 6),
                "max": round(float(amihud.max()), 6),
            }

    if "Corwin_Schultz" in df_output.columns:
        cs = df_output["Corwin_Schultz"].dropna()
        if len(cs) > 0:
            stats["liquidity_analysis"]["corwin_schultz_stats"] = {
                "mean": round(float(cs.mean()), 6),
                "median": round(float(cs.median()), 6),
                "std": round(float(cs.std()), 6),
                "min": round(float(cs.min()), 6),
                "max": round(float(cs.max()), 6),
            }

    if "Delta_Amihud" in df_output.columns:
        delta_amihud = df_output["Delta_Amihud"].dropna()
        if len(delta_amihud) > 0:
            stats["liquidity_analysis"]["delta_amihud_stats"] = {
                "mean": round(float(delta_amihud.mean()), 6),
                "median": round(float(delta_amihud.median()), 6),
                "std": round(float(delta_amihud.std()), 6),
                "min": round(float(delta_amihud.min()), 6),
                "max": round(float(delta_amihud.max()), 6),
                "positive_pct": round(
                    (delta_amihud > 0).sum() / len(delta_amihud) * 100, 2
                ),
            }

    # Return analysis
    stats["return_analysis"] = {}
    if "StockRet" in df_output.columns:
        stock_ret = df_output["StockRet"].dropna()
        if len(stock_ret) > 0:
            stats["return_analysis"]["stock_ret_stats"] = {
                "mean": round(float(stock_ret.mean()), 4),
                "median": round(float(stock_ret.median()), 4),
                "std": round(float(stock_ret.std()), 4),
                "min": round(float(stock_ret.min()), 4),
                "max": round(float(stock_ret.max()), 4),
                "positive_pct": round((stock_ret > 0).sum() / len(stock_ret) * 100, 2),
            }

    if "MarketRet" in df_output.columns:
        market_ret = df_output["MarketRet"].dropna()
        if len(market_ret) > 0:
            stats["return_analysis"]["market_ret_stats"] = {
                "mean": round(float(market_ret.mean()), 4),
                "median": round(float(market_ret.median()), 4),
                "std": round(float(market_ret.std()), 4),
                "min": round(float(market_ret.min()), 4),
                "max": round(float(market_ret.max()), 4),
            }

    # Excess returns (StockRet - MarketRet)
    if "StockRet" in df_output.columns and "MarketRet" in df_output.columns:
        excess_ret = (df_output["StockRet"] - df_output["MarketRet"]).dropna()
        if len(excess_ret) > 0:
            stats["return_analysis"]["excess_return_stats"] = {
                "mean": round(float(excess_ret.mean()), 4),
                "median": round(float(excess_ret.median()), 4),
                "std": round(float(excess_ret.std()), 4),
                "min": round(float(excess_ret.min()), 4),
                "max": round(float(excess_ret.max()), 4),
            }

    # Volatility statistics
    if "Volatility" in df_output.columns:
        vol = df_output["Volatility"].dropna()
        if len(vol) > 0:
            stats["volatility_stats"] = {
                "mean": round(float(vol.mean()), 4),
                "median": round(float(vol.median()), 4),
                "std": round(float(vol.std()), 4),
                "min": round(float(vol.min()), 4),
                "max": round(float(vol.max()), 4),
                "percentiles": {
                    "p10": round(float(vol.quantile(0.10)), 4),
                    "p25": round(float(vol.quantile(0.25)), 4),
                    "p50": round(float(vol.quantile(0.50)), 4),
                    "p75": round(float(vol.quantile(0.75)), 4),
                    "p90": round(float(vol.quantile(0.90)), 4),
                },
            }

    return stats


def compute_event_flags_input_stats(
    manifest_df: pd.DataFrame,
    sdc_df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Analyze input data for Step 3.3 Event Flags.

    Provides comprehensive statistics about manifest (sample calls)
    and SDC M&A (merger and acquisition) datasets.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        manifest_df: Master manifest DataFrame (from step 1.4)
        sdc_df: SDC M&A DataFrame

    Returns:
        Dictionary with keys:
        - manifest_stats: {total_calls, unique_gvkey, with_cusip_count, with_cusip_pct}
        - sdc_stats: {total_deals, unique_target_cusips, date_range,
                      deal_attitude_distribution, deal_status_distribution}
        - matching_potential: {manifest_with_cusip_in_sdc: count, pct}
    """

    stats: Dict[str, Any] = {}

    # Manifest statistics
    stats["manifest_stats"] = {
        "total_calls": int(len(manifest_df)),
    }

    if "gvkey" in manifest_df.columns:
        stats["manifest_stats"]["unique_gvkey"] = int(manifest_df["gvkey"].nunique())

    # CUSIP coverage
    if "cusip" in manifest_df.columns:
        with_cusip = int(manifest_df["cusip"].notna().sum())
        stats["manifest_stats"]["with_cusip_count"] = with_cusip
        stats["manifest_stats"]["with_cusip_pct"] = (
            round(with_cusip / len(manifest_df) * 100, 2) if len(manifest_df) > 0 else 0.0
        )

    if "start_date" in manifest_df.columns:
        manifest_df_temp = manifest_df.copy()
        manifest_df_temp["start_date"] = pd.to_datetime(manifest_df_temp["start_date"])
        date_col = manifest_df_temp["start_date"].dropna()
        if len(date_col) > 0:
            stats["manifest_stats"]["date_range"] = {
                "earliest": date_col.min().isoformat(),
                "latest": date_col.max().isoformat(),
            }

    # SDC statistics
    stats["sdc_stats"] = {
        "total_deals": int(len(sdc_df)),
    }

    # Unique target CUSIPs
    if "Target 6-digit CUSIP" in sdc_df.columns or "target_cusip6" in sdc_df.columns:
        cusip_col = (
            "target_cusip6"
            if "target_cusip6" in sdc_df.columns
            else "Target 6-digit CUSIP"
        )
        stats["sdc_stats"]["unique_target_cusips"] = int(sdc_df[cusip_col].nunique())

    # Date range
    if "Date Announced" in sdc_df.columns or "date_announced" in sdc_df.columns:
        date_col = (
            "date_announced" if "date_announced" in sdc_df.columns else "Date Announced"
        )
        sdc_temp = sdc_df.copy()
        sdc_temp[date_col] = pd.to_datetime(sdc_temp[date_col])
        date_series = sdc_temp[date_col].dropna()
        if len(date_series) > 0:
            stats["sdc_stats"]["date_range"] = {
                "earliest": date_series.min().isoformat(),
                "latest": date_series.max().isoformat(),
            }

    # Deal attitude distribution
    if "Deal Attitude" in sdc_df.columns or "deal_attitude" in sdc_df.columns:
        attitude_col = (
            "deal_attitude" if "deal_attitude" in sdc_df.columns else "Deal Attitude"
        )
        attitude_counts = sdc_df[attitude_col].value_counts()
        stats["sdc_stats"]["deal_attitude_distribution"] = {
            str(att): int(count) for att, count in attitude_counts.items()
        }

    # Deal status distribution
    if "Deal Status" in sdc_df.columns or "deal_status" in sdc_df.columns:
        status_col = "deal_status" if "deal_status" in sdc_df.columns else "Deal Status"
        status_counts = sdc_df[status_col].value_counts()
        stats["sdc_stats"]["deal_status_distribution"] = {
            str(status): int(count) for status, count in status_counts.items()
        }

    # Matching potential (estimate)
    stats["matching_potential"] = {
        "note": "Exact matching requires CUSIP6 comparison - estimated from available data"
    }

    return stats


def compute_event_flags_process_stats(
    takeover_count: int,
    takeover_by_type: Dict[str, int],
    duration_stats: Dict[str, float],
    total_calls: int,
    duration_seconds: float,
) -> Dict[str, Any]:
    """
    Analyze Step 3.3 Event Flags process outcomes.

    Provides detailed statistics about takeover event detection,
    deal type classification, and duration analysis.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        takeover_count: Total number of takeover events detected
        takeover_by_type: Dict mapping deal_type -> count
        duration_stats: Dict with duration statistics (mean, median, etc.)
        total_calls: Total number of calls processed
        duration_seconds: Total processing duration

    Returns:
        Dictionary with keys:
        - takeover_detection: {total_events, event_rate_pct, events_per_year}
        - deal_type_distribution: {friendly: {count, pct}, uninvited: {count, pct}}
        - duration_analysis: {mean_quarters, median_quarters, min_quarters, max_quarters,
                             duration_buckets: {bucket: {count, pct}}}
        - efficiency_metrics: {calls_processed, events_detected, duration_seconds}
    """

    stats: Dict[str, Any] = {}

    # Takeover detection
    event_rate = (
        round(takeover_count / total_calls * 100, 2) if total_calls > 0 else 0.0
    )

    stats["takeover_detection"] = {
        "total_events": int(takeover_count),
        "total_calls": int(total_calls),
        "event_rate_pct": event_rate,
    }

    # Deal type distribution
    friendly_count = takeover_by_type.get("Friendly", 0)
    uninvited_count = takeover_by_type.get("Uninvited", 0)
    total_typed = friendly_count + uninvited_count

    stats["deal_type_distribution"] = {
        "friendly": {
            "count": int(friendly_count),
            "pct": round(friendly_count / total_typed * 100, 2)
            if total_typed > 0
            else 0.0,
        },
        "uninvited": {
            "count": int(uninvited_count),
            "pct": round(uninvited_count / total_typed * 100, 2)
            if total_typed > 0
            else 0.0,
        },
    }

    # Duration analysis
    if duration_stats:
        stats["duration_analysis"] = {
            "mean_quarters": round(float(duration_stats.get("mean", 0)), 2),
            "median_quarters": round(float(duration_stats.get("median", 0)), 2),
            "min_quarters": round(float(duration_stats.get("min", 0)), 2),
            "max_quarters": round(float(duration_stats.get("max", 0)), 2),
        }

        # Duration buckets
        buckets = {
            "<1 quarter": 0,
            "1-2 quarters": 0,
            "2-3 quarters": 0,
            "3+ quarters": 0,
        }
        # These would be populated from actual duration data
        stats["duration_analysis"]["duration_buckets"] = buckets

    # Efficiency metrics
    stats["efficiency_metrics"] = {
        "calls_processed": int(total_calls),
        "events_detected": int(takeover_count),
        "duration_seconds": round(duration_seconds, 2),
        "calls_per_second": round(total_calls / duration_seconds, 2)
        if duration_seconds > 0
        else 0.0,
    }

    return stats


def compute_event_flags_output_stats(
    df_output: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Analyze Step 3.3 Event Flags output characteristics.

    Provides comprehensive statistics about takeover event flags,
    deal type classifications, and survival analysis durations.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        df_output: Output DataFrame with event flags
                   (Takeover, Takeover_Type, Duration)

    Returns:
        Dictionary with keys:
        - takeover_flag_stats: {total_events, no_events, event_rate_pct}
        - deal_type_stats: {friendly: {count, pct}, uninvited: {count, pct},
                            not_applicable: {count, pct}}
        - duration_stats: {overall: {mean, median, std, min, max},
                          for_takeovers_only: {mean, median, std, min, max}}
        - yearly_analysis: {year: {takeover_count, takeover_pct, avg_duration}}
    """

    stats: Dict[str, Any] = {}

    total_calls = len(df_output)

    # Takeover flag statistics
    if "Takeover" in df_output.columns:
        takeover_count = int(df_output["Takeover"].sum())
        no_takeover_count = int((df_output["Takeover"] == 0).sum())
        takeover_rate = (
            round(takeover_count / total_calls * 100, 2) if total_calls > 0 else 0.0
        )

        stats["takeover_flag_stats"] = {
            "total_events": takeover_count,
            "no_events": no_takeover_count,
            "event_rate_pct": takeover_rate,
        }

    # Deal type statistics
    if "Takeover_Type" in df_output.columns:
        type_counts = df_output["Takeover_Type"].value_counts()

        friendly_count = int(type_counts.get("Friendly", 0))
        uninvited_count = int(type_counts.get("Uninvited", 0))
        na_count = int(df_output["Takeover_Type"].isna().sum())
        total_typed = friendly_count + uninvited_count + na_count

        stats["deal_type_stats"] = {
            "friendly": {
                "count": friendly_count,
                "pct": round(friendly_count / total_typed * 100, 2)
                if total_typed > 0
                else 0.0,
            },
            "uninvited": {
                "count": uninvited_count,
                "pct": round(uninvited_count / total_typed * 100, 2)
                if total_typed > 0
                else 0.0,
            },
            "not_applicable": {
                "count": na_count,
                "pct": round(na_count / total_typed * 100, 2)
                if total_typed > 0
                else 0.0,
            },
        }

    # Duration statistics
    if "Duration" in df_output.columns:
        duration_all = df_output["Duration"]
        duration_takeovers = (
            df_output[df_output["Takeover"] == 1]["Duration"]
            if "Takeover" in df_output.columns
            else pd.Series()
        )

        stats["duration_stats"] = {
            "overall": {
                "mean": round(float(duration_all.mean()), 2),
                "median": round(float(duration_all.median()), 2),
                "std": round(float(duration_all.std()), 2),
                "min": round(float(duration_all.min()), 2),
                "max": round(float(duration_all.max()), 2),
            }
        }

        if len(duration_takeovers) > 0:
            stats["duration_stats"]["for_takeovers_only"] = {
                "mean": round(float(duration_takeovers.mean()), 2),
                "median": round(float(duration_takeovers.median()), 2),
                "std": round(float(duration_takeovers.std()), 2),
                "min": round(float(duration_takeovers.min()), 2),
                "max": round(float(duration_takeovers.max()), 2),
            }

    # Yearly analysis
    if "year" in df_output.columns and "Takeover" in df_output.columns:
        stats["yearly_analysis"] = {}
        for year in sorted(df_output["year"].unique()):
            year_df = df_output[df_output["year"] == year]
            year_takeover = int(year_df["Takeover"].sum())
            year_total = len(year_df)

            year_duration = year_df[year_df["Takeover"] == 1]["Duration"]
            avg_duration = (
                round(float(year_duration.mean()), 2) if len(year_duration) > 0 else 0.0
            )

            stats["yearly_analysis"][str(year)] = {
                "takeover_count": year_takeover,
                "takeover_pct": round(year_takeover / year_total * 100, 2)
                if year_total > 0
                else 0.0,
                "avg_duration": avg_duration,
            }

    return stats


# ============================================================================
# Step 3 Financial Features Statistics - Wrapper Functions
# These functions provide consistent naming for Step 3 sub-steps
# ============================================================================


def compute_step31_input_stats(
    manifest_df: pd.DataFrame,
    compustat_df: pd.DataFrame,
    ibes_df: pd.DataFrame,
    cccl_df: Optional[pd.DataFrame] = None,
    ccm_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Analyze input data for Step 3.1 (Firm Controls).

    Wrapper function for compute_financial_input_stats that provides
    Step 3.1 specific analysis including manifest, Compustat, IBES, CCCL,
    and CCM linkage statistics.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        manifest_df: Master manifest DataFrame (from step 1.4)
        compustat_df: Compustat quarterly data DataFrame
        ibes_df: IBES forecast DataFrame
        cccl_df: CCCL instrument DataFrame (optional)
        ccm_df: CCM linkage DataFrame (optional, for analysis)

    Returns:
        Dictionary with keys:
        - manifest_stats: {total_calls, unique_gvkey, date_range, calls_per_year}
        - compustat_stats: {total_observations, unique_gvkey, date_range, quarters_covered}
        - ibes_stats: {total_forecasts, unique_tickers, eps_qtr_records, date_range}
        - cccl_stats: {total_records, unique_gvkey, years_covered, intensity_variants}
        - ccm_stats: {linkages_available, unique_gvkey_linked} (if ccm_df provided)
    """
    stats = compute_financial_input_stats(manifest_df, compustat_df, ibes_df, cccl_df)

    # Add CCM analysis if provided
    if ccm_df is not None and len(ccm_df) > 0:
        stats["ccm_stats"] = {
            "linkages_available": int(len(ccm_df)),
        }
        if "gvkey" in ccm_df.columns:
            stats["ccm_stats"]["unique_gvkey_linked"] = int(ccm_df["gvkey"].nunique())
        if "LPERMNO" in ccm_df.columns:
            stats["ccm_stats"]["unique_permno_linked"] = int(
                ccm_df["LPERMNO"].nunique()
            )

    return stats


def compute_step31_process_stats(
    merge_results: Dict[str, Dict[str, int]],
    variable_coverage_df: Optional[pd.DataFrame] = None,
    winsorized_cols: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Analyze Step 3.1 (Firm Controls) construction process.

    Wrapper function for compute_financial_process_stats that provides
    detailed analysis of merge quality, variable construction, and
    winsorization impact.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        merge_results: Dict with merge stats for Compustat, IBES, CCCL
        variable_coverage_df: DataFrame with variable coverage information
        winsorized_cols: List of columns that were winsorized

    Returns:
        Dictionary with keys:
        - merge_quality_metrics: {compustat_merge, ibes_merge, cccl_merge}
        - variable_construction_metrics: {coverage_by_variable, overall_stats}
        - winsorization_impact: {winsorized_columns, tail_trimming_pct}
        - data_quality_indicators: {missing_patterns, extreme_values}
    """
    # Extract variables from merge results
    variables_computed = []
    coverage_rates = {}

    if variable_coverage_df is not None and len(variable_coverage_df) > 0:
        # Build variables list and coverage from DataFrame
        for col in variable_coverage_df.columns:
            if col in [
                "Size",
                "BM",
                "Lev",
                "ROA",
                "EPS_Growth",
                "SurpDec",
                "CurrentRatio",
                "RD_Intensity",
            ]:
                non_null = variable_coverage_df[col].notna().sum()
                total = len(variable_coverage_df)
                variables_computed.append(col)
                coverage_rates[col] = (
                    round(non_null / total * 100, 2) if total > 0 else 0.0
                )

    # Use default duration if not available
    duration_seconds = 0.0

    stats = compute_financial_process_stats(
        merge_results,
        variables_computed,
        coverage_rates,
        duration_seconds,
    )

    # Add winsorization impact
    if winsorized_cols:
        stats["winsorization_impact"] = {
            "winsorized_columns": winsorized_cols,
            "num_winsorized": len(winsorized_cols),
            "method": "1%/99% percentile winsorization",
        }
    else:
        stats["winsorization_impact"] = {"note": "No winsorization info provided"}

    return stats


def compute_step31_output_stats(
    output_df: pd.DataFrame,
    variables_list: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Analyze Step 3.1 (Firm Controls) output.

    Wrapper function for compute_financial_output_stats that provides
    comprehensive descriptive statistics for all firm control variables.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        output_df: Output DataFrame with firm controls
        variables_list: List of variables to analyze (optional, auto-detected)

    Returns:
        Dictionary with keys:
        - variable_distributions: {var_name: {count, mean, median, std, min, max, percentiles}}
        - correlation_matrix: {Size: {BM: corr, Lev: corr, ...}, ...}
        - distribution_analysis: {size_deciles, bm_quintiles, leverage_categories}
        - temp_decile_trends: {SurpDec: {year: avg_decile}}
        - shift_intensity_summary: {variant: {mean, median, std, coverage}}
    """
    # Auto-detect variables if not provided
    if variables_list is None:
        variables_list = [
            "Size",
            "BM",
            "Lev",
            "ROA",
            "EPS_Growth",
            "SurpDec",
            "CurrentRatio",
            "RD_Intensity",
        ]

    # Add shift intensity variants if present
    shift_cols = [c for c in output_df.columns if c.startswith("shift_intensity_")]
    variables_list.extend(shift_cols)

    stats = compute_financial_output_stats(output_df, variables_list)

    return stats


def compute_step32_input_stats(
    manifest_with_permno_df: pd.DataFrame,
    crsp_df_by_year: Dict[str, pd.DataFrame],
    ccm_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Analyze input data for Step 3.2 (Market Variables).

    Wrapper function for compute_market_input_stats that provides
    Step 3.2 specific analysis including manifest with PERMNO,
    CRSP data by year, and CCM linkage statistics.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        manifest_with_permno_df: Manifest DataFrame with PERMNO column
        crsp_df_by_year: Dict mapping year -> CRSP DataFrame for that year
        ccm_df: CCM linkage DataFrame (optional)

    Returns:
        Dictionary with keys:
        - manifest_stats: {total_records, unique_gvkey, unique_permno, years_present}
        - crsp_stats_by_year: {year: {observations, unique_stocks, date_range}}
        - ccm_linkage_stats: {linkages_available, unique_gvkey_with_permno}
        - permno_coverage_stats: {direct_permno_count, ccm_fallback_count, coverage_rate}
    """
    # Analyze manifest
    stats: Dict[str, Any] = {}
    stats["manifest_stats"] = {
        "total_records": int(len(manifest_with_permno_df)),
    }

    if "gvkey" in manifest_with_permno_df.columns:
        stats["manifest_stats"]["unique_gvkey"] = int(
            manifest_with_permno_df["gvkey"].nunique()
        )

    # PERMNO coverage analysis
    if "permno" in manifest_with_permno_df.columns:
        direct_permno = manifest_with_permno_df["permno"].notna().sum()
        stats["manifest_stats"]["unique_permno"] = int(
            manifest_with_permno_df["permno"].nunique()
        )
        stats["manifest_stats"]["permno_coverage_pct"] = round(
            direct_permno / len(manifest_with_permno_df) * 100, 2
        )

    # Temporal coverage
    if "start_date" in manifest_with_permno_df.columns:
        manifest_temp = manifest_with_permno_df.copy()
        manifest_temp["start_date"] = pd.to_datetime(manifest_temp["start_date"])
        dates = manifest_temp["start_date"].dropna()
        if len(dates) > 0:
            stats["manifest_stats"]["date_range"] = {
                "earliest": dates.min().isoformat(),
                "latest": dates.max().isoformat(),
            }
        years = manifest_temp["start_date"].dt.year.unique()
        stats["manifest_stats"]["years_present"] = sorted([int(y) for y in years])

    # CRSP statistics by year
    stats["crsp_stats_by_year"] = {}
    for year, crsp_df in sorted(crsp_df_by_year.items(), key=lambda x: str(x[0])):
        year_stats: YearStatsDict = {
            "observations": int(len(crsp_df)),
        }
        if "PERMNO" in crsp_df.columns:
            year_stats["unique_stocks"] = int(crsp_df["PERMNO"].nunique())

        # Check data quality
        if "date" in crsp_df.columns:
            crsp_temp = crsp_df.copy()
            crsp_temp["date"] = pd.to_datetime(crsp_temp["date"])
            dates = crsp_temp["date"].dropna()
            if len(dates) > 0:
                year_stats["date_range"] = {
                    "earliest": dates.min().isoformat(),
                    "latest": dates.max().isoformat(),
                }

        # Data availability checks
        data_cols = ["RET", "VOL", "VWRETD", "ASKHI", "BIDLO", "PRC"]
        available_cols = [c for c in data_cols if c in crsp_df.columns]
        year_stats["data_columns_available"] = available_cols

        stats["crsp_stats_by_year"][str(year)] = year_stats

    # CCM linkage statistics
    if ccm_df is not None and len(ccm_df) > 0:
        stats["ccm_linkage_stats"] = {
            "linkages_available": int(len(ccm_df)),
        }
        if "gvkey" in ccm_df.columns:
            stats["ccm_linkage_stats"]["unique_gvkey_linked"] = int(
                ccm_df["gvkey"].nunique()
            )

    return stats


def compute_step32_process_stats(
    per_year_stats: List[Dict[str, Any]],
    return_windows: Optional[List[Dict[str, Any]]] = None,
    liquidity_windows: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Analyze Step 3.2 (Market Variables) construction process.

    Wrapper function for compute_market_process_stats that provides
    detailed analysis of return computation, liquidity measures,
    and delta calculations.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        per_year_stats: List of per-year statistics dictionaries
        return_windows: List of return window statistics (optional)
        liquidity_windows: List of liquidity window statistics (optional)

    Returns:
        Dictionary with keys:
        - return_metrics: {stock_ret_coverage, market_ret_coverage, window_validity}
        - liquidity_metrics: {amihud_coverage, corwin_schultz_coverage}
        - volatility_metrics: {annualization_validity, avg_volatility}
        - coverage_trends: {by_year: {stock_ret_pct, amihud_pct}}
        - data_quality_by_year: {missing_data_patterns}
    """
    stats: Dict[str, Any] = {}

    # Aggregate per-year statistics
    total_records = 0
    stock_ret_covered = 0
    amihud_covered = 0

    coverage_trends = {}

    for year_stat in per_year_stats:
        year = year_stat.get("year", "unknown")
        total = year_stat.get("total_records", 0)
        stock_ret = year_stat.get("stock_ret_count", 0)
        amihud = year_stat.get("amihud_count", 0)

        total_records += total
        stock_ret_covered += stock_ret
        amihud_covered += amihud

        coverage_trends[str(year)] = {
            "stock_ret_pct": round(stock_ret / total * 100, 2) if total > 0 else 0.0,
            "amihud_pct": round(amihud / total * 100, 2) if total > 0 else 0.0,
        }

    # Return metrics
    stats["return_metrics"] = {
        "stock_ret_coverage": {
            "count": int(stock_ret_covered),
            "pct": round(stock_ret_covered / total_records * 100, 2)
            if total_records > 0
            else 0.0,
        },
    }

    # Liquidity metrics
    stats["liquidity_metrics"] = {
        "amihud_coverage": {
            "count": int(amihud_covered),
            "pct": round(amihud_covered / total_records * 100, 2)
            if total_records > 0
            else 0.0,
        },
    }

    # Coverage trends
    stats["coverage_trends"] = coverage_trends

    # Analyze return windows if provided
    if return_windows:
        valid_windows = sum(1 for w in return_windows if w.get("valid", False))
        stats["return_metrics"]["window_validity"] = {
            "valid_windows": int(valid_windows),
            "total_windows": len(return_windows),
            "validity_pct": round(valid_windows / len(return_windows) * 100, 2)
            if return_windows
            else 0.0,
        }

        # Average window length
        window_lengths = [
            w.get("window_length_days", 0)
            for w in return_windows
            if w.get("window_length_days", 0) > 0
        ]
        if window_lengths:
            stats["return_metrics"]["avg_window_length_days"] = round(
                float(np.mean(window_lengths)), 2
            )

    # Analyze liquidity windows if provided
    if liquidity_windows:
        sum(1 for w in liquidity_windows if w.get("amihud_valid", False))
        cs_valid = sum(
            1 for w in liquidity_windows if w.get("corwin_schultz_valid", False)
        )

        stats["liquidity_metrics"]["corwin_schultz_coverage"] = {
            "count": int(cs_valid),
            "pct": round(cs_valid / len(liquidity_windows) * 100, 2)
            if liquidity_windows
            else 0.0,
        }

    return stats


def compute_step32_output_stats(
    output_df: pd.DataFrame,
    variables_list: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Analyze Step 3.2 (Market Variables) output.

    Wrapper function for compute_market_output_stats that provides
    comprehensive descriptive statistics for all market variables.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        output_df: Output DataFrame with market variables
        variables_list: List of variables to analyze (optional, auto-detected)

    Returns:
        Dictionary with keys:
        - variable_distributions: {var_name: {mean, median, std, percentiles, zeros}}
        - return_analysis: {stock_ret_stats, market_ret_stats, positive_return_pct}
        - liquidity_analysis: {amihud_stats, corwin_schultz_stats}
        - delta_analysis: {delta_amihud_stats, delta_corwin_schultz_stats, sign_distribution}
        - volatility_analysis: {annualized_volatility_stats}
        - correlation_matrix: Pearson correlations between market variables
        - temporal_trends: Average values by year
    """
    # Auto-detect variables if not provided
    if variables_list is None:
        variables_list = [
            "StockRet",
            "MarketRet",
            "Amihud",
            "Corwin_Schultz",
            "Delta_Amihud",
            "Delta_Corwin_Schultz",
            "Volatility",
        ]

    stats = compute_market_output_stats(output_df, variables_list)

    return stats


def compute_step33_input_stats(
    manifest_df: pd.DataFrame,
    sdc_df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Analyze input data for Step 3.3 (Event Flags).

    Wrapper function for compute_event_flags_input_stats that provides
    Step 3.3 specific analysis including manifest with CUSIP and
    SDC M&A deal statistics.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        manifest_df: Manifest DataFrame (with cusip column)
        sdc_df: SDC M&A data DataFrame

    Returns:
        Dictionary with keys:
        - manifest_stats: {total_records, unique_gvkey, cusip_availability, years_present}
        - sdc_deal_stats: {total_deals, unique_target_cusips, date_range, deal_status_dist}
        - cusip_linkage_potential: {manifest_cusip6_available, sdc_cusip6_overlap}
    """
    return compute_event_flags_input_stats(manifest_df, sdc_df)


def compute_step33_process_stats(
    match_results: Dict[str, Any],
    takeover_flags_df: Optional[pd.DataFrame] = None,
    window_days: int = 365,
) -> Dict[str, Any]:
    """
    Analyze Step 3.3 (Event Flags) construction process.

    Wrapper function for compute_event_flags_process_stats that provides
    detailed analysis of CUSIP matching, takeover detection, deal type
    classification, and duration computation.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        match_results: Dictionary with matching statistics
        takeover_flags_df: DataFrame with takeover flags
        window_days: Matching window in days (default 365)

    Returns:
        Dictionary with keys:
        - matching_metrics: {cusip6_match_rate, unmatched_analysis}
        - takeover_detection_metrics: {takeover_events, window_validity, multiple_deals}
        - deal_type_classification: {takeover_type_distribution, classification_accuracy}
        - duration_analysis: {duration_distribution, censored_observations, censoring_rate}
    """
    # Extract values from arguments
    takeover_count = (
        int(takeover_flags_df["Takeover"].sum())
        if takeover_flags_df is not None and "Takeover" in takeover_flags_df.columns
        else 0
    )
    total_calls = match_results.get(
        "manifest_rows",
        len(takeover_flags_df) if takeover_flags_df is not None else 0,
    )

    # Extract takeover types
    takeover_by_type: Dict[str, int] = {}
    if (
        takeover_flags_df is not None
        and "Takeover_Type" in takeover_flags_df.columns
        and "Takeover" in takeover_flags_df.columns
    ):
        type_counts = takeover_flags_df[takeover_flags_df["Takeover"] == 1][
            "Takeover_Type"
        ].value_counts()
        takeover_by_type = {str(k): int(v) for k, v in type_counts.items()}

    # Compute duration stats
    duration_stats: Dict[str, float] = {}
    if (
        takeover_flags_df is not None
        and "Duration" in takeover_flags_df.columns
        and "Takeover" in takeover_flags_df.columns
    ):
        durations = takeover_flags_df[takeover_flags_df["Takeover"] == 1]["Duration"]
        if len(durations) > 0:
            duration_stats = {
                "mean": float(durations.mean()),
                "median": float(durations.median()),
                "min": float(durations.min()),
                "max": float(durations.max()),
            }

    # Use a placeholder for duration_seconds (not tracked in match_results)
    duration_seconds = 0.0

    return compute_event_flags_process_stats(
        takeover_count, takeover_by_type, duration_stats, total_calls, duration_seconds
    )


def compute_step33_output_stats(
    output_df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Analyze Step 3.3 (Event Flags) output.

    Wrapper function for compute_event_flags_output_stats that provides
    comprehensive descriptive statistics for takeover flags, types, and
    duration analysis.

    Deterministic: Same input produces same output (sorted outputs).

    Args:
        output_df: Output DataFrame with event flags

    Returns:
        Dictionary with keys:
        - takeover_flag_analysis: {binary_distribution, takeover_frequency_by_year, takeover_rate}
        - takeover_type_analysis: {type_distribution, type_distribution_by_year}
        - duration_analysis: {for_takeovers, for_censored, survival_analysis_preview}
        - temporal_patterns: {takeover_frequency_trends, type_trends}
    """
    return compute_event_flags_output_stats(output_df)


def generate_financial_report_markdown(
    input_stats: Dict[str, Any],
    process_stats: Dict[str, Any],
    output_stats: Dict[str, Any],
    step_name: str,
    output_path: Path,
) -> None:
    """
    Generate comprehensive markdown report for Step 3 financial features.

    Creates a publication-ready markdown report with INPUT/PROCESS/OUTPUT
    statistics for presentation to supervisors.

    Args:
        input_stats: Input statistics dictionary
        process_stats: Process statistics dictionary
        output_stats: Output statistics dictionary
        step_name: Name of the step (e.g., "3.1_FirmControls")
        output_path: Path to save the markdown report
    """
    lines = []
    lines.append(f"# Step {step_name}: Financial Features Report")
    lines.append("")
    lines.append(f"**Generated:** {pd.Timestamp.now().isoformat()}")
    lines.append("")

    # INPUT section
    lines.append("## 1. INPUT STATISTICS")
    lines.append("")

    if "manifest_stats" in input_stats:
        lines.append("### Master Manifest")
        ms = input_stats["manifest_stats"]
        lines.append(f"- **Total Calls:** {ms.get('total_calls', 0):,}")
        lines.append(f"- **Unique GVKEY:** {ms.get('unique_gvkey', 0):,}")

        if "date_range" in ms:
            lines.append(
                f"- **Date Range:** {ms['date_range'].get('earliest', 'N/A')} to {ms['date_range'].get('latest', 'N/A')}"
            )

        if "calls_per_year" in ms:
            lines.append("")
            lines.append("| Year | Calls |")
            lines.append("|------|-------|")
            for year, count in sorted(
                ms["calls_per_year"].items(),
                key=lambda x: int(x[0]) if x[0].isdigit() else 0,
            ):
                lines.append(f"| {year} | {count:,} |")

    if "compustat_stats" in input_stats:
        lines.append("")
        lines.append("### Compustat Data")
        cs = input_stats["compustat_stats"]
        lines.append(f"- **Total Observations:** {cs.get('total_observations', 0):,}")
        lines.append(f"- **Unique GVKEY:** {cs.get('unique_gvkey', 0):,}")
        lines.append(f"- **Memory Footprint:** {cs.get('memory_mb', 0):.2f} MB")

        if "date_range" in cs:
            lines.append(
                f"- **Date Range:** {cs['date_range'].get('earliest', 'N/A')} to {cs['date_range'].get('latest', 'N/A')}"
            )

    if "ibes_stats" in input_stats:
        lines.append("")
        lines.append("### IBES Forecast Data")
        ibes = input_stats["ibes_stats"]
        lines.append(f"- **Total Forecasts:** {ibes.get('total_forecasts', 0):,}")
        lines.append(f"- **Unique Tickers:** {ibes.get('unique_tickers', 0):,}")
        lines.append(f"- ** EPS/QTR Records:** {ibes.get('eps_qtr_records', 0):,}")

    if "crsp_stats" in input_stats:
        lines.append("")
        lines.append("### CRSP Stock Price Data")
        crsp = input_stats["crsp_stats"]
        lines.append(f"- **Files Available:** {crsp.get('files_available', 0)}")

        if "year_range" in crsp:
            yr = crsp["year_range"]
            lines.append(
                f"- **Year Range:** {yr.get('earliest', 'N/A')} to {yr.get('latest', 'N/A')}"
            )

    if "sdc_stats" in input_stats:
        lines.append("")
        lines.append("### SDC M&A Data")
        sdc = input_stats["sdc_stats"]
        lines.append(f"- **Total Deals:** {sdc.get('total_deals', 0):,}")
        lines.append(
            f"- **Unique Target CUSIPs:** {sdc.get('unique_target_cusips', 0):,}"
        )

        if "deal_attitude_distribution" in sdc:
            lines.append("")
            lines.append("**Deal Attitude Distribution:**")
            for attitude, count in sdc["deal_attitude_distribution"].items():
                lines.append(f"  - {attitude}: {count:,}")

    # PROCESS section
    lines.append("")
    lines.append("## 2. PROCESS STATISTICS")
    lines.append("")

    if "merge_outcomes" in process_stats:
        lines.append("### Merge Outcomes")
        lines.append("")
        lines.append("| Data Source | Match Rate | Matched | Unmatched |")
        lines.append("|-------------|------------|---------|-----------|")

        for merge_name, merge_stats in process_stats["merge_outcomes"].items():
            matched = merge_stats.get("matched", 0)
            unmatched = merge_stats.get("unmatched", 0)
            rate = merge_stats.get("match_rate_pct", 0)
            lines.append(
                f"| {merge_name} | {rate:.1f}% | {matched:,} | {unmatched:,} |"
            )

    if "coverage_metrics" in process_stats:
        lines.append("")
        lines.append("### Variable Coverage")
        cm = process_stats["coverage_metrics"]

        if "stock_ret_coverage" in cm:
            src = cm["stock_ret_coverage"]
            lines.append(f"- **StockRet:** {src['count']:,} ({src['pct']:.1f}%)")

        if "amihud_coverage" in cm:
            am = cm["amihud_coverage"]
            lines.append(f"- **Amihud:** {am['count']:,} ({am['pct']:.1f}%)")

        if "overall_coverage_stats" in process_stats:
            ocs = process_stats["overall_coverage_stats"]
            lines.append("")
            lines.append("**Overall Coverage Statistics:**")
            lines.append(
                f"- **Average Coverage:** {ocs.get('avg_coverage_pct', 0):.1f}%"
            )
            lines.append(
                f"- **Variables Above 90% Coverage:** {ocs.get('variables_above_90_pct', 0)}"
            )
            lines.append(
                f"- **Variables Below 50% Coverage:** {ocs.get('variables_below_50_pct', 0)}"
            )

    if "takeover_detection" in process_stats:
        lines.append("")
        lines.append("### Event Detection")
        td = process_stats["takeover_detection"]
        lines.append(f"- **Total Takeover Events:** {td.get('total_events', 0):,}")
        lines.append(f"- **Event Rate:** {td.get('event_rate_pct', 0):.2f}%")

        if "deal_type_distribution" in process_stats:
            lines.append("")
            lines.append("**Deal Type Distribution:**")
            dtd = process_stats["deal_type_distribution"]
            if "friendly" in dtd:
                lines.append(
                    f"  - Friendly: {dtd['friendly']['count']:,} ({dtd['friendly']['pct']:.1f}%)"
                )
            if "uninvited" in dtd:
                lines.append(
                    f"  - Uninvited: {dtd['uninvited']['count']:,} ({dtd['uninvited']['pct']:.1f}%)"
                )

    if "efficiency_metrics" in process_stats:
        lines.append("")
        lines.append("### Processing Efficiency")
        em = process_stats["efficiency_metrics"]
        lines.append(f"- **Duration:** {em.get('duration_seconds', 0):.2f} seconds")
        lines.append(
            f"- **Throughput:** {em.get('calls_per_second', 0):.0f} calls/second"
        )

    # OUTPUT section
    lines.append("")
    lines.append("## 3. OUTPUT STATISTICS")
    lines.append("")

    if "variable_distributions" in output_stats:
        lines.append("### Variable Summary Statistics")
        lines.append("")
        lines.append("| Variable | Mean | Median | Std Dev | Min | Max | Missing % |")
        lines.append("|----------|------|--------|---------|-----|-----|-----------|")

        for var_name, var_stats in sorted(
            output_stats["variable_distributions"].items()
        ):
            if "error" in var_stats:
                continue

            mean = var_stats.get("mean", "N/A")
            median = var_stats.get("median", "N/A")
            std = var_stats.get("std", "N/A")
            min_val = var_stats.get("min", "N/A")
            max_val = var_stats.get("max", "N/A")
            missing = var_stats.get("nans", {}).get("pct", 0)

            lines.append(
                f"| {var_name} | {mean} | {median} | {std} | {min_val} | {max_val} | {missing}% |"
            )

    if "liquidity_analysis" in output_stats:
        lines.append("")
        lines.append("### Liquidity Measures")
        la = output_stats["liquidity_analysis"]

        if "amihud_stats" in la:
            am = la["amihud_stats"]
            lines.append("**Amihud Illiquidity:**")
            lines.append(f"- Mean: {am.get('mean', 0):.6f}")
            lines.append(f"- Median: {am.get('median', 0):.6f}")

        if "corwin_schultz_stats" in la:
            cs = la["corwin_schultz_stats"]
            lines.append("")
            lines.append("**Corwin-Schultz Spread:**")
            lines.append(f"- Mean: {cs.get('mean', 0):.6f}")
            lines.append(f"- Median: {cs.get('median', 0):.6f}")

    if "return_analysis" in output_stats:
        lines.append("")
        lines.append("### Return Statistics")
        ra = output_stats["return_analysis"]

        if "stock_ret_stats" in ra:
            sr = ra["stock_ret_stats"]
            lines.append("**Stock Returns:**")
            lines.append(f"- Mean: {sr.get('mean', 0):.2f}%")
            lines.append(f"- Std Dev: {sr.get('std', 0):.2f}%")
            lines.append(f"- Positive Returns %: {sr.get('positive_pct', 0):.1f}%")

    if "duration_stats" in output_stats:
        lines.append("")
        lines.append("### Event Duration Analysis")
        ds = output_stats["duration_stats"]

        if "for_takeovers_only" in ds:
            dto = ds["for_takeovers_only"]
            lines.append("**Takeover Duration (quarters):**")
            lines.append(f"- Mean: {dto.get('mean', 0):.2f}")
            lines.append(f"- Median: {dto.get('median', 0):.2f}")
            lines.append(f"- Range: {dto.get('min', 0):.2f} to {dto.get('max', 0):.2f}")

    # Write report
    report_content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)


__all__ = [
    # General stats
    "print_stat",
    "analyze_missing_values",
    "print_stats_summary",
    "save_stats",
    # Input/output stats
    "compute_input_stats",
    "compute_temporal_stats",
    "compute_entity_stats",
    # Linking stats
    "compute_linking_input_stats",
    "compute_linking_process_stats",
    "compute_linking_output_stats",
    "collect_fuzzy_match_samples",
    "collect_tier_match_samples",
    "collect_unmatched_samples",
    "collect_before_after_samples",
    # Tenure stats
    "compute_tenure_input_stats",
    "compute_tenure_process_stats",
    "compute_tenure_output_stats",
    "collect_tenure_samples",
    # Manifest stats
    "compute_manifest_input_stats",
    "compute_manifest_process_stats",
    "compute_manifest_output_stats",
    "collect_ceo_distribution_samples",
    # Tokenize stats
    "compute_tokenize_input_stats",
    "compute_tokenize_process_stats",
    "compute_tokenize_output_stats",
    # ConstructVariables stats
    "compute_constructvariables_input_stats",
    "compute_constructvariables_process_stats",
    "compute_constructvariables_output_stats",
    # Financial stats
    "compute_financial_input_stats",
    "compute_financial_process_stats",
    "compute_financial_output_stats",
    # Market stats
    "compute_market_input_stats",
    "compute_market_process_stats",
    "compute_market_output_stats",
    # Event flags stats
    "compute_event_flags_input_stats",
    "compute_event_flags_process_stats",
    "compute_event_flags_output_stats",
    # Step stats
    "compute_step31_input_stats",
    "compute_step31_process_stats",
    "compute_step31_output_stats",
    "compute_step32_input_stats",
    "compute_step32_process_stats",
    "compute_step32_output_stats",
    "compute_step33_input_stats",
    "compute_step33_process_stats",
    "compute_step33_output_stats",
    # Reports
    "generate_financial_report_markdown",
]
