"""Edge case tests for subprocess_validation module."""

import pytest
from pathlib import Path
import sys

# Add 2_Scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))

try:
    from shared.subprocess_validation import validate_script_path

    SUBPROCESS_VALIDATION_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    SUBPROCESS_VALIDATION_AVAILABLE = False
    pytest.skip("subprocess_validation module not available", allow_module_level=True)


@pytest.mark.skipif(
    not SUBPROCESS_VALIDATION_AVAILABLE,
    reason="subprocess_validation module not available",
)
def test_validate_script_path_relative_path(tmp_path):
    """Test path validation resolves relative paths correctly."""
    allowed_dir = tmp_path / "allowed"
    allowed_dir.mkdir()
    script_path = allowed_dir / "script.py"
    script_path.write_text("# test script")
    relative_path = Path("allowed/script.py")
    result = validate_script_path(relative_path, tmp_path)
    assert result.is_absolute()
    assert result == script_path
