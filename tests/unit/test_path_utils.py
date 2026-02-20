"""Unit tests for path utilities module.

This module tests the path_utils functions for:
- Path validation (validate_output_path, validate_input_file)
- Directory creation (ensure_output_dir)
- Output directory resolution (get_latest_output_dir)
- Data path resolution with backward compatibility (resolve_data_path)
- Output directory management (get_output_dir, get_results_subdir)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

import pytest

from f1d.shared.path_utils import (
    DATA_RAW,
    DATA_INTERIM,
    DATA_PROCESSED,
    DATA_EXTERNAL,
    LOGS_DIR,
    RESULTS_DIR,
    INPUTS_DIR,
    OUTPUTS_DIR,
    OLD_LOGS_DIR,
    PathValidationError,
    OutputResolutionError,
    validate_output_path,
    ensure_output_dir,
    validate_input_file,
    get_available_disk_space,
    get_latest_output_dir,
    resolve_data_path,
    get_output_dir,
    get_results_subdir,
    deprecation_warning,
)


class TestPathConstants:
    """Tests for path constants."""

    def test_new_structure_constants(self):
        """Test new structure path constants are defined."""
        assert DATA_RAW == Path("data/raw")
        assert DATA_INTERIM == Path("data/interim")
        assert DATA_PROCESSED == Path("data/processed")
        assert DATA_EXTERNAL == Path("data/external")
        assert LOGS_DIR == Path("logs")
        assert RESULTS_DIR == Path("results")

    def test_legacy_constants(self):
        """Test legacy path constants are defined."""
        assert INPUTS_DIR == Path("inputs")
        assert OUTPUTS_DIR == Path("outputs")
        assert OLD_LOGS_DIR == Path("logs")


class TestValidateOutputPath:
    """Tests for validate_output_path function."""

    def test_validate_existing_directory(self, tmp_path: Path):
        """Test validation of existing directory."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        result = validate_output_path(test_dir, must_exist=True, must_be_writable=False)

        assert result == test_dir.resolve()

    def test_validate_nonexistent_directory_with_must_exist(self, tmp_path: Path):
        """Test validation raises error when must_exist=True and path doesn't exist."""
        test_dir = tmp_path / "nonexistent"

        with pytest.raises(PathValidationError, match="Path does not exist"):
            validate_output_path(test_dir, must_exist=True)

    def test_validate_file_not_directory(self, tmp_path: Path):
        """Test validation raises error when path is a file, not directory."""
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test")

        with pytest.raises(PathValidationError, match="Path is not a directory"):
            validate_output_path(test_file, must_exist=True)

    def test_validate_non_writable_directory(self, tmp_path: Path):
        """Test validation raises error for non-writable directory."""
        # This test may not work on all systems due to permission issues
        # Skip on Windows as permissions work differently
        if os.name == "nt":
            pytest.skip("Permission test not reliable on Windows")

        test_dir = tmp_path / "readonly_dir"
        test_dir.mkdir()
        os.chmod(test_dir, 0o444)

        try:
            with pytest.raises(PathValidationError, match="Path not writable"):
                validate_output_path(test_dir, must_exist=True, must_be_writable=True)
        finally:
            os.chmod(test_dir, 0o755)

    def test_validate_resolves_path(self, tmp_path: Path):
        """Test that validation returns resolved absolute path."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        result = validate_output_path(test_dir, must_exist=True)

        assert result.is_absolute()


class TestEnsureOutputDir:
    """Tests for ensure_output_dir function."""

    def test_create_new_directory(self, tmp_path: Path):
        """Test creating a new directory."""
        new_dir = tmp_path / "new_output"

        result = ensure_output_dir(new_dir)

        assert new_dir.exists()
        assert new_dir.is_dir()
        assert result == new_dir.resolve()

    def test_create_nested_directories(self, tmp_path: Path):
        """Test creating nested directories."""
        nested_dir = tmp_path / "level1" / "level2" / "level3"

        result = ensure_output_dir(nested_dir)

        assert nested_dir.exists()
        assert nested_dir.is_dir()

    def test_existing_directory(self, tmp_path: Path):
        """Test with existing directory."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        result = ensure_output_dir(existing_dir)

        assert existing_dir.exists()
        assert result == existing_dir.resolve()


class TestValidateInputFile:
    """Tests for validate_input_file function."""

    def test_validate_existing_file(self, tmp_path: Path):
        """Test validation of existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        result = validate_input_file(test_file, must_exist=True)

        assert result == test_file.resolve()

    def test_validate_nonexistent_file(self, tmp_path: Path):
        """Test validation raises error for nonexistent file."""
        test_file = tmp_path / "nonexistent.txt"

        with pytest.raises(PathValidationError, match="Input file does not exist"):
            validate_input_file(test_file, must_exist=True)

    def test_validate_directory_not_file(self, tmp_path: Path):
        """Test validation raises error when path is directory."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        with pytest.raises(PathValidationError, match="Path is not a file"):
            validate_input_file(test_dir, must_exist=True)

    def test_validate_optional_file(self, tmp_path: Path):
        """Test validation allows nonexistent file when must_exist=False."""
        test_file = tmp_path / "optional.txt"

        result = validate_input_file(test_file, must_exist=False)

        assert result == test_file.resolve()


class TestGetAvailableDiskSpace:
    """Tests for get_available_disk_space function."""

    def test_returns_positive_float(self, tmp_path: Path):
        """Test that disk space returns positive float in GB."""
        space = get_available_disk_space(tmp_path)

        assert isinstance(space, float)
        assert space > 0

    def test_space_reasonable_value(self, tmp_path: Path):
        """Test that disk space is in reasonable range (0-10000 GB)."""
        space = get_available_disk_space(tmp_path)

        # Most systems have at least some free space
        # and less than 10 TB
        assert 0 < space < 10000


class TestGetLatestOutputDir:
    """Tests for get_latest_output_dir function."""

    def test_get_latest_timestamped_dir(self, tmp_path: Path):
        """Test getting the latest timestamped directory."""
        # Create timestamped directories
        (tmp_path / "2024-01-01_120000").mkdir()
        (tmp_path / "2024-01-02_120000").mkdir()
        (tmp_path / "2024-01-03_120000").mkdir()
        # Non-timestamped directory should be ignored
        (tmp_path / "other_dir").mkdir()

        result = get_latest_output_dir(tmp_path)

        assert result.name == "2024-01-03_120000"

    def test_no_timestamped_directories(self, tmp_path: Path):
        """Test error when no timestamped directories exist."""
        (tmp_path / "other_dir").mkdir()

        with pytest.raises(OutputResolutionError, match="No timestamped directories found"):
            get_latest_output_dir(tmp_path)

    def test_nonexistent_base_directory(self, tmp_path: Path):
        """Test error when base directory doesn't exist."""
        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(OutputResolutionError, match="Output base directory not found"):
            get_latest_output_dir(nonexistent)

    def test_with_required_file(self, tmp_path: Path):
        """Test filtering by required file."""
        # Create directories with and without required file
        dir1 = tmp_path / "2024-01-01_120000"
        dir1.mkdir()
        (dir1 / "output.parquet").write_text("data")

        dir2 = tmp_path / "2024-01-02_120000"
        dir2.mkdir()
        # No output.parquet in dir2

        result = get_latest_output_dir(tmp_path, required_file="output.parquet")

        # Should return dir1 since it has the required file
        assert result.name == "2024-01-01_120000"

    def test_no_directory_with_required_file(self, tmp_path: Path):
        """Test error when no directory contains required file."""
        (tmp_path / "2024-01-01_120000").mkdir()
        (tmp_path / "2024-01-02_120000").mkdir()

        with pytest.raises(OutputResolutionError, match="No directory contains required file"):
            get_latest_output_dir(tmp_path, required_file="missing.parquet")


class TestResolveDataPath:
    """Tests for resolve_data_path function."""

    def test_resolve_canonical_names(self):
        """Test resolving canonical path names."""
        # These should return the new structure paths
        assert resolve_data_path("raw") == DATA_RAW
        assert resolve_data_path("interim") == DATA_INTERIM
        assert resolve_data_path("processed") == DATA_PROCESSED
        assert resolve_data_path("external") == DATA_EXTERNAL
        assert resolve_data_path("logs") == LOGS_DIR
        assert resolve_data_path("results") == RESULTS_DIR

    def test_resolve_legacy_name_with_new_structure(self, tmp_path: Path, monkeypatch):
        """Test resolving legacy names when new structure exists."""
        # Create new structure directory
        new_raw = tmp_path / "data" / "raw"
        new_raw.mkdir(parents=True)

        # Change to tmp_path directory
        monkeypatch.chdir(tmp_path)

        # When new structure exists, prefer it
        result = resolve_data_path("inputs", prefer_new=True)

        assert result == DATA_RAW

    def test_resolve_nonexistent_path_raises(self, tmp_path: Path, monkeypatch):
        """Test error when path not found in either location."""
        monkeypatch.chdir(tmp_path)

        with pytest.raises(FileNotFoundError, match="not found"):
            resolve_data_path("nonexistent_data")


class TestGetOutputDir:
    """Tests for get_output_dir function."""

    def test_get_output_dir_new_structure(self):
        """Test getting output directory in new structure."""
        result = get_output_dir("sample", prefer_new=True)

        assert result == DATA_INTERIM / "sample"

    def test_get_output_dir_legacy_structure(self):
        """Test getting output directory in legacy structure."""
        result = get_output_dir("sample", prefer_new=False)

        assert result == OUTPUTS_DIR / "sample"

    def test_get_output_dir_with_date(self):
        """Test getting output directory with date subdirectory."""
        result = get_output_dir("sample", date="2024-01-15", prefer_new=True)

        assert result == DATA_INTERIM / "sample" / "2024-01-15"


class TestGetResultsSubdir:
    """Tests for get_results_subdir function."""

    def test_get_figures_subdir(self):
        """Test getting figures subdirectory."""
        result = get_results_subdir("figures")

        assert result == RESULTS_DIR / "figures"

    def test_get_tables_subdir(self):
        """Test getting tables subdirectory."""
        result = get_results_subdir("tables")

        assert result == RESULTS_DIR / "tables"

    def test_get_reports_subdir(self):
        """Test getting reports subdirectory."""
        result = get_results_subdir("reports")

        assert result == RESULTS_DIR / "reports"


class TestDeprecationWarning:
    """Tests for deprecation_warning function."""

    def test_issues_deprecation_warning(self):
        """Test that deprecation warning is issued."""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            deprecation_warning("old_func", "new_func", "7.0")

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "old_func" in str(w[0].message)
            assert "new_func" in str(w[0].message)
            assert "7.0" in str(w[0].message)


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_path_with_spaces(self, tmp_path: Path):
        """Test handling paths with spaces."""
        dir_with_spaces = tmp_path / "path with spaces"
        dir_with_spaces.mkdir()

        result = validate_output_path(dir_with_spaces, must_exist=True)

        assert result == dir_with_spaces.resolve()

    def test_path_with_unicode(self, tmp_path: Path):
        """Test handling paths with unicode characters."""
        dir_with_unicode = tmp_path / "unicode_\u4e2d\u6587"
        dir_with_unicode.mkdir()

        result = validate_output_path(dir_with_unicode, must_exist=True)

        assert result == dir_with_unicode.resolve()

    def test_long_path(self, tmp_path: Path):
        """Test handling long paths."""
        long_path = tmp_path / ("a" * 100)
        long_path.mkdir()

        result = validate_output_path(long_path, must_exist=True)

        assert result == long_path.resolve()

    def test_symlink_handling(self, tmp_path: Path):
        """Test handling symbolic links."""
        real_dir = tmp_path / "real_dir"
        real_dir.mkdir()

        symlink_dir = tmp_path / "symlink_dir"

        # Create symlink (may fail on Windows without admin privileges)
        try:
            symlink_dir.symlink_to(real_dir)
        except OSError:
            pytest.skip("Symlink creation failed (may need admin on Windows)")

        result = validate_output_path(symlink_dir, must_exist=True)

        # Result should resolve to real path
        assert result == real_dir.resolve()
