"""Builder for sub-topical Political Risk variables — Hassan et al. (2019).

Loads Hassan et al. (2019) firm-level quarterly Political Risk SUB-TOPICS
(8 categories: economic, environment, trade, institutions, health, security,
tax, technology). Used by H1.5 Trump 2016 DiD design where treatment is
firm exposure to *trade* and *tax* policy specifically (Trump's two main
levers: tariffs + TCJA).

Mirrors prisk_q.py structure (overall PRisk loader) but returns multi-column
VariableResult with all requested sub-topic columns.

Input: inputs/FirmLevelRisk/firmquarter_2022q1.csv (TAB-separated)
Columns used: gvkey, date (format "YYYYqQ"), PRiskT_trade, PRiskT_tax,
              (optional: PRiskT_economic, PRiskT_environment, PRiskT_institutions,
                         PRiskT_health, PRiskT_security, PRiskT_technology)

Processing:
    1. Load quarterly TSV, parse date column ("2010q2" -> cal_q="2010q2")
    2. Filter to requested years
    3. Apply per-year 1%/99% winsorization to EACH sub-topic column independently
    4. For each call, determine calendar quarter from start_date
    5. Merge on (gvkey, cal_q)

Output columns: file_name, PRiskT_trade, PRiskT_tax (default subset)
                Optionally include all 8 sub-topics via config["include_all"] = True

Temporal Structure:
    Sub-topic PRisk measured over calendar quarter Q
    Earnings call happens within calendar quarter Q
    Contemporaneous match (same quarter, no lag) — mirrors PRiskQBuilder
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats
from .winsorization import winsorize_by_year
from f1d.shared.path_utils import get_latest_output_dir


PRISK_FILE = "inputs/FirmLevelRisk/firmquarter_2022q1.csv"

# Default sub-topic columns loaded — H1.5 Trump 2016 DiD treatment needs these two.
DEFAULT_SUBTOPICS: List[str] = ["PRiskT_trade", "PRiskT_tax"]

# All 8 Hassan et al. (2019) sub-topics (verified 2026-05-06 from inputs schema).
ALL_SUBTOPICS: List[str] = [
    "PRiskT_economic",
    "PRiskT_environment",
    "PRiskT_trade",
    "PRiskT_institutions",
    "PRiskT_health",
    "PRiskT_security",
    "PRiskT_tax",
    "PRiskT_technology",
]


def _parse_cal_q(date_str: str) -> Optional[str]:
    """Convert 'YYYYqQ' string -> calendar quarter string 'YYYYqQ'.

    Mirrors prisk_q._parse_cal_q exactly for consistency.
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


def _load_prisk_subtopics_quarterly(
    prisk_path: Path, years: range, subtopic_cols: List[str]
) -> pd.DataFrame:
    """Load and clean the Hassan PRisk sub-topic columns from quarterly TSV.

    Args:
        prisk_path: Path to the PRisk TSV (firmquarter_2022q1.csv)
        years: Range of years to include
        subtopic_cols: List of sub-topic column names to load (e.g. PRiskT_trade)

    Returns:
        DataFrame with columns: gvkey, cal_q, year, <subtopic_cols>
    """
    if not prisk_path.exists():
        raise FileNotFoundError(f"PRisk data not found: {prisk_path}")

    needed_cols = ["gvkey", "date"] + list(subtopic_cols)
    df = pd.read_csv(
        prisk_path, sep="\t", on_bad_lines="skip", usecols=needed_cols
    )
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    # Drop rows where ALL requested sub-topics are NaN (no information)
    df = df.dropna(subset=subtopic_cols, how="all")

    # Parse cal_q
    df["cal_q"] = df["date"].apply(_parse_cal_q)
    df = df.dropna(subset=["cal_q"])

    df["year"] = df["cal_q"].str[:4].astype(int)
    df = df[df["year"].isin(list(years))].copy()

    # Deduplicate (gvkey, cal_q) — keep row with max sum of sub-topics
    df["_sum_subtopics"] = df[subtopic_cols].sum(axis=1, skipna=True)
    df = df.sort_values("_sum_subtopics", ascending=False).drop_duplicates(
        subset=["gvkey", "cal_q"], keep="first"
    )
    df = df.drop(columns=["_sum_subtopics"])

    for col in subtopic_cols:
        df[col] = df[col].astype("float64")

    return df[["gvkey", "cal_q", "year"] + list(subtopic_cols)].copy()


class PRiskSubtopicsBuilder(VariableBuilder):
    """Match quarterly PRisk SUB-TOPIC columns onto each call by (gvkey, cal_q).

    By default loads 2 columns required for H1.5 Trump DiD treatment label:
        PRiskT_trade, PRiskT_tax
    Set config["include_all"] = True to load all 8 Hassan sub-topics.

    Per-year 1%/99% winsorization applied independently to each sub-topic
    column (same approach as PRiskQBuilder for overall PRisk).

    Returned VariableResult.data has columns:
        file_name, <subtopic_1>, <subtopic_2>, ...
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if config.get("include_all", False):
            self.subtopics: List[str] = list(ALL_SUBTOPICS)
        else:
            self.subtopics = list(config.get("subtopics", DEFAULT_SUBTOPICS))
        # Primary "column" attr (used by base.get_stats) — pick first sub-topic
        self.column = self.subtopics[0] if self.subtopics else "PRiskT_trade"

    def build(self, years: range, root_path: Path) -> VariableResult:
        # 1. Load manifest for file_name -> (gvkey, cal_q) mapping
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
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        manifest["cal_q"] = (
            manifest["start_date"].dt.year.astype(str)
            + "q"
            + manifest["start_date"].dt.quarter.astype(str)
        )

        # 2. Load PRisk sub-topic columns
        prisk_path = root_path / PRISK_FILE
        print(
            f"    PRiskSubtopicsBuilder: loading {len(self.subtopics)} sub-topics "
            f"({', '.join(self.subtopics)}) from {prisk_path.name} ..."
        )
        prisk_df = _load_prisk_subtopics_quarterly(prisk_path, years, self.subtopics)
        print(
            f"    PRiskSubtopicsBuilder: {len(prisk_df):,} firm-quarter rows loaded"
        )

        # 3. Per-year 1%/99% winsorization on each sub-topic
        prisk_df = winsorize_by_year(prisk_df, list(self.subtopics), year_col="year")
        print(
            "    PRiskSubtopicsBuilder: per-year 1%/99% winsorization applied"
        )

        # 4. Merge to manifest on (gvkey, cal_q)
        merge_cols = ["gvkey", "cal_q"] + list(self.subtopics)
        merged = manifest.merge(
            prisk_df[merge_cols], on=["gvkey", "cal_q"], how="left"
        )

        # 5. Align back to manifest order, return (file_name, <subtopics>)
        out_cols = ["file_name"] + list(self.subtopics)
        data = manifest[["file_name"]].merge(
            merged[out_cols], on="file_name", how="left"
        )
        data = data.drop_duplicates(subset=["file_name"])

        # Per-subtopic match stats
        n_total = len(data)
        for col in self.subtopics:
            n_matched = int(data[col].notna().sum())
            pct = 100.0 * n_matched / n_total if n_total > 0 else 0.0
            print(
                f"    PRiskSubtopicsBuilder: {col:25s} matched "
                f"{n_matched:,} / {n_total:,} ({pct:.1f}%)"
            )

        # Stats for primary column (first sub-topic) — base.get_stats requires single Series.
        stats = self.get_stats(data[self.column], self.column)

        return VariableResult(
            data=data[out_cols].copy(),
            stats=stats,
            metadata={
                "columns": list(self.subtopics),
                "primary_column": self.column,
                "source": "Hassan et al. (2019) firm-level quarterly PRisk sub-topics",
                "description": (
                    "Quarterly political-risk sub-topic shares matched to calls by "
                    "(gvkey, calendar_quarter). Per-year 1%/99% winsorized. "
                    "Contemporaneous (no lag) — mirrors PRiskQBuilder."
                ),
                "n_total": int(n_total),
            },
        )


__all__ = ["PRiskSubtopicsBuilder", "DEFAULT_SUBTOPICS", "ALL_SUBTOPICS"]
