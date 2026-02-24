"""Private Hassan Political Risk (PRisk) compute engine.

Loads the Hassan et al. (2019) firm-quarter PRisk CSV ONCE per process,
aggregates quarterly data into fiscal-year averages (PRiskFY) using a
366-day rolling window, and caches the result so that all H8 builders
share a single load pass.

NOT a VariableBuilder — this is an internal helper.

Methodology (replicates legacy 3.12_H9_PRiskFY.py, now v1 architecture):
    PRiskFY_i,t = mean(PRisk quarters) where cal_q_end ∈ (fy_end - 366d, fy_end]
    Requires >= 2 quarters; otherwise NaN (NO forward-filling, NO interpolation).

Input file:
    inputs/FirmLevelRisk/firmquarter_2022q1.csv  (TAB-separated)
    Columns: gvkey, date ("YYYYQq"), PRisk, [NPRisk, PSentiment]

Architecture notes:
    - Compustat fiscal year-end dates are retrieved via CompustatEngine.get_data()
      so we do not reload Compustat independently.
    - Output is keyed on (gvkey, fyearq) as integer year, matching the quarterly
      CompustatEngine convention.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

# We reuse CompustatEngine to get fiscal year-end dates
from ._compustat_engine import get_engine as get_compustat_engine

PRISK_FILE = "inputs/FirmLevelRisk/firmquarter_2022q1.csv"
MIN_QUARTERS = 2
WINDOW_DAYS = 366


def _parse_quarter_end(date_str: str) -> Optional[pd.Timestamp]:
    """Convert 'YYYYQq' string → quarter-end Timestamp."""
    try:
        parts = str(date_str).lower().strip().split("q")
        if len(parts) != 2:
            return None
        year, quarter = int(parts[0]), int(parts[1])
        qmap = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}
        if quarter not in qmap:
            return None
        m, d = qmap[quarter]
        return pd.Timestamp(year=year, month=m, day=d)
    except (ValueError, AttributeError):
        return None


def _load_prisk(prisk_path: Path) -> pd.DataFrame:
    """Load and clean the Hassan PRisk quarterly CSV."""
    if not prisk_path.exists():
        raise FileNotFoundError(f"PRisk data not found: {prisk_path}")

    df = pd.read_csv(prisk_path, sep="\t", on_bad_lines="skip")
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df = df.dropna(subset=["PRisk"])

    df["cal_q_end"] = pd.to_datetime(
        df["date"].apply(_parse_quarter_end), errors="coerce"
    )
    df = df.dropna(subset=["cal_q_end"])

    # Deduplicate: keep max PRisk per (gvkey, quarter)
    df = df.sort_values("PRisk", ascending=False).drop_duplicates(
        subset=["gvkey", "cal_q_end"], keep="first"
    )

    df["PRisk"] = df["PRisk"].astype("float64")
    return df[["gvkey", "cal_q_end", "PRisk"]].copy()


def _compute_priskfy(
    prisk_df: pd.DataFrame,
    comp_df: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate quarterly PRisk → fiscal-year average (PRiskFY).

    Args:
        prisk_df: firm-quarter PRisk with columns [gvkey, cal_q_end, PRisk]
        comp_df:  Compustat annual (Q4-only) with columns [gvkey, fyearq, datadate]

    Returns:
        DataFrame with columns: gvkey, fyearq, PRiskFY, n_quarters_used
        Only rows with n_quarters_used >= MIN_QUARTERS are returned.
    """
    # Work with Q4-only fiscal year-ends from Compustat
    fy = (
        comp_df[["gvkey", "fyearq", "datadate"]]
        .dropna(subset=["fyearq", "datadate"])
        .drop_duplicates(subset=["gvkey", "fyearq"])
        .copy()
    )
    fy["fyearq"] = fy["fyearq"].astype(int)
    fy["datadate"] = pd.to_datetime(fy["datadate"], errors="coerce")
    fy = fy.dropna(subset=["datadate"])

    firms_with_prisk = set(prisk_df["gvkey"].unique())
    fy = fy[fy["gvkey"].isin(firms_with_prisk)].copy()

    # Pre-group PRisk by gvkey into a dict of sorted numpy arrays.
    # This eliminates the O(N_firms × N_prisk_rows) linear scan that was
    # previously performed inside the outer loop with:
    #   firm_prisk = prisk_sorted[prisk_sorted["gvkey"] == gvkey]
    # Now each gvkey lookup is O(1) dict access instead of O(N_prisk).
    prisk_arrays: Dict[str, tuple] = {}
    for gvkey_p, grp_p in prisk_df.groupby("gvkey", sort=False):
        dates = grp_p["cal_q_end"].to_numpy(dtype="datetime64[ns]")
        vals = grp_p["PRisk"].to_numpy(dtype="float64")
        sort_idx = np.argsort(dates)
        prisk_arrays[gvkey_p] = (dates[sort_idx], vals[sort_idx])

    records = []
    for gvkey, group in fy.groupby("gvkey", sort=False):
        if gvkey not in prisk_arrays:
            continue

        dates_arr, vals_arr = prisk_arrays[gvkey]

        for _, row in group.iterrows():
            fy_end = np.datetime64(row["datadate"], "ns")
            lower = fy_end - np.timedelta64(WINDOW_DAYS * 24 * 3600 * int(1e9), "ns")

            left = int(np.searchsorted(dates_arr, lower, side="right"))
            right = int(np.searchsorted(dates_arr, fy_end, side="right"))

            window = vals_arr[left:right]
            n_q = len(window)

            if n_q >= MIN_QUARTERS:
                records.append(
                    {
                        "gvkey": gvkey,
                        "fyearq": int(row["fyearq"]),
                        "PRiskFY": float(float(np.mean(window))),
                        "n_quarters_used": n_q,
                    }
                )

    if not records:
        return pd.DataFrame(columns=["gvkey", "fyearq", "PRiskFY", "n_quarters_used"])

    return pd.DataFrame(records)


class HassanEngine:
    """Load Hassan PRisk data, compute PRiskFY, and cache the result.

    Usage:
        engine = HassanEngine()
        df = engine.get_data(root_path)
        # df has columns: gvkey, fyearq, PRiskFY, n_quarters_used
    """

    def __init__(self) -> None:
        self._cache: Optional[pd.DataFrame] = None
        self._cache_root: Optional[Path] = None

    def get_data(self, root_path: Path) -> pd.DataFrame:
        """Return PRiskFY DataFrame (cached after first call)."""
        if self._cache is not None and self._cache_root == root_path:
            return self._cache

        prisk_path = root_path / PRISK_FILE
        print(f"    HassanEngine: loading PRisk from {prisk_path.name} ...")
        prisk_df = _load_prisk(prisk_path)
        print(f"    HassanEngine: {len(prisk_df):,} firm-quarter PRisk rows loaded")

        # Get Compustat annual dates (Q4 only) via CompustatEngine
        comp_engine = get_compustat_engine()
        comp_df = comp_engine.get_data(root_path)

        # Filter to Q4 rows only (fqtr == 4) for annual fiscal-year endpoints
        if "fqtr" in comp_df.columns:
            comp_q4 = comp_df[comp_df["fqtr"] == 4].copy()
        else:
            # Fallback: group by (gvkey, fyearq) keep latest datadate
            comp_q4 = (
                comp_df[["gvkey", "fyearq", "datadate"]]
                .dropna(subset=["fyearq", "datadate"])
                .sort_values("datadate")
                .drop_duplicates(subset=["gvkey", "fyearq"], keep="last")
            )

        print(
            f"    HassanEngine: computing PRiskFY for {len(comp_q4):,} firm-years ..."
        )
        priskfy = _compute_priskfy(prisk_df, comp_q4)
        n_valid = len(priskfy)
        print(
            f"    HassanEngine: PRiskFY complete — {n_valid:,} firm-years "
            f"(>={MIN_QUARTERS} quarters, {WINDOW_DAYS}-day window)"
        )

        self._cache = priskfy
        self._cache_root = root_path
        return priskfy


# Module-level singleton
_engine = HassanEngine()


def get_engine() -> HassanEngine:
    """Return the module-level singleton HassanEngine."""
    return _engine


__all__ = ["HassanEngine", "get_engine"]
