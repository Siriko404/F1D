"""Builder for CRSP-based market variables.

Computes StockRet, MarketRet, and Volatility directly from raw CRSP daily
stock files (inputs/CRSP_DSF/CRSP_DSF_{year}_Q{1-4}.parquet).

Matching: for each call, the return/volatility window is
    [prev_call_date + 5 days,  call start_date - 5 days]
where prev_call_date is the firm's prior earnings call. Requires >= 10
trading days in the window. This mirrors the legacy build_market_variables.py.

StockRet    = compound daily return over window (%, i.e. * 100)
MarketRet   = compound VWRETD (value-weighted market) over same window (%)
Volatility  = annualized std of daily returns over window (% units):
              std(daily_ret) * sqrt(252) * 100
"""

from __future__ import annotations

import gc
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats

CRSP_RETURN_COLS = ["StockRet", "MarketRet", "Volatility"]

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
                all_data.append(pd.read_parquet(fp))

    if not all_data:
        return None

    crsp = pd.concat(all_data, ignore_index=True)

    # Normalize column names to upper-case except 'date'
    col_map = {c: c.upper() for c in crsp.columns if c.lower() != "date"}
    crsp = crsp.rename(columns=col_map)
    if "DATE" in crsp.columns:
        crsp = crsp.rename(columns={"DATE": "date"})

    crsp["date"] = pd.to_datetime(crsp["date"])
    for col in ["RET", "VOL", "VWRETD", "ASKHI", "BIDLO", "PRC"]:
        if col in crsp.columns:
            crsp[col] = pd.to_numeric(crsp[col], errors="coerce")
    if "PRC" in crsp.columns:
        crsp["PRC"] = crsp["PRC"].abs()

    return crsp


def _compute_returns_for_manifest(
    manifest: pd.DataFrame, crsp: pd.DataFrame
) -> pd.DataFrame:
    """Vectorized stock return + volatility computation.

    Args:
        manifest: rows with file_name, permno_int, window_start, window_end
        crsp: CRSP daily stock file DataFrame

    Returns:
        manifest with StockRet, MarketRet, Volatility columns added
    """
    valid = manifest[
        manifest["permno_int"].notna()
        & manifest["prev_call_date"].notna()
        & (manifest["window_end"] > manifest["window_start"])
    ].copy()

    manifest = manifest.copy()
    manifest["StockRet"] = np.nan
    manifest["MarketRet"] = np.nan
    manifest["Volatility"] = np.nan

    if len(valid) == 0:
        return manifest

    valid["permno_int"] = valid["permno_int"].astype(int)
    crsp["PERMNO"] = crsp["PERMNO"].astype(int)

    merged = valid[["file_name", "permno_int", "window_start", "window_end"]].merge(
        crsp[["PERMNO", "date", "RET", "VWRETD"]],
        left_on="permno_int",
        right_on="PERMNO",
        how="inner",
    )
    merged = merged[
        (merged["date"] >= merged["window_start"])
        & (merged["date"] <= merged["window_end"])
    ]

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

    stock_rets = merged.groupby("file_name")["RET"].apply(compound)
    market_rets = merged.groupby("file_name")["VWRETD"].apply(compound)
    stock_vol = merged.groupby("file_name")["RET"].apply(volatility)

    manifest["StockRet"] = manifest["file_name"].map(stock_rets)
    manifest["MarketRet"] = manifest["file_name"].map(market_rets)
    manifest["Volatility"] = manifest["file_name"].map(stock_vol)

    return manifest


class CRSPReturnsBuilder(VariableBuilder):
    """Build StockRet, MarketRet, and Volatility from raw CRSP daily stock files.

    Processes data year-by-year (loading previous year's CRSP too for
    cross-year return windows), then concatenates results.

    Returns a VariableResult whose .data contains:
        file_name, StockRet, MarketRet, Volatility
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def build(self, years: range, root_path: Path) -> VariableResult:
        crsp_dir = root_path / "inputs" / "CRSP_DSF"
        ccm_path = (
            root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
        )

        manifest_dir = self._resolve_manifest_dir(root_path)
        manifest_path = manifest_dir / "master_sample_manifest.parquet"

        print(f"    CRSPReturnsBuilder: loading manifest...")
        manifest = pd.read_parquet(
            manifest_path, columns=["file_name", "gvkey", "start_date"]
        )
        manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        # Map gvkey -> PERMNO via CCM linktable
        print(f"    CRSPReturnsBuilder: linking PERMNO via CCM...")
        ccm = pd.read_parquet(ccm_path, columns=["gvkey", "LPERMNO"])
        ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
        ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce")
        gvkey_map = ccm.groupby("gvkey")["LPERMNO"].first().to_dict()

        manifest["permno_int"] = manifest["gvkey"].map(gvkey_map)

        # Compute prev_call_date (prior earnings call per firm, for return window)
        manifest = manifest.sort_values(["gvkey", "start_date"])
        manifest["prev_call_date"] = manifest.groupby("gvkey")["start_date"].shift(1)

        all_results: List[pd.DataFrame] = []

        year_list = sorted(manifest["year"].unique())
        for year in year_list:
            year_manifest = manifest[manifest["year"] == year].copy()

            # Window bounds
            year_manifest["window_start"] = year_manifest[
                "prev_call_date"
            ] + pd.Timedelta(days=DAYS_AFTER_PREV_CALL)
            year_manifest["window_end"] = year_manifest["start_date"] - pd.Timedelta(
                days=DAYS_BEFORE_CURRENT_CALL
            )

            # Load CRSP for this year + prior year (for windows crossing year boundary)
            crsp = _load_crsp_years(crsp_dir, [year - 1, year])
            if crsp is None:
                print(f"    CRSPReturnsBuilder: no CRSP data for {year}, skipping")
                # Still append with NaN returns so file_name is in output
                year_manifest["StockRet"] = np.nan
                year_manifest["MarketRet"] = np.nan
                year_manifest["Volatility"] = np.nan
                all_results.append(
                    year_manifest[["file_name", "StockRet", "MarketRet", "Volatility"]]
                )
                continue

            year_manifest = _compute_returns_for_manifest(year_manifest, crsp)
            n_ret = year_manifest["StockRet"].notna().sum()
            print(
                f"    CRSPReturnsBuilder: {year} — StockRet {n_ret:,}/{len(year_manifest):,}"
            )

            all_results.append(
                year_manifest[["file_name", "StockRet", "MarketRet", "Volatility"]]
            )

            del crsp
            gc.collect()

        if not all_results:
            empty = pd.DataFrame(columns=["file_name"] + CRSP_RETURN_COLS)
            stats = self.get_stats(pd.Series(dtype=float), "StockRet")
            return VariableResult(
                data=empty,
                stats=stats,
                metadata={"source": str(crsp_dir), "columns": CRSP_RETURN_COLS},
            )

        combined = pd.concat(all_results, ignore_index=True)
        stats = self.get_stats(combined["StockRet"], "StockRet")

        return VariableResult(
            data=combined,
            stats=stats,
            metadata={
                "source": str(crsp_dir),
                "columns": CRSP_RETURN_COLS,
                "matched": int(combined["StockRet"].notna().sum()),
                "total": int(len(combined)),
            },
        )

    def _resolve_manifest_dir(self, root_path: Path) -> Path:
        from f1d.shared.path_utils import get_latest_output_dir

        return get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )


__all__ = ["CRSPReturnsBuilder", "CRSP_RETURN_COLS"]
