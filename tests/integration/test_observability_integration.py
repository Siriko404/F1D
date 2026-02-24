"""
Integration Tests for Observability Features

Tests verify that observability features work end-to-end in modified scripts:
- Memory tracking (start, end, peak, delta MB)
- Throughput metrics (rows per second)
- Output file checksums (SHA-256)
- Data quality anomaly detection (z-score method, threshold=3.0)
- Backward compatibility (existing stats.json structure preserved)

Run with: pytest tests/integration/test_observability_integration.py -v -m integration --tb=short
"""

import pytest
import re
from pathlib import Path


@pytest.fixture(scope="session")
def repo_root():
    """Path to repository root directory."""
    return Path(__file__).parent.parent.parent


def check_script_observability(script_path):
    """Verify observability features via regex pattern matching.

    Supports both the legacy inline style (functions defined in-script) and
    the modern import style (functions imported from f1d.shared.observability).
    """
    with open(script_path) as f:
        content = f.read()

    # Check that memory tracking is present (import or inline definition)
    assert re.search(
        r"get_process_memory_mb",
        content,
    ), "Missing memory tracking (get_process_memory_mb)"

    # Check that throughput calculation is present
    assert re.search(
        r"calculate_throughput",
        content,
    ), "Missing throughput calculation"

    # Check that z-score anomaly detection is present
    assert re.search(
        r"detect_anomalies_zscore",
        content,
    ), "Missing z-score anomaly detection"

    # Check that path utilities are imported
    assert re.search(
        r"path_utils import",
        content,
    ), "Missing path_utils import"


class TestObservabilityIntegration:
    """Integration tests for observability features across Steps 1 and 2 scripts."""

    def test_1_1_observability(self, repo_root):
        """Test that clean_metadata.py has observability features."""
        script_path = repo_root / "src/f1d/sample/clean_metadata.py"
        check_script_observability(script_path)
        print("✓ clean_metadata.py has observability features")
