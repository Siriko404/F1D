"""
Pytest configuration and shared fixtures for testing.

This file provides common fixtures used across all test files.

PYTEST CONFIGURATION

Subprocess Testing Pattern:
    Integration tests invoke pipeline scripts via subprocess.run().
    These scripts import from 'shared' modules, requiring PYTHONPATH
    to be set for subprocess to find 2_Scripts/shared/.

    Always use the subprocess_env fixture for subprocess calls:

        def test_my_script(subprocess_env):
            result = subprocess.run(
                ["python", "script.py"],
                env=subprocess_env,  # Critical: enables shared imports
                ...
            )
"""

import pytest
from pathlib import Path
import pandas as pd
import sys
from io import StringIO
import yaml


@pytest.fixture(scope="session")
def repo_root():
    """Path to repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def subprocess_env():
    """
    Provide environment variables for subprocess calls in integration tests.

    Sets PYTHONPATH to enable subprocess to import shared modules.
    All integration tests that invoke scripts via subprocess should use this:

        result = subprocess.run(
            ["python", str(script_path)],
            env=subprocess_env,
            ...
        )

    Returns:
        Dict[str, str]: Environment variables with PYTHONPATH set
    """
    import os
    from pathlib import Path

    repo_root = Path(__file__).parent.parent
    return {
        "PYTHONPATH": str(repo_root / "2_Scripts"),
        **os.environ,  # Preserve existing environment variables
    }


@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory (shared across all tests)."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "file_name": ["test1.docx", "test2.docx", "test3.docx"],
            "Total_Words": [100, 200, 150],
            "MaQaUnc_pct": [0.5, 0.75, 0.6],
        }
    )


@pytest.fixture
def sample_parquet_file(tmp_path, sample_dataframe):
    """Create a temporary Parquet file for testing."""
    file_path = tmp_path / "test_data.parquet"
    sample_dataframe.to_parquet(file_path)
    return file_path


@pytest.fixture
def sample_config_path(test_data_dir):
    """Path to sample project.yaml for testing."""
    config_path = test_data_dir / "sample_yaml" / "project.yaml"
    if not config_path.exists():
        pytest.skip(f"Sample config not found: {config_path}")
    return config_path


@pytest.fixture
def sample_parquet_file_with_schema(tmp_path):
    """Create a temporary Parquet file matching Unified-info schema."""
    df = pd.DataFrame(
        {
            "event_type": ["1", "1", "2"],  # String for object dtype
            "file_name": ["call1.docx", "call2.docx", "call3.docx"],
            "start_date": pd.to_datetime(["2002-01-15", "2002-02-20", "2002-03-10"]),
            "speaker_record_count": [2, 1, 1],  # Matches schema
        }
    )
    file_path = tmp_path / "unified_info_test.parquet"
    df.to_parquet(file_path)
    return file_path


@pytest.fixture
def mock_project_config(tmp_path):
    """Create a minimal project.yaml for testing."""
    config_data = {
        "project": {
            "name": "F1D_Test",
            "version": "1.0.0",
        },
        "data": {
            "year_start": 2002,
            "year_end": 2005,
        },
        "determinism": {
            "random_seed": 42,
            "thread_count": 1,
        },
    }
    config_path = tmp_path / "project.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    return config_path


@pytest.fixture
def capture_output():
    """Capture stdout and stderr for testing console output."""

    class Capture:
        def __init__(self):
            self.stdout_buf = StringIO()
            self.stderr_buf = StringIO()
            self.old_stdout = sys.stdout
            self.old_stderr = sys.stderr

        def start(self):
            sys.stdout = self.stdout_buf
            sys.stderr = self.stderr_buf

        def stop(self):
            sys.stdout = self.old_stdout
            sys.stderr = self.old_stderr
            return (self.stdout_buf.getvalue(), self.stderr_buf.getvalue())

        def reset(self):
            self.stdout_buf = StringIO()
            self.stderr_buf = StringIO()

    capture = Capture()
    yield capture
    # Cleanup: restore original streams
    sys.stdout = capture.old_stdout
    sys.stderr = capture.old_stderr
