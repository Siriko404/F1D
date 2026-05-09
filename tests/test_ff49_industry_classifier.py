"""Inline pytest for FF49 industry classifier (Phase 1A Task A3).

v2 audit m1 path lock: reads inputs/FF1248/Siccodes49.zip (NOT inputs/FamaFrench/).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from f1d.shared.variables.ff49_industry_classifier import (
    FF49IndustryClassifierBuilder,
    parse_siccodes49,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def ff49_panel() -> pd.DataFrame:
    """Build FF49 panel for 2002-2010 window (Boasiako Eq 1 sub-window)."""
    return FF49IndustryClassifierBuilder().build(
        years=range(2002, 2011), root_path=ROOT
    ).data


def test_siccodes49_zip_exists():
    """v2 audit m1: file is at inputs/FF1248/, NOT inputs/FamaFrench/."""
    p = ROOT / "inputs" / "FF1248" / "Siccodes49.zip"
    assert p.exists(), f"Siccodes49.zip missing at {p}"


def test_parse_siccodes49_returns_49_industries():
    """Standard Fama-French 49-industry classification has industry codes 1-49."""
    siccodes = parse_siccodes49(ROOT / "inputs" / "FF1248" / "Siccodes49.zip")
    assert siccodes["ff49_code"].nunique() == 49
    assert siccodes["ff49_code"].min() == 1
    assert siccodes["ff49_code"].max() == 49


def test_parse_siccodes49_covers_known_sic_ranges():
    """Spot-check: SIC 0100 (Agric crops) maps to FF49=1 (Agric)."""
    siccodes = parse_siccodes49(ROOT / "inputs" / "FF1248" / "Siccodes49.zip")
    agric_row = siccodes[siccodes["sic_start"] == 100]
    assert len(agric_row) >= 1
    assert agric_row["ff49_code"].iloc[0] == 1


def test_ff49_panel_schema(ff49_panel):
    """Output schema: gvkey + fyear + ff49_code."""
    df = ff49_panel
    assert set(df.columns) >= {"gvkey", "fyear", "ff49_code"}
    assert df["ff49_code"].between(1, 49).all()


def test_ff49_codes_in_valid_range(ff49_panel):
    """All ff49_code values in 1..49."""
    df = ff49_panel
    assert df["ff49_code"].min() >= 1
    assert df["ff49_code"].max() <= 49


def test_ff49_no_duplicate_gvkey_fyear(ff49_panel):
    """One ff49_code per (gvkey, fyear); no duplicates."""
    df = ff49_panel
    dup = df.duplicated(subset=["gvkey", "fyear"]).sum()
    assert dup == 0, f"{dup} duplicate (gvkey, fyear) rows"


def test_unmapped_sic_excluded_or_flagged(ff49_panel):
    """SIC codes not in any FF49 range should not appear (we drop them).

    Some Compustat SIC codes are 9999 (placeholder) or in gaps not covered
    by the Ken French ranges; these are excluded from the output panel.
    """
    df = ff49_panel
    assert df["ff49_code"].notna().all()
