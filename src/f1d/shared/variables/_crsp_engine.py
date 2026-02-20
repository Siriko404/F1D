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
    MAJOR-2:    prev_call_date computed on the FULL manifest before year-filtering
                so the first call of year Y correctly uses the prior call from
                year Y-1 rather than getting NaN (which would drop the observation).
"""

from __future__ import annotations

import gc
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

CRSP_RETURN_COLS = ["StockRet", "MarketRet", "Volatility", "amihud_illiq"]

MIN_TRADING_DAYS = 10
DAYS_AFTER_PREV_CALL = 5
DAYS_BEFORE_CURRENT_CALL = 5


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
                    keep_cols = ["PERMNO", "date", "RET", "VWRETD", "VOL", "PRC"]
                    for c in keep_cols:
                        if c not in df.columns:
                            df[c] = np.nan

                    df = df[keep_cols]
                    all_data.append(df)
                except Exception as e:
                    print(f"Error loading {fp}: {e}")

    if not all_data:
        return None

    crsp = pd.concat(all_data, ignore_index=True)

    crsp["date"] = pd.to_datetime(crsp["date"])
    for col in ["RET", "VOL", "VWRETD", "ASKHI", "BIDLO", "PRC"]:
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
        & manifest["prev_call_date"].notna()
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

    def compound(x: pd.Series) -> float:
        v = x.dropna()
        return (
            float(((1 + v).prod() - 1) * 100) if len(v) >= MIN_TRADING_DAYS else np.nan
        )

    def volatility(x: pd.Series) -> float:
        v = x.dropna()
        return (
            float(v.std() * np.sqrt(252) * 100)
            if len(v) >= MIN_TRADING_DAYS
            else np.nan
        )

    def amihud(x: pd.Series) -> float:
        v = x.replace([np.inf, -np.inf], np.nan).dropna()
        return float(v.mean() * 1e6) if len(v) >= MIN_TRADING_DAYS else np.nan

    stock_rets = merged.groupby("file_name")["RET"].apply(compound)
    market_rets = merged.groupby("file_name")["VWRETD"].apply(compound)
    stock_vol = merged.groupby("file_name")["RET"].apply(volatility)
    illiq = merged.groupby("file_name")["daily_illiq"].apply(amihud)

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

    def get_data(self, root_path: Path, manifest_path: Path) -> pd.DataFrame:
        """Return fully-computed CRSP returns DataFrame (cached)."""
        if (
            self._cache is not None
            and self._cache_root == root_path
            and "amihud_illiq" in self._cache.columns
        ):
            return self._cache

        crsp_dir = root_path / "inputs" / "CRSP_DSF"
        ccm_path = (
            root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
        )

        # Load full manifest (all years) for prev_call_date computation — MAJOR-2 fix
        print(f"    CRSPEngine: loading manifest (full) for prev_call_date...")
        full_manifest = pd.read_parquet(
            manifest_path, columns=["file_name", "gvkey", "start_date"]
        )
        full_manifest["gvkey"] = full_manifest["gvkey"].astype(str).str.zfill(6)
        full_manifest["start_date"] = pd.to_datetime(full_manifest["start_date"])

        # --- MAJOR-2: Compute prev_call_date on FULL manifest before any year filter ---
        full_manifest = full_manifest.sort_values(["gvkey", "start_date"])
        full_manifest["prev_call_date"] = full_manifest.groupby("gvkey")[
            "start_date"
        ].shift(1)
        full_manifest["year"] = full_manifest["start_date"].dt.year

        # --- CRITICAL-3: Date-bounded PERMNO linkage via CCM ---
        print(
            f"    CRSPEngine: loading CCM linktable for date-bounded PERMNO lookup..."
        )
        ccm_cols = ["gvkey", "LPERMNO"]
        # Try to load link date columns; fall back gracefully if absent.
        # CCM uses uppercase column names (LINKDT, LINKENDDT).
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
                "prev_call_date"
            ] + pd.Timedelta(days=DAYS_AFTER_PREV_CALL)
            year_manifest["window_end"] = year_manifest["start_date"] - pd.Timedelta(
                days=DAYS_BEFORE_CURRENT_CALL
            )

            crsp = _load_crsp_years(crsp_dir, [year - 1, year])
            if crsp is None:
                print(f"    CRSPEngine: no CRSP data for {year}, skipping")
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
            print(
                f"    CRSPEngine: {year} — StockRet {n_ret:,}/{len(year_manifest):,}, Amihud {n_illiq:,}/{len(year_manifest):,}"
            )

            all_results.append(
                year_manifest[
                    ["file_name", "StockRet", "MarketRet", "Volatility", "amihud_illiq"]
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

        self._cache = result
        self._cache_root = root_path
        return result


# Module-level singleton — shared across all individual builders in one process
_engine = CRSPEngine()


def get_engine() -> CRSPEngine:
    """Return the module-level singleton engine."""
    return _engine


__all__ = ["CRSPEngine", "CRSP_RETURN_COLS", "get_engine"]
