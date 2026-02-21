"""
Singleton engine for loading and caching IBES Analyst Forecast data.

This engine handles the chunked reading of the massive (~25M row) tr_ibes.parquet
file, filters for valid EPS estimates, computes analyst dispersion and earnings
surprise, and links CUSIP8 to GVKEY via the CRSP-Compustat Merged (CCM) table.

It aggregates data down to the (gvkey, fiscal_year, fiscal_quarter) level to
serve the H5 Analyst Dispersion hypothesis.
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

# The global singleton instance
_IBES_ENGINE_INSTANCE: Optional[IbesEngine] = None
_IBES_ENGINE_LOCK = threading.Lock()


class IbesEngine:
    """Central engine for loading, processing, and caching IBES quarterly data."""

    def __init__(self) -> None:
        self._cache: Optional[pd.DataFrame] = None
        self._cache_root: Optional[Path] = None

        # Configuration thresholds based on standard literature (e.g. Diether et al 2002)
        self.numest_min = 3
        self.meanest_min = 0.05

    def get_data(self, root_path: Path) -> pd.DataFrame:
        """Get the processed IBES panel, computing and caching it on first call."""
        if self._cache is not None and self._cache_root == root_path:
            return self._cache

        print(f"    IbesEngine: Initializing and loading data...")
        self._cache = self._build_ibes_panel(root_path)
        self._cache_root = root_path
        return self._cache

    def _build_ibes_panel(self, root_path: Path) -> pd.DataFrame:
        ibes_path = root_path / "inputs" / "tr_ibes" / "tr_ibes.parquet"
        ccm_path = (
            root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
        )

        if not ibes_path.exists():
            raise FileNotFoundError(f"IBES data not found at {ibes_path}")
        if not ccm_path.exists():
            raise FileNotFoundError(f"CCM linking data not found at {ccm_path}")

        # 1. Load CCM for linking
        print(f"    IbesEngine: Loading CCM linking table...")
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

        # 2. Process IBES in chunks with predicate pushdown
        print(f"    IbesEngine: Processing IBES in chunks with predicate pushdown...")
        import pyarrow.dataset as ds
        import pyarrow.compute as pc

        cols = [
            "CUSIP",
            "STATPERS",
            "FPEDATS",
            "FISCALP",
            "MEASURE",
            "NUMEST",
            "MEANEST",
            "STDEV",
            "ACTUAL",
        ]

        all_chunks = []

        # Use pyarrow.dataset for predicate pushdown
        dataset = ds.dataset(ibes_path, format="parquet")

        # Filter at I/O level
        # MEASURE == "EPS" and FISCALP == "QTR" and NUMEST >= 3
        filter_expr = (
            (pc.field("MEASURE") == "EPS")
            & (pc.field("FISCALP") == "QTR")
            & (pc.field("NUMEST") >= self.numest_min)
        )

        for batch in dataset.to_batches(columns=cols, filter=filter_expr):
            chunk = batch.to_pandas()

            # Apply remaining filters
            chunk = chunk[(chunk["MEANEST"].abs() >= self.meanest_min)].copy()

            chunk = chunk.dropna(
                subset=["STDEV", "MEANEST", "FPEDATS", "CUSIP", "ACTUAL"]
            )
            if len(chunk) == 0:
                continue

            chunk["cusip8"] = chunk["CUSIP"].astype(str).str[:8]
            chunk = chunk[~chunk["cusip8"].isin(["00000000", "nan", "NaN", "None"])]
            if len(chunk) == 0:
                continue

            # Link to gvkey immediately to reduce size
            chunk["gvkey"] = chunk["cusip8"].map(cusip_to_gvkey)
            chunk = chunk.dropna(subset=["gvkey"]).copy()

            # Extract STATPERS (Statistical Period - the date the consensus was formed)
            chunk["statpers"] = pd.to_datetime(chunk["STATPERS"], errors="coerce")
            chunk = chunk.dropna(subset=["statpers"])

            # Compute variables
            chunk["dispersion"] = chunk["STDEV"] / chunk["MEANEST"].abs()
            chunk["earnings_surprise_ratio"] = (
                chunk["ACTUAL"] - chunk["MEANEST"]
            ).abs() / chunk["MEANEST"].abs()

            # Compute days to target to find the nearest upcoming forecast
            chunk["fpedats"] = pd.to_datetime(chunk["FPEDATS"], errors="coerce")
            chunk["days_to_target"] = (chunk["fpedats"] - chunk["statpers"]).dt.days
            chunk = chunk[chunk["days_to_target"] >= 0].copy()

            # We DO NOT aggregate away statpers! We need the actual forecast date to match against earnings calls.
            # We keep all valid consensus months. To save memory, keep only necessary cols.
            chunk_agg = chunk[
                [
                    "gvkey",
                    "statpers",
                    "days_to_target",
                    "dispersion",
                    "earnings_surprise_ratio",
                ]
            ].copy()
            all_chunks.append(chunk_agg)

        if not all_chunks:
            raise ValueError("IBES processing resulted in empty dataframe.")

        df = pd.concat(all_chunks, ignore_index=True)

        # Deduplicate: keep the closest forecast target (smallest days_to_target)
        df = df.sort_values(["gvkey", "statpers", "days_to_target"])
        df = df.drop_duplicates(subset=["gvkey", "statpers"], keep="first")
        df = df.drop(columns=["days_to_target"]).reset_index(drop=True)

        # 3. Winsorize globally (since we dropped year grouping to avoid calendar mismatches)
        for col in ["dispersion", "earnings_surprise_ratio"]:
            p1 = df[col].quantile(0.01)
            p99 = df[col].quantile(0.99)
            df[col] = df[col].clip(lower=p1, upper=p99)

        print(
            f"    IbesEngine: Built final panel with {len(df):,} gvkey-statpers rows."
        )
        return df


def get_engine() -> IbesEngine:
    """Get or create the global IbesEngine instance (thread-safe)."""
    global _IBES_ENGINE_INSTANCE
    if _IBES_ENGINE_INSTANCE is None:
        with _IBES_ENGINE_LOCK:
            if _IBES_ENGINE_INSTANCE is None:
                _IBES_ENGINE_INSTANCE = IbesEngine()
    return _IBES_ENGINE_INSTANCE
