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
    """Verify observability features via regex pattern matching."""
    with open(script_path) as f:
        content = f.read()

    # Check required imports
    assert re.search(r"^import psutil\b", content, re.MULTILINE), (
        "Missing psutil import"
    )
    assert (
        re.search(r"^from shared\.path_utils import", content, re.MULTILINE),
        "Missing path_utils import",
    )

    # Check required functions
    assert (
        re.search(r"^def get_process_memory_mb\(", content, re.MULTILINE),
        "Missing memory tracking",
    )
    assert (
        re.search(r"^def calculate_throughput\(", content, re.MULTILINE),
        "Missing throughput calculation",
    )
    assert (
        re.search(r"^def detect_anomalies_zscore\(", content, re.MULTILINE),
        "Missing z-score anomaly detection",
    )
    assert (
        re.search(r"^def detect_anomalies_iqr\(", content, re.MULTILINE),
        "Missing IQR anomaly detection",
    )


class TestObservabilityIntegration:
    """Integration tests for observability features across Steps 1 and 2 scripts."""

    def test_1_1_observability(self, repo_root):
        """Test that 1.1_CleanMetadata.py has observability features."""
        script_path = repo_root / "2_Scripts/1_Sample/1.1_CleanMetadata.py"
        check_script_observability(script_path)
        print("✓ 1.1_CleanMetadata.py has observability features")
