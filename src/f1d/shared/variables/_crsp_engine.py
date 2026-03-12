"""Private CRSP compute engine.

Loads raw CRSP daily stock files year-by-year, computes StockRet, MarketRet,
and Volatility for each call window, and caches the result so that
StockReturnBuilder, MarketReturnBuilder, and VolatilityBuilder all share a
single CRSP load pass.

NOT a VariableBuilder — this is an internal helper.

Bug fixes applied here (from red-team audit):
    CRITICAL-3: Date-bounded CCM PERMNO lookup — join on linkdt <= call_date <=
                linkenddt so firms that changed PERMNO during the sample period
                get the correct PERMNO for each call, not just the first link.
    CRITICAL-4: PERMNO coerce-and-dropna before astype(int) — if any CRSP row
                has a NaN PERMNO (data quality issue) it is dropped cleanly
                rather than crashing the entire year's computation.
    MAJOR-2:    prev_call_date and next_call_date computed on the FULL manifest
                before year-filtering so the first/last call of year Y correctly
                uses adjacent calls from year Y-1/Y+1 rather than getting NaN.
"""

from __future__ import annotations

import gc
import logging
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

CRSP_RETURN_COLS = ["StockRet", "MarketRet", "Volatility", "amihud_illiq"]

# Additional columns needed for bid-ask spread calculations (H14)
CRSP_BIDASK_COLS = ["BIDLO", "ASKHI", "BID", "ASK", "SHROUT"]

MIN_TRADING_DAYS = 10
DAYS_AFTER_CURRENT_CALL = 1    # window starts 1 trading day after call
DAYS_BEFORE_NEXT_CALL = 5      # window ends 5 trading days before next call


def _load_crsp_years(crsp_dir: Path, years: List[int]) -> Optional[pd.DataFrame]:
    """Load CRSP quarterly parquet files for the given calendar years."""
    all_data: List[pd.DataFrame] = []

    for year in years:
        for q in range(1, 5):
            fp = crsp_dir / f"CRSP_DSF_{year}_Q{q}.parquet"
            if fp.exists():
                try:
                    df = pd.read_parquet(fp)
                    # Create empty columns if they don't exist
                    for col in ["VOL", "vol", "PRC", "prc", "vwretd", "VWRETD"]:
                        if (
                            col not in df.columns
                            and col.upper() not in df.columns
                            and col.lower() not in df.columns
                        ):
                            df[col.upper()] = np.nan

                    # Rename all to uppercase except 'date'
                    col_map = {c: c.upper() for c in df.columns if c.lower() != "date"}
                    df = df.rename(columns=col_map)
                    if "DATE" in df.columns:
                        df = df.rename(columns={"DATE": "date"})

                    # Ensure columns exist before subsetting
                    # Include BIDLO, ASKHI, SHROUT for bid-ask spread calculations (H14)
                    keep_cols = ["PERMNO", "date", "RET", "VWRETD", "VOL", "PRC", "BIDLO", "ASKHI", "BID", "ASK", "SHROUT"]
                    for c in keep_cols:
                        if c not in df.columns:
                            df[c] = np.nan

                    df = df[keep_cols]
                    all_data.append(df)
                except Exception as e:
                    logger.info(f"Error loading {fp}: {e}")

    if not all_data:
        return None

    crsp = pd.concat(all_data, ignore_index=True)

    crsp["date"] = pd.to_datetime(crsp["date"])
    for col in ["RET", "VOL", "VWRETD", "ASKHI", "BIDLO", "BID", "ASK", "PRC", "SHROUT"]:
        if col in crsp.columns:
            crsp[col] = pd.to_numeric(crsp[col], errors="coerce")
    if "PRC" in crsp.columns:
        crsp["PRC"] = crsp["PRC"].abs()

    # --- CRITICAL-4: Coerce PERMNO, drop NaN before astype(int) ---
    crsp["PERMNO"] = pd.to_numeric(crsp["PERMNO"], errors="coerce")
    crsp = crsp[crsp["PERMNO"].notna()].copy()
    crsp["PERMNO"] = crsp["PERMNO"].astype(int)

    return crsp


def _build_date_bounded_permno_map(
    ccm: pd.DataFrame, manifest: pd.DataFrame
) -> pd.DataFrame:
    """Build a per-call (file_name → PERMNO) mapping using date-bounded CCM links.

    CRITICAL-3 fix: for each call, select the CCM link row where
    linkdt <= start_date <= linkenddt. This correctly handles firms that
    changed PERMNO during the sample period.

    Args:
        ccm: CCM DataFrame with gvkey, LPERMNO, linkdt, linkenddt columns.
        manifest: DataFrame with file_name, gvkey, start_date.

    Returns:
        DataFrame with file_name, permno_int columns.
    """
    ccm = ccm.copy()
    ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
    ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce")
    ccm = ccm[ccm["LPERMNO"].notna()].copy()
    ccm["LPERMNO"] = ccm["LPERMNO"].astype(int)

    # Normalize link dates — missing linkenddt means link is still active
    if "linkdt" in ccm.columns:
        ccm["linkdt"] = pd.to_datetime(ccm["linkdt"], errors="coerce")
    else:
        ccm["linkdt"] = pd.NaT

    if "linkenddt" in ccm.columns:
        ccm["linkenddt"] = pd.to_datetime(ccm["linkenddt"], errors="coerce")
        # Missing end date = active link; set to far future
        ccm["linkenddt"] = ccm["linkenddt"].fillna(pd.Timestamp("2099-12-31"))
    else:
        ccm["linkenddt"] = pd.Timestamp("2099-12-31")

    # Join manifest to CCM on gvkey
    joined = manifest[["file_name", "gvkey", "start_date"]].merge(
        ccm[["gvkey", "LPERMNO", "linkdt", "linkenddt"]],
        on="gvkey",
        how="left",
    )

    # Date-bounded filter: keep rows where linkdt <= start_date <= linkenddt
    valid_link = (
        joined["linkdt"].isna() | (joined["start_date"] >= joined["linkdt"])
    ) & (joined["start_date"] <= joined["linkenddt"])
    joined = joined[valid_link].copy()

    # If multiple links are valid for one call, take the most recent linkdt
    joined = (
        joined.sort_values("linkdt", na_position="first")
        .groupby("file_name")["LPERMNO"]
        .last()
        .reset_index()
        .rename(columns={"LPERMNO": "permno_int"})
    )

    return joined


def _compute_returns_for_manifest(
    manifest: pd.DataFrame, crsp: pd.DataFrame
) -> pd.DataFrame:
    """Compute StockRet, MarketRet, Volatility for all calls in manifest.

    Args:
        manifest: rows with file_name, permno_int, window_start, window_end
        crsp: CRSP daily stock file DataFrame (PERMNO already int, NaN dropped)

    Returns:
        manifest with StockRet, MarketRet, Volatility columns added
    """
    manifest = manifest.copy()
    manifest["StockRet"] = np.nan
    manifest["MarketRet"] = np.nan
    manifest["Volatility"] = np.nan

    valid = manifest[
        manifest["permno_int"].notna()
        & manifest["next_call_date"].notna()
        & (manifest["window_end"] > manifest["window_start"])
    ].copy()

    if len(valid) == 0:
        return manifest

    valid["permno_int"] = valid["permno_int"].astype(int)

    # Include VOL and PRC so Amihud illiquidity can be computed
    crsp_cols = ["PERMNO", "date", "RET", "VWRETD"]
    for _c in ["VOL", "PRC"]:
        if _c in crsp.columns:
            crsp_cols.append(_c)
    merged = valid[["file_name", "permno_int", "window_start", "window_end"]].merge(
        crsp[crsp_cols],
        left_on="permno_int",
        right_on="PERMNO",
        how="inner",
    )
    merged = merged[
        (merged["date"] >= merged["window_start"])
        & (merged["date"] <= merged["window_end"])
    ]

    # Calculate daily amihud components (vectorized safely)
    # Deduplicate columns if any (Parquet reading sometimes merges index and data columns)
    merged = merged.loc[:, ~merged.columns.duplicated()].copy()

    for c in ["VOL", "PRC", "RET"]:
        if c not in merged.columns:
            merged[c] = np.nan

    merged["VOL"] = pd.to_numeric(merged["VOL"], errors="coerce")
    merged["PRC"] = pd.to_numeric(merged["PRC"], errors="coerce")
    merged["RET"] = pd.to_numeric(merged["RET"], errors="coerce")

    merged["dollar_volume"] = merged["VOL"] * merged["PRC"].abs()
    # Mask out zeros to avoid Inf
    dollar_vol_masked = merged["dollar_volume"].replace(0, np.nan)
    merged["daily_illiq"] = merged["RET"].abs() / dollar_vol_masked
    # Clamp Inf from illiq before aggregation
    merged["daily_illiq"] = merged["daily_illiq"].replace([np.inf, -np.inf], np.nan)

    # --- Vectorized aggregation (replaces four groupby.apply(UDF) calls) ---
    # Each UDF was a Python callback executed once per file_name group (~8-10k
    # groups per year). Replaced with pure numpy/pandas agg operations:
    #   compound  → log-sum trick: sum(log1p(RET)) then expm1, scaled to %
    #   volatility → std * sqrt(252) * 100
    #   amihud    → mean(daily_illiq) * 1e6
    # min_periods guard (MIN_TRADING_DAYS) applied post-agg with .where().

    # Count valid (non-NaN) trading days per call for the min_periods guard
    merged["_ret_valid"] = merged["RET"].notna().astype(int)
    merged["_log1p_ret"] = np.log1p(merged["RET"].fillna(0)).where(
        merged["RET"].notna(), np.nan
    )
    merged["_log1p_vwretd"] = np.log1p(merged["VWRETD"].fillna(0)).where(
        merged["VWRETD"].notna(), np.nan
    )

    grp = merged.groupby("file_name")

    n_valid = grp["_ret_valid"].sum()
    sum_log_ret = grp["_log1p_ret"].sum(min_count=1)
    sum_log_vwretd = grp["_log1p_vwretd"].sum(min_count=1)
    std_ret = grp["RET"].std()
    mean_illiq = grp["daily_illiq"].mean()

    # Apply MIN_TRADING_DAYS guard — results with fewer valid days → NaN
    sufficient = n_valid >= MIN_TRADING_DAYS

    stock_rets = ((np.expm1(sum_log_ret)) * 100).where(sufficient)
    market_rets = ((np.expm1(sum_log_vwretd)) * 100).where(sufficient)
    stock_vol = (std_ret * np.sqrt(252) * 100).where(sufficient)
    illiq = (mean_illiq * 1e6).where(sufficient)

    manifest["StockRet"] = manifest["file_name"].map(stock_rets)
    manifest["MarketRet"] = manifest["file_name"].map(market_rets)
    manifest["Volatility"] = manifest["file_name"].map(stock_vol)
    manifest["amihud_illiq"] = manifest["file_name"].map(illiq)

    return manifest


class CRSPEngine:
    """Load raw CRSP daily data, compute return/volatility variables, cache result.

    Usage:
        engine = CRSPEngine()
        df = engine.get_data(root_path, manifest_path)
        # df has columns: file_name, StockRet, MarketRet, Volatility

    The result is cached after the first call — subsequent calls with the same
    root_path return the cached DataFrame immediately.
    """

    def __init__(self) -> None:
        self._cache: Optional[pd.DataFrame] = None
        self._cache_root: Optional[Path] = None
        self._lock = threading.Lock()
        # Separate cache for raw daily data (H14 event-window calculations)
        self._raw_cache: Optional[pd.DataFrame] = None
        self._raw_cache_root: Optional[Path] = None

    def _is_cached(self, root_path: Path) -> bool:
        return (
            self._cache is not None
            and self._cache_root == root_path
            and "amihud_illiq" in self._cache.columns
        )

    def get_data(self, root_path: Path, manifest_path: Path) -> pd.DataFrame:
        """Return fully-computed CRSP returns DataFrame (cached).

        Uses double-checked locking so that concurrent callers in a
        multi-threaded pipeline do not trigger redundant loads.
        """
        # Fast path — no lock needed.
        if self._is_cached(root_path):
            return self._cache  # type: ignore[return-value]

        with self._lock:
            # Re-check inside the lock — another thread may have populated it.
            if self._is_cached(root_path):
                return self._cache  # type: ignore[return-value]

            crsp_dir = root_path / "inputs" / "CRSP_DSF"
            ccm_path = (
                root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
            )

            # Load full manifest (all years) for prev_call_date — MAJOR-2 fix
            logger.info("    CRSPEngine: loading manifest (full) for prev/next_call_date...")
            full_manifest = pd.read_parquet(
                manifest_path, columns=["file_name", "gvkey", "start_date"]
            )
            full_manifest["gvkey"] = full_manifest["gvkey"].astype(str).str.zfill(6)
            full_manifest["start_date"] = pd.to_datetime(full_manifest["start_date"])

            # --- MAJOR-2: Compute prev/next_call_date on FULL manifest ---
            full_manifest = full_manifest.sort_values(["gvkey", "start_date"])
            full_manifest["prev_call_date"] = full_manifest.groupby("gvkey")[
                "start_date"
            ].shift(1)
            full_manifest["next_call_date"] = full_manifest.groupby("gvkey")[
                "start_date"
            ].shift(-1)
            full_manifest["year"] = full_manifest["start_date"].dt.year

            # --- CRITICAL-3: Date-bounded PERMNO linkage via CCM ---
            logger.info(
                "    CRSPEngine: loading CCM linktable for date-bounded PERMNO lookup..."
            )
            ccm_cols = ["gvkey", "LPERMNO"]
            # Try to load link date columns; fall back gracefully if absent.
            all_ccm_cols = pd.read_parquet(ccm_path, columns=None).columns.tolist()
            all_ccm_cols_lower = {c.lower(): c for c in all_ccm_cols}
            for date_col_lower in ["linkdt", "linkenddt"]:
                actual_col = all_ccm_cols_lower.get(date_col_lower)
                if actual_col:
                    ccm_cols.append(actual_col)
            ccm = pd.read_parquet(ccm_path, columns=ccm_cols)
            # Normalize to lowercase for _build_date_bounded_permno_map
            ccm = ccm.rename(
                columns={
                    c: c.lower() for c in ccm.columns if c != "LPERMNO" and c != "gvkey"
                }
            )

            permno_map = _build_date_bounded_permno_map(ccm, full_manifest)
            full_manifest = full_manifest.merge(permno_map, on="file_name", how="left")

            # Process year by year (load current + prior year's CRSP)
            all_results: List[pd.DataFrame] = []
            year_list = sorted(full_manifest["year"].unique())

            for year in year_list:
                year_manifest = full_manifest[full_manifest["year"] == year].copy()

                year_manifest["window_start"] = year_manifest[
                    "start_date"
                ] + pd.Timedelta(days=DAYS_AFTER_CURRENT_CALL)
                year_manifest["window_end"] = year_manifest[
                    "next_call_date"
                ] - pd.Timedelta(days=DAYS_BEFORE_NEXT_CALL)

                crsp = _load_crsp_years(crsp_dir, [year, year + 1])
                if crsp is None:
                    logger.info(f"    CRSPEngine: no CRSP data for {year}, skipping")
                    year_manifest["StockRet"] = np.nan
                    year_manifest["MarketRet"] = np.nan
                    year_manifest["Volatility"] = np.nan
                    year_manifest["amihud_illiq"] = np.nan
                    all_results.append(
                        year_manifest[
                            [
                                "file_name",
                                "StockRet",
                                "MarketRet",
                                "Volatility",
                                "amihud_illiq",
                            ]
                        ]
                    )
                    continue

                year_manifest = _compute_returns_for_manifest(year_manifest, crsp)
                n_ret = year_manifest["StockRet"].notna().sum()
                n_illiq = year_manifest["amihud_illiq"].notna().sum()
                logger.info(
                    f"    CRSPEngine: {year} — "
                    f"StockRet {n_ret:,}/{len(year_manifest):,}, "
                    f"Amihud {n_illiq:,}/{len(year_manifest):,}"
                )

                all_results.append(
                    year_manifest[
                        [
                            "file_name",
                            "StockRet",
                            "MarketRet",
                            "Volatility",
                            "amihud_illiq",
                        ]
                    ]
                )
                del crsp
                gc.collect()

            if not all_results:
                result = pd.DataFrame(columns=["file_name"] + CRSP_RETURN_COLS)
            else:
                result = pd.concat(all_results, ignore_index=True)
                for c in CRSP_RETURN_COLS:
                    if c not in result.columns:
                        result[c] = float("nan")

            # === WINSORIZATION: Per-year 1%/99% for CRSP variables ===
            # This ensures consistent outlier treatment across ALL hypothesis suites
            from .winsorization import winsorize_by_year

            # Build year lookup from full_manifest
            year_lookup = full_manifest[["file_name", "year"]].drop_duplicates()
            assert year_lookup["file_name"].is_unique, (
                f"Duplicate file_name in full_manifest year lookup: "
                f"{year_lookup['file_name'].duplicated().sum()} duplicates"
            )

            # Merge year back onto result for per-year winsorization
            result_with_year = result.merge(year_lookup, on="file_name", how="left")
            assert "year" in result_with_year.columns, (
                "year column missing after merge - check full_manifest schema"
            )

            # Warn about orphaned records (no year match after merge)
            orphaned = result_with_year["year"].isna().sum()
            if orphaned > 0:
                logger.warning(
                    f"CRSPEngine: {orphaned:,} records have NaN year after merge - "
                    f"these will not be winsorized (may be calls outside manifest date range)"
                )

            # Apply per-year winsorization to CRSP variables
            result_with_year = winsorize_by_year(
                result_with_year, CRSP_RETURN_COLS, year_col="year"
            )

            # Drop year column (engine output should only have file_name + variable cols)
            result = result_with_year[["file_name"] + CRSP_RETURN_COLS]
            # === END WINSORIZATION ===

            self._cache = result
            self._cache_root = root_path
            return result

    def get_raw_daily_data(self, root_path: Path, years: Optional[List[int]] = None) -> pd.DataFrame:
        """Return raw CRSP daily data with BIDLO, ASKHI, SHROUT columns (cached).

        Used for event-window calculations (H14) that need daily bid/ask data
        around specific call dates.

        Args:
            root_path: Project root path
            years: Optional list of years to load. If None, loads all available years.

        Returns:
            DataFrame with columns: PERMNO, date, RET, VWRETD, VOL, PRC, BIDLO, ASKHI, SHROUT
        """
        # Check cache
        if self._raw_cache is not None and self._raw_cache_root == root_path:
            if years is None:
                return self._raw_cache
            # Filter to requested years
            cached_years = self._raw_cache["date"].dt.year.unique()
            if all(y in cached_years for y in years):
                return self._raw_cache[self._raw_cache["date"].dt.year.isin(years)]

        crsp_dir = root_path / "inputs" / "CRSP_DSF"

        # Determine years to load
        if years is None:
            # Load all available years
            years = []
            for fp in crsp_dir.glob("CRSP_DSF_*_Q1.parquet"):
                year_str = fp.stem.split("_")[2]
                try:
                    years.append(int(year_str))
                except ValueError:
                    continue
            years = sorted(years)

        logger.info(f"    CRSPEngine: loading raw daily data for {len(years)} years...")
        crsp = _load_crsp_years(crsp_dir, years)

        if crsp is None:
            logger.warning("    CRSPEngine: No raw daily data loaded!")
            return pd.DataFrame(columns=["PERMNO", "date"] + CRSP_BIDASK_COLS)

        logger.info(f"    CRSPEngine: Loaded {len(crsp):,} raw daily records")

        # Cache for future use
        self._raw_cache = crsp
        self._raw_cache_root = root_path

        return crsp


# Module-level singleton — shared across all individual builders in one process
_engine = CRSPEngine()


def get_engine() -> CRSPEngine:
    """Return the module-level singleton engine."""
    return _engine


__all__ = ["CRSPEngine", "CRSP_RETURN_COLS", "CRSP_BIDASK_COLS", "get_engine"]
