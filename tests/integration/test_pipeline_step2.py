"""
Integration tests for Step 2 (Text Processing).
Tests end-to-end pipeline execution for text processing scripts.
"""

import pytest
import subprocess
import json
from pathlib import Path
import pandas as pd

pytestmark = pytest.mark.integration

from f1d.shared.path_utils import get_latest_output_dir, OutputResolutionError


@pytest.fixture(scope="session")
def repo_root():
    """Path to repository root directory."""
    return Path(__file__).parent.parent.parent


def resolve_output_dir(base_path: Path) -> Path:
    """Resolve output directory using timestamp or fallback to /latest/."""
    try:
        return get_latest_output_dir(base_path)
    except OutputResolutionError:
        return base_path / "latest"


def test_step2_full_pipeline(repo_root, subprocess_env):
    """Test Step 2 (2.1_TokenizeAndCount) runs end-to-end."""
    # Arrange
    script_path = repo_root / "2_Scripts/2_Text/2.1_TokenizeAndCount.py"

    if not script_path.exists():
        pytest.skip(f"Script not found: {script_path}")

    # Act - Run script via subprocess
    result = subprocess.run(
        ["python", str(script_path)],
        env=subprocess_env,
        capture_output=True,
        text=True,
        timeout=600,  # 10 minute timeout
    )

    # Assert
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    # Verify output files exist
    output_dir = resolve_output_dir(
        repo_root / "outputs/2_Textual_Analysis/2.1_Tokenized"
    )
    assert output_dir.exists(), "Output directory not created"

    # Check for expected output files (one per year)
    expected_files = [f"linguistic_counts_{year}.parquet" for year in range(2002, 2019)]

    for filename in expected_files:
        file_path = output_dir / filename
        if not file_path.exists():
            pytest.fail(f"Expected output file not found: {filename}")


def test_output_file_format_step2(repo_root):
    """Test that output files have correct schema."""
    # Arrange
    output_file = (
        resolve_output_dir(repo_root / "outputs/2_Textual_Analysis/2.1_Tokenized")
        / "linguistic_counts_2002.parquet"
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


def test_word_count_validation_step2(repo_root):
    """Test that word counts are reasonable."""
    # Arrange
    output_file = (
        resolve_output_dir(repo_root / "outputs/2_Textual_Analysis/2.1_Tokenized")
        / "linguistic_counts_2002.parquet"
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
def test_step2_multiple_years(year, repo_root):
    """Test Step 2 output for specific years."""
    # Arrange
    output_file = (
        resolve_output_dir(repo_root / "outputs/2_Textual_Analysis/2.1_Tokenized")
        / f"linguistic_counts_{year}.parquet"
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
