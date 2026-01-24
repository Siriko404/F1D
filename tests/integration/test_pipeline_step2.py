"""
Integration tests for Step 2 (Text Processing).
Tests end-to-end pipeline execution for text processing scripts.
"""

import os
import pytest
import subprocess
import json
from pathlib import Path
import pandas as pd

# Get repository root from test file location
REPO_ROOT = Path(__file__).parent.parent.parent

# Environment for subprocess calls (includes PYTHONPATH for module resolution)
SUBPROCESS_ENV = {
    "PYTHONPATH": str(REPO_ROOT / "2_Scripts"),
    **os.environ,  # Preserve existing environment variables
}

pytestmark = pytest.mark.integration


def test_step2_full_pipeline():
    """Test Step 2 (2.1_TokenizeAndCount) runs end-to-end."""
    # Arrange
    script_path = REPO_ROOT / "2_Scripts/2_Text/2.1_TokenizeAndCount.py"

    if not script_path.exists():
        pytest.skip(f"Script not found: {script_path}")

    # Act - Run script via subprocess
    result = subprocess.run(
        ["python", str(script_path)],
        env=SUBPROCESS_ENV,
        capture_output=True,
        text=True,
        timeout=600,  # 10 minute timeout
    )

    # Assert
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    # Verify output files exist
    output_dir = REPO_ROOT / "4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest"
    assert output_dir.exists(), "Output directory not created"

    # Check for expected output files (one per year)
    expected_files = [f"linguistic_counts_{year}.parquet" for year in range(2002, 2019)]

    for filename in expected_files:
        file_path = output_dir / filename
        if not file_path.exists():
            pytest.fail(f"Expected output file not found: {filename}")


def test_output_file_format_step2():
    """Test that output files have correct schema."""
    # Arrange
    output_file = (
        REPO_ROOT
        / "4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/linguistic_counts_2002.parquet"
    )

    if not output_file.exists():
        pytest.skip("Run 2.1_TokenizeAndCount.py first")

    # Act
    df = pd.read_parquet(output_file)

    # Assert - Verify required columns exist
    required_columns = ["file_name", "Total_Words", "MaQaUnc_Words"]
    for col in required_columns:
        assert col in df.columns, f"Missing required column: {col}"

    # Verify data types
    assert df["file_name"].dtype == "object", "file_name should be object type"
    assert df["Total_Words"].dtype in ["int64", "int32"], (
        "Total_Words should be integer type"
    )

    # Verify no negative word counts
    assert (df["Total_Words"] >= 0).all(), "Word counts should be non-negative"


def test_word_count_validation_step2():
    """Test that word counts are reasonable."""
    # Arrange
    output_file = (
        REPO_ROOT
        / "4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/linguistic_counts_2002.parquet"
    )

    if not output_file.exists():
        pytest.skip("Run 2.1_TokenizeAndCount.py first")

    # Act
    df = pd.read_parquet(output_file)

    # Assert - Verify reasonable word count ranges
    assert df["Total_Words"].min() >= 0, "Minimum word count should be >= 0"
    assert df["Total_Words"].max() > 100, "Maximum word count should be > 100"

    # Verify uncertainty word counts are subset of total words
    assert (df["MaQaUnc_Words"] <= df["Total_Words"]).all(), (
        "Uncertainty words should be <= total words"
    )


@pytest.mark.parametrize("year", [2002, 2010, 2018])
def test_step2_multiple_years(year):
    """Test Step 2 output for specific years."""
    # Arrange
    output_file = (
        REPO_ROOT
        / f"4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/linguistic_counts_{year}.parquet"
    )

    if not output_file.exists():
        pytest.skip(f"Run 2.1_TokenizeAndCount.py first (year {year} not found)")

    # Act
    df = pd.read_parquet(output_file)

    # Assert - Verify file has data
    assert len(df) > 0, f"Output file for year {year} is empty"

    # Verify required columns
    required_columns = ["file_name", "Total_Words"]
    for col in required_columns:
        assert col in df.columns, f"Missing required column: {col}"
