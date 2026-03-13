"""
Singleton engine for loading and caching IBES Analyst Forecast data.

Computes consensus summary statistics (NUMEST, MEANEST, STDEV, dispersion,
earnings surprise) from yearly IBES Detail parquet files and links CUSIP8
to GVKEY via the CRSP-Compustat Merged (CCM) table.

Input: inputs/tr_ibes/tr_ibes_YYYY.parquet  (yearly detail-level files)
Output columns: gvkey, statpers, fpedats, dispersion, earnings_surprise_ratio,
                surprise_raw, meanest, actual, numest

Data flow:
    1. Load yearly IBES Detail files (individual analyst estimates)
    2. Filter to EPS quarterly: MEASURE == "EPS", FPI in ['6', '7']
    3. Link CUSIP to GVKEY via CCM
    4. For each (gvkey, FPEDATS): keep most recent estimate per analyst,
       compute NUMEST, MEANEST, STDEV, dispersion, surprise
    5. Winsorize dispersion and earnings_surprise_ratio at 1%/99%
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd

# The global singleton instance
_IBES_ENGINE_INSTANCE: Optional[IbesEngine] = None
_IBES_ENGINE_LOCK = threading.Lock()


class IbesEngine:
    """Central engine for loading, processing, and caching IBES quarterly data."""

    def __init__(self) -> None:
        self._cache: Optional[pd.DataFrame] = None
        self._cache_root: Optional[Path] = None

        # Configuration thresholds based on standard literature (e.g. Diether et al 2002)
        self.numest_min = 2
        self.meanest_min = 0.05
        self.fpi_valid = ["6", "7"]  # FPI 6 = current quarter, 7 = next quarter
        self.max_stale_days = 180

    def get_data(self, root_path: Path) -> pd.DataFrame:
        """Get the processed IBES panel, computing and caching it on first call."""
        if self._cache is not None and self._cache_root == root_path:
            return self._cache

        print("    IbesEngine: Initializing and loading data...")
        self._cache = self._build_ibes_panel(root_path)
        self._cache_root = root_path
        return self._cache

    def _build_ibes_panel(self, root_path: Path) -> pd.DataFrame:
        ibes_dir = root_path / "inputs" / "tr_ibes"
        ccm_path = (
            root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
        )

        if not ccm_path.exists():
            raise FileNotFoundError(f"CCM linking data not found at {ccm_path}")

        # 1. Load CCM for linking
        print("    IbesEngine: Loading CCM linking table...")
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

        print(f"    IbesEngine: CCM has {len(cusip_to_gvkey):,} unique CUSIP8 -> GVKEY mappings")

        # 2. Load yearly detail files and compute consensus per (gvkey, fpedats)
        import pyarrow.compute as pc
        import pyarrow.dataset as ds

        detail_cols = ["CUSIP", "ACTDATS", "ANALYS", "VALUE", "MEASURE", "FPI", "FPEDATS", "ACTUAL"]
        all_chunks: List[pd.DataFrame] = []

        year_files = sorted(ibes_dir.glob("tr_ibes_*.parquet"))
        if not year_files:
            raise FileNotFoundError(f"No IBES yearly files found in {ibes_dir}")

        for year_file in year_files:
            print(f"    IbesEngine: Processing {year_file.name}...")
            chunk = self._load_detail_year(year_file, detail_cols, cusip_to_gvkey, pc, ds)
            if chunk is not None and len(chunk) > 0:
                all_chunks.append(chunk)
                print(f"      -> {len(chunk):,} rows after filtering")

        if not all_chunks:
            raise ValueError("IBES processing resulted in empty dataframe.")

        df = pd.concat(all_chunks, ignore_index=True)
        print(f"    IbesEngine: {len(df):,} total estimate rows loaded")

        # 3. Compute consensus per (gvkey, fpedats)
        consensus = self._compute_consensus(df)

        # 4. Winsorize globally
        for col in ["dispersion", "earnings_surprise_ratio"]:
            p1 = consensus[col].quantile(0.01)
            p99 = consensus[col].quantile(0.99)
            consensus[col] = consensus[col].clip(lower=p1, upper=p99)

        print(
            f"    IbesEngine: Built final panel with {len(consensus):,} gvkey-fpedats rows."
        )
        return consensus

    def _load_detail_year(
        self,
        file_path: Path,
        cols: list,
        cusip_to_gvkey: pd.Series,
        pc,
        ds,
    ) -> Optional[pd.DataFrame]:
        """Load a single year's IBES Detail file and filter to EPS quarterly."""
        dataset = ds.dataset(file_path, format="parquet")

        # Filter at I/O level: MEASURE == "EPS" and FPI in ['6', '7']
        filter_expr = (
            (pc.field("MEASURE") == "EPS")
            & (pc.field("FPI").isin(self.fpi_valid))
        )

        try:
            # Only load columns that exist in the file
            available = dataset.schema.names
            load_cols = [c for c in cols if c in available]
            table = dataset.to_table(columns=load_cols, filter=filter_expr)
            chunk = table.to_pandas()
        except Exception as e:
            print(f"    IbesEngine: Error loading {file_path}: {e}")
            return None

        if len(chunk) == 0:
            return None

        # Drop rows with missing critical values
        required = ["CUSIP", "ACTDATS", "ANALYS", "VALUE", "FPEDATS"]
        required = [c for c in required if c in chunk.columns]
        chunk = chunk.dropna(subset=required)

        if len(chunk) == 0:
            return None

        # Convert CUSIP to 8-character string and link to gvkey
        chunk["cusip8"] = chunk["CUSIP"].astype(str).str[:8]
        chunk = chunk[~chunk["cusip8"].isin(["00000000", "nan", "NaN", "None", ""])]
        chunk["gvkey"] = chunk["cusip8"].map(cusip_to_gvkey)
        chunk = chunk.dropna(subset=["gvkey"]).copy()

        if len(chunk) == 0:
            return None

        # Convert dates
        chunk["actdats"] = pd.to_datetime(chunk["ACTDATS"], errors="coerce")
        chunk["fpedats"] = pd.to_datetime(chunk["FPEDATS"], errors="coerce")
        chunk = chunk.dropna(subset=["actdats", "fpedats"])

        # Extract needed columns
        out_cols = ["gvkey", "actdats", "fpedats", "ANALYS", "VALUE"]
        if "ACTUAL" in chunk.columns:
            chunk["actual"] = pd.to_numeric(chunk["ACTUAL"], errors="coerce")
            out_cols.append("actual")
        chunk["ANALYS"] = pd.to_numeric(chunk["ANALYS"], errors="coerce")
        chunk["VALUE"] = pd.to_numeric(chunk["VALUE"], errors="coerce")

        return chunk[out_cols].copy()

    def _compute_consensus(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute consensus stats per (gvkey, fpedats) from individual estimates.

        For each fiscal period:
        1. Keep most recent estimate per analyst
        2. Apply stale filter (drop estimates >180 days from latest)
        3. Compute NUMEST, MEANEST, STDEV
        4. Derive dispersion and earnings surprise
        5. Set statpers = latest ACTDATS (when consensus was formed)
        """
        # Sort and keep most recent estimate per (gvkey, fpedats, analyst)
        df = df.sort_values(["gvkey", "fpedats", "ANALYS", "actdats"])
        df = df.drop_duplicates(subset=["gvkey", "fpedats", "ANALYS"], keep="last")

        # Apply stale filter: drop estimates older than max_stale_days from the
        # latest estimate in each (gvkey, fpedats) group
        latest_dates = df.groupby(["gvkey", "fpedats"])["actdats"].transform("max")
        stale_mask = (latest_dates - df["actdats"]).dt.days <= self.max_stale_days
        df = df[stale_mask].copy()

        # Aggregate per (gvkey, fpedats)
        has_actual = "actual" in df.columns

        agg_dict = {
            "actdats": "max",       # statpers = latest estimate date
            "VALUE": ["count", "mean", "std"],
        }
        if has_actual:
            agg_dict["actual"] = "first"  # same for all rows in group

        grouped = df.groupby(["gvkey", "fpedats"]).agg(agg_dict)
        grouped.columns = ["statpers", "numest", "meanest", "stdev"] + (
            ["actual"] if has_actual else []
        )
        grouped = grouped.reset_index()

        # Filter: require minimum estimates and non-trivial mean
        mask = (
            (grouped["numest"] >= self.numest_min)
            & (grouped["meanest"].abs() >= self.meanest_min)
            & grouped["stdev"].notna()
        )
        if has_actual:
            mask = mask & grouped["actual"].notna()
        grouped = grouped[mask].copy()

        # Compute derived variables
        grouped["dispersion"] = grouped["stdev"] / grouped["meanest"].abs()
        if has_actual:
            grouped["earnings_surprise_ratio"] = (
                (grouped["actual"] - grouped["meanest"]).abs()
                / grouped["meanest"].abs()
            )
            grouped["surprise_raw"] = grouped["actual"] - grouped["meanest"]
        else:
            grouped["earnings_surprise_ratio"] = np.nan
            grouped["surprise_raw"] = np.nan

        # Output is already one row per (gvkey, fpedats) from the groupby above.
        # No additional dedup needed — downstream builders match on fpedats directly.

        out_cols = [
            "gvkey", "statpers", "fpedats", "dispersion",
            "earnings_surprise_ratio", "surprise_raw",
            "meanest", "actual", "numest",
        ]
        out_cols = [c for c in out_cols if c in grouped.columns]
        return grouped[out_cols].reset_index(drop=True)


def get_engine() -> IbesEngine:
    """Get or create the global IbesEngine instance (thread-safe)."""
    global _IBES_ENGINE_INSTANCE
    if _IBES_ENGINE_INSTANCE is None:
        with _IBES_ENGINE_LOCK:
            if _IBES_ENGINE_INSTANCE is None:
                _IBES_ENGINE_INSTANCE = IbesEngine()
    return _IBES_ENGINE_INSTANCE
