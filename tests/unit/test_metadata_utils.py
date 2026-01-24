"""
ID: test_metadata_utils
Description: Unit tests for variable description loading
Declared Inputs: Test variable reference files
Declared Outputs: pytest test functions
deterministic: true
"""

import pytest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))

from shared.metadata_utils import load_variable_descriptions


def test_load_variable_descriptions_basic():
    """Test basic variable description loading from a valid reference file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test reference file with tab-separated format (with header)
        ref_file = Path(tmpdir) / "ccm_varref.txt"
        ref_content = """variable_name\tvariable_code\tvariable_description
gvkey\tGlobalCompanyKey\tGlobal Company Key identifier
lpermno\tLinkPermNo\tLink permanent number
sic\tSICCode\tStandard Industrial Classification code
"""

        with open(ref_file, "w", encoding="utf-8") as f:
            f.write(ref_content)

        # Load descriptions
        result = load_variable_descriptions({"ccm": ref_file})

        # Verify all variables loaded
        assert len(result) == 3

        # Check first variable
        assert "gvkey" in result
        assert result["gvkey"]["source"] == "ccm"
        assert result["gvkey"]["description"] == "Global Company Key identifier"

        # Check second variable
        assert "lpermno" in result
        assert result["lpermno"]["source"] == "ccm"
        assert result["lpermno"]["description"] == "Link permanent number"

        # Check third variable
        assert "sic" in result
        assert result["sic"]["source"] == "ccm"
        assert result["sic"]["description"] == "Standard Industrial Classification code"


def test_load_variable_descriptions_multiple_sources():
    """Test loading descriptions from multiple source files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create CCM reference file
        ccm_file = Path(tmpdir) / "ccm_varref.txt"
        ccm_content = """variable_name\tvariable_code\tvariable_description
gvkey\tGlobalCompanyKey\tGlobal Company Key
lpermno\tLinkPermNo\tLink permanent number
"""
        with open(ccm_file, "w", encoding="utf-8") as f:
            f.write(ccm_content)

        # Create CRSP reference file
        crsp_file = Path(tmpdir) / "crsp_varref.txt"
        crsp_content = """variable_name\tvariable_code\tvariable_description
permno\tPermNo\tCRSP permanent number
permco\tPermCo\tCRSP company identifier
"""
        with open(crsp_file, "w", encoding="utf-8") as f:
            f.write(crsp_content)

        # Load descriptions from both sources
        result = load_variable_descriptions({"ccm": ccm_file, "crsp": crsp_file})

        # Verify all variables from both sources
        assert len(result) == 4

        # Check CCM variables
        assert result["gvkey"]["source"] == "ccm"
        assert result["lpermno"]["source"] == "ccm"

        # Check CRSP variables
        assert result["permno"]["source"] == "crsp"
        assert result["permco"]["source"] == "crsp"


def test_load_variable_descriptions_missing_file():
    """Test graceful handling of missing reference file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create one valid file
        valid_file = Path(tmpdir) / "valid_varref.txt"
        valid_content = """variable_name\tvariable_code\tvariable_description
var1\tVar1\tVariable 1 description
"""
        with open(valid_file, "w", encoding="utf-8") as f:
            f.write(valid_content)

        # Create path to non-existent file
        missing_file = Path(tmpdir) / "missing_varref.txt"

        # Load descriptions - missing file should be silently skipped
        result = load_variable_descriptions(
            {"valid": valid_file, "missing": missing_file}
        )

        # Should only load from valid file
        assert len(result) == 1
        assert "var1" in result
        assert result["var1"]["source"] == "valid"


def test_load_variable_descriptions_malformed_file():
    """Test handling of malformed TSV format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create malformed file (not enough columns)
        malformed_file = Path(tmpdir) / "malformed_varref.txt"
        malformed_content = """var1\tVar1
var2\tVar2\t
"""  # Only 1 or 2 columns instead of 3
        with open(malformed_file, "w", encoding="utf-8") as f:
            f.write(malformed_content)

        # Load descriptions - malformed lines should be skipped
        result = load_variable_descriptions({"malformed": malformed_file})

        # Should return empty dict (no valid lines)
        assert len(result) == 0


def test_load_variable_descriptions_empty_file():
    """Test handling of empty reference file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create empty file
        empty_file = Path(tmpdir) / "empty_varref.txt"
        with open(empty_file, "w", encoding="utf-8") as f:
            pass  # Empty file

        # Load descriptions
        result = load_variable_descriptions({"empty": empty_file})

        # Should return empty dict
        assert len(result) == 0


def test_load_variable_descriptions_header_only():
    """Test handling of file with only header row."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create file with header only
        header_file = Path(tmpdir) / "header_varref.txt"
        header_content = """var_name\tvar_code\tvar_desc
"""
        with open(header_file, "w", encoding="utf-8") as f:
            f.write(header_content)

        # Load descriptions - header should be skipped
        result = load_variable_descriptions({"header": header_file})

        # Should return empty dict (only header, no data)
        assert len(result) == 0


def test_load_variable_descriptions_varnames_lowercase():
    """Test that variable names are converted to lowercase."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create file with mixed case variable names
        ref_file = Path(tmpdir) / "mixed_case_varref.txt"
        ref_content = """variable_name\tvariable_code\tvariable_description
GVKEY\tGlobalCompanyKey\tGlobal Company Key
PermNo\tPermNo\tPermanent number
"""
        with open(ref_file, "w", encoding="utf-8") as f:
            f.write(ref_content)

        # Load descriptions
        result = load_variable_descriptions({"mixed": ref_file})

        # Verify variable names are lowercase
        assert "gvkey" in result
        assert "permno" in result
        assert "GVKEY" not in result  # Original case not preserved
        assert "PermNo" not in result  # Original case not preserved


def test_load_variable_descriptions_extra_columns():
    """Test handling of files with more than 3 columns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create file with extra columns
        extra_file = Path(tmpdir) / "extra_varref.txt"
        extra_content = """variable_name\tvariable_code\tvariable_description\textra_col1\textra_col2
var1\tVar1\tVariable 1 description\tExtra column 1\tExtra column 2
var2\tVar2\tVariable 2 description\tExtra info
"""
        with open(extra_file, "w", encoding="utf-8") as f:
            f.write(extra_content)

        # Load descriptions - should use first 3 columns
        result = load_variable_descriptions({"extra": extra_file})

        # Should load both variables, ignoring extra columns
        assert len(result) == 2
        assert result["var1"]["description"] == "Variable 1 description"
        assert result["var2"]["description"] == "Variable 2 description"
