"""Base classes for variable builders.

This module provides the base interface for building variables from various
data sources (Stage 2 text outputs, Stage 3 financial outputs, manifest).

Example:
    from f1d.shared.variables.base import VariableBuilder, VariableResult

    class MyVariableBuilder(VariableBuilder):
        def build(self, years: range, root_path: Path) -> VariableResult:
            # Load data for all years
            ...
            return VariableResult(data=df, stats=stats, metadata=metadata)
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


@dataclass
class VariableStats:
    """Summary statistics for a variable.

    Attributes:
        name: Variable name
        n: Number of non-missing observations
        mean: Mean value
        std: Standard deviation
        min: Minimum value
        p25: 25th percentile
        median: Median (50th percentile)
        p75: 75th percentile
        max: Maximum value
        n_missing: Number of missing observations
        pct_missing: Percentage of missing observations
    """
    name: str
    n: int
    mean: float
    std: float
    min: float
    p25: float
    median: float
    p75: float
    max: float
    n_missing: int
    pct_missing: float


@dataclass
class VariableResult:
    """Result from building a variable.

    Attributes:
        data: DataFrame with file_name and variable column(s)
        stats: Summary statistics for the main variable
        metadata: Dict with source, column name, etc.
    """
    data: pd.DataFrame
    stats: VariableStats
    metadata: Dict[str, Any]


class VariableBuilder:
    """Base class for variable builders.

    Each variable builder reads data from a configured source location
    and returns a VariableResult with data, stats, and metadata.

    Example:
        config = {
            "source": "outputs/2_Textual_Analysis/2.2_Variables/latest",
            "file_pattern": "linguistic_variables_{year}.parquet",
            "column": "Manager_QA_Uncertainty_pct"
        }
        builder = ManagerQAUncertaintyBuilder(config)
        result = builder.build(range(2002, 2019), root_path)
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration.

        Args:
            config: Dict with source, file_pattern, column, etc.
        """
        self.config = config

    def build(self, years: range, root_path: Path) -> VariableResult:
        """Build the variable for all years.

        Args:
            years: Range of years to process
            root_path: Project root path

        Returns:
            VariableResult with data, stats, and metadata

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement build()")

    def get_stats(self, series: pd.Series, name: str) -> VariableStats:
        """Compute summary statistics for a series.

        Args:
            series: pandas Series to compute stats for
            name: Variable name for stats

        Returns:
            VariableStats with summary statistics
        """
        # Drop NA values for stats computation
        clean = series.dropna()
        n = len(clean)
        n_missing = series.isna().sum()
        total = len(series)

        if n == 0:
            # All missing values
            return VariableStats(
                name=name,
                n=0,
                mean=np.nan,
                std=np.nan,
                min=np.nan,
                p25=np.nan,
                median=np.nan,
                p75=np.nan,
                max=np.nan,
                n_missing=n_missing,
                pct_missing=100.0 if total > 0 else 0.0
            )

        return VariableStats(
            name=name,
            n=n,
            mean=float(clean.mean()),
            std=float(clean.std()),
            min=float(clean.min()),
            p25=float(clean.quantile(0.25)),
            median=float(clean.median()),
            p75=float(clean.quantile(0.75)),
            max=float(clean.max()),
            n_missing=int(n_missing),
            pct_missing=100.0 * n_missing / total if total > 0 else 0.0
        )

    def _finalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply standard post-processing (winsorization) after data loading.

        Subclasses should call this after combining all years' data:
            combined = pd.concat(all_data, ignore_index=True)
            combined = self._finalize_data(combined)  # <-- Add this line

        Only applies winsorization if self.column is set and exists in df.
        Skips if self._skip_winsorization is True.
        """
        # Skip if explicitly disabled or column not set
        if getattr(self, '_skip_winsorization', False):
            return df
        if not hasattr(self, 'column') or not self.column:
            return df
        if self.column not in df.columns:
            return df

        from .winsorization import winsorize_pooled
        df = winsorize_pooled(df, [self.column])
        return df

    def resolve_source_dir(self, root_path: Path) -> Path:
        """Resolve source directory to the timestamp subdirectory with most files.

        Pipeline scripts output to timestamped subdirectories like:
            outputs/1.4_AssembleManifest/2026-02-19_120000/
            outputs/2_Textual_Analysis/2.2_Variables/2026-02-19_120000/

        This method finds the subdirectory containing the most matching files
        based on file_pattern (for year-partitioned data) or file_name (for
        single files like the manifest).

        Args:
            root_path: Project root path

        Returns:
            Resolved Path to the best timestamp subdirectory, or source_path
            if no subdirectories exist.
        """
        source = self.config.get("source", "")
        source_path = root_path / source

        # If source path doesn't exist, return it as-is (will fail later)
        if not source_path.exists():
            return source_path

        # Check if source_path is already a leaf directory (no subdirectories)
        # or if it directly contains the target file
        file_name = self.config.get("file_name", "")
        file_pattern = self.config.get("file_pattern", "")

        # If file_name is specified and exists directly in source_path, use it
        if file_name and (source_path / file_name).exists():
            return source_path

        # If file_pattern matches files directly in source_path, use it
        if file_pattern:
            glob_pattern = file_pattern.replace("{year}", "*")
            direct_matches = list(source_path.glob(glob_pattern))
            if direct_matches:
                return source_path

        # Otherwise, look for timestamp subdirectories
        try:
            subdirs = sorted(
                [d for d in source_path.iterdir() if d.is_dir()],
                key=lambda x: x.name,
                reverse=True  # Most recent first
            )

            if not subdirs:
                return source_path

            # Find the subdirectory with the MOST matching files
            best_dir = None
            best_count = 0

            for subdir in subdirs:
                count = 0

                if file_name:
                    # Check for single file
                    if (subdir / file_name).exists():
                        count = 1
                elif file_pattern:
                    # Check for pattern-matched files
                    glob_pattern = file_pattern.replace("{year}", "*")
                    count = len(list(subdir.glob(glob_pattern)))
                else:
                    # No specific file config, just count all parquet files
                    count = len(list(subdir.glob("*.parquet")))

                if count > best_count:
                    best_count = count
                    best_dir = subdir

            if best_dir and best_count > 0:
                return best_dir

            # Fallback: return the most recent subdirectory even if empty
            if subdirs:
                return subdirs[0]

        except Exception:
            pass

        return source_path

    def load_year_file(self, source_dir: Path, year: int) -> Optional[pd.DataFrame]:
        """Load a single year's data file.

        Args:
            source_dir: Directory containing year files
            year: Year to load

        Returns:
            DataFrame or None if file doesn't exist
        """
        file_pattern = self.config.get("file_pattern", "")
        file_path = source_dir / file_pattern.format(year=year)

        if not file_path.exists():
            return None

        return pd.read_parquet(file_path)


def stats_to_dict(stats: VariableStats) -> Dict[str, Any]:
    """Convert VariableStats to dictionary.

    Args:
        stats: VariableStats instance

    Returns:
        Dictionary representation
    """
    return asdict(stats)


def stats_list_to_dataframe(stats_list: List[Any]) -> pd.DataFrame:
    """Convert list of VariableStats or dicts to DataFrame.

    Args:
        stats_list: List of VariableStats instances or dicts

    Returns:
        DataFrame with one row per variable
    """
    records = []
    for s in stats_list:
        if isinstance(s, dict):
            records.append(s)
        else:
            records.append(asdict(s))
    return pd.DataFrame(records)


__all__ = [
    "VariableStats",
    "VariableResult",
    "VariableBuilder",
    "stats_to_dict",
    "stats_list_to_dataframe",
]
