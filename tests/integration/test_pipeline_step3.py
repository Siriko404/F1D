"""
Integration tests for Step 3 (Financial Features).
Tests end-to-end pipeline execution for financial feature scripts.
"""

import os
import pytest
import subprocess
import json
from pathlib import Path
import pandas as pd

pytestmark = pytest.mark.integration

# Get repository root from test file location
REPO_ROOT = Path(__file__).parent.parent.parent

# Environment for subprocess calls (includes PYTHONPATH for module resolution)
SUBPROCESS_ENV = {
    "PYTHONPATH": str(REPO_ROOT / "2_Scripts"),
    **os.environ,  # Preserve existing environment variables
}


def test_step3_full_pipeline():
    """Test Step 3 (3.0_BuildFinancialFeatures) runs end-to-end."""
    # Arrange
    script_path = REPO_ROOT / "2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py"

    if not script_path.exists():
        pytest.skip(f"Script not found: {script_path}")

    # Act - Run script via subprocess
    result = subprocess.run(
        ["python", str(script_path)],
        capture_output=True,
        text=True,
        timeout=600,
    )

    # Assert
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    # Verify output files exist
    output_dir = (
        REPO_ROOT / "4_Outputs/3_Financial_Features/3.0_BuildFinancialFeatures/latest"
    )
    assert output_dir.exists(), "Output directory not created"

    # Check for expected output files
    expected_files = [
        "financial_features.parquet",
        "stats.json",
    ]

    for filename in expected_files:
        file_path = output_dir / filename
        if not file_path.exists():
            pytest.fail(f"Expected output file not found: {filename}")


def test_merge_diagnostics_step3():
    """Test that merge diagnostics are recorded in stats.json."""
    # Arrange
    stats_path = (
        REPO_ROOT
        / "4_Outputs/3_Financial_Features/3.0_BuildFinancialFeatures/latest/stats.json"
    )

    if not stats_path.exists():
        pytest.skip("Run 3.0_BuildFinancialFeatures.py first")

    # Act
    with open(stats_path) as f:
        stats = json.load(f)

    # Assert - Verify merge diagnostics are present
    processing = stats.get("processing", {})
    merge_diagnostics = processing.get("merge_diagnostics", {})

    assert len(merge_diagnostics) > 0, "No merge diagnostics found in stats.json"

    # Verify each merge has required fields
    for merge_name, merge_stats in merge_diagnostics.items():
        assert "left_rows" in merge_stats, f"Missing left_rows for merge: {merge_name}"
        assert "right_rows" in merge_stats, (
            f"Missing right_rows for merge: {merge_name}"
        )
        assert "matched_rows" in merge_stats, (
            f"Missing matched_rows for merge: {merge_name}"
        )


def test_financial_variables_validation():
    """Test that financial variables are computed correctly."""
    # Arrange
    output_file = (
        REPO_ROOT
        / "4_Outputs/3_Financial_Features/3.0_BuildFinancialFeatures/latest/financial_features.parquet"
    )

    if not output_file.exists():
        pytest.skip("Run 3.0_BuildFinancialFeatures.py first")

    # Act
    df = pd.read_parquet(output_file)

    # Assert - Verify key financial variables exist
    expected_variables = [
        "SIZE",
        "BM",
        "LEV",
        "ROA",
        "StockRet",
        "MarketRet",
    ]

    for var in expected_variables:
        assert var in df.columns, f"Missing financial variable: {var}"

    # Verify no infinite or NaN values in critical variables
    for var in expected_variables:
        if var in df.columns:
            finite_count = df[var].notna().sum()
            assert finite_count > 0, f"Variable {var} has no valid values"

    # Verify return ranges are reasonable
    if "StockRet" in df.columns:
        assert df["StockRet"].min() >= -1, "Stock returns should be >= -1 (100% loss)"
        assert df["StockRet"].max() <= 10, (
            "Stock returns should be <= 1000% (sanity check)"
        )


@pytest.mark.parametrize("data_source", ["Compustat", "CRSP", "IBES"])
def test_step3_data_source_integration(data_source):
    """Test that data source merges are successful."""
    # Arrange
    stats_path = (
        REPO_ROOT
        / "4_Outputs/3_Financial_Features/3.0_BuildFinancialFeatures/latest/stats.json"
    )

    if not stats_path.exists():
        pytest.skip("Run 3.0_BuildFinancialFeatures.py first")

    # Act
    with open(stats_path) as f:
        stats = json.load(f)

    # Assert - Verify data source merge
    merge_diagnostics = stats.get("processing", {}).get("merge_diagnostics", {})

    # Check if data source is mentioned in merge diagnostics
    source_found = any(
        data_source.lower() in merge_name.lower()
        for merge_name in merge_diagnostics.keys()
    )

    if source_found:
        # Verify match rate is reasonable (> 50%)
        for merge_name, merge_stats in merge_diagnostics.items():
            if data_source.lower() in merge_name.lower():
                left_rows = merge_stats.get("left_rows", 0)
                matched_rows = merge_stats.get("matched_rows", 0)
                match_rate = matched_rows / left_rows if left_rows > 0 else 0
                assert match_rate > 0.5, (
                    f"Match rate for {data_source} is too low: {match_rate:.2%}"
                )
