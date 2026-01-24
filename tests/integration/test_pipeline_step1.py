"""
Integration tests for Step 1 (Sample Construction).
Tests end-to-end pipeline execution for sample construction scripts.
"""

import os
import pytest
import subprocess
import json
from pathlib import Path
import pandas as pd
import yaml

# Get repository root from test file location
REPO_ROOT = Path(__file__).parent.parent.parent

# Environment for subprocess calls (includes PYTHONPATH for module resolution)
SUBPROCESS_ENV = {
    "PYTHONPATH": str(REPO_ROOT / "2_Scripts"),
    **os.environ,  # Preserve existing environment variables
}

pytestmark = pytest.mark.integration  # Mark all tests in this file as integration


@pytest.fixture(scope="session")
def config():
    """Load project configuration."""
    config_path = REPO_ROOT / "config/project.yaml"
    if not config_path.exists():
        pytest.skip(f"Config file not found: {config_path}")
    with open(config_path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def sample_input_data():
    """Create minimal sample input data for Step 1 testing."""
    # For now, skip this test if real data is not available
    # In production, create minimal sample data in tests/fixtures/
    pytest.skip("Sample input data not yet available in tests/fixtures/")
    return None


def test_step1_full_pipeline(sample_input_data, config, tmp_path):
    """Test Step 1 (1.1_CleanMetadata) runs end-to-end."""
    # Arrange
    script_path = REPO_ROOT / "2_Scripts/1_Sample/1.1_CleanMetadata.py"

    if not script_path.exists():
        pytest.skip(f"Script not found: {script_path}")

    # Act - Run script via subprocess
    result = subprocess.run(
        ["python", str(script_path)],
        env=SUBPROCESS_ENV,
        capture_output=True,
        text=True,
    )

    # Assert
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    # Verify output files exist
    output_dir = REPO_ROOT / "4_Outputs/1.1_CleanMetadata/latest"
    assert output_dir.exists(), "Output directory not created"

    # Check for expected output files
    expected_files = [
        "cleaned_metadata.parquet",
        "stats.json",
    ]

    for filename in expected_files:
        file_path = output_dir / filename
        assert file_path.exists(), f"Expected output file not found: {filename}"


def test_stats_json_generation_step1(config):
    """Test that stats.json is generated with required fields."""
    # Arrange
    stats_path = REPO_ROOT / "4_Outputs/1.1_CleanMetadata/latest/stats.json"

    if not stats_path.exists():
        pytest.skip(f"stats.json not found (run 1.1_CleanMetadata.py first)")

    # Act
    with open(stats_path) as f:
        stats = json.load(f)

    # Assert - Required fields from stats schema
    assert "inputs" in stats, "Missing 'inputs' field in stats.json"
    assert "outputs" in stats, "Missing 'outputs' field in stats.json"
    assert "processing" in stats, "Missing 'processing' field in stats.json"

    # Verify processing metrics
    assert "duration_seconds" in stats["processing"], "Missing duration_seconds"
    assert "start_time" in stats["processing"], "Missing start_time"
    assert "end_time" in stats["processing"], "Missing end_time"

    # Verify input tracking
    assert "files" in stats["inputs"], "Missing input files list"
    assert len(stats["inputs"]["files"]) > 0, "No input files tracked"

    # Verify output tracking
    assert "files" in stats["outputs"], "Missing output files list"
    assert len(stats["outputs"]["files"]) > 0, "No output files tracked"


def test_row_count_validation_step1():
    """Test that output row count is validated in stats.json."""
    # Arrange
    stats_path = REPO_ROOT / "4_Outputs/1.1_CleanMetadata/latest/stats.json"
    output_path = (
        REPO_ROOT / "4_Outputs/1.1_CleanMetadata/latest/cleaned_metadata.parquet"
    )

    if not stats_path.exists() or not output_path.exists():
        pytest.skip("Run 1.1_CleanMetadata.py first")

    # Act
    with open(stats_path) as f:
        stats = json.load(f)

    df = pd.read_parquet(output_path)

    # Assert - Output row count in stats.json matches actual file
    stats_row_count = stats["outputs"].get("total_rows")
    actual_row_count = len(df)

    assert stats_row_count == actual_row_count, (
        f"Row count mismatch: stats.json says {stats_row_count}, "
        f"but file has {actual_row_count} rows"
    )
