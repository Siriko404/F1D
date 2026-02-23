"""Unit tests for make_summary_stats_table utility."""

import pandas as pd
import numpy as np
from pathlib import Path
import tempfile

import pytest

from f1d.shared.latex_tables_accounting import make_summary_stats_table


class TestMakeSummaryStatsTable:
    """Test suite for summary statistics table generation."""

    def test_basic_functionality(self):
        """Test basic stats computation with valid data."""
        df = pd.DataFrame({
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
            "y": [10.0, 20.0, 30.0, 40.0, 50.0],
        })
        vars = [{"col": "x", "label": "X"}, {"col": "y", "label": "Y"}]

        result = make_summary_stats_table(df, vars)

        assert len(result) == 2
        assert result[result["Col"] == "x"]["Mean"].values[0] == 3.0
        assert result[result["Col"] == "x"]["SD"].values[0] == np.std([1, 2, 3, 4, 5], ddof=1)

    def test_missing_variable_handling(self):
        """Test that missing variables are skipped with warning."""
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
        vars = [
            {"col": "x", "label": "X"},
            {"col": "nonexistent", "label": "Missing"},
        ]

        with pytest.warns(UserWarning, match="not found"):
            result = make_summary_stats_table(df, vars)

        assert len(result) == 1
        assert "nonexistent" not in result["Col"].values

    def test_nan_handling(self):
        """Test NaN values are excluded from statistics."""
        df = pd.DataFrame({"x": [1.0, np.nan, 3.0, 4.0, 5.0]})
        vars = [{"col": "x", "label": "X"}]

        result = make_summary_stats_table(df, vars)

        assert result[result["Col"] == "x"]["N"].values[0] == 4
        assert result[result["Col"] == "x"]["Mean"].values[0] == 3.25

    def test_zero_sd_variable(self):
        """Test constant variable (zero SD) is handled correctly."""
        df = pd.DataFrame({"x": [5.0, 5.0, 5.0, 5.0]})
        vars = [{"col": "x", "label": "X"}]

        result = make_summary_stats_table(df, vars)

        assert result[result["Col"] == "x"]["SD"].values[0] == 0.0
        assert result[result["Col"] == "x"]["Mean"].values[0] == 5.0

    def test_per_sample_breakdown(self):
        """Test per-sample statistics computation."""
        df = pd.DataFrame({
            "x": [1.0, 2.0, 3.0, 10.0, 20.0],
            "sample": ["Main", "Main", "Main", "Finance", "Finance"],
        })
        vars = [{"col": "x", "label": "X"}]

        result = make_summary_stats_table(df, vars, sample_names=["Main", "Finance"])

        assert len(result) == 2
        main_row = result[result["Sample"] == "Main"]
        finance_row = result[result["Sample"] == "Finance"]
        assert main_row["Mean"].values[0] == 2.0
        assert finance_row["Mean"].values[0] == 15.0

    def test_empty_dataframe(self):
        """Test empty DataFrame returns empty result with correct columns."""
        df = pd.DataFrame()
        vars = [{"col": "x", "label": "X"}]

        result = make_summary_stats_table(df, vars)

        assert len(result) == 0
        assert "Variable" in result.columns
        assert "N" in result.columns
        assert "Mean" in result.columns

    def test_csv_output(self):
        """Test CSV file is created correctly."""
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
        vars = [{"col": "x", "label": "X"}]

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            result = make_summary_stats_table(df, vars, output_csv=csv_path)

            assert csv_path.exists()
            loaded = pd.read_csv(csv_path)
            assert len(loaded) == 1

    def test_latex_output(self):
        """Test LaTeX file is created and contains expected elements."""
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
        vars = [{"col": "x", "label": "X"}]

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = Path(tmpdir) / "test.tex"
            result = make_summary_stats_table(df, vars, output_tex=tex_path)

            assert tex_path.exists()
            content = tex_path.read_text()
            assert "\\begin{table}" in content
            assert "\\toprule" in content
            assert "\\bottomrule" in content
            assert "X" in content

    def test_all_nan_variable(self):
        """Test variable with all NaN values reports N=0 and NaN stats."""
        df = pd.DataFrame({
            "x": [1.0, 2.0, 3.0],
            "y": [np.nan, np.nan, np.nan],
        })
        vars = [{"col": "y", "label": "Y"}]

        result = make_summary_stats_table(df, vars)

        assert result[result["Col"] == "y"]["N"].values[0] == 0
        assert np.isnan(result[result["Col"] == "y"]["Mean"].values[0])

    def test_sample_col_parameter(self):
        """Test that sample_col parameter is respected."""
        df = pd.DataFrame({
            "x": [1.0, 2.0, 10.0, 20.0],
            "group": ["A", "A", "B", "B"],
        })
        vars = [{"col": "x", "label": "X"}]

        result = make_summary_stats_table(
            df, vars, sample_names=["A", "B"], sample_col="group"
        )

        assert len(result) == 2
        a_row = result[result["Sample"] == "A"]
        b_row = result[result["Sample"] == "B"]
        assert a_row["Mean"].values[0] == 1.5
        assert b_row["Mean"].values[0] == 15.0

    def test_sample_names_none_aggregates_all(self):
        """Test that sample_names=None produces single aggregate table."""
        df = pd.DataFrame({
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
            "sample": ["Main", "Main", "Main", "Finance", "Finance"],
        })
        vars = [{"col": "x", "label": "X"}]

        result = make_summary_stats_table(df, vars, sample_names=None)

        assert len(result) == 1
        # All observations aggregated
        assert result["N"].values[0] == 5
        assert result["Mean"].values[0] == 3.0

    def test_quantile_computation(self):
        """Test that quantiles are computed correctly."""
        df = pd.DataFrame({"x": list(range(1, 101))})  # 1 to 100
        vars = [{"col": "x", "label": "X"}]

        result = make_summary_stats_table(df, vars)

        x_row = result[result["Col"] == "x"]
        assert x_row["Min"].values[0] == 1.0
        assert x_row["P25"].values[0] == 25.75
        assert x_row["Median"].values[0] == 50.5
        assert x_row["P75"].values[0] == 75.25
        assert x_row["Max"].values[0] == 100.0

    def test_latex_caption_and_label(self):
        """Test that caption and label appear in LaTeX output."""
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
        vars = [{"col": "x", "label": "X"}]

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = Path(tmpdir) / "test.tex"
            result = make_summary_stats_table(
                df, vars,
                output_tex=tex_path,
                caption="My Custom Caption",
                label="tab:my_label",
            )

            content = tex_path.read_text()
            assert "My Custom Caption" in content
            assert "tab:my_label" in content

    def test_decimal_formatting(self):
        """Test that decimals parameter affects output precision."""
        df = pd.DataFrame({"x": [1.23456789]})
        vars = [{"col": "x", "label": "X"}]

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = Path(tmpdir) / "test.tex"
            result = make_summary_stats_table(
                df, vars, output_tex=tex_path, decimals=2
            )

            content = tex_path.read_text()
            # With decimals=2, mean should be 1.23
            assert "1.23" in content

    def test_latex_panel_structure(self):
        """Test that multi-sample output has panel structure."""
        df = pd.DataFrame({
            "x": [1.0, 2.0, 10.0, 20.0],
            "sample": ["Main", "Main", "Finance", "Finance"],
        })
        vars = [{"col": "x", "label": "X"}]

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = Path(tmpdir) / "test.tex"
            result = make_summary_stats_table(
                df, vars,
                sample_names=["Main", "Finance"],
                output_tex=tex_path,
            )

            content = tex_path.read_text()
            assert "Panel A: Main Sample" in content
            assert "Panel B: Finance Sample" in content

    def test_variable_label_used_in_output(self):
        """Test that variable labels appear in output, not column names."""
        df = pd.DataFrame({"long_column_name_xyz": [1.0, 2.0, 3.0]})
        vars = [{"col": "long_column_name_xyz", "label": "Short Label"}]

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = Path(tmpdir) / "test.tex"
            result = make_summary_stats_table(df, vars, output_tex=tex_path)

            content = tex_path.read_text()
            assert "Short Label" in content
