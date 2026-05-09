"""Inline pytest for _compustat_annual_reader utility (Phase 1A Task A2).

v2 audit M7: us_only=True filter (17.4% of F1D rows are non-US).
v2 Brexit-Phase-1 lesson: decimal.Decimal dtype trap caught via pd.to_numeric.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from f1d.shared._compustat_annual_reader import read_compustat_annual

ROOT = Path(__file__).resolve().parents[1]
ANNUAL_CSV = ROOT / "inputs" / "Compustat_Annual" / "compustat_annual.csv"


@pytest.fixture(scope="module")
def small_us_sample() -> pd.DataFrame:
    """Small US-only sample for fast tests."""
    return read_compustat_annual(
        path=ANNUAL_CSV,
        cols=["gvkey", "datadate", "at", "che", "loc", "state"],
        years=range(2010, 2013),
        us_only=True,
    )


def test_at_is_float_not_decimal(small_us_sample):
    """v2 Brexit-lesson: numeric cols must be float64, not object/Decimal.

    pd.to_numeric(..., errors='coerce') applied at read time prevents the
    decimal.Decimal trap that broke Brexit Phase 1's 1% winsorization.
    """
    df = small_us_sample
    assert df["at"].dtype.kind == "f", f"at dtype is {df['at'].dtype}, expected float"
    assert df["che"].dtype.kind == "f"
    # Spot-check: no Decimal objects in head
    head_at = df["at"].dropna().head(10).tolist()
    assert not any(type(x).__name__ == "Decimal" for x in head_at)


def test_us_only_filter_drops_canadian(small_us_sample):
    """v2 audit M7: us_only=True drops Canadian firms (10,566 in F1D)."""
    df = small_us_sample
    assert (df["loc"] == "USA").all(), "us_only=True must filter to USA only"


def test_sic_excl_drops_financials_and_utilities():
    """Default sic_excl drops SIC 6000-6999 (financial) + 4900-4999 (utility)."""
    df = read_compustat_annual(
        path=ANNUAL_CSV,
        cols=["gvkey", "datadate", "at"],
        years=range(2010, 2012),
        us_only=True,
    )
    # SIC was already filtered; we verify by re-loading without filter and comparing
    df_unfiltered = read_compustat_annual(
        path=ANNUAL_CSV,
        cols=["gvkey", "datadate", "at"],
        years=range(2010, 2012),
        us_only=True,
        sic_excl=(),  # empty tuple = no exclusion
    )
    assert len(df) < len(df_unfiltered), "sic_excl filter must drop rows"


def test_year_filter_applies():
    """years=range(2010, 2013) keeps fyear in {2010, 2011, 2012}."""
    df = read_compustat_annual(
        path=ANNUAL_CSV,
        cols=["gvkey", "datadate", "at"],
        years=range(2010, 2013),
        us_only=True,
    )
    assert set(df["fyear"].dropna().unique()).issubset({2010, 2011, 2012})


def test_gvkey_is_zero_padded_string(small_us_sample):
    """gvkey must be 6-char zero-padded string for downstream merges."""
    df = small_us_sample
    assert df["gvkey"].dtype == object
    sample_gvkeys = df["gvkey"].head(5).tolist()
    for g in sample_gvkeys:
        assert isinstance(g, str)
        assert len(g) == 6
        assert g.isdigit()


def test_datadate_is_datetime(small_us_sample):
    """datadate must be datetime64 for date-based operations."""
    df = small_us_sample
    assert pd.api.types.is_datetime64_any_dtype(df["datadate"])


def test_us_only_false_keeps_canadian():
    """us_only=False (Chen path may need this) keeps non-US firms."""
    df_with_intl = read_compustat_annual(
        path=ANNUAL_CSV,
        cols=["gvkey", "datadate", "at", "loc"],
        years=range(2010, 2012),
        us_only=False,
    )
    locs = set(df_with_intl["loc"].dropna().unique())
    # Expect at least USA + at least one non-US country
    assert "USA" in locs
    assert len(locs) >= 2, f"expected multiple countries when us_only=False, got {locs}"
