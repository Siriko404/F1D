"""Private Compustat compute engine.

Loads raw Compustat quarterly data ONCE per process, computes 12 firm-level
accounting variables, and caches the result so that SizeBuilder, BMBuilder,
LevBuilder, CashHoldingsBuilder, etc. all share a single load.

NOT a VariableBuilder — this is an internal helper. Individual VariableBuilders
(size.py, bm.py, etc.) import CompustatEngine and call get_data().

Bug fixes applied here (from red-team audit):
    CRITICAL-2: Deduplicate (gvkey, datadate) before merge_asof — keeps last row
                (most recent restatement) so asof match is deterministic.
    MAJOR-3:    EPS lag uses datadate arithmetic (target = datadate - 365 days,
                merge_asof backward within gvkey, accept only if within ±45 days)
                instead of shift(4) which counts rows not calendar quarters.
    MAJOR-6:    Size = ln(atq) only for atq > 0; zero/negative → NaN (no clamp).
    MINOR-9:    Replace inf values with NaN after ratio computations before
                winsorization (winsorization skips NaN but passes inf unchanged).

H1 extension (2026-02-19):
    Added CashHoldings, TobinsQ, CapexAt, DividendPayer, OCF_Volatility.
    Requires additional Compustat columns: cheq, capxq, dvpq, oancfy, mkvaltq.
    OCF_Volatility = rolling 4-year std of (oancfy/atq) per gvkey, computed
    after deduplication using annual data (oancfy is a flow variable — use the
    most recent annual observation per gvkey-fyearq).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# All columns produced by this engine (excludes file_name — matched in builders)
COMPUSTAT_COLS = [
    "Size",
    "BM",
    "Lev",
    "ROA",
    "CurrentRatio",
    "RD_Intensity",
    "EPS_Growth",
    # H1 extension
    "CashHoldings",
    "TobinsQ",
    "CapexAt",
    "DividendPayer",
    "OCF_Volatility",
]

REQUIRED_COMPUSTAT_COLS = [
    "gvkey",
    "datadate",
    "atq",
    "ceqq",
    "cshoq",
    "prccq",
    "ltq",
    "niq",
    "epspxq",
    "actq",
    "lctq",
    "xrdq",
    # H1 extension
    "cheq",
    "capxy",  # annual CapEx — no quarterly capxq in this dataset
    "dvpq",
    "oancfy",
    "mkvaltq",
    "fyearq",
]


def _compute_eps_growth_date_based(comp: pd.DataFrame) -> pd.Series:
    """Compute EPS YoY growth using datadate arithmetic, not row-count shift.

    For each row find the prior-year quarter: target = datadate - 365 days.
    Use merge_asof (backward, within gvkey) to find the closest prior quarter,
    then accept the lag only if it falls within ±45 days of the target date.
    This is robust to missing/irregular quarters (MAJOR-3 fix).

    Returns a Series aligned to the original comp index (before sorting).
    """
    # Work on a copy with a stable row_id so we can re-align at the end
    comp_work = comp[["gvkey", "datadate", "epspxq"]].copy()
    comp_work["_row_id"] = np.arange(len(comp_work))

    # Build lag lookup — same data, just renamed columns
    # merge_asof requires right key sorted globally (not just per-group)
    lag_df = (
        comp_work[["gvkey", "datadate", "epspxq"]]
        .rename(columns={"datadate": "lag_datadate", "epspxq": "epspxq_lag"})
        .sort_values("lag_datadate")
    )

    # For each observation, compute target lag date (~1 year ago)
    # merge_asof requires left key sorted globally
    lookup = comp_work.copy()
    lookup["target_lag_date"] = lookup["datadate"] - pd.Timedelta(days=365)
    lookup = lookup.sort_values("target_lag_date")

    merged = pd.merge_asof(
        lookup,
        lag_df,
        left_on="target_lag_date",
        right_on="lag_datadate",
        by="gvkey",
        direction="backward",
    )

    # Accept lag only if within ±45 days of the target date
    date_diff = (merged["target_lag_date"] - merged["lag_datadate"]).abs()
    valid = (
        merged["lag_datadate"].notna()
        & (date_diff <= pd.Timedelta(days=45))
        & merged["epspxq_lag"].notna()
        & (merged["epspxq_lag"] != 0)
    )

    merged["EPS_Growth_tmp"] = np.where(
        valid,
        (merged["epspxq"] - merged["epspxq_lag"]) / merged["epspxq_lag"].abs(),
        np.nan,
    )

    # Re-align to original comp row order via _row_id
    merged_sorted = merged.sort_values("_row_id")
    return merged_sorted["EPS_Growth_tmp"].values


def _compute_ocf_volatility(comp: pd.DataFrame) -> pd.Series:
    """Compute OCF_Volatility = rolling 4-year std of (oancfy / atq) per gvkey.

    oancfy is an annual flow variable — use the last observation per gvkey-fyearq
    to get one data point per fiscal year. Then compute rolling std over 4 years
    and align back to the full quarterly panel via gvkey + fyearq.

    Returns a Series aligned to comp's index.
    """
    # Annual panel: last obs per gvkey-fyearq
    annual = (
        comp[["gvkey", "datadate", "fyearq", "oancfy", "atq"]]
        .dropna(subset=["fyearq"])
        .copy()
    )
    annual["fyearq"] = annual["fyearq"].astype(int)
    annual = annual.sort_values(["gvkey", "fyearq", "datadate"])
    annual = annual.drop_duplicates(subset=["gvkey", "fyearq"], keep="last")

    # OCF ratio
    annual["ocf_ratio"] = np.where(
        annual["atq"] > 0,
        annual["oancfy"] / annual["atq"],
        np.nan,
    )
    annual["ocf_ratio"] = annual["ocf_ratio"].replace([np.inf, -np.inf], np.nan)

    # Rolling 4-year std per gvkey (min 2 years required)
    annual = annual.sort_values(["gvkey", "fyearq"])
    annual["OCF_Volatility_annual"] = annual.groupby("gvkey")["ocf_ratio"].transform(
        lambda x: x.rolling(4, min_periods=2).std()
    )

    # Build lookup: gvkey + fyearq -> OCF_Volatility
    lookup = annual[["gvkey", "fyearq", "OCF_Volatility_annual"]].copy()

    # Align back to the full quarterly panel
    comp_aligned = comp[["gvkey", "fyearq"]].copy()
    comp_aligned["fyearq"] = comp_aligned["fyearq"].astype("Int64")
    comp_aligned["_idx"] = np.arange(len(comp_aligned))

    merged = comp_aligned.merge(
        lookup.rename(columns={"OCF_Volatility_annual": "OCF_Volatility"}),
        on=["gvkey", "fyearq"],
        how="left",
    )
    merged = merged.sort_values("_idx")
    return merged["OCF_Volatility"].values


def _compute_and_winsorize(comp: pd.DataFrame) -> pd.DataFrame:
    """Compute all 12 control variables on the full Compustat panel and winsorize."""
    comp = comp.sort_values(["gvkey", "datadate"]).reset_index(drop=True)

    # --- MAJOR-6: Size = ln(atq) only for positive atq; zero/neg → NaN ---
    comp["Size"] = np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)

    comp["BM"] = comp["ceqq"] / (comp["cshoq"] * comp["prccq"])
    comp["Lev"] = comp["ltq"] / comp["atq"]
    comp["ROA"] = comp["niq"] / comp["atq"]
    comp["CurrentRatio"] = comp["actq"] / comp["lctq"].replace(0, np.nan)
    comp["RD_Intensity"] = comp["xrdq"].fillna(0) / comp["atq"]

    # --- H1 extension: 5 new variables ---
    comp["CashHoldings"] = comp["cheq"] / comp["atq"]
    comp["TobinsQ"] = (comp["mkvaltq"] + comp["ltq"]) / comp["atq"]
    comp["CapexAt"] = comp["capxy"] / comp["atq"]
    comp["DividendPayer"] = (comp["dvpq"].fillna(0) > 0).astype(float)
    comp["OCF_Volatility"] = _compute_ocf_volatility(comp)

    # --- MINOR-9: Replace inf with NaN after ratio computations ---
    ratio_cols = [
        "BM",
        "Lev",
        "ROA",
        "CurrentRatio",
        "RD_Intensity",
        "CashHoldings",
        "TobinsQ",
        "CapexAt",
        "OCF_Volatility",
    ]
    for col in ratio_cols:
        comp[col] = comp[col].replace([np.inf, -np.inf], np.nan)

    # --- MAJOR-3: Date-based EPS lag ---
    comp["EPS_Growth"] = _compute_eps_growth_date_based(comp)

    # Winsorize 1% / 99% on full panel (skip DividendPayer — binary)
    winsorize_cols = [c for c in COMPUSTAT_COLS if c != "DividendPayer"]
    for col in winsorize_cols:
        valid = comp[col].notna()
        if valid.any():
            p1 = comp.loc[valid, col].quantile(0.01)
            p99 = comp.loc[valid, col].quantile(0.99)
            comp[col] = comp[col].clip(lower=p1, upper=p99)

    return comp


class CompustatEngine:
    """Load raw Compustat quarterly data, compute 12 controls, cache result.

    Usage:
        engine = CompustatEngine()
        df = engine.get_data(root_path)
        # df has columns: gvkey, datadate, Size, BM, Lev, ROA,
        #                 CurrentRatio, RD_Intensity, EPS_Growth,
        #                 CashHoldings, TobinsQ, CapexAt, DividendPayer, OCF_Volatility

    The result is cached after the first call — subsequent calls with the
    same root_path return the cached DataFrame immediately.
    """

    def __init__(self) -> None:
        self._cache: Optional[pd.DataFrame] = None
        self._cache_root: Optional[Path] = None

    def get_data(self, root_path: Path) -> pd.DataFrame:
        """Return fully-computed Compustat controls DataFrame (cached)."""
        if self._cache is not None and self._cache_root == root_path:
            return self._cache

        compustat_path = (
            root_path / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
        )
        print(f"    CompustatEngine: loading {compustat_path.name}...")
        comp = pd.read_parquet(compustat_path, columns=REQUIRED_COMPUSTAT_COLS)
        comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
        comp["datadate"] = pd.to_datetime(comp["datadate"])
        numeric_cols = [
            c
            for c in REQUIRED_COMPUSTAT_COLS
            if c not in ("gvkey", "datadate", "fyearq")
        ]
        for col in numeric_cols:
            comp[col] = pd.to_numeric(comp[col], errors="coerce").astype("float64")
        # fyearq as nullable int (may be missing)
        comp["fyearq"] = pd.to_numeric(comp["fyearq"], errors="coerce")

        # --- CRITICAL-2: Deduplicate (gvkey, datadate) — keep last (most recent restatement) ---
        before = len(comp)
        comp = comp.drop_duplicates(subset=["gvkey", "datadate"], keep="last")
        after = len(comp)
        if before != after:
            print(
                f"    CompustatEngine: dropped {before - after:,} duplicate (gvkey, datadate) rows"
            )

        print(f"    CompustatEngine: computing controls on {len(comp):,} rows...")
        comp = _compute_and_winsorize(comp)

        self._cache = comp
        self._cache_root = root_path
        return comp

    def match_to_manifest(
        self,
        manifest: pd.DataFrame,
        root_path: Path,
    ) -> pd.DataFrame:
        """Merge Compustat controls into manifest via merge_asof.

        Args:
            manifest: DataFrame with file_name, gvkey (zero-padded str),
                      start_date (datetime).
            root_path: Project root for raw data lookup.

        Returns:
            manifest with COMPUSTAT_COLS columns added (NaN where unmatched).
        """
        comp = self.get_data(root_path)
        comp_sorted = comp.sort_values("datadate")
        manifest_sorted = manifest.sort_values("start_date")

        merged = pd.merge_asof(
            manifest_sorted,
            comp_sorted[["gvkey", "datadate"] + COMPUSTAT_COLS],
            left_on="start_date",
            right_on="datadate",
            by="gvkey",
            direction="backward",
        )

        matched = merged["Size"].notna().sum()
        total = len(merged)
        print(
            f"    CompustatEngine: matched {matched:,}/{total:,} "
            f"({matched / total * 100:.1f}%)"
        )
        return merged


# Module-level singleton — shared across all individual builders in one process
_engine = CompustatEngine()


def get_engine() -> CompustatEngine:
    """Return the module-level singleton engine."""
    return _engine


__all__ = ["CompustatEngine", "COMPUSTAT_COLS", "get_engine"]
