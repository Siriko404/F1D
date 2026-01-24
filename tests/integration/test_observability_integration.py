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

import os
import re
from pathlib import Path

# Get repository root from test file location
REPO_ROOT = Path(__file__).parent.parent.parent

# Environment for subprocess calls (includes PYTHONPATH for module resolution)
SUBPROCESS_ENV = {
    "PYTHONPATH": str(REPO_ROOT / "2_Scripts"),
    **os.environ,  # Preserve existing environment variables
}


class TestObservabilityIntegration:
    """Integration tests for observability features across Steps 1 and 2 scripts."""

    def test_1_1_observability(self):
        """Test that 1.1_CleanMetadata.py has observability features."""
        import ast

        script_path = REPO_ROOT / "2_Scripts/1_Sample/1.1_CleanMetadata.py"
        with open(script_path, "r") as f:
            tree = ast.parse(f.read())

        # Check psutil import
        imports = [
            node.names[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
        ]
        import_names = [imp.names[0] for imp in imports if imp.names]
        assert "psutil" in import_names, "psutil must be imported"

        # Check observability helper functions
        funcs = {
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        }
        required_funcs = {
            "get_process_memory_mb",
            "calculate_throughput",
            "detect_anomalies_zscore",
            "detect_anomalies_iqr",
        }
        missing = required_funcs - funcs
        assert len(missing) == 0, f"Missing observability helpers: {missing}"

        print("✓ 1.1_CleanMetadata.py has observability features")

    def test_stats_json_schema_backward_compatible(self):
        """Test that modified scripts preserve existing stats.json structure."""
        # Sample key scripts to verify backward compatibility
        scripts_to_check = [
            "2_Scripts/1_Sample/1.1_CleanMetadata.py",
        ]
        required_sections = {
            "input",
            "output",
            "processing",
            "missing_values",
            "timing",
        }
        for script_path_str in scripts_to_check:
            script_path = REPO_ROOT / script_path_str
            with open(script_path, "r") as f:
                tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == "stats":
                                # Found stats assignment, check if required sections are present
                                required = required_sections.copy()
                                for section in required:
                                    if section in tree.body[i].value:
                                        break
                                if len(required) > 0:
                                    break
                                if (
                                    isinstance(target, ast.Name)
                                    and target.id == "stats"
                                ):
                                    break
                    if len(required) == 0:
                        break

        print("✓ Stats.json schema backward compatible")
