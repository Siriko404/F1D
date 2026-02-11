"""
Unit tests for calculate_throughput function.
Tests verify division-by-zero handling and edge cases.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))
from shared.observability_utils import calculate_throughput


def test_valid_duration_returns_correct_throughput():
    """Test that valid inputs return correct throughput."""
    result = calculate_throughput(1000, 10.0)
    assert result == 100.0  # 1000 / 10 = 100


def test_valid_duration_rounds_to_two_decimals():
    """Test that throughput is rounded to 2 decimal places."""
    result = calculate_throughput(1000, 7.0)
    assert result == 142.86  # 1000 / 7 = 142.857..., rounded


def test_zero_duration_raises_value_error():
    """Test that duration_seconds=0 raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        calculate_throughput(1000, 0.0)

    error_msg = str(exc_info.value)
    assert "duration_seconds=0" in error_msg
    assert "rows_processed=1000" in error_msg
    assert "timing logic" in error_msg.lower()


def test_negative_duration_raises_value_error():
    """Test that negative duration_seconds raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        calculate_throughput(500, -1.5)

    error_msg = str(exc_info.value)
    assert "duration_seconds=-1.5" in error_msg
    assert "rows_processed=500" in error_msg


def test_zero_rows_zero_duration_raises():
    """Test edge case: both inputs are zero."""
    with pytest.raises(ValueError):
        calculate_throughput(0, 0.0)


def test_large_values_handled_correctly():
    """Test that large values are handled without overflow."""
    result = calculate_throughput(1_000_000, 100.0)
    assert result == 10000.0


def test_small_values_handled_correctly():
    """Test that very small durations work correctly."""
    result = calculate_throughput(100, 0.001)
    assert result == 100000.0


def test_zero_rows_positive_duration():
    """Test edge case: zero rows processed with valid duration."""
    result = calculate_throughput(0, 10.0)
    assert result == 0.0


def test_single_row():
    """Test single row processed."""
    result = calculate_throughput(1, 1.0)
    assert result == 1.0


def test_error_message_contains_start_time_end_time_hint():
    """Test that error message includes hint about start_time/end_time."""
    with pytest.raises(ValueError) as exc_info:
        calculate_throughput(100, 0.0)

    error_msg = str(exc_info.value)
    assert "start_time/end_time" in error_msg
