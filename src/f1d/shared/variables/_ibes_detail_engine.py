"""Singleton engine for loading and caching IBES Detail data (individual analyst estimates).

This engine handles the loading of yearly IBES Detail parquet files containing
individual analyst estimates (not pre-aggregated consensus data). It provides
the data needed to compute dispersion at specific point-in-time dates.

Key differences from _ibes_engine.py:
    - Uses IBES Detail data (individual estimates) instead of Summary (consensus)
    - Loads yearly files: tr_ibes_YYYY.parquet instead of single tr_ibes.parquet
    - Computes dispersion from raw estimates on-demand at specific dates
    - Supports stale estimate filtering (max_age_days)

Data Structure (IBES Detail):
    - ~10M rows/year (individual analyst estimates)
    - Key columns: CUSIP, ACTDATS, ANALYS, VALUE, MEASURE, FPI, FPEDATS
    - Filter to EPS quarterly: ~320K rows/year

Usage:
    from f1d.shared.variables._ibes_detail_engine import get_engine

    engine = get_engine()
    df = engine.get_data(root_path, range(2015, 2019))
    # Returns: DataFrame with gvkey, actdats, analys, value, fpedats, actual
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

# Column name constants (ALL UPPERCASE in IBES Detail)
COLUMNS = {
    'cusip': 'CUSIP',
    'actdats': 'ACTDATS',  # STRING type - must convert to datetime!
    'analys': 'ANALYS',
    'value': 'VALUE',
    'measure': 'MEASURE',
    'fpi': 'FPI',
    'fpedats': 'FPEDATS',
    'pdf': 'PDF',  # Primary/Diluted flag
}

# The global singleton instance
_IBES_DETAIL_ENGINE_INSTANCE: Optional[IbesDetailEngine] = None
_IBES_DETAIL_ENGINE_LOCK = threading.Lock()


class IbesDetailEngine:
    """Central engine for loading IBES Detail data with individual analyst estimates."""

    def __init__(self) -> None:
        self._cache: Optional[pd.DataFrame] = None
        self._cache_root: Optional[Path] = None
        self._cache_years: Optional[range] = None

        # Configuration
        self.numest_min = 2  # Minimum analysts for valid dispersion
        self.fpi_valid = ['6', '7']  # FPI 6 = current quarter, 7 = next quarter (both needed: FPI is relative to estimate date, not call date)
        self.pdf_valid = ['D']  # Diluted EPS only
        self.max_stale_days = 180  # Stale estimate filter (days)

    def get_data(self, root_path: Path, years: range) -> pd.DataFrame:
        """Get the processed IBES Detail panel, loading and caching on first call.

        Args:
            root_path: Project root path
            years: Range of years to load

        Returns:
            DataFrame with columns: gvkey, actdats, analys, value, fpedats
        """
        if (self._cache is not None and
            self._cache_root == root_path and
            self._cache_years == years and
            getattr(self, '_cache_fpi', None) == self.fpi_valid and
            getattr(self, '_cache_pdf', None) == self.pdf_valid):
            return self._cache

        print(f"    IbesDetailEngine: Loading IBES Detail data for years {years.start}-{years.stop-1}...")
        print(f"    IbesDetailEngine: FPI={self.fpi_valid}, PDF={self.pdf_valid}")
        self._cache = self._build_ibes_detail_panel(root_path, years)
        self._cache_root = root_path
        self._cache_years = years
        self._cache_fpi = list(self.fpi_valid)
        self._cache_pdf = list(self.pdf_valid)
        return self._cache

    def _build_ibes_detail_panel(self, root_path: Path, years: range) -> pd.DataFrame:
        """Build the IBES Detail panel from yearly files.

        Args:
            root_path: Project root path
            years: Range of years to load

        Returns:
            DataFrame with individual analyst estimates linked to GVKEY
        """
        ibes_dir = root_path / "inputs" / "tr_ibes"
        ccm_path = root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"

        if not ccm_path.exists():
            raise FileNotFoundError(f"CCM linking data not found at {ccm_path}")

        # 1. Load CCM for linking
        print(f"    IbesDetailEngine: Loading CCM linking table...")
        ccm = pd.read_parquet(
            ccm_path, columns=["cusip", "LPERMNO", "gvkey", "LINKPRIM"]
        )
        ccm["cusip8"] = ccm["cusip"].astype(str).str[:8]
        ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)

        # Use primary links ('P' or 'C')
        ccm_primary = ccm[ccm["LINKPRIM"].isin(["P", "C"])].copy()
        cusip_to_gvkey = ccm_primary.drop_duplicates(
            subset=["cusip8"], keep="first"
        ).set_index("cusip8")["gvkey"]

        print(f"    IbesDetailEngine: CCM has {len(cusip_to_gvkey):,} unique CUSIP8 -> GVKEY mappings")

        # 2. Load yearly IBES Detail files
        import pyarrow.dataset as ds
        import pyarrow.compute as pc

        cols = [
            COLUMNS['cusip'],
            COLUMNS['actdats'],
            COLUMNS['analys'],
            COLUMNS['value'],
            COLUMNS['measure'],
            COLUMNS['fpi'],
            COLUMNS['fpedats'],
            COLUMNS['pdf'],
            'ACTUAL',  # Include ACTUAL for earnings surprise builders
        ]

        all_chunks = []

        for year in years:
            year_file = ibes_dir / f"tr_ibes_{year}.parquet"
            if not year_file.exists():
                print(f"    IbesDetailEngine: WARNING - File not found: {year_file}")
                continue

            print(f"    IbesDetailEngine: Processing {year_file.name}...")
            chunk = self._load_year_file(year_file, cols, cusip_to_gvkey)
            if chunk is not None and len(chunk) > 0:
                all_chunks.append(chunk)
                print(f"      -> {len(chunk):,} rows after filtering")

        if not all_chunks:
            raise ValueError("IBES Detail processing resulted in empty dataframe.")

        df = pd.concat(all_chunks, ignore_index=True)

        print(f"    IbesDetailEngine: Built final panel with {len(df):,} rows.")
        return df

    def _load_year_file(
        self,
        file_path: Path,
        cols: list,
        cusip_to_gvkey: pd.Series
    ) -> Optional[pd.DataFrame]:
        """Load a single year's IBES Detail file with filters applied.

        Args:
            file_path: Path to yearly parquet file
            cols: Columns to load
            cusip_to_gvkey: CUSIP8 to GVKEY mapping

        Returns:
            Filtered DataFrame or None if empty
        """
        import pyarrow.dataset as ds
        import pyarrow.compute as pc

        # Use pyarrow.dataset for predicate pushdown
        dataset = ds.dataset(file_path, format="parquet")

        # Filter at I/O level: MEASURE == "EPS", FPI filter, PDF filter
        filter_expr = (
            (pc.field(COLUMNS['measure']) == "EPS")
            & (pc.field(COLUMNS['fpi']).isin(self.fpi_valid))
            & (pc.field(COLUMNS['pdf']).isin(self.pdf_valid))
        )

        try:
            table = dataset.to_table(columns=cols, filter=filter_expr)
            chunk = table.to_pandas()
        except Exception as e:
            print(f"    IbesDetailEngine: Error loading {file_path}: {e}")
            return None

        if len(chunk) == 0:
            return None

        # Drop rows with missing critical values
        chunk = chunk.dropna(subset=[
            COLUMNS['cusip'],
            COLUMNS['actdats'],
            COLUMNS['analys'],
            COLUMNS['value'],
            COLUMNS['fpedats']
        ])

        if len(chunk) == 0:
            return None

        # Convert CUSIP to 8-character string
        chunk['cusip8'] = chunk[COLUMNS['cusip']].astype(str).str[:8]
        chunk = chunk[~chunk['cusip8'].isin(["00000000", "nan", "NaN", "None", ""])]
        if len(chunk) == 0:
            return None

        # Link to gvkey
        chunk['gvkey'] = chunk['cusip8'].map(cusip_to_gvkey)
        chunk = chunk.dropna(subset=['gvkey']).copy()

        if len(chunk) == 0:
            return None

        # Convert ACTDATS from STRING to datetime
        chunk['actdats'] = pd.to_datetime(chunk[COLUMNS['actdats']], errors='coerce')
        chunk = chunk.dropna(subset=['actdats'])

        # Convert FPEDATS from STRING to datetime
        chunk['fpedats'] = pd.to_datetime(chunk[COLUMNS['fpedats']], errors='coerce')
        chunk = chunk.dropna(subset=['fpedats'])

        # Rename to lowercase for consistency
        chunk['analys'] = chunk[COLUMNS['analys']]
        chunk['value'] = chunk[COLUMNS['value']]

        # Include ACTUAL if available in source data
        out_cols = ['gvkey', 'actdats', 'analys', 'value', 'fpedats']
        if 'ACTUAL' in chunk.columns:
            chunk['actual'] = pd.to_numeric(chunk['ACTUAL'], errors='coerce')
            out_cols.append('actual')

        chunk = chunk[out_cols].copy()

        return chunk

    def compute_dispersion_at_date(
        self,
        estimates: pd.DataFrame,
        target_date: pd.Timestamp,
        max_age_days: int = 180
    ) -> Optional[float]:
        """Compute cross-sectional dispersion at a specific date.

        This method takes a set of estimates for a company/quarter and computes
        dispersion as of a specific target date, using only estimates that were
        active on or before that date.

        Args:
            estimates: DataFrame with actdats, analys, value for a single gvkey/fpedats
            target_date: The date at which to compute dispersion
            max_age_days: Maximum age of estimates to include (stale filter)

        Returns:
            Dispersion = STDEV(VALUE) / |MEAN(VALUE)|, or None if insufficient data

        Algorithm:
            1. Filter to estimates active on/before target_date
            2. Apply stale estimate filter (max_age_days)
            3. Keep most recent estimate per analyst
            4. Require minimum 2 analysts
            5. Compute dispersion = STDEV / |MEAN|
        """
        if estimates is None or len(estimates) == 0:
            return None

        # Step 1: Filter to estimates active on/before target_date
        active = estimates[estimates['actdats'] <= target_date].copy()

        if len(active) == 0:
            return None

        # Step 2: Apply stale estimate filter
        # Only use estimates updated within max_age_days of target date
        if max_age_days > 0:
            age_days = (target_date - active['actdats']).dt.days
            active = active[age_days <= max_age_days].copy()

        if len(active) == 0:
            return None

        # Step 3: Keep most recent estimate per analyst
        active = active.sort_values('actdats').groupby('analys').last().reset_index()

        # Step 4: Require minimum 2 analysts
        if len(active) < self.numest_min:
            return None

        # Step 5: Compute dispersion = STDEV / |MEAN|
        values = active['value']
        mean_val = values.mean()

        if mean_val == 0 or np.isnan(mean_val):
            return None

        stdev_val = values.std()
        if np.isnan(stdev_val):
            return None

        dispersion = stdev_val / abs(mean_val)

        return dispersion


def get_engine() -> IbesDetailEngine:
    """Get or create the global IbesDetailEngine instance (thread-safe)."""
    global _IBES_DETAIL_ENGINE_INSTANCE
    if _IBES_DETAIL_ENGINE_INSTANCE is None:
        with _IBES_DETAIL_ENGINE_LOCK:
            if _IBES_DETAIL_ENGINE_INSTANCE is None:
                _IBES_DETAIL_ENGINE_INSTANCE = IbesDetailEngine()
    return _IBES_DETAIL_ENGINE_INSTANCE


__all__ = ["IbesDetailEngine", "get_engine", "COLUMNS"]
