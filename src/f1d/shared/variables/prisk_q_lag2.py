"""Builder for 2-quarter lagged Political Risk (PRiskQ_lag2) variable — H11-Lag2.

Loads Hassan et al. (2019) quarterly PRisk data and matches to earnings calls
by (gvkey, lagged_calendar_quarter - 2).

For a call in calendar quarter Q, matches PRisk from quarter Q-2.

Input: inputs/FirmLevelRisk/firmquarter_2022q1.csv (TAB-separated)
Columns: gvkey, date (format: "YYYYqQ"), PRisk

Processing:
    1. Load quarterly data, parse date column ("2010q2" → cal_q="2010q2")
    2. Filter to requested years (and years 1-2 for lag matches)
    3. Apply per-year 1%/99% winsorization
    4. For each call, determine calendar quarter from start_date
    5. Compute 2-quarter lagged calendar quarter
    6. Merge on (gvkey, cal_q_lag2)

Output columns: file_name, PRiskQ_lag2

Temporal Structure:
    PRiskQ_lag2 is measured over calendar quarter Q-2
    Earnings call happens within calendar quarter Q
    2-quarter lagged relationship
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats
from .winsorization import winsorize_by_year
from f1d.shared.path_utils import get_latest_output_dir


PRISK_FILE = "inputs/FirmLevelRisk/firmquarter_2022q1.csv"


def _parse_cal_q(date_str: str) -> Optional[str]:
    """Convert 'YYYYqQ' string → calendar quarter string 'YYYYqQ'.

    Args:
        date_str: Date string in format "2010q2" or "2010Q2"

    Returns:
        Calendar quarter string in format "2010q2" (lowercase q), or None if invalid
    """
    try:
        parts = str(date_str).lower().strip().split("q")
        if len(parts) != 2:
            return None
        year, quarter = int(parts[0]), int(parts[1])
        if quarter not in [1, 2, 3, 4]:
            return None
        return f"{year}q{quarter}"
    except (ValueError, AttributeError):
        return None


def _get_prev2_quarter(cal_q: str) -> str:
    """Convert calendar quarter to 2 quarters ago.

    Args:
        cal_q: Calendar quarter string in format "2010q2"

    Returns:
        Calendar quarter string 2 quarters ago, e.g., "2010q2" → "2009q4", "2010q3" → "2009q1"
    """
    year, quarter = int(cal_q[:4]), int(cal_q[-1])
    # Go back 2 quarters
    if quarter == 1:
        return f"{year-1}q3"
    elif quarter == 2:
        return f"{year-1}q4"
    else:
        return f"{year}q{quarter-2}"


def _load_prisk_quarterly_lag2(prisk_path: Path, years: range) -> pd.DataFrame:
    """Load and clean the Hassan PRisk quarterly CSV.

    Args:
        prisk_path: Path to the PRisk CSV file
        years: Range of years to include (also includes years 1-2 for lag matches)

    Returns:
        DataFrame with columns: gvkey, cal_q, PRisk, year
    """
    if not prisk_path.exists():
        raise FileNotFoundError(f"PRisk data not found: {prisk_path}")

    df = pd.read_csv(prisk_path, sep="\t", on_bad_lines="skip")
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df = df.dropna(subset=["PRisk"])

    # Parse calendar quarter from date column
    df["cal_q"] = df["date"].apply(_parse_cal_q)
    df = df.dropna(subset=["cal_q"])

    # Extract year for filtering and winsorization
    df["year"] = df["cal_q"].str[:4].astype(int)

    # Filter to requested years PLUS previous 2 years (for lag-2 matches)
    year_list = list(years)
    if year_list:
        year_list.extend([min(year_list) - 1, min(year_list) - 2])
    df = df[df["year"].isin(year_list)].copy()

    # Deduplicate: keep max PRisk per (gvkey, cal_q)
    df = df.sort_values("PRisk", ascending=False).drop_duplicates(
        subset=["gvkey", "cal_q"], keep="first"
    )

    df["PRisk"] = df["PRisk"].astype("float64")
    return df[["gvkey", "cal_q", "PRisk", "year"]].copy()


class PRiskQLag2Builder(VariableBuilder):
    """Match 2-quarter lagged PRisk onto each earnings call.

    For a call in calendar quarter Q, matches PRisk from quarter Q-2.
    This provides a longer lagged independent variable for causal inference.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.column = "PRiskQ_lag2"

    def build(self, years: range, root_path: Path) -> VariableResult:
        # 1. Load manifest to get file_name + gvkey + start_date
        manifest_dir = get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
        manifest_path = manifest_dir / "master_sample_manifest.parquet"

        manifest = pd.read_parquet(
            manifest_path, columns=["file_name", "gvkey", "start_date"]
        )
        manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year

        # Filter manifest to requested years
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        # 2. Compute calendar quarter from start_date
        manifest["cal_q"] = (
            manifest["start_date"].dt.year.astype(str)
            + "q"
            + manifest["start_date"].dt.quarter.astype(str)
        )

        # 3. Compute 2-QUARTER LAGGED calendar quarter
        manifest["cal_q_lag2"] = manifest["cal_q"].apply(_get_prev2_quarter)

        # 4. Load quarterly PRisk data (includes 2 previous years for lag-2 matches)
        prisk_path = root_path / PRISK_FILE
        print(f"    PRiskQLag2Builder: loading from {prisk_path.name} ...")
        prisk_df = _load_prisk_quarterly_lag2(prisk_path, years)
        print(f"    PRiskQLag2Builder: {len(prisk_df):,} firm-quarter PRisk rows loaded")

        # 5. Apply per-year winsorization (1%/99%)
        prisk_df = winsorize_by_year(prisk_df, ["PRisk"], year_col="year")
        print(f"    PRiskQLag2Builder: applied per-year 1%/99% winsorization")

        # 6. Merge on (gvkey, cal_q_lag2)
        merged = manifest.merge(
            prisk_df[["gvkey", "cal_q", "PRisk"]],
            left_on=["gvkey", "cal_q_lag2"],
            right_on=["gvkey", "cal_q"],
            how="left",
            suffixes=("", "_prisk"),
        )

        # Rename PRisk to PRiskQ_lag2
        merged = merged.rename(columns={"PRisk": "PRiskQ_lag2"})

        # 7. Align back to original manifest (preserve row order & count)
        data = manifest[["file_name"]].merge(
            merged[["file_name", "PRiskQ_lag2"]], on="file_name", how="left"
        )
        data = data.drop_duplicates(subset=["file_name"])

        # Compute match statistics
        n_matched = data["PRiskQ_lag2"].notna().sum()
        n_total = len(data)
        pct_matched = 100.0 * n_matched / n_total if n_total > 0 else 0.0
        print(
            f"    PRiskQLag2Builder: matched {n_matched:,} / {n_total:,} calls ({pct_matched:.1f}%)"
        )

        return VariableResult(
            data=data[["file_name", "PRiskQ_lag2"]].copy(),
            stats=self.get_stats(data["PRiskQ_lag2"], "PRiskQ_lag2"),
            metadata={
                "column": "PRiskQ_lag2",
                "source": "Hassan et al. (2019) quarterly PRisk",
                "description": (
                    "2-quarter lagged political risk exposure matched to calls by "
                    "(gvkey, calendar_quarter-2). Per-year 1%/99% winsorized. "
                    "Lagged by two quarters (t-2)."
                ),
                "n_matched": n_matched,
                "n_total": n_total,
                "pct_matched": pct_matched,
            },
        )


__all__ = ["PRiskQLag2Builder"]
