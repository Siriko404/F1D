"""Inline pytest for FF48 industry classifier (Phase 1C Task C1)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from f1d.shared.variables.ff48_industry_classifier import (
    FF48IndustryClassifierBuilder,
    parse_siccodes48,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def ff48_panel() -> pd.DataFrame:
    return FF48IndustryClassifierBuilder().build(
        years=range(1997, 2007), root_path=ROOT
    ).data


def test_siccodes48_zip_exists():
    assert (ROOT / "inputs" / "FF1248" / "Siccodes48.zip").exists()


def test_parse_siccodes48_returns_48_industries():
    siccodes = parse_siccodes48(ROOT / "inputs" / "FF1248" / "Siccodes48.zip")
    assert siccodes["ff48_code"].nunique() == 48
    assert siccodes["ff48_code"].min() == 1
    assert siccodes["ff48_code"].max() == 48


def test_ff48_panel_schema(ff48_panel):
    assert {"gvkey", "fyear", "ff48_code"}.issubset(ff48_panel.columns)
    assert ff48_panel["ff48_code"].between(1, 48).all()


def test_ff48_no_duplicate_gvkey_fyear(ff48_panel):
    assert ff48_panel.duplicated(subset=["gvkey", "fyear"]).sum() == 0


def test_ff48_distinct_from_ff49():
    """FF48 + FF49 are distinct schemes; some firms get different industry codes."""
    from f1d.shared.variables.ff49_industry_classifier import FF49IndustryClassifierBuilder
    ff48 = FF48IndustryClassifierBuilder().build(years=range(2000, 2003), root_path=ROOT).data
    ff49 = FF49IndustryClassifierBuilder().build(years=range(2000, 2003), root_path=ROOT).data
    merged = ff48.merge(ff49, on=["gvkey", "fyear"], how="inner")
    # Expect non-trivial difference for some firms (but not all — many SIC codes map identically)
    n_diff = (merged["ff48_code"] != merged["ff49_code"]).sum()
    assert n_diff > 0, "FF48 and FF49 should differ for at least some firms"
