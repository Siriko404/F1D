"""Compustat Annual ad-hoc CSV reader (Phase 1A Task A2).

Boasiako Eq 1 + Chen Restatement DiDs need ANNUAL Compustat data
(F1D's existing `_compustat_engine.py` handles QUARTERLY only via fundq;
this utility reads ANNUAL fundamental from inputs/Compustat_Annual/compustat_annual.csv).

Brexit Phase 1 lessons baked in:
- decimal.Decimal dtype trap → pd.to_numeric(col, errors='coerce') applied IMMEDIATELY
  on every numeric column post-CSV-read. Without this, numpy.quantile and
  pd.DataFrame.clip break with TypeError on Decimal × float comparisons.
- gvkey zero-padded to 6-char string for clean cross-merge with F1D conventions.

v2 audit M7: us_only=True filter (default) drops 17.4% of F1D rows that are
non-US (10,566 Canadian firms + others). Without this filter, Boasiako's
Disclosure_Law merge on `state` silently lumps US firms (state='CA' = California)
with Canadian firms (state='CA' if Canadian-Compustat 2-letter overlap).

Precedent: src/f1d/shared/variables/_archived/employment_growth_lead.py reads
this same CSV directly (~327k rows, ~1 GB).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd

# Compustat string-typed cols (do NOT coerce to numeric)
STRING_COLS = frozenset({
    "gvkey", "datadate", "sic", "tic", "cusip", "cik", "conm", "conml",
    "state", "addzip", "loc", "incorp", "fic", "naics", "exchg", "curcd",
    "datafmt", "indfmt", "consol", "costat", "city", "county", "weburl",
    "phone", "fax", "ein", "busdesc", "spcindcd", "spcseccd", "spcsrc",
    "ipodate", "dldte", "dlrsn", "fyrc", "ggroup", "gind", "gsector",
    "gsubind", "idbflag", "prican", "prirow", "priusa", "stko", "spcindi",
    "add1", "add2", "add3", "add4",
})


def read_compustat_annual(
    path: Path,
    cols: List[str],
    years: Optional[Iterable[int]] = None,
    sic_excl: Iterable[range] = (range(6000, 7000), range(4900, 5000)),
    us_only: bool = True,
) -> pd.DataFrame:
    """Read Compustat Annual CSV with Decimal-trap guard + standard filters.

    Args:
        path: path to compustat_annual.csv (default
              ``inputs/Compustat_Annual/compustat_annual.csv``).
        cols: subset of columns to load. ``gvkey``, ``datadate``, ``sic`` are
              ALWAYS auto-included. ``loc`` is auto-included when ``us_only=True``.
        years: optional fyear filter (e.g., ``range(1997, 2016)`` for Boasiako).
        sic_excl: ranges of SIC codes to drop. Default = Boasiako/Chen excl
                  SIC 6000-6999 (financial) + SIC 4900-4999 (utility). Pass
                  empty tuple ``()`` to skip industry exclusions.
        us_only: if True (v2 default per audit M7), filter to ``loc=='USA'``.
                 Required for Boasiako Eq 1 since Compustat ``state`` field is
                 HQ state for US firms but PROVINCE for Canadian firms.

    Returns:
        DataFrame with:
        - All specified ``cols`` loaded
        - All numeric cols guaranteed float64 (Decimal coerced via pd.to_numeric)
        - ``datadate`` parsed as datetime64
        - ``fyear`` int derived from ``datadate``
        - ``gvkey`` 6-char zero-padded string
        - Industry exclusions applied
        - Non-US firms dropped if ``us_only=True``

    Raises:
        FileNotFoundError: if ``path`` does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Compustat Annual CSV not found at {path}")

    needed_cols = set(cols) | {"gvkey", "datadate", "sic"}
    if us_only:
        needed_cols.add("loc")

    # Restrict CSV read to needed cols only (memory budget: ~327k rows × ~10 cols ≈ 50 MB)
    df = pd.read_csv(path, usecols=lambda c: c in needed_cols, low_memory=False)

    # Brexit Phase 1 lesson: coerce numeric cols IMMEDIATELY (decimal.Decimal trap)
    for c in df.columns:
        if c in STRING_COLS:
            continue
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # gvkey: zero-pad to 6-char string (handles int → "001750" mapping)
    df["gvkey"] = df["gvkey"].astype("Int64").astype(str).str.zfill(6)
    # Re-coerce '<NA>' rows to NaN before downstream filters
    df = df[df["gvkey"] != "<NA>".zfill(6)]

    # datadate: parse as datetime64
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df.dropna(subset=["datadate"])
    df["fyear"] = df["datadate"].dt.year.astype("Int64")

    # us_only filter (audit M7)
    if us_only:
        df = df[df["loc"] == "USA"].copy()

    # Year filter
    if years is not None:
        years_set = set(years)
        df = df[df["fyear"].isin(years_set)].copy()

    # SIC exclusions
    if sic_excl:
        df["sic"] = pd.to_numeric(df["sic"], errors="coerce").astype("Int64")
        for r in sic_excl:
            df = df[~df["sic"].between(r.start, r.stop - 1)].copy()

    return df.reset_index(drop=True)
