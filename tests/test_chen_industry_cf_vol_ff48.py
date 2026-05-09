"""Inline pytest for Chen industry CF vol (Phase 1C Task C4).

Per spec C3 SIGMA + Table 4 footer:
    FF48 industry-MEDIAN of {firm-level σ over previous 10y of OANCF/AT}
    ≥3 obs floor on firm σ
    Distinct from Boasiako (FF49 MEAN of σ-of-industry-mean-series).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from f1d.shared.variables.chen_industry_cf_vol_ff48 import (
    ChenIndustryCFVolFF48Builder,
    WINDOW_LEN,
    MIN_OBS,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def chen_sigma() -> pd.DataFrame:
    return ChenIndustryCFVolFF48Builder().build(
        years=range(1997, 2007), root_path=ROOT
    ).data


def test_schema(chen_sigma):
    assert {"ff48_code", "fyear", "sigma_chen"}.issubset(chen_sigma.columns)


def test_ff48_range(chen_sigma):
    """FF48 codes ∈ [1, 48]."""
    assert chen_sigma["ff48_code"].between(1, 48).all()


def test_year_range(chen_sigma):
    """Output restricted to plan years 1997-2006."""
    assert chen_sigma["fyear"].between(1997, 2006).all()


def test_no_duplicate_ff48_fyear(chen_sigma):
    assert chen_sigma.duplicated(subset=["ff48_code", "fyear"]).sum() == 0


def test_sigma_non_negative(chen_sigma):
    valid = chen_sigma["sigma_chen"].dropna()
    assert (valid >= 0).all()


def test_sigma_finite(chen_sigma):
    valid = chen_sigma["sigma_chen"].dropna()
    assert np.isfinite(valid).all()


def test_window_constants():
    """Locked: 10-year window with ≥3 obs floor (audit V3 inherited from Boasiako A6)."""
    assert WINDOW_LEN == 10
    assert MIN_OBS == 3


def test_chen_distinct_from_boasiako_construction():
    """Chen FF48-MEDIAN-of-firm-σ ≠ Boasiako FF49-σ-of-industry-MEAN-series.

    Different industry classification (FF48 vs FF49) AND different
    construction (firm-σ-then-MEDIAN vs MEAN-then-σ).
    """
    from f1d.shared.variables.boasiako_industry_cf_vol import BoasiakoIndustryCFVolBuilder

    chen = ChenIndustryCFVolFF48Builder().build(
        years=range(2000, 2003), root_path=ROOT
    ).data
    bk = BoasiakoIndustryCFVolBuilder().build(
        years=range(2000, 2003), root_path=ROOT
    ).data
    # Different schemas (ff48_code vs ff49_code) — they are definitionally distinct
    assert "ff48_code" in chen.columns
    assert "ff49_code" in bk.columns
    # And by construction the value distributions differ
    if len(chen) > 0 and len(bk) > 0:
        chen_med = chen["sigma_chen"].dropna().median()
        bk_med = bk["industry_cf_vol"].dropna().median()
        # Allow they could happen to be similar but not identical
        assert chen_med != bk_med or len(chen) != len(bk)
