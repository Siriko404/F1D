"""Fama-French 49-industry classifier (Phase 1A Task A3).

Boasiako Eq 1 spec §3.2 footnote 5 (verbatim): "The industry dummies are
constructed based on the 49-industry classification of Fama and French (1997)."

Reads Ken French's Siccodes49.zip (acquired one-shot during Brexit Phase 0
and stored at ``inputs/FF1248/Siccodes49.zip`` per v2 audit m1 path lock —
NOT ``inputs/FamaFrench/`` which only contains 25_Portfolios_5x5_CSV.zip).

Format of Siccodes49.txt (extracted from .zip):

    1 Agric  Agriculture
              0100-0199 Agricultural production - crops
              0200-0299 Agricultural production - livestock
              ...
    2 Food   Food Products
              2000-2009 Food and kindred products
              ...
    49 Other Almost Nothing

Industry headers start in column 1 (no leading whitespace); SIC range lines
are indented. We parse both into a (ff49_code, sic_start, sic_end) lookup
table and apply via interval merge to Compustat Annual ``sic`` field.

Output (per gvkey × fyear):
    gvkey, fyear, ff49_code, ff49_name

Firms with SIC codes not in any FF49 range (e.g., placeholder 9999) are
DROPPED from the output (not flagged). FF49 by design covers nearly all
real industries; missing-SIC rows are typically data-quality issues.

Used by:
- Boasiako Eq 1 (industry FE per spec §3.2)
- Boasiako Eq 1 industry CF Vol (10y σ over industry-MEAN CF, FF49)
- NOT used by Chen (Chen uses FF48; see ff48_industry_classifier.py)
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from f1d.shared._compustat_annual_reader import read_compustat_annual

from .base import VariableBuilder, VariableResult, VariableStats


# Header line: "<code> <abbrev>  <description>" starting at column 1
# E.g., "  1 Agric  Agriculture"
_HEADER_RE = re.compile(r"^\s*(\d{1,2})\s+(\S+)\s+(.+)$")
# Range line: indented "<sic_start>-<sic_end> <description>"
# E.g., "          0100-0199 Agricultural production - crops"
_RANGE_RE = re.compile(r"^\s+(\d{4})-(\d{4})\s+(.*)$")


def parse_siccodes49(zip_path: Path) -> pd.DataFrame:
    """Parse Ken French Siccodes49.zip → DataFrame of (ff49_code, sic_start, sic_end) ranges.

    Args:
        zip_path: path to Siccodes49.zip (e.g., ``inputs/FF1248/Siccodes49.zip``)

    Returns:
        DataFrame with cols: ff49_code (int), ff49_name (str), sic_start (int),
        sic_end (int). One row per SIC range. Multiple ranges per industry possible.
    """
    if not zip_path.exists():
        raise FileNotFoundError(f"Siccodes49.zip not found at {zip_path}")

    with zipfile.ZipFile(zip_path) as zf:
        # Find the .txt member (case-insensitive)
        members = [n for n in zf.namelist() if n.lower().endswith(".txt")]
        if not members:
            raise ValueError(f"No .txt member in {zip_path}")
        txt_name = members[0]
        with zf.open(txt_name) as f:
            text = f.read().decode("utf-8", errors="replace")

    rows = []
    current_code = None
    current_name = None
    for line in text.splitlines():
        if not line.strip():
            continue
        # Try header first (starts at col 1, no leading whitespace OR leading 1-3 spaces)
        # Headers in this file have leading 0-3 spaces before the digit
        # Range lines have ≥6 leading spaces
        leading_ws = len(line) - len(line.lstrip())
        if leading_ws <= 3:
            m = _HEADER_RE.match(line)
            if m:
                current_code = int(m.group(1))
                current_name = m.group(2)
                continue
        # Otherwise try range
        m = _RANGE_RE.match(line)
        if m and current_code is not None:
            sic_start = int(m.group(1))
            sic_end = int(m.group(2))
            rows.append({
                "ff49_code": current_code,
                "ff49_name": current_name,
                "sic_start": sic_start,
                "sic_end": sic_end,
            })

    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError(f"Failed to parse any SIC ranges from {zip_path}")
    return df


def _map_sic_to_ff49(sic: pd.Series, ranges: pd.DataFrame) -> pd.Series:
    """Vectorized SIC → ff49_code mapping via range lookup.

    Args:
        sic: pd.Series of integer SIC codes
        ranges: DataFrame with cols ff49_code, sic_start, sic_end

    Returns:
        pd.Series of ff49_code aligned to sic.index; NaN if SIC not in any range.
    """
    sic_arr = sic.to_numpy()
    starts = ranges["sic_start"].to_numpy()
    ends = ranges["sic_end"].to_numpy()
    codes = ranges["ff49_code"].to_numpy()

    # For each SIC, find first range matching sic_start <= sic <= sic_end
    # Vectorized via broadcasting (memory: n_firms × n_ranges; ~80k × ~150 = 12M comparisons; OK)
    out = np.full(len(sic_arr), np.nan)
    for i, s in enumerate(sic_arr):
        if pd.isna(s):
            continue
        s_int = int(s)
        match = (starts <= s_int) & (s_int <= ends)
        if match.any():
            out[i] = codes[match.argmax()]  # first match
    return pd.Series(out, index=sic.index, dtype="Int64")


class FF49IndustryClassifierBuilder(VariableBuilder):
    """Build (gvkey, fyear, ff49_code) panel via SIC range mapping."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = "ff49_code"

    def build(self, years: range, root_path: Path) -> VariableResult:
        zip_path = root_path / "inputs" / "FF1248" / "Siccodes49.zip"
        ranges = parse_siccodes49(zip_path)

        comp = read_compustat_annual(
            path=root_path / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
            cols=["gvkey", "datadate", "sic"],
            years=years,
            us_only=True,
            sic_excl=(),  # FF49 itself doesn't drop financials/utilities; runner-side filter
        )
        # SIC sometimes missing or invalid; drop rows where SIC is NaN
        comp = comp.dropna(subset=["sic"]).copy()
        comp["sic"] = comp["sic"].astype("Int64")

        # Map SIC → ff49_code
        comp["ff49_code"] = _map_sic_to_ff49(comp["sic"], ranges)
        comp = comp.dropna(subset=["ff49_code"]).copy()
        comp["ff49_code"] = comp["ff49_code"].astype(int)

        # Attach industry name
        name_map = ranges.drop_duplicates("ff49_code").set_index("ff49_code")["ff49_name"]
        comp["ff49_name"] = comp["ff49_code"].map(name_map)

        # Dedup to (gvkey, fyear) — Compustat may have multiple datadates per fyear
        comp = comp.sort_values(["gvkey", "fyear", "datadate"], kind="stable")
        comp = comp.drop_duplicates(subset=["gvkey", "fyear"], keep="last")

        out = comp[["gvkey", "fyear", "ff49_code", "ff49_name"]].reset_index(drop=True)

        stats = VariableStats(
            name="ff49_code",
            n=len(out),
            mean=float(out["ff49_code"].mean()),
            std=float(out["ff49_code"].std()),
            min=int(out["ff49_code"].min()),
            p25=float(out["ff49_code"].quantile(0.25)),
            median=float(out["ff49_code"].median()),
            p75=float(out["ff49_code"].quantile(0.75)),
            max=int(out["ff49_code"].max()),
            n_missing=0,
            pct_missing=0.0,
        )
        metadata: Dict[str, Any] = {
            "source": "Ken French Siccodes49.zip",
            "path": str(zip_path),
            "n_industries_distinct": int(out["ff49_code"].nunique()),
            "n_firm_years": len(out),
            "column": "ff49_code",
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
