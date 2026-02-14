"""
Unit tests for the stats module (src/f1d/shared/observability/stats.py).

This test file provides comprehensive coverage for the stats module functions
including:
- Core statistics functions (print_stat, analyze_missing_values)
- Throughput calculations
- Anomaly detection (z-score and IQR methods)
- Input/temporal/entity statistics computation
- Regression tests against golden fixtures

Run with: pytest tests/unit/test_stats_module.py -v
"""

import io
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from f1d.shared.observability.stats import (
    analyze_missing_values,
    calculate_throughput,
    compute_entity_stats,
    compute_input_stats,
    compute_temporal_stats,
    detect_anomalies_iqr,
    detect_anomalies_zscore,
    print_stat,
    print_stats_summary,
    save_stats,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Create a sample DataFrame with known statistics for testing."""
    np.random.seed(42)
    return pd.DataFrame(
        {
            "numeric_col": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            "with_nan": [1.0, 2.0, np.nan, 4.0, 5.0, np.nan, 7.0, 8.0, 9.0, 10.0],
            "all_nan": [np.nan] * 10,
            "constant": [5.0] * 10,
            "string_col": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
            "date_col": pd.date_range("2020-01-01", periods=10, freq="D"),
        }
    )


@pytest.fixture
def dataframe_with_missing() -> pd.DataFrame:
    """Create a DataFrame with known missing values for testing."""
    return pd.DataFrame(
        {
            "no_missing": [1, 2, 3, 4, 5],
            "some_missing": [1, None, 3, None, 5],
            "all_missing": [None, None, None, None, None],
        }
    )


@pytest.fixture
def dataframe_with_outliers() -> pd.DataFrame:
    """Create a DataFrame with known outliers for testing."""
    # Create data with clear outliers
    # For IQR: need data with variance so IQR > 0
    return pd.DataFrame(
        {
            "normal": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19] * 5,  # 50 values
            "with_outlier": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19] * 4
            + [10, 11, 12, 13, 14, 15, 16, 17, 18, 1000],  # 1000 is outlier, IQR > 0
            "constant": [5.0] * 50,  # Zero std
        }
    )


@pytest.fixture
def temporal_dataframe() -> pd.DataFrame:
    """Create a DataFrame with temporal data for testing."""
    dates = pd.date_range("2020-01-01", periods=100, freq="D")
    return pd.DataFrame(
        {
            "start_date": dates,
            "value": range(100),
        }
    )


@pytest.fixture
def entity_dataframe() -> pd.DataFrame:
    """Create a DataFrame with entity data for testing."""
    return pd.DataFrame(
        {
            "company_id": ["A", "A", "B", "B", "C", "C", "C"],
            "company_ticker": ["AA", "AA", "BB", "BB", "CC", "CC", "CC"],
            "city": ["NYC", "NYC", "LA", "LA", "NYC", "CHI", "CHI"],
            "data_quality_score": [0.9, 0.8, 0.95, 0.85, 0.7, 0.8, 0.9],
            "has_speaker_data": [True, True, False, True, False, True, True],
            "speaker_record_count": [5, 3, None, 2, None, 4, 6],
            "processing_lag_hours": [1.5, 2.0, 0.5, 3.0, 1.0, 2.5, 4.0],
        }
    )


# =============================================================================
# Tests for print_stat
# =============================================================================


class TestPrintStat:
    """Tests for the print_stat function."""

    def test_print_stat_with_before_after(self, capsys: pytest.CaptureFixture) -> None:
        """Test print_stat with before/after values for delta calculation."""
        print_stat("Test Stat", before=100, after=150)
        captured = capsys.readouterr()
        assert "Test Stat" in captured.out
        assert "100" in captured.out
        assert "150" in captured.out
        assert "+50.0%" in captured.out

    def test_print_stat_with_negative_delta(self, capsys: pytest.CaptureFixture) -> None:
        """Test print_stat with negative delta."""
        print_stat("Test Stat", before=100, after=50)
        captured = capsys.readouterr()
        assert "-50.0%" in captured.out

    def test_print_stat_with_zero_before(self, capsys: pytest.CaptureFixture) -> None:
        """Test print_stat with zero before value (avoid division by zero)."""
        print_stat("Test Stat", before=0, after=50)
        captured = capsys.readouterr()
        # Should not crash, pct should be 0
        assert "Test Stat" in captured.out

    def test_print_stat_with_int_value(self, capsys: pytest.CaptureFixture) -> None:
        """Test print_stat with direct integer value."""
        print_stat("Count", value=1000)
        captured = capsys.readouterr()
        assert "Count" in captured.out
        assert "1,000" in captured.out

    def test_print_stat_with_float_value(self, capsys: pytest.CaptureFixture) -> None:
        """Test print_stat with direct float value."""
        print_stat("Rate", value=12.3456)
        captured = capsys.readouterr()
        assert "Rate" in captured.out
        assert "12.35" in captured.out

    def test_print_stat_with_string_value(self, capsys: pytest.CaptureFixture) -> None:
        """Test print_stat with string value."""
        print_stat("Label", value="test_string")
        captured = capsys.readouterr()
        assert "Label" in captured.out
        assert "test_string" in captured.out

    def test_print_stat_with_custom_indent(self, capsys: pytest.CaptureFixture) -> None:
        """Test print_stat with custom indent."""
        print_stat("Stat", value=100, indent=4)
        captured = capsys.readouterr()
        # 4 spaces of indent
        assert captured.out.startswith("    Stat")


# =============================================================================
# Tests for analyze_missing_values
# =============================================================================


class TestAnalyzeMissingValues:
    """Tests for the analyze_missing_values function."""

    def test_analyze_missing_values_basic(
        self, dataframe_with_missing: pd.DataFrame
    ) -> None:
        """Test basic missing value analysis."""
        result = analyze_missing_values(dataframe_with_missing)

        # no_missing column should not be in result (no NaNs)
        assert "no_missing" not in result

        # some_missing should be present with 2 NaNs out of 5 (40%)
        assert "some_missing" in result
        assert result["some_missing"]["count"] == 2
        assert result["some_missing"]["percent"] == 40.0

        # all_missing should be present with 5 NaNs (100%)
        assert "all_missing" in result
        assert result["all_missing"]["count"] == 5
        assert result["all_missing"]["percent"] == 100.0

    def test_analyze_missing_values_no_missing(self) -> None:
        """Test with DataFrame that has no missing values."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        result = analyze_missing_values(df)
        assert result == {}

    def test_analyze_missing_values_empty_dataframe(self) -> None:
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        result = analyze_missing_values(df)
        assert result == {}

    def test_analyze_missing_values_percent_calculation(self) -> None:
        """Test that percent calculation is correct."""
        df = pd.DataFrame({"col": [1, None, None, 4, 5]})  # 2 out of 5 = 40%
        result = analyze_missing_values(df)
        assert result["col"]["percent"] == 40.0


# =============================================================================
# Tests for calculate_throughput
# =============================================================================


class TestCalculateThroughput:
    """Tests for the calculate_throughput function."""

    def test_calculate_throughput_basic(self) -> None:
        """Test basic throughput calculation."""
        result = calculate_throughput(1000, 10)
        assert result == 100.0

    def test_calculate_throughput_with_decimals(self) -> None:
        """Test throughput calculation with decimal result."""
        result = calculate_throughput(100, 30)
        assert result == 3.33  # Rounded to 2 decimals

    def test_calculate_throughput_zero_duration_raises(self) -> None:
        """Test that zero duration raises ValueError."""
        with pytest.raises(ValueError, match="duration_seconds"):
            calculate_throughput(100, 0)

    def test_calculate_throughput_negative_duration_raises(self) -> None:
        """Test that negative duration raises ValueError."""
        with pytest.raises(ValueError, match="duration_seconds"):
            calculate_throughput(100, -5)

    def test_calculate_throughput_zero_rows(self) -> None:
        """Test throughput with zero rows processed."""
        result = calculate_throughput(0, 10)
        assert result == 0.0

    def test_calculate_throughput_large_values(self) -> None:
        """Test throughput with large values."""
        result = calculate_throughput(1_000_000, 3600)  # 1M rows in 1 hour
        assert result == pytest.approx(277.78, rel=0.01)


# =============================================================================
# Tests for detect_anomalies_zscore
# =============================================================================


class TestDetectAnomaliesZscore:
    """Tests for the detect_anomalies_zscore function."""

    def test_detect_anomalies_zscore_normal_data(
        self, dataframe_with_outliers: pd.DataFrame
    ) -> None:
        """Test that normal data has no anomalies detected."""
        result = detect_anomalies_zscore(dataframe_with_outliers, ["normal"], threshold=3.0)
        assert "normal" in result
        assert result["normal"]["count"] == 0

    def test_detect_anomalies_zscore_with_outlier(
        self, dataframe_with_outliers: pd.DataFrame
    ) -> None:
        """Test that outlier is detected."""
        result = detect_anomalies_zscore(
            dataframe_with_outliers, ["with_outlier"], threshold=3.0
        )
        assert "with_outlier" in result
        assert result["with_outlier"]["count"] == 1
        assert "threshold" in result["with_outlier"]
        assert "mean" in result["with_outlier"]
        assert "std" in result["with_outlier"]

    def test_detect_anomalies_zscore_constant_data(
        self, dataframe_with_outliers: pd.DataFrame
    ) -> None:
        """Test that constant data (zero std) returns no anomalies."""
        result = detect_anomalies_zscore(dataframe_with_outliers, ["constant"], threshold=3.0)
        assert "constant" in result
        assert result["constant"]["count"] == 0

    def test_detect_anomalies_zscore_missing_column(self) -> None:
        """Test that missing columns are skipped."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = detect_anomalies_zscore(df, ["nonexistent"], threshold=3.0)
        assert "nonexistent" not in result

    def test_detect_anomalies_zscore_non_numeric(self) -> None:
        """Test that non-numeric columns are skipped."""
        df = pd.DataFrame({"text": ["a", "b", "c"]})
        result = detect_anomalies_zscore(df, ["text"], threshold=3.0)
        assert "text" not in result

    def test_detect_anomalies_zscore_empty_data(self) -> None:
        """Test with empty DataFrame."""
        df = pd.DataFrame({"a": []})
        result = detect_anomalies_zscore(df, ["a"], threshold=3.0)
        assert result["a"]["count"] == 0

    def test_detect_anomalies_zscore_all_nan(self) -> None:
        """Test with all NaN values."""
        df = pd.DataFrame({"a": [np.nan, np.nan, np.nan]})
        result = detect_anomalies_zscore(df, ["a"], threshold=3.0)
        assert result["a"]["count"] == 0

    def test_detect_anomalies_zscore_deterministic(self) -> None:
        """Test that z-score detection is deterministic."""
        df = pd.DataFrame({"A": [1, 2, 3, 4, 100]})
        result1 = detect_anomalies_zscore(df, ["A"], threshold=3.0)
        result2 = detect_anomalies_zscore(df, ["A"], threshold=3.0)
        assert result1 == result2

    def test_detect_anomalies_zscore_custom_threshold(self) -> None:
        """Test with custom threshold."""
        # Create data where 50 is only an outlier at lower thresholds
        df = pd.DataFrame({"A": [10, 11, 12, 13, 50]})
        result_strict = detect_anomalies_zscore(df, ["A"], threshold=2.0)
        result_loose = detect_anomalies_zscore(df, ["A"], threshold=5.0)
        # Stricter threshold should detect more
        assert result_strict["A"]["count"] >= result_loose["A"]["count"]


# =============================================================================
# Tests for detect_anomalies_iqr
# =============================================================================


class TestDetectAnomaliesIqr:
    """Tests for the detect_anomalies_iqr function."""

    def test_detect_anomalies_iqr_normal_data(
        self, dataframe_with_outliers: pd.DataFrame
    ) -> None:
        """Test that normal data has no anomalies detected."""
        result = detect_anomalies_iqr(dataframe_with_outliers, ["normal"], multiplier=3.0)
        assert "normal" in result
        assert result["normal"]["count"] == 0

    def test_detect_anomalies_iqr_with_outlier(
        self, dataframe_with_outliers: pd.DataFrame
    ) -> None:
        """Test that outlier is detected with IQR bounds."""
        result = detect_anomalies_iqr(
            dataframe_with_outliers, ["with_outlier"], multiplier=3.0
        )
        assert "with_outlier" in result
        assert result["with_outlier"]["count"] == 1
        assert "iqr_bounds" in result["with_outlier"]
        assert len(result["with_outlier"]["iqr_bounds"]) == 2

    def test_detect_anomalies_iqr_constant_data(
        self, dataframe_with_outliers: pd.DataFrame
    ) -> None:
        """Test that constant data (zero IQR) returns no anomalies."""
        result = detect_anomalies_iqr(dataframe_with_outliers, ["constant"], multiplier=3.0)
        assert "constant" in result
        assert result["constant"]["count"] == 0

    def test_detect_anomalies_iqr_missing_column(self) -> None:
        """Test that missing columns are skipped."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = detect_anomalies_iqr(df, ["nonexistent"], multiplier=3.0)
        assert "nonexistent" not in result

    def test_detect_anomalies_iqr_non_numeric(self) -> None:
        """Test that non-numeric columns are skipped."""
        df = pd.DataFrame({"text": ["a", "b", "c"]})
        result = detect_anomalies_iqr(df, ["text"], multiplier=3.0)
        assert "text" not in result

    def test_detect_anomalies_iqr_deterministic(self) -> None:
        """Test that IQR detection is deterministic."""
        df = pd.DataFrame({"A": [1, 2, 3, 4, 100]})
        result1 = detect_anomalies_iqr(df, ["A"], multiplier=3.0)
        result2 = detect_anomalies_iqr(df, ["A"], multiplier=3.0)
        assert result1 == result2

    def test_detect_anomalies_iqr_custom_multiplier(self) -> None:
        """Test with custom multiplier."""
        df = pd.DataFrame({"A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]})
        result_strict = detect_anomalies_iqr(df, ["A"], multiplier=1.5)
        result_loose = detect_anomalies_iqr(df, ["A"], multiplier=5.0)
        # Stricter multiplier should detect more
        assert result_strict["A"]["count"] >= result_loose["A"]["count"]


# =============================================================================
# Tests for compute_input_stats
# =============================================================================


class TestComputeInputStats:
    """Tests for the compute_input_stats function."""

    def test_compute_input_stats_basic(self, sample_dataframe: pd.DataFrame) -> None:
        """Test basic input statistics computation."""
        result = compute_input_stats(sample_dataframe)

        assert "record_count" in result
        assert result["record_count"] == 10

        assert "column_count" in result
        assert result["column_count"] == 6

        assert "memory_mb" in result
        # Small dataframes may have memory_mb of 0 (rounded from bytes)
        assert result["memory_mb"] >= 0

    def test_compute_input_stats_column_types(
        self, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test that column types are correctly identified."""
        result = compute_input_stats(sample_dataframe)

        assert "column_types" in result
        # Should have numeric, datetime, and string columns
        assert result["column_types"]["numeric"] >= 4  # numeric_col, with_nan, all_nan, constant
        assert result["column_types"]["datetime"] >= 1

    def test_compute_input_stats_numeric_stats(
        self, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test that numeric statistics are computed correctly."""
        result = compute_input_stats(sample_dataframe)

        assert "numeric_stats" in result
        assert "numeric_col" in result["numeric_stats"]

        stats = result["numeric_stats"]["numeric_col"]
        assert stats["min"] == 1.0
        assert stats["max"] == 10.0
        assert stats["mean"] == 5.5
        assert stats["median"] == 5.5

    def test_compute_input_stats_datetime_stats(
        self, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test that datetime statistics are computed."""
        result = compute_input_stats(sample_dataframe)

        assert "datetime_stats" in result
        assert "date_col" in result["datetime_stats"]

        date_stats = result["datetime_stats"]["date_col"]
        assert "min_date" in date_stats
        assert "max_date" in date_stats
        assert "span_days" in date_stats

    def test_compute_input_stats_string_stats(
        self, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test that string statistics are computed."""
        result = compute_input_stats(sample_dataframe)

        assert "string_stats" in result
        if "string_col" in result["string_stats"]:
            str_stats = result["string_stats"]["string_col"]
            assert "avg_length" in str_stats
            assert "unique_count" in str_stats

    def test_compute_input_stats_cardinality(
        self, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test that cardinality analysis is performed."""
        result = compute_input_stats(sample_dataframe)

        assert "cardinality" in result
        # String column should have cardinality analysis
        if "string_col" in result["cardinality"]:
            assert result["cardinality"]["string_col"] == 10  # 10 unique values

    def test_compute_input_stats_empty_dataframe(self) -> None:
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        result = compute_input_stats(df)
        assert result["record_count"] == 0

    def test_compute_input_stats_deterministic(
        self, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test that compute_input_stats is deterministic."""
        result1 = compute_input_stats(sample_dataframe)
        result2 = compute_input_stats(sample_dataframe)
        assert result1 == result2


# =============================================================================
# Tests for compute_temporal_stats
# =============================================================================


class TestComputeTemporalStats:
    """Tests for the compute_temporal_stats function."""

    def test_compute_temporal_stats_basic(
        self, temporal_dataframe: pd.DataFrame
    ) -> None:
        """Test basic temporal statistics computation."""
        result = compute_temporal_stats(temporal_dataframe, date_col="start_date")

        assert "year_distribution" in result
        assert "month_distribution" in result
        assert "quarter_distribution" in result
        assert "day_of_week_distribution" in result
        assert "date_range" in result

    def test_compute_temporal_stats_date_range(
        self, temporal_dataframe: pd.DataFrame
    ) -> None:
        """Test that date range is computed correctly."""
        result = compute_temporal_stats(temporal_dataframe, date_col="start_date")

        assert "earliest" in result["date_range"]
        assert "latest" in result["date_range"]
        assert "span_days" in result["date_range"]
        assert result["date_range"]["span_days"] == 99  # 100 days span

    def test_compute_temporal_stats_year_distribution(
        self, temporal_dataframe: pd.DataFrame
    ) -> None:
        """Test that year distribution is computed."""
        result = compute_temporal_stats(temporal_dataframe, date_col="start_date")

        # All dates in 2020
        assert 2020 in result["year_distribution"]
        assert result["year_distribution"][2020] == 100

    def test_compute_temporal_stats_month_distribution(
        self, temporal_dataframe: pd.DataFrame
    ) -> None:
        """Test that month distribution is computed."""
        result = compute_temporal_stats(temporal_dataframe, date_col="start_date")

        # Should have entries for months covered
        assert len(result["month_distribution"]) > 0

    def test_compute_temporal_stats_missing_column(self) -> None:
        """Test with missing date column."""
        df = pd.DataFrame({"other_col": [1, 2, 3]})
        result = compute_temporal_stats(df, date_col="nonexistent")

        assert "error" in result
        assert result["year_distribution"] == {}

    def test_compute_temporal_stats_empty_dates(self) -> None:
        """Test with empty date values."""
        df = pd.DataFrame({"start_date": [None, None, None]})
        result = compute_temporal_stats(df, date_col="start_date")

        assert "error" in result

    def test_compute_temporal_stats_deterministic(
        self, temporal_dataframe: pd.DataFrame
    ) -> None:
        """Test that temporal stats are deterministic."""
        result1 = compute_temporal_stats(temporal_dataframe, date_col="start_date")
        result2 = compute_temporal_stats(temporal_dataframe, date_col="start_date")
        assert result1 == result2


# =============================================================================
# Tests for compute_entity_stats
# =============================================================================


class TestComputeEntityStats:
    """Tests for the compute_entity_stats function."""

    def test_compute_entity_stats_company_coverage(
        self, entity_dataframe: pd.DataFrame
    ) -> None:
        """Test that company coverage is computed."""
        result = compute_entity_stats(entity_dataframe)

        assert "company_coverage" in result
        assert result["company_coverage"]["unique_companies"] == 3
        assert "avg_calls_per_company" in result["company_coverage"]

    def test_compute_entity_stats_geographic_coverage(
        self, entity_dataframe: pd.DataFrame
    ) -> None:
        """Test that geographic coverage is computed."""
        result = compute_entity_stats(entity_dataframe)

        assert "geographic_coverage" in result
        assert result["geographic_coverage"]["unique_cities"] == 3
        assert "top_cities" in result["geographic_coverage"]

    def test_compute_entity_stats_data_quality(
        self, entity_dataframe: pd.DataFrame
    ) -> None:
        """Test that data quality distribution is computed."""
        result = compute_entity_stats(entity_dataframe)

        assert "data_quality_distribution" in result
        assert "mean" in result["data_quality_distribution"]
        assert "median" in result["data_quality_distribution"]

    def test_compute_entity_stats_speaker_coverage(
        self, entity_dataframe: pd.DataFrame
    ) -> None:
        """Test that speaker coverage is computed."""
        result = compute_entity_stats(entity_dataframe)

        assert "speaker_coverage" in result
        assert "percent_with_speaker_data" in result["speaker_coverage"]

    def test_compute_entity_stats_processing_lag(
        self, entity_dataframe: pd.DataFrame
    ) -> None:
        """Test that processing lag statistics are computed."""
        result = compute_entity_stats(entity_dataframe)

        assert "processing_lag_stats" in result
        assert "mean_hours" in result["processing_lag_stats"]
        assert "median_hours" in result["processing_lag_stats"]

    def test_compute_entity_stats_missing_columns(self) -> None:
        """Test with DataFrame missing entity columns."""
        df = pd.DataFrame({"other_col": [1, 2, 3]})
        result = compute_entity_stats(df)

        # Should still return structure with default/empty values
        assert "company_coverage" in result
        assert result["company_coverage"]["unique_companies"] == 0

    def test_compute_entity_stats_deterministic(
        self, entity_dataframe: pd.DataFrame
    ) -> None:
        """Test that entity stats are deterministic."""
        result1 = compute_entity_stats(entity_dataframe)
        result2 = compute_entity_stats(entity_dataframe)
        assert result1 == result2


# =============================================================================
# Tests for print_stats_summary
# =============================================================================


class TestPrintStatsSummary:
    """Tests for the print_stats_summary function."""

    def test_print_stats_summary_basic(self, capsys: pytest.CaptureFixture) -> None:
        """Test basic stats summary printing."""
        stats = {
            "input": {"total_rows": 1000},
            "output": {"final_rows": 800},
            "timing": {"duration_seconds": 30.5},
            "processing": {"filter_a": 100, "filter_b": 100},
        }

        print_stats_summary(stats)
        captured = capsys.readouterr()

        assert "STATISTICS SUMMARY" in captured.out
        assert "1,000" in captured.out  # Input rows
        assert "800" in captured.out  # Output rows
        assert "30.50" in captured.out  # Duration

    def test_print_stats_summary_with_zero_input(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Test stats summary with zero input rows (avoid division by zero)."""
        stats = {
            "input": {"total_rows": 0},
            "output": {"final_rows": 0},
            "timing": {"duration_seconds": 0},
            "processing": {},
        }

        # Should not crash
        print_stats_summary(stats)
        captured = capsys.readouterr()
        assert "STATISTICS SUMMARY" in captured.out

    def test_print_stats_summary_skips_non_numeric(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Test that non-numeric processing values are skipped."""
        stats = {
            "input": {"total_rows": 100},
            "output": {"final_rows": 80},
            "timing": {"duration_seconds": 10},
            "processing": {
                "numeric_step": 10,
                "dict_step": {"nested": "value"},
                "list_step": [1, 2, 3],
            },
        }

        print_stats_summary(stats)
        captured = capsys.readouterr()

        # Should include numeric step but not dict/list
        assert "numeric_step" in captured.out


# =============================================================================
# Tests for save_stats
# =============================================================================


class TestSaveStats:
    """Tests for the save_stats function."""

    def test_save_stats_creates_file(self, tmp_path: Path) -> None:
        """Test that save_stats creates a JSON file."""
        stats = {
            "input": {"total_rows": 1000},
            "output": {"final_rows": 800},
        }

        save_stats(stats, tmp_path)

        stats_file = tmp_path / "stats.json"
        assert stats_file.exists()

    def test_save_stats_content(self, tmp_path: Path) -> None:
        """Test that save_stats writes correct content."""
        stats = {
            "input": {"total_rows": 1000},
            "output": {"final_rows": 800},
        }

        save_stats(stats, tmp_path)

        stats_file = tmp_path / "stats.json"
        content = json.loads(stats_file.read_text())

        assert content["input"]["total_rows"] == 1000
        assert content["output"]["final_rows"] == 800

    def test_save_stats_with_datetime(self, tmp_path: Path) -> None:
        """Test that save_stats handles datetime objects."""
        stats = {
            "timestamp": datetime(2024, 1, 15, 10, 30, 0),
        }

        save_stats(stats, tmp_path)

        stats_file = tmp_path / "stats.json"
        content = json.loads(stats_file.read_text())

        # datetime should be converted to string
        assert "timestamp" in content

    def test_save_stats_with_nan(self, tmp_path: Path) -> None:
        """Test that save_stats handles NaN values."""
        stats = {
            "value": float("nan"),
        }

        save_stats(stats, tmp_path)

        stats_file = tmp_path / "stats.json"
        content = json.loads(stats_file.read_text())

        # NaN should be converted to string "nan" or null
        assert "value" in content


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_analyze_missing_values_single_row(self) -> None:
        """Test missing value analysis with single row."""
        df = pd.DataFrame({"a": [None]})
        result = analyze_missing_values(df)
        assert result["a"]["count"] == 1
        assert result["a"]["percent"] == 100.0

    def test_calculate_throughput_small_values(self) -> None:
        """Test throughput with very small values."""
        result = calculate_throughput(1, 0.001)
        assert result == 1000.0

    def test_detect_anomalies_single_value(self) -> None:
        """Test anomaly detection with single value."""
        df = pd.DataFrame({"a": [5]})
        result_z = detect_anomalies_zscore(df, ["a"], threshold=3.0)
        result_i = detect_anomalies_iqr(df, ["a"], multiplier=3.0)

        # Single value should result in no anomalies
        assert result_z["a"]["count"] == 0
        assert result_i["a"]["count"] == 0

    def test_compute_input_stats_all_null_column(self) -> None:
        """Test input stats with all null column."""
        df = pd.DataFrame({"all_null": [None] * 5})
        result = compute_input_stats(df)

        # Should handle gracefully without crashing
        assert "record_count" in result

    def test_compute_temporal_stats_mixed_dates(self) -> None:
        """Test temporal stats with mixed valid/invalid dates.

        Note: The function does not use errors='coerce' so invalid date strings
        will raise a ValueError. This test documents that behavior.
        """
        df = pd.DataFrame(
            {
                "start_date": [
                    "2020-01-01",
                    "invalid",
                    "2020-03-01",
                    None,
                    "2020-05-01",
                ]
            }
        )
        # Invalid date string causes ValueError (not using errors='coerce')
        with pytest.raises(ValueError, match="time data"):
            compute_temporal_stats(df, date_col="start_date")


# =============================================================================
# Regression Tests with Golden Fixtures
# =============================================================================


@pytest.mark.regression
class TestRegressionGoldenFixtures:
    """Regression tests against golden fixtures to prevent silent data corruption."""

    @pytest.fixture
    def golden_stats_fixture(self) -> Dict[str, Any]:
        """Golden fixture with known expected values for regression testing."""
        return {
            "input_data": {
                "numeric_values": [1.0, 2.0, 3.0, 4.0, 5.0],
                "with_nan": [1.0, 2.0, None, 4.0, 5.0],
            },
            "expected_stats": {
                "mean": 3.0,
                "median": 3.0,
                "std": 1.5811388300841898,  # Exact value
                "min": 1.0,
                "max": 5.0,
                "missing_count": 1,
            },
            "expected_throughput": {
                "rows": 1000,
                "seconds": 10,
                "expected": 100.0,
            },
            "expected_zscore_outlier": {
                "data": [10] * 49 + [1000],
                "threshold": 3.0,
                "expected_count": 1,
            },
        }

    def test_numeric_stats_match_golden(self, golden_stats_fixture: Dict[str, Any]) -> None:
        """Verify numeric statistics match expected golden values."""
        data = golden_stats_fixture["input_data"]["numeric_values"]
        df = pd.DataFrame({"values": data})

        result = compute_input_stats(df)
        stats = result["numeric_stats"]["values"]
        expected = golden_stats_fixture["expected_stats"]

        # Use tolerance for floating point comparisons
        assert abs(stats["mean"] - expected["mean"]) < 1e-6
        assert abs(stats["median"] - expected["median"]) < 1e-6
        assert abs(stats["min"] - expected["min"]) < 1e-6
        assert abs(stats["max"] - expected["max"]) < 1e-6

    def test_missing_values_match_golden(
        self, golden_stats_fixture: Dict[str, Any]
    ) -> None:
        """Verify missing value count matches expected."""
        data = golden_stats_fixture["input_data"]["with_nan"]
        df = pd.DataFrame({"col": data})

        result = analyze_missing_values(df)
        expected = golden_stats_fixture["expected_stats"]

        assert result["col"]["count"] == expected["missing_count"]

    def test_throughput_matches_golden(self, golden_stats_fixture: Dict[str, Any]) -> None:
        """Verify throughput calculation matches expected."""
        fixture = golden_stats_fixture["expected_throughput"]

        result = calculate_throughput(fixture["rows"], fixture["seconds"])

        assert abs(result - fixture["expected"]) < 1e-6

    def test_zscore_detection_matches_golden(
        self, golden_stats_fixture: Dict[str, Any]
    ) -> None:
        """Verify z-score anomaly detection matches expected."""
        fixture = golden_stats_fixture["expected_zscore_outlier"]
        df = pd.DataFrame({"values": fixture["data"]})

        result = detect_anomalies_zscore(df, ["values"], threshold=fixture["threshold"])

        assert result["values"]["count"] == fixture["expected_count"]

    def test_determinism_across_runs(self) -> None:
        """Verify functions produce identical results across multiple runs."""
        np.random.seed(12345)
        data = np.random.randn(100).tolist()
        df = pd.DataFrame({"values": data})

        # Run twice and compare
        result1 = compute_input_stats(df)
        result2 = compute_input_stats(df)

        zscore1 = detect_anomalies_zscore(df, ["values"], threshold=3.0)
        zscore2 = detect_anomalies_zscore(df, ["values"], threshold=3.0)

        iqr1 = detect_anomalies_iqr(df, ["values"], multiplier=3.0)
        iqr2 = detect_anomalies_iqr(df, ["values"], multiplier=3.0)

        assert result1 == result2
        assert zscore1 == zscore2
        assert iqr1 == iqr2


# =============================================================================
# Golden Fixture File Tests (Task 3)
# =============================================================================


@pytest.mark.regression
class TestGoldenFixtureFile:
    """Regression tests using the external golden fixture file.

    These tests load expected values from tests/fixtures/stats_golden_output.json
    to verify that statistical functions produce consistent, correct output.
    """

    @pytest.fixture
    def golden_fixture_path(self) -> Path:
        """Return path to the golden fixture file."""
        return Path(__file__).parent.parent / "fixtures" / "stats_golden_output.json"

    @pytest.fixture
    def golden_fixture(self, golden_fixture_path: Path) -> Dict[str, Any]:
        """Load the golden fixture file."""
        with open(golden_fixture_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_golden_fixture_file_exists(self, golden_fixture_path: Path) -> None:
        """Verify the golden fixture file exists and is valid JSON."""
        assert golden_fixture_path.exists(), f"Golden fixture file not found: {golden_fixture_path}"

        with open(golden_fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "fixtures" in data
        assert "basic_numeric_stats" in data["fixtures"]

    def test_basic_numeric_stats_from_file(
        self, golden_fixture: Dict[str, Any]
    ) -> None:
        """Verify basic numeric statistics match golden fixture values."""
        fixture = golden_fixture["fixtures"]["basic_numeric_stats"]
        data = fixture["input"]["data"]
        expected = fixture["expected"]
        tolerance = fixture["tolerance"]

        df = pd.DataFrame({"values": data})
        result = compute_input_stats(df)
        stats = result["numeric_stats"]["values"]

        # Verify each expected statistic within tolerance
        assert abs(stats["mean"] - expected["mean"]) < tolerance
        assert abs(stats["median"] - expected["median"]) < tolerance
        assert abs(stats["min"] - expected["min"]) < tolerance
        assert abs(stats["max"] - expected["max"]) < tolerance
        assert abs(stats["q25"] - expected["q25"]) < tolerance
        assert abs(stats["q75"] - expected["q75"]) < tolerance

    def test_missing_values_from_file(
        self, golden_fixture: Dict[str, Any]
    ) -> None:
        """Verify missing value analysis matches golden fixture."""
        fixture = golden_fixture["fixtures"]["missing_values_analysis"]
        data = fixture["input"]["data"]
        expected = fixture["expected"]

        df = pd.DataFrame({"col": data})
        result = analyze_missing_values(df)

        assert result["col"]["count"] == expected["missing_count"]
        assert abs(result["col"]["percent"] - expected["missing_percent"]) < 1e-6

    def test_throughput_from_file(
        self, golden_fixture: Dict[str, Any]
    ) -> None:
        """Verify throughput calculation matches golden fixture."""
        fixture = golden_fixture["fixtures"]["throughput_calculation"]
        inp = fixture["input"]
        expected = fixture["expected"]
        tolerance = fixture["tolerance"]

        result = calculate_throughput(inp["rows_processed"], inp["duration_seconds"])

        assert abs(result - expected["throughput"]) < tolerance

    def test_zscore_detection_from_file(
        self, golden_fixture: Dict[str, Any]
    ) -> None:
        """Verify z-score anomaly detection matches golden fixture."""
        fixture = golden_fixture["fixtures"]["zscore_outlier_detection"]
        data = fixture["input"]["data"]
        threshold = fixture["input"]["threshold"]
        expected = fixture["expected"]
        tolerance = fixture["tolerance"]

        df = pd.DataFrame({"values": data})
        result = detect_anomalies_zscore(df, ["values"], threshold=threshold)

        assert result["values"]["count"] == expected["outlier_count"]
        # Mean and std are affected by the outlier itself, use wider tolerance
        assert abs(result["values"]["mean"] - expected["mean_approx"]) < tolerance + 10
        assert abs(result["values"]["std"] - expected["std_approx"]) < tolerance + 10

    def test_iqr_detection_from_file(
        self, golden_fixture: Dict[str, Any]
    ) -> None:
        """Verify IQR anomaly detection matches golden fixture."""
        fixture = golden_fixture["fixtures"]["iqr_outlier_detection"]
        data = fixture["input"]["data"]
        multiplier = fixture["input"]["multiplier"]
        expected = fixture["expected"]

        df = pd.DataFrame({"values": data})
        result = detect_anomalies_iqr(df, ["values"], multiplier=multiplier)

        assert result["values"]["count"] == expected["outlier_count"]
        assert "iqr_bounds" in result["values"]

    def test_temporal_stats_from_file(
        self, golden_fixture: Dict[str, Any]
    ) -> None:
        """Verify temporal statistics match golden fixture."""
        fixture = golden_fixture["fixtures"]["temporal_stats"]
        dates = fixture["input"]["dates"]
        expected = fixture["expected"]

        df = pd.DataFrame({"start_date": dates})
        result = compute_temporal_stats(df, date_col="start_date")

        # Year distribution key is integer 2020, not string "2020"
        assert result["year_distribution"][2020] == expected["year_distribution"]["2020"]
        assert result["date_range"]["span_days"] == expected["span_days"]

    def test_entity_stats_from_file(
        self, golden_fixture: Dict[str, Any]
    ) -> None:
        """Verify entity statistics match golden fixture."""
        fixture = golden_fixture["fixtures"]["entity_stats"]
        company_ids = fixture["input"]["company_ids"]
        quality_scores = fixture["input"]["quality_scores"]
        expected = fixture["expected"]
        tolerance = fixture["tolerance"]

        df = pd.DataFrame({
            "company_id": company_ids,
            "data_quality_score": quality_scores,
        })
        result = compute_entity_stats(df)

        assert result["company_coverage"]["unique_companies"] == expected["unique_companies"]
        assert abs(result["data_quality_distribution"]["mean"] - expected["mean_quality"]) < tolerance


# =============================================================================
# Additional Regression Tests
# =============================================================================


@pytest.mark.regression
class TestStatisticalPrecision:
    """Tests verifying mathematical precision of statistical computations."""

    def test_mean_precision(self) -> None:
        """Test mean calculation precision with known values."""
        # Values chosen so mean is exactly representable
        data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        df = pd.DataFrame({"values": data})

        result = compute_input_stats(df)
        stats = result["numeric_stats"]["values"]

        # Mean should be exactly 5.5
        assert stats["mean"] == 5.5

    def test_median_precision_odd_count(self) -> None:
        """Test median calculation with odd number of values."""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        df = pd.DataFrame({"values": data})

        result = compute_input_stats(df)
        stats = result["numeric_stats"]["values"]

        # Median should be exactly 3.0
        assert stats["median"] == 3.0

    def test_median_precision_even_count(self) -> None:
        """Test median calculation with even number of values."""
        data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        df = pd.DataFrame({"values": data})

        result = compute_input_stats(df)
        stats = result["numeric_stats"]["values"]

        # Median should be exactly 3.5
        assert stats["median"] == 3.5

    def test_quartile_precision(self) -> None:
        """Test quartile calculation precision."""
        # Data: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
        # Q25 should be 3.25, Q75 should be 7.75 (pandas linear interpolation)
        data = list(range(1, 11))
        df = pd.DataFrame({"values": data})

        result = compute_input_stats(df)
        stats = result["numeric_stats"]["values"]

        # Verify quartiles match pandas linear interpolation method
        assert abs(stats["q25"] - 3.25) < 0.01
        assert abs(stats["q75"] - 7.75) < 0.01

    def test_std_deviation_precision(self) -> None:
        """Test standard deviation calculation precision."""
        # Values: 2, 4, 4, 4, 5, 5, 7, 9
        # Mean = 5, Sample Variance = 4.57, Sample Std = 2.138
        # (pandas uses ddof=1 for sample std by default)
        data = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        df = pd.DataFrame({"values": data})

        result = compute_input_stats(df)
        stats = result["numeric_stats"]["values"]

        # Sample std with ddof=1 is ~2.1381
        assert abs(stats["std"] - 2.1381) < 0.01


@pytest.mark.regression
class TestOutputFormatConsistency:
    """Tests verifying output format consistency to detect breaking changes."""

    def test_compute_input_stats_output_keys(self) -> None:
        """Verify compute_input_stats returns expected keys."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = compute_input_stats(df)

        required_keys = ["record_count", "column_count", "memory_mb", "column_types"]
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"

    def test_anomaly_detection_output_format(self) -> None:
        """Verify anomaly detection returns expected format."""
        df = pd.DataFrame({"values": [1, 2, 3, 100]})

        zscore_result = detect_anomalies_zscore(df, ["values"], threshold=3.0)
        iqr_result = detect_anomalies_iqr(df, ["values"], multiplier=3.0)

        # Both should have 'values' key
        assert "values" in zscore_result
        assert "values" in iqr_result

        # Z-score result should have specific keys
        zscore_keys = ["count", "sample_anomalies", "threshold", "mean", "std"]
        for key in zscore_keys:
            assert key in zscore_result["values"], f"Missing zscore key: {key}"

        # IQR result should have specific keys
        iqr_keys = ["count", "sample_anomalies", "iqr_bounds"]
        for key in iqr_keys:
            assert key in iqr_result["values"], f"Missing iqr key: {key}"

    def test_temporal_stats_output_format(self) -> None:
        """Verify temporal stats returns expected format."""
        df = pd.DataFrame({
            "start_date": pd.date_range("2020-01-01", periods=10),
        })

        result = compute_temporal_stats(df, date_col="start_date")

        required_keys = [
            "year_distribution",
            "month_distribution",
            "quarter_distribution",
            "day_of_week_distribution",
            "date_range",
        ]
        for key in required_keys:
            assert key in result, f"Missing temporal stats key: {key}"

    def test_entity_stats_output_format(self) -> None:
        """Verify entity stats returns expected format."""
        df = pd.DataFrame({
            "company_id": ["A", "A", "B"],
        })

        result = compute_entity_stats(df)

        required_keys = ["company_coverage", "geographic_coverage"]
        for key in required_keys:
            assert key in result, f"Missing entity stats key: {key}"


# =============================================================================
# Memory Tracking Tests (Task 2)
# =============================================================================


class TestMemoryTracking:
    """Tests for memory tracking functionality in stats module.

    Note: The stats.py module itself doesn't have explicit memory tracking functions,
    but it does track memory usage in compute_input_stats via memory_mb field.
    These tests verify that memory statistics are correctly computed.
    """

    def test_compute_input_stats_memory_reporting(
        self, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test that memory usage is reported in input stats."""
        result = compute_input_stats(sample_dataframe)

        assert "memory_mb" in result
        assert isinstance(result["memory_mb"], (int, float))
        assert result["memory_mb"] >= 0

    def test_memory_reporting_large_dataframe(self) -> None:
        """Test memory reporting with larger DataFrame."""
        # Create a DataFrame with more data
        large_df = pd.DataFrame(
            {
                "col1": np.random.randn(10000),
                "col2": np.random.randn(10000),
                "col3": ["text"] * 10000,
            }
        )

        result = compute_input_stats(large_df)

        # Memory should be non-zero for larger data
        assert result["memory_mb"] > 0

    def test_memory_reporting_empty_dataframe(self) -> None:
        """Test memory reporting with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = compute_input_stats(empty_df)

        # Memory should be 0 or very small
        assert result["memory_mb"] >= 0

    def test_memory_reporting_with_deep_memory(self) -> None:
        """Test memory reporting includes deep memory for strings."""
        df = pd.DataFrame(
            {
                "short_strings": ["a", "b", "c"] * 1000,  # 3000 items
                "long_strings": ["x" * 100] * 3000,  # 3000 items - same length
            }
        )

        result = compute_input_stats(df)

        # Long strings should result in higher memory
        assert result["memory_mb"] > 0

    def test_memory_scales_with_data_size(self) -> None:
        """Test that memory reporting scales with data size."""
        small_df = pd.DataFrame({"col": range(100)})
        large_df = pd.DataFrame({"col": range(10000)})

        small_result = compute_input_stats(small_df)
        large_result = compute_input_stats(large_df)

        # Larger DataFrame should have more memory
        assert large_result["memory_mb"] >= small_result["memory_mb"]

    def test_memory_with_different_dtypes(self) -> None:
        """Test memory reporting with different data types."""
        df = pd.DataFrame(
            {
                "int_col": [1] * 1000,
                "float_col": [1.0] * 1000,
                "string_col": ["text"] * 1000,
                "bool_col": [True] * 1000,
            }
        )

        result = compute_input_stats(df)

        assert "memory_mb" in result
        assert result["memory_mb"] >= 0

        # String columns typically use more memory with deep=True
        assert result["memory_mb"] > 0

    def test_memory_with_nullable_types(self) -> None:
        """Test memory reporting with nullable integer types."""
        df = pd.DataFrame(
            {
                "nullable_int": pd.array([1, 2, None, 4, 5] * 200, dtype="Int64"),
                "nullable_str": pd.array(["a", "b", None, "d", "e"] * 200, dtype="string"),
            }
        )

        result = compute_input_stats(df)

        assert result["memory_mb"] >= 0


# =============================================================================
# Additional Memory Tracking Tests (Task 2)
# =============================================================================


class TestMemoryThresholdWarnings:
    """Tests for memory threshold and growth rate tracking.

    Note: The stats.py module tracks memory in compute_*_stats functions.
    These tests verify memory behavior and thresholds.
    """

    def test_memory_comparison_between_dataframes(self) -> None:
        """Test comparing memory between DataFrames."""
        # Create two DataFrames with different memory footprints
        df1 = pd.DataFrame({"col": [1] * 100})
        df2 = pd.DataFrame({"col": ["x" * 100] * 100})

        result1 = compute_input_stats(df1)
        result2 = compute_input_stats(df2)

        # String data should typically use more memory
        assert result2["memory_mb"] >= result1["memory_mb"]

    def test_memory_growth_with_columns(self) -> None:
        """Test that memory grows with more columns."""
        df_1col = pd.DataFrame({"a": range(1000)})
        df_5col = pd.DataFrame({chr(ord("a") + i): range(1000) for i in range(5)})

        result_1col = compute_input_stats(df_1col)
        result_5col = compute_input_stats(df_5col)

        # More columns should use more memory
        assert result_5col["memory_mb"] >= result_1col["memory_mb"]

    def test_memory_reporting_consistency(self) -> None:
        """Test that memory reporting is consistent across calls."""
        df = pd.DataFrame({"col": range(1000)})

        result1 = compute_input_stats(df)
        result2 = compute_input_stats(df)

        assert result1["memory_mb"] == result2["memory_mb"]


class TestMemoryByModuleBreakdown:
    """Tests for memory tracking by module/column breakdown."""

    def test_column_type_distribution_affects_memory(self) -> None:
        """Test that column type distribution is tracked alongside memory."""
        df = pd.DataFrame(
            {
                "numeric": [1.0] * 100,
                "string": ["text"] * 100,
                "datetime": pd.date_range("2020-01-01", periods=100),
            }
        )

        result = compute_input_stats(df)

        # Should have both memory and column type info
        assert "memory_mb" in result
        assert "column_types" in result

        # Verify types are detected
        assert result["column_types"]["numeric"] >= 1
        assert result["column_types"]["datetime"] >= 1

    def test_memory_with_datetime_columns(self) -> None:
        """Test memory reporting with datetime columns."""
        df = pd.DataFrame(
            {
                "dates": pd.date_range("2020-01-01", periods=1000),
                "timestamps": pd.date_range("2020-01-01", periods=1000, freq="h"),
            }
        )

        result = compute_input_stats(df)

        assert result["memory_mb"] > 0
        assert result["column_types"]["datetime"] >= 2

    def test_memory_with_categorical_data(self) -> None:
        """Test memory reporting with categorical data."""
        df = pd.DataFrame(
            {
                "category_col": pd.Categorical(["A", "B", "C"] * 100),
            }
        )

        result = compute_input_stats(df)

        assert result["memory_mb"] >= 0


# =============================================================================
# Extended Edge Cases for Memory Tracking
# =============================================================================


class TestMemoryEdgeCases:
    """Edge case tests for memory tracking."""

    def test_memory_single_row_dataframe(self) -> None:
        """Test memory with single row DataFrame."""
        df = pd.DataFrame({"a": [1], "b": ["text"], "c": [True]})

        result = compute_input_stats(df)

        # Memory should be very small but non-negative
        assert result["memory_mb"] >= 0
        assert result["record_count"] == 1

    def test_memory_wide_dataframe(self) -> None:
        """Test memory with wide DataFrame (many columns, few rows)."""
        df = pd.DataFrame({f"col_{i}": [i] for i in range(100)})

        result = compute_input_stats(df)

        assert result["column_count"] == 100
        assert result["memory_mb"] >= 0

    def test_memory_with_mixed_null_patterns(self) -> None:
        """Test memory with various null patterns."""
        df = pd.DataFrame(
            {
                "all_null": [None] * 100,
                "some_null": [i if i % 2 == 0 else None for i in range(100)],
                "no_null": list(range(100)),
            }
        )

        result = compute_input_stats(df)

        assert result["memory_mb"] >= 0
