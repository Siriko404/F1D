"""Fama-French 48-industry classifier (Phase 1C Task C1).

Chen et al. 2017 JAAF spec C16 verbatim: "industry classification: FF48 (Fama-French 1997)"

Reads Ken French's Siccodes48.zip from inputs/FF1248/ (v2 audit m1 path lock).

FF48 (1997) and FF49 (1997) are DISTINCT schemes:
- FF49 has 49 industries; FF48 has 48
- Some SIC range mappings differ between schemes
- Cannot share builder with Boasiako's FF49

Used by:
- Chen baseline controls SIGMA (industry-MEDIAN OCF σ over 10y, FF48)
- Chen PSM matching (within-FF48 industry constraint)
- Chen PS_DEMAND channel test (FF48 industry-MEDIAN aggregation)

Output (per gvkey × fyear):
    gvkey, fyear, ff48_code, ff48_name
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


_HEADER_RE = re.compile(r"^\s*(\d{1,2})\s+(\S+)\s+(.+)$")
_RANGE_RE = re.compile(r"^\s+(\d{4})-(\d{4})\s+(.*)$")


def parse_siccodes48(zip_path: Path) -> pd.DataFrame:
    """Parse Ken French Siccodes48.zip → (ff48_code, sic_start, sic_end) ranges."""
    if not zip_path.exists():
        raise FileNotFoundError(f"Siccodes48.zip not found at {zip_path}")

    with zipfile.ZipFile(zip_path) as zf:
        members = [n for n in zf.namelist() if n.lower().endswith(".txt")]
        if not members:
            raise ValueError(f"No .txt member in {zip_path}")
        with zf.open(members[0]) as f:
            text = f.read().decode("utf-8", errors="replace")

    rows = []
    current_code = None
    current_name = None
    for line in text.splitlines():
        if not line.strip():
            continue
        leading_ws = len(line) - len(line.lstrip())
        if leading_ws <= 3:
            m = _HEADER_RE.match(line)
            if m:
                current_code = int(m.group(1))
                current_name = m.group(2)
                continue
        m = _RANGE_RE.match(line)
        if m and current_code is not None:
            rows.append({
                "ff48_code": current_code,
                "ff48_name": current_name,
                "sic_start": int(m.group(1)),
                "sic_end": int(m.group(2)),
            })
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError(f"Failed to parse SIC ranges from {zip_path}")
    return df


def _map_sic_to_ff48(sic: pd.Series, ranges: pd.DataFrame) -> pd.Series:
    sic_arr = sic.to_numpy()
    starts = ranges["sic_start"].to_numpy()
    ends = ranges["sic_end"].to_numpy()
    codes = ranges["ff48_code"].to_numpy()
    out = np.full(len(sic_arr), np.nan)
    for i, s in enumerate(sic_arr):
        if pd.isna(s):
            continue
        s_int = int(s)
        match = (starts <= s_int) & (s_int <= ends)
        if match.any():
            out[i] = codes[match.argmax()]
    return pd.Series(out, index=sic.index, dtype="Int64")


class FF48IndustryClassifierBuilder(VariableBuilder):
    """Build (gvkey, fyear, ff48_code) panel via SIC range mapping."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = "ff48_code"

    def build(self, years: range, root_path: Path) -> VariableResult:
        zip_path = root_path / "inputs" / "FF1248" / "Siccodes48.zip"
        ranges = parse_siccodes48(zip_path)

        comp = read_compustat_annual(
            path=root_path / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
            cols=["gvkey", "datadate", "sic"],
            years=years,
            us_only=True,
            sic_excl=(),  # no excl at classifier level; runner-side filter
        )
        comp = comp.dropna(subset=["sic"]).copy()
        comp["sic"] = comp["sic"].astype("Int64")
        comp["ff48_code"] = _map_sic_to_ff48(comp["sic"], ranges)
        comp = comp.dropna(subset=["ff48_code"]).copy()
        comp["ff48_code"] = comp["ff48_code"].astype(int)

        name_map = ranges.drop_duplicates("ff48_code").set_index("ff48_code")["ff48_name"]
        comp["ff48_name"] = comp["ff48_code"].map(name_map)

        comp = comp.sort_values(["gvkey", "fyear", "datadate"], kind="stable")
        comp = comp.drop_duplicates(subset=["gvkey", "fyear"], keep="last")

        out = comp[["gvkey", "fyear", "ff48_code", "ff48_name"]].reset_index(drop=True)

        stats = VariableStats(
            name="ff48_code",
            n=len(out),
            mean=float(out["ff48_code"].mean()),
            std=float(out["ff48_code"].std()),
            min=int(out["ff48_code"].min()),
            p25=float(out["ff48_code"].quantile(0.25)),
            median=float(out["ff48_code"].median()),
            p75=float(out["ff48_code"].quantile(0.75)),
            max=int(out["ff48_code"].max()),
            n_missing=0,
            pct_missing=0.0,
        )
        metadata: Dict[str, Any] = {
            "source": "Ken French Siccodes48.zip",
            "path": str(zip_path),
            "n_industries_distinct": int(out["ff48_code"].nunique()),
            "n_firm_years": len(out),
            "column": "ff48_code",
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
