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
    MAJOR-6:    Size = ln(atq) only for atq > 0; zero/negative -> NaN (no clamp).
    MINOR-9:    Replace inf values with NaN after ratio computations before
                winsorization (winsorization skips NaN but passes inf unchanged).

H1 extension (2026-02-19):
    Added CashHoldings, TobinsQ, CapexAt, DividendPayer, OCF_Volatility.

H1 audit fixes (2026-02-19):
    TobinsQ: was (mkvaltq+ltq)/atq -- mkvaltq has 41% missing rate.
             Fixed to (atq + cshoq*prccq - ceqq)/atq which matches v2 design
             and cshoq*prccq has only 9.5% missing rate.
             Requires: cshoq, prccq, ceqq (already in REQUIRED_COMPUSTAT_COLS).
             Remove: mkvaltq (no longer needed).
    DividendPayer: was dvpq>0 (preferred dividends quarterly -- only 9.7% payers).
                   Fixed to dvy>0 (annual common dividends -- ~32% payers).
                   Requires: dvy instead of dvpq.
    OCF_Volatility: was 4-year rolling min 2 periods.
                    Fixed to 5-year rolling min 3 periods (matches v2 design).

Red-team audit fixes (2026-02-20):
    CRITICAL-1 CapexAt: capxy is YTD cumulative within fiscal year -- Q1 row has
                only Q1 capex, Q4 row has full-year capex. Fixed to use Q4-only
                capxy (full fiscal year) joined back to all quarters via
                gvkey+fyearq, same pattern as OCF_Volatility. Requires: fqtr.
    CRITICAL-2 DividendPayer: dvy is annual cumulative YTD -- same issue as capxy.
                Fixed to use Q4-only dvy (full fiscal year) joined back to all
                quarters via gvkey+fyearq. This correctly classifies dividend
                payers using full-year dividends regardless of when the call falls.
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
    "capxy",  # YTD cumulative CapEx -- used Q4-only (full fiscal year)
    "dvy",  # YTD cumulative common dividends -- used Q4-only (full fiscal year)
    "oancfy",
    "fyearq",
    "fqtr",  # fiscal quarter (1-4) -- used to identify Q4 rows for capxy/dvy
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


def _compute_annual_q4_variable(
    comp: pd.DataFrame, raw_col: str, out_col: str
) -> pd.Series:
    """Compute a full-fiscal-year variable from a YTD-cumulative Compustat field.

    capxy and dvy are YTD-cumulative within a fiscal year: Q1 holds only Q1
    values, Q4 holds the full-year total. Using Q4 rows (fqtr==4) gives the
    correct annual figure. We then join it back to ALL quarterly rows by
    gvkey+fyearq so every call in the same fiscal year gets the same value.

    Args:
        comp: Full Compustat DataFrame (must have fqtr, fyearq, gvkey, raw_col).
        raw_col: The cumulative Compustat column (e.g. 'capxy', 'dvy').
        out_col: The output column name (e.g. 'CapexAt_annual', 'DividendPayer').

    Returns:
        Series aligned to comp's index.
    """
    # Q4 rows only -- full-year cumulative value
    q4 = (
        comp[comp["fqtr"] == 4][["gvkey", "fyearq", raw_col]]
        .dropna(subset=["fyearq"])
        .copy()
    )
    q4["fyearq"] = q4["fyearq"].astype(int)
    # Keep last Q4 per gvkey-fyearq (most recent restatement)
    q4 = q4.sort_values(["gvkey", "fyearq"]).drop_duplicates(
        subset=["gvkey", "fyearq"], keep="last"
    )
    q4 = q4.rename(columns={raw_col: out_col})

    # Align back to full quarterly panel
    comp_aligned = comp[["gvkey", "fyearq"]].copy()
    comp_aligned["fyearq"] = pd.to_numeric(comp_aligned["fyearq"], errors="coerce")
    comp_aligned["_idx"] = np.arange(len(comp_aligned))

    merged = comp_aligned.merge(
        q4.assign(fyearq=lambda d: d["fyearq"].astype(float)),
        on=["gvkey", "fyearq"],
        how="left",
    )
    merged = merged.sort_values("_idx")
    return merged[out_col].values  # type: ignore[return-value]


def _compute_ocf_volatility(comp: pd.DataFrame) -> pd.Series:
    """Compute OCF_Volatility = rolling 5-year std of (oancfy / atq) per gvkey.

    oancfy is an annual flow variable -- use the last observation per gvkey-fyearq
    to get one data point per fiscal year. Then compute rolling std over 5 years
    (min 3 years required) and align back to full quarterly panel via gvkey+fyearq.

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

    # Rolling 5-year std per gvkey (min 3 years required, matches v2 design)
    annual = annual.sort_values(["gvkey", "fyearq"])
    annual["OCF_Volatility_annual"] = annual.groupby("gvkey")["ocf_ratio"].transform(
        lambda x: x.rolling(5, min_periods=3).std()
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
    # TobinsQ = (AT + MarketEquity - CEQ) / AT  (matches v2 formula; cshoq*prccq
    # has 9.5% missing vs 41% for mkvaltq, so far better coverage)
    mktcap = comp["cshoq"] * comp["prccq"]
    comp["TobinsQ"] = (comp["atq"] + mktcap - comp["ceqq"]) / comp["atq"]

    # CRITICAL-1 fix: capxy is YTD cumulative -- use Q4 annual value joined to
    # all quarters, divided by that quarter's atq for the ratio.
    # First get the full-year capxy per gvkey-fyearq from Q4 rows.
    capxy_annual = _compute_annual_q4_variable(comp, "capxy", "_capxy_annual")
    comp["CapexAt"] = capxy_annual / comp["atq"]

    # CRITICAL-2 fix: dvy is YTD cumulative -- use Q4 annual value joined to
    # all quarters to classify dividend payers using the full fiscal year.
    dvy_annual = _compute_annual_q4_variable(comp, "dvy", "_dvy_annual")
    comp["DividendPayer"] = (
        pd.Series(dvy_annual, index=comp.index).fillna(0) > 0
    ).astype(float)

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
            if c not in ("gvkey", "datadate", "fyearq", "fqtr")
        ]
        for col in numeric_cols:
            comp[col] = pd.to_numeric(comp[col], errors="coerce").astype("float64")
        # fyearq and fqtr as numeric integers (may be missing in some rows)
        comp["fyearq"] = pd.to_numeric(comp["fyearq"], errors="coerce")
        comp["fqtr"] = pd.to_numeric(comp["fqtr"], errors="coerce")

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
