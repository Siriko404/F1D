"""
Unit tests for regression_helpers.py functions.

Tests:
- build_regression_sample() with various filter configurations
- _check_missing_values() for missing value detection
- _assign_industry_codes() for FF12/FF48 industry classification

Run with: pytest tests/unit/test_regression_helpers.py -v
"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path

from f1d.shared.regression_helpers import (
    build_regression_sample,
    _check_missing_values,
    _assign_industry_codes,
)


class TestCheckMissingValues:
    """Tests for _check_missing_values() helper function."""

    def test_no_missing_values(self):
        """Test with complete data - no missing values."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3],
                "x1": [4, 5, 6],
                "c1": [7, 8, 9],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["x1"],
            "controls": ["c1"],
        }

        result = _check_missing_values(df, required_vars)

        assert result == {}, "Should return empty dict when no missing values"

    def test_missing_values_in_some_columns(self):
        """Test with missing values in some columns."""
        df = pd.DataFrame(
            {
                "y": [1, None, 3],
                "x1": [4, 5, 6],
                "c1": [7, 8, None],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["x1"],
            "controls": ["c1"],
        }

        result = _check_missing_values(df, required_vars)

        assert "y" in result, "Should detect missing values in 'y'"
        assert result["y"] == 1, "Should count 1 missing value in 'y'"
        assert "c1" in result, "Should detect missing values in 'c1'"
        assert result["c1"] == 1, "Should count 1 missing value in 'c1'"
        assert "x1" not in result, "Should not include columns with no missing values"

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame(columns=["y", "x1", "c1"])

        required_vars = {
            "dependent": ["y"],
            "independent": ["x1"],
            "controls": ["c1"],
        }

        result = _check_missing_values(df, required_vars)

        assert result == {}, "Should return empty dict for empty DataFrame"

    def test_columns_not_in_dataframe(self):
        """Test with required columns not in DataFrame."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3],
                "x1": [4, 5, 6],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["x1"],
            "controls": ["c1"],  # This column doesn't exist
        }

        result = _check_missing_values(df, required_vars)

        # Should only check columns that exist in DataFrame
        assert "c1" not in result, "Should not check columns not in DataFrame"
        assert len(result) == 0, (
            "Should return empty dict when no existing columns have missing values"
        )

    def test_return_type_is_dict_of_ints(self):
        """Test that return type is dict of missing value counts."""
        df = pd.DataFrame(
            {
                "y": [1, None, None, 4],
                "x1": [1, 2, 3, 4],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["x1"],
            "controls": [],
        }

        result = _check_missing_values(df, required_vars)

        assert isinstance(result, dict), "Should return a dictionary"
        if "y" in result:
            assert isinstance(result["y"], int), "Missing counts should be integers"


class TestAssignIndustryCodes:
    """Tests for _assign_industry_codes() helper function."""

    def test_classification_none_skips_assignment(self):
        """Test with classification=None - should skip assignment."""
        df = pd.DataFrame(
            {
                "sic": [1234, 5678, 9123],
                "y": [1, 2, 3],
            }
        )

        result = _assign_industry_codes(df, "sic", classification=None)

        assert "industry_code" not in result.columns, (
            "Should not add industry_code column"
        )
        assert len(result) == len(df), "Should return same number of rows"

    def test_missing_sic_column_skips_assignment(self):
        """Test with missing SIC column - should skip assignment."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3],
                "x1": [4, 5, 6],
            }
        )

        # Try to assign codes with non-existent SIC column
        result = _assign_industry_codes(df, "sic", classification="FF12")

        assert "industry_code" not in result.columns, (
            "Should not add industry_code column"
        )
        assert len(result) == len(df), "Should return same number of rows"

    def test_unsupported_classification_raises_error(self):
        """Test that unsupported classification raises ValueError."""
        df = pd.DataFrame(
            {
                "sic": [1234, 5678],
                "y": [1, 2],
            }
        )

        with pytest.raises(ValueError, match="Unsupported classification"):
            _assign_industry_codes(df, "sic", classification="INVALID")


class TestBuildRegressionSample:
    """Tests for build_regression_sample() function."""

    def test_empty_filter_configuration(self):
        """Test with empty filter configuration."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3, 4, 5],
                "x1": [10, 20, 30, 40, 50],
                "sic": [1234, 5678, 9123, 3456, 7890],
                "year": [2020, 2021, 2022, 2020, 2021],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["x1"],
            "controls": [],
        }

        result = build_regression_sample(
            df,
            required_vars,
            filters=None,
            min_sample_size=5,
            industry_classification=None,
        )

        assert len(result) == len(df), "Should return all rows when no filters"
        assert "y" in result.columns, "Should keep dependent variable"
        assert "x1" in result.columns, "Should keep independent variable"

    def test_eq_filter_exact_match(self):
        """Test with eq filter (exact match)."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3, 4, 5],
                "category": ["A", "B", "A", "B", "A"],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["category"],
            "controls": [],
        }

        filters = [{"column": "category", "operation": "eq", "value": "A"}]

        result = build_regression_sample(
            df,
            required_vars,
            filters=filters,
            min_sample_size=3,
            industry_classification=None,
        )

        assert len(result) == 3, "Should filter to 3 rows where category == 'A'"
        assert all(result["category"] == "A"), "All rows should have category 'A'"

    def test_gt_lt_filters_range(self):
        """Test with gt/lt filters (range filters)."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3, 4, 5],
                "value": [10, 20, 30, 40, 50],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["value"],
            "controls": [],
        }

        filters = [
            {"column": "value", "operation": "gt", "value": 15},
            {"column": "value", "operation": "lt", "value": 45},
        ]

        result = build_regression_sample(
            df,
            required_vars,
            filters=filters,
            min_sample_size=3,
            industry_classification=None,
        )

        assert len(result) == 3, "Should filter to 3 rows where value > 15 and < 45"
        assert all(result["value"] > 15), "All values should be > 15"
        assert all(result["value"] < 45), "All values should be < 45"

    def test_in_not_in_filters_list(self):
        """Test with in/not_in filters (list filters)."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3, 4, 5],
                "category": ["A", "B", "C", "D", "E"],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["category"],
            "controls": [],
        }

        filters = [{"column": "category", "operation": "in", "value": ["A", "B", "C"]}]

        result = build_regression_sample(
            df,
            required_vars,
            filters=filters,
            min_sample_size=3,
            industry_classification=None,
        )

        assert len(result) == 3, (
            "Should filter to 3 rows where category in ['A', 'B', 'C']"
        )
        assert set(result["category"]) == {"A", "B", "C"}, (
            "Categories should match list"
        )

    def test_year_range_filter(self):
        """Test with year_range filter."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3, 4, 5],
                "year": [2019, 2020, 2021, 2022, 2023],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": [],
            "controls": [],
        }

        result = build_regression_sample(
            df,
            required_vars,
            filters=None,
            year_range=(2020, 2022),
            min_sample_size=3,
            industry_classification=None,
        )

        assert len(result) == 3, "Should filter to 3 rows where year between 2020-2022"
        assert all(result["year"] >= 2020), "All years should be >= 2020"
        assert all(result["year"] <= 2022), "All years should be <= 2022"

    def test_missing_values_in_required_variables(self):
        """Test with missing values in required variables."""
        df = pd.DataFrame(
            {
                "y": [1, None, 3, 4, 5],
                "x1": [10, 20, None, 40, 50],
                "sic": [1234, 5678, 9123, 3456, 7890],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["x1"],
            "controls": [],
        }

        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = build_regression_sample(
                df, required_vars, min_sample_size=5, industry_classification=None
            )

            # Should warn about missing values
            warning_messages = [str(warning.message) for warning in w]
            assert any("Missing values" in msg for msg in warning_messages), (
                "Should warn about missing values"
            )

        # Missing values should still be in result (function warns, doesn't drop)
        assert len(result) == len(df), (
            "Should keep rows with missing values (just warns)"
        )

    def test_min_sample_size_validation(self):
        """Test that min_sample_size is validated."""
        df = pd.DataFrame(
            {
                "y": [1, 2],
                "x1": [10, 20],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["x1"],
            "controls": [],
        }

        # Set min_sample_size higher than available
        # RegressionValidationError is a custom exception
        from f1d.shared.regression_validation import RegressionValidationError

        with pytest.raises(
            RegressionValidationError, match="Insufficient observations"
        ):
            build_regression_sample(
                df,
                required_vars,
                min_sample_size=100,
                industry_classification=None,
            )

    def test_max_sample_size_with_random_sampling(self):
        """Test max_sample_size with random sampling."""
        df = pd.DataFrame(
            {
                "y": list(range(100)),
                "x1": list(range(100, 200)),
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["x1"],
            "controls": [],
        }

        result = build_regression_sample(
            df,
            required_vars,
            max_sample_size=10,
            random_seed=42,  # For reproducibility
            min_sample_size=5,
            industry_classification=None,
        )

        assert len(result) == 10, "Should sample down to max_sample_size"

    def test_missing_required_columns_raises_error(self):
        """Test that missing required columns raises ValueError."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3],
                "x1": [10, 20, 30],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["x1", "missing_col"],  # This column doesn't exist
            "controls": [],
        }

        with pytest.raises(ValueError, match="Missing required columns"):
            build_regression_sample(
                df, required_vars, min_sample_size=3, industry_classification=None
            )

    def test_invalid_required_vars_structure_raises_error(self):
        """Test that invalid required_vars structure raises ValueError."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3],
                "x1": [10, 20, 30],
            }
        )

        # Pass list instead of dict
        with pytest.raises(ValueError, match="must be a dictionary"):
            build_regression_sample(
                df, ["y", "x1"], min_sample_size=3, industry_classification=None
            )

        # Pass non-list values
        with pytest.raises(ValueError, match="must be a list"):
            build_regression_sample(
                df,
                {"dependent": "y", "independent": ["x1"]},
                min_sample_size=3,
                industry_classification=None,
            )

    def test_unsupported_filter_operation_raises_error(self):
        """Test that unsupported filter operation raises ValueError."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3],
                "value": [10, 20, 30],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["value"],
            "controls": [],
        }

        filters = [{"column": "value", "operation": "invalid_op", "value": 15}]

        with pytest.raises(ValueError, match="Unsupported filter operation"):
            build_regression_sample(
                df,
                required_vars,
                filters=filters,
                min_sample_size=3,
                industry_classification=None,
            )

    def test_year_range_without_year_column_warns(self):
        """Test year_range filter without year column issues warning."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3],
                "value": [10, 20, 30],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["value"],
            "controls": [],
        }

        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = build_regression_sample(
                df,
                required_vars,
                year_range=(2020, 2022),
                min_sample_size=3,
                industry_classification=None,
            )

            # Should warn about missing year column
            warning_messages = [str(warning.message) for warning in w]
            assert any("year" in msg and "column" in msg for msg in warning_messages), (
                "Should warn about missing year column"
            )

    def test_ge_le_filters_inclusive(self):
        """Test ge/le filters (inclusive bounds)."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3, 4, 5],
                "value": [10, 20, 30, 40, 50],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["value"],
            "controls": [],
        }

        filters = [
            {"column": "value", "operation": "ge", "value": 20},
            {"column": "value", "operation": "le", "value": 40},
        ]

        result = build_regression_sample(
            df,
            required_vars,
            filters=filters,
            min_sample_size=3,
            industry_classification=None,
        )

        assert len(result) == 3, "Should filter to 3 rows where value >= 20 and <= 40"
        assert all(result["value"] >= 20), "All values should be >= 20"
        assert all(result["value"] <= 40), "All values should be <= 40"

    def test_ne_filter_not_equal(self):
        """Test ne filter (not equal)."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3, 4, 5],
                "category": ["A", "B", "A", "B", "A"],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["category"],
            "controls": [],
        }

        filters = [{"column": "category", "operation": "ne", "value": "A"}]

        result = build_regression_sample(
            df,
            required_vars,
            filters=filters,
            min_sample_size=2,
            industry_classification=None,
        )

        assert len(result) == 2, "Should filter to 2 rows where category != 'A'"
        assert all(result["category"] != "A"), "All rows should not have category 'A'"

    def test_not_in_filter_excludes_list(self):
        """Test not_in filter (excludes values in list)."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3, 4, 5],
                "category": ["A", "B", "C", "D", "E"],
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["category"],
            "controls": [],
        }

        filters = [
            {"column": "category", "operation": "not_in", "value": ["A", "B", "C"]}
        ]

        result = build_regression_sample(
            df,
            required_vars,
            filters=filters,
            min_sample_size=2,
            industry_classification=None,
        )

        assert len(result) == 2, (
            "Should filter to 2 rows where category not in ['A', 'B', 'C']"
        )
        assert set(result["category"]) == {"D", "E"}, "Categories should be ['D', 'E']"

    def test_multiple_filters_combined(self):
        """Test multiple filters applied sequentially."""
        df = pd.DataFrame(
            {
                "y": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "category": ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"],
                "value": list(range(10, 110, 10)),
                "year": [2020] * 5 + [2021] * 5,
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["category", "value"],
            "controls": [],
        }

        filters = [
            {"column": "category", "operation": "eq", "value": "A"},
            {"column": "value", "operation": "gt", "value": 20},
            {"column": "value", "operation": "lt", "value": 80},
        ]

        result = build_regression_sample(
            df,
            required_vars,
            filters=filters,
            year_range=(2020, 2020),
            min_sample_size=2,
            industry_classification=None,
        )

        # Should filter: category == 'A', value > 20 and < 80, year == 2020
        assert len(result) == 2, "Should apply all filters sequentially"
        assert all(result["category"] == "A"), "All rows should have category 'A'"
        assert all(result["value"] > 20), "All values should be > 20"
        assert all(result["value"] < 80), "All values should be < 80"
        assert all(result["year"] == 2020), "All rows should be from year 2020"

    def test_deterministic_behavior(self):
        """Test that function is deterministic with same inputs."""
        df = pd.DataFrame(
            {
                "y": list(range(100)),
                "x1": list(range(100, 200)),
                "sic": [1234] * 100,
            }
        )

        required_vars = {
            "dependent": ["y"],
            "independent": ["x1"],
            "controls": [],
        }

        result1 = build_regression_sample(
            df,
            required_vars,
            max_sample_size=10,
            random_seed=42,
            min_sample_size=5,
            industry_classification=None,
        )

        result2 = build_regression_sample(
            df,
            required_vars,
            max_sample_size=10,
            random_seed=42,
            min_sample_size=5,
            industry_classification=None,
        )

        assert result1.equals(result2), (
            "Same input with same seed should produce identical output"
        )
