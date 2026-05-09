"""Hoberg-Phillips FIC100 industry-classification builder — H1.5.brexit_did (Module #6).

Per Campello et al. 2022 JFQA Section II.D FE specification verbatim:
"Hoberg-Phillips Fixed Industry Classification ('FIC100') × calendar quarter"
(spec lines 829, ~/.claude/plans/tender-popping-origami.md Section 6).

Reads the HP FIC dataset from inputs/Brexit_replication/HobergPhillips_FIC/FIC_Data.zip
IN-PLACE via zipfile.open() per Sina storage-constrained memory rule (no extraction).

The zip contains 'fic_data.txt' tab-separated with columns:
    gvkey, year, icode25, icode50, icode100, icode200, icode300, icode400, icode500

We project to {gvkey, year, icode100} → rename icode100 → fic100_industry_id;
restrict to year ∈ {2010..2016} matching the Brexit DiD window.

Output:
    outputs/variables/hoberg_phillips_fic100/<ts>/fic100_per_firm_year.parquet
    schema: gvkey (zfill-6 str), year (int), fic100_industry_id (int)
"""

from __future__ import annotations

import logging
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult

logger = logging.getLogger(__name__)


WINDOW_YEARS = list(range(2010, 2017))  # 2010-2016 inclusive
COL_NAME = "fic100_industry_id"


def _read_fic_zip_in_place(zip_path: Path) -> pd.DataFrame:
    """Read fic_data.txt from zip without extraction; return projected DataFrame."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        with zf.open("fic_data.txt") as f:
            buf = BytesIO(f.read())
    df = pd.read_csv(
        buf,
        sep="\t",
        usecols=["gvkey", "year", "icode100"],
        dtype={"gvkey": "Int64", "year": "Int64", "icode100": "Int64"},
    )
    df = df.dropna(subset=["gvkey", "year", "icode100"])
    df["gvkey"] = df["gvkey"].astype(int).astype(str).str.zfill(6)
    df = df.rename(columns={"icode100": COL_NAME})
    return df[["gvkey", "year", COL_NAME]]


class HobergPhillipsFIC100Builder(VariableBuilder):
    """FIC100 industry assignment per (gvkey, year) for Brexit DiD window."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = COL_NAME

    def build(self, years: range, root_path: Path) -> VariableResult:
        del years  # window fixed at Brexit panel.

        zip_path = root_path / "inputs" / "Brexit_replication" / "HobergPhillips_FIC" / "FIC_Data.zip"
        logger.info(f"HobergPhillipsFIC100Builder: reading {zip_path} in-place ...")
        df = _read_fic_zip_in_place(zip_path)
        logger.info(f"  full FIC dataset: {len(df):,} rows ({df['year'].min()}-{df['year'].max()})")

        out = df[df["year"].astype(int).isin(WINDOW_YEARS)].copy().reset_index(drop=True)
        n_firms = out["gvkey"].nunique()
        n_industries = out[COL_NAME].nunique()
        logger.info(
            f"  Brexit window 2010-2016: {len(out):,} rows; {n_firms:,} unique gvkeys; {n_industries:,} FIC100 industries"
        )

        stats = self.get_stats(out[COL_NAME], COL_NAME)
        metadata = {
            "source": "Hoberg-Phillips Fixed Industry Classification (FIC100)",
            "n_rows_brexit_window": int(len(out)),
            "n_unique_gvkeys": int(n_firms),
            "n_fic100_industries": int(n_industries),
            "year_range": [int(out["year"].min()), int(out["year"].max())],
            "column": COL_NAME,
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
