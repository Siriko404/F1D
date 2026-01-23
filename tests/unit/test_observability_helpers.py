"""
Observability Helper Functions - Inline Template for Copy-Paste to Scripts

This file contains inline helper functions for observability that can be copied
into any script. Following Phase 1 inline helper pattern for self-contained replication.

Functions included:
1. get_process_memory_mb() - Track process memory usage (RSS, VMS, percent)
2. calculate_throughput() - Calculate rows/second throughput
3. compute_file_checksum() - Compute SHA-256 checksum for files
4. detect_anomalies_zscore() - Detect outliers using z-score method
5. detect_anomalies_iqr() - Detect outliers using IQR method

All functions are deterministic and handle edge cases (empty data, all NaN, zero variance).
"""

import hashlib
import psutil
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


def get_process_memory_mb() -> Dict[str, float]:
    """
    Get current process memory usage in MB.

    Returns:
        Dict with keys:
        - rss_mb: Resident Set Size (actual physical memory in use)
        - vms_mb: Virtual Memory Size (total memory allocated)
        - percent: Memory usage as percentage of system memory

    Example:
        >>> mem_stats = get_process_memory_mb()
        >>> print(f"Memory: {mem_stats['rss_mb']:.2f} MB")
        Memory: 245.30 MB
    """
    process = psutil.Process()
    mem_info = process.memory_info()

    return {
        "rss_mb": mem_info.rss / (1024 * 1024),  # Resident Set Size
        "vms_mb": mem_info.vms / (1024 * 1024),  # Virtual Memory Size
        "percent": mem_info.percent,
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

    Example:
        >>> throughput = calculate_throughput(1000, 10)
        >>> print(f"Throughput: {throughput} rows/sec")
        Throughput: 100.0 rows/sec
    """
    if duration_seconds <= 0:
        return 0.0
    return round(rows_processed / duration_seconds, 2)


def compute_file_checksum(filepath: Path, algorithm: str = "sha256") -> str:
    """
    Compute checksum for a file using specified algorithm.

    Reads file in 8KB chunks for memory efficiency with large files.

    Args:
        filepath: Path to the file
        algorithm: Hash algorithm (default: "sha256")

    Returns:
        Hexdigest string of the file checksum

    Example:
        >>> checksum = compute_file_checksum(Path("output.csv"))
        >>> print(f"SHA-256: {checksum}")
        SHA-256: a1b2c3...
    """
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def detect_anomalies_zscore(
    df: pd.DataFrame, columns: List[str], threshold: float = 3.0
) -> Dict[str, Dict]:
    """
    Detect anomalies using z-score (standard deviation) method.

    Deterministic: Same input produces same output.

    Values beyond threshold standard deviations from mean are flagged as anomalies.
    Uses 3.0 as default threshold (commonly used for strong outliers).

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

    Example:
        >>> df = pd.DataFrame({'A': [1, 1, 1, 1, 100]})
        >>> anomalies = detect_anomalies_zscore(df, ['A'], threshold=2.0)
        >>> print(anomalies['A']['count'])
        1
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


def detect_anomalies_iqr(
    df: pd.DataFrame, columns: List[str], multiplier: float = 3.0
) -> Dict[str, Dict]:
    """
    Detect anomalies using IQR (Interquartile Range) method.

    Deterministic: Same input produces same output.

    Values beyond Q1 - multiplier*IQR or Q3 + multiplier*IQR are flagged.
    Uses 3.0 as default multiplier for strong outliers.

    Args:
        df: DataFrame to analyze
        columns: List of column names to analyze
        multiplier: IQR multiplier for cutoff (default 3.0 = strong outliers)

    Returns:
        Dict mapping column_name -> anomaly info with keys:
        - count: Number of anomalies detected
        - sample_anomalies: List of first 10 anomaly indices (for review)
        - iqr_bounds: List of [lower_bound, upper_bound] (rounded to 4 decimals)

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3, 4, 5, 100]})
        >>> anomalies = detect_anomalies_iqr(df, ['A'], multiplier=3.0)
        >>> print(anomalies['A']['count'])
        1
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


# ============= UNIT TESTS =============
"""
Unit tests for observability helper functions.

Run with: pytest tests/unit/test_observability_helpers.py -v
"""

import pytest
import tempfile


def test_get_process_memory_mb():
    """Test get_process_memory_mb returns correct structure."""
    mem_stats = get_process_memory_mb()

    # Verify return type and structure
    assert isinstance(mem_stats, dict), "Should return a dictionary"
    assert "rss_mb" in mem_stats, "Should have rss_mb key"
    assert "vms_mb" in mem_stats, "Should have vms_mb key"
    assert "percent" in mem_stats, "Should have percent key"

    # Verify values are numeric
    assert isinstance(mem_stats["rss_mb"], (int, float)), "rss_mb should be numeric"
    assert isinstance(mem_stats["vms_mb"], (int, float)), "vms_mb should be numeric"
    assert isinstance(mem_stats["percent"], (int, float)), "percent should be numeric"

    # Verify process is running (RSS should be positive)
    assert mem_stats["rss_mb"] > 0, "RSS should be positive for running process"


def test_calculate_throughput():
    """Test calculate_throughput with various inputs."""
    # Normal case
    result = calculate_throughput(1000, 10)
    assert result == 100.0, "1000 rows / 10 seconds = 100 rows/sec"

    # Division by zero - should return 0.0
    result = calculate_throughput(100, 0)
    assert result == 0.0, "Division by zero should return 0.0"

    result = calculate_throughput(100, -5)
    assert result == 0.0, "Negative duration should return 0.0"

    # Rounding to 2 decimals
    result = calculate_throughput(1, 3)
    assert result == 0.33, "1 / 3 = 0.33 (rounded to 2 decimals)"


def test_compute_file_checksum():
    """Test compute_file_checksum with known content."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        temp_path = Path(f.name)
        f.write("test content")

    try:
        # Test with SHA-256 (default)
        checksum = compute_file_checksum(temp_path, algorithm="sha256")
        expected_checksum = hashlib.sha256(b"test content").hexdigest()
        assert checksum == expected_checksum, "SHA-256 checksum should match"

        # Verify checksum is a hex string
        assert isinstance(checksum, str), "Checksum should be a string"
        assert len(checksum) == 64, "SHA-256 should produce 64-character hex string"

        # Test with different algorithm
        checksum_md5 = compute_file_checksum(temp_path, algorithm="md5")
        expected_md5 = hashlib.md5(b"test content").hexdigest()
        assert checksum_md5 == expected_md5, "MD5 checksum should match"
    finally:
        temp_path.unlink()


def test_detect_anomalies_zscore():
    """Test detect_anomalies_zscore with known outliers."""
    # Create test DataFrame with known outlier
    df = pd.DataFrame(
        {
            "normal": [1, 2, 3, 4, 5],
            "with_outlier": [1, 2, 3, 4, 100],  # 100 is an outlier
            "all_nan": [None, None, None],
            "constant": [5, 5, 5, 5, 5],  # Zero std
            "text": ["a", "b", "c", "d", "e"],  # Non-numeric
        }
    )

    # Test normal column - no anomalies
    result = detect_anomalies_zscore(df, ["normal"], threshold=3.0)
    assert "normal" in result, "Should return result for normal column"
    assert result["normal"]["count"] == 0, "Normal column should have no anomalies"

    # Test column with outlier
    result = detect_anomalies_zscore(df, ["with_outlier"], threshold=3.0)
    assert "with_outlier" in result, "Should return result for outlier column"
    assert result["with_outlier"]["count"] == 1, "Should detect 1 outlier"
    assert result["with_outlier"]["threshold"] == 3.0, "Should return threshold used"

    # Test all NaN column
    result = detect_anomalies_zscore(df, ["all_nan"], threshold=3.0)
    assert "all_nan" in result, "Should return result for all-NaN column"
    assert result["all_nan"]["count"] == 0, "All-NaN column should have 0 anomalies"

    # Test zero std column (constant values)
    result = detect_anomalies_zscore(df, ["constant"], threshold=3.0)
    assert "constant" in result, "Should return result for constant column"
    assert result["constant"]["count"] == 0, (
        "Constant column (zero std) should have 0 anomalies"
    )

    # Test non-numeric column (should skip)
    result = detect_anomalies_zscore(df, ["text"], threshold=3.0)
    assert "text" not in result, "Should skip non-numeric column"

    # Test with missing column (should skip)
    result = detect_anomalies_zscore(df, ["nonexistent"], threshold=3.0)
    assert "nonexistent" not in result, "Should skip missing column"


def test_detect_anomalies_iqr():
    """Test detect_anomalies_iqr with known outliers."""
    # Create test DataFrame with known outlier
    df = pd.DataFrame(
        {
            "normal": [1, 2, 3, 4, 5],
            "with_outlier": [1, 2, 3, 4, 100],  # 100 is an outlier
            "all_nan": [None, None, None],
            "constant": [5, 5, 5, 5, 5],  # Zero IQR
            "text": ["a", "b", "c", "d", "e"],  # Non-numeric
        }
    )

    # Test normal column - no anomalies
    result = detect_anomalies_iqr(df, ["normal"], multiplier=3.0)
    assert "normal" in result, "Should return result for normal column"
    assert result["normal"]["count"] == 0, "Normal column should have no anomalies"

    # Test column with outlier
    result = detect_anomalies_iqr(df, ["with_outlier"], multiplier=3.0)
    assert "with_outlier" in result, "Should return result for outlier column"
    assert result["with_outlier"]["count"] == 1, "Should detect 1 outlier"
    assert "iqr_bounds" in result["with_outlier"], "Should return IQR bounds"

    # Test all NaN column
    result = detect_anomalies_iqr(df, ["all_nan"], multiplier=3.0)
    assert "all_nan" in result, "Should return result for all-NaN column"
    assert result["all_nan"]["count"] == 0, "All-NaN column should have 0 anomalies"

    # Test zero IQR column (constant values)
    result = detect_anomalies_iqr(df, ["constant"], multiplier=3.0)
    assert "constant" in result, "Should return result for constant column"
    assert result["constant"]["count"] == 0, (
        "Constant column (zero IQR) should have 0 anomalies"
    )

    # Test non-numeric column (should skip)
    result = detect_anomalies_iqr(df, ["text"], multiplier=3.0)
    assert "text" not in result, "Should skip non-numeric column"

    # Test with missing column (should skip)
    result = detect_anomalies_iqr(df, ["nonexistent"], multiplier=3.0)
    assert "nonexistent" not in result, "Should skip missing column"


def test_deterministic_behavior():
    """Test that anomaly detection is deterministic."""
    df = pd.DataFrame({"A": [1, 2, 3, 4, 100]})

    # Run z-score detection twice
    result1 = detect_anomalies_zscore(df, ["A"], threshold=3.0)
    result2 = detect_anomalies_zscore(df, ["A"], threshold=3.0)
    assert result1 == result2, "z-score detection should be deterministic"

    # Run IQR detection twice
    result1 = detect_anomalies_iqr(df, ["A"], multiplier=3.0)
    result2 = detect_anomalies_iqr(df, ["A"], multiplier=3.0)
    assert result1 == result2, "IQR detection should be deterministic"
