"""Path resolution utilities for F1D project.

This module provides the PathsSettings class for resolving and validating
file system paths used throughout the F1D pipeline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class PathsSettings(BaseSettings):
    """Configuration for file system paths.

    Manages path definitions for inputs, outputs, logs, and other directories.
    Supports pattern strings with placeholders like {year} for dynamic paths.

    Attributes:
        inputs: Input data directory (relative to project root).
        scripts: Scripts directory (relative to project root).
        logs: Logs directory (relative to project root).
        outputs: Outputs directory (relative to project root).
        lm_dictionary: Path to Loughran-McDonald dictionary file.
        unified_info: Path to unified info parquet file.
        speaker_data_pattern: Pattern for speaker data files with {year} placeholder.

    Example:
        >>> from pathlib import Path
        >>> paths = PathsSettings()
        >>> resolved = paths.resolve(Path("/project"))
        >>> resolved["inputs"]
        PosixPath('/project/inputs')
    """

    inputs: str = Field(default="inputs", description="Input data directory")
    scripts: str = Field(default="src/f1d", description="Scripts directory (src-layout)")
    logs: str = Field(default="logs", description="Logs directory")
    outputs: str = Field(default="outputs", description="Outputs directory")
    lm_dictionary: Optional[str] = Field(
        default=None, description="Path to Loughran-McDonald dictionary"
    )
    unified_info: Optional[str] = Field(
        default=None, description="Path to unified info parquet"
    )
    speaker_data_pattern: Optional[str] = Field(
        default=None, description="Pattern for speaker data with {year} placeholder"
    )

    def resolve(self, base: Path) -> Dict[str, Any]:
        """Resolve all paths to absolute Path objects.

        Converts string paths to absolute Path objects relative to the base directory.
        Handles pattern strings containing placeholders like {year}.

        Args:
            base: Base directory (typically project root) for resolving relative paths.

        Returns:
            Dictionary mapping path names to resolved absolute Path objects.
            Pattern paths are returned as strings for later formatting with .format().

        Example:
            >>> paths = PathsSettings()
            >>> resolved = paths.resolve(Path("/project"))
            >>> resolved["inputs"]
            PosixPath('/project/inputs')
        """
        resolved: Dict[str, Any] = {}

        # Core directories
        resolved["inputs"] = (base / self.inputs).resolve()
        resolved["scripts"] = (base / self.scripts).resolve()
        resolved["logs"] = (base / self.logs).resolve()
        resolved["outputs"] = (base / self.outputs).resolve()

        # Optional file paths
        if self.lm_dictionary:
            resolved["lm_dictionary"] = (base / self.lm_dictionary).resolve()

        if self.unified_info:
            resolved["unified_info"] = (base / self.unified_info).resolve()

        # Pattern paths - keep as string for later formatting with .format(year=2020)
        if self.speaker_data_pattern:
            # Store pattern for later use with format()
            resolved["speaker_data_pattern"] = str(
                (base / self.speaker_data_pattern).resolve()
            )

        return resolved

    def validate_paths(self, base: Path) -> Dict[str, Any]:
        """Validate paths and create output directories if needed.

        Checks that input paths exist and creates output/log directories
        if they don't exist.

        Args:
            base: Base directory (typically project root) for resolving paths.

        Returns:
            Dictionary of validated paths.

        Raises:
            FileNotFoundError: If required input paths don't exist.

        Example:
            >>> paths = PathsSettings()
            >>> validated = paths.validate_paths(Path("/project"))
        """
        resolved = self.resolve(base)

        # Check input directory exists
        inputs_path = resolved["inputs"]
        assert isinstance(inputs_path, Path)
        if not inputs_path.exists():
            raise FileNotFoundError(f"Input directory not found: {inputs_path}")

        # Check optional input files if specified
        if "lm_dictionary" in resolved:
            lm_path = resolved["lm_dictionary"]
            assert isinstance(lm_path, Path)
            if not lm_path.exists():
                raise FileNotFoundError(f"LM dictionary not found: {lm_path}")

        if "unified_info" in resolved:
            unified_path = resolved["unified_info"]
            assert isinstance(unified_path, Path)
            if not unified_path.exists():
                raise FileNotFoundError(f"Unified info file not found: {unified_path}")

        # Create output and log directories if they don't exist
        outputs_path = resolved["outputs"]
        assert isinstance(outputs_path, Path)
        outputs_path.mkdir(parents=True, exist_ok=True)

        logs_path = resolved["logs"]
        assert isinstance(logs_path, Path)
        logs_path.mkdir(parents=True, exist_ok=True)

        return resolved
