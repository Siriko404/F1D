"""
Regression tests for output stability.
Tests detect regressions by comparing SHA-256 checksums of output files to baseline.
"""

import pytest
import hashlib
import pandas as pd
from pathlib import Path
import json

from f1d.shared.path_utils import get_latest_output_dir, OutputResolutionError


# Get repository root from test file location
REPO_ROOT = Path(__file__).parent.parent.parent


def resolve_output_dir(base_path: Path) -> Path:
    """Resolve output directory using timestamp or fallback to /latest/."""
    try:
        return get_latest_output_dir(base_path)
    except OutputResolutionError:
        return base_path / "latest"


pytestmark = pytest.mark.regression  # Mark all tests in this file as regression


def compute_dataframe_checksum(df: pd.DataFrame) -> str:
    """Compute SHA-256 checksum of a DataFrame."""
    return hashlib.sha256(
        pd.util.hash_pandas_object(df, index=False).values.tobytes()
    ).hexdigest()


def compute_file_checksum(filepath: Path) -> str:
    """Compute SHA-256 checksum of a Parquet file."""
    df = pd.read_parquet(filepath)
    return compute_dataframe_checksum(df)


@pytest.fixture(scope="session")
def baseline_checksums():
    """Load baseline checksums for regression testing."""
    baseline_path = Path("tests/fixtures/baseline_checksums.json")
    if not baseline_path.exists():
        pytest.skip(f"Baseline checksums not found: {baseline_path}")

    with open(baseline_path) as f:
        return json.load(f)


def test_regression_step1_output_stability(baseline_checksums):
    """Test that Step 1 (1.1_CleanMetadata) output hasn't changed from baseline."""
    # Arrange
    output_file = (
        resolve_output_dir(REPO_ROOT / "4_Outputs/1.1_CleanMetadata")
        / "cleaned_metadata.parquet"
    )

    if not output_file.exists():
        pytest.skip(f"Output file not found (run 1.1_CleanMetadata.py first)")

    # Act
    current_checksum = compute_file_checksum(output_file)
    expected_checksum = baseline_checksums.get("step1_cleaned_metadata")

    # Assert
    if expected_checksum is None:
        pytest.skip(
            "No baseline checksum for step1_cleaned_metadata (run with --update-baseline)"
        )

    assert current_checksum == expected_checksum, (
        f"Regression detected in Step 1 output!\n"
        f"File: {output_file}\n"
        f"Expected: {expected_checksum}\n"
        f"Got: {current_checksum}\n"
        f"Run with --update-baseline if this change is intentional"
    )


def test_regression_step2_output_stability(baseline_checksums):
    """Test that Step 2 (2.1_TokenizeAndCount) output hasn't changed from baseline."""
    # Arrange
    output_dir = Path("4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest")

    if not output_dir.exists():
        pytest.skip("Output directory not found (run 2.1_TokenizeAndCount.py first)")

    # Act - Check each yearly output file
    for year in range(2002, 2019):
        output_file = output_dir / f"linguistic_counts_{year}.parquet"

        if not output_file.exists():
            pytest.skip(f"Output file not found: {output_file.name}")

        current_checksum = compute_file_checksum(output_file)
        expected_checksum = baseline_checksums.get(f"step2_linguistic_counts_{year}")

        # Assert
        if expected_checksum is None:
            pytest.skip(
                f"No baseline checksum for {output_file.name} "
                f"(run with --update-baseline)"
            )

        assert current_checksum == expected_checksum, (
            f"Regression detected in Step 2 output (year {year})!\n"
            f"File: {output_file}\n"
            f"Expected: {expected_checksum}\n"
            f"Got: {current_checksum}\n"
            f"Run with --update-baseline if this change is intentional"
        )


def test_regression_step3_output_stability(baseline_checksums):
    """Test that Step 3 (3.0_BuildFinancialFeatures) output hasn't changed from baseline."""
    # Arrange
    output_file = (
        resolve_output_dir(
            REPO_ROOT / "4_Outputs/3_Financial_Features/3.0_BuildFinancialFeatures"
        )
        / "financial_features.parquet"
    )

    if not output_file.exists():
        pytest.skip(f"Output file not found (run 3.0_BuildFinancialFeatures.py first)")

    # Act
    current_checksum = compute_file_checksum(output_file)
    expected_checksum = baseline_checksums.get("step3_financial_features")

    # Assert
    if expected_checksum is None:
        pytest.skip(
            "No baseline checksum for step3_financial_features (run with --update-baseline)"
        )

    assert current_checksum == expected_checksum, (
        f"Regression detected in Step 3 output!\n"
        f"File: {output_file}\n"
        f"Expected: {expected_checksum}\n"
        f"Got: {current_checksum}\n"
        f"Run with --update-baseline if this change is intentional"
    )


@pytest.mark.parametrize(
    "output_dir,filename,baseline_key",
    [
        (
            "4_Outputs/1.1_CleanMetadata",
            "cleaned_metadata.parquet",
            "step1_cleaned_metadata",
        ),
        (
            "4_Outputs/2_Textual_Analysis/2.1_Tokenized",
            "linguistic_counts_2002.parquet",
            "step2_linguistic_counts_2002",
        ),
        (
            "4_Outputs/2_Textual_Analysis/2.1_Tokenized",
            "linguistic_counts_2018.parquet",
            "step2_linguistic_counts_2018",
        ),
        (
            "4_Outputs/3_Financial_Features/3.0_BuildFinancialFeatures",
            "financial_features.parquet",
            "step3_financial_features",
        ),
    ],
)
def test_regression_key_outputs(output_dir, filename, baseline_key, baseline_checksums):
    """Test that key output files haven't changed from baseline."""
    # Arrange
    output_file = resolve_output_dir(REPO_ROOT / output_dir) / filename

    if not output_file.exists():
        pytest.skip(f"Output file not found: {output_dir}/{filename}")

    # Act
    current_checksum = compute_file_checksum(output_file)
    expected_checksum = baseline_checksums.get(baseline_key)

    # Assert
    if expected_checksum is None:
        pytest.skip(
            f"No baseline checksum for {baseline_key} (run with --update-baseline)"
        )

    assert current_checksum == expected_checksum, (
        f"Regression detected in {baseline_key}!\n"
        f"Expected: {expected_checksum}\n"
        f"Got: {current_checksum}"
    )
