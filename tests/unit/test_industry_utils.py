"""
ID: test_industry_utils
Description: Unit tests for Fama-French industry classification parsing
Declared Inputs: Test FF industry zip files
Declared Outputs: pytest test functions
deterministic: true
"""

import pytest
import tempfile
import zipfile
from pathlib import Path

from f1d.shared.industry_utils import parse_ff_industries


def test_parse_ff_industries_basic():
    """Test basic FF12 file parsing with 2 industries."""
    # Create temporary FF12 zip file
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "Siccodes12.zip"

        # Create test content: 2 industries with SIC ranges
        ff_content = """1 Non-durables
100-199
200-299
2 Durables
300-399
400-499
"""

        # Create zip file
        with zipfile.ZipFile(zip_path, "w") as z:
            z.writestr("siccodes12.txt", ff_content)

        # Parse and verify
        result = parse_ff_industries(zip_path, 12)

        # Check SIC codes 100-199 mapped to industry 1
        assert result[100] == (1, "Non-durables")
        assert result[150] == (1, "Non-durables")
        assert result[199] == (1, "Non-durables")

        # Check SIC codes 200-299 mapped to industry 1 (same industry)
        assert result[200] == (1, "Non-durables")
        assert result[299] == (1, "Non-durables")

        # Check SIC codes 300-399 mapped to industry 2
        assert result[300] == (2, "Durables")
        assert result[350] == (2, "Durables")
        assert result[399] == (2, "Durables")

        # Check SIC codes 400-499 mapped to industry 2 (same industry)
        assert result[400] == (2, "Durables")
        assert result[499] == (2, "Durables")

        # Verify total count: 400 SIC codes + 1 "_catchall" sentinel key.
        # Both industries have explicit SIC ranges so _catchall is None, but
        # the key is always present.
        assert (
            len(result) == 401
        )  # 100-199 (100) + 200-299 (100) + 300-399 (100) + 400-499 (100) + _catchall key
        assert "_catchall" in result


def test_parse_ff_industries_ff48():
    """Test FF48 file parsing with multiple industries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "Siccodes48.zip"

        # Create test content: 3 industries with 4-digit SIC ranges
        ff_content = """1 Agriculture
0100-0199
2 Mining
1000-1099
2000-2099
3 Construction
1500-1599
"""

        # Create zip file
        with zipfile.ZipFile(zip_path, "w") as z:
            z.writestr("siccodes48.txt", ff_content)

        # Parse and verify
        result = parse_ff_industries(zip_path, 48)

        # Check 4-digit SIC ranges for Agriculture
        assert result[100] == (1, "Agriculture")
        assert result[199] == (1, "Agriculture")

        # Check 4-digit SIC ranges for Mining
        assert result[1000] == (2, "Mining")
        assert result[1050] == (2, "Mining")
        assert result[1099] == (2, "Mining")
        assert result[2000] == (2, "Mining")
        assert result[2050] == (2, "Mining")
        assert result[2099] == (2, "Mining")

        # Check Construction range
        assert result[1500] == (3, "Construction")
        assert result[1550] == (3, "Construction")
        assert result[1599] == (3, "Construction")


def test_parse_ff_industries_sic_range():
    """Test SIC code range parsing handles different formats."""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "Siccodes12.zip"

        # Test various SIC range formats (single-word industry names per parsing logic)
        ff_content = """1 Agriculture
100-199
1000-1099
2 Mining
2000-2099
"""

        # Create zip file
        with zipfile.ZipFile(zip_path, "w") as z:
            z.writestr("siccodes12.txt", ff_content)

        # Parse and verify
        result = parse_ff_industries(zip_path, 12)

        # Verify 2-digit range (100-199)
        assert result[100] == (1, "Agriculture")
        assert result[199] == (1, "Agriculture")

        # Verify 4-digit range (1000-1099)
        assert result[1000] == (1, "Agriculture")
        assert result[1050] == (1, "Agriculture")
        assert result[1099] == (1, "Agriculture")

        # Verify different 4-digit range
        assert result[2000] == (2, "Mining")
        assert result[2099] == (2, "Mining")


def test_parse_ff_industries_missing_file():
    """Test error handling for missing zip file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "nonexistent.zip"

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            parse_ff_industries(zip_path, 12)


def test_parse_ff_industries_empty_file():
    """Test handling of empty zip file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "empty.zip"

        # Create empty zip file
        with zipfile.ZipFile(zip_path, "w") as z:
            pass  # No files added

        # Should raise ValueError (no text files in zip)
        with pytest.raises((IndexError, ValueError)):
            parse_ff_industries(zip_path, 12)


def test_parse_ff_industries_invalid_format():
    """Test handling of malformed FF file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "invalid.zip"

        # Create malformed content (no valid SIC ranges)
        ff_content = """# Header comment
Invalid line without industry code
Another invalid line
"""

        # Create zip file
        with zipfile.ZipFile(zip_path, "w") as z:
            z.writestr("siccodes12.txt", ff_content)

        # Parse and verify: no valid SIC ranges, so only the "_catchall" sentinel
        # key is present (always added by parse_ff_industries).
        result = parse_ff_industries(zip_path, 12)
        assert len(result) == 1
        assert "_catchall" in result
