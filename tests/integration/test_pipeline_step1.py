"""
Integration tests for Step 1 (Sample Construction).
Tests end-to-end pipeline execution for sample construction scripts.
"""

import pytest
import subprocess
import json
from pathlib import Path
import pandas as pd
import yaml
import sys

pytestmark = pytest.mark.integration  # Mark all tests in this file as integration


# Add 2_Scripts to path for shared module imports (for direct imports)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))
from shared.path_utils import get_latest_output_dir, OutputResolutionError


def resolve_output_dir(base_path: Path) -> Path:
    """Resolve output directory using timestamp or fallback to /latest/."""
    try:
        return get_latest_output_dir(base_path)
    except OutputResolutionError:
        return base_path / "latest"

pytestmark = pytest.mark.integration  # Mark all tests in this file as integration


@pytest.fixture(scope="session")
def repo_root():
    """Path to repository root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def config(repo_root):
    """Load project configuration."""
    config_path = repo_root / "config/project.yaml"
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


def test_step1_full_pipeline(sample_input_data, config, repo_root, subprocess_env, tmp_path):
    """Test Step 1 (1.1_CleanMetadata) runs end-to-end."""
    # Arrange
    script_path = repo_root / "2_Scripts/1_Sample/1.1_CleanMetadata.py"

    if not script_path.exists():
        pytest.skip(f"Script not found: {script_path}")

    # Act - Run script via subprocess
    result = subprocess.run(
        ["python", str(script_path)],
        env=subprocess_env,
        capture_output=True,
        text=True,
    )

    # Assert
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    # Verify output files exist
    output_dir = resolve_output_dir(repo_root / "4_Outputs/1.1_CleanMetadata")
    assert output_dir.exists(), "Output directory not created"

    # Check for expected output files
    expected_files = [
        "cleaned_metadata.parquet",
        "stats.json",
    ]

    for filename in expected_files:
        file_path = output_dir / filename
        assert file_path.exists(), f"Expected output file not found: {filename}"


def test_stats_json_generation_step1(config, repo_root):
    """Test that stats.json is generated with required fields."""
    # Arrange
    stats_path = repo_root / "4_Outputs/1.1_CleanMetadata/latest/stats.json"

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


def test_row_count_validation_step1(repo_root):
    """Test that output row count is validated in stats.json."""
    # Arrange
    stats_path = repo_root / "4_Outputs/1.1_CleanMetadata/latest/stats.json"
    output_path = (
        repo_root / "4_Outputs/1.1_CleanMetadata/latest/cleaned_metadata.parquet"
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
