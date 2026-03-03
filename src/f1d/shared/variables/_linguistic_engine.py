"""Private Linguistic compute engine.

Loads Stage 2 linguistic variables (uncertainty, sentiment, modal percentages)
from year-partitioned parquet files, applies per-year winsorization to all
percentage columns, and caches the result.

All linguistic variable builders (ManagerQAUncertaintyBuilder, CEOQAPositiveBuilder,
etc.) query this singleton engine rather than loading files individually.

NOT a VariableBuilder — this is an internal helper.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# All percentage columns from Stage 2 that need per-year winsorization
# These are the columns that end with _pct in linguistic_variables_{year}.parquet
#
# NOTE: This list must be kept in sync with Stage 2 output schema.
# If new _pct columns are added to Stage 2, update this list to ensure they are winsorized.
# A fallback dynamic detection is used in get_data() to catch any _pct columns
# not in this list.
LINGUISTIC_PCT_COLUMNS = [
    # Analyst
    "Analyst_All_Constraining_pct",
    "Analyst_All_Litigious_pct",
    "Analyst_All_Negative_pct",
    "Analyst_All_Positive_pct",
    "Analyst_All_Strong_Modal_pct",
    "Analyst_All_Uncertainty_pct",
    "Analyst_All_Weak_Modal_pct",
    "Analyst_Pres_Constraining_pct",
    "Analyst_Pres_Litigious_pct",
    "Analyst_Pres_Negative_pct",
    "Analyst_Pres_Positive_pct",
    "Analyst_Pres_Strong_Modal_pct",
    "Analyst_Pres_Uncertainty_pct",
    "Analyst_Pres_Weak_Modal_pct",
    "Analyst_QA_Constraining_pct",
    "Analyst_QA_Litigious_pct",
    "Analyst_QA_Negative_pct",
    "Analyst_QA_Positive_pct",
    "Analyst_QA_Strong_Modal_pct",
    "Analyst_QA_Uncertainty_pct",
    "Analyst_QA_Weak_Modal_pct",
    # CEO
    "CEO_All_Constraining_pct",
    "CEO_All_Litigious_pct",
    "CEO_All_Negative_pct",
    "CEO_All_Positive_pct",
    "CEO_All_Strong_Modal_pct",
    "CEO_All_Uncertainty_pct",
    "CEO_All_Weak_Modal_pct",
    "CEO_Pres_Constraining_pct",
    "CEO_Pres_Litigious_pct",
    "CEO_Pres_Negative_pct",
    "CEO_Pres_Positive_pct",
    "CEO_Pres_Strong_Modal_pct",
    "CEO_Pres_Uncertainty_pct",
    "CEO_Pres_Weak_Modal_pct",
    "CEO_QA_Constraining_pct",
    "CEO_QA_Litigious_pct",
    "CEO_QA_Negative_pct",
    "CEO_QA_Positive_pct",
    "CEO_QA_Strong_Modal_pct",
    "CEO_QA_Uncertainty_pct",
    "CEO_QA_Weak_Modal_pct",
    # Entire
    "Entire_All_Constraining_pct",
    "Entire_All_Litigious_pct",
    "Entire_All_Negative_pct",
    "Entire_All_Positive_pct",
    "Entire_All_Strong_Modal_pct",
    "Entire_All_Uncertainty_pct",
    "Entire_All_Weak_Modal_pct",
    "Entire_Pres_Constraining_pct",
    "Entire_Pres_Litigious_pct",
    "Entire_Pres_Negative_pct",
    "Entire_Pres_Positive_pct",
    "Entire_Pres_Strong_Modal_pct",
    "Entire_Pres_Uncertainty_pct",
    "Entire_Pres_Weak_Modal_pct",
    "Entire_QA_Constraining_pct",
    "Entire_QA_Litigious_pct",
    "Entire_QA_Negative_pct",
    "Entire_QA_Positive_pct",
    "Entire_QA_Strong_Modal_pct",
    "Entire_QA_Uncertainty_pct",
    "Entire_QA_Weak_Modal_pct",
    # Manager
    "Manager_All_Constraining_pct",
    "Manager_All_Litigious_pct",
    "Manager_All_Negative_pct",
    "Manager_All_Positive_pct",
    "Manager_All_Strong_Modal_pct",
    "Manager_All_Uncertainty_pct",
    "Manager_All_Weak_Modal_pct",
    "Manager_Pres_Constraining_pct",
    "Manager_Pres_Litigious_pct",
    "Manager_Pres_Negative_pct",
    "Manager_Pres_Positive_pct",
    "Manager_Pres_Strong_Modal_pct",
    "Manager_Pres_Uncertainty_pct",
    "Manager_Pres_Weak_Modal_pct",
    "Manager_QA_Constraining_pct",
    "Manager_QA_Litigious_pct",
    "Manager_QA_Negative_pct",
    "Manager_QA_Positive_pct",
    "Manager_QA_Strong_Modal_pct",
    "Manager_QA_Uncertainty_pct",
    "Manager_QA_Weak_Modal_pct",
    # NonCEO_Manager
    "NonCEO_Manager_All_Constraining_pct",
    "NonCEO_Manager_All_Litigious_pct",
    "NonCEO_Manager_All_Negative_pct",
    "NonCEO_Manager_All_Positive_pct",
    "NonCEO_Manager_All_Strong_Modal_pct",
    "NonCEO_Manager_All_Uncertainty_pct",
    "NonCEO_Manager_All_Weak_Modal_pct",
    "NonCEO_Manager_Pres_Constraining_pct",
    "NonCEO_Manager_Pres_Litigious_pct",
    "NonCEO_Manager_Pres_Negative_pct",
    "NonCEO_Manager_Pres_Positive_pct",
    "NonCEO_Manager_Pres_Strong_Modal_pct",
    "NonCEO_Manager_Pres_Uncertainty_pct",
    "NonCEO_Manager_Pres_Weak_Modal_pct",
    "NonCEO_Manager_QA_Constraining_pct",
    "NonCEO_Manager_QA_Litigious_pct",
    "NonCEO_Manager_QA_Negative_pct",
    "NonCEO_Manager_QA_Positive_pct",
    "NonCEO_Manager_QA_Strong_Modal_pct",
    "NonCEO_Manager_QA_Uncertainty_pct",
    "NonCEO_Manager_QA_Weak_Modal_pct",
]


class LinguisticEngine:
    """Load Stage 2 linguistic variables, apply winsorization, cache result.

    Usage:
        engine = LinguisticEngine()
        df = engine.get_data(root_path, years)
        # df has columns: file_name, Manager_QA_Uncertainty_pct, CEO_QA_Positive_pct, ...

    The result is cached after the first call — subsequent calls with the same
    root_path return the cached DataFrame immediately.
    """

    def __init__(self) -> None:
        self._cache: Optional[pd.DataFrame] = None
        self._cache_root: Optional[Path] = None
        self._lock = threading.Lock()

    def _is_cached(self, root_path: Path) -> bool:
        return self._cache is not None and self._cache_root == root_path

    def get_data(
        self,
        root_path: Path,
        years: range,
    ) -> pd.DataFrame:
        """Return fully-loaded linguistic variables DataFrame (cached).

        Loads all linguistic variables from Stage 2 outputs, applies per-year
        0%/99% winsorization (upper-only) to all percentage columns, and caches the result.

        Args:
            root_path: Project root path
            years: Range of years to load

        Returns:
            DataFrame with file_name + all linguistic percentage columns,
            winsorized at 0%/99% (upper-only) per-year.
        """
        # Fast path — no lock needed
        if self._is_cached(root_path):
            return self._cache  # type: ignore[return-value]

        with self._lock:
            # Re-check inside the lock
            if self._is_cached(root_path):
                return self._cache  # type: ignore[return-value]

            # Find the latest timestamp subdirectory
            source_base = root_path / "outputs" / "2_Textual_Analysis" / "2.2_Variables"
            source_dir = self._find_latest_subdir(source_base)

            if source_dir is None:
                logger.warning(
                    f"LinguisticEngine: No data found at {source_base}. "
                    "Returning empty DataFrame."
                )
                self._cache = pd.DataFrame(columns=["file_name"] + LINGUISTIC_PCT_COLUMNS)
                self._cache_root = root_path
                return self._cache

            logger.info(f"LinguisticEngine: Loading from {source_dir}")

            # Load all year files - add year column from filename (not from file_name column)
            all_data: List[pd.DataFrame] = []
            for year in years:
                fp = source_dir / f"linguistic_variables_{year}.parquet"
                if fp.exists():
                    try:
                        df = pd.read_parquet(fp)
                        # Year comes from the parquet filename, not from extracting file_name pattern
                        if "year" not in df.columns:
                            df["year"] = year
                        all_data.append(df)
                        logger.info(f"  Loaded {year}: {len(df):,} rows")
                    except Exception as e:
                        logger.warning(f"  Error loading {fp}: {e}")

            if not all_data:
                logger.warning(
                    f"LinguisticEngine: No year files found for years {years.start}-{years.stop}. "
                    "Returning empty DataFrame."
                )
                self._cache = pd.DataFrame(columns=["file_name"] + LINGUISTIC_PCT_COLUMNS)
                self._cache_root = root_path
                return self._cache

            # Concat all years
            combined = pd.concat(all_data, ignore_index=True)
            logger.info(f"  Combined: {len(combined):,} rows, {len(combined.columns)} columns")

            # === WINSORIZATION: Per-year 0%/99% (upper-only) for all percentage columns ===
            # Per-year winsorization ensures "high for that year" semantics and handles
            # any potential language evolution or regime-dependent communication patterns
            from .winsorization import winsorize_by_year

            # Find which percentage columns actually exist in the data
            existing_pct_cols = [c for c in LINGUISTIC_PCT_COLUMNS if c in combined.columns]

            # Fallback: detect any _pct columns in data not in the hardcoded list
            dynamic_pct_cols = [c for c in combined.columns
                                if c.endswith("_pct") and c not in existing_pct_cols]
            if dynamic_pct_cols:
                logger.warning(
                    f"LinguisticEngine: Found {len(dynamic_pct_cols)} _pct columns not in "
                    f"LINGUISTIC_PCT_COLUMNS: {dynamic_pct_cols[:5]}{'...' if len(dynamic_pct_cols) > 5 else ''}. "
                    f"These will also be winsorized. Consider updating LINGUISTIC_PCT_COLUMNS."
                )
                existing_pct_cols.extend(dynamic_pct_cols)

            if existing_pct_cols:
                combined = winsorize_by_year(
                    combined, existing_pct_cols, year_col="year",
                    lower=0.0, upper=0.99, min_obs=10  # Harmonized with Compustat/CRSP engines
                )
                logger.info(f"  Winsorized {len(existing_pct_cols)} percentage columns (per-year 0%/99% upper-only)")
            # === END WINSORIZATION ===

            self._cache = combined
            self._cache_root = root_path
            return combined

    def _find_latest_subdir(self, source_base: Path) -> Optional[Path]:
        """Find the timestamp subdirectory with the most parquet files."""
        if not source_base.exists():
            return None

        # Check if source_base directly contains the files
        direct_files = list(source_base.glob("linguistic_variables_*.parquet"))
        if direct_files:
            return source_base

        # Look for timestamp subdirectories
        try:
            subdirs = sorted(
                [d for d in source_base.iterdir() if d.is_dir()],
                key=lambda x: x.name,
                reverse=True  # Most recent first
            )

            if not subdirs:
                return None

            # Find the subdirectory with the most matching files
            best_dir = None
            best_count = 0

            for subdir in subdirs:
                count = len(list(subdir.glob("linguistic_variables_*.parquet")))
                if count > best_count:
                    best_count = count
                    best_dir = subdir

            if best_dir and best_count > 0:
                return best_dir

            # Fallback: return the most recent subdirectory even if empty
            return subdirs[0] if subdirs else None

        except Exception:
            return None


# Module-level singleton — shared across all linguistic builders in one process
_engine = LinguisticEngine()


def get_engine() -> LinguisticEngine:
    """Return the module-level singleton engine."""
    return _engine


__all__ = ["LinguisticEngine", "LINGUISTIC_PCT_COLUMNS", "get_engine"]
